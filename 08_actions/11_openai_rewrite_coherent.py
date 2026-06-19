def process(data):
    import json
    import os
    import urllib.request
    from pathlib import Path

    text = data.get("selection") or data.get("clipboard") or ""
    if not text.strip():
        return "No text available."

    root = Path(__file__).resolve().parents[1]
    cfg = json.loads((root / "04_config" / "config.json").read_text(encoding="utf-8"))
    openai_cfg = cfg.get("openai", {})
    env_name = openai_cfg.get("api_key_env", "OPENAI_API_KEY")
    api_key = os.getenv(env_name, "").strip()
    if not api_key:
        return f"Missing API key. Set environment variable {env_name}."

    instruction = openai_cfg.get(
        "rewrite_instruction",
        "Rewrite this text into coherent prose with corrected punctuation and spelling while preserving meaning.",
    )
    model = openai_cfg.get("model", "gpt-4.1-mini")

    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": instruction}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": text}],
            },
        ],
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return f"OpenAI request failed: {e}"

    if isinstance(body.get("output_text"), str) and body["output_text"].strip():
        return body["output_text"].strip()

    chunks = []
    for item in body.get("output", []):
        for content in item.get("content", []):
            text_value = content.get("text")
            if isinstance(text_value, str):
                chunks.append(text_value)

    return "\n".join(chunks).strip() or "OpenAI returned no text."
