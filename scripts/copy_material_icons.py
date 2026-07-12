"""Copy Material Design icons from MkDocs Material to iw-generator."""

import shutil
from pathlib import Path

# Source directory (MkDocs Material installation)
MATERIAL_ICONS = Path("D:/python/Lib/site-packages/material/templates/.icons")

# Destination directory in iw-generator
IW_ICONS = Path("src/iw_generator/themes/.icons")


def copy_icons():
    """Copy all icon sets from MkDocs Material."""
    # Create destination directory
    IW_ICONS.mkdir(parents=True, exist_ok=True)

    # Copy each icon set
    for icon_set in ["material", "octicons", "fontawesome", "simple"]:
        src_dir = MATERIAL_ICONS / icon_set
        dst_dir = IW_ICONS / icon_set

        if src_dir.exists():
            print(f"Copying {icon_set} icons...")
            if dst_dir.exists():
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            count = sum(1 for _ in dst_dir.rglob("*.svg"))
            print(f"  Copied {count} icons to {dst_dir}")

    # Copy our custom icons (iw/*, logo/*, lang/*, etc.)
    print("\nCustom icons will be added separately.")


if __name__ == "__main__":
    copy_icons()
