/**
 * Detect local MESH capability. Browser alone cannot run BLE/Wi-Fi Direct MESH.
 * A future native shell may inject window.DoxamiNativeMesh.
 */

export function detectMeshCapabilities() {
  const bridge = typeof window !== "undefined" ? window.DoxamiNativeMesh : null;
  const hasBridge = Boolean(bridge && typeof bridge.send === "function");
  return {
    online: typeof navigator === "undefined" ? true : navigator.onLine,
    nativeBridge: hasBridge,
    ble: Boolean(hasBridge && bridge.supports?.ble),
    wifiDirect: Boolean(hasBridge && bridge.supports?.wifiDirect),
    nearby: Boolean(hasBridge && bridge.supports?.nearby),
    libp2p: Boolean(hasBridge && bridge.supports?.libp2p),
    meshAvailable: hasBridge,
  };
}

export function resolveLocalMode(capabilities = detectMeshCapabilities()) {
  if (capabilities.meshAvailable && capabilities.online === false) {
    // Native mesh can still operate offline-local.
    return "MESH";
  }
  if (!capabilities.online) return "OFFLINE";
  return "ONLINE";
}
