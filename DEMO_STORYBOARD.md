# Demonstration storyboard (target: 2 minutes 20 seconds)

## 0:00-0:15 — The problem

Show two visually related campaign assets. Ask: Which is canonical, how are they
related, and can we prove the stored file has not changed?

## 0:15-0:40 — Generate

Open Provenance Studio, enter a concise product-campaign prompt, and generate.
Highlight the run ID, provider, model, and green verification receipt.

## 0:40-1:05 — Refine with lineage

Select the first result, enter a refinement prompt, and generate the child.
Show the parent run ID and the two-item lineage view.

## 1:05-1:35 — Explain the architecture

Use one simple diagram: GMI Cloud produces media, Genblaze records the canonical
workflow, and content-addressed assets plus manifests live in Backblaze B2.
Explain that identical bytes share one storage object.

## 1:35-1:58 — Verify actual storage

Click Verify. Show that the app fetches the B2 object, recomputes its SHA-256,
and compares it with the manifest rather than trusting database metadata.

## 1:58-2:12 — Tamper evidence

Use a pre-recorded isolated demonstration in which one stored byte is changed.
Show verification fail, then restore the asset and show it pass. Never alter the
public production bucket for this scene.

## 2:12-2:20 — Close

End on: “Creative velocity without losing provenance.” Display the public app
URL and repository URL.

## Capture checklist

- Record at 1080p with a large cursor and no secret-bearing browser panels.
- Keep narration under three minutes; add accurate captions.
- Use only self-generated visuals and cleared music, preferably no music.
- Blur or crop account identifiers, tokens, bucket credentials, and headers.
- Replace all placeholder URLs and the draft proof-boundary paragraph only
  after live verification succeeds.
