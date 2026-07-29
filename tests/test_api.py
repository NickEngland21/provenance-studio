from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from provenance_studio.api import create_app


def test_api_generate_refine_verify_and_serve_asset(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))

    index = client.get("/")
    assert index.status_code == 200
    assert "Provenance Studio" in index.text
    assert "default-src 'self'" in index.headers["content-security-policy"]
    assert client.get("/static/app.js").status_code == 200

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["live_services"] is False

    initial = client.post("/runs", json={"prompt": "Accessible product campaign"})
    assert initial.status_code == 200
    first = initial.json()
    assert first["receipt"]["verified"] is True

    refined = client.post(
        "/runs",
        json={"prompt": "Warmer accessible product campaign", "parent_run_id": first["run_id"]},
    )
    assert refined.status_code == 200
    second = refined.json()
    assert second["parent_run_id"] == first["run_id"]
    assert second["receipt"]["verified"] is True

    verify = client.get(f"/runs/{second['run_id']}/verify")
    assert verify.status_code == 200
    assert verify.json()["verified"] is True

    asset = client.get(f"/runs/{second['run_id']}/asset")
    assert asset.status_code == 200
    assert asset.headers["content-type"] == "image/png"
    assert asset.content.startswith(b"\x89PNG")

    listed = client.get("/runs")
    assert set(listed.json()["run_ids"]) == {first["run_id"], second["run_id"]}


def test_api_returns_clear_not_found(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    assert client.get("/runs/missing").status_code == 404
    assert client.get("/runs/..%5C..%5Csecret").status_code == 404
    assert client.post("/runs", json={"prompt": "x", "parent_run_id": "missing"}).status_code == 404


def test_api_optional_demo_token_protects_generation(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path, access_token="judge-code"))  # noqa: S106

    denied = client.post("/runs", json={"prompt": "should be denied"})
    allowed = client.post(
        "/runs",
        json={"prompt": "authorized judge generation"},
        headers={"X-Demo-Token": "judge-code"},
    )

    assert denied.status_code == 401
    assert allowed.status_code == 200


def test_api_generation_quota_is_fail_closed(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MAX_GENERATIONS_PER_PROCESS", "1")
    client = TestClient(create_app(tmp_path))

    assert client.post("/runs", json={"prompt": "first"}).status_code == 200
    assert client.post("/runs", json={"prompt": "second"}).status_code == 429
