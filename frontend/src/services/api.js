import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach the saved session token (if any) to every outgoing request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// --- Authentication -------------------------------------------------------
export async function login(username, password) {
  const { data } = await api.post("/login", { username, password });
  localStorage.setItem("access_token", data.access_token);
  return data;
}

export function logout() {
  return api.post("/logout").finally(() => localStorage.removeItem("access_token"));
}

export function changePassword(oldPassword, newPassword) {
  return api.post("/change-password", { old_password: oldPassword, new_password: newPassword });
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem("access_token"));
}

// --- Chatbot ---------------------------------------------------------
export function sendMessage(sessionId, query) {
  return api.post("/chat", { session_id: sessionId, query }).then((r) => r.data);
}

export function getHistory(sessionId) {
  return api.get("/history", { params: { session_id: sessionId } }).then((r) => r.data);
}

// --- Documents --------------------------------------------------------
export function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  return api
    .post("/upload", formData, { headers: { "Content-Type": "multipart/form-data" } })
    .then((r) => r.data);
}

export function listDocuments() {
  return api.get("/documents").then((r) => r.data);
}

export function deleteDocument(documentId) {
  return api.delete(`/documents/${documentId}`).then((r) => r.data);
}

// --- Dashboard ----------------------------------------------------------
export function getDashboardSummary() {
  return api.get("/dashboard").then((r) => r.data);
}

export function getAnalytics() {
  return api.get("/analytics").then((r) => r.data);
}

export function getLogs() {
  return api.get("/logs").then((r) => r.data);
}

export default api;
