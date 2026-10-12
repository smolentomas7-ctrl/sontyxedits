import { Cable, CircleDot, Cog, Cpu, Crosshair, ScanLine, Snowflake } from "lucide-react";
import type { ServiceIconName } from "@/content/types";

const ICONS = {
  "scan-line": ScanLine,
  cpu: Cpu,
  crosshair: Crosshair,
  "circle-dot": CircleDot,
  cable: Cable,
  cog: Cog,
  snowflake: Snowflake,
} as const satisfies Record<ServiceIconName, unknown>;

export function ServiceIcon({
  name,
  className,
  size = 24,
}: {
  name: ServiceIconName;
  className?: string;
  size?: number;
}) {
  const Icon = ICONS[name];
  return <Icon className={className} size={size} strokeWidth={1.6} aria-hidden="true" />;
}
