"use client";

import { useMemo, useState } from "react";
import { Check, ChevronLeft, Loader2, CalendarDays } from "lucide-react";
import { submitForm, isNonEmpty, isValidEmail, isValidPhone } from "@/lib/forms";
import { CLASSES, SLOTS_BY_WEEKDAY } from "./data";

type Step = 1 | 2 | 3 | 4;

type Details = { name: string; email: string; phone: string };
type Errors = Partial<Record<keyof Details, string>>;

/** The next 14 days starting today. */
function nextDays(count: number): Date[] {
  const out: Date[] = [];
  const base = new Date();
  base.setHours(0, 0, 0, 0);
  for (let i = 0; i < count; i += 1) {
    const day = new Date(base);
    day.setDate(base.getDate() + i);
    out.push(day);
  }
  return out;
}

const DAY_NAMES = ["Ne", "Po", "Ut", "St", "Št", "Pi", "So"];
const MONTH_NAMES = [
  "januára", "februára", "marca", "apríla", "mája", "júna",
  "júla", "augusta", "septembra", "októbra", "novembra", "decembra",
];

function formatLongDate(date: Date): string {
  return `${date.getDate()}. ${MONTH_NAMES[date.getMonth()]}`;
}

function isoDate(date: Date): string {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(
    date.getDate(),
  ).padStart(2, "0")}`;
}

const STEP_LABELS = ["Hodina", "Dátum", "Čas", "Údaje"];

export function BookingFlow() {
  const [step, setStep] = useState<Step>(1);
  const [classId, setClassId] = useState<string | null>(null);
  const [date, setDate] = useState<Date | null>(null);
  const [slot, setSlot] = useState<string | null>(null);
  const [details, setDetails] = useState<Details>({ name: "", email: "", phone: "" });
  const [errors, setErrors] = useState<Errors>({});
  const [touched, setTouched] = useState<Partial<Record<keyof Details, boolean>>>({});
  const [status, setStatus] = useState<"idle" | "sending" | "done">("idle");

  const days = useMemo(() => nextDays(14), []);
  const selectedClass = CLASSES.find((c) => c.id === classId);

  /** Slots are static sample data keyed by weekday — see the note in data.ts. */
  const slots = useMemo(() => {
    if (!date || !classId) return [];
    return SLOTS_BY_WEEKDAY[date.getDay()]?.filter((s) => s.classId === classId) ?? [];
  }, [date, classId]);

  function validate(all: Details): Errors {
    const next: Errors = {};
    if (!isNonEmpty(all.name)) next.name = "Zadajte meno.";
    if (!isNonEmpty(all.email)) next.email = "Zadajte e-mail.";
    else if (!isValidEmail(all.email)) next.email = "Toto nevyzerá ako platný e-mail.";
    if (!isValidPhone(all.phone)) next.phone = "Telefónne číslo vyzerá neúplne.";
    return next;
  }

  function setDetail<K extends keyof Details>(key: K, value: Details[K]) {
    const next = { ...details, [key]: value };
    setDetails(next);
    if (touched[key]) setErrors((c) => ({ ...c, [key]: validate(next)[key] }));
  }

  async function confirm(event: React.FormEvent) {
    event.preventDefault();
    const found = validate(details);
    setErrors(found);
    setTouched({ name: true, email: true, phone: true });
    if (Object.values(found).some(Boolean)) return;

    setStatus("sending");
    await submitForm("fitness-booking", {
      class: selectedClass?.name,
      date: date ? isoDate(date) : null,
      time: slot,
      ...details,
    });
    setStatus("done");
  }

  function reset() {
    setStep(1);
    setClassId(null);
    setDate(null);
    setSlot(null);
    setDetails({ name: "", email: "", phone: "" });
    setErrors({});
    setTouched({});
    setStatus("idle");
  }

  if (status === "done") {
    return (
      <div className="rounded-2xl border border-[#FF6B1A]/40 bg-[#1A1A1C] p-8">
        <div className="flex size-12 items-center justify-center rounded-full bg-[#FF6B1A]">
          <Check aria-hidden="true" strokeWidth={2} className="size-6 text-[#0C0C0E]" />
        </div>
        <h3 className="mt-5 font-[family-name:var(--font-space-grotesk)] text-2xl font-bold uppercase tracking-[-0.01em] text-white">
          Rezervácia potvrdená
        </h3>

        <dl className="mt-6 flex flex-col divide-y divide-white/10 border-y border-white/10 text-[15px]">
          {[
            { k: "Hodina", v: selectedClass?.name ?? "" },
            { k: "Dátum", v: date ? formatLongDate(date) : "" },
            { k: "Čas", v: slot ?? "" },
            { k: "Meno", v: details.name },
            { k: "E-mail", v: details.email },
          ].map((row) => (
            <div key={row.k} className="flex justify-between gap-6 py-3">
              <dt className="text-white/55">{row.k}</dt>
              <dd className="text-right font-medium text-white">{row.v}</dd>
            </div>
          ))}
        </dl>

        <p className="mt-5 rounded-lg bg-white/5 px-4 py-3 text-[13px] text-white/60">
          Toto je ukážkový web. Rezervácia sa nikam neodoslala a v žiadnom kalendári neexistuje.
        </p>

        <button
          type="button"
          onClick={reset}
          className="mt-6 rounded-lg border border-white/25 px-5 py-2.5 text-[14px] font-medium text-white transition-colors duration-150 hover:bg-white/10"
        >
          Rezervovať ďalšiu hodinu
        </button>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-white/12 bg-[#1A1A1C] p-6 md:p-8">
      {/* ---------- step indicator ---------- */}
      <ol className="mb-8 flex items-center gap-2">
        {STEP_LABELS.map((label, index) => {
          const number = (index + 1) as Step;
          const state = number < step ? "done" : number === step ? "current" : "todo";
          return (
            <li key={label} className="flex flex-1 items-center gap-2">
              <span
                aria-current={state === "current" ? "step" : undefined}
                className="flex size-8 shrink-0 items-center justify-center rounded-full text-[13px] font-bold"
                style={{
                  background:
                    state === "todo" ? "rgba(255,255,255,0.08)" : "#FF6B1A",
                  color: state === "todo" ? "rgba(255,255,255,0.45)" : "#0C0C0E",
                }}
              >
                {state === "done" ? (
                  <Check aria-hidden="true" strokeWidth={2.5} className="size-4" />
                ) : (
                  number
                )}
              </span>
              <span
                className="hidden text-[13px] sm:inline"
                style={{ color: state === "todo" ? "rgba(255,255,255,0.4)" : "#FFFFFF" }}
              >
                {label}
              </span>
              {index < STEP_LABELS.length - 1 ? (
                <span aria-hidden="true" className="h-px flex-1 bg-white/12" />
              ) : null}
            </li>
          );
        })}
      </ol>

      {step > 1 ? (
        <button
          type="button"
          onClick={() => setStep((s) => Math.max(1, s - 1) as Step)}
          className="mb-5 inline-flex items-center gap-1.5 text-[14px] text-white/60 transition-colors duration-150 hover:text-white"
        >
          <ChevronLeft aria-hidden="true" strokeWidth={1.5} className="size-4" />
          Späť
        </button>
      ) : null}

      {/* ---------- step 1: class ---------- */}
      {step === 1 ? (
        <div>
          <h3 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold uppercase text-white">
            Vyberte hodinu
          </h3>
          <ul className="mt-5 grid gap-3 sm:grid-cols-2">
            {CLASSES.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  onClick={() => {
                    setClassId(item.id);
                    setSlot(null);
                    setStep(2);
                  }}
                  className="w-full rounded-xl border border-white/12 bg-white/4 p-4 text-left transition-colors duration-150 hover:border-[#FF6B1A]/60 hover:bg-white/8"
                >
                  <span className="block font-medium text-white">{item.name}</span>
                  <span className="mt-1 block text-[13px] text-white/55">
                    {item.duration} min · {item.level}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {/* ---------- step 2: date ---------- */}
      {step === 2 ? (
        <div>
          <h3 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold uppercase text-white">
            Vyberte dátum
          </h3>
          <p className="mt-2 text-[14px] text-white/55">
            Najbližších 14 dní. Vybraná hodina: {selectedClass?.name}
          </p>
          <ul className="mt-5 grid grid-cols-4 gap-2.5 sm:grid-cols-7">
            {days.map((day) => {
              const selected = date !== null && isoDate(day) === isoDate(date);
              return (
                <li key={isoDate(day)}>
                  <button
                    type="button"
                    onClick={() => {
                      setDate(day);
                      setSlot(null);
                      setStep(3);
                    }}
                    className="flex w-full flex-col items-center gap-0.5 rounded-lg border px-2 py-3 transition-colors duration-150"
                    style={{
                      borderColor: selected ? "#FF6B1A" : "rgba(255,255,255,0.12)",
                      background: selected ? "rgba(255,107,26,0.15)" : "rgba(255,255,255,0.04)",
                    }}
                  >
                    <span className="text-[12px] text-white/50">{DAY_NAMES[day.getDay()]}</span>
                    <span className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold text-white">
                      {day.getDate()}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      ) : null}

      {/* ---------- step 3: slot ---------- */}
      {step === 3 ? (
        <div>
          <h3 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold uppercase text-white">
            Vyberte čas
          </h3>
          <p className="mt-2 text-[14px] text-white/55">
            {selectedClass?.name} · {date ? formatLongDate(date) : ""}
          </p>

          {slots.length === 0 ? (
            <div className="mt-6 flex items-center gap-3 rounded-xl border border-white/12 bg-white/4 p-5 text-[15px] text-white/65">
              <CalendarDays aria-hidden="true" strokeWidth={1.5} className="size-5 shrink-0" />
              V tento deň sa táto hodina nekoná. Skúste iný dátum.
            </div>
          ) : (
            <ul className="mt-5 grid grid-cols-2 gap-2.5 sm:grid-cols-3">
              {slots.map((item) => {
                const selected = slot === item.time;
                return (
                  <li key={item.time}>
                    <button
                      type="button"
                      disabled={item.full}
                      onClick={() => {
                        setSlot(item.time);
                        setStep(4);
                      }}
                      className="w-full rounded-lg border px-3 py-3 text-center transition-colors duration-150 disabled:cursor-not-allowed"
                      style={{
                        borderColor: selected ? "#FF6B1A" : "rgba(255,255,255,0.12)",
                        background: item.full
                          ? "rgba(255,255,255,0.02)"
                          : selected
                            ? "rgba(255,107,26,0.15)"
                            : "rgba(255,255,255,0.04)",
                        color: item.full ? "rgba(255,255,255,0.3)" : "#FFFFFF",
                      }}
                    >
                      <span className="block font-medium">{item.time}</span>
                      <span className="mt-0.5 block text-[12px] opacity-70">
                        {item.full ? "Obsadené" : `${item.free} voľných`}
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      ) : null}

      {/* ---------- step 4: details ---------- */}
      {step === 4 ? (
        <form onSubmit={confirm} noValidate>
          <h3 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold uppercase text-white">
            Vaše údaje
          </h3>
          <p className="mt-2 text-[14px] text-white/55">
            {selectedClass?.name} · {date ? formatLongDate(date) : ""} · {slot}
          </p>

          <div className="mt-6 flex flex-col gap-5">
            {(
              [
                { key: "name", label: "Meno a priezvisko", type: "text", autoComplete: "name" },
                { key: "email", label: "E-mail", type: "email", autoComplete: "email" },
                { key: "phone", label: "Telefón (nepovinné)", type: "tel", autoComplete: "tel" },
              ] as const
            ).map((field) => (
              <div key={field.key}>
                <label
                  htmlFor={`book-${field.key}`}
                  className="mb-2 block text-[14px] font-medium text-white"
                >
                  {field.label}
                </label>
                <input
                  id={`book-${field.key}`}
                  type={field.type}
                  autoComplete={field.autoComplete}
                  value={details[field.key]}
                  onChange={(e) => setDetail(field.key, e.target.value)}
                  onBlur={() => {
                    setTouched((c) => ({ ...c, [field.key]: true }));
                    setErrors((c) => ({ ...c, [field.key]: validate(details)[field.key] }));
                  }}
                  aria-invalid={errors[field.key] ? true : undefined}
                  aria-describedby={errors[field.key] ? `book-${field.key}-error` : undefined}
                  className="h-12 w-full rounded-lg border bg-white/6 px-4 text-[15px] text-white placeholder:text-white/35 focus:outline-none focus:ring-2 focus:ring-[#FF6B1A]/50"
                  style={{
                    borderColor: errors[field.key] ? "#F87171" : "rgba(255,255,255,0.15)",
                  }}
                />
                {errors[field.key] ? (
                  <p id={`book-${field.key}-error`} className="mt-1.5 text-[13px] text-[#FCA5A5]">
                    {errors[field.key]}
                  </p>
                ) : null}
              </div>
            ))}

            <button
              type="submit"
              disabled={status === "sending"}
              className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-[#FF6B1A] px-7 font-bold uppercase tracking-wide text-[#0C0C0E] transition-colors duration-150 hover:bg-[#FF8440] disabled:opacity-60"
            >
              {status === "sending" ? (
                <>
                  <Loader2 aria-hidden="true" strokeWidth={2} className="size-4 animate-spin" />
                  Potvrdzuje sa…
                </>
              ) : (
                "Potvrdiť rezerváciu"
              )}
            </button>
          </div>
        </form>
      ) : null}
    </div>
  );
}
