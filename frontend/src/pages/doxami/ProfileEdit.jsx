import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { updateMyProfile } from "../../api/auth.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function ProfileEditInner({ onToast }) {
  const { token, user, setUser } = useAuth();
  const navigate = useNavigate();
  const [displayName, setDisplayName] = useState(user.display_name || "");
  const [bio, setBio] = useState(user.bio || "");
  const [busy, setBusy] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      const updated = await updateMyProfile(token, {
        display_name: displayName.trim(),
        bio: bio.trim() || null,
      });
      setUser(updated);
      onToast?.("Profil mis à jour.");
      navigate("/profile");
    } catch (err) {
      onToast?.(err.message || "Mise à jour impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Éditer le profil</h1>
      <p className="mt-2 text-accent">PROFILE-002</p>
      <form className="mt-8 space-y-4" onSubmit={onSubmit}>
        <label className="block space-y-1.5">
          <span className="field-label">Nom affiché</span>
          <input className="field-input" required value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
        </label>
        <label className="block space-y-1.5">
          <span className="field-label">Bio</span>
          <textarea className="field-input min-h-28" value={bio} onChange={(e) => setBio(e.target.value)} />
        </label>
        <button className="btn-primary w-full" type="submit" disabled={busy}>
          {busy ? "Enregistrement…" : "Enregistrer"}
        </button>
      </form>
      <Link to="/profile" className="mt-4 inline-block text-sm font-semibold text-primary">
        Annuler
      </Link>
    </section>
  );
}

export default function ProfileEdit({ onToast }) {
  return (
    <RequireAuth>
      <ProfileEditInner onToast={onToast} />
    </RequireAuth>
  );
}
