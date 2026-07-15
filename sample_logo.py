"""
Sample N target positions from the logo's dark pixels. The particle swarm
will use these as attraction targets, pulled toward them over the course
of the track. Output: logo_targets.json — list of [x_norm, y_norm] pairs
in [0, 1] coordinates centred so x=0.5,y=0.5 is the image centre.
"""
import sys
import json
from PIL import Image
import numpy as np

SRC = sys.argv[1] if len(sys.argv) > 1 else "logo.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "logo_targets.json"
N = 2200          # match particle count
DARK_THRESHOLD = 380   # R+G+B < this → "dark" pixel (silhouette region)

img = Image.open(SRC).convert("RGB")
arr = np.array(img)
h, w, _ = arr.shape
print(f"image: {w}x{h}")

brightness = arr.sum(axis=2)
mask = brightness < DARK_THRESHOLD
ys, xs = np.where(mask)
print(f"dark pixels: {len(xs)} / {w*h} ({len(xs)/(w*h)*100:.1f}%)")

# uniform-random sample from dark pixels
rng = np.random.default_rng(42)
idx = rng.choice(len(xs), size=N, replace=(N > len(xs)))
sx = xs[idx]
sy = ys[idx]

# normalise to [-1, +1] centred on image centre — easy to transform into canvas coords
x_norm = (sx / w - 0.5) * 2.0
y_norm = (sy / h - 0.5) * 2.0

# Output as compact list of [x, y] pairs
targets = list(zip(x_norm.tolist(), y_norm.tolist()))
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump([[round(x, 4), round(y, 4)] for x, y in targets], fh, separators=(",", ":"))
print(f"wrote: {OUT} ({N} target points)")
