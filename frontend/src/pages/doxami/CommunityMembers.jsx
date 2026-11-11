import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { listCommunityMembers } from "../../api/messaging.js";

export default function CommunityMembers() {
  const { communityId } = useParams();
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    listCommunityMembers(communityId)
      .then((data) => {
        if (!cancelled) setRows(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Membres indisponibles.");
      });
    return () => {
      cancelled = true;
    };
  }, [communityId]);

  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Membres</h1>
      <p className="mt-2 text-accent">COM-005</p>
      {error ? <p className="mt-6 text-warn">{error}</p> : null}
      <ul className="mt-8 space-y-3">
        {rows.map((row) => (
          <li key={row.user.id}>
            <Link to={`/u/${row.user.username}`} className="card block hover:border-primary/40">
              @{row.user.username} · {row.user.display_name}
            </Link>
          </li>
        ))}
      </ul>
      <Link
        to={`/communities/${communityId}`}
        className="mt-8 inline-block text-sm font-semibold text-primary"
      >
        ← Communauté
      </Link>
    </section>
  );
}
