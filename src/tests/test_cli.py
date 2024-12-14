import pytest
from unittest.mock import patch
import sys
import os
from io import StringIO
from click.testing import CliRunner

# Add src directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ..cli import main, colored_print

def test_colored_print():
    """Test that colored_print function works"""
    with patch('sys.stdout', new=StringIO()) as fake_out:
        colored_print("test message", color="BLUE")
        assert "test message" in fake_out.getvalue()

def test_main(monkeypatch):
    """Test that main function runs with CLI arguments"""
    # Mock input() to return 'q' to exit the loop
    monkeypatch.setattr('builtins.input', lambda: 'q')
    
    runner = CliRunner()
    result = runner.invoke(main, ['--verbose', '--root-dir', 'my_project'])
    assert result.exit_code == 0
    assert "[codesearch]" in result.output
    assert "my_project" in result.output
