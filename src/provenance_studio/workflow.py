"""Offline production workflow with the same Genblaze seam used by B2."""

from __future__ import annotations

import hashlib
import tempfile
import uuid
from pathlib import Path

from genblaze_core import Asset, KeyStrategy, Modality, ObjectStorageSink, Pipeline
from genblaze_core.mocks import MockProvider
from genblaze_core.pipeline.result import PipelineResult
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

from provenance_studio.storage import LocalFilesystemBackend


def _render_sample(prompt: str, destination: Path) -> None:
    """Render a deterministic rights-safe sample used only for offline proof."""

    digest = hashlib.sha256(prompt.encode("utf-8")).digest()
    width = height = 1024
    source = Path(__file__).with_name("assets") / "demo-speaker.png"
    with Image.open(source) as base:
        image = ImageOps.fit(base.convert("RGB"), (width, height), method=Image.Resampling.LANCZOS)
    image = ImageEnhance.Color(image).enhance(0.92 + digest[0] / 2550)
    image = ImageEnhance.Brightness(image).enhance(0.96 + digest[1] / 5100)
    draw = ImageDraw.Draw(image, "RGBA")
    accent = (140 + digest[2] % 80, 205 + digest[3] % 50, 30 + digest[4] % 80, 210)
    draw.rectangle((0, height - 5, width, height), fill=accent)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, format="PNG", optimize=True)


def _provider(output_dir: Path) -> MockProvider:
    def asset_factory(step) -> list[Asset]:
        path = output_dir / f"{uuid.uuid4().hex}.png"
        _render_sample(step.prompt or "Untitled media", path)
        payload = path.read_bytes()
        return [
            Asset(
                url=path.resolve().as_uri(),
                media_type="image/png",
                sha256=hashlib.sha256(payload).hexdigest(),
                size_bytes=len(payload),
                width=1024,
                height=1024,
                metadata={"offline_fixture": True, "rights": "generated_by_entry"},
            )
        ]

    return MockProvider(name="provenance-studio-local", assets=asset_factory, cost_usd=0.0)


def _pipeline(prompt: str, workspace: Path, parent: PipelineResult | None) -> PipelineResult:
    workspace = workspace.resolve()
    backend = LocalFilesystemBackend(workspace / "object-store")
    sink = ObjectStorageSink(
        backend,
        prefix="provenance-studio",
        key_strategy=KeyStrategy.CONTENT_ADDRESSABLE,
    )
    pipeline = (
        Pipeline("provenance-studio")
        .preflight(False)
        .metadata(application="Provenance Studio", environment="offline-proof")
    )
    if parent is not None:
        pipeline.from_result(parent)
    # Genblaze deliberately allows file:// transfers only from the system temp
    # directory (or an explicit provider output root). Keep generated staging
    # files in that trusted boundary and remove them after ObjectStorageSink has
    # persisted the bytes.
    with tempfile.TemporaryDirectory(prefix="provenance-studio-") as staging:
        return pipeline.step(
            _provider(Path(staging)),
            model="deterministic-local-image-v1",
            prompt=prompt,
            modality=Modality.IMAGE,
            metadata={"workflow": "campaign-asset"},
        ).run(sink=sink, raise_on_failure=True, progress=False)


def create_asset(prompt: str, workspace: str | Path) -> PipelineResult:
    if not prompt.strip():
        raise ValueError("prompt must not be empty")
    return _pipeline(prompt, Path(workspace), parent=None)


def refine_asset(
    previous: PipelineResult,
    prompt: str,
    workspace: str | Path,
) -> PipelineResult:
    if not prompt.strip():
        raise ValueError("prompt must not be empty")
    return _pipeline(prompt, Path(workspace), parent=previous)
