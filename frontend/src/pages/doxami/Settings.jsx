import { Link } from "react-router-dom";
import RequireAuth from "../../components/RequireAuth.jsx";

function SettingsInner() {
  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Paramètres</h1>
      <p className="mt-2 text-accent">SETTINGS-001</p>
      <ul className="mt-8 space-y-3">
        <li>
          <Link to="/settings/privacy" className="card block hover:border-primary/40">
            <span className="font-semibold">Confidentialité</span>
            <p className="mt-1 text-sm text-accent">Visibilité du profil (basique).</p>
          </Link>
        </li>
        <li>
          <Link to="/settings/language" className="card block hover:border-primary/40">
            <span className="font-semibold">Langue</span>
            <p className="mt-1 text-sm text-accent">Français (défaut Phase 2).</p>
          </Link>
        </li>
        <li>
          <Link to="/settings/data" className="card block hover:border-primary/40">
            <span className="font-semibold">Données & offline</span>
            <p className="mt-1 text-sm text-accent">Économie de données + sync IndexedDB.</p>
          </Link>
        </li>
        <li>
          <Link to="/profile/edit" className="card block hover:border-primary/40">
            <span className="font-semibold">Profil</span>
            <p className="mt-1 text-sm text-accent">Nom affiché et bio.</p>
          </Link>
        </li>
      </ul>
    </section>
  );
}

export default function Settings() {
  return (
    <RequireAuth>
      <SettingsInner />
    </RequireAuth>
  );
}
