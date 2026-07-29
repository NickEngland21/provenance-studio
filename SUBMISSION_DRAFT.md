# Submission draft

## Name

Provenance Studio

## One-line summary

Generate, refine, store, and verify AI campaign media with inspectable lineage
and tamper-evident assets powered by Genblaze and Backblaze B2.

## Problem

Creative teams can generate many media variants quickly, but the final files
often lose the facts needed to answer basic questions: which prompt produced
this asset, which version did it descend from, where is the canonical copy, and
has that copy changed since approval?

## Solution

Provenance Studio turns each generation into a traceable workflow record. It
stores content-addressed media in Backblaze B2, persists a canonical Genblaze
manifest, links refinements to their parent, and recomputes the stored asset
hash when anyone requests a verification receipt. Reusing identical bytes does
not create duplicate objects.

## Meaningful use of sponsor technology

- Genblaze runs the provider workflow and produces canonical run manifests.
- Its object-storage sink stores assets by content hash and records lineage.
- Backblaze B2 is the durable system of record for both media and manifests.
- Verification fetches the actual B2 object and compares it with the recorded
  digest, so B2 is part of the product behavior rather than a passive backup.

## Demonstrable flow

1. Generate an initial campaign image.
2. Refine it into a linked second version.
3. Inspect both manifests and their parent-child relationship.
4. Verify the stored bytes and receive a passing receipt.
5. Demonstrate a changed object failing verification, then restore it.

## Safety and cost controls

Live integrations are disabled unless explicitly enabled with complete secrets.
Generation requires a private judge token and is capped per process. Secrets are
never placed in source, manifests, or browser-visible responses.

## Current proof boundary

The offline workflow and HTTP API are tested. The B2/GMI production seam and
Render deployment configuration are implemented but have not been exercised
against live services. Replace this paragraph with live evidence before final
submission.
