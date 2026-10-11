import { ImageResponse } from "next/og";
import { getDictionary, isLocale } from "@/content/i18n";
import { siteConfig } from "@/config/site";

/**
 * Open Graph image, generated with Next's ImageResponse at a stable URL
 * (/sk/og, /en/og) so metadata can reference it directly. The file-based
 * opengraph-image convention does not resolve reliably underneath a route
 * group combined with a dynamic [locale] segment, which is why this is an
 * explicit route handler instead.
 */

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ locale: string }> },
) {
  const { locale: raw } = await params;
  const locale = isLocale(raw) ? raw : "sk";
  const dict = getDictionary(locale);

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#0A0A0B",
          padding: 80,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div
            style={{
              width: 38,
              height: 38,
              display: "flex",
              background: "#6EE7B7",
              clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
            }}
          />
          <div style={{ fontSize: 34, fontWeight: 700, color: "#F4F4F5" }}>{siteConfig.name}</div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 26 }}>
          <div
            style={{
              fontSize: 62,
              fontWeight: 700,
              color: "#F4F4F5",
              lineHeight: 1.12,
              maxWidth: 950,
            }}
          >
            {dict.home.heroTitle}
          </div>
          <div style={{ fontSize: 28, color: "#9A9AA5", maxWidth: 860 }}>
            {siteConfig.tagline[locale]}
          </div>
        </div>

        <div style={{ display: "flex", height: 8, width: 170, background: "#6EE7B7" }} />
      </div>
    ),
    { width: 1200, height: 630 },
  );
}
