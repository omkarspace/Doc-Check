# This file makes the middleware directory a Python package
from .static_files import setup_static_files

__all__ = ['setup_static_files']
