import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { checkoutListing, getListing } from "../../api/listings.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function MarketDetail({ onToast }) {
  const { listingId } = useParams();
  const { token, isAuthenticated } = useAuth();
  const [item, setItem] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getListing(listingId)
      .then(setItem)
      .catch((err) => setError(err.message || "Annonce introuvable."));
  }, [listingId]);

  async function onCheckout() {
    if (!isAuthenticated) {
      onToast?.("Connectez-vous pour tenter un achat.");
      return;
    }
    setBusy(true);
    try {
      await checkoutListing(token, listingId);
    } catch (err) {
      onToast?.(err.message || "Paiement indisponible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">MKT-001</p>
      {error ? <p className="mt-4 text-warn">{error}</p> : null}
      {item ? (
        <div className="mt-4">
          <h1 className="text-3xl font-extrabold">{item.title}</h1>
          <p className="mt-2 text-sm text-accent">
            {item.price_minor} {item.currency} affichés · checkout{" "}
            {item.checkout_available ? "ouvert" : "fermé"} · @{item.created_by.username}
          </p>
          {item.description ? (
            <p className="mt-4 whitespace-pre-wrap">{item.description}</p>
          ) : null}
          <button className="btn-primary mt-6" type="button" disabled={busy} onClick={onCheckout}>
            {busy ? "…" : "Tenter un achat"}
          </button>
        </div>
      ) : !error ? (
        <p className="mt-4 text-accent">Chargement…</p>
      ) : null}
      <Link to="/hub/marketplace" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Annonces
      </Link>
    </section>
  );
}
