import { useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import BrandMark from "./components/BrandMark.jsx";
import OfflineBanners from "./components/OfflineBanners.jsx";
import Toast from "./components/Toast.jsx";
import useToast from "./hooks/useToast.js";
import { OfflineProvider } from "./offline/OfflineContext.jsx";
import Communities from "./pages/doxami/Communities.jsx";
import CommunityDetail from "./pages/doxami/CommunityDetail.jsx";
import CommunityMembers from "./pages/doxami/CommunityMembers.jsx";
import CommunityNew from "./pages/doxami/CommunityNew.jsx";
import CreatePost from "./pages/doxami/CreatePost.jsx";
import Explore from "./pages/doxami/Explore.jsx";
import FollowList from "./pages/doxami/FollowList.jsx";
import HomeFeed from "./pages/doxami/HomeFeed.jsx";
import Hub from "./pages/doxami/Hub.jsx";
import LegacySangHome from "./pages/doxami/LegacySangHome.jsx";
import MessageInfo from "./pages/doxami/MessageInfo.jsx";
import MessageNew from "./pages/doxami/MessageNew.jsx";
import MessageThread from "./pages/doxami/MessageThread.jsx";
import MessagesInbox from "./pages/doxami/MessagesInbox.jsx";
import PlaceholderModule from "./pages/doxami/PlaceholderModule.jsx";
import PostDetail from "./pages/doxami/PostDetail.jsx";
import Profile from "./pages/doxami/Profile.jsx";
import ProfileEdit from "./pages/doxami/ProfileEdit.jsx";
import PublicProfile from "./pages/doxami/PublicProfile.jsx";
import Settings from "./pages/doxami/Settings.jsx";
import SettingsData from "./pages/doxami/SettingsData.jsx";
import SettingsLanguage from "./pages/doxami/SettingsLanguage.jsx";
import SettingsPrivacy from "./pages/doxami/SettingsPrivacy.jsx";
import ForgotPassword from "./pages/doxami/auth/ForgotPassword.jsx";
import Login from "./pages/doxami/auth/Login.jsx";
import Logout from "./pages/doxami/auth/Logout.jsx";
import Register from "./pages/doxami/auth/Register.jsx";
import Verify from "./pages/doxami/auth/Verify.jsx";
import Welcome from "./pages/doxami/auth/Welcome.jsx";
import DonorRegistration from "./pages/DonorRegistration.jsx";
import EmergencyAlert from "./pages/EmergencyAlert.jsx";
import LiveTracking from "./pages/LiveTracking.jsx";

const navItems = [
  { to: "/", label: "Accueil", short: "Home", end: true },
  { to: "/explore", label: "Explore", short: "Explore" },
  { to: "/create", label: "Create", short: "Create" },
  { to: "/messages", label: "Messages", short: "Msgs" },
  { to: "/communities", label: "Communities", short: "Comms" },
  { to: "/profile", label: "Profile", short: "Profil" },
];

function navClass({ isActive }) {
  return isActive
    ? "font-bold text-primary"
    : "font-medium text-accent hover:text-primary";
}

export default function App() {
  const toast = useToast();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <OfflineProvider onToast={toast.show}>
    <div className="flex min-h-dvh flex-col bg-paper">
      <a
        href="#contenu"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-xl focus:bg-white focus:px-3 focus:py-2"
      >
        Aller au contenu
      </a>

      <OfflineBanners />

      <header className="sticky top-0 z-30 border-b border-light/80 bg-paper/85 backdrop-blur-md">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
          <NavLink to="/" className="flex min-w-0 items-center gap-2.5" end>
            <BrandMark />
            <span className="min-w-0">
              <span className="font-display block truncate text-lg font-extrabold tracking-tight text-secondary">
                DOXAMI
              </span>
              <span className="block text-xs font-medium text-accent">Mesh · social · actions</span>
            </span>
          </NavLink>
          <div className="flex items-center gap-2">
            <NavLink
              to="/hub"
              className="hidden rounded-xl border border-primary/30 px-3 py-1.5 text-sm font-semibold text-primary sm:inline-flex"
            >
              Hub
            </NavLink>
            <button
              type="button"
              className="rounded-xl border-2 border-primary px-4 py-1.5 text-sm font-semibold text-primary lg:hidden"
              aria-expanded={menuOpen}
              aria-controls="nav-principale"
              onClick={() => setMenuOpen((open) => !open)}
            >
              Menu
            </button>
          </div>
          <nav className="hidden flex-wrap justify-end gap-x-5 gap-y-1 text-sm lg:flex">
            {navItems.map((link) => (
              <NavLink key={link.to} to={link.to} end={link.end} className={navClass}>
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>
        {menuOpen ? (
          <nav id="nav-principale" className="border-t border-light px-4 py-4 lg:hidden">
            <ul className="space-y-3 text-sm">
              {navItems.map((link) => (
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
              <li>
                <NavLink to="/hub" className={navClass} onClick={() => setMenuOpen(false)}>
                  Hub
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/legacy/sang"
                  className={navClass}
                  onClick={() => setMenuOpen(false)}
                >
                  Legacy SOS Sang
                </NavLink>
              </li>
            </ul>
          </nav>
        ) : null}
      </header>

      <main id="contenu" className="flex-1 pb-20 lg:pb-0">
        <Routes>
          <Route path="/" element={<HomeFeed onToast={toast.show} />} />
          <Route path="/auth" element={<Welcome />} />
          <Route path="/auth/register" element={<Register onToast={toast.show} />} />
          <Route path="/auth/login" element={<Login onToast={toast.show} />} />
          <Route path="/auth/forgot" element={<ForgotPassword />} />
          <Route path="/auth/verify" element={<Verify />} />
          <Route path="/auth/logout" element={<Logout />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/profile/edit" element={<ProfileEdit onToast={toast.show} />} />
          <Route path="/u/:username" element={<PublicProfile onToast={toast.show} />} />
          <Route path="/u/:username/followers" element={<FollowList mode="followers" />} />
          <Route path="/u/:username/following" element={<FollowList mode="following" />} />
          <Route path="/posts/:postId" element={<PostDetail onToast={toast.show} />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/settings/privacy" element={<SettingsPrivacy />} />
          <Route path="/settings/language" element={<SettingsLanguage />} />
          <Route path="/settings/data" element={<SettingsData />} />
          <Route path="/hub" element={<Hub />} />
          <Route
            path="/hub/music"
            element={<PlaceholderModule code="HUB-MUSIC" title="Music" />}
          />
          <Route path="/hub/meet" element={<PlaceholderModule code="HUB-MEET" title="Meet" />} />
          <Route path="/hub/pay" element={<PlaceholderModule code="HUB-PAY" title="Pay" />} />
          <Route
            path="/hub/watch"
            element={<PlaceholderModule code="HUB-WATCH" title="Watch" />}
          />
          <Route path="/hub/live" element={<PlaceholderModule code="HUB-LIVE" title="Live" />} />
          <Route
            path="/hub/games"
            element={<PlaceholderModule code="HUB-GAMES" title="Games" />}
          />
          <Route path="/hub/ai" element={<PlaceholderModule code="HUB-AI" title="AI" />} />
          <Route
            path="/hub/marketplace"
            element={<PlaceholderModule code="HUB-MARKET" title="Marketplace" />}
          />
          <Route
            path="/hub/events"
            element={<PlaceholderModule code="HUB-EVENTS" title="Events" />}
          />
          <Route path="/hub/work" element={<PlaceholderModule code="HUB-WORK" title="Work" />} />
          <Route
            path="/hub/creator"
            element={<PlaceholderModule code="HUB-CREATOR" title="Creator Studio" />}
          />
          <Route
            path="/hub/professional"
            element={<PlaceholderModule code="HUB-PRO" title="Professional" />}
          />
          <Route path="/hub/mesh" element={<PlaceholderModule code="HUB-MESH" title="MESH" />} />
          <Route
            path="/hub/actions"
            element={<PlaceholderModule code="HUB-ACTIONS" title="Actions" />}
          />
          <Route path="/explore" element={<Explore onToast={toast.show} />} />
          <Route path="/create" element={<CreatePost onToast={toast.show} />} />
          <Route path="/messages" element={<MessagesInbox onToast={toast.show} />} />
          <Route path="/messages/new" element={<MessageNew onToast={toast.show} />} />
          <Route path="/messages/:threadId" element={<MessageThread onToast={toast.show} />} />
          <Route path="/messages/:threadId/info" element={<MessageInfo />} />
          <Route
            path="/messages/:threadId/call"
            element={
              <PlaceholderModule
                code="MSG-009"
                title="Appel audio"
                body="WebRTC non déployé — aucun appel simulé."
              />
            }
          />
          <Route path="/communities" element={<Communities />} />
          <Route path="/communities/new" element={<CommunityNew onToast={toast.show} />} />
          <Route
            path="/communities/:communityId"
            element={<CommunityDetail onToast={toast.show} />}
          />
          <Route path="/communities/:communityId/members" element={<CommunityMembers />} />
          <Route path="/legacy/sang" element={<LegacySangHome />} />
          <Route
            path="/legacy/sang/donneur/inscription"
            element={<DonorRegistration onToast={toast.show} />}
          />
          <Route
            path="/legacy/sang/alerte"
            element={<EmergencyAlert onToast={toast.show} />}
          />
          <Route path="/legacy/sang/suivi" element={<LiveTracking onToast={toast.show} />} />
          {/* Temporary redirects for old sang URLs */}
          <Route path="/donneur/inscription" element={<DonorRegistration onToast={toast.show} />} />
          <Route path="/alerte" element={<EmergencyAlert onToast={toast.show} />} />
          <Route path="/suivi" element={<LiveTracking onToast={toast.show} />} />
        </Routes>
      </main>

      <footer className="hidden border-t border-light bg-secondary lg:block">
        <div className="mx-auto flex max-w-5xl flex-col gap-1 px-4 py-6 text-sm text-white/80 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <p className="font-display font-semibold text-white">DOXAMI</p>
          <p>
            Phase 2 fondations ·{" "}
            <NavLink to="/legacy/sang" className="underline-offset-2 hover:underline">
              Legacy SOS Sang 229
            </NavLink>
          </p>
        </div>
      </footer>

      <nav
        aria-label="Navigation principale"
        className="fixed inset-x-0 bottom-0 z-30 border-t border-light bg-paper/95 backdrop-blur-md lg:hidden"
      >
        <ul className="mx-auto grid max-w-5xl grid-cols-6">
          {navItems.map((link) => (
            <li key={link.to}>
              <NavLink
                to={link.to}
                end={link.end}
                className={({ isActive }) =>
                  `flex flex-col items-center px-0.5 py-2.5 text-[10px] font-bold ${
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
    </OfflineProvider>
  );
}
