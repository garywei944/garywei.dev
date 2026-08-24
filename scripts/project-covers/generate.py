#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow==12.3.0"]
# ///

"""Generate deterministic 1280x720 project covers from source art."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
CONFIG_PATH = SCRIPT_DIR / "covers.json"
DEFAULT_SIZE = (1280, 720)
TITLE_SIZE = 108
DESCRIPTION_SIZE = 64


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projects", nargs="*", help="Cover names from covers.json; defaults to all")
    parser.add_argument("--font", type=Path, help="Override the display font")
    return parser.parse_args()


def resolve_font(override: Path | None) -> Path:
    candidates = [
        override,
        Path(os.environ["PROJECT_COVER_FONT"]) if os.environ.get("PROJECT_COVER_FONT") else None,
        Path("/mnt/windows/Windows/Fonts/comicbd.ttf"),
        SCRIPT_DIR / "fonts" / "ComicNeue-Bold.ttf",
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "No cover font found. Pass --font or set PROJECT_COVER_FONT; ComicNeue-Bold.ttf is the supported fallback."
    )


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    lines: list[str] = []
    current: list[str] = []
    for word in text.split():
        candidate = " ".join([*current, word])
        if current and draw.textlength(candidate, font=font) > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def add_left_scrim(image: Image.Image, strength: int = 205) -> None:
    if strength <= 0:
        return
    width, height = image.size
    scrim = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pixels = scrim.load()
    assert pixels is not None
    fade_end = int(width * 0.72)
    for x in range(fade_end):
        progress = x / max(fade_end - 1, 1)
        alpha = round(strength * (1 - progress) ** 1.7)
        for y in range(height):
            pixels[x, y] = (0, 0, 0, alpha)
    image.alpha_composite(scrim)


def create_background(spec: dict[str, Any], size: tuple[int, int]) -> Image.Image:
    if spec.get("background"):
        background_path = SCRIPT_DIR / str(spec["background"])
        background = Image.open(background_path).convert("RGB")
        return ImageOps.fit(background, size, method=Image.Resampling.LANCZOS).convert("RGBA")

    start = ImageColor.getrgb(str(spec.get("background_start", "#050706")))
    end = ImageColor.getrgb(str(spec.get("background_end", "#18211d")))
    gradient = Image.new("RGBA", size)
    pixels = gradient.load()
    assert pixels is not None
    for x in range(size[0]):
        progress = x / max(size[0] - 1, 1)
        color = tuple(round(a + (b - a) * progress) for a, b in zip(start, end, strict=True))
        for y in range(size[1]):
            pixels[x, y] = (*color, 255)
    return gradient


def add_artwork(image: Image.Image, artwork_spec: dict[str, Any]) -> None:
    path = SCRIPT_DIR / str(artwork_spec["path"])
    x, y, width, height = (int(value) for value in artwork_spec["box"])
    source = Image.open(path).convert("RGBA")
    fit = str(artwork_spec.get("fit", "contain"))
    if fit == "cover":
        rendered = ImageOps.fit(source, (width, height), method=Image.Resampling.LANCZOS)
    elif fit == "contain":
        rendered = ImageOps.contain(source, (width, height), method=Image.Resampling.LANCZOS)
    else:
        raise ValueError(f"Unsupported artwork fit: {fit}")

    panel = Image.new("RGBA", (width, height), str(artwork_spec.get("background", "#ffffff")))
    panel.alpha_composite(rendered, ((width - rendered.width) // 2, (height - rendered.height) // 2))
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = int(artwork_spec.get("radius", 24))
    mask_draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
    panel.putalpha(mask)
    image.alpha_composite(panel, (x, y))

    border = artwork_spec.get("border")
    if border:
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((x, y, x + width, y + height), radius=radius, outline=str(border), width=2)


def render_cover(name: str, spec: dict[str, Any], font_path: Path) -> Path:
    size_values = spec.get("size", DEFAULT_SIZE)
    if len(size_values) != 2:
        raise ValueError(f"{name}: size must contain width and height")
    size = (int(size_values[0]), int(size_values[1]))

    output_path = REPO_ROOT / str(spec["output"])
    image = create_background(spec, size)
    add_left_scrim(image, int(spec.get("scrim", 205)))
    if spec.get("artwork"):
        add_artwork(image, spec["artwork"])

    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(str(font_path), TITLE_SIZE)
    description_font = ImageFont.truetype(str(font_path), DESCRIPTION_SIZE)
    title_color = str(spec.get("title_color", "#f2f3ef"))
    left = int(spec.get("left", 86))
    description = spec.get("description")
    title_top = 150 if description else 250

    draw.text((left, title_top), str(spec["title"]), font=title_font, fill=title_color)
    if description:
        wrapped = wrap_text(draw, str(description), description_font, int(spec.get("description_width", 1000)))
        draw.multiline_text(
            (left, 340),
            wrapped,
            font=description_font,
            fill=str(spec.get("description_color", title_color)),
            spacing=10,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, "JPEG", quality=92, subsampling=0, optimize=True, progressive=True, exif=b"")
    with Image.open(output_path) as rendered:
        if rendered.size != size:
            raise RuntimeError(f"{name}: expected {size}, got {rendered.size}")
    return output_path


def main() -> None:
    args = parse_args()
    config = json.loads(CONFIG_PATH.read_text())
    covers = config["covers"]
    selected = args.projects or list(covers)
    unknown = sorted(set(selected) - set(covers))
    if unknown:
        raise SystemExit(f"Unknown cover(s): {', '.join(unknown)}")

    font_path = resolve_font(args.font)
    print(f"font: {font_path}")
    for name in selected:
        output = render_cover(name, covers[name], font_path)
        print(f"generated: {output.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
