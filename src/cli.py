import asyncio
import logging
import os
import click
from colorama import Fore, Style, init

from src.agent.prompts import USER_PROMPT

init(autoreset=True)

# Get directory containing current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Create logs directory next to script
log_dir = os.path.join(script_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'codesearch.log')

# Configure logging
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
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
    return asyncio.run(async_main(verbose, root_dir, rebuild_ctags))

async def async_main(verbose, root_dir, rebuild_ctags):
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
        from .agent.llm_agent import agent
        agent_output = await agent.run(USER_PROMPT + user_input)
        colored_print(agent_output.data.answer, color="GREEN")

if __name__ == "__main__":
    main()  # This will now properly handle the async execution
