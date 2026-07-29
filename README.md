# Provenance Studio

Provenance Studio is a production-oriented generative-media workflow that makes
every campaign asset traceable and tamper-evident. Genblaze records generation
lineage and canonical manifests; a B2-compatible object-storage boundary stores
media by content hash so duplicate assets are stored once.

This repository contains the credential-free offline vertical slice and the
complete judge-facing browser workbench.
It creates real local PNG assets, stores them through Genblaze's
`ObjectStorageSink`, links refinements to their parent run, verifies stored bytes
against the manifest, and demonstrates that tampering is detected. The local
backend is deliberately API-compatible with the production B2 seam.

## Reproduce

Use Python 3.11 or newer in an isolated environment, install the project, then:

```text
python -m pytest -q
provenance-studio-demo --workspace .demo
provenance-studio-api --workspace .app-data
```

Expected proof:

- all tests pass;
- `before_tamper.verified` is `true`;
- `after_tamper.verified` is `false`;
- `after_restore.verified` is `true`;
- the refined run's `parent_run_id` equals the initial run ID.

## Production seam

The guarded production path uses `S3StorageBackend.for_backblaze(...)` and the
Genblaze GMI Cloud provider. The same API exposes the workflow to a future
browser client. Credentials remain outside manifests and source control.

The local API binds to `127.0.0.1` by default and provides generation, refinement,
listing, verification, asset download, health, and interactive OpenAPI routes.
Its root route serves the responsive browser application. It makes no
live-service request in offline mode.

The workbench supports prompt generation, parent-linked refinement, selectable
lineage, media zoom/download, and receipt refresh. The access token stays only
in the active browser field and is sent to the same-origin API header; it is not
written to local storage.

## Guarded production mode

`provenance_studio.production` contains the real GMI Cloud → Genblaze →
Backblaze B2 seam. It refuses to initialize either live client unless the
deployment explicitly sets `PROVENANCE_STUDIO_ENABLE_LIVE=true` and provides all
required environment variables. Copy variable names from `.env.example`; never
commit actual values. Live mode is intentionally not enabled during local proof.
Live generation requests require the `X-Demo-Token` header and are limited to
25 generations per process by default. The limit can be lowered with
`MAX_GENERATIONS_PER_PROCESS`; it is a cost guard, not a billing guarantee.

## Deployment

The included Dockerfile and Render Blueprint describe a zero-spend public
deployment backed by B2. See `DEPLOYMENT.md` for the current hosting decision,
limitations, and exact account boundary. Preparing these files does not perform
a deployment or accept any third-party terms.
