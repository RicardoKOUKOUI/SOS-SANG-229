import { useEffect, useState } from "react";
import { listAuditLogs } from "../../api/admin.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function AdminLogs() {
  const { token } = useAuth();
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    listAuditLogs(token)
      .then(setLogs)
      .catch((err) => setError(err.message || "Journal indisponible."));
  }, [token]);

  return (
    <div>
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">ADMIN-006</p>
      <h1 className="mt-2 text-3xl font-extrabold">Journal</h1>
      <p className="mt-2 text-sm text-accent">Actions et identifiants. Pas d’email, de téléphone, ni de secret.</p>
      {error ? <p className="mt-4 text-warn">{error}</p> : null}
      <ul className="mt-6 space-y-2">
        {logs.map((row) => (
          <li key={row.id} className="card text-sm">
            <p className="font-semibold">{row.action}</p>
            <p className="text-accent">
              @{row.actor_username}
              {row.target_type ? ` · ${row.target_type}` : ""}
              {row.target_id ? ` · ${row.target_id}` : ""}
            </p>
          </li>
        ))}
        {!error && logs.length === 0 ? <li className="text-accent">Aucune entrée.</li> : null}
      </ul>
    </div>
  );
}
