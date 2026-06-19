# Theophysics HUB (Stratum)

A Windows-first productivity hub. Native hotkeys (AutoHotkey) capture intent and
selected text, a Python backend runs configured actions, and a PySide6 shell
presents panels for clipboard slots, prompts, links, and text-to-speech.

## Architecture

| Folder | Responsibility |
| --- | --- |
| `00_app_shell` | Startup, lifecycle, and the `stratum_cli` command bridge AHK shells out to |
| `01_core` | Backend domain logic: config, registries, action runner, clipboard store, TTS, logging |
| `02_ui_react` | Future React frontend (not yet wired into the running app) |
| `03_ui_python` | PySide6 shell window, panels, action popup, tray, single-instance routing |
| `04_config` | Source-of-truth JSON config (actions, prompts, links, hotkeys, providers) |
| `05_logs` | `app.log`, `actions.log`, and the persisted clipboard slot store |
| `06_engines` | Engine link pointers (NAS paths, created on demand) |
| `07_ahk` | Thin Windows-native trigger layer (`Stratum.ahk`) |
| `08_actions` | TextGO-style action scripts exposing `process(data: dict) -> str` |

### Data flow

```
AHK hotkey ──▶ stratum_cli.py <command> [panel]
                     │
                     ├─ build_core_services()  (01_core/services.py)
                     │     ├─ ConfigLoader        04_config/*.json
                     │     ├─ ActionRegistry      runs 08_actions/*.py
                     │     ├─ Registry            prompts / links / hotkeys
                     │     ├─ ClipboardManager    OS clipboard I/O
                     │     ├─ ClipboardStore      75 persisted slots
                     │     └─ TTSProvider         Windows SAPI
                     │
                     ├─ gui    ──▶ MainShellWindow (panels)
                     ├─ popup  ──▶ ActionPopup (selection preview + run)
                     └─ rewrite──▶ OpenAI coherent rewrite → clipboard
```

A single shell instance is enforced with a Qt local socket (named pipe). Panel
hotkeys route to the running window instead of opening duplicates — direct local
coordination, no HTTP service.

## Hotkeys

| Hotkey | Action |
| --- | --- |
| `Ctrl+Alt+G` | Open / focus the shell (Dashboard) |
| `Ctrl+Alt+C` | Open the Clipboard panel |
| `Ctrl+Alt+P` | Open the Prompts panel |
| `Ctrl+Alt+L` | Open the Links panel |
| `Ctrl+Alt+T` | Open the Text-to-Speech panel |
| `Ctrl+Space` | Rewrite selected/clipboard text via OpenAI and paste it back |
| `Middle Mouse` | Open the action popup for the current selection |

## Running locally

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Set the OpenAI key (env var name comes from `04_config/config.json`):
   ```
   setx OPENAI_API_KEY "sk-..."
   ```
3. Launch the shell directly (no AHK needed to try the GUI):
   ```
   python 00_app_shell\stratum_cli.py gui
   python 00_app_shell\stratum_cli.py gui clipboard
   python 00_app_shell\stratum_cli.py popup
   python 00_app_shell\stratum_cli.py rewrite
   ```
4. For native hotkeys, edit `RepoRoot` at the top of `07_ahk\Stratum.ahk` to your
   checkout path, then run it with AutoHotkey v2.

## Tests

Headless backend tests (no PySide6 or network required):

```
python -m unittest discover -s tests -v
```

## Configuration

All behavior is config-driven from `04_config`:

- `config.json` — app name, panel order, hotkey labels, clipboard slot count,
  TTS voice/rate, and the OpenAI provider (model, API-key env var, rewrite
  instruction). No secrets live in source.
- `actions.json` — action registry entries (`id`, `name`, `entry`, `description`).
- `prompts.json` / `links.json` / `hotkeys.json` — content for the panels.

## Status

**Production-worthy now**

- Config-driven action registry with validation and non-crashing `ActionResult`s.
- OpenAI rewrite isolated behind an action using the Responses API; key from env.
- Clipboard capture/manager with no UI coupling; 75-slot persistent store with
  atomic writes.
- Navigable PySide6 shell (Dashboard, Clipboard, Prompts, Links, TTS), action
  popup, tray, and single-instance panel routing.
- Structured file logging of action start/success/failure and trigger source.

**Still to refine**

- React frontend host (`02_ui_react`, `webview_window.py`) is intentionally stubbed.
- Per-slot clipboard hotkeys and richer slot metadata.
- Packaging/auto-start (`bootstrapper.py` writes a marker, not a real shortcut yet).
- Engine links in `06_engines` are documented paths, created on demand.
