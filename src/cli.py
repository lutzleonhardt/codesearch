import logging
import os
import click
from colorama import Fore, Style, init

init(autoreset=True)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    filename='logs/codesearch.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def colored_print(message: str, prefix: str = "codesearch> ", color: str = None, linebreak: bool = True):
    """Print a message with optional color and prefix."""
    colored_prefix = prefix
    if color:
        colored_prefix = getattr(Fore, color.upper(), Fore.WHITE) + prefix + Style.RESET_ALL
    if linebreak:
        print(f"{colored_prefix}{message}")
    else:
        print(f"{colored_prefix}{message}", end="")

@click.command()
@click.option('--verbose', is_flag=True, default=False, help='Enable verbose output')
@click.option('--root-dir', default='.', help='Root directory to explore')
@click.option('--rebuild-ctags', is_flag=True, default=False, help='Rebuild ctags index on every tool call')
def main(verbose, root_dir, rebuild_ctags):
    """Main entry point for codesearch CLI."""
    logger.info(f"Starting codesearch")
    colored_print(f"Welcome to codesearch!", color="BLUE")
    colored_print(f"Root Directory: {root_dir}", color="CYAN")
    colored_print(f"Verbose: {verbose}", color="CYAN")
    colored_print(f"Rebuild Ctags: {rebuild_ctags}", color="CYAN")

    while True:
        colored_print("Enter query (or 'q' to quit): ", color="BLUE", linebreak=False)
        user_input = input()
        if user_input.lower() == 'q':
            break
        colored_print(f"You said: {user_input}", color="GREEN")

if __name__ == "__main__":
    main()
