"""Sound-design cue sheet. Positions are in SONG BEATS (converted to video time
through config/timing.json), so the sound design re-times with the edit.

Each cue: (beat, sound, gain_db, opts) where opts may contain
  pan: -1..1, align: 'start' | 'peak' (risers/swells end ON the beat), fade_out: seconds,
  dur: seconds (truncate), rate: playback-rate multiplier (pitch/time).
Beds: (beat_in, beat_out, sound, gain_db, fade_in_s, fade_out_s).
"""

# peak offsets (seconds from file start) for sounds aligned to land ON a beat
PEAK = {"riser_4s": 4.0, "riser_2s": 2.0, "reverse_swell": 1.5}

BEDS = [
    (-1.0, 48.0, "wind", -19, 0.4, 0.15),
    (-1.0, 48.0, "ember_crackle", -24, 0.6, 0.2),
    (9.5, 43.0, "drone", -14, 3.0, 0.08),
    (44.0, 48.0, "drone", -12, 0.05, 0.05),
    (50.0, 53.5, "wind", -24, 0.1, 0.3),
    (51.0, 52.6, "water", -18, 0.1, 0.3),
    (53.0, 54.2, "portal_fire", -14, 0.2, 0.2),
    (101.5, 129.0, "drone", -12, 1.5, 0.05),
    (102.0, 128.0, "wind", -22, 2.0, 0.3),
    (103.0, 128.0, "ember_crackle", -26, 2.0, 0.3),
    (130.5, 141.0, "wind", -26, 2.0, 2.0),
    (130.5, 140.0, "ember_crackle", -30, 2.0, 2.0),
    (135.0, 149.0, "meadow_wind", -18, 2.5, 1.5),
]

CUES = [
    # ---- ACT I
    (0.0, "sub_hit", 0, {}),
    (0.0, "impact", -6, {}),
    (1.6, "thunder_far", -8, {"pan": -0.4}),
]
# walk: one heavy step per beat (O2/O3), then the plant on the 808 at beat 8
for i, b in enumerate([1, 2, 3, 4, 5, 6, 7]):
    CUES.append((b - 0.02, "footstep_" + "abc"[i % 3], -9, {"pan": (-0.15 if i % 2 else 0.15)}))
    if i % 2 == 0:
        CUES.append((b + 0.05, "chainmail", -18, {}))
CUES += [
    (2.5, "cloth_flap", -20, {}),
    (5.5, "cloth_flap", -20, {}),
    (8.0, "footstep_heavy", -2, {}),
    (8.02, "chainmail", -14, {}),
    (16.0, "reverse_swell", -6, {"align": "peak"}),
    (16.0, "boom", -1, {}),
    (16.0, "sub_hit", -4, {}),
    (23.4, "stone_grind", -12, {}),
    (27.6, "cloth_flap", -18, {}),
    (28.2, "blade_ring", -14, {}),
    (36.8, "blade_ring", -18, {}),
    (43.0, "riser_2s", -6, {"align": "peak", "fade_out": 0.03}),
    (46.5, "footstep_heavy", -7, {}),
    (47.0, "footstep_a", -6, {}),
    (47.33, "footstep_b", -6, {}),
    (47.66, "footstep_c", -6, {}),
    (48.0, "riser_2s", -4, {"align": "peak", "fade_out": 0.02}),
    (47.55, "whoosh_a", -4, {}),
    # ---- ACT III: the clash IS the drop
    (48.0, "clash_big", 0, {}),
    (48.0, "sub_hit", -1, {}),
    (48.0, "boom", -5, {}),
    (48.15, "debris", -8, {}),
    # ---- ACT IV phase 1
    (49.85, "whoosh_long", -10, {}),
    (50.0, "sub_hit_small", -12, {}),
    (52.0, "whoosh_b", -14, {}),
    (53.7, "whoosh_long", -8, {"pan": 0.3}),
    (54.35, "clash_a", -9, {}),
    (54.5, "growl_o", -16, {"pan": -0.3}),
    (55.1, "loot_0", -12, {}),
    # phase 2 — low hits under the FLOOR numbers
    (55.9, "whoosh_a", -12, {}),
    (56.05, "shriek", -13, {"pan": 0.4}),
    (56.7, "clash_b", -11, {}),
    (57.5, "sub_hit_small", -5, {}),
    (57.5, "whoosh_b", -9, {"pan": -0.5}),
    (59.0, "sub_hit_small", -5, {}),
    (59.05, "growl_a", -11, {}),
    (60.0, "growl_u", -12, {"pan": -0.4}),
    (60.25, "growl_o", -14, {"pan": 0.5}),
    (61.0, "sub_hit_small", -5, {}),
    (61.05, "boss_roar", -8, {}),
    (62.0, "impact", -9, {}),
    (62.5, "sub_hit_small", -5, {}),
    (62.5, "impact", -9, {}),
    (63.0, "clash_b", -11, {}),
    (63.5, "impact", -9, {}),
    # phase 3 — sacrifice (slow motion)
    (63.9, "whoosh_long", -12, {"rate": 0.7}),
    (64.15, "impact_big", -2, {"rate": 0.6}),
    (64.2, "clash_a", -8, {"rate": 0.5}),
    (67.0, "impact", -6, {"rate": 0.6}),
    (67.1, "debris", -12, {"rate": 0.7}),
    (68.0, "heartbeat", -2, {}),
    (68.3, "glass_fizz", -8, {}),
    (70.0, "breath", -14, {}),
    # phase 4 — transformation
    (71.9, "whoosh_a", -12, {}),
]
for i in range(8):
    CUES.append((72.0 + 0.25 * i, "loot_%d" % i, -12 + i * 0.5, {"fade_out": 0.5}))
