"""Central video configuration for the Realm Breach trailer.

Every script (Blender scenes, edit, mix) imports this module so that frame
rate, resolution, palette, safe areas, lenses and seeds stay identical
across the whole production. Pure Python (no numpy) so Blender can import it.
"""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Format -----------------------------------------------------------------
FPS = 30
WIDTH = 1080
HEIGHT = 1920
PREVIEW_SCALE = 0.5            # 540x960 preview renders
HANDLE_FRAMES = 10             # extra frames rendered at each end of a shot

# TikTok UI safe area (pixels at full resolution): captions / buttons / username
SAFE_TOP = 220
SAFE_BOTTOM = 380
SAFE_RIGHT = 140
SAFE_LEFT = 60
# Main subject stays in the centre third of the width
SUBJECT_X_RANGE = (WIDTH / 3.0, 2.0 * WIDTH / 3.0)

# Subtitles: off-white serif, centred, just above the bottom safe zone
SUBTITLE_FONT = "assets/fonts/Cinzel.ttf"
SUBTITLE_SIZE = 62
SUBTITLE_COLOR = "#EDE6DA"
SUBTITLE_BASELINE_Y = HEIGHT - SAFE_BOTTOM - 46
SUBTITLE_MAX_W = WIDTH - SAFE_LEFT - SAFE_RIGHT - 80

# --- Palette (hex) ----------------------------------------------------------
PALETTE = {
    "void": "#07080A",
    "shadow": "#0B1418",
    "ember": "#FF6A1A",
    "gold": "#F2B544",
    "white_gold": "#FFE9A8",
    "god_steel": "#4A6C8F",
    "god_glow": "#6FA8FF",
    "heaven_white": "#FFF4DC",
    "meadow": "#8DB580",
}

# Loot rarities, in order, with their glow colours.
RARITIES = [
    ("common", "#9A9A9A"),
    ("rare", "#3D7BFF"),
    ("epic", "#A04DFF"),
    ("mythic", "#FF3B3B"),
    ("legendary", "#FF9A1A"),
    ("morbidious", "#6BFF4A"),
    ("god", "#FFE9A8"),
    ("fallen equip", "#1B2A4A"),   # deep navy body, blue glow
]
FALLEN_EQUIP_GLOW = "#6FA8FF"

ENEMY_GLOW = {
    "skeleton": "#FF6A1A",
    "ghost": "#9CC8FF",
    "bad_angel": "#FF2A2A",
    "evil": "#A04DFF",
    "morbidious": "#6BFF4A",
}

# --- Lenses (focal length mm, f-stop) ---------------------------------------
# Sensor: Super-35 width (24.89 mm) used as the *horizontal* sensor size;
# Blender fits the sensor to the larger dimension, which is vertical here, so
# scene scripts set sensor_fit = 'VERTICAL' with a 36 mm sensor height to get
# full-frame-feeling fields of view in portrait.
LENSES = {
    "closeup": (85, 1.8),
    "mid": (50, 2.8),
    "wide": (35, 5.6),
    "scale": (24, 8.0),
}
SENSOR_HEIGHT_MM = 36.0

# --- Hero dimensions --------------------------------------------------------
WARRIOR_HEIGHT_M = 1.9
FALLEN_GOD_HEIGHT_M = WARRIOR_HEIGHT_M * 3.0

# --- Grade ------------------------------------------------------------------
GRAIN_STRENGTH = 7          # ffmpeg noise alls value at full res
VIGNETTE_ANGLE = 0.55       # radians, light vignette
PHASE3_DESAT = 0.35


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_linear(h, alpha=1.0):
    """Hex colour -> linear RGBA tuple for Blender shader inputs."""
    r, g, b = hex_to_rgb(h)
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), alpha)


def seed_for(shot_id):
    """Deterministic seed = hash of the shot ID (stable across runs/platforms)."""
    return int(hashlib.sha1(shot_id.encode("utf-8")).hexdigest()[:8], 16)


def load_timing():
    with open(os.path.join(ROOT, "config", "timing.json")) as f:
        return json.load(f)


def load_timeline():
    with open(os.path.join(ROOT, "edit", "timeline.json")) as f:
        return json.load(f)


def sec_to_frame(t):
    return int(round(t * FPS))
