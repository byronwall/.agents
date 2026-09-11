#!/usr/bin/env python3
"""Build a labeled contact sheet from rendered OpenGraph images."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_item(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("items must use LABEL=PATH")
    label, raw_path = value.split("=", 1)
    if not label.strip() or not raw_path.strip():
        raise argparse.ArgumentTypeError("both LABEL and PATH are required")
    return label.strip(), Path(raw_path).expanduser()


def font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--item", action="append", required=True, type=parse_item, metavar="LABEL=PATH")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--columns", type=int, default=2)
    parser.add_argument("--tile-width", type=int, default=600)
    parser.add_argument("--title", default="OpenGraph preview contact sheet")
    args = parser.parse_args()

    if args.columns < 1 or args.tile_width < 100:
        parser.error("columns must be positive and tile-width must be at least 100")

    loaded: list[tuple[str, Image.Image, Path]] = []
    for label, path in args.item:
        if not path.is_file():
            parser.error(f"image does not exist: {path}")
        try:
            image = Image.open(path).convert("RGB")
        except Exception as error:
            parser.error(f"cannot read {path}: {error}")
        if image.width < 1 or image.height < 1:
            parser.error(f"image has empty dimensions: {path}")
        loaded.append((label, image, path))

    padding, gap, header_height, label_height = 36, 28, 68, 48
    ratios = [image.height / image.width for _, image, _ in loaded]
    tile_height = round(args.tile_width * max(ratios))
    rows = math.ceil(len(loaded) / args.columns)
    width = padding * 2 + args.columns * args.tile_width + (args.columns - 1) * gap
    height = padding * 2 + header_height + rows * (tile_height + label_height) + (rows - 1) * gap

    sheet = Image.new("RGB", (width, height), "#e7ecf2")
    draw = ImageDraw.Draw(sheet)
    draw.text((padding, padding), args.title, fill="#141b2b", font=font(30))
    draw.text(
        (padding, padding + 39),
        f"{len(loaded)} real rendered image responses",
        fill="#68758a",
        font=font(15),
    )

    for index, (label, image, path) in enumerate(loaded):
        row, column = divmod(index, args.columns)
        left = padding + column * (args.tile_width + gap)
        top = padding + header_height + row * (tile_height + label_height + gap)
        scale = min(args.tile_width / image.width, tile_height / image.height)
        resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
        frame = Image.new("RGB", (args.tile_width, tile_height), "white")
        frame.paste(resized, ((args.tile_width - resized.width) // 2, (tile_height - resized.height) // 2))
        sheet.paste(frame, (left, top))
        draw.text((left + 2, top + tile_height + 13), label, fill="#3d4657", font=font(17))
        print(f"{label}: {image.width}x{image.height} <- {path}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output, format="PNG", optimize=True)
    print(f"contact sheet: {width}x{height} -> {args.output}")


if __name__ == "__main__":
    main()
