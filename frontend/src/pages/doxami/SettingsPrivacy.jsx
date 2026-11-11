import { Link } from "react-router-dom";
import RequireAuth from "../../components/RequireAuth.jsx";

function Inner() {
  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Confidentialité</h1>
      <p className="mt-2 text-accent">SETTINGS-002</p>
      <div className="card mt-8 space-y-3 text-accent">
        <p>Le profil public expose username, nom affiché et bio uniquement.</p>
        <p>Email et hash mot de passe ne sont jamais renvoyés sur `/users/{"{username}"}`.</p>
      </div>
      <Link to="/settings" className="mt-6 inline-block text-sm font-semibold text-primary">
        ← Paramètres
      </Link>
    </section>
  );
}

export default function SettingsPrivacy() {
  return (
    <RequireAuth>
      <Inner />
    </RequireAuth>
  );
}
