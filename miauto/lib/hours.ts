import { DAY_ORDER, site, type DayKey } from "@/config/miauto";

export const TIME_ZONE = "Europe/Bratislava";

export type OpenState =
  | { readonly open: true; readonly closingAt: string }
  | { readonly open: false; readonly nextDay: DayKey; readonly nextOpening: string };

/**
 * The wall-clock day and time in Ružomberok, whatever time zone the visitor is in.
 */
export function localNow(now: Date = new Date()): {
  day: DayKey;
  minutes: number;
} {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: TIME_ZONE,
    weekday: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).formatToParts(now);

  const get = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find((p) => p.type === type)?.value ?? "";

  const weekday = get("weekday").toLowerCase().slice(0, 3);
  const day = (DAY_ORDER.find((d) => d === weekday) ?? "mon") as DayKey;
  // Intl can emit "24" for midnight in some runtimes; normalise it to 0.
  const hour = Number(get("hour")) % 24;
  const minute = Number(get("minute"));
  return { day, minutes: hour * 60 + minute };
}

function toMinutes(hhmm: string): number {
  const [h, m] = hhmm.split(":");
  return Number(h) * 60 + Number(m);
}

/**
 * Open/closed against the confirmed hours. Saturday and Sunday are null in the
 * config, so this can never report open at the weekend.
 *
 * It knows nothing about public holidays: there is no holiday data here and
 * guessing one would be a false claim about the business. See README.
 */
export function getOpenState(now: Date = new Date()): OpenState {
  const { day, minutes } = localNow(now);
  const today = site.hours[day];

  if (today) {
    const [open, close] = today;
    if (minutes >= toMinutes(open) && minutes < toMinutes(close)) {
      return { open: true, closingAt: close };
    }
    // Before opening on a working day: today is still the next opening.
    if (minutes < toMinutes(open)) {
      return { open: false, nextDay: day, nextOpening: open };
    }
  }

  // Walk forward to the next day that has hours.
  const startIndex = DAY_ORDER.indexOf(day);
  for (let step = 1; step <= 7; step += 1) {
    const candidate = DAY_ORDER[(startIndex + step) % 7] as DayKey;
    const hours = site.hours[candidate];
    if (hours) {
      return { open: false, nextDay: candidate, nextOpening: hours[0] };
    }
  }
  // Unreachable while any weekday has hours, but the type has to be total.
  return { open: false, nextDay: "mon", nextOpening: "08:00" };
}

export function isToday(day: DayKey, now: Date = new Date()): boolean {
  return localNow(now).day === day;
}
