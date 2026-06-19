"""OpenAI-backed coherent rewrite action."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from config_loader import ConfigLoader


def _extract_text(body: dict[str, Any]) -> str:
    if isinstance(body.get("output_text"), str) and body["output_text"].strip():
        return body["output_text"].strip()

    chunks: list[str] = []
    for item in body.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if isinstance(content, dict) and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    return "\n".join(chunks).strip()


def process(data: dict[str, Any]) -> str:
    """Rewrite selected or clipboard text while preserving the user's meaning."""
    text = str(data.get("selection") or data.get("clipboard") or "")
    if not text.strip():
        return "No text available."

    root = Path(__file__).resolve().parents[1]
    openai_cfg = ConfigLoader(root).app_config().get("openai", {})
    env_name = str(openai_cfg.get("api_key_env", "OPENAI_API_KEY"))
    api_key = os.getenv(env_name, "").strip()
    if not api_key:
        raise RuntimeError(f"Missing API key. Set environment variable {env_name}.")

    instruction = str(
        openai_cfg.get(
            "rewrite_instruction",
            "Rewrite this text into coherent prose with corrected punctuation and spelling while preserving meaning.",
        )
    )
    model = str(openai_cfg.get("model", "gpt-4.1-mini"))

    request_body = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": instruction}]},
            {"role": "user", "content": [{"type": "input_text", "text": text}]},
        ],
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(request_body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"OpenAI request failed with HTTP {exc.code}: {detail}") from exc
    except Exception as exc:
        raise RuntimeError(f"OpenAI request failed: {exc}") from exc

    return _extract_text(body) or "OpenAI returned no text."
