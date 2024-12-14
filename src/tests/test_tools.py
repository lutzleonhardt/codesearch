from src.tools.base import BaseTool
from src.tools.directory import DirectoryTool
import tempfile
import os

class MockTool(BaseTool):
    def run(self, **kwargs):
        return {"message": "mock"}

def test_mock_tool_instantiation():
    tool = MockTool()
    assert tool.run() == {"message": "mock"}

def test_directory_tool():
    with tempfile.TemporaryDirectory() as tmpdir:
        open(os.path.join(tmpdir, "file.txt"), "w").close()
        os.mkdir(os.path.join(tmpdir, "subdir"))
        dt = DirectoryTool()
        result = dt.run(path=tmpdir)
        assert "files" in result and "dirs" in result
        assert "file.txt" in result["files"]
        assert len(result["dirs"]) == 1
