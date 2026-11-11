import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createListing, listMarket } from "../../api/listings.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function MarketHub({ onToast }) {
  const { token, isAuthenticated } = useAuth();
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ title: "", description: "", price_minor: "" });
  const [busy, setBusy] = useState(false);

  async function reload() {
    setItems(await listMarket());
  }

  useEffect(() => {
    reload().catch((err) => onToast?.(err.message || "Annonces indisponibles."));
  }, [onToast]);

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await createListing(token, {
        title: form.title.trim(),
        description: form.description.trim() || null,
        price_minor: Number(form.price_minor || 0),
      });
      setForm({ title: "", description: "", price_minor: "" });
      await reload();
      onToast?.("Annonce publiée. Aucun paiement n’a été encaissé.");
    } catch (err) {
      onToast?.(err.message || "Publication impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">HUB-MARKET</p>
      <h1 className="mt-2 text-3xl font-extrabold">Marketplace</h1>
      <p className="mt-2 text-accent">
        Prix affiché seulement. Pay n’est pas actif : aucun achat n’est débité.
      </p>
      <ul className="mt-8 space-y-3">
        {items.map((item) => (
          <li key={item.id}>
            <Link to={`/hub/marketplace/${item.id}`} className="card block hover:border-primary/40">
              <p className="font-semibold">{item.title}</p>
              <p className="text-sm text-accent">
                {item.price_minor} {item.currency} · affichage · @{item.created_by.username}
              </p>
            </Link>
          </li>
        ))}
        {items.length === 0 ? <li className="card text-accent">Aucune annonce.</li> : null}
      </ul>
      {isAuthenticated ? (
        <form className="card mt-8 space-y-3" onSubmit={onSubmit}>
          <h2 className="font-bold">Publier une annonce</h2>
          <input
            className="field-input"
            required
            placeholder="Titre"
            value={form.title}
            onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
          />
          <input
            className="field-input"
            type="number"
            min="0"
            placeholder="Prix affiché (XOF)"
            value={form.price_minor}
            onChange={(e) => setForm((prev) => ({ ...prev, price_minor: e.target.value }))}
          />
          <textarea
            className="field-input min-h-24"
            placeholder="Description"
            value={form.description}
            onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
          />
          <button className="btn-primary" type="submit" disabled={busy}>
            {busy ? "…" : "Publier"}
          </button>
        </form>
      ) : null}
      <Link to="/hub" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Hub
      </Link>
    </section>
  );
}
