/**
 * Every form in this project submits through this one function, so the whole
 * site changes mechanism in a single edit.
 *
 * Mechanism: Netlify Forms. Netlify detects the form from the static HTML in
 * public/__forms.html at deploy time, and accepts POSTs to that path.
 *
 * HONESTY: locally, and on any host that is not Netlify, this POST does not
 * reach a form handler. That is NOT caught and dressed up as success — the
 * caller gets `ok: false` and shows the error state with the phone number. A
 * false "sent" message on a form that sent nothing is worse than no form at all.
 *
 * Two failure shapes have to be told apart from success:
 *   - the host rejects the POST (404, 405, 500) — covered by `response.ok`;
 *   - the host just serves __forms.html back, answering 200 with our own
 *     registration page. That is why that page carries a sentinel and why the
 *     body is checked for it. Without the check, a plain static host would
 *     report every enquiry as sent while nothing was ever processed.
 */

export type SubmitResult =
  | { readonly ok: true }
  | { readonly ok: false; readonly reason: "network" | "rejected"; readonly status?: number };

export const NETLIFY_FORM_ENDPOINT = "/__forms.html";

/** Present only in public/__forms.html. Seeing it back means nothing handled the POST. */
const REGISTRATION_SENTINEL = "MIAUTO_FORM_REGISTRATION_PAGE";

export async function submitForm(
  formName: string,
  data: Record<string, string>,
  signal?: AbortSignal,
): Promise<SubmitResult> {
  const payload = new URLSearchParams({ "form-name": formName, ...data });

  try {
    const response = await fetch(NETLIFY_FORM_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: payload.toString(),
      signal,
    });

    if (!response.ok) {
      return { ok: false, reason: "rejected", status: response.status };
    }

    // A 200 carrying our own registration page means the host served the file
    // rather than processing a submission.
    const text = await response.text().catch(() => "");
    if (text.includes(REGISTRATION_SENTINEL)) {
      return { ok: false, reason: "rejected", status: response.status };
    }

    return { ok: true };
  } catch {
    return { ok: false, reason: "network" };
  }
}

/**
 * Loose phone validation. It must accept Slovak formats and international ones
 * without rejecting a valid foreign number, so it checks shape, not country.
 */
export function isPlausiblePhone(value: string): boolean {
  const trimmed = value.trim();
  if (!/^[+0-9\s()./-]+$/.test(trimmed)) return false;
  const digits = trimmed.replace(/\D/g, "");
  return digits.length >= 9 && digits.length <= 15;
}

export function isPlausibleEmail(value: string): boolean {
  const trimmed = value.trim();
  if (trimmed === "") return true; // optional field
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(trimmed);
}

/** Submissions faster than this are treated as automated. No CAPTCHA. */
export const MIN_FILL_MS = 3000;
