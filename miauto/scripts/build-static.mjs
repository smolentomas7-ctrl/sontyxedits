/**
 * Builds the drag-and-drop version of the site into `out/`.
 *
 * Netlify's manual deploy publishes the folder you give it and runs no build,
 * so that folder has to be plain files. `output: "export"` produces them — but
 * it cannot coexist with a route handler or with a route that is only rendered
 * on request, so `app/api` and the 404 catch-all are moved aside for the
 * duration of the build and put straight back afterwards, including on failure.
 *
 * What this build loses: the grounded chat tier, because there is no server to
 * hold the API key. The assistant falls back to its scripted tier running in the
 * browser. Everything else — all 24 pages, the enquiry form via Netlify Forms,
 * the map, the signature interaction — works exactly as in the server build.
 *
 *   npm run build:static
 */
import { execSync } from "node:child_process";
import { existsSync, readFileSync, renameSync, rmSync, cpSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();

/**
 * Directories that cannot exist during an export, with the name each is parked
 * under while the build runs.
 *   app/api            — a route handler needs a server
 *   app/[locale]/[...rest] — renders only on request, to send a real 404 status
 */
const PARKED = [
  [join(root, "app", "api"), join(root, ".parked-api")],
  [join(root, "app", "[locale]", "[...rest]"), join(root, ".parked-catchall")],
];

function restore() {
  for (const [live, parked] of PARKED) {
    if (existsSync(parked)) {
      rmSync(live, { recursive: true, force: true });
      renameSync(parked, live);
    }
  }
}

process.on("exit", restore);
process.on("SIGINT", () => { restore(); process.exit(130); });

try {
  rmSync(join(root, "out"), { recursive: true, force: true });
  for (const [live, parked] of PARKED) {
    rmSync(parked, { recursive: true, force: true });
    if (existsSync(live)) renameSync(live, parked);
  }

  execSync("tsx scripts/build-knowledge.ts", { stdio: "inherit" });
  execSync("next build", {
    stdio: "inherit",
    env: { ...process.env, STATIC_EXPORT: "1", NEXT_PUBLIC_STATIC_CHAT: "1" },
  });

  // Netlify serves this for every unmatched URL; the export cannot produce it.
  execSync("tsx scripts/build-404.ts", { stdio: "inherit" });

  // Netlify reads these from the published folder, not from the repo root.
  for (const file of ["_redirects", "_headers"]) {
    const from = join(root, "public", file);
    if (existsSync(from)) cpSync(from, join(root, "out", file));
  }

  console.log("\nStatic site written to out/ — this is the folder to drag into Netlify.");

  // Same precedence as config/miauto.ts, with the default read back out of it so
  // the domain is written down in exactly one place.
  const fallback = /PRODUCTION_URL = "([^"]+)"/.exec(
    readFileSync(join(root, "config", "miauto.ts"), "utf8"),
  )?.[1];
  const builtFor = (
    process.env.NEXT_PUBLIC_SITE_URL ??
    process.env.URL ??
    fallback ??
    ""
  ).replace(/\/$/, "");
  const local = /^https?:\/\/(localhost|127\.0\.0\.1|\[::1\])(:|\/|$)/.test(builtFor);

  console.log(`Canonical address baked into this build: ${builtFor || "(none)"}`);
  if (local || !builtFor) {
    console.log(
      [
        "",
        "  ⚠  That is not a public address, so canonical links, hreflang, the",
        "     sitemap and the structured-data URLs are omitted from this build.",
        "     The pages still work and are indexable; they simply do not name a",
        "     canonical URL.",
        "",
        "     Build it again with the real domain:",
        "       NEXT_PUBLIC_SITE_URL=https://autoservisruzomberok.com npm run build:static",
        "",
      ].join("\n"),
    );
  } else {
    console.log(
      "  sitemap.xml, robots.txt, canonicals, hreflang and og:url all use it.",
    );
    // Not a warning: a page that does not name itself canonical is how this site
    // ended up reported as a duplicate of its own redirecting root URL.
    execSync(`node scripts/check-canonicals.mjs out ${builtFor}`, { stdio: "inherit" });
    console.log("");
  }
} finally {
  restore();
}
