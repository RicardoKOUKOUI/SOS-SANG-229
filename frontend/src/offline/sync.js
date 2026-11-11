import { createPost, createComment } from "../api/social.js";
import { sendThreadMessage, sendRoomMessage } from "../api/messaging.js";
import { listOutboxItems, removeOutboxItem, updateOutboxItem } from "./outbox.js";

/**
 * Flush pending outbox items while online.
 * Returns { synced, failed }.
 */
export async function flushOutbox(token) {
  if (!token || typeof navigator !== "undefined" && !navigator.onLine) {
    return { synced: 0, failed: 0 };
  }
  const items = await listOutboxItems();
  let synced = 0;
  let failed = 0;

  for (const item of items) {
    if (item.status === "syncing") continue;
    await updateOutboxItem(item.id, { status: "syncing", lastError: null });
    try {
      if (item.type === "post") {
        await createPost(token, item.payload.body);
      } else if (item.type === "thread_message") {
        await sendThreadMessage(token, item.payload.threadId, item.payload.body);
      } else if (item.type === "room_message") {
        await sendRoomMessage(
          token,
          item.payload.communityId,
          item.payload.roomId,
          item.payload.body,
        );
      } else if (item.type === "comment") {
        await createComment(token, item.payload.postId, item.payload.body);
      } else {
        throw new Error(`Unknown outbox type: ${item.type}`);
      }
      await removeOutboxItem(item.id);
      synced += 1;
    } catch (err) {
      await updateOutboxItem(item.id, {
        status: "failed",
        lastError: err?.message || "Sync failed",
      });
      failed += 1;
    }
  }

  return { synced, failed };
}
