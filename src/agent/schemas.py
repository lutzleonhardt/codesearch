from pydantic import BaseModel, Field
from typing import Any, Dict, List

class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

class ToolResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: str = None

class AgentInput(BaseModel):
    user_query: str

class AgentOutput(BaseModel):
    summary: str
    tool_requests: List[ToolRequest] = Field(default_factory=list)
