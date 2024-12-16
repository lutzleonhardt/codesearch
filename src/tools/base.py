from abc import ABC, abstractmethod
from typing import List
import threading

from ..shared import colored_print

io_lock = threading.Lock()


class ToolAbortedException(Exception):
    """Raised when a tool operation is aborted by the user"""
    pass


class BaseTool(ABC):
    def run(self, **kwargs):
        """Base run method that handles user approval and messaging"""
        with io_lock:
            result = self.get_tool_text_start(**kwargs)
            tool_text = result[0]
            params = result[1:] if len(result) > 1 else []

            colored_print(f"[{tool_text} - start]", color="CYAN", colorize_all=True)
            if params:
                for param in params:
                    colored_print(param, prefix="            ")
            else:
                print()  # Just newline if no params

            colored_print("Accept? (y/n) [y]: ", color="CYAN", linebreak=False)
            response = input().lower()
            if response != 'y' and response != '':
                colored_print(f"[{tool_text} - aborted]", color="RED", colorize_all=True, linebreak=False)
                print()  # new line
                print()  # new line
                raise ToolAbortedException("Operation aborted by user")

            result = self._run(**kwargs)

            if kwargs.get('verbose') and result:
                self.print_verbose_output(result)

            if result:
                end_text = self.get_tool_text_end(result)
                colored_print(f"[{tool_text} - end]", color="CYAN", colorize_all=True, linebreak=False)
                print(" " + end_text)
                print()  # new line
            return result

    @abstractmethod
    def _run(self, **kwargs):
        """Implement the actual tool logic here"""
        pass

    @abstractmethod
    def get_tool_text_start(self, **kwargs) -> List[str]:
        """Return the tool description text to show before approval"""
        pass

    @abstractmethod
    def get_tool_text_end(self, result) -> [str, str]:
        """Return the tool description text to show after completion"""
        pass

    @abstractmethod
    def print_verbose_output(self, result):
        """Print detailed tool output when verbose mode is enabled"""
        pass
