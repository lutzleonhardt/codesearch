from dataclasses import dataclass
from typing import TypeVar, Generic

from pydantic import BaseModel

T = TypeVar('T')


@dataclass
class PartialContent(Generic[T]):
    """Generic wrapper for partial content responses"""
    total_length: int
    returned_length: int
    content: T
    error: bool = False
    aborted: bool = False

    @property
    def is_complete(self) -> bool:
        return self.returned_length == self.total_length

    @property
    def missing_length(self) -> int:
        return self.total_length - self.returned_length


@dataclass
class Deps:
    """Dependencies for the agent"""
    limit: int = 100
    project_root: str = "."
    verbose: bool = False


class AgentOutput(BaseModel):
    answer: str
    error_tool_call: str
