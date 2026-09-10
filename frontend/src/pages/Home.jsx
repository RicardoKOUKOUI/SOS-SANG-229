import { Link } from "react-router-dom";
import UrgencyBadge from "../components/UrgencyBadge.jsx";

const stats = [
  { value: "8", label: "Groupes sanguins" },
  { value: "< 3 min", label: "Pour lancer une alerte" },
  { value: "229", label: "Bénin · indicatif" },
];

const steps = [
  {
    n: "01",
    title: "Lancer l’alerte",
    body: "Un établissement indique le groupe demandé et l’hôpital. L’alerte est enregistrée immédiatement.",
  },
  {
    n: "02",
    title: "SMS aux donneurs proches",
    body: "Les volontaires compatibles à proximité seront contactés par SMS (déploiement en cours).",
  },
  {
    n: "03",
    title: "Suivre jusqu’au don",
    body: "Chaque demande a un statut visible pour rassurer l’équipe soignante et les proches.",
  },
];

const actions = [
  {
    to: "/alerte",
    title: "Signaler une urgence",
    body: "Créez une demande pour un patient et un hôpital reconnu.",
  },
  {
    to: "/donneur/inscription",
    title: "Devenir donneur",
    body: "Inscrivez votre groupe, téléphone et ville pour rejoindre le réseau.",
  },
  {
    to: "/suivi",
    title: "Suivre les demandes",
    body: "Consultez les alertes : ouvertes, en matching ou pourvues.",
  },
];

export default function Home() {
  return (
    <div>
      <section className="relative overflow-hidden bg-gradient-to-b from-primary/5 via-white to-light">
        <div
          className="pointer-events-none absolute -left-24 top-10 h-64 w-64 rounded-full bg-primary/10 blur-3xl"
          aria-hidden="true"
        />
        <div
          className="pointer-events-none absolute -right-16 bottom-0 h-72 w-72 rounded-full bg-primary/10 blur-3xl"
          aria-hidden="true"
        />
        <div className="relative mx-auto max-w-5xl px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <UrgencyBadge>Urgence transfusionnelle · Bénin</UrgencyBadge>
          <h1 className="mt-6 max-w-3xl text-4xl font-extrabold leading-[1.15] tracking-tight text-secondary sm:text-5xl lg:text-6xl">
            Une alerte, des réponses, une{" "}
            <span className="text-primary">vie</span> sauvée.
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-accent">
            SOS Sang 229 relie les hôpitaux aux donneurs volontaires à
            proximité. Inscrivez-vous ou lancez une alerte : le réseau SMS
            arrive bientôt pour contacter les compatibles près de vous.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link to="/alerte" className="btn-primary w-full sm:w-auto">
              Signaler une urgence
            </Link>
            <Link to="/donneur/inscription" className="btn-secondary w-full sm:w-auto">
              Je veux donner
            </Link>
          </div>
          <dl className="mt-14 grid grid-cols-1 gap-4 sm:grid-cols-3">
            {stats.map((stat) => (
              <div key={stat.label} className="card text-center">
                <dt className="text-sm font-semibold text-accent">{stat.label}</dt>
                <dd className="mt-1 text-3xl font-extrabold text-secondary">{stat.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:px-8">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary">
          Comment ça marche
        </p>
        <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-secondary">
          Trois gestes, une <span className="text-primary">chaîne</span> claire
        </h2>
        <ol className="mt-8 grid gap-4 md:grid-cols-3">
          {steps.map((step) => (
            <li key={step.n} className="card">
              <p className="text-sm font-extrabold text-primary">{step.n}</p>
              <h3 className="mt-3 text-lg font-bold text-secondary">{step.title}</h3>
              <p className="mt-2 text-sm leading-6 text-accent">{step.body}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="bg-light/70">
        <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold tracking-tight text-secondary">
            Agir <span className="text-primary">maintenant</span>
          </h2>
          <p className="mt-3 max-w-2xl text-base leading-7 text-accent">
            Trois parcours pour sauver des vies : signaler une urgence,
            rejoindre le réseau de donneurs, ou suivre une demande en cours.
          </p>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {actions.map((action) => (
              <Link
                key={action.to}
                to={action.to}
                className="card block transition hover:-translate-y-0.5 hover:shadow-soft"
              >
                <h3 className="text-lg font-bold text-secondary">{action.title}</h3>
                <p className="mt-2 text-sm leading-6 text-accent">{action.body}</p>
                <p className="mt-4 text-sm font-bold text-primary">Ouvrir →</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="card">
          <h2 className="text-xl font-extrabold text-secondary">Confiance et données</h2>
          <p className="mt-2 text-base leading-7 text-accent">
            Groupe sanguin, téléphone et localisation sont des données
            sensibles. Elles sont traitées avec soin : le téléphone et le GPS
            ne sont jamais exposés dans les réponses publiques de l’API.
          </p>
        </div>
      </section>

      <section className="bg-gradient-to-r from-primary to-primary-dark">
        <div className="mx-auto flex max-w-5xl flex-col items-start gap-6 px-4 py-14 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <div>
            <p className="text-sm font-bold uppercase tracking-wide text-white/80">
              Prêt à agir
            </p>
            <p className="mt-2 text-2xl font-extrabold text-white sm:text-3xl">
              Une alerte, des réponses, une vie sauvée.
            </p>
          </div>
          <Link
            to="/alerte"
            className="inline-flex items-center justify-center rounded-full bg-white px-6 py-3 text-base font-semibold text-primary shadow-soft hover:bg-light"
          >
            Lancer une alerte
          </Link>
        </div>
      </section>
    </div>
  );
}
