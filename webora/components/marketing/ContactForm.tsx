"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { CheckCircle2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { TextField, TextArea, SelectField, CheckboxField } from "@/components/ui/Field";
import { submitForm, isValidEmail, isValidPhone, isNonEmpty, hasMinLength } from "@/lib/forms";
import type { Dictionary, Locale } from "@/content/i18n";

type Values = {
  name: string;
  email: string;
  phone: string;
  company: string;
  projectType: string;
  message: string;
  consent: boolean;
};

type Errors = Partial<Record<keyof Values, string>>;

const EMPTY: Values = {
  name: "",
  email: "",
  phone: "",
  company: "",
  projectType: "",
  message: "",
  consent: false,
};

export function ContactForm({ locale, dict }: { locale: Locale; dict: Dictionary }) {
  const searchParams = useSearchParams();
  const t = dict.contact;

  const [values, setValues] = useState<Values>(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  const [touched, setTouched] = useState<Partial<Record<keyof Values, boolean>>>({});
  const [status, setStatus] = useState<"idle" | "sending" | "success" | "error">("idle");

  // Prefill from ?type= and ?message= — used by the feature catalogue, the
  // individual-pricing section and the demo bars.
  useEffect(() => {
    const type = searchParams.get("type") ?? "";
    const message = searchParams.get("message") ?? "";
    if (!type && !message) return;

    setValues((current) => ({
      ...current,
      projectType: t.projectTypes.includes(type) ? type : current.projectType,
      message: message || current.message,
    }));
  }, [searchParams, t.projectTypes]);

  function validate(all: Values): Errors {
    const next: Errors = {};
    if (!isNonEmpty(all.name)) next.name = t.errors.nameRequired;

    if (!isNonEmpty(all.email)) {
      next.email = t.errors.emailRequired;
    } else if (!isValidEmail(all.email)) {
      next.email = t.errors.emailInvalid;
    }

    if (!isValidPhone(all.phone)) next.phone = t.errors.phoneInvalid;

    if (!isNonEmpty(all.message)) {
      next.message = t.errors.messageRequired;
    } else if (!hasMinLength(all.message, 20)) {
      next.message = t.errors.messageShort;
    }

    if (!all.consent) next.consent = t.errors.consentRequired;
    return next;
  }

  function setField<K extends keyof Values>(key: K, value: Values[K]) {
    const next = { ...values, [key]: value };
    setValues(next);
    // Once a field has been blurred, re-validate as the visitor types so the
    // error clears the moment it is fixed.
    if (touched[key]) {
      setErrors((current) => ({ ...current, [key]: validate(next)[key] }));
    }
  }

  function onBlur(key: keyof Values) {
    setTouched((current) => ({ ...current, [key]: true }));
    setErrors((current) => ({ ...current, [key]: validate(values)[key] }));
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    const found = validate(values);
    setErrors(found);
    setTouched({
      name: true,
      email: true,
      phone: true,
      message: true,
      consent: true,
    });

    if (Object.values(found).some(Boolean)) {
      // Move focus to the first field with a problem.
      const firstKey = (["name", "email", "phone", "message", "consent"] as const).find(
        (key) => found[key],
      );
      if (firstKey) {
        document.querySelector<HTMLElement>(`[name="${firstKey}"]`)?.focus();
      }
      return;
    }

    setStatus("sending");
    const result = await submitForm("contact", { ...values, locale });
    setStatus(result.ok ? "success" : "error");
  }

  if (status === "success") {
    return (
      <div className="rounded-2xl border border-accent/30 bg-accent-soft p-8" role="status">
        <CheckCircle2 aria-hidden="true" strokeWidth={1.5} className="size-8 text-accent" />
        <h2 className="t-h3 mt-4 text-text">{t.successTitle}</h2>
        <p className="mt-3 max-w-[48ch] text-text-muted">{t.successBody}</p>
        <p className="t-small mt-4 max-w-[48ch] rounded-lg border border-border bg-surface px-4 py-3 text-text-muted">
          {t.successNote}
        </p>
        <Button
          variant="secondary"
          className="mt-7"
          onClick={() => {
            setValues(EMPTY);
            setErrors({});
            setTouched({});
            setStatus("idle");
          }}
        >
          {t.sendAnother}
        </Button>
      </div>
    );
  }

  const projectTypeOptions = t.projectTypes.map((type) => ({ value: type, label: type }));

  return (
    <form onSubmit={onSubmit} noValidate className="flex flex-col gap-5">
      <h2 className="t-h3 text-text">{t.formTitle}</h2>

      {status === "error" ? (
        <div
          role="alert"
          className="flex gap-3 rounded-xl border border-danger/40 bg-danger/10 p-4"
        >
          <AlertCircle
            aria-hidden="true"
            strokeWidth={1.5}
            className="mt-0.5 size-5 shrink-0 text-danger"
          />
          <div>
            <p className="font-medium text-text">{t.errorTitle}</p>
            <p className="t-small mt-1 text-text-muted">{t.errorBody}</p>
          </div>
        </div>
      ) : null}

      <div className="grid gap-5 sm:grid-cols-2">
        <TextField
          label={t.name}
          name="name"
          autoComplete="name"
          required
          value={values.name}
          error={errors.name}
          onChange={(e) => setField("name", e.target.value)}
          onBlur={() => onBlur("name")}
        />
        <TextField
          label={t.email}
          name="email"
          type="email"
          autoComplete="email"
          required
          value={values.email}
          error={errors.email}
          onChange={(e) => setField("email", e.target.value)}
          onBlur={() => onBlur("email")}
        />
        <TextField
          label={t.phone}
          name="phone"
          type="tel"
          autoComplete="tel"
          optionalLabel={dict.common.optional}
          value={values.phone}
          error={errors.phone}
          onChange={(e) => setField("phone", e.target.value)}
          onBlur={() => onBlur("phone")}
        />
        <TextField
          label={t.company}
          name="company"
          autoComplete="organization"
          optionalLabel={dict.common.optional}
          value={values.company}
          onChange={(e) => setField("company", e.target.value)}
        />
        <div className="sm:col-span-2">
          <SelectField
            label={t.projectType}
            name="projectType"
            options={projectTypeOptions}
            placeholder={t.projectTypePlaceholder}
            value={values.projectType}
            onChange={(e) => setField("projectType", e.target.value)}
          />
        </div>
      </div>

      <TextArea
        label={t.message}
        name="message"
        required
        rows={7}
        placeholder={t.messagePlaceholder}
        value={values.message}
        error={errors.message}
        onChange={(e) => setField("message", e.target.value)}
        onBlur={() => onBlur("message")}
      />

      <CheckboxField
        label={t.consent}
        name="consent"
        required
        checked={values.consent}
        error={errors.consent}
        onChange={(e) => setField("consent", e.target.checked)}
        onBlur={() => onBlur("consent")}
      />

      <Button
        type="submit"
        size="lg"
        loading={status === "sending"}
        loadingLabel={t.sending}
        className="mt-1 self-start"
      >
        {t.submit}
      </Button>
    </form>
  );
}
