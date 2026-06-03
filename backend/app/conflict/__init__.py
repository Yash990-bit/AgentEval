# backend/app/conflict/__init__.py
"""Package initialization for conflict detection engine.
Provides imports for public classes.
"""

from .models import Conflict, ConflictType, ConflictStatus
from .detector import ConflictDetector
from .tasks import detect_conflicts
