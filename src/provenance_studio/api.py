"""HTTP API for the Provenance Studio production seam."""

from __future__ import annotations

import os
import secrets
import threading
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from provenance_studio.production import (
    create_production_asset,
    create_production_repository,
    readiness,
)
from provenance_studio.receipts import verify_result_with_backend
from provenance_studio.repository import RunNotFoundError, RunRepository, StorageRunRepository
from provenance_studio.workflow import create_asset, refine_asset


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    parent_run_id: str | None = None


def _summary(result, repository: StorageRunRepository) -> dict:
    receipt = verify_result_with_backend(result, repository.backend)
    step = result.run.steps[0]
    return {
        "run_id": result.run.run_id,
        "parent_run_id": result.run.parent_run_id,
        "prompt": step.prompt,
        "provider": step.provider,
        "model": step.model,
        "asset_url": f"/runs/{result.run.run_id}/asset",
        "receipt": receipt.as_dict(),
    }


def create_app(
    workspace: str | Path = ".app-data",
    *,
    live: bool | None = None,
    access_token: str | None = None,
) -> FastAPI:
    root = Path(workspace).resolve()
    live_mode = readiness().ready if live is None else live
    repository: StorageRunRepository = (
        create_production_repository() if live_mode else RunRepository(root)
    )
    expected_token = (
        access_token
        if access_token is not None
        else os.environ.get("DEMO_ACCESS_TOKEN") if live_mode else None
    )
    generation_limit = max(1, int(os.environ.get("MAX_GENERATIONS_PER_PROCESS", "25")))
    generation_count = 0
    generation_lock = threading.Lock()
    app = FastAPI(
        title="Provenance Studio",
        description="Generate, version, store, and verify tamper-evident AI media.",
        version="0.1.0",
    )
    static_directory = Path(__file__).with_name("static")
    app.mount("/static", StaticFiles(directory=static_directory), name="static")

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self'; "
            "frame-ancestors 'none'"
        )
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if live_mode:
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(static_directory / "index.html")

    @app.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "storage": "backblaze-b2" if live_mode else "local-offline",
            "live_services": live_mode,
        }

    @app.get("/runs")
    def list_runs() -> dict:
        return {"run_ids": repository.list_run_ids()}

    @app.post("/runs")
    def generate(request: GenerateRequest, x_demo_token: str | None = Header(default=None)) -> dict:
        nonlocal generation_count
        if expected_token and (
            x_demo_token is None or not secrets.compare_digest(x_demo_token, expected_token)
        ):
            raise HTTPException(status_code=401, detail="valid demo access token required")
        prompt = request.prompt.strip()
        if not prompt:
            raise HTTPException(status_code=422, detail="prompt must not be blank")
        parent = None
        if request.parent_run_id:
            try:
                parent = repository.load(request.parent_run_id)
            except RunNotFoundError as exc:
                raise HTTPException(status_code=404, detail="parent run not found") from exc
        with generation_lock:
            if generation_count >= generation_limit:
                raise HTTPException(status_code=429, detail="generation quota reached")
            generation_count += 1
        if parent is not None:
            result = (
                create_production_asset(prompt, parent=parent)
                if live_mode
                else refine_asset(parent, prompt, root)
            )
        else:
            result = create_production_asset(prompt) if live_mode else create_asset(prompt, root)
        return _summary(result, repository)

    @app.get("/runs/{run_id}")
    def get_run(run_id: str) -> dict:
        try:
            result = repository.load(run_id)
        except RunNotFoundError as exc:
            raise HTTPException(status_code=404, detail="run not found") from exc
        return _summary(result, repository)

    @app.get("/runs/{run_id}/verify")
    def verify(run_id: str) -> dict:
        try:
            result = repository.load(run_id)
        except RunNotFoundError as exc:
            raise HTTPException(status_code=404, detail="run not found") from exc
        return verify_result_with_backend(result, repository.backend).as_dict()

    @app.get("/runs/{run_id}/asset")
    def asset(run_id: str) -> Response:
        try:
            result = repository.load(run_id)
            payload, media_type = repository.asset_bytes(result)
        except RunNotFoundError as exc:
            raise HTTPException(status_code=404, detail="asset not found") from exc
        return Response(
            content=payload,
            media_type=media_type,
            headers={"Content-Disposition": f'inline; filename="{run_id}.png"'},
        )

    return app
