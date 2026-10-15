"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";
import { useCart } from "../CartContext";
import { formatPrice } from "../data";
import { submitForm, isNonEmpty, isValidEmail } from "@/lib/forms";

type Values = {
  email: string;
  name: string;
  street: string;
  city: string;
  zip: string;
  shipping: string;
  payment: string;
};

type Errors = Partial<Record<keyof Values, string>>;

const SHIPPING = [
  { id: "kurier", label: "Kuriér na adresu", price: 4.9, note: "1–2 pracovné dni" },
  { id: "odberne", label: "Odberné miesto", price: 2.9, note: "2–3 pracovné dni" },
  { id: "osobne", label: "Osobný odber", price: 0, note: "Po dohode" },
];

const PAYMENT = [
  { id: "karta", label: "Platobná karta" },
  { id: "prevod", label: "Bankový prevod" },
  { id: "dobierka", label: "Dobierka (+1,50 €)" },
];

const EMPTY: Values = {
  email: "",
  name: "",
  street: "",
  city: "",
  zip: "",
  shipping: "kurier",
  payment: "karta",
};

const labelClass = "mb-2 block text-[14px] font-medium text-[#1A1A18]";
const controlClass =
  "h-12 w-full rounded-lg border bg-white px-4 text-[15px] focus:outline-none focus:ring-2 focus:ring-[#A15D33]/40";

