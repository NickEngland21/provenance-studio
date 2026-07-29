# Fidelity and browser QA

Concept: `provenance-studio-concept.png`.
Final desktop render: `implementation-desktop-latest.png` at 1440 × 1000.
Final mobile render: `implementation-mobile-final2.png` at 390 × 844.

## Comparison

| Point | Concept evidence | Browser evidence | Result |
|---|---|---|---|
| Composition | Header plus prompt rail, dominant media, receipt rail, status strip | Same three-region workbench and strip at desktop | Matched |
| Palette | Near-black, warm white, acid-lime verification, cobalt action | Exact locked token family; no glow or glass UI | Matched |
| Typography | Serif product/prompt/verification with compact sans-serif chrome | Georgia plus deliberate Arial and Consolas roles | Matched |
| Media | One premium glass-speaker image is the focal point | Project-owned square image fills the canvas without tint | Matched |
| Lineage | Numbered vertical parent and child entries | Parent-first selectable rows; child selected in cobalt | Matched |
| Receipt | Shield, Verified, ruled metadata facts | Actual manifest and asset hashes from the API | Matched |
| Controls | Generate, access, zoom, download, refine, refresh | All represented and exercised against local API state | Matched |
| Responsive | Desktop must collapse to one column | 390 px rail, media, and receipt widths; zero horizontal overflow | Matched |

## Functional verification

- Generated an initial local asset through the browser.
- Refined it with a second prompt; the selected child receipt contained the
  exact initial run ID as its parent.
- Refreshed verification and observed the passing receipt.
- Exercised zoom from 100% to 110%.
- Confirmed two parent-first lineage entries after a cache-disabled reload.
- Browser console reported no warnings or errors.
- Every input had a label, every image had alt text, every button had an
  accessible name, and header/main/footer landmarks were present.

## Copy diff and deviations

The visible primary-screen copy matches the accepted allowed-copy inventory;
run data and prompts are dynamic by design. The implementation uses the same
information architecture and adds no marketing navigation, badge, fake metric,
or claim. The concept's photoreal media was regenerated as a standalone
project-owned asset rather than cropped from the concept. No material visual
mismatch remains in the inspected desktop or first mobile viewport.
