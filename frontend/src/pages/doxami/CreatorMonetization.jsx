import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getMonetizationStatus,
  listPremiumPlans,
  requestCheckout,
  requestPayout,
} from "../../api/creator.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function Inner({ onToast }) {
  const { token } = useAuth();
  const [status, setStatus] = useState(null);
  const [plans, setPlans] = useState([]);
  const [busy, setBusy] = useState("");

  useEffect(() => {
    getMonetizationStatus()
      .then(setStatus)
      .catch((err) => onToast?.(err.message || "Statut indisponible."));
    listPremiumPlans()
      .then(setPlans)
      .catch((err) => onToast?.(err.message || "Plans indisponibles."));
  }, [onToast]);

  async function onCheckout() {
    setBusy("checkout");
    try {
      await requestCheckout(token);
    } catch (err) {
      onToast?.(err.message || "Checkout indisponible.");
    } finally {
      setBusy("");
    }
  }

  async function onPayout() {
    setBusy("payout");
    try {
      await requestPayout(token);
    } catch (err) {
      onToast?.(err.message || "Payout indisponible.");
    } finally {
      setBusy("");
    }
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">CRE-002</p>
      <h1 className="mt-2 text-3xl font-extrabold">Ads & Premium</h1>
      <p className="mt-2 text-accent">
        Flags et catalogue seulement. Aucun paiement ni virement n’est exécuté.
      </p>

      {status ? (
        <div className="card mt-6 space-y-2">
          <p>Ads flag : {status.ads_enabled ? "on" : "off"}</p>
          <p>Premium flag : {status.premium_enabled ? "on" : "off"}</p>
          <p>
            Solde affiché : {status.earnings_minor} {status.currency} (registre vide)
          </p>
          <p className="text-sm text-accent">{status.reason}</p>
        </div>
      ) : null}

      <ul className="mt-6 space-y-3">
        {plans.map((plan) => (
          <li key={plan.code} className="card">
            <p className="font-semibold">{plan.name}</p>
            <p className="mt-1 text-sm text-accent">{plan.note}</p>
            <p className="mt-1 text-sm">
              Checkout : {plan.checkout_available ? "ouvert" : "fermé"}
            </p>
          </li>
        ))}
      </ul>

      <div className="mt-6 flex flex-wrap gap-3">
        <button className="btn-primary" type="button" disabled={busy !== ""} onClick={onCheckout}>
          {busy === "checkout" ? "…" : "Tenter un checkout"}
        </button>
        <button className="btn-secondary" type="button" disabled={busy !== ""} onClick={onPayout}>
          {busy === "payout" ? "…" : "Demander un payout"}
        </button>
      </div>

      <Link to="/hub/creator" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Studio
      </Link>
    </section>
  );
}

export default function CreatorMonetization({ onToast }) {
  return (
    <RequireAuth>
      <Inner onToast={onToast} />
    </RequireAuth>
  );
}
