import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createPost } from "../../api/social.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";
import { useOffline } from "../../offline/OfflineContext.jsx";
import { enqueueOutboxItem } from "../../offline/outbox.js";

function CreateInner({ onToast }) {
  const { token } = useAuth();
  const { online, refreshPending } = useOffline();
  const navigate = useNavigate();
  const [body, setBody] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      if (!online) {
        await enqueueOutboxItem({ type: "post", payload: { body: body.trim() } });
        await refreshPending();
        onToast?.("Hors ligne — publication mise en file IndexedDB.");
        navigate("/");
        return;
      }
      const post = await createPost(token, body);
      onToast?.("Publication créée.");
      navigate(`/posts/${post.id}`);
    } catch (err) {
      // Network failure while "online" → queue instead of fake success.
      if (!navigator.onLine || err.status === 0 || /Failed to fetch|NetworkError/i.test(err.message || "")) {
        await enqueueOutboxItem({ type: "post", payload: { body: body.trim() } });
        await refreshPending();
        onToast?.("Réseau indisponible — publication mise en file.");
        navigate("/");
      } else {
        onToast?.(err.message || "Publication impossible.");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Créer</h1>
      <p className="mt-2 text-accent">
        CREATE-001 · texte uniquement. {online ? "En ligne" : "Hors ligne → file sync"}
      </p>
      <form className="mt-8 space-y-4" onSubmit={onSubmit}>
        <label className="block space-y-1.5">
          <span className="field-label">Votre publication</span>
          <textarea
            className="field-input min-h-40"
            required
            maxLength={4000}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Partagez une idée…"
          />
        </label>
        <p className="text-sm text-accent">Images / vidéo : non activées — aucun faux upload.</p>
        <button className="btn-primary w-full" type="submit" disabled={busy || !body.trim()}>
          {busy ? "…" : online ? "Publier" : "Mettre en file offline"}
        </button>
      </form>
      <Link to="/" className="mt-6 inline-block text-sm font-semibold text-primary">
        ← Accueil
      </Link>
    </section>
  );
}

export default function CreatePost({ onToast }) {
  return (
    <RequireAuth>
      <CreateInner onToast={onToast} />
    </RequireAuth>
  );
}
