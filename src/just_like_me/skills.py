#!/usr/bin/env python3
from importlib.resources import files
from pathlib import Path
import shutil

SKILL_NAME = "recall-memory"
SKILL_TARGET_PATH = Path.home() / ".agents" / "skills" / SKILL_NAME / "SKILL.md"
INSTRUCTION_TARGET_PATHS = [
    Path.home() / ".agents" / "instructions.md",
    Path.home() / ".copilot" / "copilot-instructions.md",
]


def install_skills() -> None:
  source = files("just_like_me").joinpath("skills", SKILL_NAME, "SKILL.md")
  SKILL_TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)
  shutil.copyfile(source, SKILL_TARGET_PATH)
  print(f"Installed skill to {SKILL_TARGET_PATH}")


def install_instructions() -> None:
  source = files("just_like_me").joinpath("instructions.md")
  for target_path in INSTRUCTION_TARGET_PATHS:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target_path)
    print(f"Installed instructions to {target_path}")


def main() -> None:
  install_skills()
  install_instructions()

