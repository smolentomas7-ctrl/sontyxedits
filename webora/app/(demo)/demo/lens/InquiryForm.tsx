"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { submitForm, isNonEmpty, isValidEmail } from "@/lib/forms";

type Values = { name: string; email: string; type: string; date: string; brief: string };
type Errors = Partial<Record<keyof Values, string>>;

const TYPES = ["Portrét", "Svadba", "Produkt", "Komerčné", "Iné"];
const EMPTY: Values = { name: "", email: "", type: "", date: "", brief: "" };

const labelClass = "mb-2 block text-[12px] uppercase tracking-[0.2em] text-white/50";
const controlClass =
  "h-12 w-full border-b bg-transparent px-0 text-[16px] text-white placeholder:text-white/25 focus:border-white focus:outline-none";

export function InquiryForm() {
  const [values, setValues] = useState<Values>(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  const [touched, setTouched] = useState<Partial<Record<keyof Values, boolean>>>({});
  const [status, setStatus] = useState<"idle" | "sending" | "success">("idle");

  function validate(all: Values): Errors {
    const next: Errors = {};
    if (!isNonEmpty(all.name)) next.name = "Zadajte meno.";
    if (!isNonEmpty(all.email)) next.email = "Zadajte e-mail.";
    else if (!isValidEmail(all.email)) next.email = "Toto nevyzerá ako platný e-mail.";
    if (!isNonEmpty(all.type)) next.type = "Vyberte typ fotenia.";
    if (!isNonEmpty(all.brief)) next.brief = "Napíšte pár viet o tom, čo potrebujete.";
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
    setTouched({ name: true, email: true, type: true, brief: true });
    if (Object.values(found).some(Boolean)) return;
    setStatus("sending");
    await submitForm("lens-inquiry", values);
    setStatus("success");
  }

  if (status === "success") {
    return (
      <div role="status" className="border border-white/15 p-8">
        <h3 className="font-[family-name:var(--font-space-grotesk)] text-2xl font-medium text-white">
          Ďakujem za správu
        </h3>
        <p className="mt-3 text-[15px] leading-relaxed text-white/60">
          Ozvem sa do dvoch dní s termínmi a cenovou ponukou.
        </p>
        <p className="mt-4 bg-white/5 px-4 py-3 text-[13px] text-white/45">
          Toto je ukážkový web — správa sa nikam neodoslala.
        </p>
        <button
          type="button"
          onClick={() => {
            setValues(EMPTY);
            setErrors({});
            setTouched({});
            setStatus("idle");
          }}
          className="mt-6 border border-white/25 px-5 py-2.5 text-[13px] uppercase tracking-[0.16em] text-white transition-colors duration-150 hover:bg-white/10"
        >
          Nová správa
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} noValidate className="flex flex-col gap-7">
      {(
        [
          { key: "name", label: "Meno", type: "text", ac: "name" },
          { key: "email", label: "E-mail", type: "email", ac: "email" },
        ] as const
      ).map((field) => (
        <div key={field.key}>
          <label htmlFor={`lf-${field.key}`} className={labelClass}>
            {field.label}
          </label>
          <input
            id={`lf-${field.key}`}
            type={field.type}
            autoComplete={field.ac}
            value={values[field.key]}
            onChange={(e) => setField(field.key, e.target.value)}
            onBlur={() => onBlur(field.key)}
            aria-invalid={errors[field.key] ? true : undefined}
            aria-describedby={errors[field.key] ? `lf-${field.key}-error` : undefined}
            className={controlClass}
            style={{ borderColor: errors[field.key] ? "#F87171" : "rgba(255,255,255,0.2)" }}
          />
          {errors[field.key] ? (
            <p id={`lf-${field.key}-error`} className="mt-1.5 text-[13px] text-[#FCA5A5]">
              {errors[field.key]}
            </p>
          ) : null}
        </div>
      ))}

      <div className="grid gap-7 sm:grid-cols-2">
        <div>
          <label htmlFor="lf-type" className={labelClass}>
            Typ fotenia
          </label>
          <select
            id="lf-type"
            value={values.type}
            onChange={(e) => setField("type", e.target.value)}
            onBlur={() => onBlur("type")}
            aria-invalid={errors.type ? true : undefined}
            aria-describedby={errors.type ? "lf-type-error" : undefined}
            className={controlClass}
            style={{ borderColor: errors.type ? "#F87171" : "rgba(255,255,255,0.2)" }}
          >
            <option value="" className="bg-[#0B0B0C]">
              Vyberte…
            </option>
            {TYPES.map((type) => (
              <option key={type} value={type} className="bg-[#0B0B0C]">
                {type}
              </option>
            ))}
          </select>
          {errors.type ? (
            <p id="lf-type-error" className="mt-1.5 text-[13px] text-[#FCA5A5]">
              {errors.type}
            </p>
          ) : null}
        </div>

        <div>
          <label htmlFor="lf-date" className={labelClass}>
            Predstava o termíne
          </label>
          <input
            id="lf-date"
            type="date"
            value={values.date}
            onChange={(e) => setField("date", e.target.value)}
            className={`${controlClass} [color-scheme:dark]`}
            style={{ borderColor: "rgba(255,255,255,0.2)" }}
          />
        </div>
      </div>

      <div>
        <label htmlFor="lf-brief" className={labelClass}>
          O čo ide
        </label>
        <textarea
          id="lf-brief"
          rows={4}
          value={values.brief}
          onChange={(e) => setField("brief", e.target.value)}
          onBlur={() => onBlur("brief")}
          aria-invalid={errors.brief ? true : undefined}
          aria-describedby={errors.brief ? "lf-brief-error" : undefined}
          className="w-full resize-y border-b bg-transparent py-3 text-[16px] text-white placeholder:text-white/25 focus:border-white focus:outline-none"
          style={{ borderColor: errors.brief ? "#F87171" : "rgba(255,255,255,0.2)" }}
        />
        {errors.brief ? (
          <p id="lf-brief-error" className="mt-1.5 text-[13px] text-[#FCA5A5]">
            {errors.brief}
          </p>
        ) : null}
      </div>

      <button
        type="submit"
        disabled={status === "sending"}
        className="inline-flex h-12 items-center justify-center gap-2 self-start border border-white px-9 text-[13px] uppercase tracking-[0.2em] text-white transition-colors duration-150 hover:bg-white hover:text-[#0B0B0C] disabled:opacity-60"
      >
        {status === "sending" ? (
          <>
            <Loader2 aria-hidden="true" strokeWidth={1.5} className="size-4 animate-spin" />
            Odosiela sa
          </>
        ) : (
          "Odoslať"
        )}
      </button>
    </form>
  );
}
