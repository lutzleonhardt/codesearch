import shlex
import subprocess
from typing import List

from .base import BaseTool
from .types import BaseToolResult
from ..shared import colored_print

#AI? when i ŕun a command which involves a pipe I got an error, i.e. find: paths must precede expression: `|' on find . -type f -name "*.razor" -o -name "*.razor.cs" | sort. Why? and how to fix

class TerminalTool(BaseTool):
    def get_tool_text_start(self, command: str, limit: int = 50, **kwargs) -> List[str]:
        return [
            "Run terminal command",
            f"command: {command}",
            f"limit: {limit} lines (it summarizes output if above)"
        ]

    def print_verbose_output(self, result: BaseToolResult):
        for line in result['items']:
            colored_print(line, color="YELLOW")

    def _run(self, intention_of_this_call: str, command: str, limit: int = 50, root_dir: str = None, **kwargs) -> BaseToolResult:
        """Execute a shell command and return its output."""
        try:
            # Use shell=True for commands with pipes or shell operators
            if any(op in command for op in ['|', '>', '<', '>>', '&&', '||']):
                output = subprocess.check_output(
                    command,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    cwd=root_dir,
                    shell=True  # Enable shell processing for commands with pipes/operators
                )
            else:
                # Original behavior for simple commands
                output = subprocess.check_output(
                    shlex.split(command),
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    cwd=root_dir
                )
        except subprocess.CalledProcessError as e:
            output = e.output

        lines = output.splitlines()
        return BaseToolResult(
            total_count=len(lines),
            items=lines
        )
