"""HUB AI assistant — ready-to-wire; no fake replies without a key."""

from __future__ import annotations

import json
from urllib import error, request

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_settings
from app.deps import get_current_user
from app.models.user import User
from app.schemas.hub import AiChatRequest, AiChatResponse, AiStatusRead

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status", response_model=AiStatusRead)
def ai_status() -> AiStatusRead:
    settings = get_settings()
    configured = bool(settings.doxami_ai_api_key.strip())
    if not configured:
        return AiStatusRead(
            configured=False,
            provider=None,
            reason=(
                "DOXAMI_AI_API_KEY is not set. Assistant stays unavailable "
                "(no simulated answers)."
            ),
        )
    return AiStatusRead(
        configured=True,
        provider=settings.doxami_ai_model,
        reason="API key present — chat endpoint will call the configured provider.",
    )


@router.post("/chat", response_model=AiChatResponse)
def ai_chat(
    payload: AiChatRequest,
    _current_user: User = Depends(get_current_user),
) -> AiChatResponse:
    settings = get_settings()
    api_key = settings.doxami_ai_api_key.strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AI provider not configured. Set DOXAMI_AI_API_KEY "
                "(and optional DOXAMI_AI_BASE_URL / DOXAMI_AI_MODEL)."
            ),
        )

    body = {
        "model": settings.doxami_ai_model,
        "messages": [
            {
                "role": "system",
                "content": "You are DOXAMI AI, a concise helpful assistant for the DOXAMI app.",
            },
            {"role": "user", "content": payload.message},
        ],
        "temperature": 0.4,
    }
    req = request.Request(
        f"{settings.doxami_ai_base_url.rstrip('/')}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as resp:  # noqa: S310 — URL from settings
            raw = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI provider HTTP {exc.code}.",
        ) from exc
    except error.URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider unreachable.",
        ) from exc

    try:
        reply = raw["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unexpected AI provider response.",
        ) from exc

    return AiChatResponse(reply=reply, provider=settings.doxami_ai_model)
