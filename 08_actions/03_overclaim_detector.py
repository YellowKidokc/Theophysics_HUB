def process(data):
    import re

    text = data.get("selection") or data.get("clipboard") or ""
    strong = ["proves", "undeniable", "impossible", "always", "never", "must", "cannot", "certain", "irrefutable"]
    findings = []

    for i, line in enumerate(text.split("\n"), 1):
        for term in strong:
            if re.search(r"\b" + term + r"\b", line, re.I):
                findings.append(f"L{i}: '{term}' — {line.strip()[:80]}")

    if not findings:
        return "No overclaims detected."
    return "OVERCLAIMS FOUND:\n" + "\n".join(findings)
