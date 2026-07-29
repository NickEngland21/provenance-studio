from __future__ import annotations

from pathlib import Path

import pytest

from provenance_studio.receipts import verify_result
from provenance_studio.storage import LocalFilesystemBackend
from provenance_studio.workflow import create_asset, refine_asset


def test_complete_lineage_and_verification(tmp_path: Path) -> None:
    first = create_asset("Create an accessible campaign image", tmp_path)
    second = refine_asset(first, "Add warmer lighting and copy space", tmp_path)

    first_receipt = verify_result(first, tmp_path)
    second_receipt = verify_result(second, tmp_path)

    assert first_receipt.verified
    assert second_receipt.verified
    assert second.run.parent_run_id == first.run.run_id
    assert second_receipt.parent_run_id == first.run.run_id
    assert second.manifest.manifest_uri
    assert second.run.steps[0].assets[0].url.startswith("file:")


def test_tamper_detection_checks_stored_bytes(tmp_path: Path) -> None:
    result = create_asset("Generate a provenance protected image", tmp_path)
    asset = result.run.steps[0].assets[0]
    backend = LocalFilesystemBackend(tmp_path / "object-store")
    key = backend.key_from_url(asset.url)
    assert key is not None

    backend.put(key, backend.get(key) + b"tampered")
    receipt = verify_result(result, tmp_path)

    assert receipt.manifest_valid
    assert not receipt.assets_valid
    assert not receipt.verified
    assert receipt.assets[0].observed_sha256 != receipt.assets[0].declared_sha256


def test_content_addressing_deduplicates_same_prompt(tmp_path: Path) -> None:
    first = create_asset("A deterministic reusable asset", tmp_path)
    second = create_asset("A deterministic reusable asset", tmp_path)

    first_key = LocalFilesystemBackend(tmp_path / "object-store").key_from_url(
        first.run.steps[0].assets[0].url
    )
    second_key = LocalFilesystemBackend(tmp_path / "object-store").key_from_url(
        second.run.steps[0].assets[0].url
    )
    assert first_key == second_key


def test_empty_prompt_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="prompt"):
        create_asset("   ", tmp_path)


def test_storage_rejects_traversal(tmp_path: Path) -> None:
    backend = LocalFilesystemBackend(tmp_path / "object-store")
    with pytest.raises(ValueError, match="Unsafe"):
        backend.put("../escape", b"no")
