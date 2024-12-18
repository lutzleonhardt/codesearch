from typing import List
from .base import BaseTool
from ..shared import colored_print
import os

class FileReaderTool(BaseTool):
    def get_tool_text_start(self, file_path: str, **kwargs) -> List[str]:
        return [
            "Read file",
            f"file_path: {file_path}",
        ]

    def get_tool_text_end(self, result: dict, **kwargs) -> str:
        return f"total_lines: {result['total_lines']}"

    def print_verbose_output(self, result: dict):
        for line in result['lines']:
            colored_print(line, color="YELLOW")

    def _run(self, file_path: str, **kwargs) -> dict:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.read().splitlines()
        return {
            "total_lines": len(lines),
            "returned_lines": len(lines),
            "lines": lines
        }
