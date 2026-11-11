import { Link } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function HomeFeed() {
  const { isAuthenticated, user } = useAuth();

  return (
    <section className="bg-mesh min-h-[70vh]">
      <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:px-8">
        <p className="font-display text-sm font-semibold uppercase tracking-[0.2em] text-primary">
          DOXAMI
        </p>
        <h1 className="mt-3 max-w-xl text-4xl font-extrabold text-secondary sm:text-5xl">
          Votre espace commence ici
        </h1>
        <p className="mt-4 max-w-xl text-lg leading-relaxed text-accent">
          Feed social léger prévu en Phase 3. Les fondations (compte, profil, navigation)
          sont déjà opérationnelles — sans faux succès.
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          {isAuthenticated ? (
            <>
              <Link to="/create" className="btn-primary">
                Créer (bientôt)
              </Link>
              <Link to="/profile" className="btn-secondary">
                Mon profil · @{user?.username}
              </Link>
            </>
          ) : (
            <>
              <Link to="/auth/register" className="btn-primary">
                Créer un compte
              </Link>
              <Link to="/auth/login" className="btn-secondary">
                Se connecter
              </Link>
            </>
          )}
        </div>

        <div className="card mt-10">
          <h2 className="text-xl font-bold">Feed · HOME-001</h2>
          <p className="mt-2 text-accent">
            Aucune publication pour l’instant. Le feed authentifié arrivera en Phase 3.
          </p>
          <Link
            to="/legacy/sang"
            className="mt-4 inline-block text-sm font-semibold text-primary underline-offset-4 hover:underline"
          >
            Ouvrir la démo hackathon SOS Sang 229 →
          </Link>
        </div>
      </div>
    </section>
  );
}
