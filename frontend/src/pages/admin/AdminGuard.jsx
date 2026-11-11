import { useCallback, useEffect, useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { confirmMfa, enrollMfa, getAdminDashboard, verifyMfa } from "../../api/admin.js";
import { useAuth } from "../../auth/AuthContext.jsx";

const links = [
  { to: "/admin", label: "Tableau", end: true },
  { to: "/admin/users", label: "Users" },
  { to: "/admin/moderation", label: "Modération" },
  { to: "/admin/flags", label: "Flags" },
  { to: "/admin/logs", label: "Journal" },
];

export default function AdminGuard({ onToast }) {
  const { token, isAuthenticated, loading, applyToken } = useAuth();
  const [state, setState] = useState("loading");
  const [enrolled, setEnrolled] = useState(null);
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);

  const check = useCallback(async () => {
    if (!token) {
      setState("login");
      return;
    }
    try {
      await getAdminDashboard(token);
      setState("ready");
    } catch (err) {
      if (err.status === 403 && String(err.message).includes("2FA")) setState("mfa");
      else if (err.status === 403) setState("forbidden");
      else if (err.status === 401) setState("login");
      else {
        setState("error");
        onToast?.(err.message || "Admin indisponible.");
      }
    }
  }, [token, onToast]);

  useEffect(() => {
    if (loading) return;
    check();
  }, [loading, check]);

  async function onEnroll() {
    setBusy(true);
    try {
      setEnrolled(await enrollMfa(token));
    } catch (err) {
      if (err.status === 409) setEnrolled({ already: true });
      else onToast?.(err.message || "Enrôlement impossible.");
    } finally {
      setBusy(false);
    }
  }

  async function onCode(event) {
    event.preventDefault();
    setBusy(true);
    try {
      const result =
        enrolled && !enrolled.already
          ? await confirmMfa(token, code.trim())
          : await verifyMfa(token, code.trim());
      applyToken(result.access_token);
      setCode("");
      setState("ready");
    } catch (err) {
      onToast?.(err.message || "Code refusé.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">DOXAMI ADMIN</p>
      <nav className="mt-4 flex flex-wrap gap-2">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              `rounded-lg px-3 py-1.5 text-sm font-semibold ${
                isActive ? "bg-primary text-white" : "bg-light text-secondary"
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>

      {loading || state === "loading" ? <p className="mt-6 text-accent">Chargement…</p> : null}
      {state === "login" ? (
        <p className="card mt-6">
          <Link to="/admin/login" className="font-semibold text-primary">
            Connectez-vous
          </Link>{" "}
          avec un compte admin.
        </p>
      ) : null}
      {state === "forbidden" ? (
        <p className="card mt-6 text-accent">Ce compte n’a pas le rôle admin.</p>
      ) : null}
      {state === "mfa" ? (
        <div className="card mt-6 space-y-3">
          <h2 className="font-bold">2FA requis</h2>
          <p className="text-sm text-accent">
            Code TOTP à 6 chiffres. Aucun contournement : le tableau de bord reste fermé sans code
            valide.
          </p>
          <button className="btn-secondary" type="button" disabled={busy} onClick={onEnroll}>
            {enrolled?.already ? "Déjà activé" : "Générer un secret"}
          </button>
          {enrolled?.secret ? (
            <div className="space-y-1 text-sm">
              <p className="font-semibold">Secret (à enregistrer dans une app TOTP)</p>
              <p className="break-all font-mono">{enrolled.secret}</p>
              <p className="break-all text-accent">{enrolled.otpauth_uri}</p>
            </div>
          ) : null}
          <form className="flex gap-2" onSubmit={onCode}>
            <input
              className="field-input"
              inputMode="numeric"
              pattern="[0-9]{6}"
              required
              placeholder="000000"
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
            <button className="btn-primary" type="submit" disabled={busy || !isAuthenticated}>
              Valider
            </button>
          </form>
        </div>
      ) : null}
      {state === "ready" ? (
        <div className="mt-6">
          <Outlet />
        </div>
      ) : null}
      <Link to="/" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Accueil public
      </Link>
    </section>
  );
}
