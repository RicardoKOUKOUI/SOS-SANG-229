import { createContext, useContext, useEffect, useState } from "react";
import { useAuth } from "../auth/AuthContext.jsx";
import { listOutboxItems, pendingCount } from "./outbox.js";
import { flushOutbox } from "./sync.js";

const DATA_SAVER_KEY = "doxami_data_saver";
const OfflineContext = createContext(null);

export function OfflineProvider({ children, onToast }) {
  const { token, isAuthenticated } = useAuth();
  const [online, setOnline] = useState(
    typeof navigator === "undefined" ? true : navigator.onLine,
  );
  const [syncing, setSyncing] = useState(false);
  const [pending, setPending] = useState(0);
  const [dataSaver, setDataSaverState] = useState(() => {
    try {
      return localStorage.getItem(DATA_SAVER_KEY) === "1";
    } catch {
      return false;
    }
  });

  async function refreshPending() {
    try {
      setPending(await pendingCount());
    } catch {
      setPending(0);
    }
  }

  async function syncNow() {
    if (!isAuthenticated || !token || !navigator.onLine) return { synced: 0, failed: 0 };
    setSyncing(true);
    try {
      const result = await flushOutbox(token);
      await refreshPending();
      if (result.synced > 0) {
        onToast?.(`${result.synced} élément(s) synchronisé(s).`);
      }
      if (result.failed > 0) {
        onToast?.(`${result.failed} élément(s) en échec de sync.`);
      }
      return result;
    } finally {
      setSyncing(false);
    }
  }

  function setDataSaver(enabled) {
    setDataSaverState(Boolean(enabled));
    try {
      localStorage.setItem(DATA_SAVER_KEY, enabled ? "1" : "0");
    } catch {
      /* ignore */
    }
  }

  useEffect(() => {
    function onOnline() {
      setOnline(true);
      syncNow();
    }
    function onOffline() {
      setOnline(false);
    }
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    refreshPending();
    if (navigator.onLine && isAuthenticated) {
      syncNow();
    }
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, isAuthenticated]);

  const value = {
    online,
    syncing,
    pending,
    dataSaver,
    setDataSaver,
    refreshPending,
    syncNow,
    listOutbox: listOutboxItems,
  };

  return <OfflineContext.Provider value={value}>{children}</OfflineContext.Provider>;
}

export function useOffline() {
  const ctx = useContext(OfflineContext);
  if (!ctx) throw new Error("useOffline must be used within OfflineProvider");
  return ctx;
}
