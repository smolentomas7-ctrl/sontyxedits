---
name: miauto-web
description: "Master skill for the M.I.Auto s.r.o. automotive service website (Ružomberok, Slovakia) and for any new website brief. Covers the project facts, the non-negotiable rules, the design system, motion, images, forms, SEO, deployment to Netlify and HostCreators, and the creative-interview process for new sites. Use whenever working on this website, its SEO, its deployment, or when starting a new web design brief."
---

# miauto-web — master skill

## 0. What this skill is for

This skill **prepares production prompts for Claude Code**. When the user asks for a
website change, the output is a ready-to-paste Claude Code prompt that follows the
format in part 0.1. It is not a place to start coding by default. The skill gives
Claude Code the facts, rules and verification steps, so the prompt is complete on its
own.

Two kinds of request:

1. **M.I.Auto website** (`miauto/` in this repository). The default. The project is
   already built. Turn the request into a Claude Code prompt that uses the facts and
   rules below.
2. **New website briefs** for any other client. Run the creative interview in part 10
   first. Its final creative brief then becomes the input for the Claude Code prompt.

### 0.1 Prompt format

Every production prompt for Claude Code contains these sections, in this order:

1. **Goal**: one or two sentences on the outcome, in plain language.
2. **Context**: the relevant facts from part 2, and the state from `SPRAVA.md`.
   Only what this task needs.
3. **Scope**: files or areas that may change. Name what must NOT change.
4. **Constraints**: the hard rules from part 1 that apply to this task.
5. **Steps**: numbered, concrete actions. Include the commands to run.
6. **Verification**: the checks from part 8 that apply, plus the task-specific checks.
   Build output must be inspected, not only the source.
7. **Deliverables**: commit to `claude/miauto-website-build-7e1gr6`, changed files
   listed, deploy steps if a package is produced.
8. **Report format**: Slovak report with what changed, what was verified, what was
   not verified and why, and the exact manual steps left for the client.

Rules for writing the prompt:

- Write it in English, so Claude Code reads it cleanly. The client-facing text inside
  the site stays in Slovak and English as the project requires.
- Do not put secrets, API keys or passwords in the prompt.
- Do not put any model identifier into the prompt output, commit messages or repository
  files.
- If a fact is missing (for example an IČO), the prompt says the item stays missing. It
  must not ask Claude Code to invent it.

Working language with the client: **Slovak**. Reports to the client are in Slovak.
Code, comments and commit messages stay in English.

---

## 1. Hard rules (never break these)

- **Do not invent business data.** No IČO, DIČ, commercial-register entry, GPS
  coordinates, prices, reviews, ratings, opening hours, certifications, graduation
  dates, school names, awards, supported-engine lists, workshop equipment, customer
  counts or references. Missing data stays missing. Fields for it exist in
  `config/miauto.ts` and render only once filled.
- **No placeholders.** No lorem ipsum, "coming soon", grey boxes instead of photos,
  or bracketed `[TBD]` text. If there is no material for a block, the block does not
  render.
- **Every Slovak string needs a full English translation** (`content/sk.ts` and
  `content/en.ts`).
- **Accessibility is required**: keyboard operable, visible focus, correct ARIA,
  `prefers-reduced-motion` respected, contrast at least WCAG AA.
- **No heavy dependencies.** Animation is CSS transforms and opacity plus SVG, with
  small hand-written JavaScript. No animation libraries.
- **No misleading claims.** Never guarantee power gains from chip tuning.
- **Never state, describe or suggest removing DPF, EGR or AdBlue.** That is illegal on
  EU road vehicles.
- **Do not claim GDPR compliance** for the privacy document. Say it needs legal review.
- **`ANTHROPIC_API_KEY` is server-only.** Never a `NEXT_PUBLIC_` variable, never in
  client code, never in the repository.
- **Never edit the client's original photographs in place.** Originals live in
  `assets-originals/` (gitignored). Never upscale an image.
