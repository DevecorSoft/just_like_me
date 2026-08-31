#!/usr/bin/env python3
from importlib.resources import files
from pathlib import Path
import shutil

INSTRUCTION_TARGET_PATHS = [
    Path.home() / ".agents" / "instructions.md",
    Path.home() / ".copilot" / "copilot-instructions.md",
]


def install() -> None:
  source = files("just_like_me").joinpath("instructions.md")
  for target_path in INSTRUCTION_TARGET_PATHS:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target_path)
    print(f"Installed instructions to {target_path}")
