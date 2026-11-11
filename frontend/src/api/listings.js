import { apiRequest } from "./client.js";

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function listProfessionals() {
  return apiRequest("/professionals");
}

export function getMyProfessional(token) {
  return apiRequest("/professional/me", { headers: authHeaders(token) });
}

export function saveProfessional(token, payload) {
  return apiRequest("/professional/me", {
    method: "PUT",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export function listJobs() {
  return apiRequest("/jobs");
}

export function createJob(token, payload) {
  return apiRequest("/jobs", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export function getJob(jobId) {
  return apiRequest(`/jobs/${jobId}`);
}

export function listMarket() {
  return apiRequest("/marketplace");
}

export function createListing(token, payload) {
  return apiRequest("/marketplace", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export function getListing(listingId) {
  return apiRequest(`/marketplace/${listingId}`);
}

export function checkoutListing(token, listingId) {
  return apiRequest(`/marketplace/${listingId}/checkout`, {
    method: "POST",
    headers: authHeaders(token),
  });
}
