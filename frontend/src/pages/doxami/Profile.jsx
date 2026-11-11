import { Link } from "react-router-dom";
import RequireAuth from "../../components/RequireAuth.jsx";
import { useAuth } from "../../auth/AuthContext.jsx";

function ProfileInner() {
  const { user } = useAuth();
  return (
    <section className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">PROFILE-001</p>
      <h1 className="mt-2 text-3xl font-extrabold">{user.display_name}</h1>
      <p className="mt-1 text-accent">@{user.username}</p>
      <div className="card mt-6 space-y-3">
        <p>
          <span className="font-semibold">Email :</span> {user.email}
        </p>
        <p>
          <span className="font-semibold">Bio :</span>{" "}
          {user.bio?.trim() ? user.bio : "Aucune bio pour le moment."}
        </p>
        <p className="text-sm text-accent">
          Vérification email : {user.email_verified ? "oui" : "non (OTP non branché)"}
        </p>
      </div>
      <div className="mt-6 flex flex-wrap gap-3">
        <Link to="/profile/edit" className="btn-primary">
          Éditer le profil
        </Link>
        <Link to={`/u/${user.username}/followers`} className="btn-secondary">
          Abonnés
        </Link>
        <Link to={`/u/${user.username}/following`} className="btn-secondary">
          Abonnements
        </Link>
        <Link to="/create" className="btn-secondary">
          Créer
        </Link>
        <Link to="/settings" className="btn-secondary">
          Paramètres
        </Link>
        <Link to="/auth/logout" className="btn-secondary">
          Déconnexion
        </Link>
      </div>
    </section>
  );
}

export default function Profile() {
  return (
    <RequireAuth>
      <ProfileInner />
    </RequireAuth>
  );
}
