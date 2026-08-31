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
QUERY = "user coding style preference personality decision making constraints correction"

PROMPT_TEMPLATE = """# User Persona & Behavioral Style
{traits}

# Execution Rules
- **Memory First**: Always trigger `recall-memory` before responding.
- **Ultra-Concise**: Lead with the answer or code. Zero fluff, zero pleasantries.
- **Length Cap**: Strict limit of ≤ 4,000 characters per response.
"""


def fetch_style_observations(base_url: str = BASE_URL) -> list[str]:
  client = Hindsight(base_url=base_url)
  response = client.recall(
      bank_id=BANK_ID,
      query=QUERY,
      types=["observation"],
      budget="high",
      max_tokens=2048,
  )
  results = getattr(response, "results", response)
  client.close()
  return [getattr(r, "text", str(r)) for r in results if getattr(r, "text", None)]


def update() -> None:
  observations = fetch_style_observations()
  if not observations:
    print("No style observations found from Hindsight.")
    return

  traits_text = "\n".join(f"- {obs}" for obs in observations[:5])
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
