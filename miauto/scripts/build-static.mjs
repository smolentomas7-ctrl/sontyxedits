/**
 * Builds the drag-and-drop version of the site into `out/`.
 *
 * Netlify's manual deploy publishes the folder you give it and runs no build,
 * so that folder has to be plain files. `output: "export"` produces them — but
 * it cannot coexist with a route handler, so `app/api` is moved aside for the
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
import { existsSync, renameSync, rmSync, cpSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const api = join(root, "app", "api");
const parked = join(root, ".api-parked");

function restore() {
  if (existsSync(parked)) {
    rmSync(api, { recursive: true, force: true });
    renameSync(parked, api);
  }
}

process.on("exit", restore);
process.on("SIGINT", () => { restore(); process.exit(130); });

try {
  rmSync(join(root, "out"), { recursive: true, force: true });
  rmSync(parked, { recursive: true, force: true });

  if (existsSync(api)) renameSync(api, parked);

  execSync("tsx scripts/build-knowledge.ts", { stdio: "inherit" });
  execSync("next build", {
    stdio: "inherit",
    env: { ...process.env, STATIC_EXPORT: "1", NEXT_PUBLIC_STATIC_CHAT: "1" },
  });

  // Netlify reads these from the published folder, not from the repo root.
  for (const file of ["_redirects", "_headers"]) {
    const from = join(root, "public", file);
    if (existsSync(from)) cpSync(from, join(root, "out", file));
  }

  console.log("\nStatic site written to out/ — this is the folder to drag into Netlify.");
} finally {
  restore();
}
