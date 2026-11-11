import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { bootstrapAdmin } from "../../api/admin.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function AdminLogin({ onToast }) {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [bootstrapToken, setBootstrapToken] = useState("");
  const [busy, setBusy] = useState(false);

  async function onLogin(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await login({ email: email.trim(), password });
      navigate("/admin");
    } catch (err) {
      onToast?.(err.message || "Connexion impossible.");
    } finally {
      setBusy(false);
    }
  }

  async function onBootstrap(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await bootstrapAdmin(username.trim(), bootstrapToken.trim());
      onToast?.("Compte promu admin. Activez le 2FA ensuite.");
    } catch (err) {
      onToast?.(err.message || "Bootstrap indisponible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-md px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">ADMIN-001</p>
      <h1 className="mt-2 text-3xl font-extrabold">Admin</h1>
      <p className="mt-2 text-sm text-accent">
        Espace séparé de la navigation publique. Le 2FA TOTP est obligatoire avant le tableau de
        bord.
      </p>
      <form className="card mt-6 space-y-3" onSubmit={onLogin}>
        <input
          className="field-input"
          type="email"
          required
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="field-input"
          type="password"
          required
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button className="btn-primary" type="submit" disabled={busy}>
          {busy ? "…" : "Continuer"}
        </button>
      </form>
      <form className="card mt-6 space-y-3" onSubmit={onBootstrap}>
        <h2 className="font-bold">Premier admin</h2>
        <p className="text-sm text-accent">
          Refuse si DOXAMI_ADMIN_BOOTSTRAP_TOKEN n’est pas défini, ou si un admin existe déjà.
        </p>
        <input
          className="field-input"
          required
          placeholder="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          className="field-input"
          required
          placeholder="Jeton bootstrap"
          value={bootstrapToken}
          onChange={(e) => setBootstrapToken(e.target.value)}
        />
        <button className="btn-secondary" type="submit" disabled={busy}>
          Promouvoir
        </button>
      </form>
      <Link to="/" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Accueil public
      </Link>
    </section>
  );
}
