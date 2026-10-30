"""Load the animate engine for QC tools.

Resolves the engine module via MOTIONPLATES_ENGINE env var, falling back to the
locked engine at recipes/presets/locked/engine/animate_b9_b719e8d8.py.
"""
import importlib.util
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_ENGINE = _REPO_ROOT / "recipes" / "presets" / "locked" / "engine" / "animate_b9_b719e8d8.py"


def _load_module_from_path(name: str, path: Path):
    """Load a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_animate():
    """Load and return the animate engine module.

    Resolution order:
    1. MOTIONPLATES_ENGINE env var (path to engine .py file)
    2. Default locked engine at recipes/presets/locked/engine/animate_b9_b719e8d8.py

    Raises:
        FileNotFoundError: If the engine file is not found.
        ImportError: If the module cannot be loaded.
    """
    engine_path_str = os.environ.get("MOTIONPLATES_ENGINE")

    if engine_path_str:
        engine_path = Path(engine_path_str)
        if not engine_path.exists():
            raise FileNotFoundError(
                f"MOTIONPLATES_ENGINE={engine_path_str} does not exist. "
                f"Set MOTIONPLATES_ENGINE to a valid engine .py file path, "
                f"or unset it to use the default locked engine."
            )
    else:
        engine_path = _DEFAULT_ENGINE
        if not engine_path.exists():
            raise FileNotFoundError(
                f"Default locked engine not found at {engine_path}. "
                f"Set MOTIONPLATES_ENGINE to the path of the engine .py file."
            )

    return _load_module_from_path("animate", engine_path)


def get_root() -> str:
    """Get the project root path from MOTIONPLATES_ROOT env var or default.

    Returns:
        The root path string. Defaults to '/workspace/posterity' if MOTIONPLATES_ROOT
        is not set (preserving existing behavior on the owner's machine).
    """
    return os.environ.get("MOTIONPLATES_ROOT", "/workspace/posterity")
