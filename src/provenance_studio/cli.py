"""Run the reproducible offline vertical slice."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from provenance_studio.receipts import verify_result
from provenance_studio.storage import LocalFilesystemBackend
from provenance_studio.workflow import create_asset, refine_asset


def run_demo(workspace: Path) -> dict:
    first = create_asset(
        "A calm coastal campaign image with accessible contrast and generous copy space",
        workspace,
    )
    second = refine_asset(
        first,
        "Refine the coastal campaign with warmer light, accessible contrast, and copy space",
        workspace,
    )
    before = verify_result(second, workspace)

    asset = second.run.steps[0].assets[0]
    backend = LocalFilesystemBackend(workspace / "object-store")
    key = backend.key_from_url(asset.url)
    if key is None:
        raise RuntimeError("Generated asset was not persisted by the storage backend")
    original_bytes = backend.get(key)
    backend.put(key, original_bytes + b"tamper")
    after = verify_result(second, workspace)
    backend.put(key, original_bytes)
    restored = verify_result(second, workspace)

    payload = {
        "lineage": {
            "initial_run_id": first.run.run_id,
            "refined_run_id": second.run.run_id,
            "refined_parent_run_id": second.run.parent_run_id,
        },
        "before_tamper": before.as_dict(),
        "after_tamper": after.as_dict(),
        "after_restore": restored.as_dict(),
    }
    receipt_path = workspace / "demo-receipt.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(".demo"))
    args = parser.parse_args()
    payload = run_demo(args.workspace.resolve())
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
