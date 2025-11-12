import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  // optional timeout
  timeout: 30_000,
});

export default api;
