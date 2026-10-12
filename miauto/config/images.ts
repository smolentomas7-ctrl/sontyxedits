/**
 * Single source of truth for every image on the site, keyed by the slot id used
 * in the asset request. Intrinsic dimensions live here so every image can reserve
 * its box before it loads and CLS stays at zero.
 *
 * Each slot is published at three widths by scripts/process-images.py. `src` is
 * the full-width file; `card` and `thumb` are the narrower ones, so a grid card
 * never downloads the full-width file.
 *
 * `origin` records where the picture actually came from. "own" is a photograph of
 * M.I.Auto's own workshop; "stock" is generic imagery that is NOT their premises
 * and whose alt text must never imply otherwise.
 */
export type ImageOrigin = "own" | "stock";

export type ImageSlot = {
  /** Purpose of this slot, in the words of the asset request. */
  readonly purpose: string;
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

function slot(
  id: string,
  purpose: string,
  width: number,
  height: number,
  placeholder: string,
  origin: ImageOrigin,
): ImageSlot {
  return {
    purpose,
    src: `${base}/miauto-${id}.webp`,
    card: `${base}/miauto-${id}-card.webp`,
    thumb: `${base}/miauto-${id}-thumb.webp`,
    width,
    height,
    placeholder,
    origin,
  };
}

export const images = {
  /** 2.1 — hero. The real workshop: two cars in for work under the hex lighting. */
  hero: slot("hero", "Hero — workshop interior", 1920, 1080, "#3A3C3E", "own"),

  /** 3.1 — diagnostics. Generic: a scan tool in use, not M.I.Auto's own bay. */
  serviceDiagnostika: slot(
    "service-diagnostika", "Service 3.1 — vehicle diagnostics", 1200, 800, "#3B3A38", "stock"),
  /** 3.2 — ECU software. Generic. */
  serviceCipovanieEcu: slot(
    "service-cipovanie-ecu", "Service 3.2 — ECU software", 1200, 800, "#30322F", "stock"),
  /** 3.3 — wheel alignment. Generic. */
  serviceGeometria: slot(
    "service-geometria", "Service 3.3 — wheel alignment", 1200, 800, "#4A4C4D", "stock"),
  /** 3.4 — tyre service. Generic. */
  servicePneuservis: slot(
    "service-pneuservis", "Service 3.4 — tyre service", 1200, 800, "#44423F", "stock"),
  /** 3.5 — VW Group electrics. Generic, reframed to exclude branded workshop kit. */
  serviceElektroinstalacia: slot(
    "service-elektroinstalacia", "Service 3.5 — VW Group electrics", 1200, 800, "#3B3B3D", "stock"),
  /** 3.6 — timing system. Generic. */
  serviceRozvody: slot(
    "service-rozvody", "Service 3.6 — timing system", 1200, 800, "#38373A", "stock"),
  /** 3.7 — A/C service. Real: M.I.Auto's own A/C station on a customer car. */
  serviceKlimatizacia: slot(
    "service-klimatizacia", "Service 3.7 — A/C service", 1200, 800, "#3F4245", "own"),

  /** 4.1 — about, workshop interior. Real. */
  aboutInterior: slot("about-interior", "About 4.1 — workshop interior", 1000, 1250, "#3D3F41", "own"),
  /** 4.2a — about, work in progress. Real. */
  aboutDetail01: slot("about-detail-01", "About 4.2 — work in progress", 1200, 800, "#36383A", "own"),
  /** 4.2b — about, work in progress. Real. */
  aboutDetail02: slot("about-detail-02", "About 4.2 — work in progress", 1200, 800, "#3A3C3D", "own"),
} as const;

export type ImageKey = keyof typeof images;

/**
 * Slots from the asset request that no file was supplied for. Listed here rather
 * than filled with something misleading — see README "Known limitations".
 */
export const unfilledSlots = [
  { id: "1.1", what: "Logo file (SVG or transparent PNG)", fallback: "text wordmark" },
  { id: "1.2", what: "Owner portrait", fallback: "About page runs without a portrait" },
  { id: "1.3", what: "Workshop exterior / signage, 2 images", fallback: "no exterior section" },
  { id: "5.1", what: "Share image", fallback: "generated from the hero" },
] as const;
