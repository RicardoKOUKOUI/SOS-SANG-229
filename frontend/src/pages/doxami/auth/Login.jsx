import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../../auth/AuthContext.jsx";

export default function Login({ onToast }) {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await login({ email: email.trim(), password });
      onToast?.("Connexion réussie.");
      navigate(location.state?.from || "/");
    } catch (err) {
      onToast?.(err.message || "Connexion impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Connexion</h1>
      <p className="mt-2 text-accent">AUTH-003 · session JWT côté client.</p>
      <form className="mt-8 space-y-4" onSubmit={onSubmit}>
        <label className="block space-y-1.5">
          <span className="field-label">Email</span>
          <input className="field-input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="block space-y-1.5">
          <span className="field-label">Mot de passe</span>
          <input
            className="field-input"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        <button className="btn-primary w-full" type="submit" disabled={busy}>
          {busy ? "Connexion…" : "Se connecter"}
        </button>
      </form>
      <p className="mt-4 text-sm">
        <Link to="/auth/forgot" className="font-semibold text-primary">
          Mot de passe oublié
        </Link>
      </p>
      <p className="mt-6 text-sm text-accent">
        Pas encore de compte ?{" "}
        <Link to="/auth/register" className="font-semibold text-primary">
          Inscription
        </Link>
      </p>
    </section>
  );
}
