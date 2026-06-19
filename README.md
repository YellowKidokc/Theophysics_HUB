# Stratum

Windows panel-first productivity hub scaffold.

## Structure

- `00_app_shell`: boot and lifecycle
- `01_core`: registries, models, managers
- `02_ui_react`: future React front end
- `03_ui_python`: PySide6 host and popup layer
- `04_config`: JSON state
- `05_logs`: rolling logs
- `06_engines`: engine links or pointers
- `07_ahk`: Windows glue
- `08_actions`: TextGO-style actions

## Current State

This is a scaffolded repo shape, not a finished app.

- Action files are in place
- Config and registry stubs exist
- Engine links are documented but not created automatically
- UI files are placeholders, not the full migrated panels

## Next Implementation Steps

1. Wire `01_core/action_registry.py` into a real popup runner.
2. Build `03_ui_python/action_popup.py`.
3. Decide whether to migrate the current HTML panels into `02_ui_react`.
4. Add persistence for prompts, clipboard slots, and settings.
