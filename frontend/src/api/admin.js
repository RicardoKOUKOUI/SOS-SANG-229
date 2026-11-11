import { apiRequest } from "./client.js";

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function bootstrapAdmin(username, token) {
  return apiRequest("/admin/bootstrap", {
    method: "POST",
    body: JSON.stringify({ username, token }),
  });
}

export function enrollMfa(token) {
  return apiRequest("/admin/mfa/enroll", {
    method: "POST",
    headers: authHeaders(token),
  });
}

export function confirmMfa(token, code) {
  return apiRequest("/admin/mfa/confirm", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ code }),
  });
}

export function verifyMfa(token, code) {
  return apiRequest("/admin/mfa/verify", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ code }),
  });
}

export function getAdminDashboard(token) {
  return apiRequest("/admin/dashboard", { headers: authHeaders(token) });
}

export function listAdminUsers(token) {
  return apiRequest("/admin/users", { headers: authHeaders(token) });
}

export function setUserActive(token, userId, isActive) {
  return apiRequest(`/admin/users/${userId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify({ is_active: isActive }),
  });
}

export function listModerationPosts(token) {
  return apiRequest("/admin/moderation/posts", { headers: authHeaders(token) });
}

export function hidePost(token, postId) {
  return apiRequest(`/admin/moderation/posts/${postId}/hide`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export function restorePost(token, postId) {
  return apiRequest(`/admin/moderation/posts/${postId}/restore`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export function listFlags(token) {
  return apiRequest("/admin/flags", { headers: authHeaders(token) });
}

export function updateFlag(token, key, enabled) {
  return apiRequest(`/admin/flags/${key}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify({ enabled }),
  });
}

export function listAuditLogs(token) {
  return apiRequest("/admin/logs", { headers: authHeaders(token) });
}
