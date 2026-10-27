"""One-time: build assets/track.png (bar with fill + number removed) from assets/bar_original.png."""
from PIL import Image, ImageOps

src = Image.open("assets/bar_original.png").convert("RGBA")
out = src.copy()

# 1) erase the baked "54 / 100" (transparent rectangle, bar-PNG pixel coords)
NUM_BOX = (295, 240, 770, 342)
out.paste((0, 0, 0, 0), NUM_BOX)

# 2) replace the baked fill with empty dark track, tiled from a clean stretch
SRC_X0, SRC_X1 = 1320, 1540       # clean dark track (right of the fill)
ROW0, ROW1 = 340, 434             # rows covering outline + glow
DST_X0, DST_X1 = 352, 1190        # where the old fill sits
strip = src.crop((SRC_X0, ROW0, SRC_X1, ROW1))
out.paste(strip.resize((DST_X1 - DST_X0, strip.height), Image.LANCZOS), (DST_X0, ROW0))  # stretch = no seams
out.save("assets/track.png")
print("track.png", out.size)

# ---------- v2 clean-up: no spike, glassy track, no dark fringe ----------
import numpy as np
out = Image.open("assets/track.png").convert("RGBA")
out.paste((0, 0, 0, 0), (140, 300, 349, 485))
out.paste((0, 0, 0, 0), (345, 432, 860, 447))            # leftover blue smear under the outline            # remove the spiky spark + streak on the left
arr = np.asarray(out, dtype=np.float32) / 255.0
rgb, a = arr[..., :3], arr[..., 3]
lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
sat = rgb.max(2) - rgb.min(2)
ix0, ix1, iy0, iy1 = 352, 1688, 359, 424                  # inner track area
inner = np.zeros(a.shape, bool); inner[iy0:iy1, ix0:ix1] = True
# glassy inner track: pale lavender, mostly transparent (keeps a little of the old noise)
dark = np.clip(1 - lum, 0, 1)
rgb[inner] = np.array([0.93, 0.89, 0.96], np.float32)
a[inner] = 0.14 + 0.10 * dark[inner]
# remove the dark blurry fringe around the outline (low-lum, low-saturation pixels outside the track)
fringe = (~inner) & (sat < 0.25)
a[fringe] *= np.clip((lum[fringe] - 0.30) / 0.35, 0, 1)
res = np.concatenate([rgb, a[..., None]], axis=2)
Image.fromarray((np.clip(res, 0, 1) * 255).astype(np.uint8), "RGBA").save("assets/track.png")
print("track.png v2 saved")
