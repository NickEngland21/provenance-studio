# Reproducible evidence

Evidence recorded on 2026-07-29 in isolated Python 3.12 environments. These are
local/offline results, not proof of a public deployment or live B2/provider use.

## Source checks

```text
python -m ruff check .
All checks passed!

python -m pytest -q
13 passed, 1 dependency deprecation warning

python -m compileall -q src tests
exit code 0
```

## Distribution proof

Final no-spend-provider wheel:
`dist-nvidia/provenance_studio-0.1.0-py3-none-any.whl`

SHA-256:
`52F6D952C18418EB0A2235749A62EBE906589A5B5D5952FA107F50279027B355`

The final wheel plus both production provider extras was installed into the new
`provenance-nvidia-final` environment. The same 13 tests passed there, dependency
checks passed, and the installed NVIDIA provider constructed with the intended
`black-forest-labs/flux.1-schnell` model without making a network request.

The archive was inspected directly: all three browser files and the rights-safe
demonstration image were present; no required package file was missing.

## Workflow proof

Running `provenance-studio-demo` from the installed wheel produced two runs with
the refined run referencing the initial run. Verification was true before an
isolated local byte change, false after the change because the observed SHA-256
no longer matched the manifest, and true after restoration.

## Boundaries

- Docker was not available on the machine, so the image has not been built.
- The source repository is public at `NickEngland21/provenance-studio`, but the
  NVIDIA fallback changes recorded here are still local and unpublished.
- No public app URL, B2 bucket, generative-provider call, Render service, or
  Devpost submission was created or tested.
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

## Provider fallback proof

- Official hackathon guidance permits providers other than GMI Cloud.
- Backblaze's official multi-provider sample identifies NVIDIA NIM as a no-card
  free route for image, video, and narration.
- Live readiness now defaults to NVIDIA but explicitly supports GMI; unknown
  providers fail closed, and both credential paths remain behind the same live
  enable flag, judge token, B2 requirements, and generation quota.
