import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyProfessional, listProfessionals, saveProfessional } from "../../api/listings.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function ProfessionalHub({ onToast }) {
  const { token, isAuthenticated } = useAuth();
  const [profiles, setProfiles] = useState([]);
  const [form, setForm] = useState({
    headline: "",
    organization: "",
    city_label: "",
    summary: "",
  });
  const [busy, setBusy] = useState(false);

  async function reload() {
    setProfiles(await listProfessionals());
  }

  useEffect(() => {
    reload().catch((err) => onToast?.(err.message || "Profils indisponibles."));
    if (!token) return;
    getMyProfessional(token)
      .then((profile) => {
        setForm({
          headline: profile.headline || "",
          organization: profile.organization || "",
          city_label: profile.city_label || "",
          summary: profile.summary || "",
        });
      })
      .catch((err) => {
        if (err.status !== 404) onToast?.(err.message || "Profil indisponible.");
      });
  }, [token, onToast]);

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await saveProfessional(token, {
        headline: form.headline.trim(),
        organization: form.organization.trim() || null,
        city_label: form.city_label.trim() || null,
        summary: form.summary.trim() || null,
      });
      await reload();
      onToast?.("Profil professionnel enregistré.");
    } catch (err) {
      onToast?.(err.message || "Enregistrement impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">HUB-PRO</p>
      <h1 className="mt-2 text-3xl font-extrabold">Professional</h1>
      <p className="mt-2 text-accent">
        Fiches publiques. Le libellé de ville n’est pas une coordonnée GPS.
      </p>
      <ul className="mt-8 space-y-3">
        {profiles.map((profile) => (
          <li key={profile.id} className="card">
            <p className="font-semibold">{profile.headline}</p>
            <p className="text-sm text-accent">
              {profile.organization || "Indépendant"}
              {profile.city_label ? ` · ${profile.city_label}` : ""} · @{profile.user.username}
            </p>
            {profile.summary ? <p className="mt-2 text-sm">{profile.summary}</p> : null}
          </li>
        ))}
        {profiles.length === 0 ? <li className="card text-accent">Aucune fiche.</li> : null}
      </ul>
      {isAuthenticated ? (
        <form className="card mt-8 space-y-3" onSubmit={onSubmit}>
          <h2 className="font-bold">Ma fiche</h2>
          <input
            className="field-input"
            required
            placeholder="Titre"
            value={form.headline}
            onChange={(e) => setForm((prev) => ({ ...prev, headline: e.target.value }))}
          />
          <input
            className="field-input"
            placeholder="Organisation"
            value={form.organization}
            onChange={(e) => setForm((prev) => ({ ...prev, organization: e.target.value }))}
          />
          <input
            className="field-input"
            placeholder="Ville (libellé)"
            value={form.city_label}
            onChange={(e) => setForm((prev) => ({ ...prev, city_label: e.target.value }))}
          />
          <textarea
            className="field-input min-h-24"
            placeholder="Résumé"
            value={form.summary}
            onChange={(e) => setForm((prev) => ({ ...prev, summary: e.target.value }))}
          />
          <button className="btn-primary" type="submit" disabled={busy}>
            {busy ? "…" : "Enregistrer"}
          </button>
        </form>
      ) : (
        <p className="mt-8 text-sm text-accent">
          <Link to="/auth/login" className="font-semibold text-primary">
            Connectez-vous
          </Link>{" "}
          pour publier une fiche.
        </p>
      )}
      <Link to="/hub" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Hub
      </Link>
    </section>
  );
}
