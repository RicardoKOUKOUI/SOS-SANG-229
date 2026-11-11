import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getThread } from "../../api/messaging.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function InfoInner() {
  const { threadId } = useParams();
  const { token } = useAuth();
  const [thread, setThread] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    getThread(token, threadId)
      .then((data) => {
        if (!cancelled) setThread(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Infos indisponibles.");
      });
    return () => {
      cancelled = true;
    };
  }, [threadId, token]);

  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Infos conversation</h1>
      <p className="mt-2 text-accent">MSG-007</p>
      {error ? <p className="mt-6 text-warn">{error}</p> : null}
      {thread ? (
        <div className="card mt-8 space-y-3">
          <p>
            <span className="font-semibold">Type :</span> {thread.kind}
          </p>
          {thread.title ? (
            <p>
              <span className="font-semibold">Titre :</span> {thread.title}
            </p>
          ) : null}
          <div>
            <p className="font-semibold">Membres</p>
            <ul className="mt-2 space-y-1">
              {thread.members.map((member) => (
                <li key={member.id}>
                  <Link to={`/u/${member.username}`} className="text-primary">
                    @{member.username}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}
      <Link to={`/messages/${threadId}`} className="mt-6 inline-block text-sm font-semibold text-primary">
        ← Thread
      </Link>
    </section>
  );
}

export default function MessageInfo() {
  return (
    <RequireAuth>
      <InfoInner />
    </RequireAuth>
  );
}
