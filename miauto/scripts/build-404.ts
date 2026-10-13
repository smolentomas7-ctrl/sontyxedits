/**
 * Writes `out/404.html` for the static (drag-and-drop) build.
 *
 * Netlify serves that one file for every unmatched URL, and the export cannot
 * produce it from a page: the catch-all route that sends a real 404 status needs
 * a server, so it is parked during the export. The file is written standalone —
 * its own tokens, its own type — because a 404 is the one page that has to work
 * when something else has already gone wrong.
 *
 * It says the same thing in both languages for the same reason the server-side
 * boundary does: nothing here knows which one the visitor was reading.
 */
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { getContent } from "../content";
import { site } from "../config/miauto";

const sk = getContent("sk");
const en = getContent("en");

const escape = (value: string) =>
  value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const html = `<!doctype html>
<html lang="sk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>${escape(sk.notFound.title)} | ${escape(site.legalName)}</title>
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<style>
  :root {
    --bg: #0b0d0e; --surface: #14181a; --border: #262d31;
    --text: #f2f4f5; --text-muted: #94a1a8; --accent: #ff7a3d; --accent-ink: #0b0d0e;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--text);
    font: 400 1rem/1.6 ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    display: grid; place-items: center; min-height: 100svh; padding: 24px;
  }
  main { max-width: 42rem; width: 100%; }
  h1 { font-size: clamp(1.75rem, 6vw, 2.5rem); line-height: 1.1; margin: 0 0 1.25rem; letter-spacing: -0.02em; }
  p { color: var(--text-muted); margin: 0 0 1rem; max-width: 46ch; }
  .en { border-top: 1px solid var(--border); padding-top: 1.75rem; margin-top: 1.75rem; font-size: 0.9375rem; }
  .en strong { color: var(--text); font-weight: 600; }
  .links { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 2rem; }
  a {
    display: inline-flex; align-items: center; height: 52px; padding: 0 24px;
    border-radius: 12px; font-weight: 600; text-decoration: none;
  }
  a.primary { background: var(--accent); color: var(--accent-ink); }
  a.secondary { border: 1px solid var(--border); color: var(--text); }
  a:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
  .phone { color: var(--accent); text-decoration: none; height: auto; padding: 0; display: inline; }
</style>
</head>
<body>
<main>
  <h1>${escape(sk.notFound.title)}</h1>
  <p>${escape(sk.notFound.body)}</p>
  <p class="en" lang="en"><strong>${escape(en.notFound.title)}</strong> ${escape(en.notFound.body)}</p>
  <div class="links">
    <a class="primary" href="/sk">${escape(sk.notFound.cta)}</a>
    <a class="secondary" href="/en" lang="en">${escape(en.notFound.cta)}</a>
  </div>
  <p style="margin-top:2rem">
    <a class="phone" href="${site.phoneHref}">${escape(site.phone)}</a>
  </p>
</main>
</body>
</html>
`;

writeFileSync(join(process.cwd(), "out", "404.html"), html, "utf8");
console.log("out/404.html written (bilingual)");
