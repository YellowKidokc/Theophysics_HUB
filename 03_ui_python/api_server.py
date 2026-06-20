"""FastAPI server for Theophysics HUB HTML surfaces."""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "04_config"
HTML_DIR = ROOT / "02_ui_html"
SETTINGS_FILES = {
    "actions": CONFIG_DIR / "actions.json",
    "config": CONFIG_DIR / "config.json",
    "hotkeys": CONFIG_DIR / "hotkeys.json",
    "links": CONFIG_DIR / "links.json",
    "prompts": CONFIG_DIR / "prompts.json",
}

app = FastAPI(title="Theophysics HUB API")


class RewriteRequest(BaseModel):
    text: str = ""
    action: str = ""


class TTSRequest(BaseModel):
    text: str = ""


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def _clipboard_text() -> str:
    if platform.system() == "Windows":
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            return completed.stdout
    return os.environ.get("THEOPHYSICS_CLIPBOARD", "")


def _run_action(entry: str, text: str) -> str:
    path = ROOT / entry
    spec = importlib.util.spec_from_file_location(f"api_action_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import action module: {entry}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    processor = getattr(mod, "process", None)
    if not callable(processor):
        raise RuntimeError(f"Action does not expose process(data): {entry}")
    return str(processor({"selection": text, "clipboard": text, "trigger_source": "api"}) or "")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(HTML_DIR / "popup.html")


@app.get("/settings")
def settings_page() -> FileResponse:
    return FileResponse(HTML_DIR / "settings.html")


@app.get("/popup")
def popup_page() -> FileResponse:
    return FileResponse(HTML_DIR / "popup.html")


@app.get("/tts")
def tts_page() -> FileResponse:
    return FileResponse(HTML_DIR / "tts-engine.html")


@app.get("/api/clipboard/current")
def clipboard_current() -> JSONResponse:
    return JSONResponse({"ok": True, "text": _clipboard_text()})


@app.get("/api/settings/{name}")
def get_settings(name: str) -> JSONResponse:
    path = SETTINGS_FILES.get(name)
    if path is None:
        raise HTTPException(status_code=404, detail=f"Unknown settings file: {name}")
    return JSONResponse({"ok": True, "name": name, "path": str(path), "data": _read_json(path)})


@app.post("/api/settings/{name}")
async def save_settings(name: str, request: Request) -> JSONResponse:
    path = SETTINGS_FILES.get(name)
    if path is None:
        raise HTTPException(status_code=404, detail=f"Unknown settings file: {name}")
    data = await request.json()
    if isinstance(data, dict) and "data" in data and len(data) <= 3:
        data = data["data"]
    _atomic_write_json(path, data)
    return JSONResponse({"ok": True, "saved": name, "path": str(path)})


@app.post("/api/rewrite")
def rewrite(req: RewriteRequest) -> JSONResponse:
    actions = {
        "Clean Dictation": "08_actions/02_clean_dictation.py",
        "Compress": "08_actions/12_compress.py",
        "Rephrase x5": "08_actions/05_rephrase_5_ways.py",
        "Fix Grammar": "08_actions/04_grammar_fix.py",
    }
    entry = actions.get(req.action)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Unknown rewrite action: {req.action}")
    return JSONResponse({"ok": True, "result": _run_action(entry, req.text)})


@app.get("/api/action/chi_classify")
def chi_classify_text(text: str) -> JSONResponse:
    """Quick chi channel classification of text."""
    try:
        sys.path.insert(0, str(ROOT / "08_actions"))
        spec = importlib.util.spec_from_file_location(
            "chi_classify", ROOT / "08_actions" / "13_chi_classify.py"
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("Cannot import 13_chi_classify.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        classifier = getattr(mod, "classify", None)
        if not callable(classifier):
            raise RuntimeError("13_chi_classify.py does not expose classify(text)")
        result = classifier(text)
        return JSONResponse({"ok": True, "result": result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/tts")
def synthesize(req: TTSRequest) -> Response:
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="No text to synthesize.")
    if platform.system() == "Windows":
        out = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name)
        script = (
            "Add-Type -AssemblyName System.Speech;"
            "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            f"$s.SetOutputToWaveFile('{str(out)}');"
            "$s.Speak([Console]::In.ReadToEnd());$s.Dispose();"
        )
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            input=text,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise HTTPException(status_code=500, detail=(completed.stderr or "TTS failed").strip())
        return FileResponse(out, media_type="audio/mpeg", filename="speech.wav")
    raise HTTPException(status_code=501, detail="TTS audio generation is wired for Windows System.Speech.")


def start_api(host: str = "192.168.1.76", port: int = 3456) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if HTML_DIR.exists():
    app.mount("/static", StaticFiles(directory=HTML_DIR), name="static")
