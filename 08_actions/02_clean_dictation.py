def process(data):
    import re

    text = data.get("selection") or data.get("clipboard") or ""
    text = re.sub(r"(?i)\b(um+|uh+|er+|ah+)\b\s*", "", text)
    text = re.sub(r"(?i)\b(you know|I mean|like)\b\s*,?\s*", "", text)
    text = re.sub(r"(?i)\b(\w+)\s+\1\b", r"\1", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"([.!?])\s+([a-z])", lambda m: m.group(1) + " " + m.group(2).upper(), text)
    text = re.sub(r"^([a-z])", lambda m: m.group(1).upper(), text)
    text = re.sub(r"\bi\b", "I", text)
    return text.strip()
