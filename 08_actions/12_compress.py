def process(data):
    import re

    text = data.get("selection") or data.get("clipboard") or ""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text
