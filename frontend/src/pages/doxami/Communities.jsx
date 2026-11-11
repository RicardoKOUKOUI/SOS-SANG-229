import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listCommunities } from "../../api/messaging.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function Communities() {
  const { token } = useAuth();
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    listCommunities(token)
      .then((data) => {
        if (!cancelled) setRows(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Communautés indisponibles.");
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">COM-001</p>
      <div className="mt-2 flex flex-wrap items-end justify-between gap-3">
        <h1 className="text-3xl font-extrabold">Communities</h1>
        <Link to="/communities/new" className="btn-primary">
          Créer
        </Link>
      </div>
      {error ? <p className="mt-6 text-warn">{error}</p> : null}
      <ul className="mt-8 space-y-3">
        {rows.map((community) => (
          <li key={community.id}>
            <Link to={`/communities/${community.id}`} className="card block hover:border-primary/40">
              <span className="font-semibold">{community.name}</span>
              <p className="mt-1 text-sm text-accent">
                @{community.slug} · {community.member_count} membre(s)
              </p>
            </Link>
          </li>
        ))}
        {!error && rows.length === 0 ? (
          <li className="card text-accent">COM-008 · Aucune communauté publique.</li>
        ) : null}
      </ul>
    </section>
  );
}
