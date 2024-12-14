from pydantic import BaseModel
from typing import Any, Dict

class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

class ToolResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: str = None
