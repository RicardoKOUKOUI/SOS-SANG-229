/**
 * Client API SOS Sang 229.
 * En local: proxy Vite `/api` → :8000.
 * Sur Vercel: rewrites `/api` → API Railway (voir vercel.json).
 * Override possible: VITE_API_BASE.
 */

const API_BASE = (import.meta.env.VITE_API_BASE || "/api").replace(/\/$/, "");

const ERROR_FR = {
  "A donor with this phone is already registered.":
    "Un donneur avec ce numéro est déjà inscrit.",
};

function localizeDetail(detail) {
  if (typeof detail !== "string") return detail;
  return ERROR_FR[detail] || detail;
}

async function parseError(response) {
  let detail = `Erreur HTTP ${response.status}`;
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") detail = localizeDetail(body.detail);
    else if (Array.isArray(body?.detail)) {
      detail = body.detail
        .map((item) => item.msg || JSON.stringify(item))
        .join(" · ");
    } else if (body?.detail) detail = JSON.stringify(body.detail);
  } catch {
    /* ignore */
  }
  const err = new Error(detail);
  err.status = response.status;
  return err;
}

export async function apiRequest(path, options = {}) {
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;
  const headers = {
    Accept: "application/json",
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...options.headers,
  };
  const response = await fetch(url, { ...options, headers });
  if (!response.ok) throw await parseError(response);
  if (response.status === 204) return null;
  return response.json();
}

export function listRecognizedHospitals() {
  return apiRequest("/hospitals/recognized");
}

export function createDonor(payload) {
  return apiRequest("/donors", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createAlert(payload) {
  return apiRequest("/alerts", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listRequests() {
  return apiRequest("/requests");
}

export function getRequest(publicRef) {
  return apiRequest(`/requests/${encodeURIComponent(publicRef)}`);
}

/** Map backend UrgencyStatus → clés UI françaises (STATUS_META). */
export const BACKEND_STATUS_TO_UI = {
  open: "ouverte",
  alerting: "en matching",
  fulfilled: "pourvue",
  cancelled: "annulee",
};

export const BACKEND_STATUS_LABELS = {
  open: "Ouverte",
  alerting: "Recherche en cours",
  fulfilled: "Pourvue",
  cancelled: "Annulée",
};
