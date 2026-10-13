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
              {/* Padding is applied to every row, not only today's: adding it on
                  mount, once the client knows what day it is, would reflow the
                  table and show up as a layout shift. */}
              <th
                scope="row"
                className={clsx(
                  "py-2.5 pl-3 pr-4 font-normal",
                  today
                    ? "font-semibold text-[color:var(--text)]"
                    : "text-[color:var(--text-muted)]",
                )}
              >
                {t.common.days[day]}
                {/* Always rendered, only made visible for today's row. Which day
                    it is can only be known on the client, so adding this label on
                    mount would widen the column and reflow the whole table. Taking
                    the space up front costs nothing and keeps CLS at zero. */}
                <span
                  aria-hidden={today ? undefined : "true"}
                  className={clsx(
                    "ml-2 text-[0.75rem] font-semibold uppercase tracking-wider text-[color:var(--accent)]",
                    !today && "invisible",
                  )}
                >
                  {t.common.today}
                </span>
              </th>
              <td
                className={clsx(
                  "py-2.5 pr-3 text-right tabular-nums",
                  hours ? "text-[color:var(--text)]" : "text-[color:var(--text-muted)]",
                  today && "font-semibold",
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

  // The placeholder must be exactly as tall as the real badge. A 4px difference
  // here is a visible layout shift in the hero, because this sits in the last
  // line of a block that the whole hero column is sized from.
  if (!mounted) {
    return (
      <span
        className={clsx("inline-flex min-h-6 items-center", className)}
        aria-hidden="true"
      />
    );
  }

  const state = getOpenState();
  const label = state.open
    ? fmt(t.common.openNow, { time: state.closingAt })
    : fmt(t.common.closedNow, {
        day: t.common.days[state.nextDay].toLowerCase(),
        time: state.nextOpening,
      });

  return (
    <span className={clsx("inline-flex min-h-6 items-center gap-2", className)}>
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
