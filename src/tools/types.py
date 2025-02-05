from typing import TypedDict, List


class BaseToolResult(TypedDict, total=False):
    """Base result type for all tools

    Attributes:
        total_count: Total number of items available (entries/lines/bytes)
        returned_count: Number of items actually returned (for pagination/limits)
        items: The actual content as list of strings (entries/lines/output)
        summary: Optional summarized version of the output
        is_summarized: Flag indicating if the output was summarized
    """
    total_count: int
    returned_count: int
    items: List[str]
    summary: List[str] | None
    is_summarized: bool

# Extend like this if needed
# T = TypeVar('T')
# class ExtendedToolResult(BaseToolResult, Generic[T]):
#     """Extended result type that allows tools to add custom data
#
#     Attributes:
#         extra_data: Tool-specific additional data of type T
#     """
#     extra_data: T
