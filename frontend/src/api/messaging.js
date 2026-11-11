import { apiRequest } from "./client.js";

function authHeaders(token) {
  return { Authorization: `Bearer ${token}` };
}

export function listThreads(token) {
  return apiRequest("/messages/threads", { headers: authHeaders(token) });
}

export function openDirectThread(token, username) {
  return apiRequest("/messages/threads/direct", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ username }),
  });
}

export function createGroupThread(token, title, usernames) {
  return apiRequest("/messages/threads/group", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ title, usernames }),
  });
}

export function getThread(token, threadId) {
  return apiRequest(`/messages/threads/${encodeURIComponent(threadId)}`, {
    headers: authHeaders(token),
  });
}

export function listThreadMessages(token, threadId) {
  return apiRequest(`/messages/threads/${encodeURIComponent(threadId)}/messages`, {
    headers: authHeaders(token),
  });
}

export function sendThreadMessage(token, threadId, body) {
  return apiRequest(`/messages/threads/${encodeURIComponent(threadId)}/messages`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ body }),
  });
}

export function listCommunities(token) {
  return apiRequest("/communities", {
    headers: token ? authHeaders(token) : {},
  });
}

export function createCommunity(token, payload) {
  return apiRequest("/communities", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export function getCommunity(token, communityId) {
  return apiRequest(`/communities/${encodeURIComponent(communityId)}`, {
    headers: token ? authHeaders(token) : {},
  });
}

export function joinCommunity(token, communityId) {
  return apiRequest(`/communities/${encodeURIComponent(communityId)}/join`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export function listCommunityMembers(communityId) {
  return apiRequest(`/communities/${encodeURIComponent(communityId)}/members`);
}

export function listCommunityRooms(token, communityId) {
  return apiRequest(`/communities/${encodeURIComponent(communityId)}/rooms`, {
    headers: authHeaders(token),
  });
}

export function listRoomMessages(token, communityId, roomId) {
  return apiRequest(
    `/communities/${encodeURIComponent(communityId)}/rooms/${encodeURIComponent(roomId)}/messages`,
    { headers: authHeaders(token) },
  );
}

export function sendRoomMessage(token, communityId, roomId, body) {
  return apiRequest(
    `/communities/${encodeURIComponent(communityId)}/rooms/${encodeURIComponent(roomId)}/messages`,
    {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ body }),
    },
  );
}
