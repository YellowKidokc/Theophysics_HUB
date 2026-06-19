# Theophysics HUB Aggressive One-Shot Build Prompt

You are building inside the repo `D:\GitHub\Theophysics_HUB`.

Act like a senior Windows desktop app engineer. Take the current scaffold and turn it into the first coherent working Windows app version. Do not redesign the architecture. Implement against what is already there. Make real file changes.

## Core Goal

Build a Windows-first productivity hub with these working triggers:

- `Ctrl+Alt+G` opens the main GUI
- `Ctrl+Alt+C` opens Clipboard
- `Ctrl+Alt+P` opens Prompts
- `Ctrl+Alt+L` opens Links
- `Ctrl+Alt+T` opens TTS
- `Ctrl+Space` captures selected text or clipboard text, sends it to OpenAI, and returns rewritten coherent text with punctuation, capitalization, spelling, and sentence cleanup
- Middle mouse button opens the action popup

## Non-Negotiable Architecture

Keep this architecture:

- `07_ahk/` = Windows-native glue for hotkeys, mouse triggers, and selection workflows
- `01_core/` = backend brain for registries, action running, clipboard/selection payloads, logging, provider config, and engine paths
- `03_ui_python/` = PySide6 shell, popup, tray, and first working desktop GUI
- `02_ui_react/` = future React frontend; preserve it, but do not depend on it for the first working slice unless already necessary
- `04_config/` = source-of-truth JSON config
- `08_actions/` = TextGO-style action scripts

Do not remove AHK. Do not convert this into a browser-only app. Do not replace Windows-native triggers with web workarounds.

## Existing Repo State

The repo already contains:

- scaffold folders `00_app_shell` through `08_actions`
- action loader/registry stubs in `01_core`
- PySide stubs in `03_ui_python`
- AHK stub in `07_ahk/Stratum.ahk`
- action files in `08_actions`
- config in `04_config`
- OpenAI rewrite action in `08_actions/11_openai_rewrite_coherent.py`
- hotkey config entries for `Ctrl+Alt+G`, `Ctrl+Alt+C`, `Ctrl+Alt+P`, `Ctrl+Alt+L`, `Ctrl+Alt+T`, and `Ctrl+Space`

## Immediate Deliverable

Implement the first real end-to-end version of:

1. AHK trigger layer
2. selection/clipboard capture
3. Python action runner
4. PySide popup
5. OpenAI rewrite flow
6. main GUI launcher
7. logging

Focus on building the first real working slice, not on discussing options endlessly.

## Required Behaviors

### A. Main GUI

`Ctrl+Alt+G` should open the main GUI window. A PySide6-hosted window is enough for now, but it must be a real window, not a placeholder print or message box.

### B. Rewrite / Spell Check

`Ctrl+Space` should:

1. capture selected text if possible
2. otherwise use clipboard text
3. run `rewrite_coherent_openai`
4. return rewritten text
5. either replace the selected text in place or copy the rewritten text back to clipboard and show it clearly in a popup

This is intended to function as a serious dictation cleanup / spell-check / punctuation fixer.

### C. Action Popup

Middle mouse button should trigger a popup that:

- previews selected text
- lists available actions from `04_config/actions.json`
- runs the selected action
- shows the result
- supports copying the result

### D. Logging

Log action runs and failures into `05_logs/actions.log`.

## Existing Action Contract

Each action in `08_actions` exposes:

```python
def process(data: dict) -> str:
    ...
```

Payloads should support:

```python
{
  "selection": "...",
  "clipboard": "...",
  "timestamp": "...",
  "source_app": "..."
}
```

## Important Actions Already Present

- `02_clean_dictation.py`
- `03_overclaim_detector.py`
- `05_rephrase_5_ways.py`
- `06_full_audit.py`
- `07_markov_chain.py`
- `08_motif_scan.py`
- `11_openai_rewrite_coherent.py`

## OpenAI Requirements

There is already config for OpenAI in `04_config/config.json`.

Use:

- API key environment variable name from config
- model from config
- rewrite instruction from config

Do not hardcode the API key. Do not move the key into source code. If the API key is missing, fail clearly and visibly in the popup and logs.

Use the current OpenAI Responses API shape. Keep the OpenAI call isolated in the action or a small provider helper so it can be swapped later.

## Clipboard / Prompt / Links Direction

Do not fully rebuild all panels yet. Wire enough of the shell so the architecture is real and launcher structure is correct.

Clipboard direction:

- support 75 slots as a model
- do not over-engineer all slot behavior yet
- make sure the system design does not block the 75-slot plan

## Engine Direction

Do not assume NAS engine links already exist. Use the documented paths in:

- `01_core/engine_registry.py`
- `06_engines/create_engine_links.cmd`

## Coding Requirements

- Favor direct local coordination over unnecessary HTTP unless there is a strong reason
- Keep the code simple and maintainable
- Use Windows-first assumptions
- Implement real files, not just comments or pseudo-code
- Preserve the current repo shape for later React migration
- Do not add secrets to source control
- Fail clearly rather than silently

## Do Not Drift Into Demo Code

Do not turn this into a tiny popup tutorial or a standalone Tkinter demo app.

Avoid:

- single-file “automatic popup window” implementations
- generic reminder/alert windows with no action system
- replacing the repo architecture with a toy script

Build against the existing AHK + Python + PySide6 + config-driven structure.

## Deliverables Summary

When finished, provide:

1. files implemented
2. how to run locally
3. what hotkeys now work
4. what remains unfinished
5. test/check commands run
