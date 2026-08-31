#!/usr/bin/env python3
from importlib.resources import files
from pathlib import Path
import shutil
from hindsight_client import Hindsight

INSTRUCTION_TARGET_PATHS = [
    Path.home() / ".agents" / "instructions.md",
    Path.home() / ".copilot" / "copilot-instructions.md",
]

BANK_ID = "just_like_me"
BASE_URL = "http://localhost:8888"
REFLECT_QUERY = """Please summarize the user's personality traits, behavioral habits, coding style preferences, and decision-making principles from past interactions into 3-5 concise, high-density bullet points. Format strictly as bullet items (e.g. - **Trait Name**: Description)."""

PROMPT_TEMPLATE = """# User Persona & Behavioral Style
{traits}

# Execution Rules
- **Memory First**: Always trigger `recall-memory` before responding.
- **Ultra-Concise**: Lead with the answer or code. Zero fluff, zero pleasantries.
- **Length Cap**: Strict limit of ≤ 4,000 characters per response.
"""


def fetch_style_by_reflect(base_url: str = BASE_URL) -> str:
  client = Hindsight(base_url=base_url)
  response = client.reflect(
      bank_id=BANK_ID,
      query=REFLECT_QUERY,
      budget="low",
      max_tokens=1024,
  )
  client.close()
  return response.text.strip() if response and response.text else ""


def reflect() -> None:
  traits_text = fetch_style_by_reflect()
  if not traits_text:
    print("No reflect response returned from Hindsight.")
    return

  content = PROMPT_TEMPLATE.format(traits=traits_text)

  instructions_file = Path(__file__).parent / "instructions.md"
  instructions_file.write_text(content, encoding="utf-8")
  print(f"Updated {instructions_file}")
  install()


def install() -> None:
  source = files("just_like_me").joinpath("instructions.md")
  for target_path in INSTRUCTION_TARGET_PATHS:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target_path)
    print(f"Installed instructions to {target_path}")
