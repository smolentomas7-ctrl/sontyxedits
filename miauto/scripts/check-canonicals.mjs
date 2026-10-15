/**
 * Fails the build if any exported page does not declare itself canonical.
 *
 * This exists because the opposite happened in production: a bundle was built
 * without knowing its own domain, every canonical and hreflang silently
 * dropped out, and Search Console reported the Slovak home page as
 * "Duplicate without user-selected canonical — user-declared canonical: None",
 * picking the redirecting root URL instead. Nothing failed at build time; the
 * absence was only visible weeks later, in Google's index.
 *
 * A missing canonical is not a warning here. It is a broken build.
 *
 *   node scripts/check-canonicals.mjs <outDir> <siteUrl>
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";

const [outDir, siteUrl] = process.argv.slice(2);
if (!outDir || !siteUrl) {
  console.error("usage: check-canonicals.mjs <outDir> <siteUrl>");
  process.exit(2);
}

/** Pages that are not indexable content and carry no canonical by design. */
const SKIP = new Set(["404.html", "__forms.html", "_not-found.html"]);

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    const full = join(dir, name);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

/** out/sk.html -> /sk ;  out/sk/sluzby/x.html -> /sk/sluzby/x */
function urlPathOf(file) {
  const rel = relative(outDir, file).split(sep).join("/");
  return "/" + rel.replace(/\.html$/, "");
}

const pages = walk(outDir).filter(
  (f) => f.endsWith(".html") && !SKIP.has(f.split(sep).pop()) && !f.includes(`${sep}_not-found${sep}`),
);

const problems = [];
for (const file of pages) {
  const html = readFileSync(file, "utf8");
  const head = html.split("</head>", 1)[0];
  const found = [...head.matchAll(/<link rel="canonical" href="([^"]+)"/g)].map((m) => m[1]);
  const expected = `${siteUrl}${urlPathOf(file)}`;

  if (found.length === 0) problems.push(`${urlPathOf(file)} — no canonical`);
  else if (found.length > 1) problems.push(`${urlPathOf(file)} — ${found.length} canonicals`);
  else if (found[0] !== expected) {
    problems.push(`${urlPathOf(file)} — canonical is ${found[0]}, expected ${expected}`);
  }
}

if (problems.length > 0) {
  console.error(`\n  ✖ canonical check failed on ${problems.length} of ${pages.length} pages:\n`);
  for (const p of problems) console.error(`      ${p}`);
  console.error("\n  Nothing is deployable without these. Build aborted.\n");
  process.exit(1);
}

console.log(`  ✓ ${pages.length} pages, each declaring itself canonical under ${siteUrl}`);
