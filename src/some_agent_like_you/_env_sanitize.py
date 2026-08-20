"""Sanitize the interpreter environment before any third-party imports.

Users often have multiple Python installations (Homebrew, Nix, system) whose
site-packages leak into this tool's isolated venv via PYTHONPATH, causing
version-mismatch import errors (e.g. a Nix python3.13 pydantic shadowing the
vendored one). Strip foreign paths so the tool is immune to dirty shells.

Only runs when the process is one of this package's CLI entry points, so that
test runners and IDEs (which inject their own sys.path entries) are unaffected.
"""

import os as _os
import sys as _sys
import sysconfig as _sysconfig
from pathlib import Path as _Path

_CLI_ENTRY_POINTS = {"load_memory"}


def _is_cli_entry() -> bool:
  argv0 = _sys.argv[0] if _sys.argv else ""
  return _Path(argv0).stem in _CLI_ENTRY_POINTS


def sanitize() -> None:
  _os.environ.pop("PYTHONPATH", None)

  _purelib = _sysconfig.get_path("purelib")
  _sys.path[:] = [
    _p
    for _p in _sys.path
    if not _p or _p.startswith((_sys.prefix, _sys.base_prefix, _purelib))
  ]


if _is_cli_entry():
  sanitize()
