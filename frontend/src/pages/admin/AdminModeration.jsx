import { useEffect, useState } from "react";
import { hidePost, listModerationPosts, restorePost } from "../../api/admin.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function AdminModeration({ onToast }) {
  const { token } = useAuth();
  const [posts, setPosts] = useState([]);

  async function reload() {
    setPosts(await listModerationPosts(token));
  }

  useEffect(() => {
    reload().catch((err) => onToast?.(err.message || "Modération indisponible."));
  }, [token]);

  async function toggle(post) {
    try {
      if (post.hidden) await restorePost(token, post.id);
      else await hidePost(token, post.id);
      await reload();
    } catch (err) {
      onToast?.(err.message || "Action impossible.");
    }
  }

  return (
    <div>
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">ADMIN-004</p>
      <h1 className="mt-2 text-3xl font-extrabold">Modération</h1>
      <p className="mt-2 text-sm text-accent">
        Posts publics seulement. Les messages privés ne sont pas accessibles ici.
      </p>
      <ul className="mt-6 space-y-2">
        {posts.map((post) => (
          <li key={post.id} className="card">
            <p className="text-sm text-accent">@{post.author_username}</p>
            <p className="mt-1 whitespace-pre-wrap">{post.body}</p>
            <button className="btn-secondary mt-3" type="button" onClick={() => toggle(post)}>
              {post.hidden ? "Rétablir" : "Masquer"}
            </button>
          </li>
        ))}
        {posts.length === 0 ? <li className="text-accent">Aucun post.</li> : null}
      </ul>
    </div>
  );
}
