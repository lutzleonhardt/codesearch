from src.tools.base import BaseTool

class MockTool(BaseTool):
    def run(self, **kwargs):
        return {"message": "mock"}

def test_mock_tool_instantiation():
    tool = MockTool()
    assert tool.run() == {"message": "mock"}
