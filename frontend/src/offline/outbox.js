/**
 * IndexedDB outbox for offline text posts/messages.
 * No media. Status: pending | syncing | failed
 */

const DB_NAME = "doxami-offline";
const DB_VERSION = 1;
const STORE = "outbox";

function openDb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE)) {
        const store = db.createObjectStore(STORE, { keyPath: "id" });
        store.createIndex("by_status", "status", { unique: false });
        store.createIndex("by_created", "createdAt", { unique: false });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error("IndexedDB open failed"));
  });
}

function txDone(tx) {
  return new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error || new Error("IndexedDB tx failed"));
    tx.onabort = () => reject(tx.error || new Error("IndexedDB tx aborted"));
  });
}

export async function enqueueOutboxItem({ type, payload }) {
  const db = await openDb();
  const item = {
    id: crypto.randomUUID(),
    type,
    payload,
    status: "pending",
    createdAt: Date.now(),
    lastError: null,
  };
  const tx = db.transaction(STORE, "readwrite");
  tx.objectStore(STORE).put(item);
  await txDone(tx);
  db.close();
  return item;
}

export async function listOutboxItems() {
  const db = await openDb();
  const tx = db.transaction(STORE, "readonly");
  const store = tx.objectStore(STORE);
  const items = await new Promise((resolve, reject) => {
    const request = store.getAll();
    request.onsuccess = () => resolve(request.result || []);
    request.onerror = () => reject(request.error);
  });
  await txDone(tx);
  db.close();
  return items.sort((a, b) => a.createdAt - b.createdAt);
}

export async function updateOutboxItem(id, patch) {
  const db = await openDb();
  const tx = db.transaction(STORE, "readwrite");
  const store = tx.objectStore(STORE);
  const existing = await new Promise((resolve, reject) => {
    const request = store.get(id);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
  if (!existing) {
    db.close();
    return null;
  }
  const next = { ...existing, ...patch };
  store.put(next);
  await txDone(tx);
  db.close();
  return next;
}

export async function removeOutboxItem(id) {
  const db = await openDb();
  const tx = db.transaction(STORE, "readwrite");
  tx.objectStore(STORE).delete(id);
  await txDone(tx);
  db.close();
}

export async function pendingCount() {
  const items = await listOutboxItems();
  return items.filter((item) => item.status === "pending" || item.status === "failed").length;
}
