import { useMemo, useState } from "react";
import Dashboard from "./Dashboard";
import ShortcutsHub from "./ShortcutsHub";
import ActionPopup from "./ActionPopup";
import appConfig from "../../04_config/config.json";
import actions from "../../04_config/actions.json";
import hotkeyRows from "../../04_config/hotkeys.json";
import links from "../../04_config/links.json";
import prompts from "../../04_config/prompts.json";

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard" },
  { id: "actions", label: "Actions" },
  { id: "shortcuts", label: "Shortcuts" },
];

export default function App() {
  const [activeView, setActiveView] = useState("dashboard");
  const [query, setQuery] = useState("");

  const appModel = useMemo(
    () => ({ appConfig, actions, hotkeyRows, links, prompts }),
    [],
  );

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary">
        <div className="brand-block">
          <span className="eyebrow">Theophysics HUB</span>
          <h1>{appConfig.app_name}</h1>
          <p>Config-driven desktop command surface for Windows.</p>
        </div>
        <nav className="nav-list">
          {NAV_ITEMS.map((item) => (
            <button
              className={activeView === item.id ? "active" : ""}
              key={item.id}
              onClick={() => setActiveView(item.id)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>
        <div className="runtime-card">
          <span>Runtime source of truth</span>
          <strong>PySide6 shell</strong>
          <small>React is buildable now and ready for Qt WebEngine embedding.</small>
        </div>
      </aside>

      <main className="content-pane">
        {activeView === "dashboard" && <Dashboard model={appModel} onNavigate={setActiveView} />}
        {activeView === "actions" && (
          <ActionPopup actions={actions} query={query} setQuery={setQuery} />
        )}
        {activeView === "shortcuts" && <ShortcutsHub config={appConfig} hotkeyRows={hotkeyRows} />}
      </main>
    </div>
  );
}
