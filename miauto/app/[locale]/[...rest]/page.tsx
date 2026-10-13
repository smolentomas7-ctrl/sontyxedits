import { notFound } from "next/navigation";

/**
 * Anything under a locale that is not one of the twelve routes.
 *
 * Without this, an unmatched URL falls through to Next's own built-in 404 page,
 * which has no layout, no `<html lang>` and no Slovak. Calling `notFound()` here
 * sends the right status code and renders `app/[locale]/not-found.tsx` inside
 * the locale layout instead.
 *
 * `build:static` moves this route aside for the duration of the export, the way
 * it moves `app/api` aside: without a server there is nothing to render it with,
 * and Netlify serves `404.html` for the same URLs instead.
 */
export const dynamicParams = true;

export function generateStaticParams(): { rest: string[] }[] {
  return [];
}

export default function CatchAll(): never {
  notFound();
}
