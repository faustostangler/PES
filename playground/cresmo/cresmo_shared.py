"""Import wrapper allowing 'import cresmo_shared' for cresmo-shared.py."""

import importlib.util
from pathlib import Path

_shared_path = Path(__file__).parent / "cresmo-shared.py"
_spec = importlib.util.spec_from_file_location("cresmo_shared_mod", _shared_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Export all symbols from cresmo-shared.py
globals().update({k: v for k, v in _mod.__dict__.items() if not k.startswith("__")})
