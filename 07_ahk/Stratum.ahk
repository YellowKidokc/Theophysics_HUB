#Requires AutoHotkey v2.0
#SingleInstance Force

; Thin Windows-native trigger layer for Theophysics HUB.
; Python owns all app logic; AHK only captures user intent and selected text,
; then shells out to 00_app_shell\stratum_cli.py.

RepoRoot := "D:\GitHub\Theophysics_HUB"
Pythonw := "pythonw.exe"   ; windowless host for GUI surfaces
Python := "python.exe"     ; console host for the rewrite round-trip
Cli := RepoRoot "\00_app_shell\stratum_cli.py"

; Open or focus the shell on a specific panel. The Python side runs a single
; instance, so repeat presses reuse the same window and just switch panels.
RunGui(panel := "dashboard") {
    global Pythonw, Cli, RepoRoot
    Run('"' Pythonw '" "' Cli '" gui ' panel, RepoRoot)
}

RunPopup() {
    global Pythonw, Cli, RepoRoot
    CaptureSelectionToClipboard()
    Run('"' Pythonw '" "' Cli '" popup', RepoRoot)
}

RunRewrite() {
    global Python, Cli, RepoRoot
    CaptureSelectionToClipboard()
    RunWait('"' Python '" "' Cli '" rewrite', RepoRoot, "Hide")
    Send "^v"
}

; Copy the current selection into the clipboard so Python can read it. Restores
; the prior clipboard if nothing was selected.
CaptureSelectionToClipboard() {
    original := A_Clipboard
    A_Clipboard := ""
    Send "^c"
    if !ClipWait(0.35) {
        A_Clipboard := original
    }
}

^!g::RunGui("dashboard")
^!c::RunGui("clipboard")
^!p::RunGui("prompts")
^!l::RunGui("links")
^!t::RunGui("tts")
^Space::RunRewrite()
MButton::RunPopup()
