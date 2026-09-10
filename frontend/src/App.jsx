import { useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import BrandMark from "./components/BrandMark.jsx";
import Toast from "./components/Toast.jsx";
import useToast from "./hooks/useToast.js";
import Home from "./pages/Home.jsx";
import DonorRegistration from "./pages/DonorRegistration.jsx";
import EmergencyAlert from "./pages/EmergencyAlert.jsx";
import LiveTracking from "./pages/LiveTracking.jsx";

const links = [
  { to: "/", label: "Accueil", short: "Accueil", end: true },
  { to: "/donneur/inscription", label: "Inscription donneur", short: "Donneur" },
  { to: "/alerte", label: "Alerte urgence", short: "Alerte" },
  { to: "/suivi", label: "Suivi des demandes", short: "Suivi" },
];

function navClass({ isActive }) {
  return isActive
    ? "font-bold text-primary"
    : "font-medium text-secondary/80 hover:text-primary";
}

export default function App() {
  const toast = useToast();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="flex min-h-dvh flex-col bg-white">
      <a
        href="#contenu"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-full focus:bg-white focus:px-3 focus:py-2"
      >
        Aller au contenu
      </a>

      <header className="sticky top-0 z-30 border-b border-light/80 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
          <NavLink to="/" className="flex min-w-0 items-center gap-2.5" end>
            <BrandMark />
            <span className="min-w-0">
              <span className="block truncate text-base font-extrabold tracking-tight text-secondary">
                SOS Sang 229
              </span>
              <span className="block text-xs font-medium text-accent">
                Don de sang · urgence · Bénin
              </span>
            </span>
          </NavLink>
          <button
            type="button"
            className="rounded-full border-2 border-primary px-4 py-1.5 text-sm font-semibold text-primary sm:hidden"
            aria-expanded={menuOpen}
            aria-controls="nav-principale"
            onClick={() => setMenuOpen((open) => !open)}
          >
            Menu
          </button>
          <nav className="hidden flex-wrap justify-end gap-x-6 gap-y-1 text-sm sm:flex">
            {links.map((link) => (
              <NavLink key={link.to} to={link.to} end={link.end} className={navClass}>
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>
        {menuOpen ? (
          <nav
            id="nav-principale"
            className="border-t border-light px-4 py-4 sm:hidden"
          >
            <ul className="space-y-3 text-sm">
              {links.map((link) => (
                <li key={link.to}>
                  <NavLink
                    to={link.to}
                    end={link.end}
                    className={navClass}
                    onClick={() => setMenuOpen(false)}
                  >
                    {link.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
        ) : null}
      </header>

      <main id="contenu" className="flex-1 pb-20 sm:pb-0">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/donneur/inscription"
            element={<DonorRegistration onToast={toast.show} />}
          />
          <Route path="/alerte" element={<EmergencyAlert onToast={toast.show} />} />
          <Route path="/suivi" element={<LiveTracking onToast={toast.show} />} />
        </Routes>
      </main>

      <footer className="hidden border-t border-light bg-secondary sm:block">
        <div className="mx-auto flex max-w-5xl flex-col gap-1 px-4 py-6 text-sm text-white/80 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <p className="font-semibold text-white">SOS Sang 229</p>
          <p>Réseau d’alerte citoyen · Bénin</p>
        </div>
      </footer>

      <nav
        aria-label="Navigation principale"
        className="fixed inset-x-0 bottom-0 z-30 border-t border-light bg-white/90 backdrop-blur-md sm:hidden"
      >
        <ul className="mx-auto grid max-w-5xl grid-cols-4">
          {links.map((link) => (
            <li key={link.to}>
              <NavLink
                to={link.to}
                end={link.end}
                className={({ isActive }) =>
                  `flex flex-col items-center px-1 py-2.5 text-[11px] font-bold ${
                    isActive ? "text-primary" : "text-accent"
                  }`
                }
              >
                {link.short}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <Toast message={toast.message} onDismiss={toast.dismiss} />
    </div>
  );
}
