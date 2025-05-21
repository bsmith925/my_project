"""Test version information."""

from my_project import __version__


def test_version():
    """Test that version is a string."""
    assert isinstance(__version__, str)