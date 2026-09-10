import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import BloodGroupSelect from "../components/BloodGroupSelect.jsx";
import HospitalSearch from "../components/HospitalSearch.jsx";
import PageFrame from "../components/PageFrame.jsx";
import PageHeader from "../components/PageHeader.jsx";
import UrgencyBadge from "../components/UrgencyBadge.jsx";
import { createAlert, listRecognizedHospitals } from "../api/client.js";
import { RECOGNIZED_HOSPITALS } from "../data/demo.js";

const INITIAL = {
  bloodGroup: "",
  patientName: "",
  hospital: "",
};

export default function EmergencyAlert({ onToast }) {
  const navigate = useNavigate();
  const [form, setForm] = useState(INITIAL);
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [hospitals, setHospitals] = useState([]);
  const [hospitalsError, setHospitalsError] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const rows = await listRecognizedHospitals();
        if (cancelled) return;
        const recognized = (rows || []).filter((h) => h.is_recognized !== false);
        setHospitals(recognized);
        setHospitalsError("");
      } catch (err) {
        if (cancelled) return;
        setHospitalsError(err?.message || "Impossible de charger les hôpitaux.");
        // Fallback labels only — UUIDs from demo are not valid for API submit
        setHospitals([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const hospitalOptions =
    hospitals.length > 0
      ? hospitals
      : RECOGNIZED_HOSPITALS.filter((item) => item.is_recognized);

  const hospitalIsRecognized = hospitalOptions.some(
    (item) => String(item.id) === String(form.hospital),
  );
  const canSubmit = Boolean(
    form.bloodGroup &&
      form.patientName.trim() &&
      hospitalIsRecognized &&
      hospitals.length > 0 &&
      !submitting,
  );

  function update(field) {
    return (event) => {
      setForm((current) => ({ ...current, [field]: event.target.value }));
    };
  }

  function setHospitalId(id) {
    setForm((current) => ({ ...current, hospital: id || "" }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!canSubmit) return;
    setSubmitting(true);
    try {
      const result = await createAlert({
        blood_group_needed: form.bloodGroup,
        patient_display_name: form.patientName.trim(),
        hospital_id: form.hospital,
      });
      const matchCount = result?.matching?.match_count ?? 0;
      const ref = result?.public_ref || "—";
      setSubmitted(true);
      onToast(
        `Alerte créée · ref ${ref} · ${matchCount} donneur(s) compatible(s)`,
      );
      setForm(INITIAL);
      if (result?.public_ref) {
        navigate(`/suivi?ref=${encodeURIComponent(result.public_ref)}`);
      }
    } catch (err) {
      onToast(err?.message || "Échec de la création d'alerte.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <PageFrame>
      <div className="space-y-8">
        <PageHeader kicker="Urgence" title="Alerte" highlight="don de sang">
          Déclarez un besoin transfusionnel. L’urgence est claire, le ton reste
          rassurant.
        </PageHeader>

        <UrgencyBadge>Alerte urgence · hôpital reconnu</UrgencyBadge>

        <form className="card space-y-6" onSubmit={handleSubmit} autoComplete="off">
          <div className="rounded-2xl bg-primary/5 px-5 py-4 text-sm leading-6 text-secondary">
            L’alerte est enregistrée et les donneurs compatibles seront
            contactés (SMS en cours de déploiement). Seuls les établissements
            reconnus peuvent être choisis.
          </div>

          <div className="space-y-2">
            <label htmlFor="neededGroup" className="field-label">
              Groupe demandé <span className="font-normal text-accent">(requis)</span>
            </label>
            <BloodGroupSelect
              id="neededGroup"
              value={form.bloodGroup}
              onChange={update("bloodGroup")}
              required
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="patientName" className="field-label">
              Nom du patient{" "}
              <span className="font-normal text-accent">(requis)</span>
            </label>
            <input
              id="patientName"
              className="field-input"
              value={form.patientName}
              onChange={update("patientName")}
              placeholder="Prénom ou initiales"
              autoComplete="off"
              required
            />
            <p className="field-hint">
              Préférez un prénom ou des initiales pour limiter l’exposition des
              données personnelles.
            </p>
          </div>

          <div className="space-y-2">
            <label htmlFor="hospital" className="field-label">
              Hôpital reconnu{" "}
              <span className="font-normal text-accent">
                (liste officielle, requis)
              </span>
            </label>
            <HospitalSearch
              id="hospital"
              hospitals={hospitalOptions}
              value={form.hospital}
              onChange={setHospitalId}
              required
            />
            <p className="field-hint">
              Tapez pour rechercher parmi les structures reconnues (CNHU, CHU,
              CHD, hôpitaux de zone). La saisie libre d’un centre non listé
              n’est pas autorisée.
              {hospitalsError
                ? ` API indisponible (${hospitalsError}) — liste de secours affichée, envoi désactivé.`
                : ""}
            </p>
          </div>

          <div className="space-y-2">
            <button type="submit" className="btn-primary w-full" disabled={!canSubmit}>
              {submitting ? "Envoi…" : "Envoyer l’alerte"}
            </button>
            {!canSubmit && !submitting ? (
              <p className="field-hint">
                Renseignez le groupe, le patient et un hôpital reconnu de la
                liste pour activer l’envoi.
              </p>
            ) : null}
            {submitted ? (
              <p className="text-sm font-semibold text-success">
                Alerte créée. Redirection vers le suivi…
              </p>
            ) : null}
          </div>
        </form>
      </div>
    </PageFrame>
  );
}
