import { useEffect, useState } from "react";
import { getAdminDashboard } from "../../api/admin.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function AdminDashboard() {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getAdminDashboard(token)
      .then(setData)
      .catch((err) => setError(err.message || "Tableau indisponible."));
  }, [token]);

  return (
    <div>
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">ADMIN-002</p>
      <h1 className="mt-2 text-3xl font-extrabold">Tableau de bord</h1>
      {error ? <p className="mt-4 text-warn">{error}</p> : null}
      {data ? (
        <ul className="mt-6 grid gap-3 sm:grid-cols-2">
          {[
            ["Comptes", data.users],
            ["Admins", data.admins],
            ["Posts", data.posts],
            ["Posts masqués", data.hidden_posts],
            ["Flags actifs", data.flags_enabled],
          ].map(([label, value]) => (
            <li key={label} className="card">
              <p className="text-sm text-accent">{label}</p>
              <p className="text-3xl font-extrabold">{value}</p>
            </li>
          ))}
        </ul>
      ) : !error ? (
        <p className="mt-4 text-accent">Chargement…</p>
      ) : null}
    </div>
  );
}
