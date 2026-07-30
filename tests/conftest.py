"""Pytest configuration — make ``Scripts/`` importable and expose shared paths."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "Scripts"

# Prepend so ``import configure`` resolves to ``Scripts/configure.py``.
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
