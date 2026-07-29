from __future__ import annotations

import re
import subprocess
import sys
import wave
from pathlib import Path
from textwrap import wrap

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "draft"
WIDTH, HEIGHT = 1920, 1080

SCENES = [
    (12, "Provenance Studio", "Creative velocity without losing provenance", None),
    (
        17,
        "The missing history",
        "Prompts, versions, canonical files, and byte-level trust",
        "design/implementation-empty.png",
    ),
    (
        18,
        "Generate with evidence",
        "Run ID · provider · model · SHA-256 receipt",
        "design/implementation-desktop-final2.png",
    ),
    (
        15,
        "Refine without losing lineage",
        "Every child keeps its parent relationship",
        "design/implementation-desktop-latest.png",
    ),
    (20, "One inspectable workflow", "NVIDIA NIM  →  Genblaze  →  Backblaze B2", None),
    (
        18,
        "Verify the stored bytes",
        "Fetch from B2, recompute SHA-256, compare with the manifest",
        "design/implementation-desktop-final.png",
    ),
    (16, "Tampering becomes visible", "Changed byte: FAIL  ·  Restored bytes: PASS", None),
    (
        15,
        "Production-minded controls",
        "Private judge token · explicit live gate · generation quota",
        "design/implementation-mobile-final2.png",
    ),
    (9, "LIVE INSERT", "Authorized NVIDIA + B2 proof and final public URLs", None),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    path = Path("C:/Windows/Fonts") / name
    return ImageFont.truetype(str(path), size=size)


def fit_image(source: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    x0, y0, x1, y1 = box
    target_w, target_h = x1 - x0, y1 - y0
    scale = min(target_w / source.width, target_h / source.height)
    resized = source.resize(
        (round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS
    )
    canvas = Image.new("RGB", (target_w, target_h), "#10161d")
    canvas.paste(resized, ((target_w - resized.width) // 2, (target_h - resized.height) // 2))
    return canvas


def draw_scene(index: int, title: str, subtitle: str, source_rel: str | None) -> Path:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#0b1117")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 12), fill="#f3b23f")
    draw.text((92, 70), "PROVENANCE STUDIO", font=font(26, True), fill="#f3b23f")
    draw.text((92, 122), f"0{index}", font=font(24, True), fill="#7c8a96")
    draw.text((148, 112), title, font=font(58, True), fill="#f5f2ea")

    subtitle_lines = wrap(subtitle, width=58)
    y = 195
    for line in subtitle_lines:
        draw.text((148, y), line, font=font(30), fill="#aeb9c3")
        y += 42

    if source_rel:
        source = Image.open(ROOT / source_rel).convert("RGB")
        placed = fit_image(source, (148, 300, 1772, 965))
        image.paste(placed, (148, 300))
        draw.rounded_rectangle((142, 294, 1778, 971), radius=20, outline="#33414d", width=3)
    else:
        draw.rounded_rectangle(
            (148, 330, 1772, 910), radius=32, fill="#111b24", outline="#33414d", width=3
        )
        if title == "One inspectable workflow":
            labels = [("NVIDIA NIM", 300), ("GENBLAZE", 785), ("BACKBLAZE B2", 1270)]
            for label, x in labels:
                draw.rounded_rectangle(
                    (x, 540, x + 350, 690), radius=24, fill="#172632", outline="#f3b23f", width=3
                )
                tw = draw.textbbox((0, 0), label, font=font(30, True))[2]
                draw.text((x + (350 - tw) / 2, 594), label, font=font(30, True), fill="#f5f2ea")
            draw.line((650, 615, 785, 615), fill="#f3b23f", width=6)
            draw.line((1135, 615, 1270, 615), fill="#f3b23f", width=6)
        elif title == "Tampering becomes visible":
            draw.text((340, 535), "FAIL", font=font(100, True), fill="#ef6b68")
            draw.text((765, 570), "→ restore →", font=font(34, True), fill="#aeb9c3")
            draw.text((1250, 535), "PASS", font=font(100, True), fill="#65d29b")
        else:
            card = "FINAL LIVE CAPTURE GOES HERE" if title == "LIVE INSERT" else subtitle
            lines = wrap(card, width=34)
            cy = 540
            for line in lines:
                tw = draw.textbbox((0, 0), line, font=font(42, True))[2]
                draw.text(((WIDTH - tw) / 2, cy), line, font=font(42, True), fill="#f5f2ea")
                cy += 58

    draw.text(
        (92, 1015),
        "Genblaze orchestration · Backblaze B2 durability · SHA-256 verification",
        font=font(22),
        fill="#6f7d88",
    )
    path = OUT / f"scene-{index:02d}.png"
    image.save(path, optimize=True)
    return path


def run(command: list[str]) -> None:
    # Arguments are assembled exclusively from fixed local paths and constants.
    subprocess.run(command, check=True)  # noqa: S603


def srt_time(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1_000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_captions(narration: Path) -> Path:
    text = (HERE / "NARRATION.txt").read_text(encoding="utf-8").strip()
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", text) if item.strip()]
    with wave.open(str(narration), "rb") as audio:
        duration = audio.getnframes() / audio.getframerate()
    weights = [max(1, len(sentence.split())) for sentence in sentences]
    total_weight = sum(weights)
    cursor = 0.0
    blocks = []
    for index, (sentence, weight) in enumerate(zip(sentences, weights, strict=True), start=1):
        end = duration if index == len(sentences) else cursor + duration * weight / total_weight
        blocks.append(f"{index}\n{srt_time(cursor)} --> {srt_time(end)}\n{sentence}\n")
        cursor = end
    captions = HERE / "captions.srt"
    captions.write_text("\n".join(blocks), encoding="utf-8")
    return captions


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    clips: list[Path] = []
    for index, (duration, title, subtitle, source) in enumerate(SCENES, start=1):
        frame = draw_scene(index, title, subtitle, source)
        clip = OUT / f"scene-{index:02d}.mp4"
        run(
            [
                ffmpeg,
                "-y",
                "-loop",
                "1",
                "-i",
                str(frame),
                "-t",
                str(duration),
                "-r",
                "30",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(clip),
            ]
        )
        clips.append(clip)

    concat = OUT / "concat.txt"
    concat.write_text("".join(f"file '{clip.as_posix()}'\n" for clip in clips), encoding="utf-8")
    silent = OUT / "provenance-studio-draft-silent.mp4"
    run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(silent)])

    narration = HERE / "narration.wav"
    if not narration.exists():
        print(f"Missing narration: {narration}", file=sys.stderr)
        raise SystemExit(2)
    captions = write_captions(narration)
    final = HERE / "provenance-studio-demo-draft.mp4"
    run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(silent),
            "-i",
            str(narration),
            "-i",
            str(captions),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-af",
            "apad",
            "-c:s",
            "mov_text",
            "-metadata:s:s:0",
            "language=eng",
            "-t",
            "140",
            "-movflags",
            "+faststart",
            str(final),
        ]
    )
    print(final)


if __name__ == "__main__":
    main()
