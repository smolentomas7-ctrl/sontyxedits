import { Phone } from "lucide-react";
import { site } from "@/config/miauto";
import { ROUTES, path } from "@/lib/i18n";
import { ButtonLink } from "@/components/ui/Button";
import { Container, Section } from "@/components/ui/Section";
import { Reveal } from "@/components/ui/Reveal";
import type { Locale, LocaleContent } from "@/content/types";

/**
 * Final CTA. The phone number is the dominant element on the page here — it is
 * set at display size and is the only accent-filled thing on screen.
 */
export function CtaBand({
  locale,
  t,
  heading,
  lead,
}: {
  locale: Locale;
  t: LocaleContent;
  heading: string;
  lead: string;
}) {
  return (
    <Section className="border-t border-[var(--border)] bg-[var(--surface)]">
      <Container>
        <Reveal className="mx-auto max-w-[52rem] text-center">
          <h2 className="text-balance">{heading}</h2>
          <p className="mx-auto mt-5 max-w-[46ch] text-[1.0625rem] text-[color:var(--text-muted)]">
            {lead}
          </p>

          <a
            href={site.phoneHref}
            aria-label={t.common.callAria}
            className="tappable mt-10 inline-flex items-center gap-3 font-heading text-[clamp(1.75rem,1rem+3.4vw,3rem)] font-bold tracking-[-0.03em] text-[color:var(--text)] no-underline hover:text-[color:var(--accent)]"
            style={{ ["--press-scale" as string]: "0.98" }}
          >
            <Phone
              className="shrink-0 text-[color:var(--accent)]"
              size={32}
              strokeWidth={1.8}
              aria-hidden="true"
            />
            {site.phone}
          </a>

          <div className="mt-10 flex flex-wrap justify-center gap-3">
            <ButtonLink href={site.phoneHref} aria-label={t.common.callAria}>
              {t.common.callCta}
            </ButtonLink>
            <ButtonLink href={path(locale, ROUTES.contact)} variant="secondary">
              {t.common.contactCta}
            </ButtonLink>
          </div>
        </Reveal>
      </Container>
    </Section>
  );
}
