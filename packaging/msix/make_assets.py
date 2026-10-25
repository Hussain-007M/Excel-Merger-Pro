"""Generate required MSIX image assets from the existing application icon."""

from pathlib import Path
import sys

from PIL import Image


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python make_assets.py <icon.ico> <assets-output-folder>")

    icon = Path(sys.argv[1])
    assets = Path(sys.argv[2])
    assets.mkdir(parents=True, exist_ok=True)

    with Image.open(icon) as image:
        if hasattr(image, "ico"):
            sizes = image.ico.sizes()
            source = image.ico.getimage(max(sizes, key=lambda value: value[0] * value[1]))
        else:
            source = image.copy()
        source = source.convert("RGBA")

    for name, size in (
        ("StoreLogo.png", 50),
        ("Square44x44Logo.png", 44),
        ("Square150x150Logo.png", 150),
    ):
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        thumbnail = source.copy()
        thumbnail.thumbnail((size, size), Image.Resampling.LANCZOS)
        canvas.alpha_composite(thumbnail, ((size - thumbnail.width) // 2, (size - thumbnail.height) // 2))
        canvas.save(assets / name, format="PNG")


if __name__ == "__main__":
    main()
