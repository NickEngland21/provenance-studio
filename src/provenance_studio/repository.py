"""Durable local run repository used by the offline and API layers."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from uuid import UUID

from genblaze_core.models.manifest import parse_manifest
from genblaze_core.pipeline.result import PipelineResult
from genblaze_core.storage.base import StorageBackend

from provenance_studio.storage import LocalFilesystemBackend


class RunNotFoundError(KeyError):
    pass


class StorageRunRepository:
    def __init__(self, backend: StorageBackend) -> None:
        self.backend = backend

    @staticmethod
    def manifest_key(run_id: str) -> str:
        try:
            canonical = str(UUID(run_id))
        except (ValueError, AttributeError) as exc:
            raise RunNotFoundError(run_id) from exc
        if canonical != run_id.lower():
            raise RunNotFoundError(run_id)
        return f"provenance-studio/manifests/{canonical}.json"

    def load(self, run_id: str) -> PipelineResult:
        key = self.manifest_key(run_id)
        if not self.backend.exists(key):
            raise RunNotFoundError(run_id)
        raw = json.loads(self.backend.get(key))
        manifest = parse_manifest(raw)
        if manifest.run.run_id != run_id:
            raise ValueError("Manifest run ID does not match its storage key")
        return PipelineResult(manifest.run, manifest)

    def list_run_ids(self) -> list[str]:
        prefix = "provenance-studio/manifests/"
        try:
            page = self.backend.list(prefix=prefix, max_keys=1000)
        except NotImplementedError:
            return []
        run_ids = []
        for entry in page.entries:
            if not (entry.key.startswith(prefix) and entry.key.endswith(".json")):
                continue
            candidate = PurePosixPath(entry.key).stem
            try:
                self.manifest_key(candidate)
            except RunNotFoundError:
                continue
            run_ids.append(candidate)
        return sorted(run_ids)

    def asset_bytes(self, result: PipelineResult, index: int = 0) -> tuple[bytes, str]:
        assets = [asset for step in result.run.steps for asset in step.assets]
        try:
            asset = assets[index]
        except IndexError as exc:
            raise RunNotFoundError(f"asset {index} for run {result.run.run_id}") from exc
        key = self.backend.key_from_url(asset.url)
        if key is None or not self.backend.exists(key):
            raise RunNotFoundError(f"stored asset {index} for run {result.run.run_id}")
        return self.backend.get(key), asset.media_type


class RunRepository(StorageRunRepository):
    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace).resolve()
        super().__init__(LocalFilesystemBackend(self.workspace / "object-store"))

    def list_run_ids(self) -> list[str]:
        directory = self.workspace / "object-store" / "provenance-studio" / "manifests"
        if not directory.is_dir():
            return []
        run_ids = []
        for path in directory.glob("*.json"):
            if not path.is_file():
                continue
            try:
                self.manifest_key(path.stem)
            except RunNotFoundError:
                continue
            run_ids.append(path.stem)
        return sorted(run_ids)

    def asset_path(self, result: PipelineResult, index: int = 0) -> tuple[Path, str]:
        assets = [asset for step in result.run.steps for asset in step.assets]
        try:
            asset = assets[index]
        except IndexError as exc:
            raise RunNotFoundError(f"asset {index} for run {result.run.run_id}") from exc
        key = self.backend.key_from_url(asset.url)
        if key is None or not self.backend.exists(key):
            raise RunNotFoundError(f"stored asset {index} for run {result.run.run_id}")
        return self.backend.path_for_key(key), asset.media_type
