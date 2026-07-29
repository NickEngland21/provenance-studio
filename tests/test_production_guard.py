from __future__ import annotations

import pytest

from provenance_studio.production import LiveModeDisabledError, create_production_asset, readiness


def test_readiness_never_exposes_secret_values() -> None:
    values = {
        "PROVENANCE_STUDIO_ENABLE_LIVE": "true",
        "B2_BUCKET": "bucket",
        "B2_KEY_ID": "secret-key-id",
        "B2_APP_KEY": "secret-app-key",
        "GMI_API_KEY": "secret-gmi-key",
        "DEMO_ACCESS_TOKEN": "secret-demo-token",
    }
    status = readiness(values)
    assert status.ready
    assert "secret" not in repr(status)


def test_live_workflow_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "PROVENANCE_STUDIO_ENABLE_LIVE",
        "B2_BUCKET",
        "B2_KEY_ID",
        "B2_APP_KEY",
        "GMI_API_KEY",
        "DEMO_ACCESS_TOKEN",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(LiveModeDisabledError, match="disabled"):
        create_production_asset("This must not contact a live service")
