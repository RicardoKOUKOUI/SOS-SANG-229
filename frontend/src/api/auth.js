import { apiRequest } from "./client.js";

export function registerAccount(payload) {
  return apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function loginAccount(payload) {
  return apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchMe(token) {
  return apiRequest("/auth/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function logoutAccount(token) {
  return apiRequest("/auth/logout", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function updateMyProfile(token, payload) {
  return apiRequest("/users/me", {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export function fetchPublicProfile(username) {
  return apiRequest(`/users/${encodeURIComponent(username)}`);
}
