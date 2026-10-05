@"/root/.claude/uploads/5bb4df6d-480a-5d1c-b4fb-b8ea501ef483/1f221bbf-Valterix_-_Kingdom_Beat_Tiktok_Version_-_TSOM_128k.mp3" @"/root/.claude/uploads/5bb4df6d-480a-5d1c-b4fb-b8ea501ef483/db4aa810-WhatsApp_Video_2026-10-04_at_11.34.23.mp4" # REALM BREACH — "THE FINAL BATTLE" — CINEMATIC TIKTOK TRAILER

## ROLE
You are the DIRECTOR, CINEMATOGRAPHER, 3D CHARACTER ARTIST, MOTION DESIGNER, CREATIVE CODER, AUDIO DESIGNER, VIDEO ENGINEER and QUALITY CONTROL for this production. Treat this as a real film production, not a coding task. Think about the final video first, then choose the technology, then write the code, then render, critique and improve. Never let the implementation dictate the creative result.

Pipeline: IDEA → STORY → SHOT LIST → VISUAL DESIGN → CHARACTERS → AUDIO → ANIMATION → STILL FRAMES → PREVIEW → REVIEW → POLISH → FINAL MP4.

I provide only the song and a reference edit. You create everything else yourself: the warrior, the boss, enemies, environments and all footage (Blender + Python), the voice-over (text-to-speech), all sound effects and the titles.

The project is NOT complete until a playable, verified MP4 exists.

---

## 1. VIDEO SPEC

| Setting | Value |
|---|---|
| Type | Cinematic game trailer + viral TikTok edit (social + cinematic mode) |
| Resolution | 1080 × 1920, vertical 9:16, rendered natively vertical |
| FPS | 30 |
| Duration | Set by the song; target 45–75 s |
| Audience | TikTok gamers, Roblox players |
| Emotion | Dread → defiance → explosive energy → loss → triumph → peace |
| Visual style | Dark-fantasy AAA action RPG (Elden Ring / Lord of the Rings mood), maximum realism |
| Camera language | Slow and deliberate before the drop, beat-locked and punchy in the montage, heavy in the final battle, drifting in the ending |
| Lighting | Low-key, volumetric fog, ember rim light on the hero, cold blue on the boss |
| Audio | The song leads; deep voice-over; synthesised SFX under the music |
| Typography | Open-licensed serif display (e.g. Cinzel), wide tracking |
| Transitions | Hard cuts by default; whip pans and white flashes only on accented beats |
| Rendering method | HYBRID: Blender/EEVEE (3D) + Python/librosa (analysis) + FFmpeg (edit, grade, composite) + TTS + procedural audio |
| Output | output/realm_breach_trailer.mp4, H.264 high profile, CRF 16, AAC 320 kbps, −14 LUFS |
| Safe area | No titles or key faces in the top 220 px or bottom 380 px (TikTok UI) |

---

## 2. INPUTS
- input/song/: "Kingdom Beat (TikTok Version)". The whole edit is cut to this song.
- input/reference/: a TikTok edit. Copy its pacing, cut lengths, flashes, zooms and speed ramps, not its content.

---

## 3. THE GAME (stay faithful to it)
Realm Breach is a dark-fantasy horror action RPG on Roblox.
- Lobby: a haunted forest with scary trees, a river, a lake, rocks, a waterfall and ranking boards. A Hellgate portal leads into the dungeon world, the "Fallen World".
- Dungeon: infinite floors up to 999, dark void dimension, cracked glowing floors, fog. A boss every 5 floors; bosses drop rings.
- Enemies: skeleton, ghost, bad angel, evil, morbidious, fallen god.
- Final boss: THE FALLEN GOD on floor 999.
- Loot rarities in order: common, rare, epic, mythic, legendary, morbidious, god, fallen equip.
- Weapon classes: sword, greatsword, scythe. Abilities: Q Fireball, E Lightning, R God Attack.
- The player has 3 lives.
- True ending: after the Fallen God, the Gate of Heaven opens onto a flower meadow. Then the Rebirth button.

---

## 4. MASTER VISUAL LANGUAGE (every shot follows this)

Palette:
| Role | Colour |
|---|---|
| Void / blacks | #07080A |
| Shadows | teal-black #0B1418 |
| Hero ember (rim light, eyes, blade crack) | #FF6A1A |
| Gold accents / god attack | #F2B544 → white-gold #FFE9A8 |
| Fallen God light | steel blue #4A6C8F, glow #6FA8FF |
| Heaven ending | warm white #FFF4DC, meadow green #8DB580 |
Rarity glows: common #9A9A9A, rare #3D7BFF, epic #A04DFF, mythic #FF3B3B, legendary #FF9A1A, morbidious #6BFF4A, god #FFE9A8, fallen equip deep navy #1B2A4A with blue glow.

