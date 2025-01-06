import threading
import asyncio
from abc import ABC, abstractmethod
from typing import List

from .types import BaseToolResult
from ..shared import colored_print
from ..summarize_agent.main_agent import summarize_tool_output

io_lock = threading.Lock()


class ToolAbortedException(Exception):
    """Raised when a tool operation is aborted by the user"""
    pass

class BaseTool(ABC):
    async def run(self, intention_of_this_call: str, **kwargs) -> BaseToolResult:
        """Base run method that handles user approval and messaging"""
        with io_lock:
            result = self.get_tool_text_start(**kwargs)
            tool_text = result[0]
            params = result[1:] if len(result) > 1 else []

            colored_print(intention_of_this_call, color="GREEN", colorize_all=True)
            colored_print(f"[{tool_text}]", color="CYAN", colorize_all=True)
            if params:
                for param in params:
                    colored_print(param, prefix="            ", color="YELLOW", colorize_all=True)
            else:
                print()  # Just newline if no params

            colored_print("Accept? (y/n) [y]: ", color="CYAN", linebreak=False, colorize_all=True)
            response = input().lower()
            if response != 'y' and response != '':
                colored_print(f"[{tool_text} - aborted]", color="RED", colorize_all=True, linebreak=False)
                print()  # new line
                print()  # new line
                raise ToolAbortedException("Operation aborted by user")

            result = self._run(intention_of_this_call, **kwargs)

            # Handle summarization if needed
            limit = kwargs.get('limit', 50)
            if len(result['items']) > limit:
                summary = await summarize_tool_output(
                    result['items'],
                    intention_of_this_call,
                    max_lines=limit,
                    verbose=kwargs.get('verbose', False)
                )
                result['summary'] = summary
                result['is_summarized'] = True
            else:
                result['summary'] = None
                result['is_summarized'] = False

            if kwargs.get('verbose') and result:
                # Print original output first
                self.print_verbose_output(result)

                # Print summary if it exists
                if result.get('is_summarized'):
                    print()
                    colored_print("Summarized output:", color="YELLOW", colorize_all=True)
                    for line in result['summary']:
                        colored_print(line, color="YELLOW")

            if result:
                end_text = self.get_tool_text_end(result, **kwargs)
                colored_print(f"[{tool_text}]", color="CYAN", colorize_all=True, linebreak=False)
                print(" " + end_text)
                print()  # new line
            return result

    @abstractmethod
    def _run(self, intention_of_this_call: str, **kwargs) -> BaseToolResult:
        """Implement the actual tool logic here"""
        pass

    @abstractmethod
    def get_tool_text_start(self, **kwargs) -> List[str]:
        """Return the tool description text to show before approval"""
        pass

    def get_tool_text_end(self, result: BaseToolResult, **kwargs) -> str:
        if result.get('is_summarized'):
            return f"summarized (original total_lines: {result['total_count']})"
        return f"total_lines: {result['total_count']}"

    @abstractmethod
    def print_verbose_output(self, result: BaseToolResult):
        """Print detailed tool output when verbose mode is enabled"""
        pass
