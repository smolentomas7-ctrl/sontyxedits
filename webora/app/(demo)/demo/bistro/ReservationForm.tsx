"use client";

import { useState } from "react";
import { CheckCircle2, Loader2 } from "lucide-react";
import { submitForm, isNonEmpty, isValidPhone } from "@/lib/forms";

type Values = {
  date: string;
  time: string;
  guests: string;
  name: string;
  phone: string;
  note: string;
};

type Errors = Partial<Record<keyof Values, string>>;

const TIMES = [
  "11:30", "12:00", "12:30", "13:00", "17:00", "17:30",
  "18:00", "18:30", "19:00", "19:30", "20:00", "20:30",
];

/** Today in YYYY-MM-DD, used as the earliest selectable date. */
function todayISO(): string {
  const now = new Date();
  const offset = now.getTimezoneOffset();
  return new Date(now.getTime() - offset * 60_000).toISOString().slice(0, 10);
}

const EMPTY: Values = { date: "", time: "", guests: "2", name: "", phone: "", note: "" };

const labelClass = "mb-2 block text-[14px] font-medium text-[#FAF7F2]";
const controlClass =
  "h-12 w-full rounded-lg border bg-[#FAF7F2]/8 px-4 text-[15px] text-[#FAF7F2] " +
  "placeholder:text-[#FAF7F2]/40 focus:outline-none focus:ring-2 focus:ring-[#E9B894]";

