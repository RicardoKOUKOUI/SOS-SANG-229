"""MESH status + envelope schemas (architecture-ready)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class MeshCapability(BaseModel):
    ble: bool = False
    wifi_direct: bool = False
    nearby: bool = False
    libp2p: bool = False
    native_bridge: bool = False


class MeshStatusRead(BaseModel):
    """Server view of MESH readiness. Web clients still report local capability."""

    mode_supported: list[Literal["ONLINE", "OFFLINE", "MESH"]] = Field(
        default_factory=lambda: ["ONLINE", "OFFLINE"]
    )
    mesh_transport_ready: bool = False
    reason: str
    notes: str
    capability_template: MeshCapability


class MeshEnvelope(BaseModel):
    """Future P2P envelope. Not accepted for delivery until native transport exists."""

    id: UUID
    ttl_hops: int = Field(ge=1, le=16, default=4)
    created_at: datetime
    sender_id: UUID | None = None
    recipient_id: UUID | None = None
    kind: Literal["chat", "relay", "action_sync", "presence"] = "chat"
    payload_b64: str = Field(min_length=1, max_length=32_000)
    dedupe_key: str = Field(min_length=8, max_length=128)
