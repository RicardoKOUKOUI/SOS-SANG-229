import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../../auth/AuthContext.jsx";

export default function Register({ onToast }) {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    username: "",
    display_name: "",
    password: "",
  });
  const [busy, setBusy] = useState(false);

  function update(field) {
    return (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));
  }

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await register({
        email: form.email.trim(),
        username: form.username.trim(),
        display_name: form.display_name.trim(),
        password: form.password,
      });
      onToast?.("Compte créé — bienvenue sur DOXAMI.");
      navigate("/profile");
    } catch (err) {
      onToast?.(err.message || "Inscription impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Inscription</h1>
      <p className="mt-2 text-accent">AUTH-002 · email + mot de passe (JWT réel).</p>
      <form className="mt-8 space-y-4" onSubmit={onSubmit}>
        <label className="block space-y-1.5">
          <span className="field-label">Nom affiché</span>
          <input className="field-input" required value={form.display_name} onChange={update("display_name")} />
        </label>
        <label className="block space-y-1.5">
          <span className="field-label">Nom d’utilisateur</span>
          <input
            className="field-input"
            required
            pattern="[a-z0-9_]{3,32}"
            title="3–32 caractères : a-z, 0-9, _"
            value={form.username}
            onChange={update("username")}
          />
        </label>
        <label className="block space-y-1.5">
          <span className="field-label">Email</span>
          <input className="field-input" type="email" required value={form.email} onChange={update("email")} />
        </label>
        <label className="block space-y-1.5">
          <span className="field-label">Mot de passe</span>
          <input
            className="field-input"
            type="password"
            required
            minLength={8}
            value={form.password}
            onChange={update("password")}
          />
        </label>
        <button className="btn-primary w-full" type="submit" disabled={busy}>
          {busy ? "Création…" : "Créer mon compte"}
        </button>
      </form>
      <p className="mt-6 text-sm text-accent">
        Déjà un compte ?{" "}
        <Link to="/auth/login" className="font-semibold text-primary">
          Connexion
        </Link>
      </p>
    </section>
  );
}
