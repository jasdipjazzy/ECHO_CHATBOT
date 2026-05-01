import { useState } from "react";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input) return;

    const newMessages = [...messages, { role: "user", text: input }];
    setMessages(newMessages);

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: input, history: [] }),
    });

    const data = await res.json();

    setMessages([
      ...newMessages,
      { role: "bot", text: data.reply }
    ]);

    setInput("");
  };

  return (
    <div className="container">
      <h2>Echo Chatbot</h2>

      <div className="chat-box">
        {messages.map((m, i) => (
          <div key={i}>
            <b>{m.role === "user" ? "You" : "Echo"}:</b> {m.text}
          </div>
        ))}
      </div>

      <div className="input-box">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}
