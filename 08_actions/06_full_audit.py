def process(data):
    import os
    import subprocess
    import tempfile

    text = data.get("selection") or data.get("clipboard") or ""
    tmp = os.path.join(tempfile.gettempdir(), "textgo_audit.md")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)

    try:
        r = subprocess.run(
            ["python", r"X:\04_STATIONS\_shared\writing_audit\combined_theophysics_paper_auditor.py", tmp],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return r.stdout or r.stderr or "No output"
    except Exception as e:
        return f"Error: {e}"
