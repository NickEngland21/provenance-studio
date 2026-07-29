"""Local storage adapter matching the Genblaze B2 storage boundary."""

from __future__ import annotations

import os
import uuid
from pathlib import Path, PurePosixPath
from typing import BinaryIO
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

from genblaze_core.storage.base import StorageBackend


class LocalFilesystemBackend(StorageBackend):
    """A deterministic, credential-free backend for development and tests.

    Production swaps this class for ``S3StorageBackend.for_backblaze`` while
    retaining the same ``ObjectStorageSink`` and key layout.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _normalise_key(key: str) -> str:
        candidate = PurePosixPath(key.replace("\\", "/"))
        if candidate.is_absolute() or not candidate.parts or ".." in candidate.parts:
            raise ValueError(f"Unsafe storage key: {key!r}")
        return candidate.as_posix()

    def _path(self, key: str) -> Path:
        normalised = self._normalise_key(key)
        path = (self.root / Path(*PurePosixPath(normalised).parts)).resolve()
        path.relative_to(self.root)
        return path

    def path_for_key(self, key: str) -> Path:
        """Return a validated local path for an existing storage key."""

        return self._path(key)

    def put(
        self,
        key: str,
        data: bytes | BinaryIO,
        *,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
        extra_args: dict | None = None,
    ) -> str:
        del content_type, metadata, extra_args
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = data if isinstance(data, bytes) else data.read()
        temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
        temporary.write_bytes(payload)
        os.replace(temporary, path)
        return self._normalise_key(key)

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self._path(key).is_file()

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)

    def get_url(self, key: str, *, expires_in: int = 3600) -> str:
        del expires_in
        return self.get_durable_url(key)

    def get_durable_url(self, key: str) -> str:
        return self._path(key).as_uri()

    def key_from_url(self, url: str) -> str | None:
        parsed = urlparse(url)
        if parsed.scheme != "file" or parsed.netloc not in {"", "localhost"}:
            return None
        decoded = url2pathname(unquote(parsed.path))
        candidate = Path(decoded).resolve()
        try:
            relative = candidate.relative_to(self.root)
        except ValueError:
            return None
        return PurePosixPath(*relative.parts).as_posix()
