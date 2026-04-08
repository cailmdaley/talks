#!/usr/bin/env python3
"""Find images in images/ not referenced by any talk, and optionally move them."""

import os
import re
import shutil
import argparse


def find_used_images():
    """Scan all .qmd, .md, .html, .yml, .scss, .css files for images/ references."""
    used = set()
    skip_dirs = {"_site", ".git", "unused_images", "__pycache__"}

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if not f.endswith((".qmd", ".md", ".html", ".yml", ".yaml", ".css", ".scss")):
                continue
            try:
                content = open(os.path.join(root, f)).read()
                for m in re.finditer(r"images/+([^\s\"'\)\}\]>#,]+)", content):
                    used.add(m.group(1).rstrip("."))
            except (OSError, UnicodeDecodeError):
                pass

    return used


def collect_unused(dry_run=False):
    images_folder = "./images"
    unused_folder = "./unused_images"
    used = find_used_images()
    all_imgs = {
        f for f in os.listdir(images_folder) if f not in (".DS_Store", "preview")
    }
    unused = sorted(all_imgs - used)

    if not unused:
        print("All images are referenced.")
        return

    total = sum(os.path.getsize(f"images/{f}") for f in unused)
    print(f"{len(unused)} unused images ({total / 1024 / 1024:.1f} MB):\n")
    for f in unused:
        sz = os.path.getsize(f"images/{f}") / 1024 / 1024
        print(f"  {sz:5.1f} MB  {f}")

    if dry_run:
        print(f"\nDry run — no files moved. Use --move to relocate to {unused_folder}/")
        return

    os.makedirs(unused_folder, exist_ok=True)
    for f in unused:
        src = os.path.join(images_folder, f)
        dst = os.path.join(unused_folder, f)
        shutil.move(src, dst)
        print(f"  moved → {dst}")
    print(f"\nMoved {len(unused)} files to {unused_folder}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find and collect unused images.")
    parser.add_argument(
        "--move", action="store_true", help="Actually move files (default is dry run)"
    )
    args = parser.parse_args()
    collect_unused(dry_run=not args.move)
