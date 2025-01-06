import shlex
import subprocess
from typing import List

from typing_extensions import LiteralString

from .base import BaseTool
from .types import BaseToolResult
from ..shared import colored_print


class TerminalTool(BaseTool):
    def get_tool_text_start(self, command: str, limit: int = 50, **kwargs) -> List[str]:
        return [
            "Run terminal command",
            f"command: {command}",
            f"limit: {limit} lines"
        ]

    def get_tool_text_end(self, result: BaseToolResult, **kwargs) -> str:
        return f"total_lines: {result['total_count']}, returned_lines: {result['returned_count']}"

    def print_verbose_output(self, result: BaseToolResult):
        for line in result['items']:
            colored_print(line, color="YELLOW")

    def _run(self, intention_of_this_call: str, command: str, limit: int = 50, root_dir: str = None, **kwargs) -> BaseToolResult:
        """Execute a shell command and return its output."""
        try:
            output = subprocess.check_output(
                shlex.split(command),
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=root_dir
            )
        except subprocess.CalledProcessError as e:
            output = e.output

        lines = output.splitlines()
        total = len(lines)
        truncated: list[LiteralString] = lines[:limit]
        if total > limit:
            text: LiteralString = "NOTE: The content is truncated, missing lines: " + str(total - limit)
            truncated.append(text)
        return BaseToolResult(
            total_count=total,
            returned_count=len(truncated),
            items=truncated
        )
