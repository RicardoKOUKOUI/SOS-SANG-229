import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listProjects } from "../../api/actions.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function Inner() {
  const { token } = useAuth();
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    listProjects(token)
      .then((data) => {
        if (!cancelled) setProjects(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Actions indisponibles.");
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">ACT-001</p>
      <div className="mt-2 flex items-end justify-between gap-4">
        <h1 className="text-3xl font-extrabold">Actions</h1>
        <Link to="/hub/actions/new" className="btn-primary shrink-0 text-sm">
          Nouvelle
        </Link>
      </div>
      <p className="mt-2 text-accent">Idée → projet → tâches. Progression réelle (done / total).</p>
      {error ? <p className="mt-4 text-warn">{error}</p> : null}
      <ul className="mt-8 space-y-3">
        {projects.map((project) => (
          <li key={project.id}>
            <Link
              to={`/hub/actions/${project.id}`}
              className="card block transition hover:border-primary/40"
            >
              <p className="font-semibold">{project.title}</p>
              <p className="mt-1 text-sm text-accent">
                {project.progress_percent}% · {project.task_done}/{project.task_total} tâches
              </p>
            </Link>
          </li>
        ))}
        {!error && projects.length === 0 ? (
          <li className="card text-accent">Aucun projet. Créez-en un ou convertissez un post.</li>
        ) : null}
      </ul>
      <Link to="/hub" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Hub
      </Link>
    </section>
  );
}

export default function ActionsHome() {
  return (
    <RequireAuth>
      <Inner />
    </RequireAuth>
  );
}
