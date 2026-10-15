"use client";

import { useState } from "react";
import { CheckCircle2, Loader2 } from "lucide-react";
import { submitForm, isNonEmpty, isValidEmail, isValidPhone } from "@/lib/forms";

type Values = { name: string; email: string; phone: string; area: string; matter: string };
type Errors = Partial<Record<keyof Values, string>>;

const EMPTY: Values = { name: "", email: "", phone: "", area: "", matter: "" };

const labelClass = "mb-2 block text-[13px] uppercase tracking-[0.12em] text-[#C9A96A]";
const controlClass =
  "h-12 w-full border bg-[#FBFAF7]/6 px-4 text-[15px] text-[#FBFAF7] placeholder:text-[#FBFAF7]/60 focus:border-[#C9A96A] focus:outline-none";

export function ConsultationForm({ areas }: { areas: string[] }) {
  const [values, setValues] = useState<Values>(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  const [touched, setTouched] = useState<Partial<Record<keyof Values, boolean>>>({});
  const [status, setStatus] = useState<"idle" | "sending" | "success">("idle");

  function validate(all: Values): Errors {
    const next: Errors = {};
    if (!isNonEmpty(all.name)) next.name = "Zadajte meno.";
    if (!isNonEmpty(all.email)) next.email = "Zadajte e-mail.";
    else if (!isValidEmail(all.email)) next.email = "Toto nevyzerá ako platný e-mail.";
    if (!isValidPhone(all.phone)) next.phone = "Telefónne číslo vyzerá neúplne.";
    if (!isNonEmpty(all.area)) next.area = "Vyberte oblasť práva.";
    if (!isNonEmpty(all.matter)) next.matter = "Opíšte stručne, čoho sa vec týka.";
    else if (all.matter.trim().length < 20) next.matter = "Napíšte prosím aspoň 20 znakov.";
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
    setTouched({ name: true, email: true, phone: true, area: true, matter: true });
    if (Object.values(found).some(Boolean)) return;
    setStatus("sending");
    await submitForm("legal-consultation", values);
    setStatus("success");
  }

  if (status === "success") {
    return (
      <div role="status" className="border border-[#C9A96A]/40 bg-[#FBFAF7]/5 p-8">
        <CheckCircle2 aria-hidden="true" strokeWidth={1.25} className="size-8 text-[#C9A96A]" />
        <h3 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-2xl font-medium text-[#FBFAF7]">
          Žiadosť sme prijali
        </h3>
        <p className="mt-3 text-[15px] leading-relaxed text-[#FBFAF7]/70">
          Ozveme sa do dvoch pracovných dní a navrhneme termín konzultácie.
        </p>
        <p className="mt-4 bg-[#FBFAF7]/6 px-4 py-3 text-[13px] text-[#FBFAF7]/55">
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
          className="mt-6 border border-[#FBFAF7]/30 px-5 py-2.5 text-[14px] text-[#FBFAF7] transition-colors duration-150 hover:bg-[#FBFAF7]/10"
        >
          Nová žiadosť
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} noValidate className="border border-[#FBFAF7]/15 p-7 md:p-8">
      <div className="flex flex-col gap-5">
        {(
          [
            { key: "name", label: "Meno a priezvisko", type: "text", ac: "name" },
            { key: "email", label: "E-mail", type: "email", ac: "email" },
            { key: "phone", label: "Telefón", type: "tel", ac: "tel" },
          ] as const
        ).map((field) => (
          <div key={field.key}>
            <label htmlFor={`cf-${field.key}`} className={labelClass}>
              {field.label}
            </label>
            <input
              id={`cf-${field.key}`}
              type={field.type}
              autoComplete={field.ac}
              value={values[field.key]}
              onChange={(e) => setField(field.key, e.target.value)}
              onBlur={() => onBlur(field.key)}
              aria-invalid={errors[field.key] ? true : undefined}
              aria-describedby={errors[field.key] ? `cf-${field.key}-error` : undefined}
              className={controlClass}
              style={{ borderColor: errors[field.key] ? "#F87171" : "rgba(251,250,247,0.2)" }}
            />
            {errors[field.key] ? (
              <p id={`cf-${field.key}-error`} className="mt-1.5 text-[13px] text-[#FCA5A5]">
                {errors[field.key]}
              </p>
            ) : null}
          </div>
        ))}

        <div>
          <label htmlFor="cf-area" className={labelClass}>
            Oblasť práva
          </label>
          <select
            id="cf-area"
            value={values.area}
            onChange={(e) => setField("area", e.target.value)}
            onBlur={() => onBlur("area")}
            aria-invalid={errors.area ? true : undefined}
            aria-describedby={errors.area ? "cf-area-error" : undefined}
            className={controlClass}
            style={{ borderColor: errors.area ? "#F87171" : "rgba(251,250,247,0.2)" }}
          >
            <option value="" className="text-[#0F1B2D]">
              Vyberte…
            </option>
            {areas.map((area) => (
              <option key={area} value={area} className="text-[#0F1B2D]">
                {area}
              </option>
            ))}
          </select>
          {errors.area ? (
            <p id="cf-area-error" className="mt-1.5 text-[13px] text-[#FCA5A5]">
              {errors.area}
            </p>
          ) : null}
        </div>

        <div>
          <label htmlFor="cf-matter" className={labelClass}>
            Čoho sa vec týka
          </label>
          <textarea
            id="cf-matter"
            rows={5}
            value={values.matter}
            onChange={(e) => setField("matter", e.target.value)}
            onBlur={() => onBlur("matter")}
            aria-invalid={errors.matter ? true : undefined}
            aria-describedby={errors.matter ? "cf-matter-error" : "cf-matter-hint"}
            className="w-full resize-y border bg-[#FBFAF7]/6 px-4 py-3 text-[15px] text-[#FBFAF7] placeholder:text-[#FBFAF7]/60 focus:border-[#C9A96A] focus:outline-none"
            style={{ borderColor: errors.matter ? "#F87171" : "rgba(251,250,247,0.2)" }}
          />
          {errors.matter ? (
            <p id="cf-matter-error" className="mt-1.5 text-[13px] text-[#FCA5A5]">
              {errors.matter}
            </p>
          ) : (
            <p id="cf-matter-hint" className="mt-1.5 text-[13px] text-[#FBFAF7]/60">
              Stačí niekoľko viet. Podrobnosti preberieme na stretnutí.
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={status === "sending"}
          className="inline-flex h-12 items-center justify-center gap-2 bg-[#C9A96A] px-8 text-[15px] font-medium text-[#0F1B2D] transition-colors duration-150 hover:bg-[#896E3E] disabled:opacity-60"
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
