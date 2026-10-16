#!/usr/bin/env python
# coding: utf-8

# # Resize field-site photos
# Shrinks every heavy photo in images/sites/ to web size (longest side 1600 px,
# ~150-600 KB) so the map popups/lightbox load fast. The full-resolution file
# is moved to images/sites/original/ (git-ignored) and the web copy keeps the
# same file name, so the paths in GEN06_shapefiles.py > FIELD_SITES stay valid.
#
# Run from the repo root, after copying new photos into images/sites/:
#     python resize_site_photos.py
# Photos that are already small are left untouched, so it is safe to re-run.

import os
import shutil

from PIL import Image, ImageOps

PHOTO_DIR = "images/sites"
ORIGINAL_DIR = os.path.join(PHOTO_DIR, "original")
MAX_SIDE = 1600           # px, longest side of the web copy
MIN_BYTES = 800_000       # files smaller than this are considered done
                          # (web copies come out at ~100-600 KB)
EXTENSIONS = (".jpg", ".jpeg", ".png")

os.makedirs(ORIGINAL_DIR, exist_ok=True)

for name in sorted(os.listdir(PHOTO_DIR)):
    path = os.path.join(PHOTO_DIR, name)
    if not name.lower().endswith(EXTENSIONS) or os.path.getsize(path) < MIN_BYTES:
        continue

    original = os.path.join(ORIGINAL_DIR, name)
    if os.path.exists(original):
        # Never overwrite a kept original -- rename one of the two first.
        print(f"SKIP {name}: {original} already exists")
        continue
    shutil.move(path, original)

    # exif_transpose: phone photos store rotation as an EXIF flag; apply it so
    # the web copy isn't shown sideways once the EXIF data is dropped.
    img = ImageOps.exif_transpose(Image.open(original)).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    # Saved as JPEG under the original name (a .png keeps its name too, so
    # FIELD_SITES paths don't change; browsers detect the real format).
    img.save(path, "JPEG", quality=82, optimize=True, progressive=True)

    print(f"{name}: {os.path.getsize(original) / 1e6:.1f} MB -> "
          f"{os.path.getsize(path) / 1e3:.0f} KB ({img.width}x{img.height})")
