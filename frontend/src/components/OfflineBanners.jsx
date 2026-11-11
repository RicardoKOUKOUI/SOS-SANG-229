import { useOffline } from "../offline/OfflineContext.jsx";

export default function OfflineBanners() {
  const { online, syncing, pending, syncNow } = useOffline();

  if (online && !syncing && pending === 0) return null;

  return (
    <div className="border-b border-light bg-white/95">
      {!online ? (
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-3 px-4 py-2 text-sm sm:px-6">
          <p className="font-semibold text-warn">
            NAV-004 · Hors ligne — les envois texte partent en file IndexedDB.
          </p>
          <span className="text-accent">{pending} en attente</span>
        </div>
      ) : null}
      {online && (syncing || pending > 0) ? (
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-3 px-4 py-2 text-sm sm:px-6">
          <p className="font-semibold text-primary">
            NAV-005 · {syncing ? "Synchronisation…" : `${pending} élément(s) à synchroniser`}
          </p>
          {!syncing && pending > 0 ? (
            <button type="button" className="font-semibold text-primary underline" onClick={() => syncNow()}>
              Sync maintenant
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
