import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCreatorMe, getMonetizationStatus, saveCreatorMe } from "../../api/creator.js";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function Inner({ onToast }) {
  const { token } = useAuth();
  const [status, setStatus] = useState(null);
  const [form, setForm] = useState({ pitch: "", focus: "", accepting_collabs: false });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getMonetizationStatus()
      .then(setStatus)
      .catch((err) => onToast?.(err.message || "Statut monétisation indisponible."));
    getCreatorMe(token)
      .then((profile) => {
        setForm({
          pitch: profile.pitch || "",
          focus: profile.focus || "",
          accepting_collabs: profile.accepting_collabs,
        });
      })
      .catch((err) => {
        if (err.status !== 404) onToast?.(err.message || "Profil créateur indisponible.");
      });
  }, [token, onToast]);

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await saveCreatorMe(token, {
        pitch: form.pitch.trim() || null,
        focus: form.focus.trim() || null,
        accepting_collabs: form.accepting_collabs,
      });
      onToast?.("Studio enregistré.");
    } catch (err) {
      onToast?.(err.message || "Enregistrement impossible.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">HUB-CREATOR</p>
      <h1 className="mt-2 text-3xl font-extrabold">Creator Studio</h1>
      <p className="mt-2 text-accent">
        Profil créateur réel. Aucun revenu simulé : le solde reste 0 tant qu’il n’y a pas de
        registre de revenus ni de prestataire de paiement.
      </p>

      <form className="card mt-8 space-y-3" onSubmit={onSubmit}>
        <h2 className="font-bold">Profil</h2>
        <input
          className="field-input"
          placeholder="Focus (ex. texte, communauté)"
          value={form.focus}
          onChange={(e) => setForm((prev) => ({ ...prev, focus: e.target.value }))}
        />
        <textarea
          className="field-input min-h-28"
          placeholder="Pitch"
          value={form.pitch}
          onChange={(e) => setForm((prev) => ({ ...prev, pitch: e.target.value }))}
        />
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={form.accepting_collabs}
            onChange={(e) =>
              setForm((prev) => ({ ...prev, accepting_collabs: e.target.checked }))
            }
          />
          Ouvert aux collaborations
        </label>
        <button className="btn-primary" type="submit" disabled={busy}>
          {busy ? "…" : "Enregistrer"}
        </button>
      </form>

      <div className="card mt-6 space-y-2">
        <h2 className="font-bold">Monétisation</h2>
        {status ? (
          <>
            <p className="text-sm">Ads : {status.ads_enabled ? "activées" : "désactivées"}</p>
            <p className="text-sm">
              Premium : {status.premium_enabled ? "flag on" : "désactivé"}
            </p>
            <p className="text-sm">PSP configuré : {status.psp_configured ? "oui" : "non"}</p>
            <p className="text-sm font-semibold">
              Payouts : {status.payouts_ready ? "prêts" : "indisponibles"} · solde{" "}
              {status.earnings_minor} {status.currency}
            </p>
            <p className="text-sm text-accent">{status.reason}</p>
          </>
        ) : (
          <p className="text-accent">Chargement…</p>
        )}
        <Link to="/hub/creator/monetization" className="inline-block text-sm font-semibold text-primary">
          Détail ads / premium / payout →
        </Link>
      </div>

      <Link to="/hub" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Hub
      </Link>
    </section>
  );
}

export default function CreatorHub({ onToast }) {
  return (
    <RequireAuth>
      <Inner onToast={onToast} />
    </RequireAuth>
  );
}
