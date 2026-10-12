/**
 * Fills {placeholders} in a content template.
 *
 * Content strings are plain data rather than functions, because the whole
 * content object crosses the server/client component boundary and React cannot
 * serialize a function across it.
 */
export function fmt(template: string, vars: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (match, key: string) =>
    key in vars ? String(vars[key]) : match,
  );
}
