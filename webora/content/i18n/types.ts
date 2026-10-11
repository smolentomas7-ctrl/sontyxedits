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
  pricing: string;
  blog: string;
  about: string;
  contact: string;
  openMenu: string;
  closeMenu: string;
  switchLanguage: string;
  skipToContent: string;
};

export type Dictionary = {
  meta: {
    siteTitle: string;
    siteDescription: string;
  };
  nav: NavDict;
  common: {
    getQuote: string;
    seeDemos: string;
    openDemo: string;
    readMore: string;
    backToTop: string;
    from: string;
    allRightsReserved: string;
    legalNotice: string;
    privacy: string;
    loading: string;
    required: string;
    optional: string;
    close: string;
    previous: string;
    next: string;
    menu: string;
  };
  home: {
    metaTitle: string;
    metaDescription: string;
    heroEyebrow: string;
    heroTitle: string;
    heroSubtitle: string;
    trustTitle: string;
    trust: { title: string; body: string }[];
    demosEyebrow: string;
    demosTitle: string;
    demosSubtitle: string;
    servicesEyebrow: string;
    servicesTitle: string;
    servicesSubtitle: string;
    servicesLink: string;
    processEyebrow: string;
    processTitle: string;
    process: { title: string; body: string }[];
    pricingEyebrow: string;
    pricingTitle: string;
    pricingSubtitle: string;
    pricingLink: string;
    ctaTitle: string;
    ctaBody: string;
    ctaButton: string;
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
    priceFrom: string;
    cta: string;
    items: {
      slug: string;
      name: string;
      what: string;
      who: string;
      includes: string[];
      timeline: string;
      price: string;
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
    filterLabel: string;
    filters: { id: string; label: string }[];
    emptyTitle: string;
    emptyBody: string;
    clearFilter: string;
    enlarge: string;
    lightboxLabel: string;
    counter: string;
    note: string;
  };
  pricing: {
    metaTitle: string;
    metaDescription: string;
    heroTitle: string;
    heroSubtitle: string;
    popular: string;
    choosePackage: string;
    packages: {
      id: string;
      name: string;
      price: string;
      summary: string;
      features: string[];
      delivery: string;
    }[];
    calc: {
      title: string;
      subtitle: string;
      siteType: string;
      siteTypes: { id: string; label: string; hint: string }[];
      pages: string;
      pagesHint: string;
      languages: string;
      languagesHint: string;
      addons: string;
      addonLabels: Record<string, string>;
      estimate: string;
      breakdown: string;
      base: string;
      extraPages: string;
      extraLanguages: string;
      disclaimer: string;
      sendCta: string;
      decrease: string;
      increase: string;
    };
    faqTitle: string;
    faq: { q: string; a: string }[];
    ctaTitle: string;
    ctaBody: string;
    ctaButton: string;
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
  about: {
    metaTitle: string;
    metaDescription: string;
    heroTitle: string;
    heroSubtitle: string;
    storyTitle: string;
    story: string[];
    approachTitle: string;
    approach: { title: string; body: string }[];
    toolsTitle: string;
    toolsBody: string;
    tools: string[];
    founderTitle: string;
    founderRole: string;
    founderBody: string;
    ctaTitle: string;
    ctaBody: string;
    ctaButton: string;
  };
  contact: {
    metaTitle: string;
    metaDescription: string;
    heroTitle: string;
    heroSubtitle: string;
    formTitle: string;
    name: string;
    email: string;
    phone: string;
    company: string;
    packageLabel: string;
    packagePlaceholder: string;
    budget: string;
    budgetPlaceholder: string;
    budgets: string[];
    message: string;
    messagePlaceholder: string;
    consent: string;
    submit: string;
    sending: string;
    successTitle: string;
    successBody: string;
    sendAnother: string;
    errorTitle: string;
    errorBody: string;
    detailsTitle: string;
    emailLabel: string;
    phoneLabel: string;
    cityLabel: string;
    responseLabel: string;
    followLabel: string;
    faqTitle: string;
    faq: { q: string; a: string }[];
    errors: {
      nameRequired: string;
      emailRequired: string;
      emailInvalid: string;
      messageRequired: string;
      messageShort: string;
      consentRequired: string;
      phoneInvalid: string;
    };
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
    socialTitle: string;
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
