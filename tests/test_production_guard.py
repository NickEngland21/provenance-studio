from __future__ import annotations

import pytest

from provenance_studio.production import LiveModeDisabledError, create_production_asset, readiness


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
