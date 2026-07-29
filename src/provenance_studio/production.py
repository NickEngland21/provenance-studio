"""Guarded Backblaze B2 and GMI Cloud production workflow."""

from __future__ import annotations

import os
from dataclasses import dataclass

from genblaze_core import KeyStrategy, Modality, ObjectStorageSink, Pipeline
from genblaze_core.pipeline.result import PipelineResult
from genblaze_s3 import S3StorageBackend

from provenance_studio.repository import StorageRunRepository


class LiveModeDisabledError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProductionReadiness:
    live_enabled: bool
    missing_variables: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return self.live_enabled and not self.missing_variables


_REQUIRED_VARIABLES = (
    "B2_BUCKET",
    "B2_KEY_ID",
    "B2_APP_KEY",
    "GMI_API_KEY",
    "DEMO_ACCESS_TOKEN",
)


def readiness(environ: dict[str, str] | None = None) -> ProductionReadiness:
    values = os.environ if environ is None else environ
    enabled = values.get("PROVENANCE_STUDIO_ENABLE_LIVE", "").strip().lower() == "true"
    missing = tuple(name for name in _REQUIRED_VARIABLES if not values.get(name, "").strip())
    return ProductionReadiness(live_enabled=enabled, missing_variables=missing)


def create_production_asset(
    prompt: str,
    *,
    parent: PipelineResult | None = None,
) -> PipelineResult:
    """Run one real Genblaze image workflow only after an explicit live gate."""

    state = readiness()
    if not state.ready:
        missing = ", ".join(state.missing_variables) or "none"
        raise LiveModeDisabledError(
            "Live production is disabled or incomplete; "
            f"enable flag={state.live_enabled}, missing variables={missing}"
        )
    if not prompt.strip():
        raise ValueError("prompt must not be empty")

    # Imported only beyond the live-authority gate so offline development does
    # not require or initialize a provider connector.
    from genblaze_gmicloud import GMICloudImageProvider

    region = os.environ.get("B2_REGION", "us-west-004")
    backend = S3StorageBackend.for_backblaze(
        os.environ["B2_BUCKET"],
        region=region,
        key_id=os.environ["B2_KEY_ID"],
        app_key=os.environ["B2_APP_KEY"],
        public_url_base=os.environ.get("B2_PUBLIC_URL_BASE") or None,
        auto_lifecycle=False,
    )
    sink = ObjectStorageSink(
        backend,
        prefix="provenance-studio",
        key_strategy=KeyStrategy.CONTENT_ADDRESSABLE,
    )
    provider = GMICloudImageProvider(api_key=os.environ["GMI_API_KEY"])
    pipeline = Pipeline("provenance-studio").metadata(
        application="Provenance Studio", environment="production-b2"
    )
    if parent is not None:
        pipeline.from_result(parent)
    return pipeline.step(
        provider,
        model=os.environ.get("GMI_IMAGE_MODEL", "seedream-5.0-lite"),
        prompt=prompt.strip(),
        modality=Modality.IMAGE,
        aspect_ratio="16:9",
        metadata={"workflow": "campaign-asset"},
    ).run(sink=sink, raise_on_failure=True, progress=False, timeout=180)


def create_production_repository() -> StorageRunRepository:
    state = readiness()
    if not state.ready:
        raise LiveModeDisabledError("Live production repository is not authorized or configured")
    backend = S3StorageBackend.for_backblaze(
        os.environ["B2_BUCKET"],
        region=os.environ.get("B2_REGION", "us-west-004"),
        key_id=os.environ["B2_KEY_ID"],
        app_key=os.environ["B2_APP_KEY"],
        public_url_base=os.environ.get("B2_PUBLIC_URL_BASE") or None,
        auto_lifecycle=False,
    )
    return StorageRunRepository(backend)
