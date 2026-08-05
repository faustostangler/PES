"""Import wrapper allowing 'import cresmo_pipeline' for cresmo-pipeline.py."""

import importlib.util
from pathlib import Path

_file_path = Path(__file__).parent / "cresmo-pipeline.py"
_spec = importlib.util.spec_from_file_location("cresmo_pipeline_mod", _file_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Export all symbols from cresmo-pipeline.py
globals().update({k: v for k, v in _mod.__dict__.items() if not k.startswith("__")})
