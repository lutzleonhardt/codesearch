from .base import BaseTool
from ..shared import colored_print
import subprocess
import shlex
from typing import TypedDict, List

class CommandResult(TypedDict):
    total_lines: int
    returned_lines: int
    lines: List[str]

class TerminalTool(BaseTool):
    def get_tool_text_start(self, command: str, limit: int = 50, **kwargs) -> List[str]:
        return [
            "Run terminal command",
            f"command: {command}",
            f"limit: {limit} lines"
        ]

    def get_tool_text_end(self, result: CommandResult, **kwargs) -> str:
        return f"total_lines: {result['total_lines']}, returned_lines: {result['returned_lines']}"

    def print_verbose_output(self, result: CommandResult):
        for line in result['lines']:
            colored_print(line, color="YELLOW")

    def _run(self, command: str, limit: int = 50, **kwargs) -> CommandResult:
        try:
            output = subprocess.check_output(shlex.split(command), stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            output = e.output

        lines = output.splitlines()
        total = len(lines)
        truncated = lines[:limit]
        return {
            "total_lines": total,
            "returned_lines": len(truncated),
            "lines": truncated
        }
