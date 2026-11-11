import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getJob } from "../../api/listings.js";

export default function WorkDetail() {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getJob(jobId)
      .then(setJob)
      .catch((err) => setError(err.message || "Offre introuvable."));
  }, [jobId]);

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">WORK-001</p>
      {error ? <p className="mt-4 text-warn">{error}</p> : null}
      {job ? (
        <div className="mt-4">
          <h1 className="text-3xl font-extrabold">{job.title}</h1>
          <p className="mt-2 text-sm text-accent">
            {job.city_label || "Lieu non précisé"} · @{job.created_by.username}
          </p>
          {job.description ? <p className="mt-4 whitespace-pre-wrap">{job.description}</p> : null}
        </div>
      ) : !error ? (
        <p className="mt-4 text-accent">Chargement…</p>
      ) : null}
      <Link to="/hub/work" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Offres
      </Link>
    </section>
  );
}
