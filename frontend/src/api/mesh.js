import { apiRequest } from "./client.js";

export function fetchMeshStatus() {
  return apiRequest("/mesh/status");
}
