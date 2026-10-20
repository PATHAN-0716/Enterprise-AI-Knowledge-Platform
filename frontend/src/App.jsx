
import { useEffect, useState } from "react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function request(path, options = {}) {
    const response = await fetch(`${API}${path}`, options);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    return data;
  }

  async function refreshDocuments() {
    try {
      const data = await request("/documents/");
      setDocuments(data.documents);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refreshDocuments();
  }, []);

  async function uploadDocument(event) {
    event.preventDefault();
    if (!file) return;

    setBusy(true);
    setError("");

    try {
      const form = new FormData();
      form.append("file", file);

      await request("/upload", {
        method: "POST",
        body: form,
      });

      setFile(null);
      event.target.reset();
      await refreshDocuments();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function deleteDocument(id) {
    if (!window.confirm("Delete this document and its index?")) return;

    try {
      await request(`/documents/${id}`, { method: "DELETE" });
      await refreshDocuments();
    } catch (err) {
      setError(err.message);
    }
  }

  async function askQuestion(event) {
    event.preventDefault();
    if (!question.trim()) return;

    const currentQuestion = question.trim();
    setMessages((old) => [
      ...old,
      { role: "user", text: currentQuestion },
    ]);
    setQuestion("");
    setBusy(true);
    setError("");

    try {
      const result = await request("/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: currentQuestion }),
      });

      setMessages((old) => [
        ...old,
        { role: "assistant", text: result.answer, sources: result.sources },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="container">
      <header>
        <p className="eyebrow">AI KNOWLEDGE PLATFORM</p>
        <h1>Ask My Docs</h1>
        <p>Upload your documents and ask questions grounded in their contents.</p>
      </header>

      <section className="panel">
        <h2>Upload documents</h2>
        <form onSubmit={uploadDocument} className="upload-form">
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(event) => setFile(event.target.files[0] || null)}
          />
          <button disabled={!file || busy}>
            {busy ? "Processing..." : "Upload and index"}
          </button>
        </form>
        <p className="muted">PDF, DOCX or TXT Â· Maximum 10 MB</p>
      </section>

      <section className="panel">
        <h2>Your documents ({documents.length})</h2>
        {documents.length === 0 && <p>No indexed documents yet.</p>}
        {documents.map((doc) => (
          <div className="document" key={doc.document_id}>
            <div>
              <strong>{doc.filename}</strong>
              <p className="muted">{doc.chunks} chunks</p>
            </div>
            <button
              className="danger"
              onClick={() => deleteDocument(doc.document_id)}
              disabled={busy}
            >
              Delete
            </button>
          </div>
        ))}
      </section>

      <section className="panel">
        <h2>Ask a question</h2>
        <div className="chat">
          {messages.map((message, index) => (
            <article className={`message ${message.role}`} key={index}>
              <strong>{message.role === "user" ? "You" : "AI Assistant"}</strong>
              <p>{message.text}</p>
              {message.sources?.length > 0 && (
                <div className="sources">
                  <strong>Sources</strong>
                  {message.sources.map((source) => (
                    <details key={source.chunk_id}>
                      <summary>
                        {source.source_id}: {source.filename}
                        {source.page_number
                          ? ` Â· Page ${source.page_number}`
                          : ""}
                      </summary>
                      <p>{source.text}</p>
                    </details>
                  ))}
                </div>
              )}
            </article>
          ))}
          {busy && <p className="muted">Working on your request...</p>}
        </div>

        <form onSubmit={askQuestion} className="chat-form">
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask something about your documents..."
          />
          <button disabled={!question.trim() || busy}>Ask</button>
        </form>
      </section>

      {error && <p className="error">{error}</p>}
    </main>
  );
}

