from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.db import DB_PATH, initialize_database
from app.workflow import attempt_action, create_request, get_permit, get_permit_history, list_permits, list_users


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Permit-to-work safety workflow", version="1.0.0", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "database": str(DB_PATH)}


@app.get("/api/users")
async def users() -> list[dict]:
    return list_users()


@app.get("/api/permits")
async def permits(site: str | None = Query(default=None), status: str | None = Query(default=None)) -> dict[str, object]:
    return {"permits": list_permits(site=site, status=status), "count": len(list_permits(site=site, status=status))}


@app.get("/api/permits/{permit_id}")
async def fetch_permit(permit_id: int):
    permit = get_permit(permit_id)
    if permit is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Permit {permit_id} not found."})
    return permit


@app.get("/api/permits/{permit_id}/history")
async def fetch_history(permit_id: int):
    permit = get_permit(permit_id)
    if permit is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Permit {permit_id} not found."})
    return {"permit_id": permit_id, "history": get_permit_history(permit_id)}


@app.post("/api/permits/request")
async def route_request(payload: dict):
    result = create_request(payload)
    if result["success"]:
        return result
    return JSONResponse(status_code=400, content={"ok": False, "error": result["error"]})


@app.post("/api/permits/{permit_id}/approve")
async def route_approve(permit_id: int, payload: dict):
    user_id = str(payload.get("user_id", "")).strip()
    if not user_id:
        return JSONResponse(status_code=400, content={"ok": False, "error": {"code": "INVALID_REQUEST", "message": "A user_id is required."}})
    result = attempt_action(permit_id, "APPROVE", user_id, payload.get("comment", "Approved permit"))
    if result["success"]:
        return result
    return JSONResponse(status_code=400, content={"ok": False, "error": result["error"]})


@app.post("/api/permits/{permit_id}/close")
async def route_close(permit_id: int, payload: dict):
    user_id = str(payload.get("user_id", "")).strip()
    if not user_id:
        return JSONResponse(status_code=400, content={"ok": False, "error": {"code": "INVALID_REQUEST", "message": "A user_id is required."}})
    result = attempt_action(permit_id, "CLOSE", user_id, payload.get("comment", "Closed permit"))
    if result["success"]:
        return result
    return JSONResponse(status_code=400, content={"ok": False, "error": result["error"]})
