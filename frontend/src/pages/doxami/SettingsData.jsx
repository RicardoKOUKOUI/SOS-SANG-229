import { Link } from "react-router-dom";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useOffline } from "../../offline/OfflineContext.jsx";

function Inner() {
  const { dataSaver, setDataSaver, pending, online, syncNow, syncing } = useOffline();

  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Données & offline</h1>
      <p className="mt-2 text-accent">SETTINGS-004</p>
      <div className="card mt-8 space-y-4">
        <label className="flex items-start gap-3">
          <input
            type="checkbox"
            className="mt-1"
            checked={dataSaver}
            onChange={(e) => setDataSaver(e.target.checked)}
          />
          <span>
            <span className="font-semibold">Mode économie de données</span>
            <p className="text-sm text-accent">
              Réduit le polling agressif côté UI (intervalles plus longs). Aucune image distante
              chargée pour l’instant (texte only).
            </p>
          </span>
        </label>
        <p className="text-sm text-accent">
          Réseau : {online ? "en ligne" : "hors ligne"} · file : {pending} ·{" "}
          {syncing ? "sync…" : "idle"}
        </p>
        <button type="button" className="btn-secondary" disabled={!online || syncing} onClick={() => syncNow()}>
          Forcer la synchronisation
        </button>
      </div>
      <Link to="/settings" className="mt-6 inline-block text-sm font-semibold text-primary">
        ← Paramètres
      </Link>
    </section>
  );
}

export default function SettingsData() {
  return (
    <RequireAuth>
      <Inner />
    </RequireAuth>
  );
}
