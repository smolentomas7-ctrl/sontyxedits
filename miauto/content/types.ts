/**
 * One shared shape for both locales.
 *
 * `sk.ts` and `en.ts` are both typed `LocaleContent`, so a string that exists in
 * one language and not the other is a compile error rather than a silent fallback
 * to Slovak at runtime.
 */

export const LOCALES = ["sk", "en"] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = "sk";

export const SERVICE_SLUGS = [
  "diagnostika-vozidiel",
  "cipovanie-ecu",
  "geometria-kolies",
  "pneuservis",
  "elektroinstalacia-vw",
  "vymena-rozvodov",
  "servis-klimatizacie",
] as const;
export type ServiceSlug = (typeof SERVICE_SLUGS)[number];

/** lucide-react icon names, resolved in components/ui/ServiceIcon.tsx. */
export type ServiceIconName =
  | "scan-line" | "cpu" | "crosshair" | "circle-dot" | "cable" | "cog" | "snowflake";

export type Meta = { readonly title: string; readonly description: string };

export type ServiceContent = {
  readonly slug: ServiceSlug;
  readonly name: string;
  /** Heading on the detail page. Slovak appends " — Ružomberok" for local relevance. */
  readonly h1: string;
  readonly icon: ServiceIconName;
  /** Card copy, 12–20 words. */
  readonly cardDescription: string;
  /** Opening paragraph of the detail page, 40–60 words. */
  readonly lead: string;
  /** Two-sentence description used on the services overview rows. */
  readonly overview: string;
  /** Short bullets of what the service covers, for the overview rows. */
  readonly covers: readonly string[];
  /** "Kedy to riešiť" — 3–5 symptoms a driver would actually notice. */
  readonly when: readonly string[];
  /** "Čo robíme" — 3–5 plain steps. */
  readonly what: readonly string[];
  /**
   * Scope that the client has not confirmed. Rendered visibly, brackets and all,
   * so it cannot ship unnoticed. Never replaced with a plausible guess.
   */
  readonly toConfirm: readonly string[];
  /** Standing factual note, e.g. the independent-workshop sentence. */
  readonly note?: string;
  readonly related: readonly [ServiceSlug, ServiceSlug];
  readonly meta: Meta;
};

export type FaqItem = { readonly id: string; readonly q: string; readonly a: string };

