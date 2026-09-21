#!/usr/bin/env python3
import argparse
from importlib.resources import files
from pathlib import Path

SKILL_NAME = "recall-discernment"
SKILL_TARGET_PATH = Path.home() / ".agents" / "skills" / SKILL_NAME / "SKILL.md"


def install() -> None:
  parser = argparse.ArgumentParser(description="Install recall-discernment skill")
  parser.add_argument("--base-url", required=True, help="Hindsight base URL")
  args = parser.parse_args()

  base_url = args.base_url.rstrip("/")
  source = files("just_like_me").joinpath("skills", SKILL_NAME, "SKILL.md")
  content = source.read_text(encoding="utf-8").replace("{base_url}", base_url)
  SKILL_TARGET_PATH.parent.mkdir(parents=True, exist_ok=True)
  SKILL_TARGET_PATH.write_text(content, encoding="utf-8")
  print(f"Installed skill to {SKILL_TARGET_PATH}")


if __name__ == "__main__":
  install()
