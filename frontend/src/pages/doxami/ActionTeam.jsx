import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { addTeamMember, listTeam } from "../../api/actions.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function ActionTeam({ onToast }) {
  const { actionId } = useOutletContext();
  const { token } = useAuth();
  const [members, setMembers] = useState([]);
  const [username, setUsername] = useState("");
  const [busy, setBusy] = useState(false);

  async function reload() {
    setMembers(await listTeam(token, actionId));
  }

  useEffect(() => {
    reload().catch((err) => onToast?.(err.message || "Équipe indisponible."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, actionId]);

  async function onAdd(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await addTeamMember(token, actionId, username.trim());
      setUsername("");
      await reload();
      onToast?.("Membre ajouté.");
    } catch (err) {
      onToast?.(err.message || "Ajout impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <p className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-primary">
        ACT-007
      </p>
      <ul className="space-y-2">
        {members.map((member) => (
          <li key={member.id} className="card flex justify-between">
            <span className="font-semibold">
              {member.user.display_name}{" "}
              <span className="text-accent">@{member.user.username}</span>
            </span>
            <span className="text-sm uppercase text-accent">{member.role}</span>
          </li>
        ))}
      </ul>
      <form className="mt-4 flex gap-2" onSubmit={onAdd}>
        <input
          className="field-input flex-1"
          required
          placeholder="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <button className="btn-primary" type="submit" disabled={busy}>
          Ajouter
        </button>
      </form>
    </div>
  );
}
