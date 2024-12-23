from typing import List
from .base import BaseTool
from ..shared.utils import colored_print

class FileWriterTool(BaseTool):
    def get_tool_text_start(self, file_path: str, **kwargs) -> List[str]:
        return [
            "Write file",
            f"file_path: {file_path}",
        ]

    def get_tool_text_end(self, result: dict, **kwargs) -> str:
        return f"written_bytes: {result['written_bytes']}"

    def print_verbose_output(self, result: dict):
        colored_print(f"Wrote {result['written_bytes']} bytes to file", color="YELLOW")

    def _run(self, intention_of_this_call: str, file_path: str, content: str, **kwargs) -> dict:
        with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
            written_bytes = f.write(content)
        return {
            "written_bytes": written_bytes
        }

from typing import List
from .base import BaseTool
from ..shared.utils import colored_print

class FileWriterTool(BaseTool):
    def get_tool_text_start(self, file_path: str, **kwargs) -> List[str]:
        return [
            "Write file",
            f"file_path: {file_path}",
        ]

    def get_tool_text_end(self, result: dict, **kwargs) -> str:
        return f"written_bytes: {result['written_bytes']}"

    def print_verbose_output(self, result: dict):
        colored_print(f"Wrote {result['written_bytes']} bytes to file", color="YELLOW")

    def _run(self, intention_of_this_call: str, file_path: str, content: str, **kwargs) -> dict:
        with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
            written_bytes = f.write(content)
        return {
            "written_bytes": written_bytes
        }
