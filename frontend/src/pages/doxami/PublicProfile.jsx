import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchPublicProfile } from "../../api/auth.js";
import { followUser, listFollowers, unfollowUser } from "../../api/social.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function PublicProfile({ onToast }) {
  const { username } = useParams();
  const { token, user, isAuthenticated } = useAuth();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");
  const [isFollowing, setIsFollowing] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setError("");
      setProfile(null);
      try {
        const data = await fetchPublicProfile(username);
        if (cancelled) return;
        setProfile(data);
        if (isAuthenticated && user?.username !== username.toLowerCase()) {
          const followers = await listFollowers(username);
          if (!cancelled) {
            setIsFollowing(
              followers.some((row) => row.user.username === user.username),
            );
          }
        } else if (!cancelled) {
          setIsFollowing(false);
        }
      } catch (err) {
        if (!cancelled) setError(err.message || "Profil introuvable.");
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [username, isAuthenticated, user?.username]);

  async function toggleFollow() {
    if (!token) {
      onToast?.("Connectez-vous pour suivre.");
      return;
    }
    setBusy(true);
    try {
      if (isFollowing) {
        await unfollowUser(token, username);
        setIsFollowing(false);
        onToast?.("Abonnement retiré.");
      } else {
        await followUser(token, username);
        setIsFollowing(true);
        onToast?.("Abonnement ajouté.");
      }
    } catch (err) {
      onToast?.(err.message || "Action follow impossible.");
    } finally {
      setBusy(false);
    }
  }

  const isSelf = user?.username === username?.toLowerCase();

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
          <div className="mt-6 flex flex-wrap gap-3">
            <Link to={`/u/${username}/followers`} className="btn-secondary">
              Abonnés
            </Link>
            <Link to={`/u/${username}/following`} className="btn-secondary">
              Abonnements
            </Link>
            {!isSelf && isAuthenticated ? (
              <button
                type="button"
                className="btn-primary"
                disabled={busy}
                onClick={toggleFollow}
              >
                {isFollowing ? "Ne plus suivre" : "Suivre"}
              </button>
            ) : null}
          </div>
        </div>
      ) : null}
      <Link to="/" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Accueil
      </Link>
    </section>
  );
}
