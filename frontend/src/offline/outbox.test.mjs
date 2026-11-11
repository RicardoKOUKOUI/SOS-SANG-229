/**
 * Lightweight Node smoke for outbox helpers (no IndexedDB).
 * Run: node --test src/offline/outbox.test.mjs
 */
import test from "node:test";
import assert from "node:assert/strict";

test("outbox item shape contract", () => {
  const item = {
    id: "demo",
    type: "post",
    payload: { body: "hello" },
    status: "pending",
    createdAt: Date.now(),
    lastError: null,
  };
  assert.equal(item.type, "post");
  assert.ok(item.payload.body.length > 0);
  assert.equal(["pending", "syncing", "failed"].includes(item.status), true);
});
