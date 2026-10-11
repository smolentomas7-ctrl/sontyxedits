import type { Dictionary } from "./types";

export const en: Dictionary = {
  meta: {
    siteTitle: "Webora — websites for small businesses",
    siteDescription:
      "We design and build fast, modern websites for small and medium businesses. Browse seven live demo sites you can click through yourself.",
  },

  nav: {
    home: "Home",
    services: "Services",
    portfolio: "Portfolio",
    pricing: "Pricing",
    blog: "Blog",
    about: "About",
    contact: "Contact",
    openMenu: "Open menu",
    closeMenu: "Close menu",
    switchLanguage: "Switch language",
    skipToContent: "Skip to content",
  },

  common: {
    getQuote: "Get a quote",
    seeDemos: "See live demos",
    openDemo: "Open live demo",
    readMore: "Read more",
    backToTop: "Back to top",
    from: "from",
    allRightsReserved: "All rights reserved.",
    legalNotice: "Legal",
    privacy: "Privacy policy",
    loading: "Loading…",
    required: "required",
    optional: "optional",
    close: "Close",
    previous: "Previous",
    next: "Next",
    menu: "Menu",
  },

  home: {
    metaTitle: "Webora — websites for small businesses",
    metaDescription:
      "Fast, modern websites for small and medium businesses. Seven live demos you can click through, clear pricing, and handover with training.",
    heroEyebrow: "Web design studio",
    heroTitle: "Websites that actually bring your business customers",
    heroSubtitle:
      "We are a small web studio. We build fast, clear websites for restaurants, shops, tradespeople and professionals — and hand them over so you can run them yourself.",
    trustTitle: "What every project includes",
    trust: [
      {
        title: "Works on every device",
        body: "Phone, tablet, laptop. We test at real widths, not just in a desktop browser window.",
      },
      {
        title: "Fast to load",
        body: "Optimised images and no unnecessary code. A faster site means fewer visitors giving up before it appears.",
      },
      {
        title: "Ready for search",
        body: "Clean structure, page descriptions, a sitemap and structured data. A foundation you can build on.",
      },
      {
        title: "Handover with training",
        body: "We show you how to change text and images. The site stays yours, with no lock-in to us.",
      },
    ],
    demosEyebrow: "Live demos",
    demosTitle: "Seven websites you can click through",
    demosSubtitle:
      "Instead of pictures in a portfolio, we built complete working websites for fictional businesses. Each has its own design, its own navigation, working forms and a working cart. Open any of them and try it.",
    servicesEyebrow: "Services",
    servicesTitle: "What we can build for you",
    servicesSubtitle:
      "From a one-page site to an online shop. We always start with what your business actually needs.",
    servicesLink: "All services",
    processEyebrow: "Process",
    processTitle: "How it works",
    process: [
      {
        title: "Consultation",
        body: "We go through what you need, who you sell to and what the site has to achieve. No obligation, by call or in person.",
      },
      {
        title: "Design",
        body: "We prepare a visual design of the main pages. You comment, we adjust, until you are happy with it.",
      },
      {
        title: "Build",
        body: "We build the site, add your text and images, and test it on phones as well as desktops.",
      },
      {
        title: "Launch and handover",
        body: "We deploy the site, connect your domain and show you how to run it. We stay available for the first month.",
      },
    ],
    pricingEyebrow: "Pricing",
    pricingTitle: "Clear prices, no surprises",
    pricingSubtitle:
      "Indicative prices are below. We confirm the exact figure after a consultation, once we know the scope.",
    pricingLink: "Full pricing and calculator",
    ctaTitle: "Tell us what you need",
    ctaBody:
      "Send us a few sentences about your business. We will reply with what would make sense and roughly what it would cost.",
    ctaButton: "Get in touch",
  },

  services: {
    metaTitle: "Services — Webora",
    metaDescription:
      "Landing page, business website, online shop, redesign and maintenance. What is included, who it suits, how long it takes and what it costs.",
    heroTitle: "Services",
    heroSubtitle:
      "Five kinds of project. Each has a clear scope, timeline and indicative price — so you know what you are getting into before the first meeting.",
    whatItIs: "What it is",
    whoItSuits: "Who it suits",
    included: "What's included",
    timeline: "Timeline",
    priceFrom: "Price from",
    cta: "I'm interested",
    items: [
      {
        slug: "landing",
        name: "Landing page",
        what: "One page that says everything that matters: what you do, who for, what it costs and how to reach you. The visitor scrolls top to bottom and arrives with a reason to write.",
        who: "For tradespeople, small venues and new businesses that need a credible presence online, not a large website.",
        includes: [
          "Up to 5 sections tailored to you",
          "Contact form with validation",
          "Phone and tablet layouts",
          "Basic search engine optimisation",
          "Google Maps and social links",
          "Deployment and domain setup",
        ],
        timeline: "7 days",
        price: "€490",
      },
      {
        slug: "business",
        name: "Business website",
        what: "A multi-page site with separate pages for services, references, a blog and contact. Room to explain what makes you different and to build traffic from search.",
        who: "For established businesses with several services or locations that want customers to find them through Google.",
        includes: [
          "Up to 8 pages",
          "Blog or news section",
          "Photo gallery",
          "Advanced search engine optimisation",
          "Analytics setup",
          "Help with copy",
          "Training on managing content",
        ],
        timeline: "2–3 weeks",
        price: "€990",
      },
      {
        slug: "eshop",
        name: "Online shop",
        what: "An online shop with a product catalogue, cart, shipping and a payment gateway. Including an admin area where you add products and manage orders.",
        who: "For businesses selling physical products that want to sell beyond a physical shop or an Instagram account.",
        includes: [
          "Product catalogue with variants",
          "Cart and checkout",
          "Payment gateway integration",
          "Shipping configuration",
          "Admin area and training",
          "Accounting integration by arrangement",
        ],
        timeline: "depends on scope",
        price: "custom quote",
      },
      {
        slug: "redesign",
        name: "Redesign",
        what: "We rebuild an existing site that no longer reflects how the business looks today. We keep what works and fix what is putting visitors off.",
        who: "For businesses whose site was built years ago, does not work on phones, or that hesitate to send anyone the link.",
        includes: [
          "Review of the current site",
          "Content migrated to a new structure",
          "New visual design to match your brand",
          "Redirects so you keep your search rankings",
          "Before and after speed comparison",
        ],
        timeline: "2–4 weeks",
        price: "€690",
      },
      {
        slug: "care",
        name: "Care and maintenance",
        what: "Monthly care for your site: updates, backups, small text and image changes, and keeping an eye on everything staying up.",
        who: "For businesses that would rather not deal with the technical side and just want to call when something needs changing.",
        includes: [
          "Regular backups",
          "Security updates",
          "Small content changes",
          "Uptime monitoring",
          "Monthly traffic summary",
        ],
        timeline: "ongoing",
        price: "€39 / month",
      },
    ],
    alwaysTitle: "What's always included",
    alwaysSubtitle:
      "It does not matter whether you order a one-page site or an online shop — you always get this.",
    always: [
      { title: "Responsive design", body: "Tested on phones, tablets and large screens." },
      { title: "Accessibility", body: "Keyboard operation, readable contrast, image descriptions." },
      { title: "Speed", body: "Optimised images and a minimum of unnecessary code." },
      { title: "Basic SEO", body: "Page descriptions, a sitemap and structured data." },
      { title: "Ownership", body: "Domain, hosting and code are yours. No lock-in." },
      { title: "Training", body: "We show you how to run the site yourself." },
    ],
  },

  portfolio: {
    metaTitle: "Portfolio — live demo websites | Webora",
    metaDescription:
      "Seven complete websites for fictional businesses: a bistro, an online shop, a fitness studio, a builder, a law firm, a photographer and an estate agency.",
    heroTitle: "Portfolio",
    heroSubtitle:
      "Instead of screenshots, we built seven working websites. Each has its own design and its own personality. Open them and try them — the forms, filters and cart all really work.",
    filterLabel: "Filter by industry",
    filters: [
      { id: "all", label: "All" },
      { id: "hospitality", label: "Hospitality" },
      { id: "ecommerce", label: "E-commerce" },
      { id: "services", label: "Services" },
      { id: "professional", label: "Professional" },
      { id: "creative", label: "Creative" },
      { id: "realestate", label: "Real estate" },
    ],
    emptyTitle: "Nothing here for that filter yet",
    emptyBody: "Try another industry, or show all the demos.",
    clearFilter: "Show all",
    enlarge: "Enlarge preview",
    lightboxLabel: "Project preview",
    counter: "of",
    note: "Every business in these demos is fictional. They are not real clients and the content exists only to demonstrate the design.",
  },

  pricing: {
    metaTitle: "Pricing and calculator — Webora",
    metaDescription:
      "Three packages from €490, an interactive price calculator, and answers to the eight questions we get asked most about cost, timing and ownership.",
    heroTitle: "Pricing",
    heroSubtitle:
      "Indicative prices so you know what to expect. We confirm the exact figure after a short consultation — that is when we know the scope instead of guessing.",
    popular: "Most popular",
    choosePackage: "Choose package",
    packages: [
      {
        id: "starter",
        name: "Starter",
        price: "From €490",
        summary: "One page that says everything that matters.",
        features: [
          "One-page website",
          "Up to 5 sections",
          "Contact form",
          "Mobile layouts",
          "Basic SEO",
        ],
        delivery: "Delivered in 7 days",
      },
      {
        id: "business",
        name: "Business",
        price: "From €990",
        summary: "A multi-page site with a blog and room to grow.",
        features: [
          "Up to 8 pages",
          "Blog",
          "Photo gallery",
          "Advanced SEO",
          "Analytics setup",
          "Help with copy",
        ],
        delivery: "Delivered in 2–3 weeks",
      },
      {
        id: "eshop",
        name: "Online shop",
        price: "Custom quote",
        summary: "An online shop built around your product range.",
        features: [
          "Product catalogue",
          "Cart and orders",
          "Payment gateway",
          "Admin area",
          "Training",
        ],
        delivery: "Timeline depends on scope",
      },
    ],
    calc: {
      title: "Price calculator",
      subtitle:
        "Set up what you need and see an indicative price range straight away. The calculation runs entirely in your browser.",
      siteType: "Type of site",
      siteTypes: [
        { id: "landing", label: "Landing page", hint: "One page, everything on it" },
        { id: "business", label: "Business site", hint: "Several pages and subpages" },
        { id: "eshop", label: "Online shop", hint: "Selling products online" },
      ],
      pages: "Number of pages",
      pagesHint: "How many separate pages the site needs.",
      languages: "Number of languages",
      languagesHint: "Each extra language means translation and a second version of the content.",
      addons: "Add-ons",
      addonLabels: {
        blog: "Blog",
        booking: "Booking system",
        ecommerce: "Selling products",
        copywriting: "Copywriting",
        logo: "Logo design",
        photography: "Photography",
        care: "Monthly care plan",
      },
      estimate: "Estimated price",
      breakdown: "What makes up the price",
      base: "Base",
      extraPages: "Extra pages",
      extraLanguages: "Extra languages",
      disclaimer:
        "This is a non-binding estimate, not a quote. We confirm the final price after a consultation, once we know the scope and what materials you have.",
      sendCta: "Send this estimate as an inquiry",
      decrease: "Decrease",
      increase: "Increase",
    },
    faqTitle: "Frequently asked questions",
    faq: [
      {
        q: "How long until the site is finished?",
        a: "A one-page site takes about a week, a business site two to three weeks. An online shop depends on how many products and integrations there are. What usually delays a project is not the building but waiting for text and photos — if you have those ready, it moves fast.",
      },
      {
        q: "What do you need from us to start?",
        a: "At a minimum: what you do, who you sell to and how people should reach you. A logo, photos and existing copy all help. None of it is a precondition — if you do not have them, we can help with copy and photography.",
      },
      {
        q: "Who writes the text for the site?",
        a: "You can, or we can. Most clients send a rough description of what they do and we rewrite it so it reads well and makes sense to search engines. Copywriting for a whole site is a separate line in the calculator.",
      },
      {
        q: "Who will own the site?",
        a: "You will. The domain, the hosting and the code are yours and you can take them at any time. We do not use closed systems you cannot leave, and we do not charge a fee to release your access.",
      },
      {
        q: "Do you handle the domain and hosting?",
        a: "Yes, we can arrange and manage both. A domain costs roughly €15 a year, hosting for a typical business site €40 to €120 a year. You pay the provider directly; we do not add a margin.",
      },
      {
        q: "What if I want to change something later?",
        a: "Small text and image changes you can make yourself — we show you how. Larger changes we do at an hourly rate or as part of a monthly care plan. You are not obliged to stay with us.",
      },
      {
        q: "Do you work with clients outside Slovakia?",
        a: "Yes. We work in Slovak, Czech and English and can build a multilingual site. We invoice in euros and meet online.",
      },
      {
        q: "What happens after launch?",
        a: "For the first month we fix anything that does not work the way we agreed, at no charge. After that you can take a monthly care plan, or simply get in touch when you need something.",
      },
    ],
    ctaTitle: "Not sure which package?",
    ctaBody:
      "Tell us what you need. We will reply with a recommendation and an indicative price — even if that means telling you a smaller package is enough.",
    ctaButton: "Get in touch",
  },

  blog: {
    metaTitle: "Blog — Webora",
    metaDescription:
      "Practical articles about building a website for a small business: what a site should cost, what to prepare before ordering, and when it is time for a redesign.",
    heroTitle: "Blog",
    heroSubtitle:
      "We write about what clients ask us most often. No marketing talk, with real numbers and examples.",
    readTime: "min read",
    backToBlog: "Back to blog",
    previousPost: "Previous article",
    nextPost: "Next article",
    writtenBy: "Written by",
    authorBio:
      "Webora, a web design studio. We build websites for small and medium businesses and write about what we learn doing it.",
    published: "Published",
    relatedTitle: "More articles",
  },

  about: {
    metaTitle: "About — Webora",
    metaDescription:
      "We are a small web studio. We take on fewer projects at a time, communicate directly, and hand sites over so clients can run them themselves.",
    heroTitle: "About us",
    heroSubtitle:
      "A small studio building websites for small businesses. No account manager between you and the person actually working on your site.",
    storyTitle: "What we are like",
    story: [
      "Webora is a young web studio. We do not have hundreds of projects behind us and we are not going to pretend otherwise — instead of references, we built seven complete demo websites you can click through and judge for yourself.",
      "We deliberately take on fewer projects at a time. It means the person who answers your message is the person designing and building your site, and that you know where things stand without having to ask.",
      "Most of our clients are not technical businesses. They are people who are good at their trade and need customers to find them. We try to communicate accordingly — without jargon, and without selling features you will never use.",
    ],
    approachTitle: "How we work",
    approach: [
      {
        title: "Questions first, design second",
        body: "Before we draw anything we ask what the site has to achieve. Often it turns out a smaller scope than expected is enough.",
      },
      {
        title: "One point of contact",
        body: "You talk directly to the person doing the work. No messages relayed through a third party.",
      },
      {
        title: "Fixed price",
        body: "We agree the price before we start. If the scope changes we say so up front, not on the invoice.",
      },
      {
        title: "We hand you the keys",
        body: "Domain, hosting, code and logins are yours. We show you how to run the site, even if you later go elsewhere.",
      },
    ],
    toolsTitle: "What we build with",
    toolsBody:
      "We do not use drag-and-drop site builders. We write sites as code, which means faster loading, better search rankings, and no lock-in to a platform that might raise its prices tomorrow.",
    tools: [
      "Next.js",
      "TypeScript",
      "Tailwind CSS",
      "React",
      "Vercel",
      "Figma",
      "Google Analytics",
      "Git",
    ],
    founderTitle: "Who is behind it",
    founderRole: "Founder",
    founderBody:
      "I design and build websites for small businesses. My favourite moment is showing a client the finished site on their own phone and watching them go through it for the first time.",
    ctaTitle: "Shall we get started?",
    ctaBody:
      "Send us a few sentences about your business and what you expect from a website. We will come back with a proposal.",
    ctaButton: "Get in touch",
  },

  contact: {
    metaTitle: "Contact — Webora",
    metaDescription:
      "Tell us what you need. We reply within 24 hours on business days with a suggested approach and an indicative price.",
    heroTitle: "Contact",
    heroSubtitle:
      "Send us a few sentences about your business and what you expect from a website. You do not need a finished brief — we just need to know where to start.",
    formTitle: "Send us a message",
    name: "Full name",
    email: "Email",
    phone: "Phone",
    company: "Company",
    packageLabel: "Package you're interested in",
    packagePlaceholder: "Not sure yet",
    budget: "Rough budget",
    budgetPlaceholder: "Prefer not to say",
    budgets: ["under €500", "€500 – €1,000", "€1,000 – €2,500", "€2,500 – €5,000", "over €5,000"],
    message: "Message",
    messagePlaceholder:
      "What your business does, what the site needs to achieve, and when you would need it.",
    consent:
      "I agree to my details being used to reply to this inquiry.",
    submit: "Send inquiry",
    sending: "Sending…",
    successTitle: "Thanks, we have your inquiry",
    successBody:
      "We will reply within 24 hours on business days. If it somehow takes longer, do give us a call.",
    sendAnother: "Send another inquiry",
    errorTitle: "Could not send",
    errorBody:
      "Something went wrong. Please try again, or email us directly.",
    detailsTitle: "Contact details",
    emailLabel: "Email",
    phoneLabel: "Phone",
    cityLabel: "Based in",
    responseLabel: "Response time",
    followLabel: "Find us on",
    faqTitle: "Before you write",
    faq: [
      {
        q: "Do I need text and photos ready?",
        a: "No. It is enough to know what your business does. We can help with both copy and photography.",
      },
      {
        q: "What will it cost?",
        a: "A one-page site from €490, a business site from €990. We confirm the exact price after a consultation.",
      },
      {
        q: "Is the consultation charged?",
        a: "No. The first call and the quote are free and come with no obligation.",
      },
    ],
    errors: {
      nameRequired: "Please enter your name.",
      emailRequired: "Please enter an email so we can reply.",
      emailInvalid: "That does not look like a valid email address.",
      messageRequired: "Please write a few sentences about what you need.",
      messageShort: "Could you expand on that a little — at least 20 characters.",
      consentRequired: "We cannot reply without your agreement.",
      phoneInvalid: "That phone number looks incomplete.",
    },
  },

  privacy: {
    metaTitle: "Privacy policy — Webora",
    metaDescription:
      "A template privacy document. It must be reviewed by a lawyer before the site goes live.",
    title: "Privacy policy",
    templateWarning:
      "This is a TEMPLATE, not a finished legal document. The text is generic and has not been reviewed by a lawyer. Have a professional check it and fill in your company's details before launching the site. We make no claim that this text satisfies GDPR or any other regulation.",
    lastUpdated: "Last updated",
    sections: [
      {
        title: "Who processes your data",
        body: [
          "This website is operated by [COMPANY NAME], registered at [ADDRESS], company number [COMPANY ID].",
          "For data protection matters contact us at [EMAIL].",
        ],
      },
      {
        title: "What we collect",
        body: [
          "From the contact form: your name, email, and optionally phone, company name and the content of your message.",
          "You send us this voluntarily so that we can reply to your inquiry.",
        ],
      },
      {
        title: "What we use it for",
        body: [
          "Solely to reply to you and, where relevant, to prepare a quote.",
          "We do not send marketing emails unless you explicitly ask for them.",
        ],
      },
      {
        title: "How long we keep it",
        body: [
          "Insert a specific retention period here, for example \"for the duration of our correspondence and 12 months afterwards\".",
        ],
      },
      {
        title: "Who we share it with",
        body: [
          "List the processors you actually use — for example your hosting provider, mailbox provider or analytics tool.",
        ],
      },
      {
        title: "Your rights",
        body: [
          "You have the right to know what data we hold about you, to have it corrected or deleted, and to object to its processing.",
          "Set out the exact scope of those rights according to the regulations that apply to you.",
        ],
      },
      {
        title: "Cookies",
        body: [
          "State whether the site uses cookies, which ones and what for. If you use analytics or advertising tools, they belong here.",
        ],
      },
    ],
  },

  footer: {
    tagline: "Websites for small and medium businesses.",
    navTitle: "Pages",
    contactTitle: "Contact",
    socialTitle: "Follow us",
    placeholderNote:
      "Contact details are still placeholders. Fill them in in config/site.ts.",
  },

  chat: {
    launcherLabel: "Open chat",
    title: "Automated assistant",
    subtitle: "Answers come from a program, not a person",
    automatedNotice:
      "This is an automated assistant with pre-written answers. It is not a live person. If you need something specific, use the contact form.",
    greeting:
      "Hello. I can answer common questions about pricing, timelines and what we do. What would you like to know?",
    inputLabel: "Your question",
    inputPlaceholder: "Type a question…",
    send: "Send",
    close: "Close chat",
    suggestionsLabel: "Suggested questions",
    goToContact: "Go to the contact form",
    botName: "Assistant",
    youName: "You",
  },
};
