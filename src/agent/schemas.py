from pydantic import BaseModel, Field
from typing import Any, Dict, List

class DirectoryToolRequest(BaseModel):
    path: str

class DirectoryToolResponse(BaseModel):
    structure: Dict[str, Any]

class AgentOutput(BaseModel):
    answer: str
    summary_of_tool_call: str
    error_tool_call: str
    potential_question: str