- **Never describe a stock photograph as the client's own premises.** Images carry
  `origin: "own" | "stock"` in the manifest, and alt text describes the activity, not
  the premises, unless the image is confirmed as their own.
- **Never publish a page that impersonates a person or organisation**, and never
  invent reviews or testimonials.
- **Do not change DNS, domain registration or SSL settings** unless the client asks
  explicitly. Focus on website files.
- **Do not claim something is fixed or live until it was verified** on the built
  output, and on the live domain when that is possible. Say clearly when it was not.
- **Report honestly.** If a test could not run (no mail server, no access to the
  live domain, no PHP), say so and say how the user can verify it.

---

## 2. M.I.Auto — facts (use only these)

| Field | Value |
|---|---|
| Legal name | M.I.Auto s.r.o. |
| Short name | M.I.Auto |
| Type | Independent car repair shop (autoservis) |
| Address | Sládkovičova 2528/108, 034 01 Ružomberok, Žilinský kraj, Slovakia |
| Phone | +421 918 918 109 (primary call-to-action everywhere) |
| Published email | ivankubis96@centrum.sk |
| Form recipient | ivanautoservisrk@gmail.com (`site.formRecipient`) |
| Owners | Marián Hrnčiar, Ivan Kubis (co-owner). Portraits exist, consent is pending |
| Partner | Castrol Service |
| Opening hours | Mon–Fri 07:00–17:00, lunch break 12:00–13:00 every working day; Sat and Sun closed |
| Services | Diagnostika vozidiel, čipovanie ECU, geometria kolies, pneuservis, elektroinštalácia vozidiel VW koncernu, výmena rozvodov (2.0 TDI, 3.0 TDI), servis klimatizácie |
| Languages | Slovak (default, `/sk`), English (`/en`) |
| Canonical domain | `https://autoservisruzomberok.com` (`PRODUCTION_URL` in `config/miauto.ts`) |
| Alternate domain | autoservisruzomberoksro.sk, used for HostCreators. Decision pending from the client |

**Do not use "Autoservis" + "Ružomberok" keywords stuffing.** Mention the town
naturally, once per title and description.

### Blockers for launch (client action, not code)

1. IČO and the commercial-register entry (§ 3a Obchodného zákonníka). Required.
2. Written consent from both owners to publish their photographs.
3. Legal review of the privacy document.
4. Choose one canonical domain and redirect the other.
5. A real mailbox on the site's own domain for `MAIL_FROM` in `contact.php`.
6. Google Search Console: add the domain and submit `sitemap.xml`.

### Photography status

- Own photographs: `about-01..03`, `diagnostika`, `klimatizacia`, `owner-01/02`.
- Stock or illustrative: `hero` (the workshop photo the client supplied, marked
  `stock` until they confirm it is their workshop), and the service photos for ECU,
  geometry, tyres, electrics and timing belts.
- The client may replace stock photos later. The pipeline keeps the same slot names.

---

## 3. Technical architecture

- **Framework**: Next.js 16 (App Router), React 19, TypeScript 5.9 strict with
  `noUncheckedIndexedAccess`, Tailwind CSS 4 through `@tailwindcss/postcss`.
- **Project root**: `miauto/`. The Git repository root also contains an unrelated site
  (Sontyx). Never touch it and never deploy it.
- **Branch**: `claude/miauto-website-build-7e1gr6`. Push there and nowhere else.
- **Routing**: `app/[locale]/…`. Twelve routes per locale, 24 pages in total.
  Locale on `<html lang>` comes from the layout inside `[locale]`.
- **Content**: `content/sk.ts` and `content/en.ts` (typed by `content/types.ts`).
  Brand and contact data: `config/miauto.ts`. Images: `config/images.ts`.
- **Helpers**: `lib/i18n.ts` (`ROUTES`, `pageUrl`, `canonicalFor`, `pageSeo`),
  `lib/motion.ts` (`useReveal`, `useParallax`, press handlers, reduced-motion hook),
  `lib/forms.ts` (form submission and validation), `lib/jsonld.ts` (structured data),
  `lib/hours.ts` (open / closed / lunch state).
