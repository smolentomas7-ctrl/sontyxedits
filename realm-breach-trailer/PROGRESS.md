# PROGRESS — Realm Breach "The Final Battle"

Update after every step so work can resume after an interruption.

| Step | Status | Notes |
|---|---|---|
| 1 Setup | done | Blender 4.0.2 (apt) headless via Xvfb + Mesa llvmpipe (no GPU, 4 CPU). ffmpeg 6.1.1. Python 3.11 + librosa, scenedetect, opencv, pyloudnorm. TTS: Kokoro-82M ONNX (model from GitHub releases; HuggingFace + ElevenLabs blocked, no API key). Font: Cinzel (OFL). |
| 2 Song analysis | done | 119.64 BPM (fitted 8th grid, 4.1 ms err; librosa default 79.5 is a 3/16 artefact). 8-bar loop, constant energy -> sections made in the mix. D = video 24.239 s (song 24.28, bar 12), U = video 64.359 s (song 64.40, bar 32 loop restart). analysis/song.json, waveform.png, config/timing.json |
| 3 Reference analysis | done | Different track (corr 0.15). Drop 15.9 s; pre-drop static + word captions every ~0.45 s; post-drop 1.79 cuts/s (0.9/beat), median 0.37 s, 2-beat holds + quarter-beat strobe bursts; no flashes/zooms. analysis/reference.json |
| 4 Shot list | done | edit/shot_list.md + edit/timeline.json (69 shots, 74.73 s). Brief v2 merged (subtitles, right safe zone 140 px, loop). |
| 5 Characters (CHECKPOINT 1) | awaiting user OK | Warrior late/early + Fallen God built procedurally (scenes/lib/rb_warrior.py, rb_god.py). Turnarounds: build/characters/, sheet: assets/characters/checkpoint1_contact_sheet.jpg. Cape + tabard are cloth-simulated (mass 0.12, tension 80, collision dist 5 mm — larger distances make the cloth climb the proxies). |
| 6 World + VFX | pending | |
| 7 Stills (CHECKPOINT 2) | pending | |
| 8 Animate + render | pending | |
| 9 Voice | draft done | Kokoro bm_lewis (warrior), am_onyx (god); chains applied; assets/audio/vo/*.wav + vo.json. Line 2 kept full length. |
| 10 SFX | pending | |
| 11 Edit/grade/mix | pending | |
| 12 Preview + review | pending | |
| 13 Final | pending | |

## Environment notes
- Blender: `xvfb-run -a -s "-screen 0 1920x1080x24" blender -b --factory-startup -P <script>`
- Kokoro model files: /opt/tts/kokoro-v1.0.onnx, /opt/tts/voices-v1.0.bin
  (re-download: github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/)

## Render budget notes
- EEVEE on llvmpipe: ~5 s fixed + ~1.2 s per TAA sample per frame at 1080x1920. 2 parallel Blender workers ≈ 11 s/frame effective at 8 samples.
- Keep shadow-casting lights to 1–2 per shot; rims without shadows.
- Never wait on `pgrep -f <pattern>` inside the same shell command that contains the pattern (it matches itself).
