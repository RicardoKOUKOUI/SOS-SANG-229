import { Link } from "react-router-dom";

export default function ForgotPassword() {
  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Mot de passe oublié</h1>
      <p className="mt-2 text-accent">AUTH-004</p>
      <div className="card mt-8">
        <p className="text-secondary">
          La réinitialisation par email n’est pas encore branchée (aucun fournisseur mail
          configuré). Aucun faux succès — revenez plus tard ou contactez un admin local.
        </p>
        <Link to="/auth/login" className="btn-secondary mt-6 inline-flex">
          Retour connexion
        </Link>
      </div>
    </section>
  );
}
