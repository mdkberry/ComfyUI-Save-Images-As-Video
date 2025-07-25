# node_logger.py

# ANSI color dictionary
COLORS = {
  'BLACK': '\33[30m', 'RED': '\33[31m', 'GREEN': '\33[32m', 'YELLOW': '\33[33m',
  'BLUE': '\33[34m', 'MAGENTA': '\33[35m', 'CYAN': '\33[36m', 'WHITE': '\33[37m',
  'GREY': '\33[90m', 'BRIGHT_RED': '\33[91m', 'BRIGHT_GREEN': '\33[92m', 
  'BRIGHT_YELLOW': '\33[93m', 'BRIGHT_BLUE': '\33[94m', 'BRIGHT_MAGENTA': '\33[95m',
  'BRIGHT_CYAN': '\33[96m', 'BRIGHT_WHITE': '\33[97m',
  'RESET': '\33[00m', 'BOLD': '\33[01m', 'NORMAL': '\33[22m', 'ITALIC': '\33[03m',
  'UNDERLINE': '\33[04m', 'BLINK': '\33[05m', 'BLINK2': '\33[06m', 'SELECTED': '\33[07m',
  'BG_BLACK': '\33[40m', 'BG_RED': '\33[41m', 'BG_GREEN': '\33[42m', 'BG_YELLOW': '\33[43m',
  'BG_BLUE': '\33[44m', 'BG_MAGENTA': '\33[45m', 'BG_CYAN': '\33[46m', 'BG_WHITE': '\33[47m',
  'BG_GREY': '\33[100m', 'BG_BRIGHT_RED': '\33[101m', 'BG_BRIGHT_GREEN': '\33[102m',
  'BG_BRIGHT_YELLOW': '\33[103m', 'BG_BRIGHT_BLUE': '\33[104m', 'BG_BRIGHT_MAGENTA': '\33[105m',
  'BG_BRIGHT_CYAN': '\33[106m', 'BG_BRIGHT_WHITE': '\33[107m',
}

# Unique global prefix
GLOBAL_PREFIX = "mdkberry"


def log(message, color=None, msg_color=None, prefix=None):
  """Basic logging function"""
  # Colour for [GLOBAL_PREFIX][prefix]
  color_code = COLORS.get(str(color).upper(), COLORS.get("BRIGHT_GREEN")) 
  # Colour for the message itself
  msg_color_code = COLORS.get(str(msg_color).upper(), '') # If msg_color is not specified, the color does not change.
  
  prefix_str = f'[{prefix}]' if prefix is not None else ''
  
  
  # keeping the logic: colour is the colour for the entire block of prefixes.
  full_prefix_block = f"[{GLOBAL_PREFIX}]{prefix_str}"
  
  # If msg_color is not specified (i.e., an empty string), the message will be the same color as the prefix,
  # until COLORS[“RESET”] is encountered. If msg_color is specified, it will override the prefix color for the message text.
  print(f'{color_code}{full_prefix_block}{COLORS.get("RESET")} {msg_color_code}{message}{COLORS.get("RESET")}')
  # Small change: added RESET after the prefix so that msg_color does not “inherit” the prefix color if msg_color is not specified.
  # Or, if we want behavior where msg_color=‘’ means “continue current color”:
  # print(f'{color_code}{full_prefix_block} {msg_color_code}{message}{COLORS.get("RESET")}')


def _log_node(prefix_block_color_name, node_specific_prefix, message, msg_color='RESET'):
  """Internal logging function for nodes (adapted from rgthree)."""
  log(message, color=prefix_block_color_name, prefix=node_specific_prefix, msg_color=msg_color)


def log_node_success(node_name, message, msg_color_override='BRIGHT_GREEN'):
  """Logs success messages."""
  _log_node("GREEN", node_name, message, msg_color=msg_color_override) 


def log_node_info(node_name, message, msg_color_override='YELLOW'):
  """Logs an informational message"""
  _log_node("CYAN", node_name, message, msg_color=msg_color_override) 


def log_node_warning(node_name, message, msg_color_override='BRIGHT_YELLOW'):
  """Logs warnings."""
  _log_node("YELLOW", node_name, message, msg_color=msg_color_override) 


def log_node_error(node_name, message, msg_color_override='BRIGHT_RED'):
  """Logs error messages."""
  _log_node("RED", node_name, message, msg_color=msg_color_override) 


# If you have log_node_debug or log_node_message, you also need to check/fix them:
def log_node_debug(node_name, message, msg_color_override='GREY'):
    _log_node("MAGENTA", node_name, message, msg_color=msg_color_override) 
