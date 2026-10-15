# M.I.Auto s.r.o. — website

Marketing site for an independent car repair workshop in Ružomberok, Slovakia.
Next.js (App Router) + TypeScript, Tailwind CSS, deployed to Netlify.

Slovak is the primary language, English a secondary version. 12 routes per
locale, 24 in total.

> This project lives in `miauto/` inside the repository. The repository root
> holds an unrelated static site (Sontyx) that this project does not touch.

---

## 1. What this is, and how to run it locally

```bash
cd miauto
npm install
npm run dev          # http://localhost:3000  -> redirects to /sk
```

Other scripts:

| Command | What it does |
|---|---|
| `npm run build` | Production build. Runs `prebuild` first, which regenerates the chat knowledge. |
| `npm start` | Serves the production build. |
| `npm run typecheck` | `tsc --noEmit`, strict mode. |
| `npm run knowledge` | Regenerates `content/knowledge.generated.ts` from `content/`. |
| `npm run evals` | Runs the 50 chat golden cases. Exits non-zero on a failure. |
| `npm run images` | Re-runs the image pipeline over `assets-originals/`. |

---

## 2. How to change the text

**All copy lives in `content/sk.ts` and `content/en.ts`.** Nothing else contains
visible prose. Both files are typed against the single interface in
`content/types.ts`, so if you add a string to one language and forget the other,
`npm run typecheck` fails — it can never silently fall back to Slovak.

### Worked example: changing the home page headline

Open `content/sk.ts` and find:

```ts
  home: {
    heroTitle: "Autoservis v Ružomberku",
    heroTitleSecond: "Diagnostika, elektronika, rozvody.",
```

Change `heroTitleSecond` to `"Diagnostika, elektronika, klimatizácia."`, then do
the same in `content/en.ts`:

```ts
  home: {
    heroTitle: "Car workshop in Ružomberok",
    heroTitleSecond: "Diagnostics, electronics, air conditioning.",
```

Save. In dev the page updates immediately. **Then run `npm run knowledge`** if
you changed anything on a service page, the About page, the FAQ or the contact
details — that is what keeps the chat assistant's answers in step with the site.
`npm run build` does it for you automatically.

Word-count targets the existing copy follows: hero paragraph 20–30 words, card
descriptions 12–20, service page lead 40–60, "Kedy to riešiť" 3–5 items, "Čo
robíme" 3–5 steps.

---

## 3. How to swap an image

`config/images.ts` is the single source of truth. Every image is keyed by the
slot id from the original asset request, and carries its intrinsic dimensions so
the layout reserves the right box before the file loads.

To replace a photo:

1. Drop the new original into `assets-originals/` under the name the pipeline
   expects (`hero-workshop.jpg`, `diagnostika.jpg`, `about-01.jpg`, …; the map is
   at the top of `scripts/process-images.py`). Next's image optimiser caches by
   filename, so after replacing a file under a name it has already served, clear
   `.next/cache/images` or the old version keeps showing up in development.
2. Run `npm run images`. It strips all metadata, crops to the slot's aspect
   ratio, writes WebP + AVIF + JPEG at three widths, and prints a byte report.
3. If the dominant colour changed noticeably, copy the new `placeholder` value
   from `public/assets/miauto/manifest.json` into `config/images.ts`.

Nothing in a component references an image path directly.

---

## 4. What is still missing

Contact details, the owners and every text block on the site are filled in. What
remains is the company's registration data, and the site is built so that each
line appears only once it holds a value — there are no bracketed tokens left on
any page.

### In `config/miauto.ts`

| Field | Where it would show | Status |
|---|---|---|
| `ico` | footer, privacy policy | **required before launch** — § 3a of the Slovak Commercial Code |
| `zapisVOR` | footer, privacy policy | **required before launch** — the commercial-register entry |
| `dic` | footer | optional |
| `icDph` | footer | optional, only if the company is VAT-registered |
| `geo.lat` / `geo.lng` | JSON-LD | optional; the map works from the street address |
| `social.facebook` / `social.instagram` | footer | optional |

`has()` in the same file is what decides: an empty string means the line, its
label and its separator are not rendered at all. Fill the value in and it appears
— in the footer, in the privacy policy, and (for `ico`, `dic`, `geo`) in the
JSON-LD — with no other edit.

The owners are set in `site.owners` and render on the About page with their
photographs. Their roles come from `about.ownerRoles` in both locales.

---

## 5. How to deploy to Netlify