- **Components**: `components/home`, `components/about`, `components/ui`,
  `components/widgets` (seven interactive service widgets, including the dyno and
  tyre widgets), `components/contact`, `components/chat`, `components/brand`.

### Commands

| Command | Purpose |
|---|---|
| `npm run dev` | Development server |
| `npm run build` | Server build (`next build`) |
| `npm run typecheck` | `tsc --noEmit`. Must pass before any push |
| `npm run build:static` | Static export to `out/` for Netlify drag-and-drop. Runs the canonical guard |
| `npm run build:hostcreators` | Apache package to `../hostcreators-deploy/` and `../hostcreators-deploy.zip` |
| `npm run images` | Runs `scripts/process-images.py` (Python + Pillow) |
| `npm run evals` | Chat evaluation cases |

`npm run lint` was removed. `next lint` no longer exists in Next 16 and the project
has no ESLint config. Use `typecheck`.

### Design tokens (do not change)

`--bg #0b0d0e`, `--surface #14181a`, `--surface-hover #1c2124`, `--border #262d31`,
`--text #f2f4f5`, `--text-muted #94a1a8`, `--accent #ff7a3d`, `--accent-hover #ff9158`,
`--accent-soft #ff7a3d1f`, `--accent-ink #0b0d0e`, `--focus #ff9158`,
`--danger #f87171`, `--success #4ade80`.

Motion tokens: `--ease-ios cubic-bezier(.32,.72,0,1)`, `--ease-ios-in cubic-bezier(.4,0,.2,1)`,
`--dur-press 110ms`, `--dur-release 260ms`, `--dur-reveal 420ms`, `--dur-state 180ms`.

Tailwind v4 gotchas:
- `text-[var(--x)]` parses as font-size. Write `text-[color:var(--x)]`.
- Arbitrary `object-position` is ambiguous. Use a CSS custom property (`--hero-focus`).
- Unlayered CSS beats all layered CSS. Base element styles belong in `@layer base`.

### Motion system (already built, extend it, do not replace it)

- Press: `.tappable`, scale via `--press-scale`. Buttons use 0.975. Cards 0.985.
- Hover lift on buttons only: `.tappable--lift`, `scale(1.012)`, gated on
  `(hover: hover) and (pointer: fine)`.
- Reveal: `.reveal` and `.reveal-image` with staggered delays.
- Cursor parallax: `useParallax` in `lib/motion.ts`, wrapped by
  `components/ui/Parallax.tsx`. One rAF loop writes two custom properties and stops at
  rest. The pointer is tracked on the nearest `[data-parallax-area]` ancestor or the
  static wrapper, **never on the moving layer**, because the moving layer steps out
  from under the cursor. Off on coarse pointers and under reduced motion. Applied to
  the hero, the service showcase image and the About interior image. Not on cards.
- Global `prefers-reduced-motion` kill switch exists. Keep it.

### Dyno physics (used by the dyno widget)

`P[kW] = M[Nm] × n[rpm] / 9549`. Only torque is defined by anchor points. Power is
derived. Do not promise power gains from any modification.

---

## 4. Images

Pipeline: `scripts/process-images.py`. It reads from `assets-originals/`, strips EXIF,
pre-crops, redacts where needed, crops to the slot ratio and resizes. It writes
full, card and thumb sizes in WebP, AVIF and JPEG, with budgets of 200, 80 and 40 KB,
and writes `public/assets/miauto/manifest.json` (width, height, placeholder colour,
origin, upscaled flag).

- Hero file: `hero-workshop.jpg` → `miauto-hero.*` at 1920×1080, `origin: "stock"`.
- **Next's image optimiser caches by filename.** After replacing a photo under the
  same name, clear `.next/cache/images` or the old file keeps showing in development.
- Every `<img>` needs meaningful alt text in the page language, or `alt=""` when
  decorative. Do not keyword-stuff alt text.

---

## 5. Forms, chat and privacy

### Contact form

