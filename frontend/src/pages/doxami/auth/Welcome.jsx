import { Link } from "react-router-dom";
import BrandMark from "../../../components/BrandMark.jsx";

export default function Welcome() {
  return (
    <section className="bg-mesh min-h-[70vh]">
      <div className="mx-auto flex max-w-lg flex-col px-4 py-14 sm:px-6">
        <BrandMark className="h-14 w-14" />
        <h1 className="mt-6 font-display text-5xl font-extrabold text-secondary">DOXAMI</h1>
        <p className="mt-4 text-lg leading-relaxed text-accent">
          Écosystème unifié — communication, social, collaboration. Mobile-first, honnête sur
          ce qui est vraiment branché.
        </p>
        <div className="mt-8 flex flex-col gap-3">
          <Link to="/auth/register" className="btn-primary w-full">
            Créer un compte
          </Link>
          <Link to="/auth/login" className="btn-secondary w-full">
            Se connecter
          </Link>
        </div>
      </div>
    </section>
  );
}
