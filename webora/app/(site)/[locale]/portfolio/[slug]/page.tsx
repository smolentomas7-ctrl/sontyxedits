import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, ArrowUpRight, Check, Info } from "lucide-react";
import { Container } from "@/components/ui/Container";
import { Section } from "@/components/ui/Section";
import { ButtonLink } from "@/components/ui/Button";
import { Reveal } from "@/components/ui/Reveal";
import { Tilt } from "@/components/ui/Tilt";
import { BrowserFrame } from "@/components/ui/BrowserFrame";
import { ContactButtons } from "@/components/marketing/ContactOptions";
import { mailtoHref } from "@/config/site";
import { getDictionary, isLocale, LOCALES, type Locale } from "@/content/i18n";
import { projects, getProject } from "@/content/projects";
import { buildAlternates, ogImages } from "@/lib/seo";
import { cn } from "@/lib/utils";

export function generateStaticParams() {
  return LOCALES.flatMap((locale) => projects.map((project) => ({ locale, slug: project.slug })));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, slug } = await params;
  if (!isLocale(locale)) return {};
  const project = getProject(slug);
  if (!project) return {};

  const title = `${project.name} — ${project.categoryLabel[locale]}`;
  return {
    title,
    description: project.summary[locale],
    alternates: buildAlternates(`portfolio/${slug}`),
    openGraph: {
      title,
      description: project.summary[locale],
      type: "article",
      images: ogImages(locale),
    },
  };
}

