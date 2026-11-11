import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchPublicProfile } from "../../api/auth.js";

export default function PublicProfile() {
  const { username } = useParams();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setError("");
      setProfile(null);
      try {
        const data = await fetchPublicProfile(username);
        if (!cancelled) setProfile(data);
      } catch (err) {
        if (!cancelled) setError(err.message || "Profil introuvable.");
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [username]);

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">PROFILE-003</p>
      {error ? <p className="mt-6 text-warn">{error}</p> : null}
      {!error && !profile ? <p className="mt-6 text-accent">Chargement…</p> : null}
      {profile ? (
        <div className="mt-4">
          <h1 className="text-3xl font-extrabold">{profile.display_name}</h1>
          <p className="mt-1 text-accent">@{profile.username}</p>
          <div className="card mt-6">
            <p>{profile.bio?.trim() ? profile.bio : "Aucune bio publique."}</p>
          </div>
        </div>
      ) : null}
      <Link to="/" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Accueil
      </Link>
    </section>
  );
}
