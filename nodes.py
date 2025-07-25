# nodes.py
import subprocess
import os
import configparser
import tempfile
import numpy as np
from PIL import Image
import folder_paths
import torch
import torchaudio
from .ffmpeg_path_resolver import get_ffmpeg_path
from .node_logger import log_node_info, log_node_success, log_node_error, log_node_warning, log_node_debug 


class SaveFramesToVideoFFmpeg:
    NODE_LOG_PREFIX = "SaveVideoFFMPEG" # Class attribute for logging

    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.ffmpeg_executable_path = get_ffmpeg_path()
        log_node_debug(self.NODE_LOG_PREFIX, f"Instance initialized. Will use ffmpeg at: {self.ffmpeg_executable_path}")

    @classmethod
    def INPUT_TYPES(cls):
           return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "video"}),
                "fps": ("FLOAT", {"default": 16.0, "min": 1.0, "max": 120.0, "step": 1.0}),
                "codec": (["libx264", "libx265", "libvpx-vp9", "libsvtav1"], {"default": "libx264"}),
                "pixel_format": (["yuv420p", "yuv422p", "yuv444p", "yuv420p10le", "yuv422p10le", "yuv444p10le", "rgb24"], {"default": "yuv420p"}),
                "output_format": (["mp4", "webm", "mov", "avi", "mkv"], {"default": "mp4"}),
            },
            "optional": {
                "audio": ("AUDIO", {"tooltip": "Optional audio. Expects {'waveform': tensor, 'sample_rate': int}."}),
                "audio_codec": (["aac", "mp3", "libopus", "copy"], {"default": "aac"}),
                "audio_bitrate": (["96k", "128k", "160k", "192k", "256k", "320k"], {"default": "192k"}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "save_video"
    OUTPUT_NODE = True
    CATEGORY = "mdkberry"

    def save_video(self, images, filename_prefix, fps, codec, pixel_format, output_format, 
                   audio=None, audio_codec="aac", audio_bitrate="192k",
                   prompt=None, extra_pnginfo=None):
        
        if not isinstance(images, torch.Tensor) or images.ndim != 4:
            error_msg = f"Error: Expected 4D tensor for images, got {type(images)}"
            if hasattr(images, 'shape'): error_msg += f" with shape {images.shape}"
            log_node_error(self.NODE_LOG_PREFIX, error_msg); return {"ui": {"text": [error_msg]}}
        if images.shape[0] == 0:
            error_msg = "Error: No frames to process (batch_size is 0)."
            log_node_error(self.NODE_LOG_PREFIX, error_msg); return {"ui": {"text": [error_msg]}}

        h, w = images[0].shape[0], images[0].shape[1]
        # Use filename_prefix as is, to support subdirectories.
        full_output_folder, filename_part_returned, counter, subfolder_relative_to_output, _ = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, w, h
        )
        # Form the file name by removing unnecessary underscores
        cleaned_filename_part = filename_part_returned.rstrip('_')
        video_filename_with_counter = f"{cleaned_filename_part}_{counter:05}_.{output_format}"
        video_full_path = os.path.join(full_output_folder, video_filename_with_counter)

        temp_audio_file_for_ffmpeg = None

        with tempfile.TemporaryDirectory() as temp_dir:
            frame_paths = [] # Frame retention code
            for i, image_tensor in enumerate(images):
                try:
                    img_pil = self.tensor_to_pil(image_tensor)
                    frame_filename = os.path.join(temp_dir, f"frame_{i:06d}.png")
                    img_pil.save(frame_filename, "PNG")
                    frame_paths.append(frame_filename)
                except Exception as e_frame:
                    log_node_error(self.NODE_LOG_PREFIX, f"Error processing frame {i}: {e_frame}")
                    return {"ui": {"text": [f"Error processing frame {i}: {e_frame}"]}}
            if not frame_paths:
                 log_node_error(self.NODE_LOG_PREFIX, "Error: No frames were processed to save.")
                 return {"ui": {"text": ["Error: No frames were processed to save."]}}

            # The first element of the command is the found path to ffmpeg
            ffmpeg_cmd = [self.ffmpeg_executable_path, '-y', '-framerate', str(fps), '-i', os.path.join(temp_dir, 'frame_%06d.png')]
            has_audio_input = False

            if audio is not None and isinstance(audio, dict) and "waveform" in audio and "sample_rate" in audio:
                waveform_tensor = audio["waveform"]; sample_rate = audio["sample_rate"]
                log_node_debug(self.NODE_LOG_PREFIX, f"Audio data. Waveform: {waveform_tensor.shape}, SR: {sample_rate}")
                if waveform_tensor.ndim == 3 and waveform_tensor.shape[0] > 0 and waveform_tensor.shape[2] > 0:
                    if waveform_tensor.shape[0] > 1: log_node_warning(self.NODE_LOG_PREFIX, f"Audio batch size {waveform_tensor.shape[0]}. Using first track.")
                    waveform_to_save = waveform_tensor[0].cpu()
                    if waveform_to_save.numel() > 0:
                        try:
                            temp_audio_file_for_ffmpeg = os.path.join(temp_dir, "temp_audio_for_ffmpeg.wav")
                            torchaudio.save(temp_audio_file_for_ffmpeg, waveform_to_save, sample_rate)
                            ffmpeg_cmd.extend(['-i', temp_audio_file_for_ffmpeg]); has_audio_input = True
                            log_node_info(self.NODE_LOG_PREFIX, f"Audio input prepared: {temp_audio_file_for_ffmpeg}")
                        except Exception as e_asave:
                            log_node_error(self.NODE_LOG_PREFIX, f"Error saving temp audio: {e_asave}. Skipping audio.")
                            if temp_audio_file_for_ffmpeg and os.path.exists(temp_audio_file_for_ffmpeg): os.remove(temp_audio_file_for_ffmpeg)
                            temp_audio_file_for_ffmpeg = None; has_audio_input = False
                    else: log_node_warning(self.NODE_LOG_PREFIX,"Audio waveform empty. Skipping audio.")
                else: log_node_warning(self.NODE_LOG_PREFIX, f"Audio waveform shape {waveform_tensor.shape} unexpected. Skipping.")
            elif audio is not None: log_node_warning(self.NODE_LOG_PREFIX, f"Audio input not expected format. Type: {type(audio)}. Skipping.")
            
            ffmpeg_cmd.extend(['-c:v', codec, '-pix_fmt', pixel_format])
            if codec in ["libx264", "libx265"]: ffmpeg_cmd.extend(['-crf', '19'])
            # if codec in ["libaom-av1"]: ffmpeg_cmd.extend(['-crf', '23'])
            if codec in ["libsvtav1"]: ffmpeg_cmd.extend(['-crf', '35'])
            if output_format in ["mp4", "mov"]: ffmpeg_cmd.extend(['-movflags', '+faststart'])
                        
            if has_audio_input:
                if audio_codec == "copy": ffmpeg_cmd.extend(['-c:a', 'copy'])
                else:
                    ffmpeg_cmd.extend(['-c:a', audio_codec])
                    if audio_codec in ["aac", "mp3", "libopus"]: # Changed opus to libopus
                        ffmpeg_cmd.extend(['-b:a', audio_bitrate])
                ffmpeg_cmd.extend(['-shortest'])
            else: ffmpeg_cmd.extend(['-an'])
            ffmpeg_cmd.append(video_full_path)
            
            log_node_info(self.NODE_LOG_PREFIX, f"Executing ffmpeg: {' '.join(ffmpeg_cmd)}")
            try:
                process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
                stdout, stderr = process.communicate(timeout=300)
                if process.returncode != 0:
                    err_msg = f"ffmpeg error (code {process.returncode}):\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                    log_node_error(self.NODE_LOG_PREFIX, err_msg)
                    return {"ui": {"text": [f"ffmpeg error (code {process.returncode}): Check console for details."]}}
                else:
                    log_node_success(self.NODE_LOG_PREFIX, f"Video saved: {video_full_path}")
                    if stdout.strip(): log_node_info(self.NODE_LOG_PREFIX, f"ffmpeg stdout:\n{stdout}", msg_color_override="GREY")
                    if stderr.strip(): log_node_warning(self.NODE_LOG_PREFIX, f"ffmpeg stderr (warnings):\n{stderr}", msg_color_override="GREY")
                    
                    preview_files_for_ui = [{"filename": video_filename_with_counter, "subfolder": subfolder_relative_to_output, "type": self.type}]
                    ui_response_content = {"images": preview_files_for_ui, "animated": (True,)} 
                    return {"ui": ui_response_content}
            except subprocess.TimeoutExpired:
                process.kill(); stdout, stderr = process.communicate()
                log_node_error(self.NODE_LOG_PREFIX, f"ffmpeg timeout. STDOUT:{stdout} STDERR:{stderr}")
                return {"ui": {"text": [f"ffmpeg timeout. STDOUT:{stdout} STDERR:{stderr}"]}}
            except Exception as e:
                log_node_error(self.NODE_LOG_PREFIX, f"Python error (ffmpeg exec): {str(e)}")
                return {"ui": {"text": [f"Python error (ffmpeg exec): {str(e)}"]}}
            finally:
                if temp_audio_file_for_ffmpeg and os.path.exists(temp_audio_file_for_ffmpeg):
                    try: os.remove(temp_audio_file_for_ffmpeg)
                    except Exception as e_rem: log_node_warning(self.NODE_LOG_PREFIX, f"Warning: Could not remove temp audio: {e_rem}")
    
    def tensor_to_pil(self, tensor_image):
        if isinstance(tensor_image, Image.Image): return tensor_image
        if isinstance(tensor_image, np.ndarray):
            if tensor_image.dtype != np.uint8:
                tensor_image = np.clip(tensor_image, 0.0, 1.0); tensor_image = (tensor_image * 255).astype(np.uint8)
            if tensor_image.ndim == 3 and tensor_image.shape[-1] == 1: tensor_image = tensor_image.squeeze(-1)
            return Image.fromarray(tensor_image)
        if not isinstance(tensor_image, torch.Tensor): raise TypeError(f"Input must be Tensor, PIL, or NumPy, got {type(tensor_image)}")
        if tensor_image.ndim == 2: tensor_image = tensor_image.unsqueeze(-1)
        if tensor_image.ndim == 3 and tensor_image.shape[0] in (1, 3, 4):
            if tensor_image.shape[0] < tensor_image.shape[1] and tensor_image.shape[0] < tensor_image.shape[2]:
                tensor_image = tensor_image.permute(1, 2, 0)
        if tensor_image.ndim != 3 or tensor_image.shape[-1] not in (1, 3, 4):
            raise ValueError(f"Unsupported tensor shape: {tensor_image.shape}.")
        image_np = tensor_image.cpu().float().numpy()
        if image_np.max() > 1.001 or image_np.min() < -0.001:
            image_np = np.clip(image_np, 0.0, 1.0)
        image_np = (image_np * 255).astype(np.uint8)
        if image_np.shape[-1] == 1: image_np = image_np.squeeze(-1)
        return Image.fromarray(image_np)


NODE_CLASS_MAPPINGS = {"SaveFramesToVideoFFmpeg": SaveFramesToVideoFFmpeg}
NODE_DISPLAY_NAME_MAPPINGS = {"SaveFramesToVideoFFmpeg": "Save Images to Video (FFmpeg)"}
