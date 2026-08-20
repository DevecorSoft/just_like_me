# Sanitizes the environment only when running as a CLI entry point; no-op
# for test runners and IDEs. See _env_sanitize for details.
from some_agent_like_you import _env_sanitize as _env_sanitize


def main() -> None:
    print("Hello from some-agent-like-you!")
