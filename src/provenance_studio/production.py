"""Guarded Backblaze B2 and Genblaze production workflow."""

from __future__ import annotations

import os
from contextlib import nullcontext
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from typing import Any

from genblaze_core import KeyStrategy, Modality, ObjectStorageSink, Pipeline
from genblaze_core.pipeline.result import PipelineResult
from genblaze_s3 import S3StorageBackend

from provenance_studio.repository import StorageRunRepository


class LiveModeDisabledError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProductionReadiness:
    live_enabled: bool
    provider: str
    missing_variables: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return (
            self.live_enabled
            and self.provider in {"nvidia", "gmi"}
            and not self.missing_variables
        )


_REQUIRED_VARIABLES = (
    "B2_BUCKET",
    "B2_KEY_ID",
    "B2_APP_KEY",
    "DEMO_ACCESS_TOKEN",
)

_PROVIDER_KEYS = {"nvidia": "NVIDIA_API_KEY", "gmi": "GMI_API_KEY"}


def readiness(environ: dict[str, str] | None = None) -> ProductionReadiness:
    values = os.environ if environ is None else environ
    enabled = values.get("PROVENANCE_STUDIO_ENABLE_LIVE", "").strip().lower() == "true"
    provider = values.get("GEN_MEDIA_PROVIDER", "nvidia").strip().lower()
    required = (
        (*_REQUIRED_VARIABLES, _PROVIDER_KEYS[provider])
        if provider in _PROVIDER_KEYS
        else _REQUIRED_VARIABLES
    )
    missing = tuple(name for name in required if not values.get(name, "").strip())
    if provider not in _PROVIDER_KEYS:
        missing = (*missing, "GEN_MEDIA_PROVIDER")
    return ProductionReadiness(
        live_enabled=enabled,
        provider=provider,
        missing_variables=missing,
    )


def _create_provider(provider_name: str, output_dir: str | None = None) -> tuple[Any, str]:
    if provider_name == "nvidia":
        from genblaze_nvidia import NvidiaImageProvider

        return (
            NvidiaImageProvider(
                api_key=os.environ["NVIDIA_API_KEY"],
                output_dir=output_dir,
            ),
            os.environ.get("NVIDIA_IMAGE_MODEL", "black-forest-labs/flux.2-klein-4b"),
        )
    if provider_name == "gmi":
        from genblaze_gmicloud import GMICloudImageProvider

        return (
            GMICloudImageProvider(api_key=os.environ["GMI_API_KEY"]),
            os.environ.get("GMI_IMAGE_MODEL", "seedream-5.0-lite"),
        )
    raise LiveModeDisabledError(f"Unsupported live provider: {provider_name}")


def _image_params(model: str) -> dict[str, Any]:
    if model == "black-forest-labs/flux.2-klein-4b":
        # NVIDIA's current low-latency FLUX endpoint accepts native dimensions
        # rather than the older aspect_ratio convenience field.
        return {
            "width": 1392,
            "height": 752,
            "cfg_scale": 1,
            "steps": 4,
            "samples": 1,
        }
    return {"aspect_ratio": "16:9"}


def _create_b2_backend() -> S3StorageBackend:
    """Create a B2 backend compatible with a bucket-scoped application key.

    Backblaze bucket-scoped keys permit object I/O but reject the S3 HeadBucket
    request used by Genblaze's region preflight.  The deployment supplies the
    exact bucket-console region, so skip that incompatible discovery request and
    mark the configured region verified.  Real object operations still fail
    normally if the endpoint or credentials are wrong.
    """

    backend = S3StorageBackend.for_backblaze(
        os.environ["B2_BUCKET"],
        region=os.environ.get("B2_REGION", "us-west-004"),
        key_id=os.environ["B2_KEY_ID"],
        app_key=os.environ["B2_APP_KEY"],
        public_url_base=os.environ.get("B2_PUBLIC_URL_BASE") or None,
        auto_lifecycle=False,
        preflight=False,
    )
    backend._region_verified = True
    return backend


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

    backend = _create_b2_backend()
    sink = ObjectStorageSink(
        backend,
        prefix="provenance-studio",
        key_strategy=KeyStrategy.CONTENT_ADDRESSABLE,
    )
    staging = (
        TemporaryDirectory(prefix="provenance-studio-nvidia-")
        if state.provider == "nvidia"
        else nullcontext(None)
    )
    with staging as output_dir:
        provider, model = _create_provider(state.provider, output_dir)
        pipeline = Pipeline("provenance-studio").metadata(
            application="Provenance Studio",
            environment="production-b2",
            inference_provider=state.provider,
        )
        if parent is not None:
            pipeline.from_result(parent)
        try:
            return pipeline.step(
                provider,
                model=model,
                prompt=prompt.strip(),
                modality=Modality.IMAGE,
                metadata={"workflow": "campaign-asset"},
                **_image_params(model),
            ).run(sink=sink, raise_on_failure=True, progress=False, timeout=180)
        finally:
            close = getattr(provider, "close", None)
            if callable(close):
                close()


def create_production_repository() -> StorageRunRepository:
    state = readiness()
    if not state.ready:
        raise LiveModeDisabledError("Live production repository is not authorized or configured")
    backend = _create_b2_backend()
    return StorageRunRepository(backend)
