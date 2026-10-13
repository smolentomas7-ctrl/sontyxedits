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
  /** Standing factual note, e.g. the independent-workshop sentence. */
  readonly note?: string;
  readonly related: readonly [ServiceSlug, ServiceSlug];
  readonly meta: Meta;
};

export type Beat = { readonly name: string; readonly body: string };

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
     *   breakNow  — {time}
     */
    readonly openNow: string;
    readonly closedNow: string;
    /** Midday break; placeholder {time} is when they open again. */
    readonly breakNow: string;
    readonly breakLabel: string;
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
    readonly ownersHeading: string;
    /**
     * Roles, keyed from config/miauto.ts `owners[].roleKey`. The portraits carry
     * their own name labels, so these are used in the alt text rather than
     * printed under the photographs.
     */
    readonly ownerRoles: Readonly<Record<"owner" | "coOwner", string>>;
    /** What the owners bring to the work. Figures supplied by the owners. */
    readonly experience: {
      readonly heading: string;
      readonly lead: string;
      readonly body: string;
      readonly points: readonly { readonly title: string; readonly body: string }[];
    };
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
    /**
     * The controller block is rendered from config/miauto.ts rather than written
     * out here, so the identification data required by § 3a of the Slovak
     * Commercial Code can never drift from the footer, and each line appears
     * only once it actually holds a value.
     */
    readonly controller: { readonly heading: string; readonly intro: string };
    readonly sections: readonly { readonly heading: string; readonly body: readonly string[] }[];
  };

  /**
   * The Castrol Service partnership, as the owners describe it. Nothing here is
   * a certification claim and the site reproduces no Castrol artwork.
   */
  readonly castrol: {
    readonly eyebrow: string;
    readonly heading: string;
    readonly lead: string;
    readonly body: string;
    /** Four trust points, in the order the icons are assigned in the component. */
    readonly points: readonly [string, string, string, string];
  };

  readonly signature: {
    readonly title: string;
    /** Short visible hint; the full keyboard map lives in `keyboardHint`, sr-only. */
    readonly hint: string;
    readonly keyboardHint: string;
    readonly svgTitle: string;
    readonly stageLabel: string;
    /** Five beats. `name` labels the stage, `body` says why it matters. */
    readonly stages: readonly [Beat, Beat, Beat, Beat, Beat];
    /** Illustrative fault codes shown on the tool's display. */
    readonly codes: readonly { readonly id: string; readonly label: string }[];
    readonly displayTitle: string;
    readonly circuitTitle: string;
    /** Four labelled points on the test circuit. */
    readonly circuitPoints: readonly [string, string, string, string];
    readonly dialRpm: string;
    readonly dialSpeed: string;
    readonly odo: string;
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

  /** Strings for the seven interactive service widgets. */
  readonly widgets: {
    readonly dyno: {
      readonly heading: string; readonly lead: string; readonly disclaimer: string;
      readonly sliderLabel: string; readonly power: string; readonly torque: string;
      readonly stock: string; readonly sceneAlt: string; readonly chartAlt: string;
      readonly legendPower: string; readonly legendTorque: string; readonly legendStock: string;
    };
    readonly diagnostics: {
      readonly heading: string; readonly lead: string; readonly disclaimer: string;
      readonly pick: string; readonly remaining: string; readonly narrowed: string;
      readonly stepLabel: string; readonly reset: string; readonly sceneAlt: string;
      readonly symptoms: readonly {
        readonly id: string; readonly label: string;
        /** Candidate causes, narrowed step by step; the last one is what is left. */
        readonly causes: readonly string[];
        readonly steps: readonly string[];
      }[];
    };
    readonly alignment: {
      readonly heading: string; readonly lead: string; readonly disclaimer: string;
      readonly toe: string; readonly camber: string; readonly wear: string;
      readonly pull: string; readonly ok: string; readonly sceneAlt: string;
      readonly wearInner: string; readonly wearOuter: string; readonly wearEven: string;
      readonly pullLeft: string; readonly pullRight: string; readonly pullNone: string;
      /** Captions under the three panels, plus the note that angles are drawn larger. */
      readonly frontView: string; readonly topView: string;
      readonly section: string; readonly exaggerated: string;
    };
    readonly tyres: {
      readonly heading: string; readonly lead: string; readonly disclaimer: string;
      readonly depth: string; readonly braking: string; readonly legalMin: string;
      readonly versusNew: string; readonly sceneAlt: string; readonly fromSpeed: string;
    };
    readonly electrics: {
      readonly heading: string; readonly lead: string; readonly disclaimer: string;
      readonly instruction: string; readonly measure: string; readonly reset: string;
      readonly found: string; readonly sceneAlt: string; readonly notMeasured: string;
      readonly points: readonly { readonly id: string; readonly label: string }[];
    };
    readonly timing: {
      readonly heading: string; readonly lead: string; readonly disclaimer: string;
      readonly mileage: string; readonly condition: string; readonly interval: string;
      readonly run: string; readonly reset: string; readonly sceneAlt: string;
      readonly states: readonly [string, string, string];
      readonly failure: string; readonly failureBody: string;
    };
    readonly aircon: {
      readonly heading: string; readonly lead: string; readonly disclaimer: string;
      readonly charge: string; readonly ventTemp: string; readonly state: string;
      readonly sceneAlt: string;
      readonly states: readonly [string, string, string];
      /** Compressor, condenser, expansion valve, evaporator — labels on the diagram. */
      readonly parts: readonly [string, string, string, string];
      readonly cabin: string;
    };
  };

  readonly footer: {
    readonly tagline: string;
    readonly servicesHeading: string;
    readonly contactHeading: string;
    readonly legalHeading: string;
    readonly rights: string;
    readonly icoLabel: string;
    readonly dicLabel: string;
    readonly icDphLabel: string;
    readonly registryLabel: string;
  };

  readonly notFound: {
    readonly title: string;
    readonly body: string;
    readonly cta: string;
  };
};
