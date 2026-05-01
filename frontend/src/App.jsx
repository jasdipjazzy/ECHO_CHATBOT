import { useState } from "react";

export default function App() {
  const [messages, setMessages] = useState([
    { role: "model", content: "Hi, I'm Echo 👋 Ask me anything about company policies." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: input,
          history: newMessages
        })
      });

      const data = await res.json();

      setMessages([
        ...newMessages,
        { role: "model", content: data.reply }
      ]);
    } catch (err) {
      setMessages([
        ...newMessages,
        { role: "model", content: "Error: Unable to respond." }
      ]);
    }

    setLoading(false);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      
      {/* Header */}
      <div style={{
        padding: "12px",
        background: "#1f2937",
        color: "white",
        fontWeight: "bold",
        textAlign: "center"
      }}>
        Echo Chatbot (Open Arena 2.0 Submission)
      </div>

      {/* Chat */}
      <div style={{
        flex: 1,
        padding: "10px",
        overflowY: "auto",
        background: "#f3f4f6"
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            marginBottom: "10px",
            textAlign: msg.role === "user" ? "right" : "left"
          }}>
            <div style={{
              display: "inline-block",
              padding: "10px",
              borderRadius: "10px",
              background: msg.role === "user" ? "#3b82f6" : "#e5e7eb",
              color: msg.role === "user" ? "white" : "black",
              maxWidth: "70%"
            }}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && <div>Echo is typing...</div>}
      </div>

      {/* Input */}
      <div style={{
        display: "flex",
        padding: "10px",
        background: "white",
        borderTop: "1px solid #ddd"
      }}>
        <input
          style={{ flex: 1, padding: "10px" }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
        />
        <button
          onClick={sendMessage}
          style={{
            marginLeft: "10px",
            padding: "10px 15px",
            background: "#3b82f6",
            color: "white",
            border: "none"
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
