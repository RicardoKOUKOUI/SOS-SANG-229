import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  createComment,
  getPost,
  likePost,
  listComments,
  unlikePost,
} from "../../api/social.js";
import { useAuth } from "../../auth/AuthContext.jsx";
import PostCard from "../../components/PostCard.jsx";

export default function PostDetail({ onToast }) {
  const { postId } = useParams();
  const { token, isAuthenticated } = useAuth();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [body, setBody] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function reload() {
    const [postData, commentData] = await Promise.all([
      getPost(postId, token),
      listComments(postId),
    ]);
    setPost(postData);
    setComments(commentData);
  }

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setError("");
      try {
        const [postData, commentData] = await Promise.all([
          getPost(postId, token),
          listComments(postId),
        ]);
        if (!cancelled) {
          setPost(postData);
          setComments(commentData);
        }
      } catch (err) {
        if (!cancelled) setError(err.message || "Publication introuvable.");
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [postId, token]);

  async function onToggleLike(current) {
    if (!token) {
      onToast?.("Connectez-vous pour aimer.");
      return;
    }
    try {
      if (current.liked_by_me) await unlikePost(token, current.id);
      else await likePost(token, current.id);
      await reload();
    } catch (err) {
      onToast?.(err.message || "Like impossible.");
    }
  }

  async function onComment(event) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      await createComment(token, postId, body);
      setBody("");
      await reload();
      onToast?.("Commentaire publié.");
    } catch (err) {
      onToast?.(err.message || "Commentaire impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">POST-001</p>
      {error ? <p className="mt-6 text-warn">{error}</p> : null}
      {post ? (
        <div className="mt-6 space-y-6">
          <PostCard post={post} onToggleLike={onToggleLike} />
          {isAuthenticated ? (
            <Link
              to={`/posts/${post.id}/to-action`}
              className="inline-flex text-sm font-semibold text-primary"
            >
              ACT-003 · Transformer en action →
            </Link>
          ) : null}
          <div>
            <h2 className="text-xl font-bold">Commentaires · POST-002</h2>
            <ul className="mt-4 space-y-3">
              {comments.map((comment) => (
                <li key={comment.id} className="rounded-xl border border-light bg-white px-4 py-3">
                  <Link
                    to={`/u/${comment.author.username}`}
                    className="font-semibold text-primary"
                  >
                    @{comment.author.username}
                  </Link>
                  <p className="mt-1 whitespace-pre-wrap">{comment.body}</p>
                </li>
              ))}
              {comments.length === 0 ? (
                <li className="text-accent">Aucun commentaire pour l’instant.</li>
              ) : null}
            </ul>
            {isAuthenticated ? (
              <form className="mt-4 space-y-3" onSubmit={onComment}>
                <textarea
                  className="field-input min-h-24"
                  required
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  placeholder="Écrire un commentaire…"
                />
                <button className="btn-primary" type="submit" disabled={busy}>
                  {busy ? "Envoi…" : "Commenter"}
                </button>
              </form>
            ) : (
              <p className="mt-4 text-sm text-accent">
                <Link to="/auth/login" className="font-semibold text-primary">
                  Connectez-vous
                </Link>{" "}
                pour commenter.
              </p>
            )}
          </div>
        </div>
      ) : null}
      <Link to="/" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Accueil
      </Link>
    </section>
  );
}
