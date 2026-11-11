import { Link } from "react-router-dom";

export default function PostCard({ post, onToggleLike, likeBusy }) {
  return (
    <article className="card space-y-3">
      <header className="flex items-baseline justify-between gap-3">
        <div>
          <Link
            to={`/u/${post.author.username}`}
            className="font-display font-bold text-secondary hover:text-primary"
          >
            {post.author.display_name}
          </Link>
          <p className="text-sm text-accent">@{post.author.username}</p>
        </div>
        <Link to={`/posts/${post.id}`} className="text-xs font-semibold text-primary">
          Ouvrir
        </Link>
      </header>
      <p className="whitespace-pre-wrap text-base leading-relaxed text-secondary">{post.body}</p>
      <footer className="flex flex-wrap items-center gap-4 text-sm text-accent">
        <button
          type="button"
          className={`font-semibold ${post.liked_by_me ? "text-primary" : "text-accent"}`}
          disabled={likeBusy}
          onClick={() => onToggleLike?.(post)}
        >
          {post.liked_by_me ? "Aimé" : "Aimer"} · {post.like_count}
        </button>
        <Link to={`/posts/${post.id}`} className="font-semibold hover:text-primary">
          Commentaires · {post.comment_count}
        </Link>
      </footer>
    </article>
  );
}
