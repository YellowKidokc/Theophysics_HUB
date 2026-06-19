def process(data):
    import re
    from collections import Counter

    text = data.get("selection") or data.get("clipboard") or ""
    tokens = re.findall(r"[A-Za-z][A-Za-z'\-]*", text.lower())
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    lengths = [len(s.split()) for s in sents if s.strip()]
    motifs = ["coherence", "entropy", "grace", "faith", "truth", "collapse", "observer", "logos"]
    text_lower = text.lower()
    hits = {m: text_lower.count(m) for m in motifs if text_lower.count(m) > 0}
    bigrams = Counter(tuple(tokens[i:i + 2]) for i in range(len(tokens) - 1))
    repeated = [" ".join(k) for k, v in bigrams.most_common(10) if v >= 4]
    avg = sum(lengths) / len(lengths) if lengths else 0
    return f"Words: {len(tokens)} | Sentences: {len(sents)} | Avg len: {avg:.1f}\nMotifs: {hits}\nRepeated: {repeated}"
