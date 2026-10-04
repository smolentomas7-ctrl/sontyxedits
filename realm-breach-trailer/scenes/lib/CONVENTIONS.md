# Blender production conventions — REALM BREACH trailer

Read this before writing any Blender code for this project.

## Running Blender
- Blender **4.0.2** (Ubuntu apt build, system Python 3.12, numpy available). **EEVEE Legacy** (`BLENDER_EEVEE`), not EEVEE Next.
- No GPU: software GL via Xvfb. Always run headless like this:
  `xvfb-run -a -s "-screen 0 1920x1080x24" blender -b --factory-startup -P <script.py> -- <args>`
- Scripts add the lib folder to `sys.path`:
  `sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))` (adjust for `scenes/tests/`).
- Render cost ≈ 5 s fixed + ~1.2 s per TAA sample per frame at 1080×1920, dominated by shadow maps.
  **Iterate at `scale 0.25–0.5` with 4–8 samples.** Other agents share the 4 CPUs — keep test renders small and few.
- **Budget shadows:** at most 2 shadow-casting lights per shot (key + one). Rims, fills, kickers: `shadow=False`.
  Use `soft_shadows` (already on). Spot lights with volumetrics make god rays — cheap if shadowless, but shadowed spots make shafts through pillars.
- Never wait with `pgrep -f <pattern>` inside a shell command that contains `<pattern>` (it matches itself).

## Coordinates / units
- Metres, Z up. Characters face **−Y** (camera looking at a character's front sits at negative Y).
- Warrior is 1.90 m (rig: `rb_warrior.J`), Fallen God 5.70 m (`rb_god.J`). Rig = FK hierarchy of empties,
  world-aligned at rest; animate with `rotation_euler` (degrees via `rb_warrior.pose`) and the root empty's location/rotation.
- Frame rate 30. Scene frame == video frame (see `scenes/lib/rb_shot.py`).

## Libraries (read the code; do NOT edit these shared files — put new helpers in your own module)
- `rb_core.py` — `reset_scene`, `setup_render(scale, samples, …)`, `world`, `world_gradient`, `camera(name, lens, fstop, focus)`
  (vertical sensor fit, 36 mm sensor height), `look_at`, `light(kind, name, loc, color(hex ok), energy, size, target, shadow, spot_size, blend, volume)`,
  easing (`ease_in_out`, `ease_out`, `ease_in`, `ease_out_back`, `smooth`), `noise1(t, seed)`, `decay_shake`, `rng(shot_id, salt)`,
  `empty`, `parent_keep`, `key_transform`, `hexcol`.
- `rb_mesh.py` — `grid_mesh(rows×cols×3 array, closed_u, caps, skip=fn)`, `tube(p0, p1, radius(t,θ), arc=…)`, `ellipsoid_cap`,
  `finish_plate(thick, bevel, subsurf)`, `dents`, `bake_attributes` (point attrs `wear`, `mud`, `cav` used by materials),
  `curve_tube(polyline, radius)`, `rivets`, `join`, `set_mat`, `add_mod`, `apply_all`.
- `rb_mat.py` — node builder `NB` + `new(name, blend)`; materials `steel`, `chainmail`, `leather`, `cloth`, `emission(name, color, strength, ctrl)`,
  `matte`, `blade`, `stone_god`, `obsidian`, `robe`. Animated controls are Value nodes named `CTRL_<name>`; key them with `rb_mat.key_ctrl(mat, name, frame, value)`.
  Principled BSDF (4.0) sockets: "Base Color", "Metallic", "Roughness", "Specular IOR Level", "Coat Weight", "Sheen Weight",
  "Emission Color", "Emission Strength", "Alpha", "Normal".
- `rb_warrior.py` — `build_warrior(look='late'|'mid'|'early', rings=bool, sword_glow=float)` → `.rig`, `.root`, `.sword`, `.mats`, `.cloths`, `.cape`, `.tabard`.
- `rb_god.py` — `build_god()` → `.rig`, `.root`, `.blade`, `.blade_pivot`, `.halo`, `.halo_pivot`, `.mats` (`stone` has CTRL_ignite/CTRL_glow, `eyes` CTRL_eye_glow, halo mat CTRL_halo).
- `rb_shot.py` — `Shot(id)` reads `edit/timeline.json`, sets up render, frame ranges (`frames_all`, `frames_render`, `key_frame`), `t(f)`, `register_cloth`, `render()`.

## Look (locked — see `assets/characters.md` and `config/video.py` PALETTE)
- Dark-fantasy AAA realism (Elden Ring / LOTR mood), low-key. PBR everywhere: wet cracked stone, obsidian, blackened steel, cloth with thickness. Nothing plastic or toy-like, nothing "Roblox".
- Palette: void #07080A, teal-black shadows #0B1418, ember #FF6A1A (warrior rim, eyes, blade crack), gold #F2B544 → #FFE9A8, Fallen-God steel blue #4A6C8F / glow #6FA8FF, heaven warm white #FFF4DC, meadow green #8DB580. Rarity glows in config/video.py.
- Volumetric haze in every dungeon/arena shot (world volume density ~0.01–0.04 + local fog where needed). Ember rim light on the warrior in every shot.
- Colour management: AgX "Medium High Contrast" (set by `setup_render`). Do NOT bake a heavy grade; the final grade (teal shadows, ember highlights, grain, vignette) is applied in the edit. Expose so blacks are deep but not crushed and only emissive cores clip.
- Vertical 9:16 composition: stack sky → subject → ground; main subject in the centre third of the width; nothing important in the top 220 px, bottom 380 px or right 140 px (at 1080×1920; scale proportionally).

## Determinism
- Every random choice uses a seeded generator (`rb_core.rng(id, salt)` or `random.Random(seed)`); no `random.random()` without a seed, no time-based values.
- Animation = per-frame keys computed from frame number (or Blender sims started at a fixed frame with fixed seeds).
- Geometry Nodes / particles: fixed seeds; anything time-varying must derive from the frame.
