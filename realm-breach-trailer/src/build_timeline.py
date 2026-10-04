"""STEP 2/4/5 — Build config/timing.json, edit/timeline.json and edit/shot_list.md.

Every time position comes from analysis/song.json (fitted beat grid) and
assets/audio/vo/vo.json (measured line lengths). Shots are written in *song
beats* (beat 0 = the song's first downbeat / first 808 hit); this script
turns them into video seconds and frames.

Song structure decision (see analysis/song.json notes): the track is an
8-bar loop with constant energy, so the trailer's sections are created in
the mix on top of the measured grid:
  beats   0– 48  intro  (12 bars, song heard muffled; build from beat 40)
  beat   48      D      (bar 12 = loop bar 4, an 808 downbeat)
  beats  48– 88  drop montage (10 bars, 5 phases)
  beats  88–104  final battle at full mix
  beats 104–128  break (music low-passed and ducked for the dialogue)
  beat  128      U      (bar 32 = loop restart, strongest 808 downbeat)
  beats 129–149  outro
Change any beat number here and the whole video re-times.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "config"))
import video  # noqa: E402

FPS = video.FPS
FIRST_HIT_FRAME = 5          # the song's first hit lands on video frame 5 (open on black)

D_BEAT = 48
U_BEAT = 128
BUILD_BEAT = 40
SILENT_BEAT = 43             # "one beat of silence" before the roar
BREAK_BEAT = 104
END_BEAT = 149               # loop point: video ends FIRST_HIT_FRAME frames before this beat

# Placement of every voice line: (id, song beat where the *speech* starts)
VO_PLACEMENT = [
    ("VO1", 16.35), ("VO2", 26.45), ("VO3", 36.75), ("VO4", 39.4), ("VO5", 44.08),
    ("VO6", 106.1), ("VO7", 115.0), ("VO8", 120.45), ("VO9", 125.3),
]

# ---------------------------------------------------------------------------
# SHOT LIST. start/end in song beats unless start_frame/end_frame are given.
# Fields: act, cam, lens, dof, motion, subject, light, trans, audio, why,
#         look (warrior look), env, flags.
# ---------------------------------------------------------------------------
S = []


def shot(sid, start, end, **kw):
    kw.update({"id": sid, "start_beat": start, "end_beat": end})
    S.append(kw)


# ---- ACT I — THE FINAL FLOOR ----------------------------------------------
shot("O1", None, None, start_frame=0, end_frame="O1_END", act="I", env="black", look=None,
     cam="static", lens="—", dof="—",
     motion="black for 4 frames; text slams 115%→100% with overshoot over 4 frames on the first hit, holds 8 frames",
     subject='"FLOOR 999" centred, Cinzel, wide tracking, ember glow', light="ember glow on the text",
     trans="hard cut", audio="first musical hit (song's first 808) + sub boom",
     why="Scroll-stopper that reads with the sound off: the number alone says 'final level'.")
shot("O2", "O1_END", 6, act="I", env="arena999", look="late",
     cam="tracking from behind, 0.6 m high, 3 m back, matched to walk speed, 10% push-in", lens="35mm", dof="medium (f/4)",
     motion="slow, eased push-in; one step per beat", subject="Warrior walks into the floor 999 arena; colossal ruined pillars rise "
     "out of frame top, embers drift past the lens, cape swaying", light="distant ember backlight through fog, ember rim, volumetric haze",
     trans="cut", audio="footsteps on the beat, chainmail, distant thunder, wind",
     why="Establishes the hero, his weight and the scale of the void; vertical frame used for pillar height.")
shot("O3", 6, 7.5, act="I", env="arena999", look="late",
     cam="side tracking, broken pillars in the foreground for parallax", lens="50mm", dof="shallow (f/2)",
     motion="slow lateral track", subject="Rim-lit silhouette of the warrior in profile; helm, pauldron and cape edge",
     light="rim only (ember from behind, teal fill nil)", trans="cut", audio="wind, low drone, step",
     why="Shape language of the character in one readable silhouette.")
shot("O4", 7.5, 9.5, act="I", env="arena999", look="late",
     cam="ground-level static insert", lens="50mm", dof="shallow (f/2)", motion="none; dust settles",
     subject="His sabaton plants on the cracked glowing floor on the 808; dust and ash lift and settle",
     light="low raking ember light across the floor cracks", trans="cut", audio="one heavy step on the beat, then near silence",
     why="He stops: the walk ends, tension begins.")
shot("O5", 9.5, 16, act="II", env="arena999", look=None,
     cam="starts at the boss's feet 0.3 m high, 4 m away; tilts up 70° over 3 s, decelerating at the face", lens="24mm", dof="deep (f/8)",
     motion="slow ease-out tilt", subject="THE FALLEN GOD: blue cracks ignite feet→head, eyes last, broken halo behind",
     light="cold blue underlight, god rays through fog", trans="cut as the eyes ignite (on the 808)",
     audio="sub swell, deep boom on the eyes",
     why="The reveal; the full 9:16 height sells a 5.7 m god.")
shot("O6", 16, 23, act="II", env="arena999", look="late",
     cam="static extreme close-up on the visor slit", lens="85mm", dof="very shallow (f/1.4)", motion="breathing micro-move",
     subject="The T-slit; two ember eyes burn inside", light="ember key from inside, blue fill from the boss side",
     trans="cut", audio="VO1", why="The hero answers the reveal; his eyes are his face.")
shot("O7", 23, 26, act="II", env="arena999", look=None,
     cam="low angle, slow 5% push-in", lens="35mm", dof="medium", motion="very slow", subject="The Fallen God slowly tilts his head",
     light="blue", trans="cut", audio="silence, ambience, stone grinding", why="A beat of contempt; silence before the vow.")
shot("O8", 26, 36.5, act="II", env="arena999", look="late",
     cam="mid shot, 15% push-in", lens="50mm", dof="shallow", motion="slow raise with 8-frame anticipation",
     subject="He slowly raises the greatsword; the blade crack glows faintly", light="ember rim, teal shadows",
     trans="cut", audio="VO2, blade ring", why="Resolve; the weapon is introduced.")
shot("O9", 36.5, 39, act="II", env="arena999", look="late",
     cam="static extreme close-up on the visor", lens="85mm", dof="very shallow", motion="none",
     subject="Eyes flare brighter", light="ember", trans="cut", audio="VO3; the music begins to build",
     why="Turn of the scene; the build starts here.")
shot("O10", 39, 44, act="II", env="arena999", look="late",
     cam="over the warrior's shoulder, boss framed beyond the blade tip", lens="35mm", dof="deep", motion="static",
     subject="Sword pointed at the Fallen God", light="mixed ember / blue", trans="cut",
     audio="VO4, then one beat of silence", why="Declares the target; vertical stack: blade → boss.")
shot("O11a", 44, 46.5, act="III", env="arena999", look="late",
     cam="close-up, slight push", lens="50mm", dof="shallow", motion="head snaps up with anticipation",
     subject='The roar: "YOUR REIGN ENDS HERE!" — eyes and blade flare', light="ember", trans="cut",
     audio="VO5 (shout), riser", why="Defiance.")
shot("O11b", 46.5, 48, act="III", env="arena999", look="late",
     cam="low fast dolly beside him, speed ramp 0.5× → 1.5×", lens="24mm", dof="medium", motion="accelerate",
     subject="The charge; ember trails off the blade", light="ember trails", trans="whip into O12",
     audio="riser, heavy running steps", why="Momentum into the drop.")
shot("O12", 48, 50, act="III", env="arena999", look="late",
     cam="wide side-on, both fighters", lens="24mm", dof="deep",
     motion="2-frame freeze on contact, then debris bursts", subject="Greatsword meets obsidian blade on D: ring shockwave, sparks",
     light="white-hot flash at contact", trans="2-frame white impact + shake decaying over 6 frames",
     audio="drop + stacked metal clash + sub drop", why="The single explosive cut: the clash IS the drop.", flags=["flash_full"])

# ---- ACT IV — THE JOURNEY (drop montage) ----------------------------------
P1 = dict(act="IV", phase=1, look="early", lens="35mm", dof="medium", light="cold grey moonlight, fog, ember rim")
shot("M101", 50, 51, env="forest", cam="wide observational, punch-in zoom", motion="slow drift + punch-in",
     subject="Haunted forest: twisted trees, river, fog; the early-look warrior small in frame", trans="cut",
     audio="whoosh, wind", why="Where it began: small and unproven.", flags=["flash_phase", "punch_in"], **P1)
shot("M102", 51, 52, env="forest_waterfall", cam="wide", motion="slow drift", subject="Dark waterfall into a black lake; he stands on the rocks",
     trans="cut", audio="water roar under music", why="World texture of the lobby.", **P1)
shot("M103", 52, 53, env="forest_boards", cam="wide low", motion="slow push", subject="Ranking boards with faint names; he walks past them",
     trans="cut", audio="wood creak", why="The game's lobby: the ladder he will climb.", **P1)
shot("M104", 53, 54, env="hellgate", cam="tracking from behind, whip pan through the portal", motion="push then whip",
     subject="He walks into the burning Hellgate", trans="whip pan", audio="fire roar, whoosh", why="Crossing into the Fallen World.", **P1)
shot("M105", 54, 55, env="dungeon", cam="wide", motion="handheld feel", subject="Floor 1: his first skeleton fight, short sword clash",
     trans="cut", audio="bone/metal clank", why="First blood.", **P1)
shot("M106", 55, 56, env="dungeon", cam="low insert, punch-in", motion="punch-in", subject="A grey COMMON drop glows on the floor at his feet",
     trans="cut", audio="dull chime", why="Humble first reward; sets up the rarity ladder.", flags=["punch_in"], **P1)

P2 = dict(act="IV", phase=2, look="mid", lens="35mm", dof="medium", light="darker; teal shadows, enemy glows")
shot("M201", 56, 57.5, env="dungeon", cam="handheld-feel tracking", motion="shake on hit", subject="A ghost lunges out of the fog; he blocks",
     trans="cut", audio="ghost shriek, block clank", why="The struggle begins.", flags=["flash_phase"], **P2)
shot("M202", 57.5, 59, env="dungeon", cam="low angle", motion="dive", subject="A bad angel dives, black broken wings, red glow",
     trans="cut", audio="wing whoosh, low hit", why="Enemy variety; FLOOR 25 on the snare.", text="FLOOR 25", **P2)
shot("M203", 59, 60, env="dungeon", cam="mid", motion="strike", subject="The horned evil looms; he strikes into it",
     trans="cut", audio="growl, low hit", why="FLOOR 100.", text="FLOOR 100", **P2)
shot("M204", 60, 61, env="dungeon", cam="high wide, 24mm", motion="slow push", subject="Crowds of skeletons and ghosts close in around him",
     trans="cut", audio="crowd growls", why="Overwhelming odds; uses the full vertical frame.", **P2)
shot("M205", 61, 62, env="dungeon", cam="low angle", motion="heavy", subject="Floor-5 boss: a towering armoured skeleton king raises its axe",
     trans="cut", audio="boss roar, low hit", why="A boss every five floors; FLOOR 250.", text="FLOOR 250", **P2)
shot("M206", 62, 62.5, env="dungeon", cam="close", motion="slash", subject="Greatsword slash through bone", trans="cut",
     audio="impact", why="Fill: rhythm.", **P2)
shot("M207", 62.5, 63, env="dungeon", cam="mid", motion="impact", subject="Evil shattered into smoke", trans="cut",
     audio="impact, low hit", why="FLOOR 500.", text="FLOOR 500", **P2)
shot("M208", 63, 63.5, env="dungeon", cam="close", motion="impact", subject="Sparks off his pauldron as a blade glances", trans="cut",
     audio="impact", why="Fill: he is getting hurt.", **P2)
shot("M209", 63.5, 64, env="dungeon", cam="wide", motion="impact", subject="He is driven back across the floor", trans="cut",
     audio="impact", why="Fill: into the sacrifice.", **P2)

P3 = dict(act="IV", phase=3, look="mid", lens="85mm", dof="shallow", light="desaturated, darker",
          flags=["slowmo", "desat"])
shot("M301", 64, 66, env="dungeon", cam="slow dolly, close", motion="50% slow motion", subject="He is hit hard: the evil's blow lands on his chest, sparks hang",
     trans="cut", audio="pitched-down impact", why="The cost of the climb.", **P3)
shot("M302", 66, 68, env="dungeon", cam="slow dolly", motion="50% slow motion, ends on the beat", subject="He falls backwards to the floor; ash rises",
     trans="cut", audio="body impact, muffled music", why="He falls.", **P3)
shot("M303", 68, 70, env="ui_orbs", cam="static macro", motion="50% slow motion", subject="Three life orbs; one goes dark",
     trans="cut", audio="heartbeat, one held beat of near silence", why="Lives are the stake.", **P3)
shot("M304", 70, 72, env="dungeon", cam="slow push", motion="50% slow motion", subject="He kneels, gripping the greatsword, head bowed",
     trans="cut", audio="heartbeat fades, music returns", why="Low point before the rise.", **P3)

P4 = dict(act="IV", phase=4, look="late", lens="50mm", dof="shallow", light="gold and rarity colours ignite")
shot("M401", 72, 74, env="loot", cam="orbit + push-in", motion="colour changes every quarter beat",
     subject="A loot pillar glows through every rarity in order: common→rare→epic→mythic→legendary→morbidious→god→fallen equip",
     trans="cut", audio="chimes rising per rarity", why="Power climbs, in the game's own colour ladder.", flags=["flash_phase"], **P4)
shot("M402", 74, 75, env="dungeon", cam="low", motion="speed ramp into the drop", subject="A boss collapses to ash and drops a glowing ring",
     trans="cut", audio="ring chime", why="Bosses drop rings.", flags=["ramp"], **P4)
shot("M403", 75, 76, env="macro", cam="macro push-in", motion="slide", subject="The ring slides onto his gauntlet finger beside three others; all four glow",
     trans="cut", audio="metal slide, hum", why="The Great Rings: he is no longer the same.", **P4)
shot("M404", 76, 77, env="dungeon", cam="orbit", motion="speed ramp into impact", subject="Q — Fireball: orange-red fire erupts from his palm",
     trans="cut", audio="fire whoosh", why="Ability Q.", flags=["ramp"], **P4)
shot("M405", 77, 78, env="dungeon", cam="push-in", motion="speed ramp", subject="E — Lightning: white-blue forks tear through enemies",
     trans="cut", audio="thunder crack", why="Ability E.", flags=["ramp"], **P4)
shot("M406", 78, 79, env="dungeon", cam="wide", motion="impact", subject="R — God Attack: golden-white blast", trans="white flash",
     audio="blast", why="Ability R (foreshadows the finale).", flags=["flash_full"], **P4)
shot("M407", 79, 80, env="dungeon", cam="close along the blade", motion="push", subject="The blade crack ignites, ember fire racing to the tip",
     trans="cut", audio="fire ignite", why="His signature weapon awakens.", **P4)

P5 = dict(act="IV", phase=5, look="late", lens="24mm", dof="medium", light="ember and gold, motion blur")
shot("M501", 80, 80.5, env="dungeon", cam="fast", motion="strike", subject="Morbidious brute lunges, toxic green", trans="cut",
     audio="growl", why="Legend phase.", flags=["flash_phase"], **P5)
shot("M502", 80.5, 81, env="dungeon", cam="fast", motion="slash", subject="He cleaves the morbidious", trans="cut", audio="impact", why="", **P5)
shot("M503", 81, 81.5, env="dungeon", cam="low", motion="impact", subject="Colossal boss kill: the skeleton king shatters", trans="cut", audio="impact", why="", **P5)
shot("M504", 81.5, 82, env="dungeon", cam="wide", motion="impact", subject="Bad angel cut out of the air", trans="cut", audio="impact", why="", **P5)
shot("M505", 82, 82.5, env="dungeon", cam="wide", motion="blast", subject="Biggest god attack: a pillar of gold light", trans="cut", audio="blast", why="", **P5)
shot("M506", 82.5, 83, env="dungeon", cam="fast", motion="slash", subject="Lightning-wreathed slash through a crowd", trans="cut", audio="impact", why="", **P5)
shot("M507", 83, 83.5, env="dungeon", cam="low", motion="impact", subject="Fireball detonates on evil", trans="cut", audio="impact", why="", **P5)
shot("M508", 83.5, 84, env="dungeon", cam="fast", motion="slash", subject="Greatsword arc, ember trail", trans="cut", audio="impact", why="", **P5)
shot("M509", 84, 86, env="strobe", cam="quarter-beat strobe of M502–M508", motion="motion blur", subject="Quarter-beat strobe of the legend's kills",
     trans="cuts on quarter beats", audio="strobe ticks", why="Peak density, matching the reference's strobe bursts.", flags=["strobe"], **P5)
shot("M510", 86, 88, env="arena999", cam="low angle, static", motion="hold", subject="Held hero shot: full late-look warrior, cape lifting, blade burning",
     trans="hard cut on the last downbeat", audio="sub hit", why="He is a legend now.", **dict(P5, lens="24mm"))

# ---- ACT V — THE LAST LIFE ------------------------------------------------
F = dict(act="V", look="late", env="arena999")
shot("F1a", 88, 90, cam="wide, heavy handheld feel", lens="24mm", dof="deep", motion="mid-swing", subject="Return: greatsword and obsidian blade mid-clash",
     light="ember vs blue", trans="cut", audio="clash", why="Back to the present, mid-fight.", flags=["flash_phase"], **F)
shot("F1b", 90, 91, cam="low", lens="24mm", dof="deep", motion="fast", subject="He dodges; the obsidian blade smashes the floor",
     light="blue", trans="cut", audio="whoosh, floor smash", why="Danger.", **F)
shot("F1c", 91, 92, cam="mid", lens="35mm", dof="medium", motion="fast", subject="Fireball into the god's chest", light="orange-red",
     trans="cut", audio="fire", why="Q in the fight.", **F)
shot("F1d", 92, 93, cam="mid", lens="35mm", dof="medium", motion="fast", subject="Lightning forks across the god's stone", light="white-blue",
     trans="cut", audio="thunder", why="E in the fight.", **F)
shot("F1e", 93, 96, cam="wide", lens="24mm", dof="deep", motion="heavy", subject="Full exchange: blocks, the god barely moves",
     light="ember vs blue", trans="cut", audio="clashes", why="The god is unmoved.", **F)
shot("F2a", 96, 98, cam="low angle on the boss", lens="24mm", dof="deep", motion="heavy", subject="The Fallen God raises the obsidian blade overhead",
     light="blue overpowers", trans="cut", audio="stone grind, low swell", why="He dominates.", **F)
shot("F2b", 98, 99, cam="weapon close-up", lens="50mm", dof="shallow", motion="impact", subject="Obsidian crashes into the greatsword; sparks",
     light="blue", trans="cut", audio="clash", why="Contact.", **F)
shot("F2c", 99, 101, cam="wide", lens="24mm", dof="deep", motion="heavy", subject="He is thrown down across the floor",
     light="blue", trans="cut", audio="big impact", why="The fall.", **F)
shot("F2d", 101, 104, cam="macro", lens="85mm", dof="shallow", motion="slow", subject="Second life orb goes dark — one left",
     light="blue", trans="cut", audio="heartbeat, music muffles and enters the break", why="One life left.", env_override="ui_orbs", **F)
shot("F3", 104, 114.5, cam="low angle looking up at the boss", lens="24mm", dof="deep", motion="slow push", subject="The Fallen God looks down and speaks",
     light="cold blue key", trans="cut", audio="Fallen God VO", why="The antagonist's voice.", **F)
shot("F4", 114.5, 120, cam="mid", lens="50mm", dof="shallow", motion="slow", subject="He slowly rises, gripping the greatsword",
     light="ember rim returns", trans="cut", audio="VO7", why="He refuses to stay down.", **F)
shot("F5", 120, 124.75, cam="close-up", lens="85mm", dof="shallow", motion="static", subject='"But you made one mistake."',
     light="ember", trans="cut", audio="VO8", why="The turn.", **F)
shot("F6", 124.75, 127.5, cam="slow push into an extreme close-up of the visor", lens="85mm", dof="very shallow",
     motion="slow push", subject='"YOU LET ME LIVE." Eyes and blade crack blaze', light="ember overtakes blue",
     trans="cut", audio="VO9, riser", why="Ember takes the frame back.", **F)
shot("F7", 127.5, 129, cam="wide, camera whips with the strike", lens="24mm", dof="deep", motion="explosive",
     subject="R — God Attack: golden-white blast hits the Fallen God on U", light="golden-white floods the frame",
     trans="full white", audio="biggest impact stack: riser, impact, sub drop, debris", why="The ultimate on the biggest hit.",
     flags=["flash_full"], **F)

# ---- ACT VI — THE GATE OF HEAVEN ------------------------------------------
shot("E1", 129, "E1_END", act="VI", env="white", look=None, cam="—", lens="—", dof="—", motion="—",
     subject="Full white, 8 frames", light="—", trans="fade from white", audio="silence (debris tail only)",
     why="Release.")
shot("E2", "E1_END", 134, act="VI", env="arena999_after", look="late", cam="slow crane-down reveal", lens="35mm", dof="deep",
     motion="drifting", subject="The Fallen God fallen, halo shattered on the floor; the warrior stands exhausted, embers drifting down",
     light="dim, ember", trans="cut", audio="silence, then soft music, breathing", why="No celebration. He breathes.")
shot("E3", 134, 138, act="VI", env="heaven_gate", look="late", cam="tracking from behind", lens="35mm", dof="medium", motion="slow",
     subject="He turns and walks toward the Gate of Heaven; warm light pours out", light="warm white",
     trans="light bloom", audio="music fading, soft wind", why="Peace is earned.")
shot("E4", 138, 146, act="VI", env="meadow", look="late", cam="slow wide pull-back", lens="24mm", dof="deep", motion="drifting",
     subject="Flower meadow, petals in the air; he is small again, at peace. Title lands: REALM BREACH, then the tagline",
     light="soft warm", trans="cut", audio="soft wind; single low hit as the title lands",
     why="Heaven: the palette flips; the title.", overlays=["title"])
shot("E6", 146, 148, act="VI", env="rebirth", look=None, cam="static", lens="—", dof="—", motion="glow pulses once",
     subject="A glowing REBIRTH button", light="ember-gold glow", trans="hard cut to black", audio="soft swell, then the song's first note",
     why="The game's loop: rebirth.")
shot("END", 148, "END", act="VI", env="black", look=None, cam="—", lens="—", dof="—", motion="—",
     subject="Black, identical to frame 0", light="—", trans="loop to frame 0", audio="first note of the song",
     why="Seamless loop into the FLOOR 999 slam.")


def main():
    song = json.load(open(os.path.join(ROOT, "analysis", "song.json")))
    vo = json.load(open(os.path.join(ROOT, "assets", "audio", "vo", "vo.json")))
    t0, beat = song["grid_t0"], song["beat_sec"]
    song_offset = t0 - FIRST_HIT_FRAME / FPS

    def vt(b):
        return t0 + b * beat - song_offset

    def vf(b):
        return int(round(vt(b) * FPS))

    def cut(b):
        """Cut / impact frame: 1 frame before the beat."""
        return vf(b) - 1

    special = {
        "O1_END": FIRST_HIT_FRAME - 1 + 4 + 8,       # slam appears 1 frame early, settles in 4, holds 8
        "E1_END": cut(129) + 8,
        "END": vf(END_BEAT) - FIRST_HIT_FRAME,       # so the loop lands the next hit on the grid
    }

    def resolve(x, is_start):
        if isinstance(x, str):
            return special[x]
        return cut(x)

    shots = []
    for s in S:
        sf = s.get("start_frame")
        ef = s.get("end_frame")
        sf = special[sf] if isinstance(sf, str) else sf
        ef = special[ef] if isinstance(ef, str) else ef
        if sf is None:
            sf = resolve(s["start_beat"], True)
        if ef is None:
            ef = resolve(s["end_beat"], False)
        d = dict(s)
        d["start_frame"], d["end_frame"] = int(sf), int(ef)
        d["frames"] = int(ef - sf)
        d["start"] = round(sf / FPS, 3)
        d["end"] = round(ef / FPS, 3)
        d["flags"] = list(s.get("flags", []))
        shots.append(d)
    # continuity check
    for a, b in zip(shots, shots[1:]):
        assert a["end_frame"] == b["start_frame"], (a["id"], b["id"], a["end_frame"], b["start_frame"])
        assert a["frames"] > 0, a["id"]
    total_frames = shots[-1]["end_frame"]

    # FLOOR text slams land on the snare 8th inside their shot
    for d in shots:
        if d.get("text"):
            d["text_frame"] = d["start_frame"]

    # Voice placements (speech start beat -> file start time, accounting for lead-in swell)
    vo_out = {}
    for vid, b in VO_PLACEMENT:
        meta = vo[vid]
        speech_start = vt(b)
        file_start = speech_start - meta["lead_in"]
        vo_out[vid] = {"speech_start": round(speech_start, 3), "file_start": round(file_start, 3),
                       "speech_end": round(speech_start + meta["speech_dur"], 3),
                       "file": meta["file"], "text": meta["text"], "speaker": meta["speaker"]}
    # VO must sit inside its shot window (plus small J/L-cut allowance)
    owner = {"VO1": "O6", "VO2": "O8", "VO3": "O9", "VO4": "O10", "VO5": "O11a",
             "VO6": "F3", "VO7": "F4", "VO8": "F5", "VO9": "F6"}
    byid = {d["id"]: d for d in shots}
    for vid, sid in owner.items():
        v, s = vo_out[vid], byid[sid]
        assert v["speech_start"] >= s["start"] - 0.8 and v["speech_end"] <= s["end"] + 0.6, (vid, v, s["start"], s["end"])
    # the line after VO4 must leave one beat of silence before the roar
    assert vo_out["VO4"]["speech_end"] <= vt(SILENT_BEAT) + 0.05, vo_out["VO4"]
    for a, b in (("VO1", "VO2"), ("VO2", "VO3"), ("VO3", "VO4"), ("VO4", "VO5"), ("VO6", "VO7"), ("VO7", "VO8"), ("VO8", "VO9")):
        assert vo_out[a]["speech_end"] < vo_out[b]["speech_start"], (a, b)

    # Music automation: (song beat, low-pass Hz, gain dB). Linear interpolation of
    # gain and log interpolation of cutoff between keys. Applied in src/mix.py.
    music = [
        (-1, 300, -9), (36, 300, -9), (BUILD_BEAT, 320, -9), (SILENT_BEAT - 0.05, 2600, -4),
        (SILENT_BEAT, 2600, -60), (SILENT_BEAT + 0.98, 2600, -60), (SILENT_BEAT + 1, 3200, -4),
        (D_BEAT - 0.02, 9000, -2), (D_BEAT, 20000, 0),
        (68, 20000, 0), (68.05, 520, -24), (69, 520, -22), (70, 1500, -8), (72, 20000, 0),
        (101.3, 20000, 0), (101.6, 520, -10), (BREAK_BEAT, 420, -11), (124, 420, -11), (U_BEAT - 0.02, 7000, -3),
        (U_BEAT, 20000, 0), (129, 20000, 0), (129.03, 20000, -80), (132, 1300, -80), (133, 1300, -15),
        (140, 1100, -17), (146, 900, -28), (147.5, 900, -80), (END_BEAT + 2, 900, -80),
    ]
    music_keys = [{"beat": b, "t": round(vt(b), 4), "lowpass_hz": hz, "gain_db": g} for b, hz, g in music]

    markers_b = {"first_hit": 0, "build_start": BUILD_BEAT, "silent_beat": SILENT_BEAT, "D": D_BEAT,
                 "phase1": 50, "phase2": 56, "phase3": 64, "phase4": 72, "phase5": 80, "return": 88,
                 "break_start": BREAK_BEAT, "U": U_BEAT, "outro_start": 129, "music_returns": 132,
                 "title": 140, "rebirth": 146, "black": 148, "loop": END_BEAT}
    markers = {k: round(vt(b), 4) for k, b in markers_b.items()}
    markers["video_end"] = round(total_frames / FPS, 4)

    beats_v = [round(vt(b), 4) for b in range(-1, END_BEAT + 2)]
    timing = {
        "generated_by": "src/build_timeline.py",
        "fps": FPS, "width": video.WIDTH, "height": video.HEIGHT,
        "bpm": song["bpm"], "beat_sec": beat, "bar_sec": beat * 4,
        "song_grid_t0": t0, "song_offset": round(song_offset, 5),
        "video_time_of_song_beat": "t = song_grid_t0 + beat*beat_sec - song_offset",
        "total_frames": total_frames, "duration": round(total_frames / FPS, 4),
        "markers_beats": markers_b, "markers": markers,
        "markers_song_time": {k: round(t0 + b * beat, 4) for k, b in markers_b.items()},
        "sections": [
            {"name": "intro (muffled song)", "start": 0.0, "end": markers["build_start"]},
            {"name": "build", "start": markers["build_start"], "end": markers["D"]},
            {"name": "drop montage", "start": markers["D"], "end": markers["return"]},
            {"name": "final battle", "start": markers["return"], "end": markers["break_start"]},
            {"name": "break (dialogue)", "start": markers["break_start"], "end": markers["U"]},
            {"name": "ultimate + outro", "start": markers["U"], "end": markers["video_end"]},
        ],
        "shots": {d["id"]: {"start_frame": d["start_frame"], "end_frame": d["end_frame"],
                            "start": d["start"], "end": d["end"]} for d in shots},
        "vo": vo_out,
        "music_automation": music_keys,
        "beats_video_time": {"first_beat_index": -1, "times": beats_v},
    }
    os.makedirs(os.path.join(ROOT, "edit"), exist_ok=True)
    with open(os.path.join(ROOT, "config", "timing.json"), "w") as fh:
        json.dump(timing, fh, indent=1)
    with open(os.path.join(ROOT, "edit", "timeline.json"), "w") as fh:
        json.dump({"fps": FPS, "total_frames": total_frames, "song_offset": round(song_offset, 5),
                   "shots": shots, "vo": vo_out}, fh, indent=1)

    # ---- shot_list.md ----------------------------------------------------
    acts = {"I": "ACT I — THE FINAL FLOOR", "II": "ACT II — THE FALLEN GOD", "III": "ACT III — THE CLASH",
            "IV": "ACT IV — THE JOURNEY (drop montage)", "V": "ACT V — THE LAST LIFE", "VI": "ACT VI — THE GATE OF HEAVEN"}
    L = ["# Shot list — REALM BREACH: THE FINAL BATTLE", "",
         "Generated by `src/build_timeline.py` from `analysis/song.json` (%.2f BPM, beat %.4f s) and measured voice lengths. "
         "Times are video seconds; every cut is placed 1 frame before its beat. 1080×1920, 30 fps, total %.2f s (%d frames)."
         % (song["bpm"], beat, total_frames / FPS, total_frames), "",
         "Key markers: **D = %.3f s** (clash), **U = %.3f s** (God Attack). Build starts %.3f s, break %.3f s."
         % (markers["D"], markers["U"], markers["build_start"], markers["break_start"]), ""]
    cur = None
    for d in shots:
        if d["act"] != cur:
            cur = d["act"]
            L += ["", "## " + acts[cur], ""]
        ph = (" · Phase %d" % d["phase"]) if d.get("phase") else ""
        L.append("### %s%s — %.2f–%.2f s (%d f)%s" % (d["id"], ph, d["start"], d["end"], d["frames"],
                                                      ("  · text: **%s**" % d["text"]) if d.get("text") else ""))
        L.append("- **Camera:** %s · **Lens:** %s · **DOF:** %s" % (d.get("cam", ""), d.get("lens", ""), d.get("dof", "")))
        L.append("- **Motion:** %s" % d.get("motion", ""))
        L.append("- **Subject / action:** %s" % d.get("subject", ""))
        L.append("- **Lighting:** %s · **Transition:** %s" % (d.get("light", ""), d.get("trans", "")))
        L.append("- **Audio:** %s" % d.get("audio", ""))
        if d.get("why"):
            L.append("- **Why:** %s" % d["why"])
        if d.get("look"):
            L.append("- **Warrior look:** %s" % d["look"])
    L += ["", "## Voice placement", "", "| Line | Speaker | Speech start (s) | End (s) | Text |", "|---|---|---|---|---|"]
    for vid, v in vo_out.items():
        L.append("| %s | %s | %.2f | %.2f | %s |" % (vid, v["speaker"], v["speech_start"], v["speech_end"], v["text"]))
    with open(os.path.join(ROOT, "edit", "shot_list.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("total %.2f s (%d frames), D %.3f  U %.3f  shots %d" % (total_frames / FPS, total_frames, markers["D"], markers["U"], len(shots)))


if __name__ == "__main__":
    main()
