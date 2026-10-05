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
- F2c re-render: good (thrown toward the lens, god behind). F2b (test 0.3x): helm + greatsword + compact burst read as the clash; obsidian still faint - accepted for a 15-frame insert.
- Batch 5: O6 (3/4 helm) good; M401 thin mythic-red beam over the greatsword - reads as loot; M407 blade crack reads; M505 warrior silhouetted against the column. All accepted.
- M105: reads (early warrior vs skeleton, sparks); grade cools it to floor-1 grey. M201: ghost lunge reads; near-lens ember bokeh too busy -> near=2 (also M508). M202/M204/M205 failed: CARRY lacked 'mid' -> fixed, re-render.
- M203: evil too close (purple mass) -> camera pulled back to 4.7 m.
- M205: king read same size as the warrior -> tight OTS looking steeply up (pauldron lower-left, king + axe fill the frame).
- M206: reads (slash shatters the skeleton) but the spark flash washed the teal set beige -> sparks strength 0.5.
- M207: good (evil bursts into purple smoke + sparks, warrior foreground).
- M208: framing good but key frame before the hit -> 957.
- M209: reads (evil presses, warrior driven back, boot sparks); recoil pose a bit stiff in a still - judge in motion.
- M301: evil (attack pose leans 1 m) overlapped the warrior and filled the 85 mm frame -> evil back to 1.75, camera 5 m side-on. M302: side-on 85 mm lost the falling body -> camera from his feet side, tracking his chest, cold rim.
- M302 test: holds him but helm hidden -> camera z 2.15. M402: ring still airborne at the key -> key 1131.
- M405: lightning reads, frame washed white -> strength 0.6. M501: good OTS (morbidious lunging, green pustules).
- M502: reads (cleave into the morbidious); both cut at the frame edges -> camera 3.1 m.
- M503: good (king shatters behind a shockwave, warrior foreground, blade blazing).
- M504: good (bad angel cut out of the air, red halo, burst at the cut).
- M506: washed white, crowd hid the warrior -> crowd centred in front of him, camera high OTS, lightning 0.5.
- M507: reads (fireball detonates on the evil); frame flooded orange -> fireball strength 0.7.
- E3: excellent (warrior from behind walking into the light pouring through the gate).
- E4: excellent (warrior small lower-middle, calm sky for the title, hills, flowers).
- M202 re-render: good (bad angel diving, red halo, low angle behind him).
- M205 re-render: good (king towers over the pauldron, axe up, eyes lit). M204: good (rune ring, wraiths + skeletons around him).
- M206 re-render: still beige at the hit frame (spark light ~100 W at 0.3 m in fog) -> key 942 (bones flying, light decayed), sparks 0.35.
- M208 re-render (key 957): flash filled the whole frame (sparks sprayed at the lens, scale 1.3 at 1.2 m) -> spray forward/away, scale 0.7, strength 0.45.
- M301 re-render: evil reads (horns, veins) but he was cut at the right edge (only the gauntlet, in the safe zone) and sparks washed it warm -> target on him (y 0.18), camera 5.6 m, sparks across frame at 0.45.
- M402 re-render: frame all gold fog, the real-size ring a speck in the bottom safe zone -> floor-level macro 0.5 m from a 2.2x ring, king's ash soft behind.
- M302 re-render: tight 85 mm chest from 3 m at 14 deg down = headless dark torso, fall unreadable -> camera high in front (z 4, ~43 deg down) tracking the chest: his front and helm turn up to us as he falls.
- M405 re-render: reads (lightning past his shoulder into the skeletons). M502 re-render: reads (cleave into the morbidious, both in frame). Raw haze to judge on the graded sheet.
- Graded check: M405, M502, M508 good. M506 washed white-grey (lightning 0.5 + full sparks 260 W in gold fog) -> lightning 0.35, sparks 0.4. M507 still flooded orange, evil lost -> fireball 0.4.
- Batch 8: M206 good (teal back, blade through ribs). M302 good (topples back, arms flung, helm visible). M402 good (ring glowing on wet stone, centred). M208 flash sphere still hid the pauldron -> flash=False. M301 recoil carried him to the right edge -> camera 6.2 m, target y 0.02.
