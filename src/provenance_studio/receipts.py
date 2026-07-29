"""Verification receipts for manifests and stored output bytes."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path

from genblaze_core.pipeline.result import PipelineResult
from genblaze_core.storage.base import StorageBackend

from provenance_studio.storage import LocalFilesystemBackend


@dataclass(frozen=True)
class AssetCheck:
    asset_id: str
    storage_key: str | None
    declared_sha256: str | None
    observed_sha256: str | None
    matches: bool


@dataclass(frozen=True)
class VerificationReceipt:
    run_id: str
    parent_run_id: str | None
    manifest_hash: str
    manifest_valid: bool
    assets_valid: bool
    assets: tuple[AssetCheck, ...]

    @property
    def verified(self) -> bool:
        return self.manifest_valid and self.assets_valid

    def as_dict(self) -> dict:
        payload = asdict(self)
        payload["verified"] = self.verified
        return payload


def verify_result(result: PipelineResult, workspace: str | Path) -> VerificationReceipt:
    backend = LocalFilesystemBackend(Path(workspace) / "object-store")
    return verify_result_with_backend(result, backend)


def verify_result_with_backend(
    result: PipelineResult,
    backend: StorageBackend,
) -> VerificationReceipt:
    checks: list[AssetCheck] = []
    for step in result.run.steps:
        for asset in step.assets:
            key = backend.key_from_url(asset.url)
            if key is None or not backend.exists(key):
                observed = None
            else:
                observed = hashlib.sha256(backend.get(key)).hexdigest()
            checks.append(
                AssetCheck(
                    asset_id=asset.asset_id,
                    storage_key=key,
                    declared_sha256=asset.sha256,
                    observed_sha256=observed,
                    matches=bool(asset.sha256 and observed == asset.sha256),
                )
            )
    return VerificationReceipt(
        run_id=result.run.run_id,
        parent_run_id=result.run.parent_run_id,
        manifest_hash=result.manifest.canonical_hash,
        manifest_valid=result.manifest.verify(),
        assets_valid=bool(checks) and all(check.matches for check in checks),
        assets=tuple(checks),
    )
