import { getContent } from "@/content";
import { ButtonLink } from "@/components/ui/Button";
import { Container, Section } from "@/components/ui/Section";
import { path } from "@/lib/i18n";

/**
 * A not-found boundary cannot read route params, so it cannot know which locale
 * the visitor came from. Rather than guess and be wrong half the time, it says
 * the same thing in both languages and offers both home pages.
 *
 * Next renders this in its own document rather than inside the locale layout,
 * because that layout needs a `locale` param and a 404 has none — so the page
 * arrives without the header and footer. The status code is a real 404 and both
 * home pages are one tap away, which is what a 404 is actually for.
 */
export default function NotFound() {
  const sk = getContent("sk");
  const en = getContent("en");

  return (
    <Section className="pt-[calc(var(--nav-h)+64px)]">
      <Container>
        <h1>{sk.notFound.title}</h1>
        <p className="mt-5 max-w-[46ch] text-[color:var(--text-muted)]">{sk.notFound.body}</p>

        <p
          lang="en"
          className="mt-8 max-w-[46ch] border-t border-[var(--border)] pt-8 text-[0.9375rem] text-[color:var(--text-muted)]"
        >
          <span className="text-[color:var(--text)]">{en.notFound.title}</span> {en.notFound.body}
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          <ButtonLink href={path("sk")}>{sk.notFound.cta}</ButtonLink>
          <ButtonLink href={path("en")} variant="secondary" lang="en">
            {en.notFound.cta}
          </ButtonLink>
        </div>
      </Container>
    </Section>
  );
}
