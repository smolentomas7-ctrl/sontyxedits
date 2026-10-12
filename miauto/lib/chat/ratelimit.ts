/**
 * Two layers: per-IP message rate, and a global daily token ceiling.
 *
 * LIMITATION, stated plainly: this is a module-scope Map. It resets whenever the
 * serverless function cold-starts and is not shared across regions or instances,
 * so a determined caller can get more than the nominal allowance. It stops
 * casual abuse and runaway cost, not a motivated attacker. The upgrade is a
 * durable KV store (Netlify Blobs, Upstash Redis) keyed the same way — see README.
 */

const WINDOW_MS = 10 * 60 * 1000;
const MAX_PER_WINDOW = 20;

type Bucket = { count: number; resetAt: number };
const buckets = new Map<string, Bucket>();

let tokensToday = 0;
let tokenDay = new Date().toISOString().slice(0, 10);

export const DAILY_TOKEN_CAP = Number(process.env.CHAT_DAILY_TOKEN_CAP ?? 300_000);

export function rateLimit(ip: string): { allowed: boolean; retryAfter: number } {
  const now = Date.now();
  const bucket = buckets.get(ip);

  if (!bucket || now > bucket.resetAt) {
    buckets.set(ip, { count: 1, resetAt: now + WINDOW_MS });
    // Opportunistic sweep so the map cannot grow without bound.
    if (buckets.size > 5000) {
      for (const [key, value] of buckets) {
        if (now > value.resetAt) buckets.delete(key);
      }
    }
    return { allowed: true, retryAfter: 0 };
  }

  bucket.count += 1;
  if (bucket.count > MAX_PER_WINDOW) {
    return { allowed: false, retryAfter: Math.ceil((bucket.resetAt - now) / 1000) };
  }
  return { allowed: true, retryAfter: 0 };
}

export function recordTokens(count: number): void {
  const today = new Date().toISOString().slice(0, 10);
  if (today !== tokenDay) {
    tokenDay = today;
    tokensToday = 0;
  }
  tokensToday += count;
}

/** True once the day's ceiling is spent. Everyone drops to the scripted tier. */
export function overBudget(): boolean {
  const today = new Date().toISOString().slice(0, 10);
  if (today !== tokenDay) {
    tokenDay = today;
    tokensToday = 0;
  }
  return tokensToday >= DAILY_TOKEN_CAP;
}

export function tokensUsedToday(): number {
  return tokensToday;
}