There are two routes, and they are not equivalent. **Read the comparison before
choosing**, because the drag-and-drop one gives up the grounded assistant.

| | Git / CLI build | Drag-and-drop (`npm run build:static`) |
|---|---|---|
| All 24 pages | ✅ | ✅ |
| Enquiry form (Netlify Forms) | ✅ | ✅ |
| Map, signature interaction, both locales | ✅ | ✅ |
| Scripted assistant | ✅ server-side | ✅ in the browser |
| **Grounded assistant (`CHAT_API_KEY`)** | ✅ | ❌ **not possible** |
| Needs a Git connection or the CLI | yes | no |

A static site has no server, so there is nowhere to keep an API key and no
`/api/chat` to call. That is the whole of the difference. The form is unaffected
either way: Netlify Forms is handled by Netlify's own infrastructure, not by a
function.

### Route A — Git or CLI (recommended, full functionality)

The repository already contains `miauto/netlify.toml` with the right settings.

1. In Netlify, **Add new site → Import an existing project**, and pick this
   repository.
2. Netlify reads `netlify.toml`, so the build settings come through already set:
   base directory `miauto`, build command `npm run build`, publish directory
   `miauto/.next`.
3. **The `@netlify/plugin-nextjs` runtime adapter is required.** Netlify installs
   it automatically for a Next.js site; `netlify.toml` also declares it
   explicitly. Without it the chat route and the form POST are not deployed as
   functions and both return 404. Do **not** add `output: "export"` to
   `next.config.ts` for the same reason.
4. Set `NEXT_PUBLIC_SITE_URL` to the final public URL (e.g.
   `https://miauto.sk`). It drives canonicals, `hreflang`, the sitemap and the
   Open Graph image URLs. Without it those fall back to Netlify's deploy URL.

### Route B — drag and drop

Netlify's manual deploy publishes the folder you hand it and **runs no build**,
so the folder has to be finished files.

```bash
cd miauto
npm install
npm run build:static     # writes out/
```

Then drag the **`out/` folder** (or a zip of its *contents*, not of the folder
itself) onto the deploy area in the Netlify dashboard.

`build:static` sets `STATIC_EXPORT=1`, moves `app/api` aside for the duration of
the build because a route handler cannot coexist with `output: "export"`, puts it
straight back afterwards, and copies `_redirects` and `_headers` into `out/` —
those do the jobs that `redirects()` and `headers()` in `next.config.ts` do for
the server build.

To move from Route B to Route A later, connect the repository in Netlify and
redeploy. Nothing in the source needs changing.

### Custom domain and DNS

1. **Site configuration → Domain management → Add a domain**, enter the domain.
2. Easiest: let Netlify manage DNS. It gives you four nameservers; set those at
   the registrar. Propagation is usually under an hour, sometimes up to 24.
3. Or keep your DNS provider and point records at Netlify:
   - apex `miauto.sk` → an `ALIAS`/`ANAME` record to `apex-loadbalancer.netlify.com`,
     or an `A` record to Netlify's load balancer IP shown in the dashboard;
   - `www` → a `CNAME` to `<your-site>.netlify.app`.
4. Netlify provisions a Let's Encrypt certificate once DNS resolves. Then turn on
   **Force HTTPS**.
5. Update `NEXT_PUBLIC_SITE_URL` to the custom domain and redeploy, so canonicals
   and the sitemap point at the real address.

### Enquiry form

Netlify Forms needs the form to exist in the deployed HTML, which a React
component does not provide at build time. `public/__forms.html` is a static form
carrying the same field names; Netlify detects it and accepts POSTs to it. After
the first deploy the form appears under **Forms → dopyt**. Add the notification
address there — **ivankubis96@centrum.sk** — otherwise enquiries sit in the
Netlify dashboard and nobody is told about them. This is a dashboard setting, not
a code change, and it has to be done once per site.

---

## 6. What needs credentials

