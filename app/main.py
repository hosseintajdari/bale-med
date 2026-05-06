from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request

from .config import get_settings
from .database import init_db
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


@app.post("/webhook/bale/{secret}")
async def bale_webhook(secret: str, request: Request) -> dict[str, Any]:
    settings = get_settings()
    if not settings.bale_webhook_secret:
        raise RuntimeError("BALE_WEBHOOK_SECRET is required for /webhook/bale/{secret}")
    if secret != settings.bale_webhook_secret:
        raise HTTPException(status_code=404, detail="Not Found")
    update = await request.json()
    return route_update(update)
