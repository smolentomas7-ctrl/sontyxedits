"use client";

import { AlertCircle, CheckCircle2, Loader2, Phone } from "lucide-react";
import Link from "next/link";
import { useId, useRef, useState } from "react";
import { SERVICE_SLUGS } from "@/content/types";
import { site } from "@/config/miauto";
import { ROUTES, path } from "@/lib/i18n";
import { MIN_FILL_MS, isPlausibleEmail, isPlausiblePhone, submitForm } from "@/lib/forms";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Field, inputClasses, textareaClasses } from "@/components/ui/Field";
import type { Locale, LocaleContent } from "@/content/types";

const FORM_NAME = "dopyt";
const MESSAGE_MAX = 1500;

type Status = "idle" | "submitting" | "error" | "success";
type FieldName = "name" | "phone" | "email" | "message" | "consent";
type Errors = Partial<Record<FieldName, string>>;

export function ContactForm({ locale, t }: { locale: Locale; t: LocaleContent }) {
  const uid = useId();
  const mountedAt = useRef(Date.now());
  const [status, setStatus] = useState<Status>("idle");
  const [errors, setErrors] = useState<Errors>({});
  const [touched, setTouched] = useState<Partial<Record<FieldName, boolean>>>({});
  const [values, setValues] = useState({
    name: "",
    phone: "",
    email: "",
    vehicle: "",
    service: "",
    message: "",
    consent: false,
    "bot-field": "",
  });

  const set = <K extends keyof typeof values>(key: K, value: (typeof values)[K]) =>
    setValues((previous) => ({ ...previous, [key]: value }));

  /**
   * `seen` is passed explicitly rather than read from state: a blur handler sets
   * `touched` and validates in the same tick, and reading `touched` from the
   * closure there would still see the value from before the blur, so the first
   * error on a field would never appear.
   */
  function validate(all = false, seen: Partial<Record<FieldName, boolean>> = touched): Errors {
    const next: Errors = {};
    const name = values.name.trim();
    if (all || seen.name) {
      if (name === "") next.name = t.form.errors.nameRequired;
      else if (name.length < 2 || name.length > 80) next.name = t.form.errors.nameLength;
    }
    if (all || seen.phone) {
      if (values.phone.trim() === "") next.phone = t.form.errors.phoneRequired;
      else if (!isPlausiblePhone(values.phone)) next.phone = t.form.errors.phoneInvalid;
    }
    if ((all || seen.email) && !isPlausibleEmail(values.email)) {
      next.email = t.form.errors.emailInvalid;
    }
    const message = values.message.trim();
    if (all || seen.message) {
      if (message === "") next.message = t.form.errors.messageRequired;
      else if (message.length < 10 || message.length > MESSAGE_MAX) {
        next.message = t.form.errors.messageLength;
      }
    }
    if ((all || seen.consent) && !values.consent) {
      next.consent = t.form.errors.consentRequired;
    }
    return next;
  }

  // Submit stays disabled until the required fields validate, and the reason is
  // written out in text below the button rather than implied by the colour.
  const ready =
    values.name.trim().length >= 2 &&
    isPlausiblePhone(values.phone) &&
    values.message.trim().length >= 10 &&
    values.consent &&
    isPlausibleEmail(values.email);

  const blur = (field: FieldName) => {
    const seen = { ...touched, [field]: true };
    setTouched(seen);
    setErrors(validate(false, seen));
  };

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTouched({ name: true, phone: true, email: true, message: true, consent: true });
    const found = validate(true, {});
    setErrors(found);
    if (Object.keys(found).length > 0) return;

    // Timing check, in place of a CAPTCHA.
    if (Date.now() - mountedAt.current < MIN_FILL_MS) {
      setErrors({ message: t.form.errors.tooFast });
      return;
    }
    if (values["bot-field"] !== "") return; // honeypot tripped: fail silently

    setStatus("submitting");
    const result = await submitForm(FORM_NAME, {
      meno: values.name.trim(),
      telefon: values.phone.trim(),
      email: values.email.trim(),
      vozidlo: values.vehicle.trim(),
      sluzba: values.service || t.form.serviceOther,
      sprava: values.message.trim(),
      suhlas: "ano",
      locale,
      "bot-field": "",
    });

    // No false success. A 404 from a non-Netlify host lands here, as an error.
    setStatus(result.ok ? "success" : "error");
  }

  if (status === "success") {
    return (
      <div className="rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--surface)] p-7 md:p-9">
        <CheckCircle2 size={28} aria-hidden="true" className="text-[color:var(--success)]" />
        <h3 className="mt-5 text-[1.375rem]">{t.form.successHeading}</h3>
        <p className="mt-3 max-w-[48ch] text-[color:var(--text-muted)]">{t.form.successBody}</p>
        <ButtonLink href={site.phoneHref} className="mt-7" aria-label={t.common.callAria}>
          <Phone size={17} aria-hidden="true" />
          {site.phone}
        </ButtonLink>
      </div>
    );
  }

  const busy = status === "submitting";

  return (
    <form onSubmit={onSubmit} noValidate className="flex flex-col gap-6">
      {/* Honeypot. Visually hidden but NOT display:none, so bots still fill it. */}
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          width: 1,
          height: 1,
          overflow: "hidden",
          clip: "rect(0 0 0 0)",
          whiteSpace: "nowrap",
        }}
      >
        <label htmlFor={`${uid}-bot`}>Do not fill this in</label>
        <input
          id={`${uid}-bot`}
          name="bot-field"
          tabIndex={-1}
          autoComplete="off"
          value={values["bot-field"]}
          onChange={(e) => set("bot-field", e.target.value)}
        />
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <Field id={`${uid}-name`} label={t.form.name} error={errors.name}>
          {(props) => (
            <input
              {...props}
              type="text"
              name="meno"
              autoComplete="name"
              maxLength={80}
              readOnly={busy}
              placeholder={t.form.namePlaceholder}
              value={values.name}
              onChange={(e) => set("name", e.target.value)}
              onBlur={() => blur("name")}
            />
          )}
        </Field>

        <Field id={`${uid}-phone`} label={t.form.phone} error={errors.phone}>
          {(props) => (
            <input
              {...props}
              type="tel"
              name="telefon"
              autoComplete="tel"
              inputMode="tel"
              readOnly={busy}
              placeholder={t.form.phonePlaceholder}
              value={values.phone}
              onChange={(e) => set("phone", e.target.value)}
              onBlur={() => blur("phone")}
            />
          )}
        </Field>

        <Field
          id={`${uid}-email`}
          label={t.form.email}
          optional={t.form.emailOptional}
          error={errors.email}
        >
          {(props) => (
            <input
              {...props}
              type="email"
              name="email"
              autoComplete="email"
              readOnly={busy}
              value={values.email}
              onChange={(e) => set("email", e.target.value)}
              onBlur={() => blur("email")}
            />
          )}
        </Field>

        <Field
          id={`${uid}-vehicle`}
          label={t.form.vehicle}
          optional={t.form.emailOptional}
          hint={t.form.vehicleHint}
        >
          {(props) => (
            <input
              {...props}
              type="text"
              name="vozidlo"
              maxLength={120}
              readOnly={busy}
              placeholder={t.form.vehiclePlaceholder}
              value={values.vehicle}
              onChange={(e) => set("vehicle", e.target.value)}
            />
          )}
        </Field>
      </div>

      <Field id={`${uid}-service`} label={t.form.service}>
        {(props) => (
          <select
            {...props}
            name="sluzba"
            disabled={busy}
            value={values.service}
            onChange={(e) => set("service", e.target.value)}
            className={`${inputClasses} appearance-none`}
          >
            <option value="">{t.form.servicePrompt}</option>
            {SERVICE_SLUGS.map((slug) => (
              <option key={slug} value={t.services[slug].name}>
                {t.services[slug].name}
              </option>
            ))}
            <option value={t.form.serviceOther}>{t.form.serviceOther}</option>
          </select>
        )}
      </Field>

      <Field id={`${uid}-message`} label={t.form.message} error={errors.message}>
        {(props) => (
          <textarea
            {...props}
            name="sprava"
            rows={6}
            maxLength={MESSAGE_MAX}
            readOnly={busy}
            placeholder={t.form.messagePlaceholder}
            value={values.message}
            onChange={(e) => set("message", e.target.value)}
            onBlur={() => blur("message")}
            className={`${textareaClasses} ${errors.message ? "border-[var(--danger)]" : ""}`}
          />
        )}
      </Field>

      <div>
        <label className="flex cursor-pointer items-start gap-3 text-[0.9375rem]">
          <input
            type="checkbox"
            name="suhlas"
            checked={values.consent}
            disabled={busy}
            onChange={(e) => set("consent", e.target.checked)}
            onBlur={() => blur("consent")}
            aria-describedby={errors.consent ? `${uid}-consent-error` : undefined}
            className="mt-0.5 size-5 shrink-0 accent-[var(--accent)]"
          />
          <span className="text-[color:var(--text-muted)]">
            {t.form.consent}{" "}
            <Link href={path(locale, ROUTES.privacy)} className="text-[color:var(--accent)]">
              {t.form.consentLink}
            </Link>
          </span>
        </label>
        {errors.consent ? (
          <p
            id={`${uid}-consent-error`}
            className="mt-2 text-[0.8125rem] font-medium text-[color:var(--danger)]"
          >
            {errors.consent}
          </p>
        ) : null}
      </div>

      {status === "error" ? (
        <div
          role="alert"
          className="rounded-[var(--radius-card)] border border-[var(--danger)] bg-[color-mix(in_srgb,var(--danger)_10%,transparent)] p-5"
        >
          <p className="flex items-center gap-2 font-semibold text-[color:var(--danger)]">
            <AlertCircle size={18} aria-hidden="true" />
            {t.form.errorHeading}
          </p>
          <p className="mt-2 text-[0.9375rem]">{t.form.errorBody}</p>
          <a
            href={site.phoneHref}
            className="mt-3 inline-flex items-center gap-2 font-semibold no-underline hover:text-[color:var(--accent)]"
          >
            <Phone size={17} aria-hidden="true" />
            {site.phone}
          </a>
        </div>
      ) : null}

      <div className="flex flex-col gap-3">
        <Button type="submit" disabled={!ready || busy} className="self-start">
          {busy ? (
            <>
              <Loader2 size={18} aria-hidden="true" className="animate-spin" />
              {t.form.submitting}
            </>
          ) : (
            t.form.submit
          )}
        </Button>
        {!ready && !busy ? (
          <p className="text-[0.8125rem] text-[color:var(--text-muted)]">{t.form.disabledReason}</p>
        ) : null}
      </div>
    </form>
  );
}
