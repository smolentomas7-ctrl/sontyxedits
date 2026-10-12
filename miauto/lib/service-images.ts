import { images, type ImageSlot } from "@/config/images";
import type { ServiceSlug } from "@/content/types";

/** Slot 3.1–3.7, one per service page. */
export const SERVICE_IMAGE: Record<ServiceSlug, ImageSlot> = {
  "diagnostika-vozidiel": images.serviceDiagnostika,
  "cipovanie-ecu": images.serviceCipovanieEcu,
  "geometria-kolies": images.serviceGeometria,
  pneuservis: images.servicePneuservis,
  "elektroinstalacia-vw": images.serviceElektroinstalacia,
  "vymena-rozvodov": images.serviceRozvody,
  "servis-klimatizacie": images.serviceKlimatizacia,
};
