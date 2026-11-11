import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchMeshStatus } from "../../api/mesh.js";
import { detectMeshCapabilities, resolveLocalMode } from "../../mesh/capabilities.js";
import { createMeshTransport } from "../../mesh/transport.js";
import { useOffline } from "../../offline/OfflineContext.jsx";

export default function MeshHub() {
  const { online } = useOffline();
  const [server, setServer] = useState(null);
  const [localCaps, setLocalCaps] = useState(() => detectMeshCapabilities());
  const [transportStatus, setTransportStatus] = useState(null);
  const [error, setError] = useState("");
  const [probeError, setProbeError] = useState("");

  useEffect(() => {
    let cancelled = false;
    fetchMeshStatus()
      .then((data) => {
        if (!cancelled) setServer(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Statut MESH API indisponible.");
      });

    const transport = createMeshTransport();
    transport
      .getStatus()
      .then((status) => {
        if (!cancelled) setTransportStatus(status);
      })
      .catch((err) => {
        if (!cancelled) setProbeError(err.message || "Transport probe failed.");
      });

    function refresh() {
      setLocalCaps(detectMeshCapabilities());
    }
    window.addEventListener("online", refresh);
    window.addEventListener("offline", refresh);
    return () => {
      cancelled = true;
      window.removeEventListener("online", refresh);
      window.removeEventListener("offline", refresh);
    };
  }, [online]);

  const mode = resolveLocalMode({ ...localCaps, online });

  async function tryDiscovery() {
    setProbeError("");
    try {
      const transport = createMeshTransport();
      await transport.startDiscovery();
    } catch (err) {
      setProbeError(err.message || "Discovery impossible.");
    }
  }

  return (
    <section className="bg-mesh min-h-[70vh]">
      <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">HUB-MESH</p>
        <h1 className="mt-2 text-4xl font-extrabold">DOXAMI MESH</h1>
        <p className="mt-3 max-w-2xl text-accent">
          Communication locale sans Internet — uniquement si un transport natif est présent.
          La sync IndexedDB offline n’est <strong>pas</strong> du MESH.
        </p>

        <div className="card mt-8 space-y-3">
          <h2 className="text-xl font-bold">Mode local</h2>
          <p className="text-3xl font-display font-extrabold text-primary">{mode}</p>
          <ul className="text-sm text-accent space-y-1">
            <li>Réseau navigateur : {online ? "online" : "offline"}</li>
            <li>Pont natif DoxamiNativeMesh : {localCaps.nativeBridge ? "détecté" : "absent"}</li>
            <li>BLE : {localCaps.ble ? "oui" : "non"}</li>
            <li>Wi-Fi Direct : {localCaps.wifiDirect ? "oui" : "non"}</li>
            <li>Nearby : {localCaps.nearby ? "oui" : "non"}</li>
            <li>libp2p : {localCaps.libp2p ? "oui" : "non"}</li>
          </ul>
        </div>

        <div className="card mt-4 space-y-3">
          <h2 className="text-xl font-bold">API /mesh/status</h2>
          {error ? <p className="text-warn">{error}</p> : null}
          {server ? (
            <>
              <p className="text-sm">{server.reason}</p>
              <p className="text-sm text-accent">{server.notes}</p>
              <p className="text-sm">
                Transport serveur prêt : {server.mesh_transport_ready ? "oui" : "non"}
              </p>
            </>
          ) : (
            <p className="text-accent">Chargement…</p>
          )}
        </div>

        <div className="card mt-4 space-y-3">
          <h2 className="text-xl font-bold">Transport client</h2>
          {transportStatus ? (
            <p className="text-sm">
              Disponible : {transportStatus.available ? "oui" : "non"} — {transportStatus.reason}
            </p>
          ) : (
            <p className="text-accent">Probe…</p>
          )}
          {probeError ? <p className="text-warn text-sm">{probeError}</p> : null}
          <button type="button" className="btn-secondary" onClick={tryDiscovery}>
            Tenter discovery (échoue sans pont natif)
          </button>
        </div>

        <Link to="/hub" className="mt-8 inline-block text-sm font-semibold text-primary">
          ← Hub
        </Link>
      </div>
    </section>
  );
}