- Materials: PBR everywhere. Blackened steel, worn leather, wet cracked stone, obsidian, cloth with thickness. No plastic or toy look.
- Lighting: low-key. Ember rim light on the warrior in every shot. Volumetric fog in every dungeon shot. Cold blue only where the Fallen God is.
- Contrast and grade: crushed blacks lifted slightly, filmic contrast, teal shadows, ember highlights. Phase 3 desaturated by about 35%. Heaven ending opens up warm and soft.
- Film grain: subtle, seeded, constant across the video. Light vignette.
- Lenses: 85mm close-ups, 50mm mids, 35mm wides, 24mm for scale. Shallow DOF on close-ups.
- Animation curves: cubic ease-in-out on all camera moves. Anticipation (6–8 frames) before every swing, follow-through on the cape, overshoot on text slams. No linear motion anywhere except constant drift (fog, embers).
- Typography: off-white serif, wide tracking, faint ember glow. Only for "FLOOR" numbers, the title and the final line.
- Transitions: hard cuts. Whip pan with motion blur only between environments. White flash only on D, phase changes and the ultimate.

---

## 5. CHARACTER AND OBJECT SPECS (lock these; never redesign between shots)

THE WARRIOR (the Breach Runner)
- Body: realistic adult human proportions, about 1.9 m, broad shoulders, heavy and grounded.
- Armour: blackened steel plate over chainmail and dark leather. Edges scratched to bare metal, soot, dried mud, dents. Layered pauldrons, the left larger with a cracked rim. Plated gauntlets.
- Helmet: closed great helm with a narrow T-shaped visor slit. Two ember-orange eyes glow inside. Close-ups of "his eyes" are close-ups of this slit.
- Cape: long, tattered, crimson-black, torn hem, cloth-simulated.
- Weapon: greatsword, black steel, nearly his height, a thin ember-orange crack along the blade that glows brighter when he attacks. Always in his right hand.
- Rings: from Phase 4 on, 4 Great Rings over the gauntlet fingers, each softly glowing. None before.
- Abilities: Q Fireball = orange-red fire. E Lightning = white-blue forks. R God Attack = golden-white blast of light (the finale).
- Early look (Phase 1 only): plain worn grey iron armour, leather hood, plain short sword, no cape, no rings, no glow.
- Personality in motion: slow, heavy, deliberate, unstoppable.
- Poses/animations: walk, stop, stand, raise sword, point sword, charge, swing, clash, block, fall, kneel, rise, cast, god attack, exhausted stand, walk away.

THE FALLEN GOD
- About 3× the warrior's height.
- Cracked pale stone body with black void visible through the cracks; cold blue light leaks from the cracks and eyes.
- A broken halo ring floating behind his head. Long tattered dark robes.
- Weapon: a massive obsidian blade, two-handed.
- Always shot from a low angle until he falls.
- Personality in motion: still, slow, monumental; every move feels inevitable.

ENEMIES (one distinct silhouette + glow each): skeleton (bone white, ember eyes), ghost (translucent pale blue), bad angel (black broken wings, red glow), evil (horned shadow, purple glow), morbidious (bloated, toxic green glow).

Write all of this to assets/characters.md before modelling.

---

## 6. HARD RULES
- Never invent song timestamps. All timing comes from your audio analysis.
- Characters, weapons, palette and grade stay identical in every shot (except the planned early look).
- Deterministic rendering: everything is a function of frame number; every random generator is seeded (seed = hash of the shot ID). The same frame always renders the same way.
- Quality > quantity, story > effects, design > complexity, consistency > randomness. Cut any shot that does not have a clear purpose.
- No real person's voice cloned. No copyrighted characters.
- Never spend long render time on anything that has not been checked as a still or a low-res preview first.

---

## 7. PROJECT STRUCTURE AND CENTRALISED TIMING

realm-breach-trailer/
  input/song/, input/reference/
  config/video.py        → FPS, resolution, palette, safe areas, lens presets, seeds
  config/timing.json     → generated from the song analysis; the single source of truth for every shot's start/end
  analysis/              → song.json, reference.json, waveform.png
  assets/                → characters/, enemies/, environments/, vfx/, fonts/, audio/, characters.md
  scenes/                → one Blender Python script per shot, each reading config/
  src/                   → analyse_song.py, analyse_reference.py, build_timeline.py, render_shots.py, tts.py, sfx.py, edit.py, mix.py
  build/                 → characters/, stills/, shots/, preview/
  edit/                  → timeline.json, timeline.md
  output/
  PROGRESS.md            → update after every step so the work can resume if the session is interrupted
  README.md              → how to re-render everything with one command

