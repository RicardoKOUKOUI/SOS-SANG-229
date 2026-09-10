import { useState } from "react";
import BloodGroupSelect from "../components/BloodGroupSelect.jsx";
import PageFrame from "../components/PageFrame.jsx";
import PageHeader from "../components/PageHeader.jsx";
import { createDonor } from "../api/client.js";
import { DEMO_CITIES } from "../data/demo.js";

const INITIAL = {
  displayName: "",
  bloodGroup: "",
  phone: "",
  city: "",
  gpsConsent: false,
};

/** Normalize to 10 Benin digits starting with 01, or null if invalid. */
function normalizeBeninPhone(raw) {
  let digits = String(raw || "").replace(/\D/g, "");
  if (digits.startsWith("229") && digits.length === 13) {
    digits = digits.slice(3);
  }
  if (digits.length !== 10 || !digits.startsWith("01")) return null;
  return digits;
}

function readGpsIfConsented(consent) {
  if (!consent || !navigator.geolocation) {
    return Promise.resolve(null);
  }
  return new Promise((resolve) => {
    const timer = window.setTimeout(() => resolve(null), 4000);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        window.clearTimeout(timer);
        resolve({
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
        });
      },
      () => {
        window.clearTimeout(timer);
        resolve(null);
      },
      { enableHighAccuracy: false, maximumAge: 60_000, timeout: 3500 },
    );
  });
}

export default function DonorRegistration({ onToast }) {
  const [form, setForm] = useState(INITIAL);
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const phoneOk = normalizeBeninPhone(form.phone) !== null;
  const canSubmit = Boolean(
    form.bloodGroup && phoneOk && form.city && !submitting,
  );

  function update(field) {
    return (event) => {
      const value =
        event.target.type === "checkbox" ? event.target.checked : event.target.value;
      setForm((current) => ({ ...current, [field]: value }));
    };
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const phone = normalizeBeninPhone(form.phone);
    if (!form.bloodGroup || !phone || !form.city || submitting) return;

    setSubmitting(true);
    try {
      const location = await readGpsIfConsented(form.gpsConsent);
      const payload = {
        display_name: form.displayName.trim() || "Donneur",
        blood_group: form.bloodGroup,
        phone,
        city: form.city,
      };
      if (location) payload.location = location;

      const created = await createDonor(payload);
      setSubmitted(true);
      onToast(
        `Donneur enregistré : ${created.display_name} (${created.blood_group}) · ${created.city}`,
      );
      setForm(INITIAL);
    } catch (err) {
      onToast(err?.message || "Échec de l'inscription donneur.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <PageFrame>
      <div className="space-y-8">
        <PageHeader kicker="Volontaire" title="Inscription" highlight="donneur">
          Rejoignez le réseau SOS Sang 229. Votre profil sert au matching en
          cas d’urgence transfusionnelle près de chez vous.
        </PageHeader>

        <form className="card space-y-6" onSubmit={handleSubmit} autoComplete="off">
          <div className="space-y-2">
            <label htmlFor="displayName" className="field-label">
              Nom d’affichage
            </label>
            <input
              id="displayName"
              className="field-input"
              value={form.displayName}
              onChange={update("displayName")}
              placeholder="Prénom ou alias"
              autoComplete="off"
            />
            <p className="field-hint">
              Visible uniquement pour le suivi interne ; le téléphone n’est pas
              exposé publiquement.
            </p>
          </div>

          <div className="space-y-2">
            <label htmlFor="bloodGroup" className="field-label">
              Groupe sanguin <span className="font-normal text-accent">(requis)</span>
            </label>
            <BloodGroupSelect
              id="bloodGroup"
              value={form.bloodGroup}
              onChange={update("bloodGroup")}
              required
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="phone" className="field-label">
              Téléphone <span className="font-normal text-accent">(requis)</span>
            </label>
            <input
              id="phone"
              type="tel"
              inputMode="numeric"
              className="field-input"
              value={form.phone}
              onChange={update("phone")}
              placeholder="0190123456"
              autoComplete="off"
              required
            />
            <p className="field-hint">
              Exactement 10 chiffres béninois commençant par 01 (ex. 0190123456).
            </p>
          </div>

          <div className="space-y-2">
            <label htmlFor="city" className="field-label">
              Ville / zone <span className="font-normal text-accent">(requis)</span>
            </label>
            <select
              id="city"
              className="field-input"
              value={form.city}
              onChange={update("city")}
              required
            >
              <option value="">Choisir une ville</option>
              {DEMO_CITIES.map((city) => (
                <option key={city} value={city}>
                  {city}
                </option>
              ))}
            </select>
          </div>

          <fieldset className="rounded-2xl bg-light px-5 py-4">
            <legend className="px-1 text-sm font-bold text-secondary">Localisation</legend>
            <label className="mt-2 flex items-start gap-3 text-sm leading-6 text-secondary">
              <input
                type="checkbox"
                className="mt-1 h-4 w-4 rounded border-accent text-primary focus:ring-primary"
                checked={form.gpsConsent}
                onChange={update("gpsConsent")}
              />
              <span>
                J’accepte de partager une position approximative pour améliorer
                le matching avec les hôpitaux proches.
              </span>
            </label>
            <p className="mt-2 text-sm text-accent">
              {form.gpsConsent
                ? "Si le navigateur l’autorise, une position approximative sera enregistrée avec votre profil."
                : "Sans consentement, aucune coordonnée GPS n’est lue."}
            </p>
          </fieldset>

          <div className="space-y-2">
            <button type="submit" className="btn-primary w-full" disabled={!canSubmit}>
              {submitting ? "Enregistrement…" : "Rejoindre le réseau"}
            </button>
            {!canSubmit && !submitting ? (
              <p className="field-hint">
                Le bouton s’active lorsque le groupe, un téléphone 01… (10 chiffres) et
                la ville sont renseignés.
              </p>
            ) : null}
            {submitted ? (
              <p className="text-sm font-semibold text-success">
                Profil enregistré. Merci de rejoindre le réseau.
              </p>
            ) : null}
          </div>
        </form>
      </div>
    </PageFrame>
  );
}
