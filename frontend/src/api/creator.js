import { apiRequest } from "./client.js";

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function getCreatorMe(token) {
  return apiRequest("/creator/me", { headers: authHeaders(token) });
}

export function saveCreatorMe(token, payload) {
  return apiRequest("/creator/me", {
    method: "PUT",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export function getMonetizationStatus() {
  return apiRequest("/monetization/status");
}

export function listPremiumPlans() {
  return apiRequest("/monetization/plans");
}

export function requestCheckout(token) {
  return apiRequest("/monetization/checkout", {
    method: "POST",
    headers: authHeaders(token),
  });
}

export function requestPayout(token) {
  return apiRequest("/creator/payouts", {
    method: "POST",
    headers: authHeaders(token),
  });
}
