"""
Unit and regression test for the ccmp_tools package.
"""

# Import package, test suite, and other packages as needed
import ccmp_tools
import pytest
import sys


def test_ccmp_tools_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "ccmp_tools" in sys.modules
