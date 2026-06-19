def process(data):
    import json
    import urllib.request

    text = data.get("selection") or data.get("clipboard") or ""
    prompt = (
        "Give exactly 5 alternative ways to write this sentence. Number them 1-5. "
        "Keep the same meaning but vary the style — formal, casual, punchy, academic, poetic. "
        "Output ONLY the 5 alternatives.\n\n"
        f"{text}"
    )
    body = json.dumps({"model": "mistral", "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        body,
        {"Content-Type": "application/json"},
    )

    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
        return resp.get("response", "Error: no response")
    except Exception as e:
        return f"Error: {e}\nIs Ollama running?"
