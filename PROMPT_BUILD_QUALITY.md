# Theophysics HUB Quality Build Prompt

You are working in `D:\GitHub\Theophysics_HUB`.

Build this as if it will be publicly reviewed on GitHub by strong engineers. The code should be clean, structured, readable, and defensible. Do not produce fragile glue code, giant monolith files, or vague placeholder architecture.

## Standard

Optimize for:

- clarity
- separation of concerns
- explicit data flow
- good naming
- minimal but real abstractions
- local testability
- maintainability

Avoid:

- giant god objects
- hidden globals
- duplicated logic
- hardcoded secrets
- UI logic mixed into backend logic
- “just make it pass” hacks

## Architecture You Must Preserve

Keep this repo structure and implement within it:

- `00_app_shell/` = lifecycle and startup
- `01_core/` = backend domain logic
- `02_ui_react/` = future React frontend
- `03_ui_python/` = PySide6 shell and popup UI
- `04_config/` = source-of-truth JSON config
- `05_logs/` = logs
- `06_engines/` = engine pointers
- `07_ahk/` = Windows-native hotkeys and mouse glue
- `08_actions/` = action scripts

Keep:

- `AHK` for Windows-native triggers
- `Python` for backend orchestration
- `PySide6` for desktop popup/shell
- config-driven behavior

## Immediate Working Slice

Implement the first high-quality runnable slice:

1. `Ctrl+Alt+G` opens the main GUI
2. `Ctrl+Space` captures selected text or clipboard text, runs the OpenAI rewrite action, and returns usable rewritten output
3. middle mouse button opens an action popup
4. popup loads actions from config, runs them cleanly, and displays result
5. action runs are logged

## Design Requirements

### 1. Action system

Implement `01_core/action_registry.py` as a real registry.

Requirements:

- load from `04_config/actions.json`
- validate action records
- dynamically import action modules
- expose a clean `run(action_id, payload) -> ActionResult`
- handle errors without crashing the app

Create a small result model instead of returning random strings everywhere.

Suggested direction:

- `ActionRecord`
- `ActionResult`
- `ActionExecutionError`

### 2. Clipboard/selection capture

Implement `01_core/clipboard_manager.py`.

Requirements:

- clean interface
- no UI code inside it
- capture:
  - `selection`
  - `clipboard`
  - `timestamp`
  - `source_app`
- fail predictably

### 3. Popup UI

Implement `03_ui_python/action_popup.py`.

Requirements:

- clean PySide6 widget design
- no backend business logic embedded in UI
- receives services through constructor or explicit methods
- shows:
  - selected text preview
  - action list
  - result pane
  - copy button
- state transitions should be clear

### 4. Main GUI

Implement a real shell window for `Ctrl+Alt+G`.

This does not need full React migration yet.
It does need to be a real coherent window, not a message box or print statement.

### 5. AHK integration

Implement `07_ahk/Stratum.ahk`.

Requirements:

- `^!g` opens/focuses GUI
- `^Space` triggers rewrite flow
- `MButton` opens action popup
- keep this thin: trigger layer only, not app logic

### 6. OpenAI rewrite flow

Use the existing `08_actions/11_openai_rewrite_coherent.py`.

Requirements:

- API key from env var defined in config
- no secret in code
- clear failure behavior
- preserve user meaning
- rewrite for punctuation, capitalization, sentence boundaries, spelling, coherence

## Coding Style Requirements

- Prefer small classes/functions with clear responsibilities
- Add docstrings where interface intent matters
- Use dataclasses or typed models where helpful
- Use type hints throughout Python
- Keep imports tidy
- Keep config access centralized
- Keep side effects explicit

## Logging

Implement structured-enough logging to:

- `05_logs/actions.log`
- `05_logs/app.log`

Log:

- action start
- action success
- action failure
- trigger source

Do not spam logs with noise.

## Constraints

- Do not rewrite the repo layout
- Do not remove AHK
- Do not overbuild React yet
- Do not invent unnecessary web services if direct local coordination is enough
- Do not touch unrelated files
- Ignore `02_ui_react/node_modules/`

## Anti-Pattern Warning

Do not downgrade this project into a toy popup demo.

Specifically, do not:

- replace the architecture with a tiny standalone Tkinter reminder script
- build a one-file popup example with no real backend separation
- treat the action popup as a generic message-box demo
- ignore the existing config/action/hotkey structure

If you use Tkinter at all, it must be because you can justify it against the current PySide6-oriented shell plan. Otherwise stay aligned with the existing desktop architecture.

This project is a real Windows productivity hub, not a beginner popup-window tutorial.

## Deliverable

When finished, provide:

1. files changed
2. architectural decisions made
3. how to run locally
4. what hotkeys now work
5. what is production-worthy already
6. what still needs refinement

Build something we would be comfortable showing publicly on GitHub.
