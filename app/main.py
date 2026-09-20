from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import parse_qs

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from .config import get_settings
from .database import (
    get_message_stats,
    init_db,
    list_pending_review_items,
    list_shadow_review_items,
    mark_review_item_reviewed,
    upsert_shadow_review_annotation,
)
from .handlers import route_update
from .shadow_review import (
    ShadowReviewAnnotationPayload,
    clamp_shadow_review_limit,
    form_to_annotation_input,
    payload_to_annotation_input,
)
from .shadow_review_ui import build_shadow_review_ui_page

LOCAL_REVIEW_CLIENT_HOSTS = {"127.0.0.1", "::1", "localhost", "testclient"}
FORWARDED_CLIENT_HEADERS = {"forwarded", "x-forwarded-for", "x-real-ip"}


def require_local_review_request(request: Request) -> None:
    client_host = request.client.host if request.client else ""
    # Reverse proxies connect from loopback, so forwarded client headers mean
    # the request is not a direct local operator request.
    has_forwarded_client = any(request.headers.get(header) for header in FORWARDED_CLIENT_HEADERS)
    if has_forwarded_client or client_host not in LOCAL_REVIEW_CLIENT_HOSTS:
        raise HTTPException(status_code=404, detail="Not Found")


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


@app.get("/api/v1/rare-medicines/search")
def search_rare_medicines(
    q: str | None = None,
    province: str | None = None,
    category: str | None = None,
    scarcity_level: str | None = None,
    supply_status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    from .rare_medicine import get_rare_medicine_service

    service = get_rare_medicine_service()
    result = service.search(
        query=q,
        province=province,
        category=category,
        scarcity_level=scarcity_level,
        supply_status=supply_status,
        limit=limit,
        offset=offset,
    )
    return result.to_dict()


@app.get("/api/v1/rare-medicines/categories")
def list_rare_medicine_categories() -> dict[str, list[str]]:
    from .rare_medicine import get_rare_medicine_service

    service = get_rare_medicine_service()
    return {"categories": service.list_categories()}


@app.get("/api/v1/rare-medicines/pharmacies")
def list_rare_medicine_pharmacies(province: str | None = None) -> dict[str, list[dict[str, str]]]:
    from .rare_medicine import get_rare_medicine_service

    service = get_rare_medicine_service()
    return {"pharmacies": service.list_pharmacies(province)}


@app.get("/api/v1/rare-medicines/{medicine_id}")
def get_rare_medicine_detail(medicine_id: str) -> dict[str, Any]:
    from .rare_medicine import get_rare_medicine_service

    service = get_rare_medicine_service()
    item = service.get_by_id(medicine_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Rare medicine not found")
    return item.to_dict()


@app.get("/local/rare-medicines/summary")
def local_rare_medicines_summary(request: Request) -> dict[str, Any]:
    require_local_review_request(request)
    from .rare_medicine import get_rare_medicine_service

    service = get_rare_medicine_service()
    return {
        "total_rare_medicines": service.total_count,
        "categories": service.list_categories(),
        "provinces": service.list_provinces(),
    }


@app.get("/local/reviews/pending")
def pending_reviews(request: Request) -> dict[str, list[dict[str, str | int | None]]]:
    require_local_review_request(request)
    return {"pending_reviews": list_pending_review_items()}


@app.get("/local/reviews/stats")
def review_stats(request: Request) -> dict[str, int]:
    require_local_review_request(request)
    return get_message_stats()


@app.post("/local/reviews/{message_id}/mark-reviewed")
def mark_reviewed(request: Request, message_id: int) -> dict[str, str | int | bool]:
    require_local_review_request(request)

    result = mark_review_item_reviewed(message_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Not Found")
    return result


@app.get("/local/shadow-reviews")
def shadow_reviews(request: Request, limit: int = 50) -> dict[str, Any]:
    require_local_review_request(request)
    safe_limit = clamp_shadow_review_limit(limit)
    items = list_shadow_review_items(safe_limit)
    return {
        "shadow_reviews": items,
        "count": len(items),
        "limit": safe_limit,
    }


@app.get("/local/shadow-reviews/ui", response_class=HTMLResponse)
def shadow_reviews_ui(request: Request, limit: int = 50, saved: int | None = None) -> HTMLResponse:
    require_local_review_request(request)
    safe_limit = clamp_shadow_review_limit(limit)
    items = list_shadow_review_items(safe_limit)
    html_page = build_shadow_review_ui_page(items, limit=safe_limit, saved_message_id=saved)
    return HTMLResponse(content=html_page)


@app.post("/local/shadow-reviews/{message_id}/annotate", response_model=None)
async def annotate_shadow_review(
    request: Request, message_id: int
) -> dict[str, Any] | RedirectResponse:
    require_local_review_request(request)

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body_json = await request.json()
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc
        try:
            payload = ShadowReviewAnnotationPayload.model_validate(body_json)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        annotation_input = payload_to_annotation_input(payload)
        redirect_after_save = False
    else:
        body = await request.body()
        parsed_form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        form_data = {key: values[0] if values else "" for key, values in parsed_form.items()}
        try:
            annotation_input = form_to_annotation_input(form_data)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        redirect_after_save = form_data.get("redirect_to_ui") == "1"

    result = upsert_shadow_review_annotation(
        message_id,
        needs_review_ok=annotation_input.needs_review_ok,
        drug_name_ok=annotation_input.drug_name_ok,
        corrected_drug_name=annotation_input.corrected_drug_name,
        owner_notes=annotation_input.owner_notes,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Not Found")

    if redirect_after_save:
        return RedirectResponse(
            url=f"/local/shadow-reviews/ui?saved={message_id}",
            status_code=303,
        )
    return result


@app.post("/webhook/bale/{secret}")
async def bale_webhook(secret: str, request: Request) -> dict[str, Any]:
    settings = get_settings()
    if not settings.bale_webhook_secret:
        raise HTTPException(
            status_code=503,
            detail="BALE_WEBHOOK_SECRET is not configured. Copy .env.example to .env and set a webhook secret.",
        )
    if secret != settings.bale_webhook_secret:
        raise HTTPException(status_code=404, detail="Not Found")
    try:
        update = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc
    if not isinstance(update, dict):
        raise HTTPException(status_code=400, detail="Webhook payload must be a JSON object")
    return route_update(update)
