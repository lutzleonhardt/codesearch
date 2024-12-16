import logging
import os
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

    def get_tool_text_start(self, action: str, input_file: str = "", symbol: str = "", kind: str = "", **kwargs) -> List[str]:
        return [
            "Query ctags",
            f"action: {action}",
            f"input_file: {input_file}",
            f"symbol: {symbol}",
            f"kind: {kind}"
        ]

    def get_tool_text_end(self, result: CtagsPage) -> str:
        return f"total_entries: {result['total_entries']}, returned_entries: {result['returned_entries']}"

    def _run(self, action: str, input_file: str = "", symbol: str = "", kind: str = "", limit: int = 50, **kwargs) -> CtagsPage:
        """Run ctags/readtags actions."""
        # Run actions based on provided parameters
        tags_file = os.path.join(input_file, 'tags') if os.path.isdir(input_file) else 'tags'

        if action == 'generate_tags':
            # Generate/update tags file
            # Example: universal-ctags command (recursive)
            # Adjust as needed for your environment
            cmd = ["ctags", "-R", "-f", tags_file, input_file]
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

        if action == 'find_symbol':
            if not symbol:
                logger.error("No symbol provided for 'find_symbol'.")
                return {"total_entries": 0, "returned_entries": 0, "entries": []}
            # Direct symbol lookup with case insensitive matching
            cmd = base_cmd + ["-i", symbol]

        elif action == 'list_symbols':
            # List all symbols
            cmd = base_cmd + ["--list"]

        elif action == 'filter_by_kind':
            if not kind:
                logger.error("No kind provided for 'filter_by_kind'.")
                return {"total_entries": 0, "returned_entries": 0, "entries": []}
            # List all and filter by kind using -Q filter expression
            cmd = base_cmd + ["--list", "-Q", f"kind == '{kind}'"]

        else:
            logger.error(f"Unknown action: {action}")
            return {"total_entries": 0, "returned_entries": 0, "entries": []}

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
