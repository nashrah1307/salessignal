// frontend/src/pages/Chat.jsx
import { useState, useRef, useEffect } from "react";

const BASE = "http://localhost:8001";
const SESSION_ID = "session_" + Math.random().toString(36).substr(2, 9);

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! I'm SalesSignal AI. I can help you analyse deals, find at-risk opportunities, send follow-up emails, and update your CRM. Try asking: 'Show me all at-risk deals' or 'Analyse deal 4988063'"
    }
  ]);
  const [input,   setInput]   = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", text: userMsg }]);
    setLoading(true);

    try {
      const res  = await fetch(`${BASE}/chat`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ message: userMsg, session_id: SESSION_ID })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", text: data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", text: "Error connecting to agent. Make sure the backend is running." }]);
    }
    setLoading(false);
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 50px)", fontFamily: "Arial", maxWidth: "900px", margin: "0 auto", padding: "16px" }}>
      <h2 style={{ color: "#1F4E79", marginBottom: "12px" }}>SalesSignal AI Agent</h2>
      <p style={{ color: "#666", fontSize: "13px", marginBottom: "16px" }}>
        Ask me anything about your pipeline. I can look up deals, find risks, send emails, and update your CRM.
      </p>

      {/* Suggested prompts */}
      <div style={{ display: "flex", gap: "8px", marginBottom: "16px", flexWrap: "wrap" }}>
        {[
          "Show me all at-risk deals",
          "Analyse deal 4988063",
          "What are the top risk factors for deal 4988063?",
          "Which product line has the lowest win rate?"
        ].map(prompt => (
          <button key={prompt} onClick={() => setInput(prompt)}
            style={{ fontSize: "12px", padding: "6px 12px", borderRadius: "16px", border: "1px solid #1F4E79", background: "white", color: "#1F4E79", cursor: "pointer" }}>
            {prompt}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", border: "1px solid #ddd", borderRadius: "8px", padding: "16px", background: "#fafafa", marginBottom: "12px" }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            display: "flex",
            justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
            marginBottom: "12px"
          }}>
            <div style={{
              maxWidth: "75%",
              padding: "10px 14px",
              borderRadius: msg.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
              background: msg.role === "user" ? "#1F4E79" : "white",
              color: msg.role === "user" ? "white" : "#333",
              border: msg.role === "user" ? "none" : "1px solid #e0e0e0",
              fontSize: "13px",
              lineHeight: "1.6",
              whiteSpace: "pre-wrap"
            }}>
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "12px" }}>
            <div style={{ padding: "10px 14px", borderRadius: "16px 16px 16px 4px", background: "white", border: "1px solid #e0e0e0", color: "#999", fontSize: "13px" }}>
              🔍 Agent is querying tools and reasoning... (may take 10-20 seconds)
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ display: "flex", gap: "8px" }}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask about deals, risks, or trigger actions... (Enter to send)"
          rows={2}
          style={{ flex: 1, padding: "10px 14px", borderRadius: "8px", border: "1px solid #ddd", fontSize: "13px", resize: "none", fontFamily: "Arial" }}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}
          style={{ padding: "10px 20px", background: loading ? "#ccc" : "#1F4E79", color: "white", border: "none", borderRadius: "8px", cursor: loading ? "not-allowed" : "pointer", fontWeight: "bold", fontSize: "13px" }}>
          Send
        </button>
      </div>
    </div>
  );
}
