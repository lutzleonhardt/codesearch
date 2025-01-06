from dataclasses import dataclass
from typing import TypeVar, Generic, List

from pydantic import BaseModel

T = TypeVar('T')


@dataclass
class MaybeSummarizedContent(Generic[T]):
    """Generic wrapper for partial content responses"""
    total_length: int
    content: List[str]
    returned_length: int = 0
    error: bool = False
    aborted: bool = False
    result_is_complete: bool = True
    is_summarized: bool = False

    #@property
    #def result_is_complete(self) -> bool:
    #    return self.returned_length == self.total_length


@dataclass
class Deps:
    """Dependencies for the agent"""
    limit: int = 100
    project_root: str = "."
    verbose: bool = False


class AgentOutput(BaseModel):
    answer: str
    confidence_1_to_10: int
