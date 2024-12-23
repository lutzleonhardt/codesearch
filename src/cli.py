import asyncio
import logging
import os

import click
from colorama import init, Fore, Style

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

def print_blue_line():
    # Print blue separator line
    terminal_width = os.get_terminal_size().columns
    print(f"{Fore.BLUE}{Style.BRIGHT}{'━' * terminal_width}{Style.RESET_ALL}")


async def run_interactive_session(deps):
    """Run the interactive session with the agent."""
    previous_messages = []
    total_cost = 0  # Track cumulative cost of tokens
    print_blue_line()

    while True:
        colored_print("Enter query ('/exit' to quit): ", color="BLUE", linebreak=False, colorize_all=True)
        user_input = input()
        if user_input.lower() == '/exit':
            break

        print() # new line
        from .agent.llm_agent import agent
        # Create a copy of messages with cleared ToolReturn content
        # This is to clean up the context for the LLM, we keep only the result
        # Hint: is is not possible to delete ToolReturn messages from the history
        processed_messages = []
        for msg in previous_messages:
            # if msg.role == 'tool-return':
            #     # Create new ToolReturn with cleared content
            #     msg = msg.__class__(
            #         tool_name=msg.tool_name,
            #         content="<content cleared>",
            #         tool_id=msg.tool_id,
            #         timestamp=msg.timestamp
            #     )
            processed_messages.append(msg)

        agent_output = await agent.run(
            USER_PROMPT.replace('{question}', user_input),
            deps=deps,
            message_history=processed_messages,
        )

        # Update message history for next iteration
        previous_messages = agent_output.all_messages()

        # Print agent answer
        colored_print(agent_output.data.answer, color="GREEN", colorize_all=True)
        colored_print("Confidence (1-10): " + str(agent_output.data.confidence_1_to_10), color="YELLOW", colorize_all=True)

        # Calculate and display token usage
        current_cost = agent_output.cost()
        total_cost = total_cost + current_cost.total_tokens
        print_token_usage(current_cost, total_cost)
        print_blue_line()

        # Log each message
        for msg in agent_output.all_messages():
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
