"use client";

import { useState } from "react";
import { CheckCircle2, Loader2 } from "lucide-react";
import { submitForm, isNonEmpty, isValidEmail, isValidPhone } from "@/lib/forms";

type Values = {
  name: string;
  email: string;
  phone: string;
  type: string;
  budget: string;
  scope: string;
};

type Errors = Partial<Record<keyof Values, string>>;

const TYPES = [
  "Novostavba",
  "Rekonštrukcia bytu",
  "Rekonštrukcia domu",
  "Prístavba",
  "Strecha",
  "Fasáda a zateplenie",
  "Iné",
];

const BUDGETS = [
  "do 10 000 €",
  "10 000 – 30 000 €",
  "30 000 – 70 000 €",
  "70 000 – 150 000 €",
  "nad 150 000 €",
  "zatiaľ neviem",
];

const EMPTY: Values = { name: "", email: "", phone: "", type: "", budget: "", scope: "" };

const labelClass = "mb-2 block text-[14px] font-bold uppercase tracking-[0.06em] text-[#1C1C1A]";
const controlClass =
  "h-12 w-full rounded border-2 bg-white px-4 text-[15px] focus:outline-none focus:border-[#F5C518]";

export function QuoteForm() {
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
    if (!isNonEmpty(all.type)) next.type = "Vyberte typ projektu.";
    if (!isNonEmpty(all.scope)) next.scope = "Opíšte prosím, o čo ide.";
    else if (all.scope.trim().length < 20) next.scope = "Napíšte aspoň pár viet (20 znakov).";
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
    setTouched({ name: true, email: true, phone: true, type: true, scope: true });
    if (Object.values(found).some(Boolean)) return;

    setStatus("sending");
    await submitForm("build-quote", values);
    setStatus("success");
  }

  if (status === "success") {
    return (
      <div role="status" className="border-l-4 border-[#F5C518] bg-white p-8">
        <CheckCircle2 aria-hidden="true" strokeWidth={1.5} className="size-8 text-[#1C1C1A]" />
        <h3 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-2xl font-bold uppercase text-[#1C1C1A]">
          Dopyt sme prijali
        </h3>
        <p className="mt-3 text-[15px] leading-relaxed text-[#4A4A46]">
          Obhliadku zvyčajne dohodneme do troch pracovných dní. Cenovú ponuku dostanete do
          desiatich dní od obhliadky.
        </p>
        <p className="mt-4 bg-[#F2F2EF] px-4 py-3 text-[13px] text-[#6B6B66]">
          Toto je ukážkový web — dopyt sa nikam neodoslal.
        </p>
        <button
          type="button"
          onClick={() => {
            setValues(EMPTY);
            setErrors({});
            setTouched({});
            setStatus("idle");
          }}
          className="mt-6 border-2 border-[#1C1C1A] px-5 py-2.5 text-[14px] font-bold uppercase tracking-wide text-[#1C1C1A] transition-colors duration-150 hover:bg-[#1C1C1A] hover:text-white"
        >
          Nový dopyt
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} noValidate className="bg-white p-7 md:p-9">
      <h3 className="font-[family-name:var(--font-space-grotesk)] text-2xl font-bold uppercase tracking-[-0.01em] text-[#1C1C1A]">
        Dopyt na cenu
      </h3>
      <p className="mt-2 text-[15px] text-[#6B6B66]">
        Čím viac detailov, tým presnejšia prvá odpoveď.
      </p>

      <div className="mt-7 flex flex-col gap-5">
        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <label htmlFor="q-name" className={labelClass}>
              Meno
            </label>
            <input
              id="q-name"
              type="text"
              autoComplete="name"
              value={values.name}
              onChange={(e) => setField("name", e.target.value)}
              onBlur={() => onBlur("name")}
              aria-invalid={errors.name ? true : undefined}
              aria-describedby={errors.name ? "q-name-error" : undefined}
              className={controlClass}
              style={{ borderColor: errors.name ? "#DC2626" : "#D4D4D0" }}
            />
            {errors.name ? (
              <p id="q-name-error" className="mt-1.5 text-[13px] text-[#DC2626]">
                {errors.name}
              </p>
            ) : null}
          </div>

          <div>
            <label htmlFor="q-email" className={labelClass}>
              E-mail
            </label>
            <input
              id="q-email"
              type="email"
              autoComplete="email"
              value={values.email}
              onChange={(e) => setField("email", e.target.value)}
              onBlur={() => onBlur("email")}
              aria-invalid={errors.email ? true : undefined}
              aria-describedby={errors.email ? "q-email-error" : undefined}
              className={controlClass}
              style={{ borderColor: errors.email ? "#DC2626" : "#D4D4D0" }}
            />
            {errors.email ? (
              <p id="q-email-error" className="mt-1.5 text-[13px] text-[#DC2626]">
                {errors.email}
              </p>
            ) : null}
          </div>

          <div>
            <label htmlFor="q-phone" className={labelClass}>
              Telefón
            </label>
            <input
              id="q-phone"
              type="tel"
              autoComplete="tel"
              value={values.phone}
              onChange={(e) => setField("phone", e.target.value)}
              onBlur={() => onBlur("phone")}
              aria-invalid={errors.phone ? true : undefined}
              aria-describedby={errors.phone ? "q-phone-error" : undefined}
              className={controlClass}
              style={{ borderColor: errors.phone ? "#DC2626" : "#D4D4D0" }}
            />
            {errors.phone ? (
              <p id="q-phone-error" className="mt-1.5 text-[13px] text-[#DC2626]">
                {errors.phone}
              </p>
            ) : null}
          </div>

          <div>
            <label htmlFor="q-type" className={labelClass}>
              Typ projektu
            </label>
            <select
              id="q-type"
              value={values.type}
              onChange={(e) => setField("type", e.target.value)}
              onBlur={() => onBlur("type")}
              aria-invalid={errors.type ? true : undefined}
              aria-describedby={errors.type ? "q-type-error" : undefined}
              className={controlClass}
              style={{ borderColor: errors.type ? "#DC2626" : "#D4D4D0" }}
            >
              <option value="">Vyberte…</option>
              {TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
            {errors.type ? (
              <p id="q-type-error" className="mt-1.5 text-[13px] text-[#DC2626]">
                {errors.type}
              </p>
            ) : null}
          </div>
        </div>

        <div>
          <label htmlFor="q-budget" className={labelClass}>
            Rozpočet
          </label>
          <select
            id="q-budget"
            value={values.budget}
            onChange={(e) => setField("budget", e.target.value)}
            className={controlClass}
            style={{ borderColor: "#D4D4D0" }}
          >
            <option value="">Nechcem uvádzať</option>
            {BUDGETS.map((budget) => (
              <option key={budget} value={budget}>
                {budget}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="q-scope" className={labelClass}>
            Rozsah prác
          </label>
          <textarea
            id="q-scope"
            rows={5}
            placeholder="Napríklad: trojizbový byt, 72 m², kompletná rekonštrukcia vrátane rozvodov, kúpeľňa a kuchyňa na mieru."
            value={values.scope}
            onChange={(e) => setField("scope", e.target.value)}
            onBlur={() => onBlur("scope")}
            aria-invalid={errors.scope ? true : undefined}
            aria-describedby={errors.scope ? "q-scope-error" : undefined}
            className="w-full resize-y rounded border-2 bg-white px-4 py-3 text-[15px] focus:border-[#F5C518] focus:outline-none"
            style={{ borderColor: errors.scope ? "#DC2626" : "#D4D4D0" }}
          />
          {errors.scope ? (
            <p id="q-scope-error" className="mt-1.5 text-[13px] text-[#DC2626]">
              {errors.scope}
            </p>
          ) : null}
        </div>

        <button
          type="submit"
          disabled={status === "sending"}
          className="inline-flex h-12 items-center justify-center gap-2 bg-[#F5C518] px-8 font-bold uppercase tracking-wide text-[#1C1C1A] transition-colors duration-150 hover:bg-[#E0B30C] disabled:opacity-60"
        >
          {status === "sending" ? (
            <>
              <Loader2 aria-hidden="true" strokeWidth={2} className="size-4 animate-spin" />
              Odosiela sa…
            </>
          ) : (
            "Odoslať dopyt"
          )}
        </button>
      </div>
    </form>
  );
}
