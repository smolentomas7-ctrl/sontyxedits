"use client";

import dynamic from "next/dynamic";
import { LazyMount } from "./WidgetFrame";
import type { LocaleContent, ServiceSlug } from "@/content/types";

/**
 * One interactive piece per service, loaded only on the page that uses it.
 *
 * Each widget is its own chunk: the route file is shared by all seven services,
 * so a static import would ship all seven to every one of them. `LazyMount`
 * then holds the mount until the section is near the viewport, which keeps the
 * widget out of the page's first render entirely.
 */
const WIDGETS: Record<
  ServiceSlug,
  { readonly Component: React.ComponentType<{ t: LocaleContent }>; readonly minHeight: number }
> = {
  "diagnostika-vozidiel": {
    Component: dynamic(() => import("./DiagnosticsWidget").then((m) => m.DiagnosticsWidget)),
    minHeight: 620,
  },
  "cipovanie-ecu": {
    Component: dynamic(() => import("./DynoWidget").then((m) => m.DynoWidget)),
    minHeight: 720,
  },
  "geometria-kolies": {
    Component: dynamic(() => import("./AlignmentWidget").then((m) => m.AlignmentWidget)),
    minHeight: 640,
  },
  pneuservis: {
    Component: dynamic(() => import("./TyreWidget").then((m) => m.TyreWidget)),
    minHeight: 600,
  },
  "elektroinstalacia-vw": {
    Component: dynamic(() => import("./ElectricsWidget").then((m) => m.ElectricsWidget)),
    minHeight: 640,
  },
  "vymena-rozvodov": {
    Component: dynamic(() => import("./TimingWidget").then((m) => m.TimingWidget)),
    minHeight: 640,
  },
  "servis-klimatizacie": {
    Component: dynamic(() => import("./AcWidget").then((m) => m.AcWidget)),
    minHeight: 620,
  },
};

export function ServiceWidget({ slug, t }: { slug: ServiceSlug; t: LocaleContent }) {
  const { Component, minHeight } = WIDGETS[slug];
  return (
    <LazyMount minHeight={minHeight}>
      <Component t={t} />
    </LazyMount>
  );
}
