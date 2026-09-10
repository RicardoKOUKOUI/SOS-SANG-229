/** Constantes UI : groupes, villes, fallbacks hors ligne. */

export const BLOOD_GROUPS = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"];

export const DEMO_CITIES = [
  "Cotonou",
  "Porto-Novo",
  "Parakou",
  "Abomey-Calavi",
  "Bohicon",
  "Natitingou",
];

/**
 * Liste de secours si l’API hôpitaux est indisponible.
 * Plus tard : charger via l’API en filtrant `is_recognized=true`
 * (ex. GET /hospitals?is_recognized=true). Aucun saisie libre côté alerte.
 */
export const RECOGNIZED_HOSPITALS = [
  {
    id: "HOSP-DEMO-001",
    name: "Hôpital Demo Reconnu — Cotonou Nord",
    is_recognized: true,
  },
  {
    id: "HOSP-DEMO-002",
    name: "Hôpital Demo Reconnu — Cotonou Sud",
    is_recognized: true,
  },
  {
    id: "HOSP-DEMO-003",
    name: "Centre Hospitalier Demo Reconnu — Porto-Novo",
    is_recognized: true,
  },
  {
    id: "HOSP-DEMO-004",
    name: "Hôpital de Zone Demo Reconnu — Parakou",
    is_recognized: true,
  },
  {
    id: "HOSP-DEMO-005",
    name: "Hôpital Demo Reconnu — Abomey-Calavi",
    is_recognized: true,
  },
  {
    id: "HOSP-DEMO-006",
    name: "Hôpital Demo Reconnu — Bohicon",
    is_recognized: true,
  },
  {
    id: "HOSP-DEMO-007",
    name: "Centre Demo Transfusion Reconnu — Natitingou",
    is_recognized: true,
  },
];

export const DEMO_REQUESTS = [
  {
    id: "REQ-DEMO-001",
    status: "ouverte",
    group: "O+",
    zone: "Zone Demo A",
    hospital: "Hôpital Demo Reconnu — Cotonou Nord",
    patient: "Patient Demo A",
    updated: "Il y a 8 min",
  },
  {
    id: "REQ-DEMO-002",
    status: "en matching",
    group: "A+",
    zone: "Zone Demo B",
    hospital: "Centre Hospitalier Demo Reconnu — Porto-Novo",
    patient: "Patient Demo B",
    updated: "Il y a 22 min",
  },
  {
    id: "REQ-DEMO-003",
    status: "pourvue",
    group: "B+",
    zone: "Zone Demo C",
    hospital: "Hôpital de Zone Demo Reconnu — Parakou",
    patient: "Patient Demo C",
    updated: "Il y a 1 h",
  },
];

export const STATUS_META = {
  ouverte: {
    label: "Ouverte",
    className: "bg-primary/10 text-primary",
  },
  "en matching": {
    label: "En matching",
    className: "bg-light text-accent",
  },
  pourvue: {
    label: "Pourvue",
    className: "bg-success/10 text-success",
  },
  annulee: {
    label: "Annulée",
    className: "bg-light text-accent",
  },
};
