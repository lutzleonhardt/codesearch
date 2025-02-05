from typing import List
from .base import BaseTool
from .types import BaseToolResult
from ..shared import colored_print

class FileReaderTool(BaseTool):
    def get_tool_text_start(self, file_path: str, limit: int = 50, **kwargs) -> List[str]:
        return [
            "Read file",
            f"file_path: {file_path}",
            f"limit: {limit} lines (it summarizes output if above)"
        ]

    def print_verbose_output(self, result: BaseToolResult):
        for line in result['items']:
            colored_print(line, color="YELLOW")

    def _run(self, intention_of_this_call: str, file_path: str, **kwargs) -> BaseToolResult:
        """Read a file and return its contents as a BaseToolResult."""
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.read().splitlines()
        return BaseToolResult(
            total_count=len(lines),
            items=lines
        )
