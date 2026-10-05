"""Build the CHECKPOINT 2 review page (HTML + act sheets + compressed animatic) for publishing as an Artifact.

python3 src/checkpoint_page.py [--sheets assets/checkpoint2] [--animatic build/preview/realm_breach_animatic.mp4]

Writes build/checkpoint2_page/{index.html, act_*.jpg, animatic.mp4}.
"""
import argparse
import html
import json
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--sheets", default=os.path.join(ROOT, "assets", "checkpoint2"))
ap.add_argument("--animatic", default=os.path.join(ROOT, "build", "preview", "realm_breach_animatic.mp4"))
ap.add_argument("--out", default=os.path.join(ROOT, "build", "checkpoint2_page"))
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

tl = json.load(open(os.path.join(ROOT, "edit", "timeline.json")))
tm = json.load(open(os.path.join(ROOT, "config", "timing.json")))
shots = tl["shots"]
ACTS = [("I", "The walk", "Floor 999. He walks the endless hall alone and stops."),
        ("II", "The reveal", "The Fallen God, halo burning blue. Four lines of challenge, his blade rising."),
        ("III", "The charge", "The roar, the charge, and the clash on the drop."),
        ("IV", "The climb", "Five phases: the haunted forest and his first floors, the struggle, the sacrifice, "
                            "the transformation, the legend."),
        ("V", "The last life", "The final duel. One life left. God Attack on the ultimate."),
        ("VI", "Rebirth", "White. The god defeated, the Gate of Heaven, the meadow, the title, REBIRTH, loop.")]

# act sheets
sheets = []
for act, name, _ in ACTS:
    src = os.path.join(a.sheets, "act_%s.jpg" % act)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(a.out, "act_%s.jpg" % act))
        sheets.append(act)
