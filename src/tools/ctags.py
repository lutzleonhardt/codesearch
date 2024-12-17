import logging
import os
import subprocess
from typing import List, TypedDict

from .base import BaseTool, ToolAbortedException
from ..shared import colored_print

logger = logging.getLogger(__name__)

class CtagsEntry(TypedDict):
    symbol: str
    file: str
    pattern: str
    kind: str
    line: int

class CtagsPage(TypedDict):
    total_entries: int
    returned_entries: int
    entries: List[CtagsEntry]

class CtagsTool(BaseTool):
    def print_verbose_output(self, result: CtagsPage):
        for entry in result['entries']:
            colored_print(f"{entry['kind']} {entry['symbol']} @ {entry['file']} line {entry['line']}", color="YELLOW")
    def get_tool_text_start(self, action: str, input_path: str = "", symbol: str = "", kind: str = "", **kwargs) -> List[str]:
        return [
            "Query ctags",
            f"action: {action}",
            f"input_path: {input_path}",
            f"symbol: {symbol}",
            f"kind: {kind}",
        ]

    def get_tool_text_end(self, result: CtagsPage) -> str:
        return f"total_entries: {result['total_entries']}, returned_entries: {result['returned_entries']}"

    def _run(self, action: str, input_path: str = "", symbol: str = "", kind: str = "", limit: int = 50, exclude_dirs: List[str] = None, isSymbolRegex: bool = False, **kwargs) -> CtagsPage:
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
            return {"total_entries": 0, "returned_entries": 0, "entries": []}

        # For readtags-based queries, ensure tags file exists
        if not os.path.exists(tags_file):
            logger.error("No tags file found. Run 'generate_tags' first.")
            #return {"total_entries": 0, "returned_entries": 0, "entries": []}
            raise ToolAbortedException("No tags file found. Run 'generate_tags' first.")

        # Base command with extension fields and line numbers
        base_cmd = ["readtags", "-t", tags_file, "-e", "-n"]

        if action == 'filter':
            # Unified logic
            if isSymbolRegex:
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
                    cmd = base_cmd + ["-l", "-Q", f'(eq? $kind "{kind}")']
                else:
                    logger.error(f"Unknown action: {action}")
                    return {"total_entries": 0, "returned_entries": 0, "entries": []}

        else:
            logger.error(f"Unknown action: {action}")
            raise ToolAbortedException("Unknown action")

        # Run readtags command and parse results
        output = self._run_command(cmd)
        entries = self._parse_readtags_output(output)

        # Truncate results
        truncated = entries[:limit]

        return {
            "total_entries": len(entries),
            "returned_entries": len(truncated),
            "entries": truncated
        }

    def _run_command(self, cmd: List[str]) -> str:
        import subprocess
        logger.info(f"Running command: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr}")
            return ""

    def _parse_readtags_output(self, output: str) -> List[CtagsEntry]:
        entries = []
        # readtags output format (default) per line:
        # symbol  file    ex_cmd  ext_fields...
        # Typically: SYMBOL  FILE  /pattern/  kind:[a-zA-Z]
        # We'll parse line-by-line
        for line in output.splitlines():
            if not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) < 3:
                continue
            symbol, file_, pattern = parts[:3]
            # Additional fields may contain kind:
            kind = ""
            line_num = 0
            for field in parts[3:]:
                if field.startswith("kind:"):
                    kind = field.split("kind:", 1)[1]
                elif field.startswith("line:"):
                    try:
                        line_num = int(field.split("line:", 1)[1])
                    except ValueError:
                        pass

            entries.append({
                "symbol": symbol,
                "file": file_,
                "pattern": pattern,
                "kind": kind,
                "line": line_num
            })
        return entries
