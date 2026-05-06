from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request

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


@app.post("/webhook/bale")
async def bale_webhook(request: Request) -> dict[str, Any]:
    update = await request.json()
    return route_update(update)
