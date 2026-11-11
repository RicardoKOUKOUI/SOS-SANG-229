import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../../auth/AuthContext.jsx";

export default function Logout() {
  const { logout, isAuthenticated } = useAuth();
  const [done, setDone] = useState(!isAuthenticated);
  const ran = useRef(false);

  useEffect(() => {
    if (ran.current) return;
    ran.current = true;
    let cancelled = false;
    async function run() {
      if (isAuthenticated) {
        await logout();
      }
      if (!cancelled) setDone(true);
    }
    run();
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, logout]);

  return (
    <section className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-extrabold">Déconnexion</h1>
      <p className="mt-2 text-accent">AUTH-012</p>
      <div className="card mt-8">
        <p>{done ? "Session terminée sur cet appareil." : "Déconnexion en cours…"}</p>
        <Link to="/auth/login" className="btn-primary mt-6 inline-flex">
          Se reconnecter
        </Link>
      </div>
    </section>
  );
}
