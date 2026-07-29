# Security

- Never place API keys, B2 application keys, presigned URLs, passwords, or
  personal information in prompts, manifests, logs, receipts, source files, or
  screenshots.
- Production credentials are read only from the deployment environment.
- Use a dedicated B2 bucket and a least-privilege application key scoped to that
  bucket. Do not reuse an account-level master key.
- Live-service execution is disabled unless `PROVENANCE_STUDIO_ENABLE_LIVE` is
  explicitly set to `true` in an authorized deployment.
- Live generation requires a timing-safe `X-Demo-Token` check and is capped per
  process to reduce the risk that a public judge URL exhausts provider credits.
- Local-file ingestion is restricted by Genblaze's file-root controls and the
  storage adapter rejects absolute and parent-traversal keys.
- Report security concerns privately to the repository owner after publication.
