const { useEffect, useState } = React;

async function apiRequest(path) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
  });
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();
  if (!response.ok) {
    const error = new Error(payload?.detail ?? "Request failed");
    error.status = response.status;
    throw error;
  }
  return payload;
}

function Hero() {
  return (
    <header className="hero">
      <div>
        <p className="eyebrow">Aurelian</p>
        <h1>Conversation Category Workspace</h1>
        <p className="hero-copy">
          Review transcripts and saved category data for each conversation.
        </p>
      </div>
      <div className="hero-badge">Starter repo</div>
    </header>
  );
}

function ConversationList({ conversations, selectedId, onSelect }) {
  return (
    <section className="panel panel-stretch">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Dispatcher View</p>
          <h2>Recent conversations</h2>
        </div>
      </div>
      <div className="conversation-list">
        {conversations.map((conversation) => (
          <button
            key={conversation.id}
            type="button"
            className={`conversation-card ${conversation.id === selectedId ? "selected" : ""}`}
            onClick={() => onSelect(conversation.id)}
          >
            <div className="conversation-card-row">
              <strong>{conversation.caller_name}</strong>
              <span className="pill">{conversation.id}</span>
            </div>
            <p>{conversation.summary}</p>
          </button>
        ))}
      </div>
    </section>
  );
}

function ConversationDetail({ conversation }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Conversation Detail</p>
          <h2>{conversation.caller_name}</h2>
        </div>
        <span className="pill">{conversation.id}</span>
      </div>
      <div className="stack">
        <div>
          <div className="detail-label">Dispatcher summary</div>
          <p>{conversation.summary}</p>
        </div>
        <div>
          <div className="detail-label">Transcript</div>
          <pre className="transcript">{conversation.transcript}</pre>
        </div>
      </div>
    </section>
  );
}

function FieldGrid({ categoryFields, fieldValues }) {
  return (
    <div className="field-grid">
      {categoryFields.map((field) => {
        const value = fieldValues[field.key];
        const hasValue = value != null && String(value).trim() !== "";
        return (
          <div key={field.key} className="field-card">
            <div className="conversation-card-row">
              <strong>{field.label}</strong>
              {field.required && <span className="pill pill-required">required</span>}
            </div>
            <div className="detail-label">{field.key}</div>
            <div className={hasValue ? "field-value" : "field-value muted"}>
              {hasValue ? String(value) : "Not captured"}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function CategoryPanel({ conversation, categoryRecord }) {
  if (!categoryRecord) {
    return (
      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Conversation Category</p>
            <h3>No saved category yet</h3>
          </div>
          <span className="pill">{conversation.id}</span>
        </div>
        <div className="empty-state">
          <p>This conversation does not have a saved category yet.</p>
          <p>Create one and reload this panel to verify the read path.</p>
        </div>
      </section>
    );
  }

  try {
    const {
      category_id,
      category_name,
      review_status,
      field_values,
      category_fields,
      missing_required_fields,
    } = categoryRecord;
    const statusPill =
      review_status === "confirmed" ? "pill pill-confirmed" : "pill pill-review";

    return (
      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Conversation Category</p>
            <h3>{category_name || category_id}</h3>
          </div>
          <div className="category-panel-badges">
            <span className={statusPill}>{review_status}</span>
            <span className="pill">{conversation.id}</span>
          </div>
        </div>

        {missing_required_fields.length > 0 && (
          <div className="warning-card">
            Missing required fields: {missing_required_fields.join(", ")}
          </div>
        )}

        {category_fields.length > 0 && (
          <FieldGrid categoryFields={category_fields} fieldValues={field_values} />
        )}
      </section>
    );
  } catch (err) {
    console.error("Failed to render conversation category panel", err);
    return (
      <section className="panel">
        <div className="error-card">
          <h3>Unable to load category data</h3>
          <p>Something went wrong rendering this conversation's category.</p>
        </div>
      </section>
    );
  }
}

function App() {
  const [conversations, setConversations] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [categoryRecord, setCategoryRecord] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    apiRequest("/api/conversations")
      .then((list) => {
        if (cancelled) return;
        setConversations(list);
        if (list.length > 0) setSelectedId(list[0].id);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    let cancelled = false;
    setError(null);
    setSelectedConversation(null);
    setCategoryRecord(null);

    (async () => {
      try {
        const conversation = await apiRequest(`/api/conversations/${selectedId}`);
        if (cancelled) return;
        setSelectedConversation(conversation);

        const record = await apiRequest(
          `/api/conversations/${selectedId}/category`,
        ).catch((err) => {
          if (err.status === 404) return null;
          throw err;
        });
        if (!cancelled) setCategoryRecord(record);
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  return (
    <div className="app-shell">
      <Hero />
      <main className="workspace-grid">
        <ConversationList
          conversations={conversations}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />
        <div className="detail-column">
          {error ? (
            <section className="panel">
              <div className="error-card">
                <h3>Unable to load the workspace</h3>
                <p>{error}</p>
              </div>
            </section>
          ) : !selectedConversation ? (
            <section className="panel">
              <div className="empty-state">Select a conversation to inspect it.</div>
            </section>
          ) : (
            <>
              <ConversationDetail conversation={selectedConversation} />
              <CategoryPanel
                conversation={selectedConversation}
                categoryRecord={categoryRecord}
              />
            </>
          )}
        </div>
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
