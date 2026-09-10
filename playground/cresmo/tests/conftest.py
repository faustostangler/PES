"""Pytest fixtures and environment configuration for Cresmo test suite."""

from pathlib import Path
import sys

# Ensure playground/cresmo is in sys.path for all tests in this directory
cresmo_dir = Path(__file__).resolve().parent.parent
if str(cresmo_dir) not in sys.path:
    sys.path.insert(0, str(cresmo_dir))
