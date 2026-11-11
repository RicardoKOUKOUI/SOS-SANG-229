/**
 * MeshTransport interface (architecture-ready).
 * Web default implementation reports unsupported — never fakes delivery.
 */

import { detectMeshCapabilities } from "./capabilities.js";

export class UnsupportedMeshTransport {
  constructor(reason) {
    this.reason = reason || "MESH transport unavailable in this runtime.";
  }

  async getStatus() {
    const caps = detectMeshCapabilities();
    return {
      available: false,
      reason: this.reason,
      capabilities: caps,
    };
  }

  async send() {
    throw new Error(this.reason);
  }

  async startDiscovery() {
    throw new Error(this.reason);
  }
}

export class NativeBridgeMeshTransport {
  constructor(bridge) {
    this.bridge = bridge;
  }

  async getStatus() {
    const caps = detectMeshCapabilities();
    return {
      available: true,
      reason: "Native bridge detected.",
      capabilities: caps,
    };
  }

  async send(envelope) {
    return this.bridge.send(envelope);
  }

  async startDiscovery() {
    if (typeof this.bridge.startDiscovery !== "function") {
      throw new Error("Native bridge does not implement startDiscovery.");
    }
    return this.bridge.startDiscovery();
  }
}

export function createMeshTransport() {
  const bridge = typeof window !== "undefined" ? window.DoxamiNativeMesh : null;
  if (bridge && typeof bridge.send === "function") {
    return new NativeBridgeMeshTransport(bridge);
  }
  return new UnsupportedMeshTransport(
    "No DoxamiNativeMesh bridge. Web offline sync ≠ MESH P2P.",
  );
}
