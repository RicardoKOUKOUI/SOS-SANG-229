import { Link } from "react-router-dom";

export default function PlaceholderModule({
  code,
  title,
  body = "Module non activé pour cette phase. Aucune action simulée.",
}) {
  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">{code}</p>
      <h1 className="mt-2 text-3xl font-extrabold">{title}</h1>
      <div className="card mt-8">
        <p className="text-accent">{body}</p>
        <Link to="/hub" className="btn-secondary mt-6 inline-flex">
          Retour Hub
        </Link>
      </div>
    </section>
  );
}
