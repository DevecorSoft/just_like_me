#!/usr/bin/env python3
from importlib.resources import files
from pathlib import Path
import shutil

SKILL_NAME = "recall-memory"
TARGET_PATH = Path.home() / ".agents" / "skills" / SKILL_NAME / "SKILL.md"


def main() -> None:
  source = files("some_agent_like_you").joinpath("skills", SKILL_NAME, "SKILL.md")
  TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)
  shutil.copyfile(source, TARGET_PATH)
  print(f"Installed skill to {TARGET_PATH}")


if __name__ == "__main__":
  main()
