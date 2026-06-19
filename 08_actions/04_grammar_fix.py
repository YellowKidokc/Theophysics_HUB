def process(data):
    text = data.get("selection") or data.get("clipboard") or ""
    return text.strip()
