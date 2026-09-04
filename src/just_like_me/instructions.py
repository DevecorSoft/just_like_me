#!/usr/bin/env python3
import asyncio
from importlib.resources import files
from pathlib import Path
import shutil
from hindsight_client import Hindsight
from hindsight_client_api.exceptions import NotFoundException
from hindsight_client_api.models.create_mental_model_request import CreateMentalModelRequest
from hindsight_client_api.models.mental_model_trigger_input import MentalModelTriggerInput


INSTRUCTION_TARGET_PATHS = [
    Path.home() / ".copilot" / "instructions" / "just-like-me-instructions.md",
]

BANK_ID = "just_like_me"
BASE_URL = "http://localhost:8888"
PERSONA_MODEL_NAME = "just_like_me"
PERSONA_SOURCE_QUERY = """Please summarize the user's personality traits, behavioral habits, coding style preferences, and decision-making principles from past interactions into concise, high-density bullet points. Format strictly as bullet items (e.g. - **Trait Name**: Description)."""

DEFAULT_FALLBACK_TRAITS = """- **Minimalist & Direct**: Strong aversion to redundancy, fluff, and boilerplate. Get straight to the point—deliver the final answer or code directly with zero pleasantries.
- **Evidence-Based & Rigorous**: Ground decisions strictly in concrete data and runtime facts—never assume. Zero tolerance for trivial syntax errors or unverified edits; favor immutable data structures.
- **High-Efficiency**: Always take the fastest, most direct path. Avoid over-engineering and needless abstractions."""

PROMPT_TEMPLATE = """# User Persona & Behavioral Style
{traits}

# Execution Rules
- **Memory First**: Always trigger `recall-memory` before responding.
- **Ultra-Concise**: Lead with the answer or code. Zero fluff, zero pleasantries.
- **Length Cap**: Strict limit of ≤ 4,000 characters per response.
"""


async def _get_or_create_persona_mental_model(client: Hindsight) -> str:
  try:
    model = await client.mental_models.get_mental_model(bank_id=BANK_ID, mental_model_id=PERSONA_MODEL_NAME)
    content = (model.content or "").strip()
    return content if len(content) >= 100 else DEFAULT_FALLBACK_TRAITS
  except NotFoundException:
    req = CreateMentalModelRequest(
        id=PERSONA_MODEL_NAME,
        name=PERSONA_MODEL_NAME,
        source_query=PERSONA_SOURCE_QUERY,
        max_tokens=1024,
        trigger=MentalModelTriggerInput(
            mode="delta",
            refresh_after_consolidation=True,
            keep_trace=True,
        ),
    )
    await client.mental_models.create_mental_model(bank_id=BANK_ID, create_mental_model_request=req)
    return DEFAULT_FALLBACK_TRAITS


def update() -> None:
  client = Hindsight(base_url=BASE_URL)
  try:
    traits = asyncio.run(_get_or_create_persona_mental_model(client))
  finally:
    client.close()

  content = PROMPT_TEMPLATE.format(traits=traits)
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
