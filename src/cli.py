import asyncio
import logging
import os
import click
from colorama import init
from src.agent.prompts import USER_PROMPT
from src.agent.schemas import Deps
from src.shared.utils import colored_print

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
    deps = Deps(limit=100, project_root=root_dir)

    while True:
        colored_print("Enter query (or 'q' to quit): ", color="BLUE", linebreak=False)
        user_input = input()
        if user_input.lower() == 'q':
            break
        from .agent.llm_agent import agent
        agent_output = await agent.run(USER_PROMPT + user_input, deps=deps)
        colored_print(agent_output.data.answer, color="GREEN")
        logger.info(agent_output.all_messages())

if __name__ == "__main__":
    main()  # This will now properly handle the async execution
