'''backend/app/memory/__init__.py'''
"""Memory subsystem package.
Provides:
- MemoryManager
- STM, LTM helpers
- Shared/Episodic models
"""

from .manager import MemoryManager

__all__ = ["MemoryManager"]
