from typing import Dict, Any


def create_tool_class(tool_name: str, tool_obj: Any):
    """Dynamically create a class that wraps a tool function."""

    class DynamicToolClass:
        def __init__(self, **kwargs):
            self.tool = tool_obj

        async def __call__(self, *args, **kwargs) -> Dict[str, Any]:
            return await self.tool(*args, **kwargs)

    DynamicToolClass.__name__ = tool_name
    return DynamicToolClass
