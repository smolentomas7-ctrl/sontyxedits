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
   expects (`hero.jpg`, `diagnostika.jpg`, `about-01.jpg`, …; the map is at the
   top of `scripts/process-images.py`).
2. Run `npm run images`. It strips all metadata, crops to the slot's aspect
   ratio, writes WebP + AVIF + JPEG at three widths, and prints a byte report.
3. If the dominant colour changed noticeably, copy the new `placeholder` value
   from `public/assets/miauto/manifest.json` into `config/images.ts`.

Nothing in a component references an image path directly.

---

## 4. Where the placeholders are

Everything still to be supplied renders **visibly, with its square brackets**, so
it cannot ship unnoticed.

### In `config/miauto.ts`

| Token | Where it shows | What it needs |
|---|---|---|
| `[EMAIL]` | footer, contact page, privacy policy | the shop's email address |
| `[IČO]` | footer, privacy policy | the company registration number |

Once filled, both start behaving as real values automatically: `[EMAIL]` becomes
a `mailto:` link and gets added to the JSON-LD; `[IČO]` renders as plain text.
`isPlaceholder()` is what decides.

`social.facebook` and `social.instagram` hold `[FACEBOOK_URL]` and
`[INSTAGRAM_URL]`. These are the exception: they **do not render at all** until
they hold real URLs, because a footer link pointing at the literal text
`[FACEBOOK_URL]` is worse than no link.

### On the About page (`content/sk.ts` / `content/en.ts`, `about:`)

| Token | What it needs |
|---|---|
| `[TEXT O SERVISE — doplní klient]` | a paragraph or two about the workshop |
| `[TEXT O MAJITEĽOVI — doplní klient]` | a paragraph about the owner |

The owner's name, **Ivan Kubis**, is confirmed and set in `config/miauto.ts`.

### `[TO CONFIRM: …]` markers

These mark service scope nobody has confirmed. They are in `content/sk.ts` and
`content/en.ts` under each service's `toConfirm`, and they render in a visible
panel on the service page. They **must be resolved with the client before
launch** — see "Known limitations".

---

## 5. How to deploy to Netlify

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
the first deploy the form appears under **Forms → dopyt**; add a notification
email there so submissions actually reach someone.

---

## 6. What needs credentials

| Variable | Required? | Effect |
|---|---|---|
| `CHAT_API_KEY` | No | Without it the assistant runs in **scripted mode**. With it, and with `CHAT_MODEL`, it runs grounded against the model. |
| `CHAT_MODEL` | With a key | A **pinned** model id, never a floating alias. Both this and the key must be set; either one alone keeps it scripted. |
| `CHAT_DAILY_TOKEN_CAP` | No | Daily token ceiling; default 300,000. When reached, everyone drops to scripted until the next day. |
| `CHAT_BASE_URL` | No | Points the SDK at a gateway instead of the default API. Used for testing against a stub. |
| `NEXT_PUBLIC_SITE_URL` | Recommended | The public URL, for canonicals, sitemap and OG images. |

Set them in **Site configuration → Environment variables**. `CHAT_API_KEY` is
read from `process.env` inside the route handler only. It is never a
`NEXT_PUBLIC_` variable, never reaches a client component, and never appears in
the shipped bundle.

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
  open/closed from the confirmed Monday–Friday 08:00–16:00 against
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
- **The `[TO CONFIRM: …]` service scopes must be resolved with the client before
  launch.** Seven services carry at least one. Until they are answered, the
  pages tell visitors to confirm by phone, which is honest but costs conversions.
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
- **No logo file.** The brand is set as a text wordmark in
  `components/layout/Wordmark.tsx`. Dropping in a real logo means editing that
  one component.
- **The hero photograph has the workshop's logo burned into the middle of the
  frame.** The scrim is weighted hard to the left to keep the headline legible
  over it. A clean version of the same photograph would let the hero breathe.
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