export function ReservationForm() {
  const [values, setValues] = useState<Values>(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  const [touched, setTouched] = useState<Partial<Record<keyof Values, boolean>>>({});
  const [status, setStatus] = useState<"idle" | "sending" | "success">("idle");

  function validate(all: Values): Errors {
    const next: Errors = {};
    if (!isNonEmpty(all.date)) next.date = "Vyberte dátum.";
    else if (all.date < todayISO()) next.date = "Dátum už bol. Vyberte dnešok alebo neskôr.";
    if (!isNonEmpty(all.time)) next.time = "Vyberte čas.";
    if (!isNonEmpty(all.name)) next.name = "Zadajte meno, na ktoré stôl rezervujeme.";
    if (!isNonEmpty(all.phone)) next.phone = "Bez telefónu vás nevieme kontaktovať.";
    else if (!isValidPhone(all.phone)) next.phone = "Telefónne číslo vyzerá neúplne.";
    return next;
  }

  function setField<K extends keyof Values>(key: K, value: Values[K]) {
    const next = { ...values, [key]: value };
    setValues(next);
    if (touched[key]) setErrors((c) => ({ ...c, [key]: validate(next)[key] }));
  }

  function onBlur(key: keyof Values) {
    setTouched((c) => ({ ...c, [key]: true }));
    setErrors((c) => ({ ...c, [key]: validate(values)[key] }));
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    const found = validate(values);
    setErrors(found);
    setTouched({ date: true, time: true, name: true, phone: true });
    if (Object.values(found).some(Boolean)) return;

    setStatus("sending");
    await submitForm("bistro-reservation", values);
    setStatus("success");
  }

  if (status === "success") {
    return (
      <div
        role="status"
        className="rounded-2xl border border-[#E9B894]/40 bg-[#FAF7F2]/8 p-8 text-[#FAF7F2]"
      >
        <CheckCircle2 aria-hidden="true" strokeWidth={1.5} className="size-8 text-[#E9B894]" />
        <h3 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-2xl font-bold">
          Rezerváciu máme
        </h3>
        <p className="mt-3 text-[15px] leading-relaxed text-[#FAF7F2]/80">
          Stôl pre {values.guests} {Number(values.guests) === 1 ? "osobu" : "osôb"} dňa{" "}
          {values.date} o {values.time} na meno {values.name}.
        </p>
        <p className="mt-4 rounded-lg bg-[#FAF7F2]/8 px-4 py-3 text-[13px] text-[#FAF7F2]/70">
          Toto je ukážkový web — rezervácia sa nikam neodoslala a nikto ju nedostal.
        </p>
        <button
          type="button"
          onClick={() => {
            setValues(EMPTY);
            setErrors({});
            setTouched({});
            setStatus("idle");
          }}
          className="mt-6 rounded-lg border border-[#FAF7F2]/30 px-5 py-2.5 text-[14px] font-medium transition-colors duration-150 hover:bg-[#FAF7F2]/10"
        >
          Nová rezervácia
        </button>
      </div>
    );
  }

  return (
    <form
      onSubmit={onSubmit}
      noValidate
      className="rounded-2xl border border-[#FAF7F2]/15 bg-[#FAF7F2]/5 p-7 md:p-8"
    >
      <h3 className="font-[family-name:var(--font-space-grotesk)] text-2xl font-bold text-[#FAF7F2]">
        Rezervácia stola
      </h3>
      <p className="mt-2 text-[15px] text-[#FAF7F2]/70">
        Pre skupiny nad 8 osôb nám radšej zavolajte.
      </p>

      <div className="mt-7 flex flex-col gap-5">
        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <label htmlFor="res-date" className={labelClass}>
              Dátum
            </label>
            <input
              id="res-date"
              type="date"
              min={todayISO()}
              value={values.date}
              onChange={(e) => setField("date", e.target.value)}
              onBlur={() => onBlur("date")}
              aria-invalid={errors.date ? true : undefined}
              aria-describedby={errors.date ? "res-date-error" : undefined}
              className={controlClass}
              style={{ borderColor: errors.date ? "#F87171" : "rgba(250,247,242,0.22)" }}
            />
            {errors.date ? (
              <p id="res-date-error" className="mt-1.5 text-[13px] text-[#FCA5A5]">
                {errors.date}
              </p>
            ) : null}
          </div>

          <div>
            <label htmlFor="res-time" className={labelClass}>
              Čas
            </label>
            <select
              id="res-time"
              value={values.time}
              onChange={(e) => setField("time", e.target.value)}
              onBlur={() => onBlur("time")}
              aria-invalid={errors.time ? true : undefined}
              aria-describedby={errors.time ? "res-time-error" : undefined}
              className={controlClass}
              style={{ borderColor: errors.time ? "#F87171" : "rgba(250,247,242,0.22)" }}
            >
              <option value="">Vyberte čas</option>
              {TIMES.map((time) => (
                <option key={time} value={time} className="text-[#1F3D2F]">
                  {time}
                </option>
              ))}
            </select>
            {errors.time ? (
              <p id="res-time-error" className="mt-1.5 text-[13px] text-[#FCA5A5]">
                {errors.time}
              </p>
            ) : null}
          </div>
        </div>

        <div>
          <label htmlFor="res-guests" className={labelClass}>
            Počet osôb
          </label>
          <select
            id="res-guests"
            value={values.guests}
            onChange={(e) => setField("guests", e.target.value)}
            className={controlClass}
            style={{ borderColor: "rgba(250,247,242,0.22)" }}
          >
            {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
              <option key={n} value={String(n)} className="text-[#1F3D2F]">
                {n} {n === 1 ? "osoba" : n < 5 ? "osoby" : "osôb"}
              </option>
            ))}
          </select>
        </div>

        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <label htmlFor="res-name" className={labelClass}>
              Meno
            </label>
            <input
              id="res-name"
              type="text"
              autoComplete="name"
              value={values.name}
              onChange={(e) => setField("name", e.target.value)}
              onBlur={() => onBlur("name")}
              aria-invalid={errors.name ? true : undefined}
              aria-describedby={errors.name ? "res-name-error" : undefined}
              className={controlClass}
              style={{ borderColor: errors.name ? "#F87171" : "rgba(250,247,242,0.22)" }}
            />
            {errors.name ? (
              <p id="res-name-error" className="mt-1.5 text-[13px] text-[#FCA5A5]">
                {errors.name}
              </p>
            ) : null}
          </div>

          <div>
            <label htmlFor="res-phone" className={labelClass}>
              Telefón
            </label>
            <input
              id="res-phone"
              type="tel"
              autoComplete="tel"
              value={values.phone}
              onChange={(e) => setField("phone", e.target.value)}
              onBlur={() => onBlur("phone")}
              aria-invalid={errors.phone ? true : undefined}
              aria-describedby={errors.phone ? "res-phone-error" : undefined}
              className={controlClass}
              style={{ borderColor: errors.phone ? "#F87171" : "rgba(250,247,242,0.22)" }}
            />
            {errors.phone ? (
              <p id="res-phone-error" className="mt-1.5 text-[13px] text-[#FCA5A5]">
                {errors.phone}
              </p>
            ) : null}
          </div>
        </div>

        <div>
          <label htmlFor="res-note" className={labelClass}>
            Poznámka <span className="font-normal text-[#FAF7F2]/55">(nepovinné)</span>
          </label>
          <textarea
            id="res-note"
            rows={3}
            placeholder="Alergie, detská stolička, oslava…"
            value={values.note}
            onChange={(e) => setField("note", e.target.value)}
            className="w-full resize-y rounded-lg border bg-[#FAF7F2]/8 px-4 py-3 text-[15px] text-[#FAF7F2] placeholder:text-[#FAF7F2]/40 focus:outline-none focus:ring-2 focus:ring-[#E9B894]"
            style={{ borderColor: "rgba(250,247,242,0.22)" }}
          />
        </div>

        <button
          type="submit"
          disabled={status === "sending"}
          className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-[#C4653A] px-7 font-medium text-[#FAF7F2] transition-colors duration-150 hover:bg-[#A8522C] disabled:opacity-60"
        >
          {status === "sending" ? (
            <>
              <Loader2 aria-hidden="true" strokeWidth={1.5} className="size-4 animate-spin" />
              Odosiela sa…
            </>
          ) : (
            "Rezervovať stôl"
          )}
        </button>
      </div>
    </form>
  );
}