| Variable | Required? | Effect |
|---|---|---|
| `ANTHROPIC_API_KEY` | No | Without it the assistant runs in **scripted mode**. With it, it runs grounded against the model. (`CHAT_API_KEY` is still read as a fallback name.) |
| `CHAT_MODEL` | No | Overrides the model id. Default `claude-opus-5-5`. Always a **pinned** id, never a floating alias. |
| `CHAT_DAILY_TOKEN_CAP` | No | Daily token ceiling; default 300,000. When reached, everyone drops to scripted until the next day. |
| `CHAT_BASE_URL` | No | Points the SDK at a gateway instead of the default API. Used for testing against a stub. |
| `NEXT_PUBLIC_SITE_URL` | No | Overrides the public URL. The default is `PRODUCTION_URL` in `config/miauto.ts` (`https://autoservisruzomberok.com`), so canonicals, `hreflang`, the sitemap, `robots.txt` and the Open Graph URLs are correct in every build including the manual one. Set this only to build for a different address, e.g. staging. It is inlined **at build time**. Point it at localhost and `siteUrlIsPlaceholder` turns true, which omits every absolute URL rather than publishing an unreachable one. |

Set them in **Site configuration → Environment variables**. The API key is read
from `process.env` inside the route handler only. It is never a `NEXT_PUBLIC_`
variable, never reaches a client component, and never appears in the shipped
bundle.

### What the assistant costs to run

A grounded answer sends the rules block plus the knowledge base (together about
5,000 tokens, of which the knowledge block is cached and bills at a tenth after
the first request) and returns a short answer at `effort: "low"`. At the default
model that is roughly a cent or two per answer; `CHAT_DAILY_TOKEN_CAP` is the
hard ceiling. Published per-million-token prices are on Anthropic's pricing page,
and the model can be changed to a cheaper one with `CHAT_MODEL` — `claude-haiku-5-5`
is the cheapest current model, at the cost of some nuance in the answers.

The assistant also sends `fallbacks: "default"` on the models that accept it, so
a safety decline is retried on a fallback model inside the same call instead of
leaving the visitor with half a sentence. If it still fails, the widget drops to
the scripted tier and **says so under the answer, with the phone number**.

**Without any key, the site is fully functional.** Every page works; the
assistant answers from a scripted decision tree built from the same content the
pages render. It is not AI-powered until a key is present, and the README, the
final report and the widget itself all say so.

---

## 7. What is a prototype, or depends on the environment

- **The enquiry form only sends on Netlify.** Locally and on any non-Netlify
  host the POST to `/__forms.html` returns 404 and the form shows its error state
  with the phone number. This is deliberate: it never reports success for a
  message that was not sent.
- **Opening hours have no public-holiday data.** `lib/hours.ts` computes
  open/closed from the confirmed Monday–Friday 07:00–17:00 (with a 12:00–13:00 break) against
  Europe/Bratislava. It cannot know about public holidays, and guessing one would
  be a false claim about the business. On a holiday the badge will say "open"
  while the workshop is shut.
- **The chat rate limiter is in-memory.** `lib/chat/ratelimit.ts` uses a
  module-scope `Map`. It **resets on every cold start and is not shared across
  regions or function instances**, so a determined caller can exceed the nominal
  20 messages / 10 minutes. It stops casual abuse and runaway cost, not a
  motivated attacker. The upgrade is a durable KV store — Netlify Blobs or
  Upstash Redis — keyed the same way; the interface in that file is small enough
  to swap behind.
- **The daily token ceiling resets on cold start too**, for the same reason.

---

## 8. Known limitations

- **The map is geocoded from the street address, not from exact coordinates.**
  None were supplied. Google resolves `Sládkovičova 2528/108, 034 01 Ružomberok`.
  If it lands on the wrong building, replace `mapEmbedUrl` in `config/miauto.ts`
  with `https://www.google.com/maps?q=<lat>,<lng>&output=embed` — one value, one
  edit, and `mapDirectionsUrl` beside it takes the same treatment.
- **IČO and the commercial-register entry are missing.** § 3a of the Slovak
  Commercial Code requires both on a company's business website. `config/miauto.ts`
  has the fields; until they are filled the footer and the privacy policy simply
  omit those lines, which is not a lawful end state. This blocks launch.
- **The privacy policy is a template and has not been legally reviewed.** The
  page says so in a visible notice at the top, not a footnote. It makes no claim
  of GDPR compliance. It needs a qualified person before launch.
- **No analytics, and therefore no cookie banner.** Nothing on this site sets a
  tracking cookie. If analytics are added later, **consent must come first and
  nothing may load before it** — and a banner becomes necessary at that point.
- **Several service images are generic, not this workshop.** `config/images.ts`
  records `origin: "own" | "stock"` per slot. Alt text on the generic ones
  describes the activity and never implies it is M.I.Auto's own premises. Real
  photographs for those slots would be a straight upgrade.
