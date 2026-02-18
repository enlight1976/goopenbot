"""Tests for goopenbot."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from goopenbot.tools.base import Tool
from goopenbot.tools.read import ReadTool
from goopenbot.tools.write import WriteTool
from goopenbot.tools.glob import GlobTool
from goopenbot.tools.grep import GrepTool
from goopenbot.tools.edit import EditTool
from goopenbot.tools.bash import BashTool
from goopenbot.tools import get_tool_by_name, get_tools_schema


class TestTools:
    """Test tool implementations."""

    def test_get_tool_by_name(self):
        """Test getting tool by name."""
        assert get_tool_by_name("read") is not None
        assert get_tool_by_name("write") is not None
        assert get_tool_by_name("glob") is not None
        assert get_tool_by_name("grep") is not None
        assert get_tool_by_name("edit") is not None
        assert get_tool_by_name("bash") is not None
        assert get_tool_by_name("nonexistent") is None

    def test_get_tools_schema(self):
        """Test getting tools schema."""
        schema = get_tools_schema()
        assert len(schema) == 6
        tool_names = [s["function"]["name"] for s in schema]
        assert "read" in tool_names
        assert "write" in tool_names

    def test_read_tool(self, tmp_path):
        """Test read tool."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        tool = ReadTool()
        result = tool.execute(file_path=str(test_file))

        assert result["success"] is True
        assert "Hello, World!" in result["output"]

    def test_read_tool_file_not_found(self):
        """Test read tool with non-existent file."""
        tool = ReadTool()
        result = tool.execute(file_path="/nonexistent/file.txt")

        assert result["success"] is False
        assert "not found" in result["output"].lower()

    def test_write_tool(self, tmp_path):
        """Test write tool."""
        test_file = tmp_path / "output.txt"

        tool = WriteTool()
        result = tool.execute(
            file_path=str(test_file),
            content="Test content"
        )

        assert result["success"] is True
        assert test_file.read_text() == "Test content"

    def test_write_tool_creates_directory(self, tmp_path):
        """Test write tool creates parent directories."""
        test_file = tmp_path / "subdir" / "output.txt"

        tool = WriteTool()
        result = tool.execute(
            file_path=str(test_file),
            content="Test"
        )

        assert result["success"] is True
        assert test_file.exists()

    def test_glob_tool(self, tmp_path):
        """Test glob tool."""
        # Create test files
        (tmp_path / "test1.txt").write_text("test")
        (tmp_path / "test2.txt").write_text("test")
        (tmp_path / "other.md").write_text("test")

        tool = GlobTool()
        result = tool.execute(pattern="*.txt", path=str(tmp_path))

        assert result["success"] is True
        assert "test1.txt" in result["output"]
        assert "test2.txt" in result["output"]
        assert "other.md" not in result["output"]

    def test_grep_tool(self, tmp_path):
        """Test grep tool."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    print('hello')\n    return True")

        tool = GrepTool()
        result = tool.execute(pattern="def hello", path=str(tmp_path), regex=False)

        assert result["success"] is True
        assert "def hello" in result["output"]

    def test_edit_tool(self, tmp_path):
        """Test edit tool."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")

        tool = EditTool()
        result = tool.execute(
            file_path=str(test_file),
            old_string="World",
            new_string="Python"
        )

        assert result["success"] is True
        assert test_file.read_text() == "Hello Python"

    def test_edit_tool_string_not_found(self, tmp_path):
        """Test edit tool with non-existent string."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")

        tool = EditTool()
        result = tool.execute(
            file_path=str(test_file),
            old_string="Nonexistent",
            new_string="Python"
        )

        assert result["success"] is False


class TestConfig:
    """Test configuration."""

    def test_load_config(self):
        """Test loading config."""
        from goopenbot.core.config import load_config, Config

        config = load_config()
        assert isinstance(config, Config)
        assert config.provider.model == "qwen2.5-coder:7b"

    def test_get_config_dir(self):
        """Test getting config directory."""
        from goopenbot.core.config import get_config_dir

        config_dir = get_config_dir()
        assert config_dir.exists()
        assert config_dir.name == "goopenbot"

    def test_get_data_dir(self):
        """Test getting data directory."""
        from goopenbot.core.config import get_data_dir

        data_dir = get_data_dir()
        assert data_dir.exists()
        assert data_dir.name == "goopenbot"


class TestSession:
    """Test session management."""

    def test_session_creation(self):
        """Test creating a session."""
        from goopenbot.core.session import Session

        session = Session.create(model="test-model")
        assert session.id is not None
        assert session.model == "test-model"
        assert len(session.messages) == 0

    def test_session_add_message(self):
        """Test adding messages to session."""
        from goopenbot.core.session import Session

        session = Session.create()
        session.add_message("user", "Hello")

        assert len(session.messages) == 1
        assert session.messages[0]["role"] == "user"
        assert session.messages[0]["content"] == "Hello"

    def test_session_store(self, tmp_path):
        """Test session storage."""
        from goopenbot.core.session import Session, SessionStore

        # Override data dir for test
        import goopenbot.core.config
        original_data_dir = goopenbot.core.config.get_data_dir
        goopenbot.core.config.get_data_dir = lambda: tmp_path

        try:
            store = SessionStore()
            session = Session.create(model="test")
            session.add_message("user", "Test")

            store.save(session)
            loaded = store.get(session.id)

            assert loaded is not None
            assert loaded.id == session.id
            assert loaded.model == "test"
            assert len(loaded.messages) == 1
        finally:
            goopenbot.core.config.get_data_dir = original_data_dir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