Every script reads timing from config/timing.json. Changing one beat assignment must re-time the whole video.

---

## 8. PRODUCTION STEPS

STEP 1 — SETUP
Check Blender (command line), ffmpeg/ffprobe, Python 3. If Blender is missing, stop and tell me how to install it. Install librosa, numpy, soundfile, opencv-python, scenedetect. Create the structure above.

STEP 2 — SONG ANALYSIS
librosa: BPM, beats, downbeats, onset strength, RMS energy. Identify intro, build-up, main drop (first beat = D), post-drop break, the biggest hit after the drop (= U, the ultimate), outro. Save analysis/song.json and waveform.png with markers, look at the PNG, sanity-check D. Write config/timing.json.

STEP 3 — REFERENCE ANALYSIS
PySceneDetect: every cut, shot lengths, white flashes (luma spikes), cut rate per section, aligned to the song if it uses the same track. Save analysis/reference.json.

STEP 4 — CHARACTERS (CHECKPOINT 1)
Model the warrior (late + early look) and the Fallen God. Render turnarounds (front, side, back, close-up of visor/face) under neutral light into build/characters/, make one contact sheet, review it yourself and fix anything blocky or unfinished. Then show me the contact sheet and WAIT for my OK.

STEP 5 — TIMELINE
Turn the shot table (section 9) into edit/timeline.json + edit/timeline.md with real times from config/timing.json. Opening shots are timed backwards from D by dialogue length; everything after D snaps to beats.

STEP 6 — WORLD AND VFX
Build reusable assets: haunted forest lobby with waterfall and ranking boards, Hellgate portal, dungeon floor kit, floor 999 void arena, Gate of Heaven + flower meadow, all enemies, VFX (embers, fog volumes, sparks, shockwave ring, fireball, lightning, god attack, rarity loot glows, ring glow, life orbs).

STEP 7 — STILL FRAMES (CHECKPOINT 2)
Render one key frame per shot into build/stills/, one contact sheet in shot order. Check composition, colours, lighting, camera angle, safe areas and consistency. Fix, then show me the contact sheet and WAIT for my OK.

STEP 8 — ANIMATE AND RENDER SHOTS
Animate per the shot table. Render with EEVEE (bloom, volumetrics, soft shadows, motion blur, DOF); Cycles only if a shot truly needs it. Natively 1080x1920, 30 fps, 10 extra frames at each end. First render every shot at 50% resolution for the preview.

STEP 9 — VOICE (text-to-speech)
WARRIOR: "So... you're the one who's been waiting for me."
WARRIOR: "I have crossed worlds... faced death... and sacrificed everything."
WARRIOR: "But now..."
WARRIOR: "The Fallen God..."
WARRIOR: "YOUR REIGN ENDS HERE!"
FALLEN GOD: "After everything you've lost... you still dare to challenge me?"
WARRIOR: "You took everything from me..."
WARRIOR: "But you made one mistake."
WARRIOR: "YOU LET ME LIVE."
- If an ElevenLabs (or similar) API key is in my environment: deep, mature male library voice, each line separately, several takes, keep the best.
- Otherwise: the best open-source local TTS you can install (e.g. Piper or Kokoro), deepest male voice. Never a robotic voice like espeak. If it still sounds robotic, tell me.
- If the intro is too short, shorten line 2 to "I have faced death... and sacrificed everything." and tell me.
- Warrior chain: pitch −1 to −2 semitones, high-pass 70 Hz, +3 dB at 120 Hz, −3 dB at 300 Hz, +2 dB at 3 kHz, compression 4:1, short plate reverb 15% wet, slight helmet-muffled tone, light saturation on shouts.
- Fallen God chain: layer the line at −5 semitones with an octave-down distorted copy underneath, reverse-reverb swell before the first word, long hall reverb 30% wet.

STEP 10 — SOUND DESIGN (synthesised in Python/ffmpeg)
Heavy armoured footsteps, chainmail, cape flaps, wind, thunder, ember crackle, sub drone, deep booms, greatsword clashes, whooshes, risers, heartbeat, fire, lightning, god-attack blast, monster growls, soft meadow wind.
Sync map: text slam → sub hit · cut between environments → whoosh · weapon contact → metal clash stack · life lost → heartbeat + low-pass on music · ultimate → riser, impact, sub drop, debris tail · title → single low hit.

