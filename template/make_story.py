"""Build the two layers of a Black November product STORY (1080x1920).

Usage: python3 template/make_story.py data.json outdir
data.json: {"title","sub","price","old","line","save","when"(optional),"count"(optional),
            "photo_width","photo_height"}
Writes outdir/base.png (1080x1920, empty white card), outdir/badge.png (transparent Save badge)
and outdir/placement.json (where the product photo and the badge go on the 1080x1920 page).
"""
import json, pathlib, subprocess, sys
from PIL import Image

here = pathlib.Path(__file__).resolve().parent
data = json.loads(pathlib.Path(sys.argv[1]).read_text())
out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
tpl = (here / "story.html").read_text()

def shot(mode, target):
    d = dict(data, mode=mode, photo="")
    tmp = here / f"_render_{mode}.html"
    tmp.write_text(tpl.replace("__DATA__", json.dumps(d)))
    extra = ["--default-background-color=00000000"] if mode == "badge" else []
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--allow-file-access-from-files",
                    "--virtual-time-budget=4000", *extra, "--window-size=1080,1920",
                    f"--screenshot={target}", tmp.as_uri()], check=True, capture_output=True)
    tmp.unlink()

shot("base", out / "_base_full.png")
Image.open(out / "_base_full.png").convert("RGB").save(out / "base.png")
(out / "_base_full.png").unlink()
shot("badge", out / "_badge_full.png")
BADGE = (750, 1195, 1060, 1515)
Image.open(out / "_badge_full.png").convert("RGBA").crop(BADGE).save(out / "badge.png")
(out / "_badge_full.png").unlink()

# Product photo: fit inside an 860x580 box centred in the white card (card is x 50-1030, y 350-990).
pw, ph = float(data.get("photo_width", 1080)), float(data.get("photo_height", 1080))
s = min(860 / pw, 700 / ph)
w, h = round(pw * s), round(ph * s)
placement = {
    "base":  {"left": 0, "top": 0, "width": 1080, "height": 1920},
    "photo": {"left": round(540 - w / 2), "top": round(960 - h / 2), "width": w, "height": h},
    "badge": {"left": BADGE[0], "top": BADGE[1], "width": BADGE[2] - BADGE[0], "height": BADGE[3] - BADGE[1]},
    "order": ["base", "photo", "badge"],
}
(out / "placement.json").write_text(json.dumps(placement, indent=1))
print(json.dumps(placement))
