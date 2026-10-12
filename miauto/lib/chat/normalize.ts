/**
 * Slovak visitors type both "čipovanie" and "cipovanie", both "rozvody" and
 * "rozvodi", so every comparison runs over a lowercased, de-accented form.
 */
export function normalize(input: string): string {
  return input
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function tokens(input: string): string[] {
  return normalize(input).split(" ").filter(Boolean);
}
