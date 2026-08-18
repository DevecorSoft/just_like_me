"""Sanitize the interpreter environment before any third-party imports.

Users often have multiple Python installations (Homebrew, Nix, system) whose
site-packages leak into this tool's isolated venv via PYTHONPATH, causing
version-mismatch import errors (e.g. a Nix python3.13 pydantic shadowing the
vendored one). Strip foreign paths so the tool is immune to dirty shells.
"""

import os as _os
import sys as _sys
import sysconfig as _sysconfig

_os.environ.pop("PYTHONPATH", None)

_purelib = _sysconfig.get_path("purelib")
_sys.path[:] = [
    _p
    for _p in _sys.path
    if not _p or _p.startswith((_sys.prefix, _sys.base_prefix, _purelib))
]


def main() -> None:
    print("Hello from some-agent-like-you!")
