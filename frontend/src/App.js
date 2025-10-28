import React, { useState } from "react";

function App() {
  const [files, setFiles] = useState([]);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]); // full conversation
  const [loading, setLoading] = useState(false);
  const [processed, setProcessed] = useState(false);

  // Upload PDFs
  const uploadPDFs = async () => {
    const formData = new FormData();
    for (let file of files) {
      formData.append("files", file);
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        alert("✅ PDFs processed successfully!");
        setProcessed(true);
      } else {
        alert("❌ Upload failed.");
      }
    } catch (err) {
      console.error(err);
      alert("Error uploading files.");
    }
  };

  // Ask question
  const askQuestion = async () => {
    if (!processed) {
      alert("Please process PDFs first!");
      return;
    }

    if (!question) return;

    // Add user message
    setMessages((prev) => [...prev, { type: "user", text: question }]);
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { type: "bot", text: data.answer || data.error || "(no response)" },
      ]);
      setQuestion(""); // clear input
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { type: "bot", text: "Error contacting backend." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ fontFamily: "Arial", maxWidth: 600, margin: "3rem auto" }}>
      <h2>🤖 Chat with PDFs (Cohere API)</h2>

      <div style={{ marginBottom: "1rem" }}>
        <input
          type="file"
          multiple
          accept="application/pdf"
          onChange={(e) => setFiles(Array.from(e.target.files))}
        />
        <button onClick={uploadPDFs} style={{ marginLeft: "0.5rem" }}>
          Process PDFs
        </button>
      </div>

      <div style={{ marginTop: "2rem", display: "flex" }}>
        <input
          type="text"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={{
            width: "70%",
            padding: "0.5rem",
            borderRadius: "5px",
            border: "1px solid #ccc",
          }}
        />
        <button
          onClick={askQuestion}
          disabled={loading}
          style={{
            marginLeft: "0.5rem",
            padding: "0.5rem 1rem",
            background: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "5px",
          }}
        >
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>

      <div
        style={{
          marginTop: "2rem",
          maxHeight: "400px",
          overflowY: "auto",
          background: "#f2f2f2",
          padding: "1rem",
          borderRadius: "10px",
        }}
      >
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: "flex",
              justifyContent: msg.type === "user" ? "flex-end" : "flex-start",
              marginBottom: "1rem",
            }}
          >
            <div
              style={{
                background: msg.type === "user" ? "#2b313e" : "#475063",
                color: "white",
                padding: "0.5rem 1rem",
                borderRadius: "10px",
                maxWidth: "80%",
              }}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
