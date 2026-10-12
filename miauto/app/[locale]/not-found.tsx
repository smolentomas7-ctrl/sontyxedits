import { getContent } from "@/content";
import { ButtonLink } from "@/components/ui/Button";
import { Container, Section } from "@/components/ui/Section";
import { DEFAULT_LOCALE, path } from "@/lib/i18n";

export default function NotFound() {
  const t = getContent(DEFAULT_LOCALE);
  return (
    <Section className="pt-[calc(var(--nav-h)+64px)]">
      <Container>
        <h1>{t.notFound.title}</h1>
        <p className="mt-5 max-w-[46ch] text-[color:var(--text-muted)]">{t.notFound.body}</p>
        <ButtonLink href={path(DEFAULT_LOCALE)} className="mt-8">
          {t.notFound.cta}
        </ButtonLink>
      </Container>
    </Section>
  );
}
