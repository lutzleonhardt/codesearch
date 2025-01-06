from typing import TypedDict, List


class BaseToolResult(TypedDict):
    """Base result type for all tools

    Attributes:
        total_count: Total number of items available (entries/lines/bytes)
        returned_count: Number of items actually returned (for pagination/limits)
        items: The actual content as list of strings (entries/lines/output)
    """
    total_count: int
    returned_count: int
    items: List[str]

# Extend like this if needed
# T = TypeVar('T')
# class ExtendedToolResult(BaseToolResult, Generic[T]):
#     """Extended result type that allows tools to add custom data
#
#     Attributes:
#         extra_data: Tool-specific additional data of type T
#     """
#     extra_data: T
