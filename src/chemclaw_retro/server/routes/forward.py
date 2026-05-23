"""Forward synthesis prediction — useful both internally (round-trip) and
to the consumer agent for sanity-checking proposed reactions."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ...backends.base import BackendError
from ...backends.remote import RemoteBackend
from ...config import get_settings
from ...schemas import ForwardRequest, ForwardResponse
from ..auth import require_token

router = APIRouter(tags=["reaction"])


@router.post(
    "/reaction/forward",
    response_model=ForwardResponse,
    operation_id="reaction_forward",
    summary="Predict products from a set of reactants",
    dependencies=[Depends(require_token)],
)
async def forward(req: ForwardRequest) -> ForwardResponse:
    settings = get_settings()
    backend = RemoteBackend("forward", settings.forward_url, timeout_s=60.0)
    try:
        products = await backend.forward(req)
    except BackendError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return ForwardResponse(products=products, backend=backend.name)
