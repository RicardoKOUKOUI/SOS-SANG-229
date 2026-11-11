import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { listFollowers, listFollowing } from "../../api/social.js";

export default function FollowList({ mode }) {
  const { username } = useParams();
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const title = mode === "followers" ? "Abonnés" : "Abonnements";
  const code = mode === "followers" ? "PROFILE-006" : "PROFILE-005";

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setError("");
      try {
        const data =
          mode === "followers"
            ? await listFollowers(username)
            : await listFollowing(username);
        if (!cancelled) setRows(data);
      } catch (err) {
        if (!cancelled) setError(err.message || "Liste indisponible.");
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [username, mode]);

  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">{code}</p>
      <h1 className="mt-2 text-3xl font-extrabold">
        {title} · @{username}
      </h1>
      {error ? <p className="mt-6 text-warn">{error}</p> : null}
      <ul className="mt-8 space-y-3">
        {rows.map((row) => (
          <li key={row.user.id}>
            <Link to={`/u/${row.user.username}`} className="card block hover:border-primary/40">
              <span className="font-semibold">{row.user.display_name}</span>
              <span className="mt-1 block text-sm text-accent">@{row.user.username}</span>
            </Link>
          </li>
        ))}
        {!error && rows.length === 0 ? (
          <li className="text-accent">Liste vide.</li>
        ) : null}
      </ul>
      <Link to={`/u/${username}`} className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Profil
      </Link>
    </section>
  );
}
