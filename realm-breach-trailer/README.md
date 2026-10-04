# REALM BREACH — "The Final Battle" (vertical cinematic TikTok trailer)

1080×1920, 30 fps, ~74.7 s. Everything — characters, environments, VFX,
voice, sound design, titles — is generated from code in this folder. The only
inputs are the song and a reference edit (not committed; place them in
`input/`).

## Requirements

- Blender 4.0+ (command line), run headless through `xvfb-run` (software GL is fine; a GPU is faster)
- `python3-numpy` available to Blender's Python
- ffmpeg / ffprobe 6+ with librubberband
- Python 3.11 with: `librosa numpy soundfile opencv-python-headless scenedetect pyloudnorm scipy matplotlib pillow kokoro-onnx`
- Kokoro-82M ONNX model files (`kokoro-v1.0.onnx`, `voices-v1.0.bin`) from
  `github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0` → `/opt/tts/`
  (or set `KOKORO_MODEL` / `KOKORO_VOICES`)

## Inputs

```
input/song/kingdom_beat_tiktok.mp3
input/reference/reference_edit.mp4
```

## Pipeline (step by step)

```bash
python3 src/analyse_song.py          # analysis/song.json + waveform.png
python3 src/analyse_reference.py     # analysis/reference.json
python3 src/tts.py                   # assets/audio/vo/*.wav + vo.json
python3 src/build_timeline.py        # config/timing.json, edit/timeline.json, edit/shot_list.md
python3 src/analyse_song.py          # re-draw waveform.png with the D/U markers

# characters (checkpoint 1)
xvfb-run -a blender -b --factory-startup -P scenes/turnarounds.py -- --char warrior_late
xvfb-run -a blender -b --factory-startup -P scenes/turnarounds.py -- --char warrior_early
xvfb-run -a blender -b --factory-startup -P scenes/turnarounds.py -- --char god
```

Shots, sound design, edit and mix are added as the production progresses;
see `PROGRESS.md`.

## Project layout

| Path | Purpose |
|---|---|
| `config/video.py` | format, palette, safe zones, lenses, seeds (imported everywhere) |
| `config/timing.json` | generated; single source of truth for every shot's start/end |
| `analysis/` | song.json, reference.json, waveform.png |
| `assets/characters.md` | locked character / object bible |
| `scenes/lib/` | Blender libraries: core, mesh, materials, warrior, god, … |
| `scenes/` | one Blender script per shot + turnarounds |
| `src/` | analysis, timeline, TTS, SFX, edit, mix scripts |
| `edit/` | shot_list.md, timeline.json |
| `build/` | renders (not committed) |
| `output/` | final MP4 |

## Determinism

Every random generator is seeded from the shot ID (`config/video.py: seed_for`);
animation is keyed per frame from pure functions of the frame number; cloth is
simulated from each shot's first frame. Re-running a shot renders identical frames.

## Credits / licences

- Font: Cinzel by Natanael Gama — SIL Open Font License 1.1 (`assets/fonts/OFL.txt`).
- Voice: Kokoro-82M (Apache-2.0), voices `bm_lewis` (warrior) and `am_onyx` (Fallen God). No real person's voice is cloned.
- Song: "Kingdom Beat (TikTok Version)" — Valterix; supplied by the user, not redistributed here.
