import asyncio
import logging
import os

import click
from colorama import init
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style
from pydantic_ai.messages import ModelRequest, SystemPromptPart, UserPromptPart

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
@click.option('--tools-result-limit', default=100, help='Maximum number of results (lines) to return for tools')
def main(verbose, root_dir, tools_result_limit):
    """Main entry point for codesearch CLI."""
    return asyncio.run(async_main(verbose, root_dir, tools_result_limit))

def print_token_usage(current_cost, total_cost):
    """Print token usage statistics and costs."""
    print() # new line
    print(f"Tokens: {current_cost.request_tokens/1000:.1f}k sent, {current_cost.response_tokens/1000:.1f}k received. Session cost: {total_cost/1000:.1f}k")

from .commands import print_blue_line, handle_command, CommandType


async def run_interactive_session(deps):
    """Run the interactive session with the agent."""
    previous_messages = []
    total_cost = 0  # Track cumulative cost of tokens
    print_blue_line()

    style = Style.from_dict({
        'prompt': 'ansicyan',
        'query': 'ansiblue',
    })

    session = PromptSession(style=style)

    while True:
        prompt_message = HTML(
            '<prompt>codesearch></prompt> '
            '<query>Enter query (\'/exit\' to quit, /help for commands): </query>'
        )
        with patch_stdout():
            user_input = await session.prompt_async(message=prompt_message)

        print()  # new line

        if user_input.startswith('/'):
            result = handle_command(user_input, previous_messages)

            if result.type == CommandType.EXIT:
                break
            elif result.type in (CommandType.CONTINUE, CommandType.COPY):
                previous_messages = result.messages
                continue
            elif result.type == CommandType.AGENT_QUERY:
                prompt_to_use = result.agent_prompt
                previous_messages = result.messages
        else:
            prompt_to_use = USER_PROMPT.replace('{question}', user_input)

        from .agent.main_agent import agent


        agent_output = await agent.run(
            prompt_to_use,
            deps=deps,
            message_history=previous_messages
        )


        # remember message history for next iteration
        previous_messages  = agent_output.all_messages()

        # Print agent answer
        colored_print(agent_output.data.answer, color="GREEN", colorize_all=True)
        colored_print("Confidence (1-10): " + str(agent_output.data.confidence_1_to_10), color="YELLOW", colorize_all=True)

        # Calculate and display token usage
        current_cost = agent_output.cost()
        total_cost = total_cost + current_cost.total_tokens
        print_token_usage(current_cost, total_cost)
        print_blue_line()

        # Log each message
        for msg in previous_messages:
            logger.info(f"Message: {msg}")

async def async_main(verbose, root_dir, tools_result_limit):
    """Main entry point for codesearch CLI."""
    logger.info("Starting codesearch")
    try:
        deps = Deps(limit=tools_result_limit, project_root=root_dir, verbose=verbose)
        await run_interactive_session(deps)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        colored_print(f"Error: {str(e)}", color="RED")

if __name__ == "__main__":
    main()  # This will now properly handle the async execution
