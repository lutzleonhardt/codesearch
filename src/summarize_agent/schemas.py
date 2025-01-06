from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class SummarizerDeps:
    """Dependencies for the summarizer agent"""
    max_lines: int = 1000
    verbose: bool = False

class SummarizerOutput(BaseModel):
    summary: str
