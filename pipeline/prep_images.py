"""Stage 1: resize -> remove background (rembg) -> flatten onto neutral gray."""
import argparse
from pathlib import Path
from PIL import Image
from rembg import remove, new_session

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("dst")
ap.add_argument("--model", default="isnet-general-use")
ap.add_argument("--max-side", type=int, default=1600)
a = ap.parse_args()

src, dst = Path(a.src), Path(a.dst)
dst.mkdir(parents=True, exist_ok=True)
session = new_session(a.model)

exts = {".jpg", ".jpeg", ".png"}
files = sorted(p for p in src.iterdir() if p.suffix.lower() in exts)
print(f"Found {len(files)} images in {src}")

for i, p in enumerate(files, 1):
    im = Image.open(p).convert("RGB")
    im.thumbnail((a.max_side, a.max_side))          # downscale; keeps aspect ratio
    cut = remove(im, session=session).convert("RGBA")  # background removed
    bg = Image.new("RGBA", cut.size, (128, 128, 128, 255))
    Image.alpha_composite(bg, cut).convert("RGB").save(dst / f"{p.stem}.jpg", quality=95)
    print(f"[{i}/{len(files)}] {p.name}")