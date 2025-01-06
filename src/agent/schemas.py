from dataclasses import dataclass
from typing import TypeVar, Generic, List

from pydantic import BaseModel

T = TypeVar('T')


@dataclass
class MaybeSummarizedContent(Generic[T]):
    """Generic wrapper for partial content responses"""
    total_length: int
    content: List[str]
    error: bool = False
    aborted: bool = False
    is_summarized: bool = False

@dataclass
class Deps:
    """Dependencies for the agent"""
    limit: int = 100
    project_root: str = "."
    verbose: bool = False


class AgentOutput(BaseModel):
    answer: str
    confidence_1_to_10: int
