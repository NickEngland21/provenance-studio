# Demo-media evidence

Evidence date: 2026-07-29 Europe/London

## Current rough cut

- File: `provenance-studio-demo-draft.mp4`
- SHA-256: `23F484E9F8C0AD3D0ED70C6BA4E5C6E6045C658F552C4A4ABCD030F44381EB7A`
- Runtime: 00:02:20.00
- Picture: H.264 High, 1920 × 1080, progressive, 30 fps, yuv420p
- Sound: AAC LC, 22.05 kHz mono; mean -18.0 dB, peak -1.4 dB
- Captions: embedded English `mov_text` track plus `captions.srt`

## Visual review

Representative frames at 0:02, 0:35, 1:10, 1:40, and 2:15 were extracted
from the encoded MP4 and reviewed together. The title, product workbench,
architecture, tamper proof, and live-insert card are legible at full HD. No
credentials, account emails, browser controls, or third-party marks appear.

## Reproduction

1. Create `narration.wav` from `NARRATION.txt` with an authorized voice.
2. Install Pillow and `imageio-ffmpeg` in an isolated environment.
3. Run `render_draft.py` from the repository root.
4. Inspect the MP4 streams, audio volume, runtime, and representative frames.

## Proof boundary

This is a credential-free rough cut, not the uploadable final competition
video. Scene 9 is visibly labelled `LIVE INSERT`. Replace the parent, child,
receipt, and closing footage with the authorized public NVIDIA/Genblaze/B2 run
and final URLs, regenerate narration/captions if wording changes, then repeat
the complete media QA before upload.
