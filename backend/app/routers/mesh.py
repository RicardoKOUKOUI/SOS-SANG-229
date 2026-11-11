"""MESH status endpoints — ready-to-wire, no fake P2P."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.mesh import MeshCapability, MeshEnvelope, MeshStatusRead

router = APIRouter(prefix="/mesh", tags=["mesh"])

_FORCE_KEYS = {"simulate", "ready", "mesh_transport_ready"}


@router.get("/status", response_model=MeshStatusRead)
def mesh_status(request: Request) -> MeshStatusRead:
    forced = any(key in request.query_params for key in _FORCE_KEYS)
    notes = (
        "DOXAMI MESH requires a native bridge (or companion) exposing "
        "window.DoxamiNativeMesh / equivalent. Offline IndexedDB sync is NOT MESH."
    )
    if forced:
        notes += " Query flags cannot enable a transport."
    return MeshStatusRead(
        mode_supported=["ONLINE", "OFFLINE"],
        mesh_transport_ready=False,
        reason=(
            "No native MESH transport is configured on this API host. "
            "Browser web clients cannot provide BLE / Wi-Fi Direct / Nearby."
        ),
        notes=notes,
        capability_template=MeshCapability(),
    )


@router.post("/envelopes", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def accept_envelope(_payload: MeshEnvelope) -> None:
    """Reject delivery until a real transport is wired (honest failure)."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "MESH envelope relay is not active. "
            "Configure a native transport before enabling delivery."
        ),
    )