# compressed animatic (keeps the page under the per-file limit)
has_video = False
if os.path.exists(a.animatic):
    dst = os.path.join(a.out, "animatic.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.animatic, "-c:v", "libx264", "-profile:v", "high",
                    "-crf", "30", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", dst], check=True)
    has_video = os.path.getsize(dst) < 15e6
    if not has_video:
        os.remove(dst)


def tc(sec):
    return "%d:%05.2f" % (int(sec // 60), sec % 60)


rows = []
for s in shots:
    sb = s.get("start_beat")
    beat = "" if sb is None else ("%g" % sb if isinstance(sb, (int, float)) else str(sb))
    text = s.get("text", "")
    rows.append("<tr><td class='id'>%s</td><td class='num'>%s</td><td class='num'>%s</td><td class='num'>%d</td>"
                "<td>%s</td><td class='subj'>%s%s</td></tr>" % (
                    html.escape(s["id"]), tc(s["start"]), beat, s["frames"], html.escape(s.get("lens", "")),
                    html.escape(s["subject"]), (" <span class='tag'>%s</span>" % html.escape(text)) if text else ""))

d_t = tm["markers"].get("D") if isinstance(tm.get("markers"), dict) else None
u_t = tm["markers"].get("U") if isinstance(tm.get("markers"), dict) else None


def fmt_marker(m):
    if m is None:
        return "—"
    if isinstance(m, dict):
        t = m.get("video_time", m.get("t"))
        f = m.get("frame")
        return "%s (frame %s)" % (tc(t), f) if t is not None else json.dumps(m)
    return tc(float(m))


acts_html = []
for act, name, blurb in ACTS:
    if act not in sheets:
        continue
    n = sum(1 for s in shots if s["act"] == act)
    acts_html.append("""
<section class="act" id="act-%s">
  <header><p class="eyebrow">Act %s · %d shots</p><h2>%s</h2><p class="blurb">%s</p></header>
  <a href="act_%s.jpg" target="_blank" rel="noopener"><img src="act_%s.jpg" alt="Act %s key stills in shot order" loading="lazy"></a>
</section>""" % (act, act, n, html.escape(name), html.escape(blurb), act, act, act))

video_html = ("""
<section class="film">
  <div class="phone"><video src="animatic.mp4" controls playsinline preload="metadata"></video></div>
  <div class="film-notes">
    <h2>Animatic</h2>
    <p>Every key still placed at its exact length on the song, with the real mix, voice, subtitles, titles,
    flashes and grade. It shows pacing, text placement and sound; motion comes after your OK.</p>
    <dl>
      <div><dt>Length</dt><dd>%s · %d frames · 30 fps</dd></div>
      <div><dt>Tempo</dt><dd>%.2f BPM</dd></div>
      <div><dt>Drop (D)</dt><dd>%s</dd></div>
      <div><dt>Ultimate (U)</dt><dd>%s</dd></div>
    </dl>
  </div>
</section>""" % (tc(tm["duration"]), tm["total_frames"], tm["bpm"], fmt_marker(d_t), fmt_marker(u_t))) if has_video else ""

page = """<title>Realm Breach Checkpoint 2</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Spectral:ital,wght@0,400;0,500;1,400&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: a dark screening-room page; one column of act sheets after the animatic, shot table last. Single dark
   world by choice (the film's own void, ember and god-blue). */
:root {
  --void: #0b0d10; --panel: #13171c; --line: #252c34; --ink: #ece5d8; --muted: #9aa3ab;
  --ember: #ff6a1a; --god: #6fa8ff;
  --display: "Cinzel", "Trajan Pro", Georgia, serif;
  --body: "Spectral", Georgia, "Times New Roman", serif;
  --mono: "JetBrains Mono", ui-monospace, Menlo, Consolas, monospace;
  color-scheme: dark;
}
body { background: var(--void); color: var(--ink); font: 17px/1.6 var(--body); }
.wrap { max-width: 1120px; margin: 0 auto; padding-inline: 20px; padding-block: 40px 72px; display: grid; gap: 56px; }
h1, h2 { font-family: var(--display); font-weight: 700; letter-spacing: 0.06em; text-wrap: balance; margin: 0; }
h1 { font-size: clamp(2rem, 6vw, 3.4rem); line-height: 1.05; }
h1 span { color: var(--ember); }
h2 { font-size: 1.45rem; }
p { margin: 0; max-width: 65ch; }
.eyebrow { font: 500 0.72rem/1 var(--mono); letter-spacing: 0.16em; text-transform: uppercase; color: var(--ember); }
.lead { display: grid; gap: 18px; }
.lead p { color: var(--muted); }
.ask { border-left: 2px solid var(--ember); padding-left: 16px; color: var(--ink) !important; }
.film { display: grid; grid-template-columns: minmax(0, 300px) minmax(0, 1fr); gap: 32px; align-items: start; }
.phone { aspect-ratio: 9 / 16; max-width: 100%; border: 1px solid var(--line); border-radius: 18px; overflow: hidden; background: #000; }
.phone video { width: 100%; height: 100%; display: block; object-fit: cover; }
.film-notes { display: grid; gap: 16px; min-width: 0; }
.film-notes p { color: var(--muted); }
dl { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 24px; margin: 0; }
dl div { border-top: 1px solid var(--line); padding-top: 8px; }
dt { font: 500 0.7rem/1.4 var(--mono); letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); }
dd { margin: 2px 0 0; font: 500 1rem/1.4 var(--mono); font-variant-numeric: tabular-nums; }
.act { display: grid; gap: 14px; }
.act header { display: grid; gap: 6px; }
.blurb { color: var(--muted); font-style: italic; }
.act img { display: block; width: 100%; height: auto; border: 1px solid var(--line); border-radius: 6px; }
.table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 6px; }
table { border-collapse: collapse; width: 100%; min-width: 640px; font-size: 0.92rem; }
th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font: 500 0.7rem/1.4 var(--mono); letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); background: var(--panel); position: sticky; top: 0; }
td.id { font: 500 0.85rem/1.5 var(--mono); color: var(--ember); white-space: nowrap; }
td.num { font-family: var(--mono); font-variant-numeric: tabular-nums; white-space: nowrap; color: var(--muted); }
.tag { font: 500 0.72rem/1 var(--mono); letter-spacing: 0.08em; color: var(--god); border: 1px solid var(--god); border-radius: 3px; padding: 2px 5px; white-space: nowrap; }
a { color: inherit; }
a:focus-visible, video:focus-visible { outline: 2px solid var(--ember); outline-offset: 3px; }
@media (max-width: 720px) { .film { grid-template-columns: minmax(0, 1fr); } .phone { max-width: 300px; } dl { grid-template-columns: minmax(0, 1fr); } }
</style>
<main class="wrap">
  <section class="lead">
    <p class="eyebrow">Checkpoint 2 · key stills</p>
    <h1>REALM BREACH <span>·</span> THE FINAL BATTLE</h1>
    <p>One graded key still for every shot of the 74.7-second vertical trailer, in shot order, with titles and
    subtitles exactly as the edit places them, and safe zones respected. Characters, sets, lighting and effects are
    all generated in code.</p>
    <p class="ask">Reply OK to start the animation renders, or name the shots you want changed.</p>
  </section>
  {{VIDEO}}
  {{ACTS}}
  <section class="act">
    <header><p class="eyebrow">All {{N}} shots</p><h2>Shot list</h2></header>
    <div class="table-wrap"><table>
      <thead><tr><th>Shot</th><th>Time</th><th>Beat</th><th>Frames</th><th>Lens</th><th>Subject</th></tr></thead>
      <tbody>{{ROWS}}</tbody>
    </table></div>
  </section>
</main>
"""
page = (page.replace("{{VIDEO}}", video_html).replace("{{ACTS}}", "".join(acts_html))
        .replace("{{N}}", str(len(shots))).replace("{{ROWS}}", "".join(rows)))
open(os.path.join(a.out, "index.html"), "w").write(page)
print("wrote", a.out, "sheets", sheets, "video", has_video)
