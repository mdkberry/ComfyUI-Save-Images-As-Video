# /home/san4itos/ComfyUI/custom_nodes/ComfyUI-san4itos/__init__.py

from .nodes import NODE_CLASS_MAPPINGS as FFMPEG_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as FFMPEG_DISPLAY_MAPPINGS
from .node_logger import log_node_info, log_node_success, log_node_error, log_node_warning, log_node_debug 

NODE_CLASS_MAPPINGS = {
    **FFMPEG_MAPPINGS,
    # **OTHER_MAPPINGS, # Розкоментуйте та додайте інші, якщо є
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **FFMPEG_DISPLAY_MAPPINGS,
    # **OTHER_DISPLAY_MAPPINGS, # Розкоментуйте та додайте інші, якщо є
}

# WEB_DIRECTORY = "./js" # Вказує на папку js

# __all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

log_node_info("INIT","*** Loading Custom Nodes from ComfyUI-san4itos ***") # Для перевірки завантаження
