import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createGroupThread, openDirectThread } from "../../api/messaging.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function NewInner({ onToast }) {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState("direct");
  const [username, setUsername] = useState("");
  const [title, setTitle] = useState("");
  const [usernames, setUsernames] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      if (mode === "direct") {
        const thread = await openDirectThread(token, username.trim());
        navigate(`/messages/${thread.id}`);
      } else {
        const list = usernames
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean);
        const thread = await createGroupThread(token, title.trim(), list);
        navigate(`/messages/${thread.id}`);
      }
    } catch (err) {
      onToast?.(err.message || "Impossible de créer la conversation.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Nouveau message</h1>
      <p className="mt-2 text-accent">MSG-003 / MSG-006</p>
      <div className="mt-6 flex gap-2">
        <button
          type="button"
          className={mode === "direct" ? "btn-primary" : "btn-secondary"}
          onClick={() => setMode("direct")}
        >
          1:1
        </button>
        <button
          type="button"
          className={mode === "group" ? "btn-primary" : "btn-secondary"}
          onClick={() => setMode("group")}
        >
          Groupe
        </button>
      </div>
      <form className="mt-8 space-y-4" onSubmit={onSubmit}>
        {mode === "direct" ? (
          <label className="block space-y-1.5">
            <span className="field-label">Nom d’utilisateur</span>
            <input
              className="field-input"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="ex. bob_demo"
            />
          </label>
        ) : (
          <>
            <label className="block space-y-1.5">
              <span className="field-label">Titre du groupe</span>
              <input className="field-input" required value={title} onChange={(e) => setTitle(e.target.value)} />
            </label>
            <label className="block space-y-1.5">
              <span className="field-label">Membres (usernames, séparés par des virgules)</span>
              <input
                className="field-input"
                value={usernames}
                onChange={(e) => setUsernames(e.target.value)}
                placeholder="alice_demo, bob_demo"
              />
            </label>
          </>
        )}
        <button className="btn-primary w-full" type="submit" disabled={busy}>
          {busy ? "Création…" : "Ouvrir"}
        </button>
      </form>
      <Link to="/messages" className="mt-6 inline-block text-sm font-semibold text-primary">
        ← Inbox
      </Link>
    </section>
  );
}

export default function MessageNew({ onToast }) {
  return (
    <RequireAuth>
      <NewInner onToast={onToast} />
    </RequireAuth>
  );
}