Two deployment modes, chosen at build time by `NEXT_PUBLIC_FORM_ENDPOINT`:

- **Netlify** (default). POST to `/__forms.html`. Netlify Forms stores the submission
  and emails only if a notification exists in the Netlify dashboard. The form
  registration file must keep `MIAUTO_FORM_REGISTRATION_PAGE`: `lib/forms.ts` treats a
  response containing that sentinel as a failed submission.
- **HostCreators / Apache**. POST to `/contact.php` (`deploy-assets/contact.php`).
  Server-side validation, header-injection protection, throttling per IP, JSON answer.
  `MAIL_FROM` must be a mailbox on the site's own domain. Gmail there causes silent
  rejection.

Front-end rules that must stay: a success message only when the server accepted the
message; a double-submit guard while sending; the honeypot field `bot-field` must not
be `display: none`; a minimum fill time of 3 s; fields are kept after an error.

The throttle is recorded only after a message is actually sent.

### Chat assistant

The grounded assistant needs a server route (`app/api/chat`) and the Anthropic SDK
with `ANTHROPIC_API_KEY` set server-side only. Static hosts run the scripted tier in
the browser. Say this to the client when relevant.

### Privacy document

Describes: the form data collected, legal basis (legitimate interest in answering an
enquiry), Netlify as processor, Google (Gmail) as the further processor for the
forwarded email, 12-month retention, access limited to the owners. It must not claim
GDPR compliance. It needs legal review before launch.

---

## 6. SEO and crawl configuration

- **Canonical**: every page self-canonical, absolute, using `pageUrl(locale, route)`.
  Exactly one canonical per page. Slovak pages never canonical to English or the
  reverse. Never canonical to the home page.
- **Root**: `/` is a 301 to `/sk/` (Netlify `_redirects`, or `.htaccess` on Apache).
  Do not link to the bare root from the site.
- **hreflang**: `sk`, `en`, and `x-default` pointing at the Slovak version. In the
  `<head>`, not via JavaScript.
- **Sitemap**: `app/sitemap.xml/route.ts` writes the file by hand. Exactly 24
  `<url><loc>` entries in the sitemaps.org namespace. No `lastmod`, `changefreq` or
  `priority`, because nothing verifiable supports them. No hreflang inside the sitemap
  (it is already in the HTML). Never list redirects, preview URLs or localhost.
- **robots.txt**: `Allow: /`, a `Sitemap:` line to the canonical sitemap URL, and a
  `Host:` line. The `Disallow: /__forms.html` line only exists in the Netlify build.
- **noindex** only on the 404 pages and the Netlify form registration file.
- **Structured data**: `AutoRepair` with name, address, phone, email, opening hours
  (split around the lunch break), map link, owners. No ratings, reviews, price range or
  coordinates unless the client supplies them.
- **Open Graph**: `og:url` equals the canonical. `pageSeo()` builds metadata and
  OG tags from one source.
- **Title and description**: unique per page, Slovak and English. The home page:
  "Autoservis Ružomberok | M.I.Auto — opravy a servis vozidiel".
- **Build guard**: `scripts/check-canonicals.mjs` runs at the end of the static build
  and fails the build if any page lacks exactly one correct canonical. Keep it.

---

## 7. Deployment

### Netlify (drag-and-drop, the existing deploy)

1. `cd miauto && npm run build:static`
2. Unzip `deploy/miauto-netlify-drag-and-drop.zip` (or take `out/`) and drag the
   **contents** of the folder into Netlify Deploys. Not the folder itself.
3. Netlify runs no build in drag-and-drop, so no functions. Chat falls back to the
   scripted tier. The form needs a notification set up in Netlify → Forms → `dopyt`.

Git-based Netlify deploy also exists (`netlify.toml`, the Next.js plugin, base
`miauto`). It supports the chat route and server features.

### HostCreators (Apache, WebFTP)

