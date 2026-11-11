import { useEffect, useState } from "react";
import { listAdminUsers, setUserActive } from "../../api/admin.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function AdminUsers({ onToast }) {
  const { token } = useAuth();
  const [users, setUsers] = useState([]);

  async function reload() {
    setUsers(await listAdminUsers(token));
  }

  useEffect(() => {
    reload().catch((err) => onToast?.(err.message || "Utilisateurs indisponibles."));
  }, [token]);

  async function toggle(user) {
    try {
      await setUserActive(token, user.id, !user.is_active);
      await reload();
    } catch (err) {
      onToast?.(err.message || "Mise à jour impossible.");
    }
  }

  return (
    <div>
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">ADMIN-003</p>
      <h1 className="mt-2 text-3xl font-extrabold">Utilisateurs</h1>
      <p className="mt-2 text-sm text-accent">Identifiants publics seulement. Pas d’email ni de téléphone.</p>
      <ul className="mt-6 space-y-2">
        {users.map((user) => (
          <li key={user.id} className="card flex items-center justify-between gap-3">
            <div>
              <p className="font-semibold">
                {user.display_name} <span className="text-accent">@{user.username}</span>
              </p>
              <p className="text-xs uppercase text-accent">
                {user.role} · {user.is_active ? "actif" : "inactif"} · 2FA{" "}
                {user.totp_enabled ? "oui" : "non"}
              </p>
            </div>
            <button className="btn-secondary" type="button" onClick={() => toggle(user)}>
              {user.is_active ? "Désactiver" : "Réactiver"}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
