import { Link } from "react-router-dom";

const tiles = [
  { to: "/hub/music", label: "Music", status: "non activé" },
  { to: "/hub/meet", label: "Meet", status: "non activé" },
  { to: "/hub/pay", label: "Pay", status: "non activé" },
  { to: "/hub/watch", label: "Watch", status: "non activé" },
  { to: "/hub/live", label: "Live", status: "non activé" },
  { to: "/hub/games", label: "Games", status: "non activé" },
  { to: "/hub/ai", label: "AI", status: "non activé" },
  { to: "/hub/marketplace", label: "Marketplace", status: "non activé" },
  { to: "/hub/events", label: "Events", status: "non activé" },
  { to: "/hub/work", label: "Work", status: "non activé" },
  { to: "/hub/creator", label: "Creator Studio", status: "non activé" },
  { to: "/hub/professional", label: "Professional", status: "non activé" },
  { to: "/hub/mesh", label: "MESH", status: "non activé" },
  { to: "/hub/actions", label: "Actions", status: "non activé" },
];

export default function Hub() {
  return (
    <section className="bg-mesh min-h-[70vh]">
      <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">HUB-001</p>
        <h1 className="mt-2 text-4xl font-extrabold">DOXAMI Hub</h1>
        <p className="mt-3 max-w-2xl text-accent">
          Tuiles prêtes à brancher. Chaque module affiche un état honnête tant que le service
          n’est pas configuré.
        </p>
        <ul className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {tiles.map((tile) => (
            <li key={tile.to}>
              <Link
                to={tile.to}
                className="block rounded-2xl border border-light bg-white/90 px-4 py-5 shadow-soft transition hover:border-primary/40"
              >
                <span className="font-display text-lg font-bold">{tile.label}</span>
                <span className="mt-2 block text-sm text-accent">{tile.status}</span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
