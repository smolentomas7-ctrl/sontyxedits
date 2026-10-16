import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { Container } from "@/components/ui/Container";
import { Card } from "@/components/ui/Card";
import { ButtonLink } from "@/components/ui/Button";
import { WhatsAppIcon } from "@/components/ui/WhatsAppIcon";
import { getDictionary, isLocale, LOCALES, type Locale } from "@/content/i18n";
import { getPost, sortedPosts, type Block } from "@/content/blog/posts";
import { siteConfig } from "@/config/site";
import { buildAlternates, canonicalUrl } from "@/lib/seo";
import { formatDate } from "@/lib/utils";

export function generateStaticParams() {
  return LOCALES.flatMap((locale) =>
    sortedPosts().map((post) => ({ locale, slug: post.slug })),
  );
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, slug } = await params;
  if (!isLocale(locale)) return {};
  const post = getPost(slug);
  if (!post) return {};

  const title = post.title[locale];
  const description = post.excerpt[locale];

  return {
    title,
    description,
    alternates: buildAlternates(`blog/${slug}`),
    openGraph: {
      title,
      description,
      type: "article",
      publishedTime: post.date,
      url: canonicalUrl(locale, `blog/${slug}`),
      images: [{ url: `${siteConfig.url}${post.cover.src}` }],
    },
    twitter: { card: "summary_large_image", title, description },
  };
}

/** Renders one content block. Text is interpolated, never injected as HTML. */
function renderBlock(block: Block, index: number) {
  switch (block.type) {
    case "h2":
      return <h2 key={index}>{block.text}</h2>;
    case "h3":
      return <h3 key={index}>{block.text}</h3>;
    case "ul":
      return (
        <ul key={index}>
          {block.items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      );
    case "quote":
      return <blockquote key={index}>{block.text}</blockquote>;
    case "p":
    default:
      return <p key={index}>{block.text}</p>;
  }
}

export default async function BlogPostPage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  if (!isLocale(locale)) notFound();
  const typedLocale: Locale = locale;
  const dict = getDictionary(typedLocale);

  const post = getPost(slug);
  if (!post) notFound();

  const all = sortedPosts();
  const index = all.findIndex((p) => p.slug === slug);
  const previous = index > 0 ? all[index - 1] : null;
  const next = index < all.length - 1 ? all[index + 1] : null;

  const articleLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title[typedLocale],
    description: post.excerpt[typedLocale],
    datePublished: post.date,
    dateModified: post.date,
    image: `${siteConfig.url}${post.cover.src}`,
    author: { "@type": "Organization", name: siteConfig.name },
    publisher: { "@type": "Organization", name: siteConfig.name },
    mainEntityOfPage: canonicalUrl(typedLocale, `blog/${slug}`),
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleLd) }}
      />

      <Container>
        <article className="py-16 md:py-24">
          <Link
            href={`/${typedLocale}/blog`}
            className="inline-flex items-center gap-1.5 text-[14px] text-text-muted transition-colors duration-150 hover:text-accent"
          >
            <ArrowLeft aria-hidden="true" strokeWidth={1.5} className="size-4" />
            {dict.blog.backToBlog}
          </Link>

          <header className="mt-8 flex flex-col gap-5">
            <span className="t-small font-medium uppercase tracking-[0.16em] text-accent">
              {post.category[typedLocale]}
            </span>
            <h1 className="t-h1 max-w-[20ch] text-balance text-text">
              {post.title[typedLocale]}
            </h1>
            <p className="t-small text-text-muted">
              {dict.blog.published}{" "}
              <time dateTime={post.date}>{formatDate(post.date, typedLocale)}</time>
              {" · "}
              {post.readMinutes} {dict.blog.readTime}
            </p>
          </header>

          <div className="mt-10 overflow-hidden rounded-2xl border border-border">
            <Image
              src={post.cover.src}
              width={post.cover.width}
              height={post.cover.height}
              alt={post.cover.alt}
              priority
              sizes="(max-width: 1200px) 100vw, 1200px"
              className="w-full object-cover"
            />
          </div>

          <div className="prose-webora mt-12">
            {post.body[typedLocale].map((block, blockIndex) => renderBlock(block, blockIndex))}
          </div>

          <Card interactive={false} className="mt-14 flex flex-col gap-2 p-6">
            <p className="t-small font-medium uppercase tracking-[0.12em] text-text-muted">
              {dict.blog.writtenBy}
            </p>
            <p className="font-display text-lg font-semibold text-text">
              {siteConfig.name}
            </p>
            <p className="t-small t-prose text-text-muted">{dict.blog.authorBio}</p>
            <div className="mt-3 flex flex-wrap gap-3">
              <ButtonLink href={siteConfig.whatsapp.href} external target="_blank" size="sm">
                <WhatsAppIcon className="size-4" />
                {dict.contact.whatsappCta}
              </ButtonLink>
              <ButtonLink href={`/${typedLocale}/portfolio`} size="sm" variant="secondary">
                {dict.common.seeWork}
              </ButtonLink>
            </div>
          </Card>

          <nav
            aria-label={dict.blog.relatedTitle}
            className="mt-10 grid gap-4 border-t border-border pt-10 sm:grid-cols-2"
          >
            {previous ? (
              <Link
                href={`/${typedLocale}/blog/${previous.slug}`}
                className="group flex flex-col gap-1.5 rounded-xl border border-border p-5 transition-colors duration-150 hover:border-accent/30 hover:bg-surface"
              >
                <span className="t-small inline-flex items-center gap-1.5 text-text-muted">
                  <ArrowLeft aria-hidden="true" strokeWidth={1.5} className="size-3.5" />
                  {dict.blog.previousPost}
                </span>
                <span className="font-medium text-text group-hover:text-accent">
                  {previous.title[typedLocale]}
                </span>
              </Link>
            ) : (
              <span />
            )}

            {next ? (
              <Link
                href={`/${typedLocale}/blog/${next.slug}`}
                className="group flex flex-col gap-1.5 rounded-xl border border-border p-5 text-right transition-colors duration-150 hover:border-accent/30 hover:bg-surface sm:items-end"
              >
                <span className="t-small inline-flex items-center gap-1.5 text-text-muted">
                  {dict.blog.nextPost}
                  <ArrowRight aria-hidden="true" strokeWidth={1.5} className="size-3.5" />
                </span>
                <span className="font-medium text-text group-hover:text-accent">
                  {next.title[typedLocale]}
                </span>
              </Link>
            ) : null}
          </nav>
        </article>
      </Container>
    </>
  );
}
