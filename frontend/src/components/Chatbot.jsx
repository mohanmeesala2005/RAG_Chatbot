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
      // use central API client so requests go to backend (dev proxy or direct baseURL)
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
    <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6">
      <div className="mb-4">
        <input
          type="text"
          className="border rounded px-3 py-2 w-3/4 mr-2"
          placeholder="Enter website URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={scraped || loading}
        />
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
          onClick={handleScrape}
          disabled={scraped || loading}
        >
          Scrape
        </button>
      </div>
      <div className="h-64 overflow-y-auto border rounded p-3 bg-gray-50 mb-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`mb-2 text-sm ${
              msg.sender === "user" ? "text-right" : "text-left"
            }`}
          >
            <span
              className={`inline-block px-3 py-2 rounded-lg ${
                msg.sender === "user"
                  ? "bg-blue-100 text-blue-800"
                  : "bg-gray-200 text-gray-800"
              }`}
            >
              {msg.text}
            </span>
          </div>
        ))}
        {loading && <div className="text-gray-400 text-center">Loading...</div>}
      </div>
      <form onSubmit={handleSend} className="flex">
        <input
          type="text"
          className="border rounded px-3 py-2 flex-1 mr-2"
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!scraped || loading}
        />
        <button
          type="submit"
          className="bg-green-500 text-white px-4 py-2 rounded disabled:opacity-50"
          disabled={!scraped || loading}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default Chatbot;
