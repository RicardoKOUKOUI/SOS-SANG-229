import { apiRequest } from "./client.js";

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function listEvents(token) {
  return apiRequest("/events", { headers: authHeaders(token) });
}

export function createEvent(token, payload) {
  return apiRequest("/events", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export function getAiStatus() {
  return apiRequest("/ai/status");
}

export function aiChat(token, message) {
  return apiRequest("/ai/chat", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ message }),
  });
}
