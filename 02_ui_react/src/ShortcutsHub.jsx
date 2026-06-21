const LABELS = {
  gui: "Open shell",
  clipboard: "Clipboard panel",
  prompts: "Prompts panel",
  links: "Links panel",
  tts: "Text-to-Speech panel",
  rewrite: "Rewrite selected text",
  open_gui: "Open shell",
  open_clipboard: "Clipboard panel",
  open_prompts: "Prompts panel",
  open_links: "Links panel",
  open_tts: "Text-to-Speech panel",
  rewrite_coherent_openai: "Rewrite selected text",
};

export default function ShortcutsHub({ config, hotkeyRows }) {
  const configuredHotkeys = Object.entries(config.hotkeys ?? {}).map(([id, combo]) => ({
    id,
    combo,
    description: LABELS[id] ?? id,
  }));
  const rows = (hotkeyRows.length > 0 ? hotkeyRows : configuredHotkeys).map((row) => ({
    id: row.id ?? row.action,
    combo: row.combo ?? row.keys,
    name: row.name ?? LABELS[row.action] ?? row.action,
    description: row.description ?? "Configured desktop command",
  }));

  return (
    <section className="panel-card full-height" aria-labelledby="shortcuts-title">
      <span className="eyebrow">Windows-first controls</span>
      <h2 id="shortcuts-title">Shortcut map</h2>
      <p className="section-intro">
        These shortcuts mirror the native AHK/PySide6 path. The React view documents the active configuration without
        introducing a web service or competing runtime.
      </p>
      <div className="shortcut-list">
        {rows.map((row) => (
          <article className="shortcut-row" key={row.id ?? row.combo}>
            <kbd>{row.combo}</kbd>
            <div>
              <strong>{row.name ?? row.description}</strong>
              <span>{row.description ?? "Configured desktop command"}</span>
            </div>
          </article>
        ))}
        <article className="shortcut-row">
          <kbd>Middle Mouse</kbd>
          <div>
            <strong>Action popup</strong>
            <span>Open the configured action runner for the current selection.</span>
          </div>
        </article>
      </div>
    </section>
  );
}
