"use client";

import { useState } from "react";
import { CheckCircle2, Loader2 } from "lucide-react";
import { submitForm, isNonEmpty, isValidEmail, isValidPhone } from "@/lib/forms";

type Values = { name: string; email: string; phone: string; date: string; note: string };
type Errors = Partial<Record<keyof Values, string>>;

const EMPTY: Values = { name: "", email: "", phone: "", date: "", note: "" };

const labelClass = "mb-2 block text-[14px] font-medium text-[#0E2A47]";
const controlClass =
  "h-12 w-full rounded-lg border bg-white px-4 text-[15px] focus:border-[#17457A] focus:outline-none focus:ring-2 focus:ring-[#17457A]/20";

export function ViewingForm({ propertyTitle }: { propertyTitle?: string }) {
  const [values, setValues] = useState<Values>(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  const [touched, setTouched] = useState<Partial<Record<keyof Values, boolean>>>({});
  const [status, setStatus] = useState<"idle" | "sending" | "success">("idle");

  function validate(all: Values): Errors {
    const next: Errors = {};
    if (!isNonEmpty(all.name)) next.name = "Zadajte meno.";
    if (!isNonEmpty(all.email)) next.email = "Zadajte e-mail.";
    else if (!isValidEmail(all.email)) next.email = "Toto nevyzerá ako platný e-mail.";
    if (!isNonEmpty(all.phone)) next.phone = "Zadajte telefón, obhliadku dohadujeme telefonicky.";
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
    setTouched({ name: true, email: true, phone: true });
    if (Object.values(found).some(Boolean)) return;
    setStatus("sending");
    await submitForm("estate-viewing", { ...values, property: propertyTitle });
    setStatus("success");
  }

  if (status === "success") {
    return (
      <div role="status" className="rounded-xl border border-[#1F9D64]/40 bg-[#F1FAF5] p-7">
        <CheckCircle2 aria-hidden="true" strokeWidth={1.5} className="size-8 text-[#1F9D64]" />
        <h3 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-xl font-bold text-[#0E2A47]">
          Žiadosť o obhliadku odoslaná
        </h3>
        <p className="mt-2 text-[15px] text-[#4A5A69]">
          Maklér sa vám ozve do jedného pracovného dňa a dohodnete presný termín.
        </p>
        <p className="mt-4 rounded-lg bg-white px-4 py-3 text-[13px] text-[#5B6977]">
          Toto je ukážkový web — žiadosť sa nikam neodoslala.
        </p>
        <button
          type="button"
          onClick={() => {
            setValues(EMPTY);
            setErrors({});
            setTouched({});
            setStatus("idle");
          }}
          className="mt-5 rounded-lg border border-[#D9E0E8] bg-white px-5 py-2.5 text-[14px] font-medium text-[#17457A]"
        >
          Nová žiadosť
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} noValidate className="rounded-xl border border-[#D9E0E8] bg-white p-7">
      <h3 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold text-[#0E2A47]">
        Dohodnúť obhliadku
      </h3>
      {propertyTitle ? (
        <p className="mt-1.5 text-[14px] text-[#5B6977]">{propertyTitle}</p>
      ) : (
        <p className="mt-1.5 text-[14px] text-[#5B6977]">
          Napíšte nám a dohodneme termín, ktorý vám vyhovuje.
        </p>
      )}

      <div className="mt-6 flex flex-col gap-5">
        {(
          [
            { key: "name", label: "Meno a priezvisko", type: "text", ac: "name" },
            { key: "email", label: "E-mail", type: "email", ac: "email" },
            { key: "phone", label: "Telefón", type: "tel", ac: "tel" },
          ] as const
        ).map((field) => (
          <div key={field.key}>
            <label htmlFor={`vf-${field.key}`} className={labelClass}>
              {field.label}
            </label>
            <input
              id={`vf-${field.key}`}
              type={field.type}
              autoComplete={field.ac}
              value={values[field.key]}
              onChange={(e) => setField(field.key, e.target.value)}
              onBlur={() => onBlur(field.key)}
              aria-invalid={errors[field.key] ? true : undefined}
              aria-describedby={errors[field.key] ? `vf-${field.key}-error` : undefined}
              className={controlClass}
              style={{ borderColor: errors[field.key] ? "#DC2626" : "#D9E0E8" }}
            />
            {errors[field.key] ? (
              <p id={`vf-${field.key}-error`} className="mt-1.5 text-[13px] text-[#DC2626]">
                {errors[field.key]}
              </p>
            ) : null}
          </div>
        ))}

        <div>
          <label htmlFor="vf-date" className={labelClass}>
            Preferovaný termín <span className="font-normal text-[#5B6977]">(nepovinné)</span>
          </label>
          <input
            id="vf-date"
            type="date"
            value={values.date}
            onChange={(e) => setField("date", e.target.value)}
            className={controlClass}
            style={{ borderColor: "#D9E0E8" }}
          />
        </div>

        <div>
          <label htmlFor="vf-note" className={labelClass}>
            Poznámka <span className="font-normal text-[#5B6977]">(nepovinné)</span>
          </label>
          <textarea
            id="vf-note"
            rows={3}
            value={values.note}
            onChange={(e) => setField("note", e.target.value)}
            className="w-full resize-y rounded-lg border border-[#D9E0E8] bg-white px-4 py-3 text-[15px] focus:border-[#17457A] focus:outline-none focus:ring-2 focus:ring-[#17457A]/20"
          />
        </div>

        <button
          type="submit"
          disabled={status === "sending"}
          className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-[#17457A] px-7 font-medium text-white transition-colors duration-150 hover:bg-[#0E2A47] disabled:opacity-60"
        >
          {status === "sending" ? (
            <>
              <Loader2 aria-hidden="true" strokeWidth={1.5} className="size-4 animate-spin" />
              Odosiela sa…
            </>
          ) : (
            "Odoslať žiadosť"
          )}
        </button>
      </div>
    </form>
  );
}
