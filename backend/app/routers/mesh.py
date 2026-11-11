"""MESH status endpoints — ready-to-wire, no fake P2P."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.mesh import MeshCapability, MeshEnvelope, MeshStatusRead

router = APIRouter(prefix="/mesh", tags=["mesh"])


@router.get("/status", response_model=MeshStatusRead)
def mesh_status() -> MeshStatusRead:
    return MeshStatusRead(
        mode_supported=["ONLINE", "OFFLINE"],
        mesh_transport_ready=False,
        reason=(
            "No native MESH transport is configured on this API host. "
            "Browser web clients cannot provide BLE / Wi-Fi Direct / Nearby."
        ),
        notes=(
            "DOXAMI MESH requires a native bridge (or companion) exposing "
            "window.DoxamiNativeMesh / equivalent. Offline IndexedDB sync is NOT MESH."
        ),
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
