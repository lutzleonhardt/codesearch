from typing import List

from .base import BaseTool
from .types import BaseToolResult
from ..shared.utils import colored_print


class FileWriterTool(BaseTool):
    def get_tool_text_start(self, file_path: str, **kwargs) -> List[str]:
        return [
            "Write file",
            f"file_path: {file_path}",
        ]

    def get_tool_text_end(self, result: BaseToolResult, **kwargs) -> str:
        return f"written_bytes: {result['total_count']}"

    def print_verbose_output(self, result: BaseToolResult):
        colored_print(f"Wrote {result['total_count']} bytes to file", color="YELLOW")

    def _run(self, intention_of_this_call: str, file_path: str, content: str, **kwargs) -> BaseToolResult:
        """Write content to a file and return the number of bytes written."""
        with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
            written_bytes = f.write(content)
        return BaseToolResult(
            total_count=written_bytes,
            returned_count=written_bytes,
            items=[f"Wrote {written_bytes} bytes"]
        )
