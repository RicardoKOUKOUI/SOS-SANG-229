import test from "node:test";
import assert from "node:assert/strict";
import { resolveLocalMode } from "./capabilities.js";

test("resolveLocalMode distinguishes offline from mesh", () => {
  assert.equal(resolveLocalMode({ online: true, meshAvailable: false }), "ONLINE");
  assert.equal(resolveLocalMode({ online: false, meshAvailable: false }), "OFFLINE");
  assert.equal(resolveLocalMode({ online: false, meshAvailable: true }), "MESH");
});
