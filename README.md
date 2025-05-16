# Save Images to Video (FFmpeg) for ComfyUI

A custom node for ComfyUI to save image sequences as video files using FFmpeg. Supports various codecs, audio muxing, and in-node previews.

![Save Images to Video (FFmpeg)](./screenshots/screenshot.png)

## Features

*   Saves image frames to MP4, WebM, MOV, AVI, MKV.
*   Video Codecs: libx264, libx265, mpeg4, libvpx-vp9, libsvtav1.
*   Configurable FPS, pixel format.
*   Optional audio input with configurable codec (AAC, MP3, libopus, copy) and bitrate.
*   In-node preview (H.265 in-node preview is broken).

## Installation

1.  **FFmpeg:** Ensure FFmpeg is installed and in your system's PATH.
2.  **Clone:**
    ```bash
    cd ComfyUI/custom_nodes/
    git clone https://github.com/San4itos/ComfyUI-Save-Images-as-Video.git 
    cd ComfyUI-Save-Images-as-Video
    pip install -r requirements.txt
    ```
Find the node in "Add Node" -> "San4itos" -> "Save Images to Video (FFmpeg)".

## Usage
Connect `IMAGE` output to `images` input. Configure parameters as needed. Optionally connect `AUDIO` input.

**H.265 Preview Note:** In-node H.265 previews might not work. The video file is saved correctly, and live preview in the ComfyUI queue section works.

---

# Збереження Зображень у Відео (FFmpeg) для ComfyUI

Кастомний вузол для ComfyUI для збереження послідовностей зображень у відеофайли за допомогою FFmpeg. Підтримує різні кодеки, додавання аудіо та попередній перегляд у вузлі.

![Save Images to Video (FFmpeg)](./screenshots/screenshot.png)

## Можливості

*   Збереження кадрів зображень у MP4, WebM, MOV, AVI, MKV.
*   Відеокодеки: libx264, libx265, mpeg4, libvpx-vp9, libsvtav1.
*   Налаштовувані FPS, формат пікселів.
*   Опціональний аудіовхід з налаштовуваним кодеком (AAC, MP3, libopus, copy) та бітрейтом.
*   Попередній перегляд у вузлі (попередній перегляд H.265 у вузлі не працює належним чином).

## Встановлення

1.  **FFmpeg:** Переконайтеся, що FFmpeg встановлено та доступно у системному PATH.
2.  **Клонувати:**
    ```bash
    cd ComfyUI/custom_nodes/
    git clone https://github.com/San4itos/ComfyUI-Save-Images-as-Video.git 
    cd ComfyUI-Save-Images-as-Video
    pip install -r requirements.txt
    ```
Знайдіть вузол в "Add Node" -> "San4itos" -> "Save Images to Video (FFmpeg)".

## Використання
Підключіть вихід `IMAGE` до входу `images`. Налаштуйте параметри за потребою. Опціонально підключіть вхід `AUDIO`.

**Примітка щодо прев'ю H.265:** Попередній перегляд H.265 у вузлі може не працювати. Відеофайл зберігається коректно, а попередній перегляд у секції черги ComfyUI працює.
