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
