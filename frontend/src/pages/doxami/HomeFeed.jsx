import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { listPosts, likePost, unlikePost } from "../../api/social.js";
import { useAuth } from "../../auth/AuthContext.jsx";
import PostCard from "../../components/PostCard.jsx";

export default function HomeFeed({ onToast }) {
  const { isAuthenticated, user, token } = useAuth();
  const [params, setParams] = useSearchParams();
  const tab = params.get("tab") === "following" ? "following" : "recent";
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [likeBusy, setLikeBusy] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        if (tab === "following" && !token) {
          setPosts([]);
          setError("Connectez-vous pour le feed Abonnements.");
          return;
        }
        const data = await listPosts(tab, token);
        if (!cancelled) setPosts(data);
      } catch (err) {
        if (!cancelled) {
          setPosts([]);
          setError(err.message || "Impossible de charger le feed.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [tab, token]);

  async function onToggleLike(post) {
    if (!token) {
      onToast?.("Connectez-vous pour aimer une publication.");
      return;
    }
    setLikeBusy(post.id);
    try {
      if (post.liked_by_me) await unlikePost(token, post.id);
      else await likePost(token, post.id);
      setPosts((prev) =>
        prev.map((item) =>
          item.id === post.id
            ? {
                ...item,
                liked_by_me: !item.liked_by_me,
                like_count: item.like_count + (item.liked_by_me ? -1 : 1),
              }
            : item,
        ),
      );
    } catch (err) {
      onToast?.(err.message || "Action like impossible.");
    } finally {
      setLikeBusy("");
    }
  }

  return (
    <section className="bg-mesh min-h-[70vh]">
      <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6 lg:px-8">
        <p className="font-display text-sm font-semibold uppercase tracking-[0.2em] text-primary">
          DOXAMI · HOME-001
        </p>
        <h1 className="mt-3 text-4xl font-extrabold text-secondary">Accueil</h1>
        <p className="mt-3 text-accent">
          Feed texte réel. Médias non activés (pas de faux upload).
        </p>

        <div className="mt-6 flex flex-wrap gap-2">
          <button
            type="button"
            className={tab === "recent" ? "btn-primary" : "btn-secondary"}
            onClick={() => setParams({})}
          >
            Récent
          </button>
          <button
            type="button"
            className={tab === "following" ? "btn-primary" : "btn-secondary"}
            onClick={() => setParams({ tab: "following" })}
          >
            Abonnements
          </button>
          {isAuthenticated ? (
            <Link to="/create" className="btn-secondary">
              Créer
            </Link>
          ) : (
            <Link to="/auth/register" className="btn-secondary">
              Créer un compte
            </Link>
          )}
        </div>

        {isAuthenticated ? (
          <p className="mt-4 text-sm text-accent">Connecté · @{user?.username}</p>
        ) : null}

        <div className="mt-8 space-y-4">
          {loading ? <p className="text-accent">Chargement du feed…</p> : null}
          {error ? <p className="text-warn">{error}</p> : null}
          {!loading && !error && posts.length === 0 ? (
            <div className="card">
              <h2 className="text-xl font-bold">HOME-004 · Feed vide</h2>
              <p className="mt-2 text-accent">
                Aucune publication.{" "}
                {isAuthenticated ? (
                  <Link to="/create" className="font-semibold text-primary">
                    Écrire la première
                  </Link>
                ) : (
                  <Link to="/auth/login" className="font-semibold text-primary">
                    Se connecter
                  </Link>
                )}
              </p>
            </div>
          ) : null}
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              likeBusy={likeBusy === post.id}
              onToggleLike={onToggleLike}
            />
          ))}
        </div>

        <Link
          to="/legacy/sang"
          className="mt-10 inline-block text-sm font-semibold text-primary underline-offset-4 hover:underline"
        >
          Legacy SOS Sang 229 →
        </Link>
      </div>
    </section>
  );
}
