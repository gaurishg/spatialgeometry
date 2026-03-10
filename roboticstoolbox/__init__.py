from __future__ import annotations

import sys
from importlib.machinery import PathFinder
from importlib.util import module_from_spec
from pathlib import Path
from types import ModuleType

import numpy as np


def _install_swift_stub(message: str) -> None:
    module = ModuleType("swift")

    class Swift:  # pragma: no cover - exercised via downstream imports
        def __init__(self, *args: object, **kwargs: object) -> None:
            raise ImportError(message)

    module.Swift = Swift
    module.__all__ = ["Swift"]
    sys.modules["swift"] = module


def _patch_numpy_compatibility() -> None:
    if not hasattr(np, "disp"):
        np.disp = print  # type: ignore[attr-defined]


def _load_real_roboticstoolbox() -> ModuleType:
    repo_root = Path(__file__).resolve().parent.parent
    search_paths = [
        path
        for path in sys.path
        if Path(path or ".").resolve() != repo_root
    ]
    spec = PathFinder.find_spec(__name__, search_paths)
    if spec is None or spec.loader is None:
        raise ModuleNotFoundError(
            "The installed roboticstoolbox package could not be found"
        )

    module = module_from_spec(spec)
    sys.modules[__name__] = module
    spec.loader.exec_module(module)
    return module


_patch_numpy_compatibility()
if np.lib.NumpyVersion(np.__version__) >= "2.0.0":
    _install_swift_stub(
        "swift-sim could not be imported because its binary extensions are "
        "incompatible with the active NumPy build. Importing "
        "roboticstoolbox still works, but Swift visualisation remains "
        "unavailable in this environment."
    )


_REAL_MODULE = _load_real_roboticstoolbox()
globals().update(_REAL_MODULE.__dict__)
