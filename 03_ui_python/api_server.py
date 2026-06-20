"""FastAPI server for Theophysics HUB HTML surfaces."""

from __future__ import annotations

import ast
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
sys.path.insert(0, str(ROOT / "01_core"))

from action_registry import ActionRegistry
from clipboard_store import ClipboardStore
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


class ActionRequest(BaseModel):
    text: str = ""
    selection: str | None = None
    clipboard: str | None = None


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


def _action_registry() -> ActionRegistry:
    return ActionRegistry(ROOT)


def _clipboard_store() -> ClipboardStore:
    return ClipboardStore.from_config(ROOT, _read_json(SETTINGS_FILES["config"]).get("clipboard", {}))


def _action_payload(req: ActionRequest, trigger_source: str = "api") -> dict[str, Any]:
    text = req.text or req.selection or req.clipboard or ""
    return {
        "selection": req.selection if req.selection is not None else text,
        "clipboard": req.clipboard if req.clipboard is not None else text,
        "text": text,
        "trigger_source": trigger_source,
    }


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
        "Clean Dictation": "clean_dictation",
        "Compress": "compress",
        "Rephrase x5": "rephrase_5_ways",
        "Fix Grammar": "grammar_fix",
    }
    action_id = actions.get(req.action)
    if action_id is None:
        raise HTTPException(status_code=404, detail=f"Unknown rewrite action: {req.action}")
    result = _action_registry().run(
        action_id,
        {"selection": req.text, "clipboard": req.text, "text": req.text, "trigger_source": "api/rewrite"},
    )
    if not result.ok:
        raise HTTPException(status_code=500, detail=result.error)
    return JSONResponse({"ok": True, "result": result.output})


@app.get("/api/popup-actions")
def popup_actions() -> JSONResponse:
    actions = [
        {
            "id": record.id,
            "name": record.name,
            "entry": str(record.entry.relative_to(ROOT)),
            "description": record.description,
        }
        for record in _action_registry().list_actions()
    ]
    return JSONResponse({"ok": True, "actions": actions})


@app.post("/api/action/{action_id}")
def run_popup_action(action_id: str, req: ActionRequest) -> JSONResponse:
    result = _action_registry().run(action_id, _action_payload(req, "api/action"))
    status = 200 if result.ok else 404 if result.error and "Unknown action" in result.error else 500
    return JSONResponse(
        {"ok": result.ok, "action_id": action_id, "result": result.output, "error": result.error},
        status_code=status,
    )


@app.get("/api/clips/ranked")
def ranked_clips() -> JSONResponse:
    slots = _clipboard_store().ranked_slots()
    return JSONResponse({"ok": True, "clips": slots})

@app.get("/api/action/chi_classify")
def chi_classify_text(text: str) -> JSONResponse:
    """Compatibility endpoint for quick chi channel classification."""
    result = _action_registry().run(
        "chi_classify",
        {"selection": text, "clipboard": text, "text": text, "trigger_source": "api/action/chi_classify"},
    )
    if not result.ok:
        return JSONResponse({"ok": False, "error": result.error}, status_code=500)
    try:
        payload = ast.literal_eval(result.output)
    except (ValueError, SyntaxError):
        payload = result.output
    return JSONResponse({"ok": True, "result": payload})

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
