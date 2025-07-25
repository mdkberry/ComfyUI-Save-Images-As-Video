# ffmpeg_path_resolver.py
import os
import subprocess
import configparser
from .node_logger import log_node_info, log_node_success, log_node_warning, log_node_error, log_node_debug

_CACHED_FFMPEG_PATH = None
_CACHED_FFMPEG_SOURCE_TYPE = None # Source type: "config", "local_bin", "system_path", "fallback"

# Use a fixed prefix for the logs of this module.
RESOLVER_LOG_PREFIX = "FFmpegPathResolver" 

def _test_ffmpeg_executable(path_to_test):
    if not path_to_test: return False
    try:
        log_node_debug(RESOLVER_LOG_PREFIX, f"Testing ffmpeg at: {path_to_test}")
        subprocess.run([path_to_test, '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, check=True)
        return True
    except Exception:
        return False

def initialize_ffmpeg_path_and_log(package_root_directory):
    global _CACHED_FFMPEG_PATH, _CACHED_FFMPEG_SOURCE_TYPE
    if _CACHED_FFMPEG_PATH is not None: # Already initialized
        return

    ffmpeg_command_name = "ffmpeg"
    determined_path = None
    source_type = "unknown"

    # 1. Config file
    config_file_path = os.path.join(package_root_directory, "ffmpeg_config.ini")
    path_from_config_ini = None
    if os.path.exists(config_file_path):
        try:
            config = configparser.ConfigParser(); config.read(config_file_path)
            if 'FFMPEG' in config and 'custom_ffmpeg_path' in config['FFMPEG']:
                configured_value = config['FFMPEG']['custom_ffmpeg_path'].strip()
                if configured_value: path_from_config_ini = configured_value
        except Exception as e_cfg:
            log_node_warning(RESOLVER_LOG_PREFIX, f"Error reading ffmpeg_config.ini: {e_cfg}.")

    if path_from_config_ini:
        abs_path = os.path.abspath(os.path.join(package_root_directory, path_from_config_ini) if not os.path.isabs(path_from_config_ini) else path_from_config_ini)
        potential_path = None
        if os.path.isdir(abs_path): potential_path = os.path.join(abs_path, ffmpeg_command_name)
        elif os.path.isfile(abs_path) and abs_path.lower().endswith(ffmpeg_command_name): potential_path = abs_path
            
        if _test_ffmpeg_executable(potential_path):
            determined_path = potential_path
            source_type = "config"
            log_node_success(RESOLVER_LOG_PREFIX, f"Using ffmpeg from configured path: {determined_path}")
        else:
            log_node_warning(RESOLVER_LOG_PREFIX, f"ffmpeg not working at configured path '{potential_path or abs_path}'. Checking other locations.")
            # source_type remains “unknown” so that the logic below can determine it correctly
    
    # 2. Local node directory (if not found via config or config path was empty/invalid)
    if not determined_path:
        local_path = os.path.join(package_root_directory, "ffmpeg_bin", ffmpeg_command_name)
        if _test_ffmpeg_executable(local_path):
            determined_path = local_path
            source_type = "local_bin"
            log_node_success(RESOLVER_LOG_PREFIX, f"Using ffmpeg from local 'ffmpeg_bin': {determined_path}")
        else:
            log_node_info(RESOLVER_LOG_PREFIX, f"ffmpeg not in local 'ffmpeg_bin' or not working. Checking system PATH.")
            # source_type remains “unknown” or previous if config was present but did not work

    # 3. System PATH (if not found yet)
    if not determined_path:
        if _test_ffmpeg_executable(ffmpeg_command_name):
            determined_path = ffmpeg_command_name
            source_type = "system_path"
            log_node_info(RESOLVER_LOG_PREFIX, f"Using ffmpeg from system PATH: '{determined_path}'")
        else:
            log_node_error(RESOLVER_LOG_PREFIX, f"ffmpeg ('{ffmpeg_command_name}') also not found or not working in system PATH.")
            determined_path = ffmpeg_command_name # Fallback
            source_type = "fallback"

    _CACHED_FFMPEG_PATH = determined_path
    _CACHED_FFMPEG_SOURCE_TYPE = source_type


def get_ffmpeg_path():
    global _CACHED_FFMPEG_PATH
    if _CACHED_FFMPEG_PATH is None:
        # This situation should not occur if initialize_ffmpeg_path_and_log is called from the package's __init__.py.
        log_node_error("FFmpegPath", "FATAL: get_ffmpeg_path() called before path was initialized!")
        # Return the default, but this is a sign of a problem in the initialization process.
        return "ffmpeg" 
    return _CACHED_FFMPEG_PATH
