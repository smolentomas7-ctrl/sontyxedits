import manifest from "@/public/assets/miauto/manifest.json";

/**
 * Single source of truth for every image on the site.
 *
 * Dimensions, placeholder colour and provenance are read straight from
 * `public/assets/miauto/manifest.json`, which scripts/process-images.py writes.
 * Nothing is restated by hand here, so the boxes the layout reserves can never
 * drift from the files that actually shipped.
 *
 * `origin` records where a picture came from. "own" is a photograph taken at
 * M.I.Auto; "stock" is generic imagery that is NOT their premises, and its alt
 * text must never imply otherwise.
 */
export type ImageOrigin = "own" | "stock";

export type ImageSlot = {
  readonly id: string;
  readonly src: string;
  readonly card: string;
  readonly thumb: string;
  readonly width: number;
  readonly height: number;
  /** Dominant colour, painted under the image so nothing flashes white. */
  readonly placeholder: string;
  readonly origin: ImageOrigin;
};

const base = "/assets/miauto";

type ManifestEntry = {
  width: number;
  height: number;
  placeholder: string;
  origin: string;
  upscaled: boolean;
};

function slot(id: string): ImageSlot {
  const entry = (manifest as Record<string, ManifestEntry>)[id];
  if (!entry) throw new Error(`images: no manifest entry for "${id}" — run npm run images`);
  return {
    id,
    src: `${base}/miauto-${id}.webp`,
    card: `${base}/miauto-${id}-card.webp`,
    thumb: `${base}/miauto-${id}-thumb.webp`,
    width: entry.width,
    height: entry.height,
    placeholder: entry.placeholder,
    origin: entry.origin === "own" ? "own" : "stock",
  };
}

export const images = {
  /** 2.1 — hero: the real workshop, two cars in for work. */
  hero: slot("hero"),

  serviceDiagnostika: slot("service-diagnostika"),
  serviceCipovanieEcu: slot("service-cipovanie-ecu"),
  serviceGeometria: slot("service-geometria"),
  servicePneuservis: slot("service-pneuservis"),
  serviceElektroinstalacia: slot("service-elektroinstalacia"),
  serviceRozvody: slot("service-rozvody"),
  /** 3.7 — real: M.I.Auto's own A/C station on a customer car. */
  serviceKlimatizacia: slot("service-klimatizacia"),

  aboutInterior: slot("about-interior"),
  aboutDetail01: slot("about-detail-01"),
  aboutDetail02: slot("about-detail-02"),

  /** 1.2 — owner portraits, 4:5. */
  owner01: slot("owner-01"),
  owner02: slot("owner-02"),
} as const;

export type ImageKey = keyof typeof images;

/** Look a slot up by its manifest id, for data-driven config such as `owners`. */
export function imageById(id: string): ImageSlot | null {
  return (manifest as Record<string, ManifestEntry>)[id] ? slot(id) : null;
}

/** Slots still using generic imagery rather than a photograph of this workshop. */
export const stockSlots = Object.values(images)
  .filter((s) => s.origin === "stock")
  .map((s) => s.id);
