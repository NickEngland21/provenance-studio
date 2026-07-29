# Provenance Studio design system

Accepted concept: `provenance-studio-concept.png` (generated 2026-07-29).

## Composition

- True near-black shell with a 72 px header and a one-pixel neutral divider.
- Desktop workbench: 380 px prompt/lineage rail, flexible 16:10 media canvas,
  and 350 px verification inspector. Panels are open rails, not nested cards.
- Mobile: header, prompt controls, media, lineage, receipt, then status bar.
- The media image is the visual focal point. Chrome stays restrained.

## Tokens

- Background `#080909`; surface `#111313`; raised `#171919`.
- Primary text `#f4f3ed`; secondary `#a8aaa6`; border `#343735`.
- Verification/primary accent `#c9f52f`; secondary action `#4f7cff`.
- Failure `#ff6b5f`; focus ring `#d8ff58`.
- Radius: 3 px controls, 1 px framed media. No glows or glass effects.
- Spacing scale: 4, 8, 12, 16, 24, 32, 48 px.

## Type

- Product name and prompt/result prose: Georgia, Times New Roman, serif.
- UI chrome: Arial, Helvetica, sans-serif.
- Name 28/32; panel title 18/24; body 15/22; labels 12/18.
- Buttons 15/20, weight 700. Hashes use Consolas monospace at 12/18.

## Components and states

- Header: geometric code-native SVG mark, product name only.
- Prompt: large textarea, full-width acid-lime Generate action, masked access
  token with show/hide control.
- Lineage: vertical rail with selectable numbered rows; current child is cobalt.
- Media: 16:10 object frame, zoom/download controls, cobalt refine action.
- Receipt: refresh action, shield check, semantic pass/fail state, ruled facts.
- Status: Backblaze B2 and Genblaze labels in a single bottom strip.
- All actions have hover, keyboard focus, loading, disabled, and error states.
- Motion is limited to 160 ms state transitions and disabled for reduced motion.

## Allowed primary-screen copy

Provenance Studio; Prompt; Generate; Judge access; Lineage; Refine this version;
Verification receipt; Verified; Run ID; Parent; Provider; Model; Manifest hash;
Asset hash; Backblaze B2; Genblaze; and the entered prompt. Accessible labels may
be more explicit when visually hidden.
