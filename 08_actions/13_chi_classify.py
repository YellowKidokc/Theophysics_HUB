def classify(text: str):
    """Return a lightweight chi-channel classification for popup triage."""
    lowered = (text or "").lower()
    channels = {
        "analytical": ["because", "therefore", "evidence", "logic", "model", "system"],
        "creative": ["imagine", "story", "metaphor", "beauty", "dream", "poem"],
        "practical": ["todo", "step", "fix", "build", "ship", "test"],
        "emotional": ["feel", "love", "fear", "angry", "grief", "hope"],
    }
    scores = {name: sum(lowered.count(term) for term in terms) for name, terms in channels.items()}
    best = max(scores, key=scores.get) if any(scores.values()) else "general"
    return {"channel": best, "scores": scores, "length": len(text or "")}


def process(data):
    return classify(data.get("selection") or data.get("clipboard") or "")
