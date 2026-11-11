import { apiRequest } from "./client.js";

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function listPosts(tab = "recent", token) {
  const query = tab === "following" ? "?tab=following" : "?tab=recent";
  return apiRequest(`/posts${query}`, { headers: authHeaders(token) });
}

export function createPost(token, body) {
  return apiRequest("/posts", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ body }),
  });
}

export function getPost(postId, token) {
  return apiRequest(`/posts/${encodeURIComponent(postId)}`, {
    headers: authHeaders(token),
  });
}

export function likePost(token, postId) {
  return apiRequest(`/posts/${encodeURIComponent(postId)}/likes`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export function unlikePost(token, postId) {
  return apiRequest(`/posts/${encodeURIComponent(postId)}/likes`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
}

export function listComments(postId) {
  return apiRequest(`/posts/${encodeURIComponent(postId)}/comments`);
}

export function createComment(token, postId, body) {
  return apiRequest(`/posts/${encodeURIComponent(postId)}/comments`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ body }),
  });
}

export function followUser(token, username) {
  return apiRequest(`/users/${encodeURIComponent(username)}/follow`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export function unfollowUser(token, username) {
  return apiRequest(`/users/${encodeURIComponent(username)}/follow`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
}

export function listFollowers(username) {
  return apiRequest(`/users/${encodeURIComponent(username)}/followers`);
}

export function listFollowing(username) {
  return apiRequest(`/users/${encodeURIComponent(username)}/following`);
}

export function exploreSearch(q, token) {
  return apiRequest(`/explore/search?q=${encodeURIComponent(q)}`, {
    headers: authHeaders(token),
  });
}