export default function CheckoutPage() {
  const { detailed, total, clear } = useCart();
  const [values, setValues] = useState<Values>(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  const [touched, setTouched] = useState<Partial<Record<keyof Values, boolean>>>({});
  const [status, setStatus] = useState<"idle" | "sending" | "success">("idle");

  const shippingOption = SHIPPING.find((s) => s.id === values.shipping) ?? SHIPPING[0];
  const codFee = values.payment === "dobierka" ? 1.5 : 0;
  const grandTotal = total + shippingOption.price + codFee;

  function validate(all: Values): Errors {
    const next: Errors = {};
    if (!isNonEmpty(all.email)) next.email = "Zadajte e-mail.";
    else if (!isValidEmail(all.email)) next.email = "Toto nevyzerá ako platný e-mail.";
    if (!isNonEmpty(all.name)) next.name = "Zadajte meno a priezvisko.";
    if (all.shipping !== "osobne") {
      if (!isNonEmpty(all.street)) next.street = "Zadajte ulicu a číslo.";
      if (!isNonEmpty(all.city)) next.city = "Zadajte mesto.";
      if (!isNonEmpty(all.zip)) next.zip = "Zadajte PSČ.";
      else if (!/^\d{3}\s?\d{2}$/.test(all.zip.trim())) next.zip = "PSČ má mať 5 číslic.";
    }
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
    setTouched({ email: true, name: true, street: true, city: true, zip: true });
    if (Object.values(found).some(Boolean)) return;

    setStatus("sending");
    await submitForm("shop-checkout", {
      ...values,
      items: detailed.map((d) => ({
        name: d.product.name,
        variant: d.line.variant,
        quantity: d.line.quantity,
      })),
      total: grandTotal,
    });
    clear();
    setStatus("success");
  }

  if (status === "success") {
    return (
      <div className="mx-auto max-w-[640px] px-5 py-20 text-center md:px-8 md:py-28">
        <CheckCircle2
          aria-hidden="true"
          strokeWidth={1.5}
          className="mx-auto size-12 text-[#2F7A4F]"
        />
        <h1 className="mt-6 font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold tracking-[-0.025em]">
          Objednávka prijatá
        </h1>
        <p className="mt-4 text-[16px] text-[#4A4A46]">
          V skutočnom e-shope by vám teraz prišlo potvrdenie na {values.email || "váš e-mail"}.
        </p>
        <p className="mt-6 rounded-xl border border-[#E8C89A] bg-[#FDF6EA] px-5 py-4 text-[14px] text-[#7A5520]">
          Toto je ukážkový web. Žiadna objednávka nevznikla, neprebehla žiadna platba a nikomu
          sa nič neodoslalo.
        </p>
        <Link
          href="/demo/shop"
          className="mt-8 inline-flex h-12 items-center rounded-lg bg-[#1A1A18] px-7 font-medium text-white"
        >
          Späť do obchodu
        </Link>
      </div>
    );
  }

  if (detailed.length === 0) {
    return (
      <div className="mx-auto max-w-[640px] px-5 py-20 text-center md:px-8 md:py-28">
        <h1 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold tracking-[-0.025em]">
          Košík je prázdny
        </h1>
        <p className="mt-4 text-[16px] text-[#4A4A46]">
          Pridajte do košíka aspoň jeden produkt a vráťte sa do pokladne.
        </p>
        <Link
          href="/demo/shop/produkty"
          className="mt-8 inline-flex h-12 items-center rounded-lg bg-[#1A1A18] px-7 font-medium text-white"
        >
          Prejsť na produkty
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[1240px] px-5 py-14 md:px-8 md:py-20">
      <h1 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold tracking-[-0.025em] md:text-[2.75rem]">
        Pokladňa
      </h1>

      <div
        role="note"
        className="mt-6 flex gap-3 rounded-xl border border-[#E8C89A] bg-[#FDF6EA] p-5"
      >
        <AlertTriangle
          aria-hidden="true"
          strokeWidth={1.5}
          className="mt-0.5 size-5 shrink-0 text-[#A15D33]"
        />
        <p className="text-[15px] leading-relaxed text-[#7A5520]">
          <strong className="font-semibold">Toto je iba ukážka rozhrania.</strong> Neprebehne
          žiadna platba, nespracúvame údaje o karte a objednávka sa nikam neodošle. Formulár
          slúži len na predvedenie, ako by pokladňa vyzerala a správala sa.
        </p>
      </div>

      <form onSubmit={onSubmit} noValidate className="mt-10 grid gap-10 lg:grid-cols-[1.3fr_1fr]">
        <div className="flex flex-col gap-8">
          <fieldset>
            <legend className="mb-4 font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
              Kontakt
            </legend>
            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <label htmlFor="co-email" className={labelClass}>
                  E-mail
                </label>
                <input
                  id="co-email"
                  type="email"
                  autoComplete="email"
                  value={values.email}
                  onChange={(e) => setField("email", e.target.value)}
                  onBlur={() => onBlur("email")}
                  aria-invalid={errors.email ? true : undefined}
                  aria-describedby={errors.email ? "co-email-error" : undefined}
                  className={controlClass}
                  style={{ borderColor: errors.email ? "#DC2626" : "#E5E5E3" }}
                />
                {errors.email ? (
                  <p id="co-email-error" className="mt-1.5 text-[13px] text-[#DC2626]">
                    {errors.email}
                  </p>
                ) : null}
              </div>
              <div>
                <label htmlFor="co-name" className={labelClass}>
                  Meno a priezvisko
                </label>
                <input
                  id="co-name"
                  type="text"
                  autoComplete="name"
                  value={values.name}
                  onChange={(e) => setField("name", e.target.value)}
                  onBlur={() => onBlur("name")}
                  aria-invalid={errors.name ? true : undefined}
                  aria-describedby={errors.name ? "co-name-error" : undefined}
                  className={controlClass}
                  style={{ borderColor: errors.name ? "#DC2626" : "#E5E5E3" }}
                />
                {errors.name ? (
                  <p id="co-name-error" className="mt-1.5 text-[13px] text-[#DC2626]">
                    {errors.name}
                  </p>
                ) : null}
              </div>
            </div>
          </fieldset>

          <fieldset>
            <legend className="mb-4 font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
              Doprava
            </legend>
            <div className="flex flex-col gap-2.5">
              {SHIPPING.map((option) => {
                const selected = values.shipping === option.id;
                return (
                  <label
                    key={option.id}
                    className="flex cursor-pointer items-center justify-between gap-4 rounded-lg border px-4 py-3.5 transition-colors duration-150"
                    style={{
                      borderColor: selected ? "#1A1A18" : "#E5E5E3",
                      background: selected ? "#FAFAF8" : "#FFFFFF",
                    }}
                  >
                    <span className="flex items-center gap-3">
                      <input
                        type="radio"
                        name="shipping"
                        value={option.id}
                        checked={selected}
                        onChange={() => setField("shipping", option.id)}
                        className="size-4 accent-[#A15D33]"
                      />
                      <span>
                        <span className="block text-[15px] font-medium">{option.label}</span>
                        <span className="block text-[13px] text-[#6E6E68]">{option.note}</span>
                      </span>
                    </span>
                    <span className="shrink-0 font-medium">
                      {option.price === 0 ? "Zadarmo" : formatPrice(option.price)}
                    </span>
                  </label>
                );
              })}
            </div>
          </fieldset>

          {values.shipping !== "osobne" ? (
            <fieldset>
              <legend className="mb-4 font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
                Adresa
              </legend>
              <div className="grid gap-5 sm:grid-cols-2">
                <div className="sm:col-span-2">
                  <label htmlFor="co-street" className={labelClass}>
                    Ulica a číslo
                  </label>
                  <input
                    id="co-street"
                    type="text"
                    autoComplete="street-address"
                    value={values.street}
                    onChange={(e) => setField("street", e.target.value)}
                    onBlur={() => onBlur("street")}
                    aria-invalid={errors.street ? true : undefined}
                    aria-describedby={errors.street ? "co-street-error" : undefined}
                    className={controlClass}
                    style={{ borderColor: errors.street ? "#DC2626" : "#E5E5E3" }}
                  />
                  {errors.street ? (
                    <p id="co-street-error" className="mt-1.5 text-[13px] text-[#DC2626]">
                      {errors.street}
                    </p>
                  ) : null}
                </div>
                <div>
                  <label htmlFor="co-city" className={labelClass}>
                    Mesto
                  </label>
                  <input
                    id="co-city"
                    type="text"
                    autoComplete="address-level2"
                    value={values.city}
                    onChange={(e) => setField("city", e.target.value)}
                    onBlur={() => onBlur("city")}
                    aria-invalid={errors.city ? true : undefined}
                    aria-describedby={errors.city ? "co-city-error" : undefined}
                    className={controlClass}
                    style={{ borderColor: errors.city ? "#DC2626" : "#E5E5E3" }}
                  />
                  {errors.city ? (
                    <p id="co-city-error" className="mt-1.5 text-[13px] text-[#DC2626]">
                      {errors.city}
                    </p>
                  ) : null}
                </div>
                <div>
                  <label htmlFor="co-zip" className={labelClass}>
                    PSČ
                  </label>
                  <input
                    id="co-zip"
                    type="text"
                    inputMode="numeric"
                    autoComplete="postal-code"
                    value={values.zip}
                    onChange={(e) => setField("zip", e.target.value)}
                    onBlur={() => onBlur("zip")}
                    aria-invalid={errors.zip ? true : undefined}
                    aria-describedby={errors.zip ? "co-zip-error" : undefined}
                    className={controlClass}
                    style={{ borderColor: errors.zip ? "#DC2626" : "#E5E5E3" }}
                  />
                  {errors.zip ? (
                    <p id="co-zip-error" className="mt-1.5 text-[13px] text-[#DC2626]">
                      {errors.zip}
                    </p>
                  ) : null}
                </div>
              </div>
            </fieldset>
          ) : null}

          <fieldset>
            <legend className="mb-4 font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
              Platba
            </legend>
            <div className="flex flex-col gap-2.5">
              {PAYMENT.map((option) => {
                const selected = values.payment === option.id;
                return (
                  <label
                    key={option.id}
                    className="flex cursor-pointer items-center gap-3 rounded-lg border px-4 py-3.5 transition-colors duration-150"
                    style={{
                      borderColor: selected ? "#1A1A18" : "#E5E5E3",
                      background: selected ? "#FAFAF8" : "#FFFFFF",
                    }}
                  >
                    <input
                      type="radio"
                      name="payment"
                      value={option.id}
                      checked={selected}
                      onChange={() => setField("payment", option.id)}
                      className="size-4 accent-[#A15D33]"
                    />
                    <span className="text-[15px]">{option.label}</span>
                  </label>
                );
              })}
            </div>
            <p className="mt-3 text-[13px] text-[#6E6E68]">
              Nezadávate žiadne údaje o karte — v ukážke by na ne nebolo kam.
            </p>
          </fieldset>
        </div>

        {/* ---------- summary ---------- */}
        <aside className="lg:sticky lg:top-40 lg:self-start">
          <div className="rounded-2xl border border-[#E5E5E3] bg-[#F6F5F2] p-6">
            <h2 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
              Zhrnutie
            </h2>

            <ul className="mt-5 flex flex-col gap-4">
              {detailed.map(({ line, product }) => (
                <li key={line.key} className="flex gap-3">
                  <Image
                    src={product.gallery[0].src}
                    width={product.gallery[0].width}
                    height={product.gallery[0].height}
                    alt=""
                    sizes="56px"
                    className="size-14 shrink-0 rounded-lg bg-white object-cover"
                  />
                  <div className="min-w-0 flex-1 text-[14px]">
                    <p className="truncate font-medium">{product.name}</p>
                    {line.variant ? <p className="text-[#6E6E68]">{line.variant}</p> : null}
                    <p className="text-[#6E6E68]">{line.quantity} ks</p>
                  </div>
                  <p className="shrink-0 text-[14px] font-medium">
                    {formatPrice(product.price * line.quantity)}
                  </p>
                </li>
              ))}
            </ul>

            <dl className="mt-6 border-t border-[#E5E5E3] pt-5 text-[15px]">
              <div className="flex justify-between py-1.5">
                <dt className="text-[#6E6E68]">Medzisúčet</dt>
                <dd>{formatPrice(total)}</dd>
              </div>
              <div className="flex justify-between py-1.5">
                <dt className="text-[#6E6E68]">Doprava</dt>
                <dd>
                  {shippingOption.price === 0 ? "Zadarmo" : formatPrice(shippingOption.price)}
                </dd>
              </div>
              {codFee > 0 ? (
                <div className="flex justify-between py-1.5">
                  <dt className="text-[#6E6E68]">Dobierka</dt>
                  <dd>{formatPrice(codFee)}</dd>
                </div>
              ) : null}
              <div className="mt-2 flex items-baseline justify-between border-t border-[#E5E5E3] pt-4">
                <dt className="font-medium">Spolu</dt>
                <dd
                  aria-live="polite"
                  className="font-[family-name:var(--font-space-grotesk)] text-2xl font-bold"
                >
                  {formatPrice(grandTotal)}
                </dd>
              </div>
            </dl>

            <button
              type="submit"
              disabled={status === "sending"}
              className="mt-6 inline-flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-[#1A1A18] font-medium text-white transition-colors duration-150 hover:bg-[#333330] disabled:opacity-60"
            >
              {status === "sending" ? (
                <>
                  <Loader2 aria-hidden="true" strokeWidth={1.5} className="size-4 animate-spin" />
                  Spracúva sa…
                </>
              ) : (
                "Dokončiť objednávku"
              )}
            </button>
            <p className="mt-3 text-center text-[13px] text-[#6E6E68]">
              Neprebehne žiadna platba.
            </p>
          </div>
        </aside>
      </form>
    </div>
  );
}
