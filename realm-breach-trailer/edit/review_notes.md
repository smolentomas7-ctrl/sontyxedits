# Stills review notes (pre-checkpoint 2)

- M101 ok (moody, warrior centre third). M104 strong.
- M102 re-rendered: good (waterfall into black lake, warrior centred on the rocks).
- M103 early iron read as matte black from the front -> cold key added (rb_montage.cold_key); re-render.
- O3 (arena WIP): two floor hot spots bottom-left; warrior reads thin in profile (cape not visible);
  foreground parallax pillar missing (clear_view hides it). Fix: camera inside the nave, keep one
  out-of-focus broken drum in the foreground, check the cape side.
- O4: greaves were featureless tubes and the sabaton toe was an open tube (hollow visible) ->
  fixed in rb_warrior (front ridge, strap rivets, domed toe cap). Dust puff VFX pending rb_vfx.
- O7: good (god centred, halo reads). Blue underlight hot spot at the very bottom (inside the bottom
  safe zone, acceptable); robe reads as a flat sheet — consider folds/tatter in rb_god if time allows.
- CAPE BUG (all late-look shots): collision proxies had inward normals, so collisions pulled the cape INTO
  the chest/pelvis proxies (it shrank to a 0.4 x 0.7 m bundle within ~30 frames, even standing still).
  Fixed (rb_warrior._normals_out). Battle shots also get a soft cloth goal + body-only colliders.
- O8: salute fists read as hollow rings: palm tube open + wrist roll undefined for near-vertical blades ->
  palm caps + natural wrist roll in rb_motion.aim_hand.
- O9: camera 0.5 m from the helm at 85 mm (1 cm DOF, eyes bloomed into discs) -> 0.95 m, f/8.
- O11b: camera looked away from the warrior -> low rear 3/4 dolly. F7: whip still mid-turn at impact ->
  whip-tilt from warrior to god landing on the impact. F2a: camera between the fighters -> low side.
  F2b: blades only -> 3 m, helm + contact + obsidian blade. F1d: pulled back for hand + god. F2c: low,
  he is thrown toward the lens.
- Arena floor puddles reflect blue/white hot spots (F1a-F1c, F7) -> tame.
- O11b: cape flew up over the helm in the charge (arm proxies, friction 8) -> violent intro shots (O11a/O11b/O12) use the battle cloth settings. Re-render O11b.
- M103: cold key works (iron reads as metal). Early hood crown read as a paper cone side-on -> elliptical dome (rb_warrior._early_head). Re-render M103/M105/M106 later.
- F1a: good (cape streams, sparks); warrior's cape crossed the right safe zone -> camera back 0.8 m, aim between them. Re-render.
- F1d: god's halo/robe in the right safe zone; key frame after the bolt -> camera back, aim weighted to the god, key 1391. Re-render.
- F2a: obsidian blade invisible against the dark, god small -> 7 m, edge_glow x4. Re-render.
- F2b: sparks great but hid both blades -> key 1479, sparks 0.75, camera 3.7 m slightly higher. Re-render.
- F2c: reads (thrown, cape flying, god behind) -> key 1512 for a bigger figure. Re-render.
- F7: strong — god attack blast floods the hall, warrior foreground right, inside safe zones.
- E2: warrior at the left edge -> camera on the line through warrior and kneeling god (stacked), crane 5 -> 2 m.
- M106 (smoke test): 0.9 m blade cropped -> 1.75 m. M401: camera inside the beam at god rarity -> orbit r 4.4 -> 3.6.
- VFX + dungeon/props modules landed (dungeon ~35-45 s/frame uncontended at full res: needs light culling).
## Preliminary checkpoint sheet review (build/checkpoint2_pre)
- O6 ECU blurred (0.62 m at 85 mm) -> head-and-shoulders at 1.15 m f/8. O11a dark, no blade -> low-angle 35 mm
  knees-up with ember under-light. O11b cape still a wad -> cloth goal only holds the top 35% (torso-relative goal
  pulled the cape up the back when pitched forward).
- F2a obsidian still invisible (edge glow driven by a near-zero wear attr) -> big cool area rim behind the blade.
  F2b sparks hid both blades -> side-on to the clash. F2c warrior cropped left -> camera on his flight line,
  target tracks him. F7 key frame was under the edit's white flash -> 1935.
- M401/M406/M505 washed white -> beam glow 0.38, god attack strength 0.45/0.4. M304 black blob -> cold rim key.
  M407 only bokeh -> side-on push along the blade. M303/E6 props too small -> tighter fit.
- O11a re-render: good (low front angle, roar, blade blazing, centred).
- O11b re-render: cape streams horizontally behind the charge (foreshortened to a band from the low rear camera) - physically right, accepted; judge in the preview motion.
- O12 re-render: strong (blades meet, spark burst, shockwave + dust). Air ring edge-on reads as a line in a still; fine in motion.
- M303 re-render: good (orbs fill the width, the right one mid-death).
- M304 re-render: good (bowed helm, hands on the pommel, ash; cold rim makes the armour read).
- M401: god tier beam still a cream wall -> beam_radius 0.22, exposure -0.8, key still on mythic (1100).
- M406: reads (arch, brazier, god attack column). Legend haze lifted the blacks -> grade black point 0.07 + contrast 1.22 for phases 4/5. M407: blade + crack read; near-lens ember blob -> embers moved behind the blade.
- M505: column hid the warrior -> column behind him, silhouette against the light.
- AUDIO: verify_output.py found the AAC-decoded true peak at -0.08 dBTP (wav -1.21) -> limiter ceiling -2.4 dBFS; decoded AAC now -14.05 LUFS / -1.28 dBTP.
- God robe: fold + wrinkle bump (large distorted bands + noise) so it reads as heavy cloth, not a sheet.
- F1d re-render: strong (bolt from his hand to the god's chest, both in frame).
- F2a: blade now reads but glows white (x4 + rim) -> edge_glow 1.8, keep the specular rim (bible: near-black, faint blue edge).
- F2b: side-on still unreadable (sparks dominate, obsidian invisible) -> rim light + edge glow like F2a, sparks 0.5, key 1478.
