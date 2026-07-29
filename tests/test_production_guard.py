from __future__ import annotations

import pytest
from genblaze_s3 import S3StorageBackend

from provenance_studio.production import (
    LiveModeDisabledError,
    _create_b2_backend,
    _image_params,
    create_production_asset,
    readiness,
)


def test_current_nvidia_model_uses_its_supported_native_shape() -> None:
    assert _image_params("black-forest-labs/flux.2-klein-4b") == {
        "width": 1392,
        "height": 752,
        "cfg_scale": 1,
        "steps": 4,
        "samples": 1,
    }
    assert _image_params("black-forest-labs/flux.1-schnell") == {
        "aspect_ratio": "16:9"
    }


def test_readiness_never_exposes_secret_values() -> None:
    values = {
        "PROVENANCE_STUDIO_ENABLE_LIVE": "true",
        "B2_BUCKET": "bucket",
        "B2_KEY_ID": "secret-key-id",
        "B2_APP_KEY": "secret-app-key",
        "GEN_MEDIA_PROVIDER": "nvidia",
        "NVIDIA_API_KEY": "secret-nvidia-key",
        "DEMO_ACCESS_TOKEN": "secret-demo-token",
    }
    status = readiness(values)
    assert status.ready
    assert status.provider == "nvidia"
    assert "secret" not in repr(status)


def test_gmi_remains_an_explicit_supported_fallback() -> None:
    values = {
        "PROVENANCE_STUDIO_ENABLE_LIVE": "true",
        "B2_BUCKET": "bucket",
        "B2_KEY_ID": "key-id",
        "B2_APP_KEY": "app-key",
        "GEN_MEDIA_PROVIDER": "gmi",
        "GMI_API_KEY": "gmi-key",
        "DEMO_ACCESS_TOKEN": "demo-token",
    }
    status = readiness(values)
    assert status.ready
    assert status.provider == "gmi"


def test_unknown_provider_fails_readiness() -> None:
    values = {
        "PROVENANCE_STUDIO_ENABLE_LIVE": "true",
        "B2_BUCKET": "bucket",
        "B2_KEY_ID": "key-id",
        "B2_APP_KEY": "app-key",
        "GEN_MEDIA_PROVIDER": "unknown",
        "DEMO_ACCESS_TOKEN": "demo-token",
    }
    status = readiness(values)
    assert not status.ready
    assert status.missing_variables == ("GEN_MEDIA_PROVIDER",)


def test_live_workflow_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "PROVENANCE_STUDIO_ENABLE_LIVE",
        "B2_BUCKET",
        "B2_KEY_ID",
        "B2_APP_KEY",
        "GEN_MEDIA_PROVIDER",
        "NVIDIA_API_KEY",
        "GMI_API_KEY",
        "DEMO_ACCESS_TOKEN",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(LiveModeDisabledError, match="disabled"):
        create_production_asset("This must not contact a live service")


def test_bucket_scoped_b2_key_skips_incompatible_head_bucket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeBackend:
        _region_verified = False

    backend = FakeBackend()
    captured: dict[str, object] = {}

    def fake_for_backblaze(*args: object, **kwargs: object) -> FakeBackend:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return backend

    monkeypatch.setenv("B2_BUCKET", "bucket")
    monkeypatch.setenv("B2_REGION", "eu-central-003")
    monkeypatch.setenv("B2_KEY_ID", "key-id")
    monkeypatch.setenv("B2_APP_KEY", "app-key")
    monkeypatch.setattr(S3StorageBackend, "for_backblaze", fake_for_backblaze)

    assert _create_b2_backend() is backend
    assert captured["args"] == ("bucket",)
    assert captured["kwargs"] == {
        "region": "eu-central-003",
        "key_id": "key-id",
        "app_key": "app-key",
        "public_url_base": None,
        "auto_lifecycle": False,
        "preflight": False,
    }
    assert backend._region_verified is True
    
