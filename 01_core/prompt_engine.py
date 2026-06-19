"""Prompt template lookup and variable expansion."""

from __future__ import annotations

from models import PromptRecord


def expand_prompt(template: str, variables: dict[str, str]) -> str:
    """Substitute ``{name}`` placeholders in ``template`` with ``variables``."""
    text = template
    for key, value in variables.items():
        text = text.replace("{" + key + "}", value)
    return text


class PromptEngine:
    """Resolves prompt templates by name and expands them against variables."""

    def __init__(self, prompts: list[PromptRecord]):
        self._by_name = {prompt.name: prompt for prompt in prompts}

    def names(self) -> list[str]:
        return list(self._by_name)

    def get(self, name: str) -> PromptRecord:
        try:
            return self._by_name[name]
        except KeyError as exc:
            raise KeyError(f"Unknown prompt: {name}") from exc

    def render(self, name: str, text: str = "", **variables: str) -> str:
        prompt = self.get(name)
        return expand_prompt(prompt.content, {"text": text, **variables})
