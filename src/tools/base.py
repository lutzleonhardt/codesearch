from abc import ABC, abstractmethod
from ..shared import colored_print

class ToolAbortedException(Exception):
    """Raised when a tool operation is aborted by the user"""
    pass

class BaseTool(ABC):
    def run(self, **kwargs):
        """Base run method that handles user approval and messaging"""
        [tool_text, param_text] = self.get_tool_text_start(**kwargs)
        colored_print(tool_text, color="CYAN", colorize_all=True, linebreak=False)
        print(" " + param_text)

        colored_print("Accept? (y/n) [y]: ", color="BLUE", linebreak=False)
        response = input().lower()
        if response != 'y' and response != '':
            colored_print(tool_text, color="CYAN", colorize_all=True, linebreak=False)
            print(" Aborted")
            raise ToolAbortedException("Operation aborted by user")

        result = self._run(**kwargs)
        if result:
            end_text = self.get_tool_text_end(result)
            colored_print(tool_text, color="CYAN", colorize_all=True, linebreak=False)
            print(" " + end_text)
        return result

    @abstractmethod
    def _run(self, **kwargs):
        """Implement the actual tool logic here"""
        pass

    @abstractmethod
    def get_tool_text_start(self, **kwargs) -> [str, str]:
        """Return the tool description text to show before approval"""
        pass

    @abstractmethod
    def get_tool_text_end(self, result) -> [str, str]:
        """Return the tool description text to show after completion"""
        pass