export default async function CaseStudyPage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  if (!isLocale(locale)) notFound();
  const typedLocale: Locale = locale;
  const dict = getDictionary(typedLocale);

  const project = getProject(slug);
  if (!project) notFound();

  const index = projects.findIndex((p) => p.slug === slug);
  const next = projects[(index + 1) % projects.length];
  const isClient = project.kind === "client";

  return (
    <>
      <Container>
        <div className="py-16 md:py-24">
          <Link
            href={`/${typedLocale}/portfolio`}
            className="inline-flex items-center gap-1.5 text-[14px] text-text-muted transition-colors duration-150 hover:text-accent"
          >
            <ArrowLeft aria-hidden="true" strokeWidth={1.5} className="size-4" />
            {dict.common.backToPortfolio}
          </Link>

          <header className="mt-8 flex flex-col gap-5">
            <div className="flex flex-wrap items-center gap-2">
              <span
                className={cn(
                  "rounded-full px-3 py-1 text-[12px] font-medium uppercase tracking-[0.1em]",
                  isClient
                    ? "bg-accent-soft text-accent"
                    : "border border-border text-text-muted",
                )}
              >
                {isClient ? dict.portfolio.clientBadge : dict.portfolio.demoBadge}
              </span>
              <span className="t-small text-text-muted">{project.categoryLabel[typedLocale]}</span>
            </div>

            <h1 className="t-h1 max-w-[16ch] text-balance text-text">{project.name}</h1>
            <p className="t-prose text-lg text-text-muted">{project.summary[typedLocale]}</p>

            <dl className="mt-2 flex flex-wrap gap-x-10 gap-y-4 border-t border-border pt-6">
              <div>
                <dt className="t-small text-text-muted">{dict.caseStudy.type}</dt>
                <dd className="mt-0.5 font-medium text-text">
                  {project.categoryLabel[typedLocale]}
                </dd>
              </div>
              <div>
                <dt className="t-small text-text-muted">{dict.caseStudy.year}</dt>
                <dd className="mt-0.5 font-medium text-text">{project.year}</dd>
              </div>
            </dl>

            <div className="mt-2 flex flex-col gap-3 sm:flex-row">
              <ButtonLink
                href={project.href}
                size="lg"
                external={Boolean(project.external)}
                target={project.external ? "_blank" : undefined}
              >
                {isClient ? dict.common.viewExample : dict.common.openLiveDemo}
                <ArrowUpRight aria-hidden="true" strokeWidth={1.5} className="size-4" />
              </ButtonLink>
              <ButtonLink
                href={mailtoHref(`${dict.contact.mailSubject} — ${project.categoryLabel[typedLocale]}`)}
                external
                variant="secondary"
                size="lg"
              >
                {dict.caseStudy.ctaButton}
              </ButtonLink>
            </div>
          </header>

          {/* ---------- hero capture ---------- */}
          <Reveal className="mt-14">
            <Tilt max={3.5} scale={1.006} depth={6} glare>
              <BrowserFrame url={project.domain}>
                <Image
                  src={project.preview.src}
                  width={project.preview.width}
                  height={project.preview.height}
                  alt={project.preview.alt}
                  priority
                  sizes="(max-width: 1200px) 100vw, 1200px"
                  className="w-full object-cover"
                />
              </BrowserFrame>
            </Tilt>
          </Reveal>

          <p className="t-small mt-5 flex max-w-[66ch] gap-2.5 text-text-muted">
            <Info aria-hidden="true" strokeWidth={1.5} className="mt-0.5 size-4 shrink-0 text-accent" />
            {isClient ? dict.caseStudy.liveNote : dict.caseStudy.demoNote}
          </p>
        </div>
      </Container>

      {/* ---------- overview + what it covered ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="overview-heading">
        <div className="grid gap-12 lg:grid-cols-[1fr_1.15fr] lg:gap-16">
          <Reveal>
            <h2 id="overview-heading" className="t-h2 text-text">
              {dict.caseStudy.overview}
            </h2>
            <p className="t-prose mt-6 text-text-muted">{project.intro[typedLocale]}</p>

            <h3 className="t-small mt-10 mb-4 font-medium uppercase tracking-[0.12em] text-text">
              {dict.caseStudy.capabilities}
            </h3>
            <ul className="flex flex-wrap gap-2">
              {project.capabilities[typedLocale].map((cap) => (
                <li
                  key={cap}
                  className="rounded-lg border border-border bg-surface px-3 py-1.5 text-[14px] text-text-muted"
                >
                  {cap}
                </li>
              ))}
            </ul>
          </Reveal>

          <Reveal delay={80}>
            <h3 className="t-h3 mb-6 text-text">{dict.caseStudy.whatWeBuilt}</h3>
            <ul className="flex flex-col gap-4">
              {project.highlights[typedLocale].map((item) => (
                <li key={item} className="flex items-start gap-3 text-[15px] text-text-muted">
                  <Check
                    aria-hidden="true"
                    strokeWidth={1.5}
                    className="mt-0.5 size-4 shrink-0 text-accent"
                  />
                  {item}
                </li>
              ))}
            </ul>
          </Reveal>
        </div>
      </Section>

      {/* ---------- screens ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="screens-heading">
        <h2 id="screens-heading" className="t-h2 mb-12 text-text">
          {dict.caseStudy.screens}
        </h2>

        <div
          className={cn(
            "grid gap-6",
            project.mobile ? "lg:grid-cols-[1.6fr_0.6fr]" : "sm:grid-cols-2",
          )}
        >
          <ul className={cn("grid gap-6", project.mobile ? "sm:grid-cols-2" : "contents")}>
            {project.gallery.slice(1).map((shot, i) => (
              <Reveal as="li" key={shot.src} delay={i * 70}>
                <Tilt max={4} scale={1.01} depth={5}>
                  <div className="overflow-hidden rounded-xl border border-border bg-surface">
                    <Image
                      src={shot.src}
                      width={shot.width}
                      height={shot.height}
                      alt={shot.alt}
                      loading="lazy"
                      sizes="(max-width: 1024px) 100vw, 50vw"
                      className="w-full object-cover"
                    />
                  </div>
                </Tilt>
              </Reveal>
            ))}
          </ul>

          {project.mobile ? (
            <Reveal delay={120}>
              <p className="t-small mb-3 font-medium uppercase tracking-[0.12em] text-text-muted">
                {dict.caseStudy.onMobile}
              </p>
              <Tilt max={6} scale={1.015} depth={8}>
                <div className="overflow-hidden rounded-[22px] border-4 border-border bg-surface">
                  <Image
                    src={project.mobile.src}
                    width={project.mobile.width}
                    height={project.mobile.height}
                    alt={project.mobile.alt}
                    loading="lazy"
                    sizes="320px"
                    className="w-full object-cover"
                  />
                </div>
              </Tilt>
            </Reveal>
          ) : null}
        </div>
      </Section>

      {/* ---------- next + CTA ---------- */}
      <Section className="border-t border-border pb-24 md:pb-32">
        <div className="grid gap-10 lg:grid-cols-2 lg:gap-16">
          <Reveal className="min-w-0">
            <p className="t-small font-medium uppercase tracking-[0.12em] text-text-muted">
              {dict.caseStudy.nextProject}
            </p>
            <Link
              href={`/${typedLocale}/portfolio/${next.slug}`}
              className="group/next mt-4 flex items-center gap-4 rounded-2xl border border-border bg-surface p-4 transition-colors duration-200 hover:border-accent/35 hover:bg-surface-hover sm:gap-5 sm:p-5"
            >
              <Image
                src={next.preview.src}
                width={next.preview.width}
                height={next.preview.height}
                alt=""
                loading="lazy"
                sizes="160px"
                className="h-16 w-24 shrink-0 rounded-lg object-cover object-top sm:h-20 sm:w-32"
              />
              <span className="min-w-0">
                <span className="block truncate font-[family-name:var(--font-space-grotesk)] text-lg font-medium text-text group-hover/next:text-accent">
                  {next.name}
                </span>
                <span className="t-small block truncate text-text-muted">
                  {next.categoryLabel[typedLocale]}
                </span>
              </span>
              <ArrowUpRight
                aria-hidden="true"
                strokeWidth={1.5}
                className="ml-auto size-5 shrink-0 text-text-muted transition-transform duration-200 group-hover/next:translate-x-0.5 group-hover/next:-translate-y-0.5 motion-reduce:transition-none"
              />
            </Link>
          </Reveal>

          <Reveal delay={80} className="min-w-0">
            <div className="rounded-2xl border border-accent/20 bg-accent-soft p-6 sm:p-8">
              <h2 className="t-h3 text-text">{dict.caseStudy.ctaTitle}</h2>
              <p className="mt-3 text-[15px] text-text-muted">{dict.caseStudy.ctaBody}</p>
              <ContactButtons dict={dict} className="mt-6" />
            </div>
          </Reveal>
        </div>
      </Section>
    </>
  );
}
