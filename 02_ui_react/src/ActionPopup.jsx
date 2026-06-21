export default function ActionPopup({ actions, query, setQuery }) {
  const normalizedQuery = query.trim().toLowerCase();
  const filteredActions = actions.filter((action) => {
    const haystack = `${action.name} ${action.id} ${action.description}`.toLowerCase();
    return haystack.includes(normalizedQuery);
  });

  return (
    <section className="panel-card full-height" aria-labelledby="actions-title">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Action registry</span>
          <h2 id="actions-title">Configured text actions</h2>
        </div>
        <label className="search-box">
          <span>Filter</span>
          <input
            onChange={(event) => setQuery(event.target.value)}
            type="search"
            value={query}
          />
        </label>
      </div>
      <p className="section-intro">
        This is the React counterpart to the native middle-click popup: searchable, config-backed, and ready for a future
        Python bridge. Execution still belongs to the existing desktop shell.
      </p>
      <div className="action-grid">
        {filteredActions.map((action) => (
          <article className="action-card" key={action.id}>
            <div>
              <h3>{action.name}</h3>
              <p>{action.description}</p>
            </div>
            <code>{action.id}</code>
            <small>{action.entry}</small>
          </article>
        ))}
      </div>
      {filteredActions.length === 0 && <p className="empty-state">No configured actions match “{query}”.</p>}
    </section>
  );
}
