import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createCommunity } from "../../api/messaging.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function Inner({ onToast }) {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    slug: "",
    description: "",
  });
  const [busy, setBusy] = useState(false);

  function update(field) {
    return (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));
  }

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      const community = await createCommunity(token, {
        name: form.name.trim(),
        slug: form.slug.trim().toLowerCase(),
        description: form.description.trim() || null,
        is_public: true,
      });
      onToast?.("Communauté créée.");
      navigate(`/communities/${community.id}`);
    } catch (err) {
      onToast?.(err.message || "Création impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Créer une communauté</h1>
      <p className="mt-2 text-accent">COM-003</p>
      <form className="mt-8 space-y-4" onSubmit={onSubmit}>
        <label className="block space-y-1.5">
          <span className="field-label">Nom</span>
          <input className="field-input" required value={form.name} onChange={update("name")} />
        </label>
        <label className="block space-y-1.5">
          <span className="field-label">Slug</span>
          <input
            className="field-input"
            required
            pattern="[a-z0-9-]{3,64}"
            value={form.slug}
            onChange={update("slug")}
          />
        </label>
        <label className="block space-y-1.5">
          <span className="field-label">Description</span>
          <textarea className="field-input min-h-24" value={form.description} onChange={update("description")} />
        </label>
        <button className="btn-primary w-full" type="submit" disabled={busy}>
          {busy ? "Création…" : "Créer"}
        </button>
      </form>
      <Link to="/communities" className="mt-6 inline-block text-sm font-semibold text-primary">
        ← Liste
      </Link>
    </section>
  );
}

export default function CommunityNew({ onToast }) {
  return (
    <RequireAuth>
      <Inner onToast={onToast} />
    </RequireAuth>
  );
}
