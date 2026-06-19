#Requires AutoHotkey v2.0
#SingleInstance Force

; Thin Windows-native trigger layer for Theophysics HUB.
; Python owns app logic; AHK only captures user intent and selected text.

RepoRoot := "D:\GitHub\Theophysics_HUB"
Pythonw := "pythonw.exe"
Python := "python.exe"
Cli := RepoRoot "\00_app_shell\stratum_cli.py"

RunGui() {
    global Pythonw, Cli, RepoRoot
    Run('"' Pythonw '" "' Cli '" gui', RepoRoot)
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

CaptureSelectionToClipboard() {
    original := A_Clipboard
    A_Clipboard := ""
    Send "^c"
    if !ClipWait(0.35) {
        A_Clipboard := original
    }
}

^!g::RunGui()
^!c::RunGui()
^!p::RunGui()
^!l::RunGui()
^!t::RunGui()
^Space::RunRewrite()
MButton::RunPopup()
