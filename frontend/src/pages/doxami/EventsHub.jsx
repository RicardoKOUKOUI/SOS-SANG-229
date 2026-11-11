import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createEvent, listEvents } from "../../api/hub.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function EventsHub({ onToast }) {
  const { token, isAuthenticated } = useAuth();
  const [events, setEvents] = useState([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState({
    title: "",
    description: "",
    location_label: "",
    starts_at: "",
  });

  async function reload() {
    const data = await listEvents(token);
    setEvents(data);
  }

  useEffect(() => {
    let cancelled = false;
    reload()
      .catch((err) => {
        if (!cancelled) setError(err.message || "Events indisponibles.");
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function onSubmit(event) {
    event.preventDefault();
    if (!isAuthenticated) {
      onToast?.("Connectez-vous pour créer un événement.");
      return;
    }
    setBusy(true);
    try {
      await createEvent(token, {
        title: form.title.trim(),
        description: form.description.trim() || null,
        location_label: form.location_label.trim() || null,
        starts_at: new Date(form.starts_at).toISOString(),
      });
      setForm({ title: "", description: "", location_label: "", starts_at: "" });
      await reload();
      onToast?.("Événement créé.");
    } catch (err) {
      onToast?.(err.message || "Création impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">HUB-EVENTS</p>
      <h1 className="mt-2 text-3xl font-extrabold">Events</h1>
      <p className="mt-2 text-accent">Événements persistés en base (pas de carte sociale GPS).</p>
      {error ? <p className="mt-4 text-warn">{error}</p> : null}

      <ul className="mt-8 space-y-3">
        {events.map((item) => (
          <li key={item.id} className="card">
            <p className="font-semibold">{item.title}</p>
            <p className="mt-1 text-sm text-accent">
              {new Date(item.starts_at).toLocaleString()}
              {item.location_label ? ` · ${item.location_label}` : ""}
            </p>
            {item.description ? <p className="mt-2 text-sm">{item.description}</p> : null}
          </li>
        ))}
        {!error && events.length === 0 ? (
          <li className="card text-accent">Aucun événement pour l’instant.</li>
        ) : null}
      </ul>

      {isAuthenticated ? (
        <form className="card mt-8 space-y-3" onSubmit={onSubmit}>
          <h2 className="font-bold">Créer un événement</h2>
          <input
            className="field-input"
            required
            placeholder="Titre"
            value={form.title}
            onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
          />
          <input
            className="field-input"
            type="datetime-local"
            required
            value={form.starts_at}
            onChange={(e) => setForm((prev) => ({ ...prev, starts_at: e.target.value }))}
          />
          <input
            className="field-input"
            placeholder="Lieu (libellé)"
            value={form.location_label}
            onChange={(e) => setForm((prev) => ({ ...prev, location_label: e.target.value }))}
          />
          <textarea
            className="field-input min-h-24"
            placeholder="Description"
            value={form.description}
            onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
          />
          <button className="btn-primary" type="submit" disabled={busy}>
            {busy ? "…" : "Publier"}
          </button>
        </form>
      ) : (
        <p className="mt-8 text-sm text-accent">
          <Link to="/auth/login" className="font-semibold text-primary">
            Connectez-vous
          </Link>{" "}
          pour créer un événement.
        </p>
      )}

      <Link to="/hub" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Hub
      </Link>
    </section>
  );
}
