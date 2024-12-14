import pytest
from unittest.mock import patch
import sys
import os
from io import StringIO

# Add src directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ..cli import main, colored_print

def test_colored_print():
    """Test that colored_print function works"""
    with patch('sys.stdout', new=StringIO()) as fake_out:
        colored_print("test message", color="BLUE")
        assert "test message" in fake_out.getvalue()

def test_main():
    """Test that main function runs without errors"""
    with patch('sys.stdout', new=StringIO()) as fake_out:
        main()
        assert "Welcome to codesearch!" in fake_out.getvalue()
