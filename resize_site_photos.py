#!/usr/bin/env python
# coding: utf-8

# # Resize field-site photos
# Prepares every photo in images/sites/ for the map popups:
#   1. Web copy: longest side shrunk to 1280 px (~80-300 KB), same file name,
#      so the paths in GEN06_shapefiles.py > FIELD_SITES stay valid. Heavy
#      camera originals are moved to images/sites/original/ (git-ignored).
#   2. Thumbnail: images/sites/thumbs/<same name>, ~10 KB, shown in the popup
#      so it opens instantly; the web copy only loads in the lightbox.
#
# Run from the repo root, after copying new photos into images/sites/:
#     python resize_site_photos.py
# Then commit images/sites/ including thumbs/. Already-processed photos are
# left untouched, so it is safe to re-run.

import os
import shutil

from PIL import Image, ImageOps

PHOTO_DIR = "images/sites"
ORIGINAL_DIR = os.path.join(PHOTO_DIR, "original")
THUMB_DIR = os.path.join(PHOTO_DIR, "thumbs")
MAX_SIDE = 1280             # px, longest side of the web copy (lightbox)
THUMB_SIDE = 240            # px, longest side of the thumbnail (popup, 2x for sharp screens)
KEEP_ORIGINAL_BYTES = 1_500_000   # bigger files are camera originals worth keeping
EXTENSIONS = (".jpg", ".jpeg", ".png")

os.makedirs(ORIGINAL_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)


def _save_jpeg(img, path, quality):
    img.save(path, "JPEG", quality=quality, optimize=True, progressive=True)


for name in sorted(os.listdir(PHOTO_DIR)):
    path = os.path.join(PHOTO_DIR, name)
    if not os.path.isfile(path) or not name.lower().endswith(EXTENSIONS):
        continue

    # exif_transpose: phone photos store rotation as an EXIF flag; apply it so
    # the copies aren't shown sideways once the EXIF data is dropped.
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")

    # --- 1. Web copy ---
    if max(img.size) > MAX_SIDE:
        before = os.path.getsize(path)
        if before > KEEP_ORIGINAL_BYTES:
            original = os.path.join(ORIGINAL_DIR, name)
            if os.path.exists(original):
                # Never overwrite a kept original -- rename one of the two first.
                print(f"SKIP {name}: {original} already exists")
                continue
            shutil.move(path, original)
        img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        # Saved as JPEG under the original name (a .png keeps its name too, so
        # FIELD_SITES paths don't change; browsers detect the real format).
        _save_jpeg(img, path, quality=80)
        print(f"{name}: {before / 1e3:.0f} KB -> {os.path.getsize(path) / 1e3:.0f} KB "
              f"({img.width}x{img.height})")

    # --- 2. Thumbnail (re-made whenever the photo is newer) ---
    thumb = os.path.join(THUMB_DIR, name)
    if not os.path.exists(thumb) or os.path.getmtime(thumb) < os.path.getmtime(path):
        img.thumbnail((THUMB_SIDE, THUMB_SIDE), Image.LANCZOS)
        _save_jpeg(img, thumb, quality=75)
        print(f"  thumbnail {name}: {os.path.getsize(thumb) / 1e3:.0f} KB")