export type LocaleContent = {
  readonly locale: Locale;
  readonly htmlLang: string;

  readonly common: {
    readonly skipToContent: string;
    readonly callCta: string;
    readonly callAria: string;
    readonly servicesCta: string;
    readonly contactCta: string;
    readonly navigateCta: string;
    readonly readMore: string;
    readonly backToServices: string;
    readonly home: string;
    /**
     * Templates, not functions. The whole content object is handed from server
     * components to client components, and React cannot serialize a function
     * across that boundary. Placeholders are filled by `fmt()` in lib/format.ts.
     *   openNow   — {time}
     *   closedNow — {day}, {time}
     */
    readonly openNow: string;
    readonly closedNow: string;
    readonly closedToday: string;
    readonly today: string;
    readonly hoursHeading: string;
    readonly addressHeading: string;
    readonly phoneHeading: string;
    readonly days: Readonly<Record<"mon" | "tue" | "wed" | "thu" | "fri" | "sat" | "sun", string>>;
    readonly closedLabel: string;
    readonly menu: string;
    readonly closeMenu: string;
    readonly languageLabel: string;
    readonly switchTo: string;
    readonly copyAddress: string;
    readonly addressCopied: string;
    readonly relatedServices: string;
    readonly toConfirmLabel: string;
    readonly placeholderLabel: string;
  };

  readonly nav: {
    readonly services: string;
    readonly about: string;
    readonly contact: string;
    readonly privacy: string;
  };

  readonly home: {
    readonly meta: Meta;
    readonly heroTitle: string;
    readonly heroTitleSecond: string;
    /** 20–30 words, drawn only from the seven confirmed services. */
    readonly heroLead: string;
    readonly heroImageAlt: string;
    readonly servicesHeading: string;
    readonly servicesLead: string;
    readonly signatureHeading: string;
    readonly signatureLead: string;
    readonly whyHeading: string;
    readonly why: readonly { readonly title: string; readonly body: string }[];
    readonly mapHeading: string;
    readonly mapLead: string;
    readonly mapLoadButton: string;
    readonly mapLoadNote: string;
    readonly finalHeading: string;
    readonly finalLead: string;
    readonly finalFormCta: string;
  };

  readonly servicesPage: {
    readonly meta: Meta;
    readonly h1: string;
    readonly lead: string;
    readonly faqHeading: string;
    readonly ctaHeading: string;
    readonly ctaLead: string;
  };

  readonly services: Readonly<Record<ServiceSlug, ServiceContent>>;

  readonly about: {
    readonly meta: Meta;
    readonly h1: string;
    readonly lead: string;
    readonly whatWeDoHeading: string;
    readonly quietHeading: string;
    readonly quietBody: readonly string[];
    readonly ownerHeading: string;
    readonly ownerRole: string;
    readonly placeholderShop: string;
    readonly placeholderOwner: string;
    readonly factsHeading: string;
    readonly interiorAlt: string;
    readonly detail01Alt: string;
    readonly detail02Alt: string;
  };

  readonly contact: {
    readonly meta: Meta;
    readonly h1: string;
    readonly lead: string;
    readonly mapHeading: string;
    readonly mapTitle: string;
    readonly mapDisclosure: string;
    readonly mapDisclosureLink: string;
    readonly formHeading: string;
    readonly formLead: string;
    readonly emailPendingNote: string;
  };

  readonly form: {
    readonly name: string;
    readonly namePlaceholder: string;
    readonly phone: string;
    readonly phonePlaceholder: string;
    readonly email: string;
    readonly emailOptional: string;
    readonly vehicle: string;
    readonly vehiclePlaceholder: string;
    readonly vehicleHint: string;
    readonly service: string;
    readonly serviceOther: string;
    readonly servicePrompt: string;
    readonly message: string;
    readonly messagePlaceholder: string;
    readonly consent: string;
    readonly consentLink: string;
    readonly submit: string;
    readonly submitting: string;
    readonly disabledReason: string;
    readonly successHeading: string;
    readonly successBody: string;
    readonly errorHeading: string;
    readonly errorBody: string;
    /** Template; placeholder {n}. */
    readonly charactersLeft: string;
    readonly errors: {
      readonly nameRequired: string;
      readonly nameLength: string;
      readonly phoneRequired: string;
      readonly phoneInvalid: string;
      readonly emailInvalid: string;
      readonly messageRequired: string;
      readonly messageLength: string;
      readonly consentRequired: string;
      readonly tooFast: string;
    };
  };

  readonly faq: readonly FaqItem[];

  readonly privacy: {
    readonly meta: Meta;
    readonly h1: string;
    readonly reviewNotice: string;
    readonly updated: string;
    readonly sections: readonly { readonly heading: string; readonly body: readonly string[] }[];
  };

  readonly signature: {
    readonly title: string;
    readonly instructions: string;
    readonly keyboardHint: string;
    readonly svgTitle: string;
    readonly stageLabel: string;
    readonly stages: readonly [string, string, string, string, string];
    readonly codeListLabel: string;
    readonly codeRowLabel: string;
    readonly dashboardLabel: string;
  };

  readonly chat: {
    readonly launcherLabel: string;
    readonly panelTitle: string;
    readonly panelSubtitle: string;
    readonly automatedBadge: string;
    readonly greeting: string;
    readonly inputLabel: string;
    readonly inputPlaceholder: string;
    readonly send: string;
    readonly stop: string;
    readonly close: string;
    readonly sourceLabel: string;
    readonly errorMessage: string;
    readonly turnLimit: string;
    readonly suggestedLabel: string;
    readonly starterChips: readonly string[];
    readonly scriptedNotice: string;
    readonly thinking: string;
    readonly feedbackUp: string;
    readonly feedbackDown: string;
    readonly feedbackThanks: string;
  };

  readonly footer: {
    readonly tagline: string;
    readonly servicesHeading: string;
    readonly contactHeading: string;
    readonly legalHeading: string;
    readonly rights: string;
    readonly icoLabel: string;
  };

  readonly notFound: {
    readonly title: string;
    readonly body: string;
    readonly cta: string;
  };
};
