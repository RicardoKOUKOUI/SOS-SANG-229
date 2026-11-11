import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createProject } from "../../api/actions.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function Inner({ onToast }) {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      const project = await createProject(token, {
        title: title.trim(),
        description: description.trim() || null,
      });
      onToast?.("Projet créé.");
      navigate(`/hub/actions/${project.id}`);
    } catch (err) {
      onToast?.(err.message || "Création impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">ACT-002</p>
      <h1 className="mt-2 text-3xl font-extrabold">Créer une action</h1>
      <form className="mt-8 space-y-3" onSubmit={onSubmit}>
        <input
          className="field-input"
          required
          placeholder="Titre du projet"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <textarea
          className="field-input min-h-28"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button className="btn-primary" type="submit" disabled={busy}>
          {busy ? "…" : "Créer"}
        </button>
      </form>
      <Link to="/hub/actions" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Liste
      </Link>
    </section>
  );
}

export default function ActionsNew({ onToast }) {
  return (
    <RequireAuth>
      <Inner onToast={onToast} />
    </RequireAuth>
  );
}
