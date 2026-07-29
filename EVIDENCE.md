# Reproducible evidence

Evidence recorded on 2026-07-29 in isolated Python 3.12 environments. These are
local/offline results, not proof of a public deployment or live B2/GMI use.

## Source checks

```text
python -m ruff check .
All checks passed!

python -m pytest -q
11 passed, 1 dependency deprecation warning

python -m compileall -q src tests
exit code 0
```

## Distribution proof

Final browser-enabled wheel:
`dist-final/provenance_studio-0.1.0-py3-none-any.whl`

SHA-256:
`d85523f4119a046a85c83cd5c3be5d511309aca953026e57a48aa08ab61fb270`

The final wheel was force-installed without project dependencies into the independent
`provenance-clean` environment, whose dependencies had already been resolved
from published packages. The same 11 tests passed there.

The archive was inspected directly: all three browser files and the rights-safe
demonstration image were present; no required package file was missing.

## Workflow proof

Running `provenance-studio-demo` from the installed wheel produced two runs with
the refined run referencing the initial run. Verification was true before an
isolated local byte change, false after the change because the observed SHA-256
no longer matched the manifest, and true after restoration.

## Boundaries

- Docker was not available on the machine, so the image has not been built.
- No public URL, B2 bucket, GMI provider call, Render service, GitHub repository,
  or Devpost submission was created or tested.
- The FastAPI behavior was exercised in-process with its official test client;
  the browser interface was additionally exercised against a loopback-only
  development server. No external system was contacted.

## Browser proof

- Accepted concept and latest implementation were directly compared at desktop.
- Browser QA used 1440 × 1000 desktop and 390 × 844 mobile viewports.
- Generate, refine, parent-linked lineage, verification refresh, image loading,
  and zoom were exercised against the local API.
- Desktop and mobile had zero horizontal overflow; console warnings/errors were
  empty; the final document had one H1 plus header, main, and footer landmarks.
- See `design/FIDELITY_LEDGER.md` for the comparison and exact screenshots.
