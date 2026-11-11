import { Link } from "react-router-dom";

export default function Verify() {
  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Vérification</h1>
      <p className="mt-2 text-accent">AUTH-005</p>
      <div className="card mt-8">
        <p>
          OTP email/SMS non activé : Twilio et mailer absents. Les comptes fonctionnent sans
          vérification email pour cette phase.
        </p>
        <Link to="/" className="btn-primary mt-6 inline-flex">
          Retour à l’accueil
        </Link>
      </div>
    </section>
  );
}
