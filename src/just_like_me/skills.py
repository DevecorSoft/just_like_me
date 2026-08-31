#!/usr/bin/env python3
from importlib.resources import files
from pathlib import Path
import shutil

SKILL_NAME = "recall-memory"
SKILL_TARGET_PATH = Path.home() / ".agents" / "skills" / SKILL_NAME / "SKILL.md"


def install() -> None:
  source = files("just_like_me").joinpath("skills", SKILL_NAME, "SKILL.md")
  SKILL_TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)
  shutil.copyfile(source, SKILL_TARGET_PATH)
  print(f"Installed skill to {SKILL_TARGET_PATH}")
