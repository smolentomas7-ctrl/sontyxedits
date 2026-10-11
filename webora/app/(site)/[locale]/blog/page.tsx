import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { Container } from "@/components/ui/Container";
import { Section } from "@/components/ui/Section";
import { Card } from "@/components/ui/Card";
import { Reveal } from "@/components/ui/Reveal";
import { ButtonLink } from "@/components/ui/Button";
import { getDictionary, isLocale, type Locale } from "@/content/i18n";
import { sortedPosts } from "@/content/blog/posts";
import { buildAlternates, ogImages } from "@/lib/seo";
import { formatDate } from "@/lib/utils";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const dict = getDictionary(locale);

  return {
    title: dict.blog.metaTitle,
    description: dict.blog.metaDescription,
    alternates: buildAlternates("blog"),
    openGraph: {
      title: dict.blog.metaTitle,
      description: dict.blog.metaDescription,
      type: "website",
      images: ogImages(locale),
    },
  };
}

export default async function BlogIndexPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const typedLocale: Locale = locale;
  const dict = getDictionary(typedLocale);
  const posts = sortedPosts();

  return (
    <>
      <Container>
        <div className="flex flex-col gap-6 py-20 md:py-28">
          <h1 className="t-h1 max-w-[10ch] text-text">{dict.blog.heroTitle}</h1>
          <p className="t-prose text-lg text-text-muted">{dict.blog.heroSubtitle}</p>
        </div>
      </Container>

      <Section className="border-t border-border pt-14 md:pt-20">
        <ul className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {posts.map((post, index) => (
            <Reveal as="li" key={post.slug} delay={index * 60} className="flex">
              <Card as="div" className="group flex w-full flex-col overflow-hidden">
                <Link href={`/${typedLocale}/blog/${post.slug}`} className="flex h-full flex-col">
                  <div className="relative aspect-[16/9] overflow-hidden bg-bg">
                    <Image
                      src={post.cover.src}
                      alt={post.cover.alt}
                      fill
                      sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                      className="object-cover transition-transform duration-300 ease-out group-hover:scale-[1.03]"
                    />
                  </div>

                  <div className="flex flex-1 flex-col gap-3 p-6">
                    <span className="t-small font-medium uppercase tracking-[0.14em] text-accent">
                      {post.category[typedLocale]}
                    </span>
                    <h2 className="font-[family-name:var(--font-space-grotesk)] text-xl font-medium leading-snug text-text">
                      {post.title[typedLocale]}
                    </h2>
                    <p className="t-small flex-1 text-text-muted">{post.excerpt[typedLocale]}</p>
                    <p className="t-small text-text-muted">
                      <time dateTime={post.date}>{formatDate(post.date, typedLocale)}</time>
                      {" · "}
                      {post.readMinutes} {dict.blog.readTime}
                    </p>
                  </div>
                </Link>
              </Card>
            </Reveal>
          ))}
        </ul>

        <div className="mt-16 flex flex-col gap-3 sm:flex-row">
          <ButtonLink href={`/${typedLocale}/contact`}>{dict.common.getQuote}</ButtonLink>
          <ButtonLink href={`/${typedLocale}/services`} variant="secondary">
            {dict.home.servicesLink}
          </ButtonLink>
        </div>
      </Section>
    </>
  );
}
