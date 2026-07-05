import React, { useEffect, useRef, useState } from "react";
import { sendMessage, getHistory } from "../services/api.js";
import MessageBubble from "../components/MessageBubble.jsx";

function getOrCreateSessionId() {
  let sessionId = localStorage.getItem("session_id");
  if (!sessionId) {
    sessionId = "S" + Date.now();
    localStorage.setItem("session_id", sessionId);
  }
  return sessionId;
}

export default function ChatPage() {
  const [sessionId] = useState(getOrCreateSessionId);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    getHistory(sessionId)
      .then((history) => {
        const loaded = history.flatMap((item) => [
          { role: "customer", text: item.user_query },
          { role: "assistant", text: item.ai_response },
        ]);
        setMessages(loaded);
      })
      .catch(() => {
        // No history yet - safe to ignore on first visit.
      });
  }, [sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const query = input.trim();
    if (!query) return;

    setError("");
    setMessages((prev) => [...prev, { role: "customer", text: query }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendMessage(sessionId, query);
      setMessages((prev) => [...prev, { role: "assistant", text: data.response }]);
    } catch (err) {
      setError("Sorry, something went wrong reaching the assistant. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") handleSend();
  }

  return (
    <div className="container">
      <div className="card">
        <h2>Customer Support Chat</h2>
        <div className="chat-window">
          {messages.map((m, i) => (
            <MessageBubble key={i} role={m.role} text={m.text} />
          ))}
          {loading && <MessageBubble role="assistant" text="Typing..." />}
          <div ref={bottomRef} />
        </div>
        {error && <p className="error-text">{error}</p>}
        <div className="chat-input-row">
          <input
            type="text"
            placeholder="Ask a question about our products or policies..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button className="btn" onClick={handleSend} disabled={loading}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