CUES += [
    (74.0, "impact", -9, {}),
    (74.35, "chime_low", -12, {}),
    (75.1, "ring_slide", -10, {}),
    (75.95, "fire", -6, {}),
    (76.95, "lightning", -6, {}),
    (77.9, "riser_2s", -14, {"align": "peak", "dur": 0.1}),
    (78.0, "god_blast", -7, {"fade_out": 1.5, "dur": 2.0}),
    (78.0, "impact_big", -6, {}),
    (79.0, "fire", -11, {"dur": 1.2, "fade_out": 0.4}),
    # phase 5 — legend
    (80.0, "growl_u", -12, {}),
]
for i, b in enumerate([80.0, 80.5, 81.0, 81.5, 82.0, 82.5, 83.0, 83.5]):
    CUES.append((b, ["impact", "clash_a", "impact_big", "clash_b", "impact", "clash_a", "impact", "clash_b"][i],
                 -10, {"pan": (-0.3 if i % 2 else 0.3), "dur": 0.6, "fade_out": 0.2}))
CUES += [(82.0, "god_blast", -12, {"dur": 1.0, "fade_out": 0.4})]
for i in range(8):
    CUES.append((84.0 + 0.25 * i, "tick", -12, {}))
CUES += [
    (86.0, "sub_hit", -4, {}),
    (86.0, "cloth_flap", -14, {}),
    # ---- ACT V — the last life
    (87.85, "whoosh_a", -8, {}),
    (88.0, "clash_big", -3, {}),
    (89.9, "whoosh_long", -8, {}),
    (90.35, "impact_big", -4, {}),
    (90.4, "debris", -9, {}),
    (91.0, "fire", -7, {}),
    (92.0, "lightning", -7, {}),
    (93.5, "clash_a", -7, {}),
    (94.5, "clash_b", -7, {}),
    (95.3, "clash_a", -6, {}),
    (96.0, "stone_grind", -9, {}),
    (96.2, "reverse_swell", -10, {"align": "peak"}),
    (98.0, "clash_big", -3, {}),
    (99.6, "impact_big", -1, {}),
    (99.7, "debris", -8, {}),
    (100.4, "impact", -4, {}),
    (101.5, "heartbeat", -2, {}),
    (101.9, "glass_fizz", -8, {}),
    (112.5, "breath", -13, {}),
    (114.6, "chainmail", -12, {}),
    (116.0, "footstep_heavy", -8, {}),
    (117.0, "cloth_flap", -16, {}),
    (124.6, "blade_ring", -10, {}),
    (128.0, "riser_4s", -8, {"align": "peak", "fade_out": 0.02}),
    (128.0, "reverse_swell", -6, {"align": "peak"}),
    # ---- U: the ultimate — the biggest sound in the video
    (127.9, "whoosh_long", -6, {}),
    (128.0, "god_blast", 0, {"fade_out": 3.5, "dur": 6.0}),
    (128.0, "sub_hit", -1, {}),
    (128.0, "impact_big", -3, {}),
    (128.0, "clash_big", -6, {}),
    # ---- ACT VI — heaven
    (131.6, "breath", -12, {}),
    (134.2, "reverse_swell", -16, {"align": "peak"}),
    (140.0, "sub_hit", -5, {}),
    (146.2, "chime_low", -16, {}),
]
