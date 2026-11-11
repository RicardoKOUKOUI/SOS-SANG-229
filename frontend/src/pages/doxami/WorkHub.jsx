import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createJob, listJobs } from "../../api/listings.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function WorkHub({ onToast }) {
  const { token, isAuthenticated } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [form, setForm] = useState({ title: "", description: "", city_label: "" });
  const [busy, setBusy] = useState(false);

  async function reload() {
    setJobs(await listJobs());
  }

  useEffect(() => {
    reload().catch((err) => onToast?.(err.message || "Offres indisponibles."));
  }, [onToast]);

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await createJob(token, {
        title: form.title.trim(),
        description: form.description.trim() || null,
        city_label: form.city_label.trim() || null,
      });
      setForm({ title: "", description: "", city_label: "" });
      await reload();
      onToast?.("Offre publiée.");
    } catch (err) {
      onToast?.(err.message || "Publication impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">HUB-WORK</p>
      <h1 className="mt-2 text-3xl font-extrabold">Work</h1>
      <p className="mt-2 text-accent">Annonces textuelles. Aucune candidature payante.</p>
      <ul className="mt-8 space-y-3">
        {jobs.map((job) => (
          <li key={job.id}>
            <Link to={`/hub/work/${job.id}`} className="card block hover:border-primary/40">
              <p className="font-semibold">{job.title}</p>
              <p className="text-sm text-accent">
                {job.city_label || "Lieu non précisé"} · @{job.created_by.username}
              </p>
            </Link>
          </li>
        ))}
        {jobs.length === 0 ? <li className="card text-accent">Aucune offre.</li> : null}
      </ul>
      {isAuthenticated ? (
        <form className="card mt-8 space-y-3" onSubmit={onSubmit}>
          <h2 className="font-bold">Publier une offre</h2>
          <input
            className="field-input"
            required
            placeholder="Titre"
            value={form.title}
            onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
          />
          <input
            className="field-input"
            placeholder="Ville (libellé)"
            value={form.city_label}
            onChange={(e) => setForm((prev) => ({ ...prev, city_label: e.target.value }))}
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
      ) : null}
      <Link to="/hub" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Hub
      </Link>
    </section>
  );
}
