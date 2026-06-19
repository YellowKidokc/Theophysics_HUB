# Stratum One-Shot Build Prompt

You are taking over a Windows desktop productivity app scaffold at `D:\GitHub\stratum`.

Your job is to turn this scaffold into the first coherent working version of the app, not to brainstorm endlessly.

## Non-Negotiable Architecture

- `07_ahk/` stays in the project.
- `AHK` is the Windows-native glue for:
  - global hotkeys
  - mouse middle-button trigger
  - selection-trigger workflows
- `Python` is the backend brain for:
  - action registry
  - clipboard and selection processing
  - AI/provider integration
  - engine preferences
  - persistence
- `PySide6` is the desktop shell for:
  - tray icon
  - popup windows
  - embedded web UI if needed
  - lifecycle management
- `React` is the preferred long-term front-end for settings/dashboard/panel UIs

Do not remove `AHK` and do not replace it with a pure browser or pure Python keyboard-hook solution unless you can prove a Windows-native alternative is more reliable.

## Current Repo State

This repo is a scaffold, not a finished app.

Existing structure:

- `00_app_shell/`
- `01_core/`
- `02_ui_react/`
- `03_ui_python/`
- `04_config/`
- `05_logs/`
- `06_engines/`
- `07_ahk/`
- `08_actions/`

Already present:

- action files in `08_actions/`
- action definitions in `04_config/actions.json`
- stub registries in `01_core/`
- stub AHK glue in `07_ahk/Stratum.ahk`
- placeholder React files in `02_ui_react/src/`
- placeholder PySide files in `03_ui_python/`

## Product Direction

This app is a panel-first Windows system with these major tools:

1. Clipboard
2. Prompt Picker
3. Research Links
4. TTS
5. Middle-click action popup

The UI style should be:

- dark
- compact
- intentional
- not generic SaaS dashboard styling
- comfortable with mono-heavy typography

## Immediate Build Goal

Build the first working slice around the action popup and backend integration.

That means:

1. Implement a real action registry that loads `04_config/actions.json`
2. Implement a real runner that imports action modules from `08_actions/`
3. Implement a selection/clipboard payload flow
4. Implement a PySide6 popup window that:
   - appears on command
   - shows the current selected text or clipboard text
   - lists available actions
   - runs the chosen action
   - shows the result
   - supports copy result
5. Implement `AHK` glue so middle mouse button can trigger the popup

## Action Interface

Each action file exposes:

```python
def process(data: dict) -> str:
    ...
```

The `data` payload should support at least:

```python
{
  "selection": "...",
  "clipboard": "...",
  "timestamp": "...",
  "source_app": "..."
}
```

## Important Existing Actions

Priority actions already present:

- `02_clean_dictation.py`
- `03_overclaim_detector.py`
- `05_rephrase_5_ways.py`
- `06_full_audit.py`
- `07_markov_chain.py`
- `08_motif_scan.py`

Additional placeholder actions:

- `01_stt.py`
- `04_grammar_fix.py`
- `09_adversarial_check.py`
- `10_kimi_chat.py`

## Behavior Requirements

The first working version should support:

- launch popup from `AHK`
- run at least one action end-to-end
- support selected text if available, otherwise clipboard
- log executions to `05_logs/actions.log`
- fail clearly, not silently

## Clipboard Model

The system is expected to support many numbered clipboard slots.

Current design intent:

- 75 clipboard slots
- future focused-panel slot entry via `Ctrl+Alt` + digits + `Enter`
- persistent storage later

Do not try to fully solve every clipboard feature first. Get the popup/action path working first.

## Engine Paths

The engine NAS targets are documented in:

- `01_core/engine_registry.py`
- `06_engines/create_engine_links.cmd`

Do not assume those links already exist locally.

## Implementation Priorities

Priority order:

1. `01_core/action_registry.py`
2. `01_core/clipboard_manager.py`
3. `03_ui_python/action_popup.py`
4. `03_ui_python/api_server.py` if needed
5. `07_ahk/Stratum.ahk`
6. lifecycle/bootstrap polish

## Constraints

- Keep code simple and local-first.
- Prefer direct local coordination over unnecessary network layers.
- Do not invent a cloud dependency just to connect AHK to Python.
- Do not remove folders from the current repo shape.
- Do not turn this into a web-only app.
- Preserve Windows-first assumptions.

## Deliverable

Produce a first runnable local version where:

- user triggers the popup
- popup loads actions
- popup runs an action on selected text or clipboard text
- result is visible and copyable

When done, summarize:

- what files were implemented
- how to run it
- what still remains unfinished
