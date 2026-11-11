import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getThread, listThreadMessages, sendThreadMessage } from "../../api/messaging.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";
import { useOffline } from "../../offline/OfflineContext.jsx";
import { enqueueOutboxItem } from "../../offline/outbox.js";

function ThreadInner({ onToast }) {
  const { threadId } = useParams();
  const { token, user } = useAuth();
  const { online, refreshPending, dataSaver } = useOffline();
  const [thread, setThread] = useState(null);
  const [messages, setMessages] = useState([]);
  const [body, setBody] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function reload() {
    const [threadData, messageData] = await Promise.all([
      getThread(token, threadId),
      listThreadMessages(token, threadId),
    ]);
    setThread(threadData);
    setMessages(messageData);
  }

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setError("");
      try {
        await reload();
      } catch (err) {
        if (!cancelled) setError(err.message || "Thread indisponible.");
      }
    }
    load();
    const timer = setInterval(() => {
      if (!navigator.onLine) return;
      reload().catch(() => {});
    }, dataSaver ? 15000 : 5000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [threadId, token, dataSaver]);

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      if (!online) {
        await enqueueOutboxItem({
          type: "thread_message",
          payload: { threadId, body: body.trim() },
        });
        await refreshPending();
        setBody("");
        onToast?.("Hors ligne — message mis en file.");
        return;
      }
      await sendThreadMessage(token, threadId, body);
      setBody("");
      await reload();
    } catch (err) {
      if (!navigator.onLine || /Failed to fetch|NetworkError/i.test(err.message || "")) {
        await enqueueOutboxItem({
          type: "thread_message",
          payload: { threadId, body: body.trim() },
        });
        await refreshPending();
        setBody("");
        onToast?.("Réseau indisponible — message mis en file.");
      } else {
        onToast?.(err.message || "Envoi impossible.");
      }
    } finally {
      setBusy(false);
    }
  }

  const title =
    thread?.kind === "group"
      ? thread.title
      : thread?.members?.find((member) => member.username !== user.username)?.display_name ||
        "Discussion";

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">MSG-002</p>
      <h1 className="mt-2 text-3xl font-extrabold">{title || "…"}</h1>
      {thread ? (
        <Link to={`/messages/${threadId}/info`} className="text-sm font-semibold text-primary">
          Infos conversation · MSG-007
        </Link>
      ) : null}
      {error ? <p className="mt-6 text-warn">{error}</p> : null}
      <ul className="mt-8 space-y-3">
        {messages.map((message) => (
          <li
            key={message.id}
            className={`rounded-xl px-4 py-3 ${
              message.sender.username === user.username
                ? "bg-primary/10 ml-8"
                : "bg-white border border-light mr-8"
            }`}
          >
            <p className="text-xs font-semibold text-accent">@{message.sender.username}</p>
            <p className="mt-1 whitespace-pre-wrap">{message.body}</p>
          </li>
        ))}
      </ul>
      <form className="mt-6 space-y-3" onSubmit={onSubmit}>
        <textarea
          className="field-input min-h-24"
          required
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Écrire un message…"
        />
        <button className="btn-primary" type="submit" disabled={busy}>
          {busy ? "Envoi…" : "Envoyer"}
        </button>
      </form>
      <Link to="/messages" className="mt-6 inline-block text-sm font-semibold text-primary">
        ← Inbox
      </Link>
    </section>
  );
}

export default function MessageThread({ onToast }) {
  return (
    <RequireAuth>
      <ThreadInner onToast={onToast} />
    </RequireAuth>
  );
}
