/**
 * ============================================================
 * THE ONLY SUBMIT PATH IN THE PROJECT
 * ============================================================
 *
 * Every form — the marketing contact form and all seven demo forms — calls
 * submitForm(). Right now it validates, logs to the console, waits 800 ms and
 * returns success. NOTHING IS SENT ANYWHERE. No email leaves the browser and
 * there is no API route.
 *
 * The UI copy is written to match: no form claims an email has been sent.
 *
 * ------------------------------------------------------------
 * TO MAKE THIS SEND REAL EMAILS
 * ------------------------------------------------------------
 *
 * You need a server endpoint, because an email API key must never ship to the
 * browser. Create app/api/contact/route.ts, then replace the simulated block
 * at the bottom of this file with a fetch to it.
 *
 * --- Option A: Resend (https://resend.com) ---
 *
 * 1. npm install resend
 * 2. Put RESEND_API_KEY in .env.local (never commit it).
 * 3. Create app/api/contact/route.ts:
 *
 *    import { Resend } from "resend";
 *    const resend = new Resend(process.env.RESEND_API_KEY);
 *
 *    export async function POST(request: Request) {
 *      const { formName, data } = await request.json();
 *      await resend.emails.send({
 *        from: "Webora <web@your-verified-domain.sk>",
 *        to: "your@email.sk",
 *        replyTo: typeof data.email === "string" ? data.email : undefined,
 *        subject: `New inquiry from the website (${formName})`,
 *        text: Object.entries(data)
 *          .map(([k, v]) => `${k}: ${String(v)}`)
 *          .join("\n"),
 *      });
 *      return Response.json({ ok: true });
 *    }
 *
 * 4. Swap the simulated block below for:
 *
 *    const response = await fetch("/api/contact", {
 *      method: "POST",
 *      headers: { "Content-Type": "application/json" },
 *      body: JSON.stringify({ formName, data }),
 *    });
 *    if (!response.ok) return { ok: false, error: "send_failed" };
 *    return { ok: true };
 *
 * --- Option B: Web3Forms (https://web3forms.com) ---
 *
 * No server needed — the access key is public by design and Web3Forms does
 * the delivery. Simpler, but anyone can read the key from the page source,
 * so turn on their spam protection.
 *
 *    const response = await fetch("https://api.web3forms.com/submit", {
 *      method: "POST",
 *      headers: { "Content-Type": "application/json", Accept: "application/json" },
 *      body: JSON.stringify({
 *        access_key: "YOUR-PUBLIC-ACCESS-KEY",
 *        subject: `New inquiry from the website (${formName})`,
 *        ...data,
 *      }),
 *    });
 *    if (!response.ok) return { ok: false, error: "send_failed" };
 *    return { ok: true };
 *
 * Whichever you choose, also update the success copy in the relevant
 * dictionary so it reflects that a message really was sent.
 */

export type SubmitResult =
  | { ok: true }
  | { ok: false; error: "validation" | "send_failed" };

/** How long the simulated send takes, in milliseconds. */
const SIMULATED_DELAY_MS = 800;

export async function submitForm(
  formName: string,
  data: Record<string, unknown>,
): Promise<SubmitResult> {
  // Guard against an empty payload reaching a future real endpoint.
  if (!formName || typeof data !== "object" || data === null) {
    return { ok: false, error: "validation" };
  }

  if (process.env.NODE_ENV !== "production") {
    // eslint-disable-next-line no-console
    console.info(`[submitForm] "${formName}" — not sent anywhere:`, data);
  }

  // ----- simulated send; replace this block, see the notes above -----
  await new Promise((resolve) => setTimeout(resolve, SIMULATED_DELAY_MS));
  return { ok: true };
  // -------------------------------------------------------------------
}

/* ============================================================
   Shared validators, used by every form in the project
   ============================================================ */

export function isValidEmail(value: string): boolean {
  // Deliberately permissive: catches obvious typos without rejecting
  // legitimate but unusual addresses.
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value.trim());
}

export function isValidPhone(value: string): boolean {
  const trimmed = value.trim();
  if (trimmed === "") return true; // optional field
  const digits = trimmed.replace(/[^\d]/g, "");
  return digits.length >= 9 && /^[\d\s+()/-]+$/.test(trimmed);
}

export function isNonEmpty(value: string): boolean {
  return value.trim().length > 0;
}

export function hasMinLength(value: string, min: number): boolean {
  return value.trim().length >= min;
}
