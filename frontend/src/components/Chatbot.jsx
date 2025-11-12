import React, { useState } from "react";
import axios from "axios";
import api from "../api";

const Chatbot = () => {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! Enter a website URL to start." },
  ]);
  const [input, setInput] = useState("");
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [scraped, setScraped] = useState(false);

  const handleScrape = async () => {
    if (!url) return;
    setLoading(true);
    try {
      await api.post("/api/scrape", { url });
      setScraped(true);
      setMessages([
        { sender: "bot", text: "Website scraped! Ask your question." },
      ]);
    } catch (err) {
      setMessages([{ sender: "bot", text: "Failed to scrape website." }]);
    }
    setLoading(false);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { sender: "user", text: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setLoading(true);
    try {
      const res = await api.post("/api/chat", { question: input });
      setMessages((msgs) => [
        ...msgs,
        { sender: "bot", text: res.data.answer },
      ]);
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { sender: "bot", text: "Error getting answer." },
      ]);
    }
    setInput("");
    setLoading(false);
  };

  return (
    <div className="w-full max-w-2xl mx-auto bg-white rounded-xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
        <h1 className="text-xl font-semibold text-white">RAG Chatbot</h1>
        <p className="text-blue-100 text-sm mt-1">Powered by AI</p>
      </div>

      {/* URL Input Section */}
      <div className="border-b bg-gray-50 px-6 py-4">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Website URL
        </label>
        <div className="flex gap-3">
          <input
            type="url"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={scraped || loading}
          />
          <button
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed transition"
            onClick={handleScrape}
            disabled={scraped || loading}
          >
            {loading ? "Scraping..." : "Scrape"}
          </button>
        </div>
        {scraped && (
          <p className="text-sm text-green-600 mt-2 flex items-center">
            ✓ Website ready
          </p>
        )}
      </div>

      {/* Messages Container */}
      <div className="h-96 overflow-y-auto px-6 py-6 bg-white space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-xs px-4 py-3 rounded-lg text-sm ${
                msg.sender === "user"
                  ? "bg-blue-600 text-white rounded-br-none"
                  : "bg-gray-100 text-gray-900 rounded-bl-none"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-center py-2">
            <div className="text-gray-500 text-sm flex items-center gap-2">
              <span className="inline-flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></span>
              </span>
              Thinking...
            </div>
          </div>
        )}
      </div>

      {/* Input Section */}
      <form onSubmit={handleSend} className="border-t bg-gray-50 px-6 py-4">
        <div className="flex gap-3">
          <input
            type="text"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder={scraped ? "Ask a question..." : "Scrape a website first"}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!scraped || loading}
          />
          <button
            type="submit"
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed transition"
            disabled={!scraped || loading}
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chatbot;
