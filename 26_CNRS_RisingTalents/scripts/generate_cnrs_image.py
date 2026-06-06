#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "openai>=1.86.0",
#   "pillow>=11.0.0",
# ]
# ///

from __future__ import annotations

import argparse
import base64
import os
from pathlib import Path

from openai import OpenAI
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a CNRS slide illustration.")
    parser.add_argument("prompt", type=Path, help="Markdown prompt file.")
    parser.add_argument("output", type=Path, help="Output image path.")
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1.5"),
        help="OpenAI image model ID. Defaults to OPENAI_IMAGE_MODEL or gpt-image-1.5.",
    )
    parser.add_argument("--size", default="1536x1024", help="Image size for GPT image models.")
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    parser.add_argument("--background", default="auto", choices=["auto", "opaque", "transparent"])
    parser.add_argument("--max-width", type=int, default=2000, help="Downscale wider images.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if "OPENAI_API_KEY" not in os.environ:
        raise SystemExit("OPENAI_API_KEY is not set.")

    prompt = args.prompt.read_text(encoding="utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    response = OpenAI().images.generate(
        model=args.model,
        prompt=prompt,
        size=args.size,
        quality=args.quality,
        background=args.background,
        output_format="png",
        n=1,
    )

    image_b64 = response.data[0].b64_json
    if not image_b64:
        raise SystemExit("Image response did not include b64_json.")

    args.output.write_bytes(base64.b64decode(image_b64))

    with Image.open(args.output) as image:
        if image.width > args.max_width:
            height = round(image.height * args.max_width / image.width)
            image = image.resize((args.max_width, height), Image.Resampling.LANCZOS)
        image.save(args.output, optimize=True)

    size_mb = args.output.stat().st_size / (1024 * 1024)
    print(f"Wrote {args.output} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()

