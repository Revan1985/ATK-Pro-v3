"""Shim module for compatibility with tests and older imports.
Re-exports the main GUI entrypoints from `src.main_gui_qt`.
"""
from .main_gui_qt import *  # re-export everything for compatibility

__all__ = [name for name in dir() if not name.startswith("_")]
