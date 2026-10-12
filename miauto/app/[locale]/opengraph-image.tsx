import { ImageResponse } from "next/og";
import { formattedAddress, site } from "@/config/miauto";
import { isLocale } from "@/content";

/**
 * Asset slot 5.1 was not supplied, so the share image is generated rather than
 * faked with a photograph that is not theirs. Everything on it is a confirmed fact.
 */
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
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ width: 14, height: 44, background: "#FF7A3D", borderRadius: 4 }} />
          <div style={{ fontSize: 34, fontWeight: 700, letterSpacing: -1 }}>
            M.I.<span style={{ color: "#FF7A3D" }}>Auto</span>
            <span style={{ fontSize: 20, color: "#94A1A8", marginLeft: 8 }}>s.r.o.</span>
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
