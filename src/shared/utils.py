from colorama import Fore, Style

def colored_print(message: str, prefix: str = "codesearch> ", color: str = None, linebreak: bool = True, colorize_all: bool = False):
    """Print a message with optional color and prefix."""
    colored_prefix = prefix
    if color:
        color_code = getattr(Fore, color.upper(), Fore.WHITE)
        if colorize_all:
            colored_prefix = color_code + prefix
            message = message + Style.RESET_ALL
        else:
            colored_prefix = color_code + prefix + Style.RESET_ALL
    if linebreak:
        print(f"{colored_prefix}{message}")
    else:
        print(f"{colored_prefix}{message}", end="")
