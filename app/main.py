from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request

from .config import get_settings
from .database import init_db, list_pending_review_items, mark_review_item_reviewed
from .handlers import route_update


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Bale Pharmacy Assistant Bot",
    description="Minimal webhook skeleton for a pharmacy assistant bot.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/local/reviews/pending")
def pending_reviews(request: Request) -> dict[str, list[dict[str, str | int | None]]]:
    client_host = request.client.host if request.client else ""
    if client_host not in {"127.0.0.1", "::1", "localhost", "testclient"}:
        raise HTTPException(status_code=404, detail="Not Found")
    return {"pending_reviews": list_pending_review_items()}


@app.post("/local/reviews/{message_id}/mark-reviewed")
def mark_reviewed(request: Request, message_id: int) -> dict[str, str | int | bool]:
    client_host = request.client.host if request.client else ""
    if client_host not in {"127.0.0.1", "::1", "localhost", "testclient"}:
        raise HTTPException(status_code=404, detail="Not Found")

    result = mark_review_item_reviewed(message_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Not Found")
    return result


@app.post("/webhook/bale/{secret}")
async def bale_webhook(secret: str, request: Request) -> dict[str, Any]:
    settings = get_settings()
    if not settings.bale_webhook_secret:
        raise RuntimeError("BALE_WEBHOOK_SECRET is required for /webhook/bale/{secret}")
    if secret != settings.bale_webhook_secret:
        raise HTTPException(status_code=404, detail="Not Found")
    update = await request.json()
    return route_update(update)
