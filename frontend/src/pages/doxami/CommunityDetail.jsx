import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  getCommunity,
  joinCommunity,
  listCommunityMembers,
  listCommunityRooms,
  listRoomMessages,
  sendRoomMessage,
} from "../../api/messaging.js";
import { useAuth } from "../../auth/AuthContext.jsx";
import { useOffline } from "../../offline/OfflineContext.jsx";
import { enqueueOutboxItem } from "../../offline/outbox.js";

export default function CommunityDetail({ onToast }) {
  const { communityId } = useParams();
  const { token, isAuthenticated } = useAuth();
  const { online, refreshPending, dataSaver } = useOffline();
  const [community, setCommunity] = useState(null);
  const [members, setMembers] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [activeRoom, setActiveRoom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [body, setBody] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function loadBase() {
    const data = await getCommunity(token, communityId);
    setCommunity(data);
    const memberData = await listCommunityMembers(communityId);
    setMembers(memberData);
    if (data.is_member && token) {
      const roomData = await listCommunityRooms(token, communityId);
      setRooms(roomData);
      if (roomData[0]) setActiveRoom(roomData[0]);
    } else {
      setRooms([]);
      setActiveRoom(null);
      setMessages([]);
    }
  }

  useEffect(() => {
    let cancelled = false;
    loadBase().catch((err) => {
      if (!cancelled) setError(err.message || "Communauté introuvable.");
    });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [communityId, token]);

  useEffect(() => {
    if (!activeRoom || !token || !community?.is_member) return undefined;
    let cancelled = false;
    async function loadMessages() {
      try {
        const data = await listRoomMessages(token, communityId, activeRoom.id);
        if (!cancelled) setMessages(data);
      } catch {
        /* keep previous */
      }
    }
    loadMessages();
    const timer = setInterval(() => {
      if (!navigator.onLine) return;
      loadMessages();
    }, dataSaver ? 15000 : 5000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [activeRoom, token, communityId, community?.is_member, dataSaver]);

  async function onJoin() {
    if (!token) {
      onToast?.("Connectez-vous pour rejoindre.");
      return;
    }
    setBusy(true);
    try {
      await joinCommunity(token, communityId);
      await loadBase();
      onToast?.("Vous avez rejoint la communauté.");
    } catch (err) {
      onToast?.(err.message || "Adhésion impossible.");
    } finally {
      setBusy(false);
    }
  }

  async function onSend(event) {
    event.preventDefault();
    if (!activeRoom) return;
    setBusy(true);
    try {
      if (!online) {
        await enqueueOutboxItem({
          type: "room_message",
          payload: {
            communityId,
            roomId: activeRoom.id,
            body: body.trim(),
          },
        });
        await refreshPending();
        setBody("");
        onToast?.("Hors ligne — message salon mis en file.");
        return;
      }
      await sendRoomMessage(token, communityId, activeRoom.id, body);
      setBody("");
      const data = await listRoomMessages(token, communityId, activeRoom.id);
      setMessages(data);
    } catch (err) {
      if (!navigator.onLine || /Failed to fetch|NetworkError/i.test(err.message || "")) {
        await enqueueOutboxItem({
          type: "room_message",
          payload: {
            communityId,
            roomId: activeRoom.id,
            body: body.trim(),
          },
        });
        await refreshPending();
        setBody("");
        onToast?.("Réseau indisponible — message salon mis en file.");
      } else {
        onToast?.(err.message || "Message impossible.");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">COM-002</p>
      {error ? <p className="mt-6 text-warn">{error}</p> : null}
      {community ? (
        <>
          <h1 className="mt-2 text-3xl font-extrabold">{community.name}</h1>
          <p className="mt-2 text-accent">{community.description || "Pas de description."}</p>
          <div className="mt-4 flex flex-wrap gap-3">
            {!community.is_member && isAuthenticated ? (
              <button type="button" className="btn-primary" disabled={busy} onClick={onJoin}>
                Rejoindre · COM-006
              </button>
            ) : null}
            <Link to={`/communities/${communityId}/members`} className="btn-secondary">
              Membres · COM-005
            </Link>
          </div>

          {community.is_member ? (
            <div className="mt-8 grid gap-6 lg:grid-cols-[220px_1fr]">
              <aside>
                <h2 className="font-bold">Salons · COM-004</h2>
                <ul className="mt-3 space-y-2">
                  {rooms.map((room) => (
                    <li key={room.id}>
                      <button
                        type="button"
                        className={`w-full rounded-xl px-3 py-2 text-left text-sm font-semibold ${
                          activeRoom?.id === room.id
                            ? "bg-primary text-white"
                            : "bg-white border border-light"
                        }`}
                        onClick={() => setActiveRoom(room)}
                      >
                        #{room.slug}
                      </button>
                    </li>
                  ))}
                </ul>
              </aside>
              <div>
                <h2 className="font-bold">{activeRoom ? `#${activeRoom.slug}` : "Salon"}</h2>
                <ul className="mt-4 space-y-3">
                  {messages.map((message) => (
                    <li key={message.id} className="rounded-xl border border-light bg-white px-4 py-3">
                      <p className="text-xs font-semibold text-accent">@{message.author.username}</p>
                      <p className="mt-1 whitespace-pre-wrap">{message.body}</p>
                    </li>
                  ))}
                </ul>
                {activeRoom ? (
                  <form className="mt-4 space-y-3" onSubmit={onSend}>
                    <textarea
                      className="field-input min-h-24"
                      required
                      value={body}
                      onChange={(e) => setBody(e.target.value)}
                    />
                    <button className="btn-primary" type="submit" disabled={busy}>
                      Envoyer
                    </button>
                  </form>
                ) : null}
              </div>
            </div>
          ) : (
            <p className="mt-8 text-accent">Rejoignez la communauté pour voir les salons.</p>
          )}
        </>
      ) : null}
      <Link to="/communities" className="mt-8 inline-block text-sm font-semibold text-primary">
        ← Communities
      </Link>
    </section>
  );
}
