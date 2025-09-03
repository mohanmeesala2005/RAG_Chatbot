import { useState } from "react";

function Chat() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]); // Stores Q&A history
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const RAG_API_URL = "http://localhost:8000/rag";

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading || !query.trim()) return;

    const newMessage = { role: "user", content: query };
    setMessages((prev) => [...prev, newMessage]); // Add user msg
    setQuery(""); // Clear input after sending
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(RAG_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) throw new Error("API error");
      const data = await response.json();

      // Add assistant's response
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.result || JSON.stringify(data) },
      ]);
    } catch (err) {
      setError(err.message);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `⚠️ Error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#1a1a1a] text-[#ececec] font-sans">
      <header className="text-center py-4 text-lg font-semibold bg-[#23272f] border-b border-[#333] text-[#19c37d]">
        RAG Demo App
      </header>

      <div className="flex-1 px-6 py-4 overflow-y-auto flex flex-col gap-4 scrollbar-thin">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={
              msg.role === "user"
                ? "self-end max-w-[80%] px-4 py-3 rounded-xl bg-[#19c37d] text-white text-base break-words border-b-4 border-b-[#128a5c]"
                : "self-start max-w-[80%] px-4 py-3 rounded-xl bg-[#23272f] text-[#ececec] text-base break-words border border-[#333] border-b-4 border-b-[#333]"
            }
          >
            {msg.content}
          </div>
        ))}
        {loading && (
          <div className="self-start max-w-[80%] px-4 py-3 rounded-xl bg-[#23272f] text-[#ececec] text-base break-words border border-[#333] border-b-4 border-b-[#333]">
            ⏳ Thinking...
          </div>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex gap-2 p-4 bg-[#23272f] border-t border-[#333]"
        autoComplete="off"
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
          className="flex-1 px-4 py-3 rounded-lg border border-[#333] bg-[#1a1a1a] text-[#ececec] text-base outline-none focus:border-[#19c37d]"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className={`px-4 py-3 rounded-lg font-medium text-white transition-colors ${
            loading || !query.trim()
              ? "bg-[#444] cursor-not-allowed"
              : "bg-[#19c37d] hover:bg-[#128a5c] cursor-pointer"
          }`}
        >
          {loading ? "Loading..." : "Send"}
        </button>
      </form>
    </div>
  );
}

export default Chat;
