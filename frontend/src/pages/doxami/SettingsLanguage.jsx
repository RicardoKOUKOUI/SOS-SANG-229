import { Link } from "react-router-dom";
import RequireAuth from "../../components/RequireAuth.jsx";

function Inner() {
  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Langue</h1>
      <p className="mt-2 text-accent">SETTINGS-007</p>
      <div className="card mt-8">
        <p>Interface : Français. Sélecteur multi-langue prévu plus tard.</p>
      </div>
      <Link to="/settings" className="mt-6 inline-block text-sm font-semibold text-primary">
        ← Paramètres
      </Link>
    </section>
  );
}

export default function SettingsLanguage() {
  return (
    <RequireAuth>
      <Inner />
    </RequireAuth>
  );
}
