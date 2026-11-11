import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useParams } from "react-router-dom";
import { getProject } from "../../api/actions.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function Inner() {
  const { actionId } = useParams();
  const { token } = useAuth();
  const [project, setProject] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    getProject(token, actionId)
      .then((data) => {
        if (!cancelled) setProject(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Projet introuvable.");
      });
    return () => {
      cancelled = true;
    };
  }, [token, actionId]);

  const tabs = [
    { to: `/hub/actions/${actionId}`, end: true, label: "Aperçu" },
    { to: `/hub/actions/${actionId}/board`, label: "Kanban" },
    { to: `/hub/actions/${actionId}/tasks`, label: "Tasks" },
    { to: `/hub/actions/${actionId}/team`, label: "Équipe" },
    { to: `/hub/actions/${actionId}/progress`, label: "Progression" },
  ];

  return (
    <section className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">ACT-004</p>
      {error ? <p className="mt-4 text-warn">{error}</p> : null}
      {project ? (
        <>
          <h1 className="mt-2 text-3xl font-extrabold">{project.title}</h1>
          {project.description ? (
            <p className="mt-2 text-accent whitespace-pre-wrap">{project.description}</p>
          ) : null}
          <p className="mt-2 text-sm font-semibold text-primary">
            {project.progress_percent}% · {project.task_done}/{project.task_total}
          </p>
          {project.source_post_id ? (
            <Link
              to={`/posts/${project.source_post_id}`}
              className="mt-2 inline-block text-sm text-primary"
            >
              Issu d’un post →
            </Link>
          ) : null}
        </>
      ) : !error ? (
        <p className="mt-4 text-accent">Chargement…</p>
      ) : null}

      <nav className="mt-6 flex flex-wrap gap-2 border-b border-light pb-3">
        {tabs.map((tab) => (
          <NavLink
            key={tab.to}
            to={tab.to}
            end={tab.end}
            className={({ isActive }) =>
              `rounded-lg px-3 py-1.5 text-sm font-semibold ${
                isActive ? "bg-primary text-white" : "bg-light text-secondary"
              }`
            }
          >
            {tab.label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-6">
        <Outlet context={{ project, setProject, actionId }} />
      </div>

      <Link to="/hub/actions" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Actions
      </Link>
    </section>
  );
}

export default function ActionDetail() {
  return (
    <RequireAuth>
      <Inner />
    </RequireAuth>
  );
}