1. `cd miauto && npm run build:hostcreators`. This builds with the production domain,
   `NEXT_PUBLIC_TRAILING_SLASH=1` and `NEXT_PUBLIC_FORM_ENDPOINT=/contact.php`. It
   removes Netlify-only files, adds `.htaccess`, `contact.php` and a root `index.html`,
   checks the package and writes `hostcreators-deploy.zip` with files at the archive
   root.
2. Upload the **contents** of `hostcreators-deploy/` to the web root (`public_html`,
   `www` or `web`). Delete the old test `index.html` that says "Test".
3. Turn on **show hidden files** in WebFTP. `.htaccess` is a dotfile and will not
   upload or display otherwise.
4. Check that `https://<domain>/` redirects to `/sk/`.
5. Confirm with HostCreators that `mod_rewrite`, `mod_headers` and PHP are enabled.

Why the 403 happened: the Netlify build had no `index.html` at the root (the redirect
lived in `_redirects`, which Apache ignores), and every page was stored as a directory
without an index file. Fixed by trailing-slash output plus `.htaccess`.

### Verifying a deployment without live access

Serve the output with a server that behaves like the target (Apache rules:
`DirectoryIndex`, 403 on index-less directories, `mod_dir` slash redirect), then crawl
from `/` following links in a headless browser, and check status, one `<h1>`, one
canonical and zero failed requests. Report that this is a simulation, not the live
host.

---

## 8. Verification checklist (run before every hand-off)

- [ ] `npm run typecheck` passes.
- [ ] `npm run build:static` (or `build:hostcreators`) passes, including the canonical guard.
- [ ] 24 pages, each with one `h1`, one canonical, three hreflang links.
- [ ] Sitemap: valid XML, 24 `<url><loc>` entries, all 200, none redirecting.
- [ ] `robots.txt` points to the correct sitemap.
- [ ] No `noindex` on indexable pages. No `localhost`, `netlify.app` or dev references in output.
- [ ] Root redirects to `/sk/`.
- [ ] Contact form: validation, double-submit guard, success only on server acceptance.
- [ ] Motion: parallax on a fine pointer only, press states, reduced motion holds.
- [ ] Mobile width (390 px): no horizontal overflow, tap targets 44 px or more.
- [ ] Console: no errors.
- [ ] Commit and push to `claude/miauto-website-build-7e1gr6` with a descriptive message.
- [ ] Final report in Slovak: what changed, what was verified, what was not, and the
      exact upload or deploy steps.

---

## 9. Ongoing decisions and open items

- Which domain is canonical: `autoservisruzomberok.com` or `autoservisruzomberoksro.sk`.
- Which mailbox sends form mail (`MAIL_FROM`) and whether Netlify notifications exist.
- Owner consent for photographs. Legal review of the privacy text.
- IČO and commercial-register entry.
- Whether the client confirms the hero photo as their own workshop (`origin` → `own`).
- Whether to add `lastmod` to the sitemap. Only once page content changes are recorded.
- Optional: XSL stylesheet for a readable sitemap in browsers. Not added; it would
  change the generator for cosmetic benefit only.

---

## 10. New website briefs — creative interview (for other clients)

Use this part only for a **new** website, or a redesign that asks for creative
direction. Do not use it for M.I.Auto, which is already designed.

### Role

Senior web designer, creative director, UX/UI designer and art director. The first job
is to understand what the site should look like. This is not a prompt for generating a
website.

### Hard rule: generate nothing without permission

- Do not generate images, videos, design mock-ups or a website without explicit
  approval.
- Before any paid generation, state:
  - what will be generated,
  - why it is needed,
  - the model,
  - the estimated cost in tokens or credits. If the price is not known, say so and say
    it must be checked in the client's own account. Never invent prices.
  - what the result will be.
- Then ask: **"Môžem túto generáciu spustiť?"** (Can I start this generation?)
  Proceed only on a clear yes.
- Generate few images. Never create several near-identical images.

### Interview blocks

Ask in small groups, summarise after each block, then continue. Never ask 30 questions
at once. Offer choices when the client does not know.

