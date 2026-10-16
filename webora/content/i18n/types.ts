/**
 * The shape every locale must satisfy. sk.ts and en.ts are both typed against
 * this, so a missing or misspelled key is a compile error rather than an
 * "undefined" rendered on the page.
 */

export type Locale = "sk" | "en";

export const LOCALES: readonly Locale[] = ["sk", "en"] as const;
export const DEFAULT_LOCALE: Locale = "sk";

export function isLocale(value: string): value is Locale {
  return (LOCALES as readonly string[]).includes(value);
}

export type NavDict = {
  home: string;
  services: string;
  portfolio: string;
  features: string;
  blog: string;
  contact: string;
  openMenu: string;
  closeMenu: string;
  switchLanguage: string;
  skipToContent: string;
  logoLabel: string;
};

export type FaqItem = { q: string; a: string };

export type Dictionary = {
  meta: {
    siteTitle: string;
    siteDescription: string;
  };
  nav: NavDict;
  common: {
    getQuote: string;
    seeWork: string;
    viewExample: string;
    caseStudy: string;
    readMore: string;
    from: string;
    allRightsReserved: string;
    privacy: string;
    required: string;
    optional: string;
    close: string;
    previous: string;
    next: string;
    menu: string;
    backToPortfolio: string;
    openLiveDemo: string;
  };

  home: {
    metaTitle: string;
    metaDescription: string;
    heroEyebrow: string;
    heroTitle: string;
    heroTitleAccent: string;
    heroSubtitle: string;
    heroPrimary: string;
    heroSecondary: string;
    heroStats: { value: string; label: string }[];
    trustTitle: string;
    trust: { title: string; body: string }[];
    workEyebrow: string;
    workTitle: string;
    workSubtitle: string;
    servicesEyebrow: string;
    servicesTitle: string;
    servicesSubtitle: string;
    servicesLink: string;
    processEyebrow: string;
    processTitle: string;
    processSubtitle: string;
    process: { title: string; body: string }[];
    ctaTitle: string;
    ctaBody: string;
    ctaButton: string;
    ctaSecondary: string;
  };

  services: {
    metaTitle: string;
    metaDescription: string;
    heroTitle: string;
    heroSubtitle: string;
    whatItIs: string;
    whoItSuits: string;
    included: string;
    timeline: string;
    cta: string;
    items: {
      slug: string;
      name: string;
      what: string;
      who: string;
      includes: string[];
      timeline: string;
    }[];
    alwaysTitle: string;
    alwaysSubtitle: string;
    always: { title: string; body: string }[];
  };

  portfolio: {
    metaTitle: string;
    metaDescription: string;
    heroTitle: string;
    heroSubtitle: string;
    note: string;
    typeLabel: string;
    clientBadge: string;
    demoBadge: string;
    demoNote: string;
  };

  caseStudy: {
    overview: string;
    whatWeBuilt: string;
    capabilities: string;
    screens: string;
    onMobile: string;
    year: string;
    type: string;
    liveNote: string;
    demoNote: string;
    nextProject: string;
    ctaTitle: string;
    ctaBody: string;
    ctaButton: string;
  };

  features: {
    metaTitle: string;
    metaDescription: string;
    eyebrow: string;
    title: string;
    subtitle: string;
    note: string;
    ctaTitle: string;
    ctaBody: string;
    ctaButton: string;
    groups: {
      id: string;
      title: string;
      summary: string;
      items: string[];
      /** Shown as a caveat inside the group where one is warranted. */
      caveat?: string;
    }[];
  };

  testimonials: {
    eyebrow: string;
    title: string;
    subtitle: string;
    /** Accessible name of the star row, e.g. "Hodnotenie 5 z 5". `{n}` is the rating. */
    ratingLabel: string;
    /** Avatar alt text; `{name}` is replaced with the reviewer's name. */
    photoAlt: string;
  };

  pricing: {
    eyebrow: string;
    title: string;
    body: string[];
    factorsTitle: string;
    factors: { title: string; body: string }[];
    note: string;
    ctaPrimary: string;
    ctaSecondary: string;
  };

  faq: {
    eyebrow: string;
    title: string;
    subtitle: string;
    items: FaqItem[];
  };

  blog: {
    metaTitle: string;
    metaDescription: string;
    heroTitle: string;
    heroSubtitle: string;
    readTime: string;
    backToBlog: string;
    previousPost: string;
    nextPost: string;
    writtenBy: string;
    authorBio: string;
    published: string;
    relatedTitle: string;
  };

  contact: {
    metaTitle: string;
    metaDescription: string;
    heroTitle: string;
    heroSubtitle: string;
    /** Heading above the two contact options. */
    title: string;
    body: string;
    emailLabel: string;
    emailCta: string;
    /** Prefilled subject line on the mail draft. */
    mailSubject: string;
    whatsappLabel: string;
    whatsappCta: string;
    whatsappNote: string;
    responseLabel: string;
    nextStepsTitle: string;
    nextSteps: string[];
  };

  privacy: {
    metaTitle: string;
    metaDescription: string;
    title: string;
    templateWarning: string;
    lastUpdated: string;
    sections: { title: string; body: string[] }[];
  };

  footer: {
    tagline: string;
    navTitle: string;
    contactTitle: string;
    placeholderNote: string;
  };

  chat: {
    launcherLabel: string;
    title: string;
    subtitle: string;
    automatedNotice: string;
    greeting: string;
    inputLabel: string;
    inputPlaceholder: string;
    send: string;
    close: string;
    suggestionsLabel: string;
    goToContact: string;
    botName: string;
    youName: string;
  };
};
