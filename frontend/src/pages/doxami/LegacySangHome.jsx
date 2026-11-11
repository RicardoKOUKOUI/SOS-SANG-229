import { Link } from "react-router-dom";

export default function LegacySangHome() {
  return (
    <section className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-warn">LEGACY SOS</p>
      <h1 className="mt-2 text-3xl font-extrabold">SOS Sang 229</h1>
      <p className="mt-3 text-accent">
        Démo hackathon préservée. Routes déplacées sous <code>/legacy/sang</code> pendant la
        transition DOXAMI (Option A).
      </p>
      <ul className="mt-8 space-y-3">
        <li>
          <Link className="btn-primary w-full sm:w-auto" to="/legacy/sang/donneur/inscription">
            Inscription donneur
          </Link>
        </li>
        <li>
          <Link className="btn-secondary w-full sm:w-auto" to="/legacy/sang/alerte">
            Alerte urgence
          </Link>
        </li>
        <li>
          <Link className="btn-secondary w-full sm:w-auto" to="/legacy/sang/suivi">
            Suivi des demandes
          </Link>
        </li>
      </ul>
      <Link to="/" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Retour DOXAMI
      </Link>
    </section>
  );
}
