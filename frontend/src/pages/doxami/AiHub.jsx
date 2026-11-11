import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { aiChat, getAiStatus } from "../../api/hub.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function Inner({ onToast }) {
  const { token } = useAuth();
  const [status, setStatus] = useState(null);
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getAiStatus()
      .then(setStatus)
      .catch((err) => onToast?.(err.message || "Statut AI indisponible."));
  }, [onToast]);

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setReply("");
    try {
      const result = await aiChat(token, message);
      setReply(result.reply);
    } catch (err) {
      onToast?.(err.message || "Assistant indisponible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">HUB-AI</p>
      <h1 className="mt-2 text-3xl font-extrabold">DOXAMI AI</h1>
      <div className="card mt-6 space-y-2">
        {status ? (
          <>
            <p className="font-semibold">
              Configuré : {status.configured ? "oui" : "non"}
            </p>
            <p className="text-sm text-accent">{status.reason}</p>
            {status.provider ? (
              <p className="text-sm text-accent">Modèle : {status.provider}</p>
            ) : null}
          </>
        ) : (
          <p className="text-accent">Chargement du statut…</p>
        )}
      </div>

      <form className="mt-8 space-y-3" onSubmit={onSubmit}>
        <textarea
          className="field-input min-h-28"
          required
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Posez une question…"
          disabled={!status?.configured}
        />
        <button className="btn-primary" type="submit" disabled={busy || !status?.configured}>
          {busy ? "…" : status?.configured ? "Envoyer" : "Indisponible sans clé API"}
        </button>
      </form>

      {reply ? (
        <div className="card mt-6">
          <h2 className="font-bold">Réponse</h2>
          <p className="mt-2 whitespace-pre-wrap">{reply}</p>
        </div>
      ) : null}

      <Link to="/hub" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Hub
      </Link>
    </section>
  );
}

export default function AiHub({ onToast }) {
  return (
    <RequireAuth>
      <Inner onToast={onToast} />
    </RequireAuth>
  );
}
