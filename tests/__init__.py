"""Integration tests for the package."""

# pylint: disable=unused-import

try:
    from IPython.terminal.debugger import TerminalPdb as Debugger
except ImportError:
    from pdb import Pdb as Debugger
