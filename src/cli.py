import logging
import os
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

def colored_print(message: str, prefix: str = "codesearch> ", color: str = None):
    """Print a message with optional color and prefix."""
    colored_prefix = prefix
    if color:
        colored_prefix = getattr(Fore, color.upper(), Fore.WHITE) + prefix + Style.RESET_ALL
    print(f"{colored_prefix}{message}")

def main():
    """Main entry point for codesearch CLI."""
    logger.info("Starting codesearch")
    colored_print("Welcome to codesearch!", color="BLUE")

if __name__ == "__main__":
    main()
