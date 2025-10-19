"""
Main entry point for the markdown_translator package.

This module allows the package to be run as a module using:
    python -m markdown_translator
"""

from .cli import cli_entry_point

if __name__ == '__main__':
    cli_entry_point()
