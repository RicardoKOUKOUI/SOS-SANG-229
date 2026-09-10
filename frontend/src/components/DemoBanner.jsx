export default function DemoBanner({ children }) {
  return (
    <aside className="rounded-2xl border border-primary/10 bg-primary/5 px-5 py-4 text-sm leading-6 text-secondary">
      <p className="font-bold text-primary">Information</p>
      <p className="mt-1 text-secondary/80">{children}</p>
    </aside>
  );
}
