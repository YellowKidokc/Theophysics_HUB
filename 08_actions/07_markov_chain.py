def process(data):
    import subprocess

    text = data.get("selection") or data.get("clipboard") or ""
    words = text.strip().split()
    seed = " ".join(words[-3:]) if len(words) >= 3 else text

    try:
        r = subprocess.run(
            ["python", r"X:\06_ENGINES\P07_markovify\generate.py", "--seed", seed, "--count", "5"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return r.stdout or "Markov engine not wired yet"
    except Exception:
        return "P07 Markov engine at X:\\06_ENGINES\\P07_markovify needs a generate.py entry point"
