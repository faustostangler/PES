"""Import wrapper allowing 'import cresmo_ingestion' for cresmo-ingestion.py."""

import importlib.util
from pathlib import Path

_file_path = Path(__file__).parent / "cresmo-ingestion.py"
_spec = importlib.util.spec_from_file_location("cresmo_ingestion_mod", _file_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Export all symbols from cresmo-ingestion.py
globals().update({k: v for k, v in _mod.__dict__.items() if not k.startswith("__")})
