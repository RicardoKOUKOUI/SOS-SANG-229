import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import PageFrame from "../components/PageFrame.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import {
  BACKEND_STATUS_TO_UI,
  listRequests,
} from "../api/client.js";
import { DEMO_REQUESTS, STATUS_META } from "../data/demo.js";

const FILTERS = ["toutes", ...Object.keys(STATUS_META)];

function formatUpdated(iso) {
  if (!iso) return "—";
  try {
    const then = new Date(iso);
    const diffMs = Date.now() - then.getTime();
    if (Number.isNaN(diffMs)) return String(iso);
    const mins = Math.max(0, Math.floor(diffMs / 60_000));
    if (mins < 1) return "À l’instant";
    if (mins < 60) return `Il y a ${mins} min`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `Il y a ${hours} h`;
    return then.toLocaleString("fr-FR", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return String(iso);
  }
}

function mapApiRow(row) {
  const uiStatus =
    BACKEND_STATUS_TO_UI[row.status] || row.status || "ouverte";
  return {
    id: row.public_ref,
    status: uiStatus,
    group: row.blood_group_needed || "—",
    zone: row.zone_label || row.hospital_city || "—",
    hospital: row.hospital_name || "—",
    patient:
      row.patient_display_name ||
      `${row.alerted_donors_count ?? 0} alerté(s)`,
    updated: formatUpdated(row.updated_at || row.created_at),
  };
}

export default function LiveTracking({ onToast }) {
  const [searchParams] = useSearchParams();
  const focusRef = searchParams.get("ref") || "";

  const [filter, setFilter] = useState("toutes");
  const [emptyMode, setEmptyMode] = useState(false);
  const [rowsSource, setRowsSource] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fromApi, setFromApi] = useState(false);

  const load = useCallback(
    async ({ silent } = {}) => {
      if (!silent) setLoading(true);
      try {
        const data = await listRequests();
        setRowsSource((data || []).map(mapApiRow));
        setFromApi(true);
        if (!silent) {
          onToast(
            `Actualisé · ${(data || []).length} demande(s)`,
          );
        }
      } catch (err) {
        setRowsSource(DEMO_REQUESTS);
        setFromApi(false);
        if (!silent) {
          onToast(
            err?.message ||
              "API indisponible — affichage d’un aperçu hors ligne.",
          );
        }
      } finally {
        setLoading(false);
      }
    },
    [onToast],
  );

  useEffect(() => {
    load({ silent: true });
  }, [load]);

  const rows = useMemo(() => {
    if (emptyMode) return [];
    let list = rowsSource;
    if (focusRef) {
      const hit = list.filter((item) => item.id === focusRef);
      if (hit.length) list = hit;
    }
    if (filter === "toutes") return list;
    return list.filter((item) => item.status === filter);
  }, [filter, emptyMode, rowsSource, focusRef]);

  return (
    <PageFrame wide>
      <div className="space-y-8">
        <PageHeader kicker="Suivi" title="Demandes" highlight="en cours">
          Suivez les alertes transfusionnelles : ouvertes, en matching ou
          pourvues. Actualisez pour voir les dernières mises à jour.
        </PageHeader>

        {focusRef ? (
          <p className="rounded-2xl bg-primary/5 px-4 py-3 text-sm text-secondary">
            Filtre ref&nbsp;: <span className="font-mono font-bold">{focusRef}</span>
          </p>
        ) : null}

        <div className="flex flex-wrap gap-2">
          {FILTERS.map((key) => {
            const label = key === "toutes" ? "Toutes" : STATUS_META[key].label;
            const active = filter === key;
            return (
              <button
                key={key}
                type="button"
                onClick={() => {
                  setEmptyMode(false);
                  setFilter(key);
                }}
                className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                  active
                    ? "bg-primary text-white"
                    : "bg-light text-secondary hover:bg-primary/10"
                }`}
              >
                {label}
              </button>
            );
          })}
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            className="btn-secondary w-full sm:w-auto"
            disabled={loading}
            onClick={() => load({ silent: false })}
          >
            {loading ? "Chargement…" : "Actualiser"}
          </button>
          <button
            type="button"
            className="btn-secondary w-full sm:w-auto"
            onClick={() => setEmptyMode(true)}
          >
            Voir l’état vide
          </button>
        </div>

        {!fromApi && !loading ? (
          <p className="text-xs text-accent">
            Source : aperçu hors ligne (API indisponible).
          </p>
        ) : null}

        {rows.length === 0 ? (
          <div className="card text-center">
            <p className="text-lg font-extrabold text-secondary">
              Aucune demande pour ce filtre
            </p>
            <p className="mt-2 text-sm leading-6 text-accent">
              Aucune alerte ouverte ne correspond à ce filtre pour le moment.
            </p>
            <button
              type="button"
              className="btn-primary mt-5"
              onClick={() => {
                setEmptyMode(false);
                setFilter("toutes");
                load({ silent: true });
              }}
            >
              Réafficher les demandes
            </button>
          </div>
        ) : (
          <ul className="grid gap-4 md:grid-cols-2">
            {rows.map((item) => (
              <li
                key={item.id}
                className={`card space-y-4 ${
                  focusRef && item.id === focusRef
                    ? "ring-2 ring-primary"
                    : ""
                }`}
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <p className="font-mono text-sm font-bold text-secondary">{item.id}</p>
                  <StatusBadge status={item.status} />
                </div>
                <dl className="grid grid-cols-2 gap-x-3 gap-y-3 text-sm">
                  <div>
                    <dt className="text-xs font-bold uppercase tracking-wide text-accent">
                      Groupe
                    </dt>
                    <dd className="mt-0.5 font-bold text-primary">{item.group}</dd>
                  </div>
                  <div>
                    <dt className="text-xs font-bold uppercase tracking-wide text-accent">
                      Zone
                    </dt>
                    <dd className="mt-0.5 text-secondary">{item.zone}</dd>
                  </div>
                  <div>
                    <dt className="text-xs font-bold uppercase tracking-wide text-accent">
                      Établissement
                    </dt>
                    <dd className="mt-0.5 text-secondary">{item.hospital}</dd>
                  </div>
                  <div>
                    <dt className="text-xs font-bold uppercase tracking-wide text-accent">
                      Patient
                    </dt>
                    <dd className="mt-0.5 text-secondary">{item.patient}</dd>
                  </div>
                </dl>
                <p className="text-xs text-accent">Mis à jour {item.updated}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </PageFrame>
  );
}
