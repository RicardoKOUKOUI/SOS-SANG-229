import assert from "node:assert/strict";
import { detectMeshCapabilities, resolveLocalMode } from "../src/mesh/capabilities.js";

assert.equal(resolveLocalMode({ meshAvailable: false, online: true }), "ONLINE");
assert.equal(resolveLocalMode({ meshAvailable: false, online: false }), "OFFLINE");
assert.equal(resolveLocalMode({ meshAvailable: true, online: false }), "MESH");
assert.equal(resolveLocalMode({ meshAvailable: true, online: true }), "ONLINE");

const detected = detectMeshCapabilities();
assert.equal(detected.nativeBridge, false);
assert.equal(detected.meshAvailable, false);
assert.equal(detected.ble, false);

console.log("mesh mode checks ok");
