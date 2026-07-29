# Devpost submission package

This document is the exact prepared entry. Replace every bracketed value only
after live evidence exists. Do not submit the proof-boundary notes themselves.

## Project name

Provenance Studio

## Tagline

Generate, refine, store, and verify AI campaign media without losing lineage.

## Short description

Provenance Studio gives every generated campaign asset an inspectable lineage,
a content-addressed canonical copy in Backblaze B2, and a verification receipt
that detects changed bytes instead of trusting metadata alone.

## Inspiration

Creative teams can generate dozens of variants in minutes, but the approved
files often lose the facts needed to answer simple questions: Which prompt and
model created this? Which version did it descend from? Where is the canonical
copy? Has that copy changed since approval? Provenance Studio makes those facts
part of the workflow rather than an after-the-fact spreadsheet.

## What it does

A creator generates an initial campaign image and can refine it into linked
children. Each run displays its provider, model, parent, manifest hash, asset
hash, and current verification state. Media and manifests are stored in
Backblaze B2 under content-addressable keys, so identical bytes share one
durable object. When a reviewer clicks Verify, the app fetches the actual B2
object, recomputes SHA-256, and compares it with the canonical Genblaze record.
A changed byte fails verification; restoring the original bytes passes again.

## How we built it

- Genblaze `Pipeline` orchestrates NVIDIA NIM image generation and produces the
  canonical provenance manifest.
- The selected provider/model is NVIDIA NIM with
  `black-forest-labs/flux.1-schnell`.
- Genblaze's `ObjectStorageSink` and `genblaze-s3` write generated media to a
  private Backblaze B2 bucket using content-addressable object keys.
- A FastAPI service exposes generation, parent-linked refinement, lineage,
  verification, media, health, and OpenAPI routes.
- A responsive same-origin browser workbench presents the workflow without
  persisting its private judge token in browser storage.
- A free Render Docker service hosts the public judge experience; durable state
  remains in B2 rather than Render's ephemeral filesystem.

## Meaningful Backblaze B2 use

B2 is the product's durable system of record, not a backup destination. It
stores the generated asset bytes and the records needed to retrieve and verify
them. Verification re-fetches the B2 object and hashes those bytes. The
content-addressable key strategy deduplicates identical output and makes object
identity independently inspectable.

## Meaningful Genblaze use

Genblaze performs the provider step, captures provider/model/prompt metadata,
links a refinement to its parent run, calculates the canonical manifest, and
hands the output to its B2-compatible storage sink. The app depends on those
orchestration and provenance surfaces rather than merely importing the SDK.

## Challenges

The hardest boundary was proving the stored object rather than only proving a
database row. The workflow therefore resolves the B2 object, streams its bytes,
recomputes SHA-256, and compares the result with the manifest. Another challenge
was preserving local-file safety while accepting inline provider output; NVIDIA
bytes are staged only in a temporary directory before the guarded B2 sink reads
them, and the provider client closes deterministically.

## Accomplishments

- Parent-first lineage survives refinement.
- Identical bytes deduplicate through content-addressable object keys.
- Verification detects an isolated one-byte change and passes again after
  restoration.
- Live inference, storage, and public access remain fail-closed until every
  required secret, the explicit enable flag, and judge token are present.
- A per-process generation quota limits accidental free-tier use.
- The browser interface is responsive, accessible, and contains no secret
  persistence.

## What we learned

Generation provenance is useful only if it stays connected to the durable
asset. A manifest without byte-level re-verification can describe what should
exist but cannot prove what is currently stored. Content addressing plus B2
retrieval makes that distinction visible to ordinary reviewers.

## What's next

Add B2 Event Notifications for asynchronous verification, Object Lock for
approved manifests, organization-level reviewer roles, and exportable approval
bundles for campaign handoff.

## Built with

Backblaze B2, Genblaze, NVIDIA NIM, Python, FastAPI, Pydantic, Pillow, Docker,
Render, JavaScript, HTML, and CSS.

## Links

- Working application: `[FINAL_RENDER_URL]`
- Source repository: `https://github.com/NickEngland21/provenance-studio`
- Demonstration video: `[FINAL_VIDEO_URL]`

## Judge instructions

1. Open `[FINAL_RENDER_URL]`; allow up to one minute for a free-tier cold start.
2. Enter the private judge token supplied in Devpost's testing instructions.
3. Generate an initial image, then select it and create a refinement.
4. Inspect the parent link and click Verify on either result.
5. The public demo is capped at `[FINAL_QUOTA]` generations per process.

## Final evidence gate

- [ ] Public repository contains the NVIDIA fallback commit and is cleanly
  cloneable.
- [ ] The exact public commit passes all tests from a fresh installation.
- [ ] One real NVIDIA parent and one real NVIDIA child are stored in B2.
- [ ] Both display correct provider/model metadata and parent linkage.
- [ ] A public Render URL survives cold-start and authorized generation tests.
- [ ] Verification re-fetches the live B2 object and passes.
- [ ] Final video replaces every `LIVE INSERT` and placeholder URL.
- [ ] Final MP4 is under three minutes, has audible unclipped narration, and
  includes captions.
- [ ] Repository, application, and video URLs are publicly reachable.
- [ ] The user reviews the exact text and performs the legal submission action.
