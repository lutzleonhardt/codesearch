import asyncio
import logging
import os
import click
from colorama import init, Fore, Style
from src.agent.prompts import USER_PROMPT
from src.agent.schemas import Deps
from src.shared.utils import colored_print
from pydantic_ai.result import Cost  # Ensure this import matches your actual project structure

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
    logger.info("Starting codesearch")
    deps = Deps(limit=100, project_root=root_dir)

    # Store previous messages
    previous_messages = []
    total_cost = 0 # Track cumulative cost of tokens

    while True:
        colored_print("Enter query (or 'q' to quit): ", color="BLUE", linebreak=False)
        user_input = input()
        if user_input.lower() == 'q':
            break

        from .agent.llm_agent import agent
        # Create a copy of messages with cleared ToolReturn content
        # This is to clean up the context for the LLM, we keep only the result
        # Hint: is is not possible to delete ToolReturn messages from the history
        processed_messages = []
        for msg in previous_messages:
            if msg.role == 'tool-return':
                # Create new ToolReturn with cleared content
                msg = msg.__class__(
                    tool_name=msg.tool_name,
                    content="<content cleared>",
                    tool_id=msg.tool_id,
                    timestamp=msg.timestamp
                )
            processed_messages.append(msg)

        agent_output = await agent.run(
            USER_PROMPT + user_input,
            deps=deps,
            message_history=processed_messages
        )


        # Update message history for next iteration
        previous_messages = agent_output.all_messages()

        # Print agent answer
        colored_print(agent_output.data.answer, color="GREEN")

        # Extract current cost
        current_cost = agent_output.cost()

        # Print token usage in aider style
        print(f"Tokens: {current_cost.request_tokens/1000:.1f}k sent, {current_cost.response_tokens/1000:.1f}k received. Session cost: ${total_cost:1000:.1f}k")

        #AI!: I do not want this blue line to have little distances between the dashes
        # Print blue separator line
        terminal_width = os.get_terminal_size().columns
        print(f"{Fore.BLUE}{Style.BRIGHT}{'-' * terminal_width}{Style.RESET_ALL}")

        # Update cumulative cost
        total_cost = total_cost + current_cost.total_tokens

        # Log each message
        for msg in agent_output.all_messages():
            logger.info(f"Message ({msg.role}): {msg}")

if __name__ == "__main__":
    main()  # This will now properly handle the async execution
