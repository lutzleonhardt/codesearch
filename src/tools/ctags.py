import logging
import os
import subprocess
from typing import List

from .base import BaseTool, ToolAbortedException
from ..shared import colored_print

logger = logging.getLogger(__name__)

from .types import BaseToolResult

class CtagsTool(BaseTool):
    def print_verbose_output(self, result: BaseToolResult):
        for line in result["items"]:
            colored_print(line, color="YELLOW")

    def get_tool_text_start(self, action: str, input_path: str = "", symbol: str = "", kind: str = "", limit: int = 50, is_symbol_regex: bool = False, **kwargs) -> List[str]:
        if action == 'generate_tags':
            return [
                "Query ctags",
                f"action: {action}",
                f"input_path: {input_path}"
            ]
        return [
            "Query ctags",
            f"action: {action}",
            f"input_path: {input_path}",
            f"symbol: {symbol}",
            f"kind: {kind}",
            f"is_symbol_regex: {is_symbol_regex}",
            f"limit: {limit} lines (it summarizes output if above)"
        ]


    def get_tool_text_end(self, result: BaseToolResult, **kwargs) -> str:
        action = kwargs.get('action', '')
        if action == 'generate_tags':
            return ""
        else:
            return super().get_tool_text_end(result, **kwargs)



    def _run(self, intention_of_this_call: str, action: str, input_path: str = "", symbol: str = "", kind: str = "", limit: int = 50, exclude_dirs: List[str] = None, is_symbol_regex: bool = False, **kwargs) -> BaseToolResult:
        """Run ctags/readtags actions."""
        # Run actions based on provided parameters
        if os.path.isdir(input_path):
            tags_file = os.path.join(input_path, 'tags')
        else:
            tags_file = f"{input_path}_tags"

        if action == 'generate_tags':
            if os.path.isdir(input_path):
                cwd = input_path
                git_ls_files = subprocess.run(["git", "ls-files"], stdout=subprocess.PIPE, check=True, text=True, cwd=cwd)
                ctags_cmd = ["ctags", "-f", "tags", "-L", "-"]
                subprocess.run(ctags_cmd, input=git_ls_files.stdout, text=True, check=True, cwd=cwd)
            else:
                cmd = ["ctags", "-R", "-f", tags_file]
                cmd.append(input_path)
                self._run_command(cmd)
            # After generation, no entries returned
            return BaseToolResult(total_count=0, returned_count=0, items=[])

        # For readtags-based queries, ensure tags file exists
        if not os.path.exists(tags_file):
            logger.error("No tags file found. Run 'generate_tags' first.")
            #return BaseToolResult(total_count=0, returned_count=0, items=[])
            raise ToolAbortedException("No tags file found. Run 'generate_tags' first.")

        # Base command with extension fields and line numbers
        base_cmd = ["readtags", "-t", tags_file, "-e", "-n"]

        symbol = None if symbol == "" else symbol
        symbol = None if symbol == "." else symbol

        kind = None if kind == "" else kind
        if action == 'filter':
            # Unified logic
            if is_symbol_regex:
                if symbol and kind:
                    cmd = base_cmd + ["-Q", f'(and (#/{symbol}/ $name) (eq? $kind "{kind}"))', "-l"]
                elif symbol:
                    cmd = base_cmd + ["-Q", f'(#/{symbol}/ $name)', "-l"]
                elif kind:
                    cmd = base_cmd + ["-Q", f'(eq? $kind "{kind}")', "-l"]
                else:
                    cmd = base_cmd + ["-l"]
            else:
                if not symbol and not kind:
                    cmd = base_cmd + ["-l"]
                elif symbol and kind:
                    cmd = base_cmd + ["-i", symbol, "-Q", f'(eq? $kind "{kind}")']
                elif symbol:
                    cmd = base_cmd + ["-i", symbol]
                elif kind:
                    cmd = base_cmd + ["-Q", f'(eq? $kind "{kind}")', "-l"]
                else:
                    logger.error(f"Unknown action: {action}")
                    return BaseToolResult(total_count=0, returned_count=0, items=[])

        else:
            logger.error(f"Unknown action: {action}")
            raise ToolAbortedException("Unknown action")

        # Run readtags command and get output lines
        output = self._run_command(cmd)
        lines = [line.strip() for line in output.splitlines() if line.strip()]

        # Truncate results if needed
        return BaseToolResult(
            total_count=len(lines),
            items=lines
        )

    def _run_command(self, cmd: List[str]) -> str:
        import subprocess
        logger.info(f"Running command: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr}")
            return ""

