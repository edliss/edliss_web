#!/usr/bin/env python3
#
#  copy_app_store_badges.py
#  edliss_web
#
#  Created by Ed Khamaiseh on 05/11/2026.
#  Copyright © 2026 Edliss LLC. All rights reserved.
#

"""Copies the App Store badges the site uses into ``assets/badges``.

Apple's full badge sets (every language, SVG and EPS) live outside the site in
``~/Developer/Edliss LLC/Brand Assets/App Store Badges``. Only the SVGs for the languages
the site's pages use are copied, under one naming scheme that every app page shares:

    /assets/badges/<download|pre-order>-<locale>-<black|white>.svg

Black is the badge for light backgrounds, white for dark. Add a language to ``LOCALES`` and
re-run when an app page gains one.
"""

import glob
import os
import shutil

SOURCE = os.path.expanduser("~/Developer/Edliss LLC/Brand Assets/App Store Badges")
DESTINATION = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "badges")

#: Site locale → (folder in the download set, folder in the pre-order set)
LOCALES = {
    "en": ("US", "US-UK"),
    "de": ("DE", "DE"),
    "fr": ("FR", "FR"),
    "es": ("ES", "ES"),
    "es-mx": ("ESMX", "ESMX"),
    "it": ("IT", "IT"),
    "pt-br": ("PTBR", "PTBR"),
    "ja": ("JP", "JP"),
    "ko": ("KR", "KR"),
    "zh-hans": ("CN(SC)", "CNSC"),
    "zh-hant": ("HKTW(TC)", "CNTC"),
}

KINDS = {
    "download": ("Download on the App Store", 0),
    "pre-order": ("Pre-order on the App Store", 1),
}


def find_svg(kind_folder, locale_folder, color):
    tag = "blk" if color == "black" else "wht"
    pattern = os.path.join(SOURCE, kind_folder, glob.escape(locale_folder), "**", "SVG", f"*_{tag}_*.svg")
    matches = glob.glob(pattern, recursive=True)
    if len(matches) != 1:
        raise SystemExit(f"Expected one {color} SVG in {kind_folder}/{locale_folder}, found {len(matches)}")
    return matches[0]


def main():
    os.makedirs(DESTINATION, exist_ok=True)
    wanted = set()
    for locale, folders in LOCALES.items():
        for kind, (kind_folder, index) in KINDS.items():
            for color in ("black", "white"):
                name = f"{kind}-{locale}-{color}.svg"
                shutil.copyfile(find_svg(kind_folder, folders[index], color), os.path.join(DESTINATION, name))
                wanted.add(name)
    for name in os.listdir(DESTINATION):
        if name not in wanted:
            os.remove(os.path.join(DESTINATION, name))
            print(f"removed {name}")
    print(f"{len(wanted)} badges in {os.path.relpath(DESTINATION)}")


if __name__ == "__main__":
    main()
