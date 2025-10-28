import React, { useState } from "react";

function App() {
  const [files, setFiles] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const uploadPDFs = async () => {
    const formData = new FormData();
    for (let file of files) {
      formData.append("files", file);
    }
    await fetch("http://127.0.0.1:8000/upload", {
      method: "POST",
      body: formData,
    });
    alert("PDFs processed!");
  };

  const askQuestion = async () => {
    setLoading(true);
    const res = await fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    setAnswer(data.answer);
    setLoading(false);
  };

  return (
    <div style={{ margin: "2rem", fontFamily: "sans-serif" }}>
      <h1>Chat with PDFs (Cohere API)</h1>

      <input
        type="file"
        multiple
        onChange={(e) => setFiles(Array.from(e.target.files))}
      />
      <button onClick={uploadPDFs}>Process PDFs</button>

      <hr />

      <input
        type="text"
        placeholder="Ask a question"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button onClick={askQuestion} disabled={loading}>
        {loading ? "Thinking..." : "Send"}
      </button>

      <div style={{ marginTop: "1rem", background: "#eee", padding: "1rem" }}>
        <strong>Answer:</strong> {answer}
      </div>
    </div>
  );
}

export default App;