- **The hero photograph is marked `stock` until the client says otherwise.** The
  image they supplied shows a different workshop from the one in their own
  photographs, and a different logo on the wall, so its provenance is not
  established: `ORIGIN["hero"]` in `scripts/process-images.py` is `"stock"` and
  the alt text describes the activity rather than the premises. One word from the
  client flips it to `"own"` and the alt text with it.
- **The chat knowledge is about 4,800 tokens**, not the 8–15k originally
  estimated. That is a consequence of the content being honest and compact
  rather than padded; it costs less per request and nothing is missing from it.

---

## Project layout

```
miauto/
├── app/
│   ├── [locale]/              root layout (carries <html lang>), all 12 routes
│   ├── api/chat/route.ts      streaming SSE chat endpoint
│   ├── globals.css            design tokens + the iOS motion layer
│   ├── robots.ts, sitemap.ts
├── components/
│   ├── ui/                    button, card, field, section, image, accordion
│   ├── layout/                nav, footer, call bar, CTA band, wordmark
│   ├── home/                  hero, services grid, map teaser, signature scene
│   ├── contact/               enquiry form, map frame, copy-address
│   └── chat/                  launcher (lazy), panel, conversation hook
├── config/
│   ├── miauto.ts              brand + contact data. The only place.
│   └── images.ts              every image, keyed by slot id
├── content/                   sk.ts, en.ts, types.ts, knowledge.generated.ts
├── lib/                       i18n, hours, motion, forms, jsonld, chat/
├── scripts/                   build-knowledge.ts, process-images.py
├── evals/                     50 golden chat cases + runner
├── public/
│   ├── assets/miauto/         processed images (3 widths x 3 formats)
│   └── __forms.html           Netlify form registration
└── assets-originals/          unprocessed photographs — gitignored
```

## The enquiry form

It posts to Netlify Forms. `public/__forms.html` is what Netlify parses at
deploy time to register the form — the real form is a React component that no
build-time parser ever sees — and every input there must match a key sent by
`lib/forms.ts` or that field is silently dropped from the submission.

Three things about it are load-bearing:

- **The sentinel.** `__forms.html` carries `MIAUTO_FORM_REGISTRATION_PAGE`, and
  `lib/forms.ts` treats a response containing it as a *failed* submission. A host
  that simply serves the file back answers 200, and without this check every
  enquiry would be reported as sent while nothing processed it.
- **Netlify does not email anything by itself.** It stores the submission and
  sends mail only if a form notification exists in the site dashboard
  (Forms → `dopyt` → Settings → Form notifications → Email notification). The
  intended recipient is `site.formRecipient` in `config/miauto.ts`; that constant
  documents the destination and feeds the handover text, but nothing in this
  repository can route an email.
- **The static build has no functions.** A submission-created function or a
  transactional-email provider would not run on a drag-and-drop deploy, which is
  how this site is published. Netlify Forms is the mechanism that works there.

Spam handling is a honeypot field (`bot-field`, visually hidden but not
`display: none`, which bots skip) plus a minimum fill time of 3s. No CAPTCHA.

## Accessibility and performance notes

- One `h1` per page, unbroken heading order, real landmarks on all 24 routes.
- Focus ring is a single treatment: 2px `--focus`, 3px offset, plus a `--bg`
  separator ring so it stays visible against `--bg`, `--surface` and an accent
  fill. Outlines are never removed without that replacement.
- `prefers-reduced-motion` is honoured everywhere, including press scaling and
  image reveals. The signature interaction opens on its **final** state under
  reduced motion and stays fully operable.
- Base element styles live in `@layer base`. This matters: cascade layers resolve
  before specificity, so an unlayered `a { color: inherit }` would beat every
  Tailwind text-colour utility and silently turn the label on a filled button
  back to body colour.
- Images reserve their box with `aspect-ratio`; `priority` is set on the hero
  only. The chat panel is a separate chunk, fetched on first interaction with the
  launcher.
- Cursor parallax (`useParallax` in `lib/motion.ts`, wrapped by
  `components/ui/Parallax.tsx`) writes two CSS custom properties from one rAF
  loop that stops itself at rest and releases `will-change`. The pointer is
  tracked on the nearest `[data-parallax-area]` ancestor, or failing that on the
  static wrapper — **never on the moving layer itself**, which steps out from
  under the cursor near its own edge and makes the browser fire `pointerleave`
  mid-gesture. It is gated on `(hover: hover) and (pointer: fine)` in JS and the
  exact complement in CSS, both watched live, so a resting scale is never applied
  where nothing can move.
