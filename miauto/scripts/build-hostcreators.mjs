/**
 * Builds the upload package for traditional Apache hosting (HostCreators).
 *
 * The Netlify bundle cannot simply be re-uploaded there. Three things in it are
 * Netlify's and nobody else's:
 *
 *   _redirects   sent / to /sk. Apache ignores the file, so the root address
 *                has no page at all — which is the 403 Forbidden.
 *   _headers     the security headers. Same: ignored.
 *   __forms.html Netlify Forms. The service does not exist on this host.
 *
 * And one thing about the export itself: Netlify serves out/sk.html at /sk, and
 * Apache does not. Worse, /sk/kontakt there is a *directory* holding payload
 * files and no index, which is a second 403 waiting to happen. So this build
 * runs with trailingSlash, which writes out/sk/kontakt/index.html instead and
 * lets DirectoryIndex serve it with no rewrite rules involved.
 *
 *   node scripts/build-hostcreators.mjs
 */
import { execSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";

const projectRoot = process.cwd();
const repoRoot = resolve(projectRoot, "..");
const outDir = join(projectRoot, "out");
const deployDir = join(repoRoot, "hostcreators-deploy");
const assets = join(projectRoot, "deploy-assets");

const SITE_URL = "https://autoservisruzomberoksro.sk";

/** Netlify's own files. They are noise at best on another host. */
const NETLIFY_ONLY = ["_redirects", "_headers", "__forms.html"];

const step = (n, text) => console.log(`\n[${n}] ${text}`);

// ── 1. build ────────────────────────────────────────────────────────────────
step(1, `Building the static export for ${SITE_URL}`);
execSync("node scripts/build-static.mjs", {
  stdio: "inherit",
  env: {
    ...process.env,
    NEXT_PUBLIC_SITE_URL: SITE_URL,
    NEXT_PUBLIC_TRAILING_SLASH: "1",
    // Netlify Forms does not exist here; the PHP handler takes its place.
    NEXT_PUBLIC_FORM_ENDPOINT: "/contact.php",
  },
});

// ── 2. copy ─────────────────────────────────────────────────────────────────
step(2, `Assembling ${relative(repoRoot, deployDir)}/`);
rmSync(deployDir, { recursive: true, force: true });
mkdirSync(deployDir, { recursive: true });
cpSync(outDir, deployDir, { recursive: true });

for (const file of NETLIFY_ONLY) {
  const path = join(deployDir, file);
  if (existsSync(path)) {
    rmSync(path);
    console.log(`    removed ${file} (Netlify only)`);
  }
}

// ── 3. the Apache pieces ────────────────────────────────────────────────────
step(3, "Adding .htaccess and contact.php");
cpSync(join(assets, "htaccess"), join(deployDir, ".htaccess"));
cpSync(join(assets, "contact.php"), join(deployDir, "contact.php"));

// ── 4. the root entry point ─────────────────────────────────────────────────
// .htaccess redirects / to /sk/ before this file is ever reached. It exists for
// the case where mod_rewrite is unavailable: then Apache falls back to
// DirectoryIndex, finds this, and the visitor still arrives at the site rather
// than at a 403. noindex, because the page a crawler should hold is /sk/.
step(4, "Writing the root index.html");
writeFileSync(
  join(deployDir, "index.html"),
  `<!doctype html>
<html lang="sk">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="robots" content="noindex" />
    <link rel="canonical" href="${SITE_URL}/sk/" />
    <meta http-equiv="refresh" content="0; url=/sk/" />
    <title>M.I.Auto s.r.o. — Autoservis Ružomberok</title>
    <style>
      html { background: #0b0d0e; color: #f2f4f5; font-family: system-ui, sans-serif; }
      body { display: grid; place-items: center; min-height: 100svh; margin: 0; }
      a { color: #ff7a3d; }
    </style>
  </head>
  <body>
    <p>Pokračujte na <a href="/sk/">autoservis v Ružomberku</a>.</p>
    <script>location.replace('/sk/');</script>
  </body>
</html>
`,
  "utf8",
);

// ── 5. checks that decide whether this is shippable ─────────────────────────
step(5, "Verifying the package");
const problems = [];

const indexPath = join(deployDir, "index.html");
if (!existsSync(indexPath)) problems.push("no index.html at the root");

const walk = (dir) =>
  readdirSync(dir).flatMap((name) => {
    const full = join(dir, name);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
const files = walk(deployDir);

// every page is a directory index, which is what Apache serves natively
const pages = files.filter((f) => f.endsWith(`${sep}index.html`));
if (pages.length < 25) problems.push(`expected 24 pages plus the root, found ${pages.length}`);

// a page still sitting as a flat .html means trailingSlash did not take effect
const flat = files.filter(
  (f) => f.endsWith(".html") && !f.endsWith(`${sep}index.html`) && !/404\.html$/.test(f),
);
if (flat.length > 0) {
  problems.push(`flat .html pages Apache will not serve at their link target: ${flat.length}`);
}

for (const file of NETLIFY_ONLY) {
  if (existsSync(join(deployDir, file))) problems.push(`${file} is still in the package`);
}

// every asset referenced by the home page must actually be in the package
const home = readFileSync(join(deployDir, "sk", "index.html"), "utf8");
const refs = [...home.matchAll(/(?:src|href)="(\/[^"]+)"/g)]
  .map((m) => m[1].split("?")[0])
  .filter((p) => /\.(js|css|woff2?|avif|webp|jpe?g|png|svg|ico|webmanifest)$/.test(p));
const missing = [...new Set(refs)].filter((p) => !existsSync(join(deployDir, p)));
if (missing.length > 0) problems.push(`assets referenced but absent: ${missing.join(", ")}`);

// nothing may point at a development server or at the old host
const offenders = new Set();
for (const file of files.filter((f) => /\.(html|js|css|xml|txt|json|webmanifest)$/.test(f))) {
  const text = readFileSync(file, "utf8");
  if (/localhost:\d+|127\.0\.0\.1:\d+/.test(text)) offenders.add(`${relative(deployDir, file)} → localhost`);
  if (/\.netlify\.app/.test(text)) offenders.add(`${relative(deployDir, file)} → netlify.app`);
}
if (offenders.size > 0) problems.push(`development or Netlify references: ${[...offenders].join(", ")}`);

execSync(`node scripts/check-canonicals.mjs "${deployDir}" ${SITE_URL}`, { stdio: "inherit" });

if (problems.length > 0) {
  console.error("\n  ✖ the package is not shippable:\n");
  for (const p of problems) console.error(`      ${p}`);
  process.exit(1);
}

const bytes = files.reduce((sum, f) => sum + statSync(f).size, 0);
console.log(`    ✓ ${files.length} files, ${(bytes / 1024 / 1024).toFixed(1)} MB`);
console.log(`    ✓ index.html at the root, ${pages.length - 1} pages as directory indexes`);
console.log(`    ✓ no Netlify-only files, no development references`);

// ── 6. the archive, with the files at its root ──────────────────────────────
step(6, "Creating hostcreators-deploy.zip");
const zipPath = join(repoRoot, "hostcreators-deploy.zip");
rmSync(zipPath, { force: true });
// -r from inside the directory, so index.html sits at the root of the archive
// rather than inside a hostcreators-deploy/ folder.
execSync(`cd "${deployDir}" && zip -rq "${zipPath}" . -x '.DS_Store'`, { stdio: "inherit", shell: "/bin/bash" });
console.log(`    ✓ ${relative(repoRoot, zipPath)} (${(statSync(zipPath).size / 1024 / 1024).toFixed(1)} MB)`);
console.log(`\nUpload the CONTENTS of ${relative(repoRoot, deployDir)}/ to the site's web root.\n`);
