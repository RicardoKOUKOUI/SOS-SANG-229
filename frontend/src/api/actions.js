import { apiRequest } from "./client.js";

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function listProjects(token) {
  return apiRequest("/actions", { headers: authHeaders(token) });
}

export function createProject(token, payload) {
  return apiRequest("/actions", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export function createFromPost(token, postId) {
  return apiRequest(`/actions/from-post/${postId}`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export function getProject(token, projectId) {
  return apiRequest(`/actions/${projectId}`, { headers: authHeaders(token) });
}

export function listTasks(token, projectId) {
  return apiRequest(`/actions/${projectId}/tasks`, { headers: authHeaders(token) });
}

export function createTask(token, projectId, payload) {
  return apiRequest(`/actions/${projectId}/tasks`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export function updateTask(token, projectId, taskId, payload) {
  return apiRequest(`/actions/${projectId}/tasks/${taskId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export function listTeam(token, projectId) {
  return apiRequest(`/actions/${projectId}/team`, { headers: authHeaders(token) });
}

export function addTeamMember(token, projectId, username) {
  return apiRequest(`/actions/${projectId}/team`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ username }),
  });
}

export function getProgress(token, projectId) {
  return apiRequest(`/actions/${projectId}/progress`, { headers: authHeaders(token) });
}