STEP 11 — EDIT, GRADE, MIX
src/edit.py reads edit/timeline.json: trims, speed ramps (slow motion always ends on a beat), punch-in zooms with ease-out, seeded camera shake that decays over 6 frames, white flash frames, grade, vignette, seeded grain, titles. Place every visual impact 1–2 frames BEFORE its beat. Mix song + SFX + voice; duck the music 8–10 dB under every line; normalise to −14 LUFS.

STEP 12 — PREVIEW, SELF-REVIEW, ITERATE
Render a 540x960 preview of the full video. Export frames at D, each phase start, U and the title into a contact sheet. Review as a professional:
- STORY: is the journey from floor 1 to the Fallen God clear without words?
- HOOK: is the first second gripping with the sound off?
- COMPOSITION: is the eye always on the right thing, inside the safe area?
- MOTION: does every move feel designed (easing, anticipation, follow-through)?
- CAMERA: does every camera move have a reason?
- CONSISTENCY: is the warrior identical in every shot? Same grade everywhere?
- AUDIO: is every line clear on a phone speaker? Does every impact land on its beat?
- PACING: is any shot longer than its beats deserve?
- POLISH: does anything look procedural, empty or unfinished?
Fix everything you find, re-render the preview, review again. Repeat until it holds up.

STEP 13 — FINAL
Render 1080x1920, 30 fps to output/realm_breach_trailer.mp4. Verify with ffprobe (resolution, fps, duration, audio stream) and confirm it plays. If anything fails, diagnose and fix it before finishing.

---

## 9. SHOT TABLE
D = first beat of the drop. U = biggest hit after the drop. Real times come from config/timing.json.

### OPENING (intro → D)
| Shot | Time | Camera | Lens / DOF | Motion | Subject / Action | Lighting | Transition | Audio |
|---|---|---|---|---|---|---|---|---|
| O1 Hook | first 1–1.5 s | static | — | text slams 115% → 100% with overshoot, 8 frames | Black, "FLOOR 999" in the centre | ember glow on text | hard cut | first musical hit + sub boom |
| O2 Walk | intro | tracking from behind, 0.6 m high, 3 m back, matching walk speed, 10% push-in | 35mm / medium | slow, eased | Warrior walks through the floor 999 arena; ruined pillars, embers drifting past the lens, cape moving | distant ember backlight, rim light, volumetric fog | cut | footsteps, armour, thunder |
| O3 Profile (drop if intro is short) | intro | side tracking, pillars in the foreground for parallax | 50mm / shallow | slow | Rim-lit silhouette | rim only | cut | wind, drone |
| O4 Stop | intro | ground-level static insert | 50mm / shallow | — | His boot plants, dust settles | low raking light | cut | one heavy step, near silence |
| O5 Reveal | intro | starts at the boss's feet, 0.3 m high, 4 m away; tilts up 70° over 3 s, decelerating at the face | 24mm / deep | slow, decelerate | THE FALLEN GOD; blue cracks ignite bottom to top, eyes last, halo behind | cold blue underlight, god rays | cut as the eyes ignite | sub swell, boom on the eyes |
| O6 | VO1 | static extreme close-up on the visor slit | 85mm / very shallow | breathing micro-move | Eyes glowing | ember key, blue fill from the boss side | cut | VO1 |
| O7 | after VO1 | low angle, 5% push-in | 35mm / medium | very slow | The boss tilts his head | blue | cut | ambience |
| O8 | VO2 | mid shot, 15% push-in | 50mm / shallow | slow | Raises the greatsword, blade crack glows faintly | rim | cut | VO2, blade ring |
| O9 | VO3, build starts | static extreme close-up on the visor | 85mm / very shallow | — | Eyes flare brighter | ember | cut | VO3, build begins |
| O10 | VO4 | over the warrior's shoulder, boss framed beyond the blade tip | 35mm / deep | static | Sword pointed at the boss | mixed ember / blue | cut | VO4, then 1 beat silence |
| O11 | D−4 → D−1 beats | close-up shout, then low fast dolly with the charge, speed ramp 0.5× → 1.5× | 24mm / medium | accelerate | "YOUR REIGN ENDS HERE!" and the charge | ember trails | whip into O12 | VO5, riser |
| O12 Clash | D | wide side-on, both fighters | 24mm / deep | 2-frame freeze on contact, then debris bursts | Greatsword meets obsidian blade: shockwave ring, sparks | white-hot flash at contact | 2-frame white impact + shake decaying over 6 frames | drop + metal clash stack + sub |

