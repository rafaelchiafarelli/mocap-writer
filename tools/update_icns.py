#!/usr/bin/env python3
# build resources_mac/icon.icns from trelby/resources/icon*.png; needs the
# icnsutil package (MIT), which is not in the Docker image:
#   pip install icnsutil && tools/update_icns.py
import glob
import os

import icnsutil

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
IN_DIR = os.path.join(ROOT, "trelby", "resources")
OUT_DIR = os.path.join(ROOT, "resources_mac")

img = icnsutil.IcnsFile()
for name in sorted(glob.glob(os.path.join(IN_DIR, "icon*.png"))):
    try:
        img.add_media(file=name)
    except icnsutil.IcnsType.CanNotDetermine:
        print(f"Skipping {name}")
img.write(os.path.join(OUT_DIR, "icon.icns"))
