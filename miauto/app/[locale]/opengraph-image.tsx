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
              but cannot resolve a CSS variable, so the two colours are literal. */}
          <svg width="56" height="56" viewBox="0 0 32 32" fill="none">
            <path
              d="M6.6 26V12.4L10.8 8.2L16 13.4L21.2 8.2L25.4 12.4V26"
              stroke="#F2F4F5"
              strokeWidth="3.6"
              strokeLinecap="butt"
              strokeLinejoin="miter"
            />
            <circle cx="6.6" cy="27.4" r="2.6" fill="#FF7A3D" />
            <circle cx="25.4" cy="27.4" r="2.6" fill="#FF7A3D" />
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