- **A. Basics**: name of the business or product, slogan, what is sold or offered, the
  main goal (sales, leads, portfolio, service presentation, bookings, e-shop, brand,
  contacts). Target visitor: who, B2B or B2C, age, expertise, main problem, why choose
  this business.
- **B. Visual identity**: main colours and any existing brand colours, light or dark,
  accent colours, mood (luxury, technological, natural, energetic, minimal). If the
  client cannot choose, offer at most three colour directions. Logo, existing identity,
  preferred typeface, whether the site should feel part of an existing brand.
- **C. Style**: offer options such as minimalist, futuristic, technological, luxury,
  brutalist, editorial, Apple-style, dark mode, clean white, retro-futurist, industrial,
  elegant, playful, cinematic, 3D immersive. Ask: "If you had to describe the site in
  three words, what would they be?"
- **D. References**: a site they like, screenshots, Pinterest or Behance boards, specific
  elements they like (hero, animation, navigation, typography, colour, layout, product
  photography, 3D, scroll effects). If there is no reference, write a verbal creative
  direction first (style, colour atmosphere, photo type, graphic elements, typography,
  composition, animation, overall mood). Only then offer a reference image, and only
  with approval.
- **E. Emotion**: what should the visitor feel in the first moment, and which single
  idea or emotion should they keep after five seconds. Examples: "this looks expensive",
  "this firm is professional", "I can trust this firm", "this is simple and pleasant",
  "this is bold and creative".
- **F. Functions**: contact form, e-shop, bookings, gallery, blog, portfolio, login,
  several languages, animations, video, 3D, interactivity, mobile priority. Do not
  offer complex features that do not fit the project.
- **G. Experience**: fast and simple, or cinematic and immersive. Scroll behaviour,
  micro-interactions, reaction to the pointer, smooth scrolling, storytelling flow.
  Ask: "Should the site be mainly practical and simple, or should the browsing itself be
  a big part of the experience?"
- **H. Content**: sections wanted, existing texts, photos, product photos, videos, logo.
  If nothing exists, help build a content plan.

### Follow-up questions (after the blocks)

Fullscreen hero or not; whether the main product is visible immediately; minimal or
bold navigation; large bold or light typography; symmetrical or experimental layout;
more whitespace or denser content; static or dynamic feel; more photography or more
graphics; timeless or trend-following design. Adapt every question to the project.

### Creative brief (final output, Slovak or the client's language)

1. **Project**: name, type, main goal.
2. **Target visitor**: who, what they need, why choose this business.
3. **Main emotion**: what the first five seconds should create.
4. **Visual style**: overall style, atmosphere, layout, composition, typography,
   colour palette.
5. **Hero vision**: what is seen first, where the headline sits, where the product or
   main visual is, background, atmosphere, primary call-to-action.
6. **Visual elements**: photography, 3D, abstract graphics, lines, glow, textures,
   particles, gradients, UI elements.
7. **Animations**: hero, scroll, hover, transitions, micro-interactions. Each must
   support the design, not decorate it.
8. **Functions**: the concrete list.
9. **Section structure**: the proposed order, adapted to the project.

### Generation plan (show before any generation, then ask for approval)

For each generation: what, why, recommended model, estimated cost (or "to be checked"),
expected result. End with: **"Schvaľuješ tento plán a môžem pokračovať s prvou
generáciou?"**

### Communication style

Simple, natural, creative, like an experienced creative director. Avoid jargon. Guide
the client step by step. If the client cannot answer, offer choices. Do not treat the
first answer as final. Keep thinking about what else is needed for a strong site.

---

## 11. How to start a session on this project

1. Read this skill. Check `git status` and the current branch.
2. Read `SPRAVA.md` (handover report) and `README.md` in `miauto/` for the latest state.
3. Run `npm run typecheck` to confirm a clean baseline.
4. Ask the client only for what is missing from section 2 or section 9. Do not re-ask
   answered questions.
5. Make the change, verify on the built output, commit, push to the designated branch.
6. Report in Slovak with the file list, verification results, and the exact next
   manual steps.
