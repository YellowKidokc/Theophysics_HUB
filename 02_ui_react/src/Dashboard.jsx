function StatCard({ label, value, detail }) {
  return (
    <article className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}

export default function Dashboard({ model, onNavigate }) {
  const { appConfig, actions, hotkeyRows, links, prompts } = model;
  const panelList = appConfig.panels ?? [];
  const openai = appConfig.openai ?? {};

  return (
    <section className="dashboard-grid" aria-labelledby="dashboard-title">
      <header className="hero-panel">
        <span className="eyebrow">First public slice</span>
        <h2 id="dashboard-title">A focused control room for text actions.</h2>
        <p>
          Review configured actions, confirm desktop shortcuts, and keep the native Python shell as the operational host.
        </p>
        <div className="hero-actions">
          <button type="button" onClick={() => onNavigate("actions")}>Browse actions</button>
          <button className="secondary" type="button" onClick={() => onNavigate("shortcuts")}>View shortcuts</button>
        </div>
      </header>

      <div className="stats-row">
        <StatCard label="Configured actions" value={actions.length} detail="Loaded from actions.json" />
        <StatCard label="Panels" value={panelList.length} detail={panelList.join(" · ")} />
        <StatCard label="Prompt presets" value={prompts.length} detail="Available to the shell" />
        <StatCard label="Reference links" value={links.length} detail="Config-backed resources" />
      </div>

      <section className="panel-card wide">
        <div>
          <span className="eyebrow">Execution model</span>
          <h3>Native shell remains the source of truth</h3>
        </div>
        <p>
          This React slice is a production-shaped dashboard that builds from the existing configuration. Action execution,
          clipboard capture, hotkeys, and single-instance routing continue to run through the Python/PySide6 shell.
        </p>
        <dl className="definition-list">
          <div><dt>UI mode</dt><dd>{appConfig.ui_mode}</dd></div>
          <div><dt>Rewrite hotkey</dt><dd>{appConfig.hotkeys?.rewrite}</dd></div>
          <div><dt>OpenAI model</dt><dd>{openai.model}</dd></div>
          <div><dt>API key env</dt><dd>{openai.api_key_env}</dd></div>
        </dl>
      </section>

      <section className="panel-card checklist">
        <h3>Readiness checklist</h3>
        <ul>
          <li><strong>Ready:</strong> Python shell panels, action registry, clipboard store, prompt registry, and hotkeys.</li>
          <li><strong>Ready:</strong> React dashboard, shortcuts view, and action browser build as static assets.</li>
          <li><strong>Stubbed by dependency:</strong> Qt WebEngine host is optional and reports a clear install/runtime error.</li>
          <li><strong>Next:</strong> Add a bridge for invoking Python actions from an embedded React webview.</li>
        </ul>
      </section>

      <section className="panel-card checklist">
        <h3>Desktop shortcuts</h3>
        <ul>
          {hotkeyRows.slice(0, 5).map((row) => (
            <li key={(row.id ?? row.action)}><strong>{row.combo ?? row.keys}</strong> {row.description ?? row.action}</li>
          ))}
        </ul>
      </section>
    </section>
  );
}
