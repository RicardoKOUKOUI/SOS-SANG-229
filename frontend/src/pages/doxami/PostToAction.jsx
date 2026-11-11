import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { createFromPost } from "../../api/actions.js";
import { getPost } from "../../api/social.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function Inner({ onToast }) {
  const { postId } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getPost(postId, token)
      .then(setPost)
      .catch((err) => setError(err.message || "Post introuvable."));
  }, [postId, token]);

  async function onConvert() {
    setBusy(true);
    try {
      const project = await createFromPost(token, postId);
      onToast?.("Action créée depuis le post.");
      navigate(`/hub/actions/${project.id}`);
    } catch (err) {
      onToast?.(err.message || "Conversion impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">ACT-003</p>
      <h1 className="mt-2 text-3xl font-extrabold">Post → Action</h1>
      {error ? <p className="mt-4 text-warn">{error}</p> : null}
      {post ? (
        <div className="card mt-6">
          <p className="whitespace-pre-wrap">{post.body}</p>
          <button className="btn-primary mt-4" type="button" disabled={busy} onClick={onConvert}>
            {busy ? "…" : "Créer le projet"}
          </button>
        </div>
      ) : !error ? (
        <p className="mt-6 text-accent">Chargement…</p>
      ) : null}
      <Link
        to={`/posts/${postId}`}
        className="mt-8 inline-block text-sm font-semibold text-primary"
      >
        ← Post
      </Link>
    </section>
  );
}

export default function PostToAction({ onToast }) {
  return (
    <RequireAuth>
      <Inner onToast={onToast} />
    </RequireAuth>
  );
}
