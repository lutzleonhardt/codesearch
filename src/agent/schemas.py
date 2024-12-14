from pydantic import BaseModel
from typing import Any, Dict

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
    tool_requests: list[ToolRequest] = []
