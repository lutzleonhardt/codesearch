from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional
from pydantic_ai.messages import ModelRequest, ModelResponse, SystemPromptPart, UserPromptPart, ToolCallPart, ArgsDict
from src.shared.utils import colored_print
from src.agent.prompts import SPEC_PROMPT
import pyperclip

class CommandType(Enum):
    CONTINUE = auto()
    EXIT = auto()
    AGENT_QUERY = auto()
    COPY = auto()

@dataclass
class CommandResult:
    type: CommandType
    messages: List[dict]
    agent_prompt: Optional[str] = None

def print_blue_line():
    """Print blue separator line."""
    import os
    from colorama import Fore, Style
    terminal_width = os.get_terminal_size().columns
    print(f"{Fore.BLUE}{Style.BRIGHT}{'━' * terminal_width}{Style.RESET_ALL}")

def handle_command(command: str, previous_messages: list) -> CommandResult:
    """Handle CLI commands and return a CommandResult."""
    parts = command.lower().split(maxsplit=1)
    cmd = parts[0]

    match cmd:
        case '/exit':
            return CommandResult(
                type=CommandType.EXIT,
                messages=previous_messages
            )

        case '/help':
            colored_print("Available commands:", color="CYAN", colorize_all=True)
            colored_print("  /help        - Show this help message", color="CYAN", colorize_all=True)
            colored_print("  /exit        - Exit the program", color="CYAN", colorize_all=True)
            colored_print("  /spec        - Show current configuration", color="CYAN", colorize_all=True)
            colored_print("  /add-context - Add text to chat history", color="CYAN", colorize_all=True)
            colored_print("  /copy        - Copy latest message to clipboard", color="CYAN", colorize_all=True)
            print_blue_line()
            return CommandResult(
                type=CommandType.CONTINUE,
                messages=previous_messages
            )

        case '/add-context':
            if len(parts) > 1:
                context = command[len('/add-context'):].strip()
                # previous_messages.append({"role": "user", "content": f"Context: {context}"})
                previous_messages.append(ModelRequest(parts=[UserPromptPart(content=f"Context: {context}")]))
                colored_print("Context added to chat history", color="CYAN", colorize_all=True)
            else:
                colored_print("Please provide text after /add-context", color="RED", colorize_all=True)
            print_blue_line()
            return CommandResult(
                type=CommandType.CONTINUE,
                messages=previous_messages
            )

        case '/spec':
            if len(parts) > 1:
                spec_name = command[len('/spec'):].strip()
                # previous_messages.append({"role": "user", "content": f"Please create a detailed specification for: {spec_name}"})
                return CommandResult(
                    type=CommandType.AGENT_QUERY,
                    messages=previous_messages,
                    agent_prompt=SPEC_PROMPT.format(name=spec_name)
                )
            else:
                colored_print("Please provide a name after /spec", color="RED", colorize_all=True)
                print_blue_line()
                return CommandResult(
                    type=CommandType.CONTINUE,
                    messages=previous_messages
                )

        case '/copy':
            if not previous_messages:
                colored_print("No messages to copy", color="RED", colorize_all=True)
                print_blue_line()
                return CommandResult(
                    type=CommandType.CONTINUE,
                    messages=previous_messages
                )
            
            # Search backwards for final_result
            final_result = None
            for message in reversed(previous_messages):
                if (isinstance(message, ModelResponse) and 
                    message.parts and 
                    isinstance(message.parts[0], ToolCallPart) and
                    message.parts[0].tool_name == 'final_result' and
                    isinstance(message.parts[0].args, ArgsDict)):
                    final_result = message.parts[0].args.args_dict.get('answer')
                    break
            
            if final_result is None:
                colored_print("No final result found to copy", color="RED", colorize_all=True)
                print_blue_line()
                return CommandResult(
                    type=CommandType.CONTINUE,
                    messages=previous_messages
                )
                
            pyperclip.copy(final_result)
            colored_print("Latest final result copied to clipboard", color="GREEN", colorize_all=True)
            print_blue_line()
            return CommandResult(
                type=CommandType.COPY,
                messages=previous_messages
            )

        case _:
            colored_print(f"Unknown command: {command}", color="RED", colorize_all=True)
            colored_print("Type /help for available commands", color="CYAN", colorize_all=True)
            print_blue_line()
            return CommandResult(
                type=CommandType.CONTINUE,
                messages=previous_messages
            )