### DROP MONTAGE (split the drop's bars across 5 phases; use the reference's cut rates where they differ)
| Phase | Cut rate | Camera style | Shots | Accent effects |
|---|---|---|---|---|
| 1 Beginning | 1 per beat | wide and observational, 35mm | Early-look warrior: haunted forest, waterfall, ranking boards, walking into the Hellgate, floor 1, skeleton fight, a grey common drop | punch-in zoom, whip pan through the portal |
| 2 Struggle | 1 per beat, half-beat on fills | handheld-feel tracking, 35mm | Ghost, bad angel, evil, crowds of enemies, a floor-5 boss, "FLOOR 25 / 100 / 250 / 500" on snares; armour heavier and darker | hard cuts, shake on hits |
| 3 Sacrifice | 1 per 2 beats | slow dolly, 85mm close-ups | Hit hard, falling; three life orbs going dark one by one | 50% slow motion, desaturated, one held beat if the song allows |
| 4 Transformation | 1 per beat | orbit and push-ins, 50mm | Drops glowing through all 8 rarity colours in order, a boss dropping a ring, the ring sliding onto his gauntlet, Q fireball → E lightning → R god attack, the blade crack igniting | speed ramps into impacts, white flash on the god attack |
| 5 Legend | half-beat, last bar quarter-beat | fast dynamic, 24mm | Morbidious enemies, huge boss kills, biggest god attacks; ends on a held hero shot of the full late-look warrior, low angle | motion blur, quarter-beat strobe, then hold |
| Return | last downbeat of the drop | — | Hard cut back to the Fallen God fight mid-swing | — |

### FINAL BATTLE (post-drop)
| Shot | Time | Camera | Lens / DOF | Motion | Subject / Action | Lighting | Transition | Audio |
|---|---|---|---|---|---|---|---|---|
| F1 | section start | wide, heavy handheld feel | 24mm / deep | fast | Full-intensity exchange, blocks, dodges, fireball and lightning | ember vs blue | cuts on beats | music full |
| F2 | next 2 bars | low angle on the boss, weapon close-ups | 35mm / medium | heavy | The Fallen God dominates; the warrior is knocked down; one life orb left | blue overpowers | cut | big impact, music ducks −10 dB or enters the break |
| F3 | break | low angle looking up at the boss | 24mm / deep | slow push | Boss line | cold blue key | cut | Fallen God VO |
| F4 | break | mid shot | 50mm / shallow | slow | Warrior rises, gripping the greatsword | ember rim returns | cut | VO7 |
| F5 | break | close-up | 85mm / shallow | static | "But you made one mistake." | ember | cut | VO8 |
| F6 | last bar of the break | slow push into an extreme close-up of the visor | 85mm / very shallow | slow push | "YOU LET ME LIVE." Eyes and blade crack blaze | ember overtakes blue | cut | VO9, riser |
| F7 Ultimate | U | wide, camera whips with the strike | 24mm / deep | explosive | R God Attack: golden-white blast hits the Fallen God | golden-white floods the frame | full white flash | biggest impact stack |

### ENDING (outro)
| Shot | Time | Camera | Lens / DOF | Motion | Subject / Action | Lighting | Transition | Audio |
|---|---|---|---|---|---|---|---|---|
| E1 | after U | — | — | — | Full white, 6–10 frames | — | fade from white | ~1 s silence |
| E2 | outro | slow crane-down reveal | 35mm / deep | drifting | Fallen God defeated, halo shattered; warrior standing exhausted, embers drifting | dim, ember | cut | music returns soft, breathing |
| E3 | outro | tracking from behind | 35mm / medium | slow | He walks toward the Gate of Heaven, warm light pouring out | warm white | light bloom | music fading |
| E4 | outro | slow wide pull-back | 24mm / deep | drifting | The flower meadow, petals in the air | soft warm | dissolve | soft wind |
| E5 | last ~3 s | static | — | title fades in with slight scale-up | "REALM BREACH", then "EVERY LEGEND HAS A BEGINNING. EVERY JOURNEY HAS AN END." | — | — | single low hit |
| E6 | final frames | static | — | glow pulse | A glowing REBIRTH button, then hard cut to black matching O1 so the video loops | ember glow | hard cut | first note of the song |

---

## 10. FINAL REPORT
When done, report:
1. Path to the final MP4
2. Resolution
3. FPS
4. Duration
5. Rendering method
6. Main technologies used
7. External assets used (TTS voice, font + licence, anything downloaded)
Also: BPM and D/U times found, the 3 weakest shots and how you would improve them.