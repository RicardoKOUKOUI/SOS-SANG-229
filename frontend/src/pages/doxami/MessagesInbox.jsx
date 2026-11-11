import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listThreads } from "../../api/messaging.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function InboxInner({ onToast }) {
  const { token, user } = useAuth();
  const [threads, setThreads] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await listThreads(token);
        if (!cancelled) setThreads(data);
      } catch (err) {
        if (!cancelled) setError(err.message || "Inbox indisponible.");
      }
    }
    load();
    const timer = setInterval(load, 8000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [token]);

  function threadLabel(thread) {
    if (thread.kind === "group") return thread.title || "Groupe";
    const other = thread.members.find((member) => member.username !== user.username);
    return other ? `${other.display_name} (@${other.username})` : "Discussion";
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">MSG-001</p>
      <div className="mt-2 flex flex-wrap items-end justify-between gap-3">
        <h1 className="text-3xl font-extrabold">Messages</h1>
        <Link to="/messages/new" className="btn-primary">
          Nouveau
        </Link>
      </div>
      <p className="mt-2 text-accent">Texte 1:1 / groupe · rafraîchissement polling (pas de WebRTC).</p>
      {error ? <p className="mt-6 text-warn">{error}</p> : null}
      <ul className="mt-8 space-y-3">
        {threads.map((thread) => (
          <li key={thread.id}>
            <Link to={`/messages/${thread.id}`} className="card block hover:border-primary/40">
              <span className="font-semibold">{threadLabel(thread)}</span>
              <p className="mt-1 text-sm text-accent">
                {thread.last_message
                  ? `${thread.last_message.sender.username}: ${thread.last_message.body}`
                  : "Aucun message"}
              </p>
            </Link>
          </li>
        ))}
        {!error && threads.length === 0 ? (
          <li className="card text-accent">MSG-004 · Inbox vide. Démarrez une conversation.</li>
        ) : null}
      </ul>
    </section>
  );
}

export default function MessagesInbox({ onToast }) {
  return (
    <RequireAuth>
      <InboxInner onToast={onToast} />
    </RequireAuth>
  );
}
