import { ImageResponse } from "next/og";
import { formattedAddress, site } from "@/config/miauto";
import { isLocale, LOCALES } from "@/content";

/**
 * Asset slot 5.1 was not supplied, so the share image is generated rather than
 * faked with a photograph that is not theirs. Everything on it is a confirmed fact.
 */
/** Prerendered for both builds: every value on it is a confirmed constant. */
export const dynamic = "force-static";

export function generateStaticParams() {
  return LOCALES.map((locale) => ({ locale }));
}

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt = `${site.legalName} — ${site.city}`;

export default async function OpengraphImage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const sk = !isLocale(locale) || locale === "sk";

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#0B0D0E",
          color: "#F2F4F5",
          padding: 72,
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          {/* The same mark the header carries, drawn inline: Satori renders SVG
              but cannot resolve a CSS variable, so the colour is literal. */}
          <svg width="64" height="64" viewBox="0 0 64 64" fill="#FF7A3D">
            <path d="M3.12 42.29L2.39 41.16L1.33 36.78L0.93 30.27L1.46 26.16L3.32 20.18L7.04 13.81L10.82 9.76L14.81 6.71L20.38 3.92L26.09 2.33L33.39 1.93L38.44 2.59L44.68 4.72L49.46 7.51L54.3 11.82L57.22 15.54L60.41 21.78L60.08 22.11L59.48 21.64L57.49 17.4L54.17 12.75L50.12 8.97L44.55 5.51L40.16 3.79L33.13 2.59L27.42 2.86L22.11 4.05L16.27 6.71L11.49 10.16L7.44 14.61L4.92 18.59L2.53 24.83L1.73 30.01L1.86 35.45L3.46 41.69L3.12 42.29ZM32.07 62.07L26.49 61.67L22.11 60.61L16.4 58.09L12.82 55.7L8.77 51.91L4.39 45.67L5.45 45.81L8.9 50.99L12.68 54.64L16.27 57.16L21.58 59.68L26.76 61.01L33.0 61.41L37.24 60.88L42.55 59.28L47.47 56.76L51.18 53.97L55.1 49.92L57.62 46.21L59.48 42.22L61.07 36.38L61.47 31.07L60.81 26.03L61.41 26.09L62.14 31.87L61.47 38.37L59.22 44.75L56.03 49.92L50.92 55.17L46.01 58.49L40.16 60.88L32.07 62.07Z" />
            <path d="M9.23 40.83L13.94 36.91L17.26 27.35L17.13 25.23L23.3 25.56L24.03 26.29L25.49 30.81L22.11 33.66L21.25 31.47L20.65 31.27L18.79 36.05L14.54 38.7L9.23 40.83ZM26.62 41.36L24.5 41.36L24.17 40.9L23.37 37.97L24.9 36.58L26.89 34.99L27.55 36.05L27.95 35.92L32.46 31.27L36.85 28.48L43.95 26.29L42.42 28.61L36.71 31.67L27.82 40.96L26.62 41.36ZM63.0 25.03L56.76 24.1L54.77 22.77L51.45 21.84L36.98 21.84L41.76 21.31L41.96 20.85L38.57 19.06L35.78 18.39L29.01 18.66L22.37 20.78L22.51 21.58L28.75 24.5L20.52 22.64L17.46 22.77L14.28 24.5L14.21 23.1L13.01 21.25L17.06 21.18L28.75 17.6L34.46 17.33L39.37 18.52L44.81 21.05L50.12 20.91L55.03 21.71L63.0 25.03ZM45.74 43.09L41.29 42.89L45.14 30.27L45.61 29.54L50.12 29.68L45.74 43.09ZM3.66 44.28L2.19 44.15L10.43 42.16L16.13 39.63L19.59 37.51L30.74 28.75L37.64 25.83L41.43 25.36L36.18 27.15L29.54 31.0L18.13 40.03L16.93 43.09L12.68 42.95L3.66 44.28ZM37.91 43.09L33.19 43.02L34.52 38.37L36.25 34.12L38.84 31.93L42.02 30.21L37.91 43.09ZM50.65 28.08L45.94 27.75L46.74 26.03L47.73 25.3L51.45 25.16L50.65 28.08ZM33.93 23.84L28.75 23.04L25.76 21.78L27.29 21.58L33.93 23.84ZM51.32 23.17L48.06 23.1L50.12 22.77L51.32 23.17Z" />
          </svg>
          {/* Satori needs an explicit display on any element with more than one
              child; without it the whole image throws at render time. */}
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              fontSize: 34,
              fontWeight: 700,
              letterSpacing: -1,
            }}
          >
            <span>M.I.</span>
            <span style={{ color: "#FF7A3D" }}>Auto</span>
            <span style={{ fontSize: 20, color: "#94A1A8", marginLeft: 8, fontWeight: 400 }}>
              s.r.o.
            </span>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 76, fontWeight: 700, letterSpacing: -2.5, lineHeight: 1.05 }}>
            {sk ? "Autoservis v Ružomberku" : "Car workshop in Ružomberok"}
          </div>
          <div style={{ fontSize: 30, color: "#94A1A8", marginTop: 20 }}>
            {sk
              ? "Diagnostika · Elektronika · Rozvody · Pneuservis"
              : "Diagnostics · Electronics · Timing · Tyres"}
          </div>
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-end",
            borderTop: "1px solid #262D31",
            paddingTop: 28,
            fontSize: 24,
          }}
        >
          <div style={{ color: "#94A1A8" }}>{formattedAddress}</div>
          <div style={{ color: "#FF7A3D", fontWeight: 700 }}>{site.phone}</div>
        </div>
      </div>
    ),
    size,
  );
}
