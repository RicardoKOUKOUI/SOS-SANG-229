import { useState } from "react";
import { Link } from "react-router-dom";
import { exploreSearch } from "../../api/social.js";
import { useAuth } from "../../auth/AuthContext.jsx";
import PostCard from "../../components/PostCard.jsx";

export default function Explore({ onToast }) {
  const { token } = useAuth();
  const [q, setQ] = useState("");
  const [results, setResults] = useState(null);
  const [busy, setBusy] = useState(false);
  const [searched, setSearched] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    const query = q.trim();
    if (!query) return;
    setBusy(true);
    setSearched(true);
    try {
      const data = await exploreSearch(query, token);
      setResults(data);
    } catch (err) {
      setResults(null);
      onToast?.(err.message || "Recherche impossible.");
    } finally {
      setBusy(false);
    }
  }

  const empty =
    searched &&
    results &&
    results.people.length === 0 &&
    results.posts.length === 0;

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Explorer</h1>
      <p className="mt-2 text-accent">EXPLORE-001 · personnes et publications texte.</p>
      <form className="mt-8 flex flex-col gap-3 sm:flex-row" onSubmit={onSubmit}>
        <input
          className="field-input"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Rechercher…"
          required
        />
        <button className="btn-primary sm:w-40" type="submit" disabled={busy}>
          {busy ? "…" : "Chercher"}
        </button>
      </form>

      {empty ? (
        <div className="card mt-8">
          <h2 className="font-bold">EXPLORE-008 · Aucun résultat</h2>
          <p className="mt-2 text-accent">Essayez un autre terme.</p>
        </div>
      ) : null}

      {results?.people?.length ? (
        <div className="mt-8">
          <h2 className="text-xl font-bold">Personnes · EXPLORE-002</h2>
          <ul className="mt-3 space-y-2">
            {results.people.map((person) => (
              <li key={person.id}>
                <Link
                  to={`/u/${person.username}`}
                  className="card block hover:border-primary/40"
                >
                  <span className="font-semibold">{person.display_name}</span>
                  <span className="mt-1 block text-sm text-accent">@{person.username}</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {results?.posts?.length ? (
        <div className="mt-8 space-y-4">
          <h2 className="text-xl font-bold">Publications · EXPLORE-003</h2>
          {results.posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      ) : null}
    </section>
  );
}
