"use client";

import clsx from "clsx";
import { DAY_ORDER, site } from "@/config/miauto";
import { getOpenState, isToday } from "@/lib/hours";
import { useMounted } from "@/lib/motion";
import { fmt } from "@/lib/format";
import type { LocaleContent } from "@/content/types";

/**
 * The hours themselves are static and render on the server. Only the live
 * "today" marker and the open/closed badge wait for mount — they depend on the
 * current time, which the server cannot know for the visitor without a
 * hydration mismatch.
 */
export function HoursTable({ t, compact = false }: { t: LocaleContent; compact?: boolean }) {
  const mounted = useMounted();

  return (
    <table className={clsx("w-full border-collapse text-left", compact && "text-[0.9375rem]")}>
      <caption className="sr-only">{t.common.hoursHeading}</caption>
      <tbody>
        {DAY_ORDER.map((day) => {
          const hours = site.hours[day];
          const today = mounted && isToday(day);
          return (
            <tr
              key={day}
              className={clsx(
                "border-b border-[var(--border)] last:border-b-0",
                today && "bg-[var(--accent-soft)]",
              )}
            >
              <th
                scope="row"
                className={clsx(
                  "py-2.5 pr-4 font-normal",
                  today ? "font-semibold text-[color:var(--text)]" : "text-[color:var(--text-muted)]",
                  today && "pl-3",
                )}
              >
                {t.common.days[day]}
                {today ? (
                  <span className="ml-2 text-[0.75rem] font-semibold uppercase tracking-wider text-[color:var(--accent)]">
                    {t.common.today}
                  </span>
                ) : null}
              </th>
              <td
                className={clsx(
                  "py-2.5 text-right tabular-nums",
                  hours ? "text-[color:var(--text)]" : "text-[color:var(--text-muted)]",
                  today && "pr-3 font-semibold",
                )}
              >
                {hours ? `${hours[0]} – ${hours[1]}` : t.common.closedLabel}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

/**
 * "Teraz otvorené — zatvárame o 16:00" / "Teraz zatvorené — otvárame v pondelok o 8:00".
 * Renders nothing until mounted, so the server never asserts an opening state.
 */
export function OpenBadge({ t, className }: { t: LocaleContent; className?: string }) {
  const mounted = useMounted();
  if (!mounted) {
    return <span className={clsx("inline-block h-5", className)} aria-hidden="true" />;
  }

  const state = getOpenState();
  const label = state.open
    ? fmt(t.common.openNow, { time: state.closingAt })
    : fmt(t.common.closedNow, {
        day: t.common.days[state.nextDay].toLowerCase(),
        time: state.nextOpening,
      });

  return (
    <span className={clsx("inline-flex items-center gap-2", className)}>
      <span
        aria-hidden="true"
        className="inline-block size-2 rounded-full"
        style={{ backgroundColor: state.open ? "var(--success)" : "var(--text-muted)" }}
      />
      <span className={state.open ? "text-[color:var(--success)]" : "text-[color:var(--text-muted)]"}>
        {label}
      </span>
    </span>
  );
}
