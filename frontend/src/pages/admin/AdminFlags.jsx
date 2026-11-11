import { useEffect, useState } from "react";
import { listFlags, updateFlag } from "../../api/admin.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function AdminFlags({ onToast }) {
  const { token } = useAuth();
  const [flags, setFlags] = useState([]);

  async function reload() {
    setFlags(await listFlags(token));
  }

  useEffect(() => {
    reload().catch((err) => onToast?.(err.message || "Flags indisponibles."));
  }, [token]);

  async function toggle(flag) {
    try {
      await updateFlag(token, flag.key, !flag.enabled);
      await reload();
      onToast?.("Flag enregistré. Le checkout et les payouts restent fermés.");
    } catch (err) {
      onToast?.(err.message || "Mise à jour impossible.");
    }
  }

  return (
    <div>
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">ADMIN-005</p>
      <h1 className="mt-2 text-3xl font-extrabold">Feature flags</h1>
      <p className="mt-2 text-sm text-accent">
        Activer Premium ou Ads ne débite rien et n’ouvre pas le checkout.
      </p>
      <ul className="mt-6 space-y-2">
        {flags.map((flag) => (
          <li key={flag.key} className="card flex items-center justify-between gap-3">
            <div>
              <p className="font-semibold">{flag.key}</p>
              <p className="text-sm text-accent">{flag.note}</p>
            </div>
            <button className="btn-secondary" type="button" onClick={() => toggle(flag)}>
              {flag.enabled ? "Désactiver" : "Activer"}
            </button>
          </li>
        ))}
        {flags.length === 0 ? (
          <li className="card text-accent">
            Aucun flag en base. Les seeds arrivent avec la migration.
          </li>
        ) : null}
      </ul>
    </div>
  );
}
