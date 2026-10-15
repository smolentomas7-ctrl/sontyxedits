import type { Dictionary } from "./types";

export const en: Dictionary = {
  meta: {
    siteTitle: "Webora — websites for businesses",
    siteDescription:
      "I design and build websites for businesses and sole traders. See one real client project and two demonstrations of what I can build.",
  },

  nav: {
    home: "Home",
    services: "Services",
    portfolio: "Portfolio",
    features: "What a site can do",
    blog: "Blog",
    about: "About",
    contact: "Contact",
    openMenu: "Open menu",
    closeMenu: "Close menu",
    switchLanguage: "Switch language",
    skipToContent: "Skip to content",
    logoLabel: "Webora — back to the home page",
  },

  common: {
    getQuote: "Free consultation",
    seeWork: "See the work",
    viewExample: "View example",
    caseStudy: "Project detail",
    readMore: "More",
    from: "from",
    allRightsReserved: "All rights reserved.",
    privacy: "Privacy policy",
    required: "required",
    optional: "optional",
    close: "Close",
    previous: "Previous",
    next: "Next",
    menu: "Menu",
    backToPortfolio: "Back to portfolio",
    openLiveDemo: "Open live demo",
  },

  home: {
    metaTitle: "Webora — websites for businesses",
    metaDescription:
      "Custom websites for businesses and sole traders. One real client project, two capability demos, and pricing set by actual scope.",
    heroEyebrow: "Web design studio",
    heroTitle: "Websites that bring you",
    heroTitleAccent: "actual customers",
    heroSubtitle:
      "I design and build websites for businesses and sole traders. Not a template with the photos swapped — a site built around what your business needs to achieve.",
    heroPrimary: "Book a consultation",
    heroSecondary: "See the work",
    heroStats: [
      { value: "3", label: "kinds of site I build" },
      { value: "2–3", label: "weeks typical delivery" },
      { value: "100%", label: "code and logins stay yours" },
    ],
    trustTitle: "What every project includes",
    trust: [
      {
        title: "Works on every device",
        body: "I test at real screen widths, from a small phone to a wide monitor. Not just in one browser window.",
      },
      {
        title: "Fast to load",
        body: "Optimised images and no unnecessary code. A slow site loses visitors before it even appears.",
      },
      {
        title: "Ready for search",
        body: "Clean structure, page descriptions, a sitemap and structured data. A foundation you can build on.",
      },
      {
        title: "Handover with training",
        body: "I show you how to change text and images. The domain, hosting and code stay yours, with no lock-in to me.",
      },
    ],
    workEyebrow: "Work",
    workTitle: "Three kinds of site, three examples",
    workSubtitle:
      "One real client project and two demonstrations showing how I handle selling online and presenting photography. You can click through all three.",
    servicesEyebrow: "Services",
    servicesTitle: "What you can come to me with",
    servicesSubtitle:
      "From a one-page presentation to an online shop. We always start with what your business actually needs, not a feature list.",
    servicesLink: "All services",
    processEyebrow: "Process",
    processTitle: "How it works",
    processSubtitle: "Five steps from the first call to a live site.",
    process: [
      {
        title: "Consultation and requirements",
        body: "We go through what you need, who you sell to and what the site has to achieve. No obligation, by phone or in person.",
      },
      {
        title: "Proposed solution",
        body: "I prepare a structure and a visual design for the main pages, together with a quote for that specific scope.",
      },
      {
        title: "Building the site",
        body: "I build the site, add your text and images, and show you progress as it grows.",
      },
      {
        title: "Testing and revisions",
        body: "We go through the site on phones and desktops, fix what needs adjusting, and revise it to your notes.",
      },
      {
        title: "Launch",
        body: "I deploy the site, connect your domain and show you how to run it. I stay available for the first month.",
      },
    ],
    ctaTitle: "Tell me what you need",
    ctaBody:
      "Send a few sentences about your business and what you expect from a website. I'll come back with a proposed approach and a price for that scope.",
    ctaButton: "Send a message",
    ctaSecondary: "See what a site can do",
  },

  services: {
    metaTitle: "Services — Webora",
    metaDescription:
      "Landing page, business website, online shop, redesign and maintenance. What's included, who it suits and how long it takes.",
    heroTitle: "Services",
    heroSubtitle:
      "Five kinds of project. Each one lists what it covers and who it suits. I price by actual scope — there are no fixed packages.",
    whatItIs: "What it is",
    whoItSuits: "Who it suits",
    included: "What it covers",
    timeline: "Typical duration",
    cta: "I'm interested",
    items: [
      {
        slug: "landing",
        name: "One-page website",
        what: "A single page that says everything that matters: what you do, who for, and how to reach you. The visitor scrolls top to bottom and arrives with a reason to get in touch.",
        who: "For tradespeople, small venues and new businesses that need a credible presence, not a large website.",
        includes: [
          "Sections assembled around your needs",
          "Contact form with field validation",
          "Tappable phone number and email",
          "Phone and tablet layouts",
          "Basic search engine optimisation",
          "Deployment and domain setup",
        ],
        timeline: "about a week",
      },
      {
        slug: "business",
        name: "Business website",
        what: "A multi-page site with separate pages for services, references and contact. Room to explain what makes you different and to build traffic from search.",
        who: "For established businesses with several services or locations that want customers to find them through Google.",
        includes: [
          "A standalone page per service",
          "Blog or news section",
          "Photo gallery",
          "Advanced search engine optimisation",
          "Analytics setup",
          "Help with copy",
          "Training on managing content",
        ],
        timeline: "about two to three weeks",
      },
      {
        slug: "eshop",
        name: "Online shop",
        what: "An online shop with a product catalogue, cart and checkout. The scope always depends on what you sell and what it needs to connect to.",
        who: "For businesses selling products that want to sell beyond a physical shop or social media.",
        includes: [
          "Product catalogue with categories and variants",
          "Cart and checkout flow",
          "Prepared for payment gateway integration",
          "Shipping configuration",
          "Admin area and training",
        ],
        timeline: "depends on scope and integrations",
      },
      {
        slug: "redesign",
        name: "Redesign of an existing site",
        what: "I rebuild a site that no longer reflects how the business looks today. I keep what works and fix what is putting visitors off.",
        who: "For businesses whose site was built years ago, doesn't work on phones, or that hesitate to send anyone the link.",
        includes: [
          "Review of the current site",
          "Content migrated to a new structure",
          "New visual design to match your brand",
          "Redirects so you keep your search rankings",
          "Before and after speed comparison",
        ],
        timeline: "about two to four weeks",
      },
      {
        slug: "care",
        name: "Care and maintenance",
        what: "Looking after the site after launch: updates, backups, small text and image changes, and keeping an eye on everything staying up.",
        who: "For businesses that would rather not deal with the technical side and just get in touch when something needs changing.",
        includes: [
          "Regular backups",
          "Security updates",
          "Small content changes",
          "Uptime monitoring",
          "Traffic summary",
        ],
        timeline: "ongoing, by arrangement",
      },
    ],
    alwaysTitle: "What's always part of it",
    alwaysSubtitle:
      "It doesn't matter whether it's one page or an online shop — every project covers this.",
    always: [
      { title: "Responsive design", body: "Tested on phones, tablets and large screens." },
      { title: "Accessibility", body: "Keyboard operation, readable contrast, image descriptions." },
      { title: "Speed", body: "Optimised images and a minimum of unnecessary code." },
      { title: "Basic SEO", body: "Page descriptions, a sitemap and structured data." },
      { title: "Ownership", body: "Domain, hosting and code are yours. No lock-in." },
      { title: "Training", body: "I show you how to run the site yourself." },
    ],
  },

  portfolio: {
    metaTitle: "Portfolio — website examples | Webora",
    metaDescription:
      "Three kinds of site: a real client project for a car service, a demo online shop, and a gallery site for a photographer.",
    heroTitle: "Portfolio",
    heroSubtitle:
      "Three sites, three different jobs. One is a real client project; two are demonstrations I built to show what I can handle.",
    note: "Each project clearly states whether it is real client work or a capability demonstration.",
    typeLabel: "Type of site",
    clientBadge: "Client project",
    demoBadge: "Capability demo",
    demoNote: "Demo sites are built for fictional businesses. They are not real clients.",
  },

  caseStudy: {
    overview: "About the project",
    whatWeBuilt: "What the project covered",
    capabilities: "Solutions used",
    screens: "How it looks",
    onMobile: "On mobile",
    year: "Year",
    type: "Type",
    liveNote:
      "Below are real captures of the delivered site. The photography in them is the client's own.",
    demoNote: "This is a demo site for a fictional business. You can click through all of it.",
    nextProject: "Next project",
    ctaTitle: "Need something similar?",
    ctaBody:
      "Tell me what kind of site you have in mind. I'll come back with an approach and a price for that scope.",
    ctaButton: "Send a message",
  },

  features: {
    metaTitle: "What a website can do — Webora",
    metaDescription:
      "An overview of what I can build into a site — forms, maps, e-commerce, bookings, SEO, multiple languages and integrations.",
    eyebrow: "Capabilities",
    title: "What a website can do",
    subtitle:
      "An overview of what I can build in. It is not a list to pick everything from — during the consultation we work out what actually makes sense for your business.",
    note:
      "Not every feature is automatically part of every site. The final scope always depends on the brief, and some items require third-party services or ongoing costs.",
    ctaTitle: "Not sure which of these you need?",
    ctaBody:
      "Describe what your business does and what the site should handle. I'll propose a scope that makes sense — and say what I'd leave out.",
    ctaButton: "Describe your project",
    groups: [
      {
        id: "dizajn",
        title: "Design and user experience",
        summary: "How the site looks and how it feels to use.",
        items: [
          "Custom design instead of a template",
          "Responsive layouts for phone, tablet and desktop",
          "Custom layout and visual identity",
          "Smooth animations and transitions",
          "Interactive elements and microinteractions",
          "Image galleries and portfolio sections",
          "Project showcases and case studies",
          "Custom buttons, navigation and cards",
          "Light or dark visual themes",
          "Keyboard operation and an accessible interface",
        ],
      },
      {
        id: "obsah",
        title: "Content and business presentation",
        summary: "Pages that explain what you do and why you.",
        items: [
          "Home page and business introduction",
          "About section",
          "Services and their descriptions",
          "Product and service showcases",
          "Contact pages",
          "Frequently asked questions",
          "Testimonials, once real feedback is available",
          "Opening hours",
          "Company and billing details",
          "Standalone landing pages",
          "Calls to action aimed at enquiries",
          "News, articles or a blog",
        ],
      },
      {
        id: "kontakt",
        title: "Contact and lead generation",
        summary: "The routes a visitor uses to reach you.",
        items: [
          "Click-to-call phone links",
          "Click-to-email links",
          "Contact forms",
          "Enquiry forms",
          "Quote request forms",
          "WhatsApp contact button",
          "Links to social media",
          "Appointment request form",
          "Lead-generation landing pages",
          "Confirmation message after submission",
          "Spam protection",
          "Field validation and clear error messages",
        ],
        caveat:
          "Form submission requires connecting an email service or a backend. Until that is configured and tested, a form does not actually send anything.",
      },
      {
        id: "mapy",
        title: "Google Maps and location",
        summary: "So customers can find the premises.",
        items: [
          "Embedded Google Maps",
          "Interactive location map",
          "Address and directions",
          "Button to open directions in Google Maps",
          "Location details and opening hours",
          "Multiple locations on one site",
        ],
        caveat:
          "Depending on the integration, Google Maps may require an API key and a Google Cloud project with billing enabled. Where a plain map link is enough, I don't add the complexity.",
      },
      {
        id: "eshop",
        title: "E-commerce and products",
        summary: "Selling directly from the site.",
        items: [
          "Product catalogue",
          "Product categories",
          "Product detail pages",
          "Product galleries",
          "Search and filtering",
          "Shopping cart",
          "Checkout interface",
          "Payment gateway integration",
          "Order management",
          "Stock and inventory integration",
          "Shipping and delivery options",
          "Discount codes",
          "Customer accounts",
        ],
        caveat:
          "Payments, stock, order management and customer accounts require external services and a backend. The demo shop in the portfolio is a working interface, not a running store.",
      },
      {
        id: "rezervacie",
        title: "Bookings and reservations",
        summary: "When customers book a slot online.",
        items: [
          "Appointment request form",
          "Booking calendar",
          "Available time-slot selection",
          "Booking confirmation",
          "Email notifications",
          "Integration with an external scheduling platform",
          "Booking management",
        ],
        caveat:
          "Automatic confirmation and booking management only work once a real booking system or calendar is connected.",
      },
      {
        id: "galerie",
        title: "Galleries and media",
        summary: "When the images should do the talking.",
        items: [
          "Responsive image galleries",
          "Lightbox image viewing",
          "Category filtering",
          "Before-and-after comparison",
          "Video embedding",
          "Background video",
          "Project portfolios",
          "Interactive image previews",
          "Optimised image delivery",
        ],
      },
      {
        id: "seo",
        title: "SEO and search visibility",
        summary: "So people who don't know you yet can find the site.",
        items: [
          "Search-friendly page structure",
          "Page titles and descriptions",
          "Semantic HTML",
          "Descriptive image alt text",
          "Canonical URLs",
          "XML sitemap",
          "robots.txt",
          "Structured data",
          "Local SEO foundations",
          "Location-specific pages where justified",
          "Open Graph metadata for sharing",
          "Indexing configuration",
          "Core Web Vitals improvements",
          "Help setting up Google Search Console",
        ],
        caveat:
          "Nobody can guarantee a specific search position. I can prepare the technical foundation and content structure — the result also depends on competition and time.",
      },
      {
        id: "rychlost",
        title: "Speed and technical quality",
        summary: "What you don't see but do feel.",
        items: [
          "Responsive layouts",
          "Image optimisation",
          "Lazy loading for off-screen content",
          "Efficient CSS and JavaScript",
          "Minimal unnecessary dependencies",
          "Smooth transitions",
          "Cross-browser testing",
          "Mobile usability",
          "Accessibility improvements",
          "Semantic, maintainable code",
          "Error handling",
          "Deployment support",
        ],
      },
      {
        id: "jazyky",
        title: "Multilingual sites",
        summary: "When you speak to more than one market.",
        items: [
          "Slovak version",
          "Czech version",
          "English version",
          "Further languages as needed",
          "Language switcher",
          "Localised content",
          "Per-language metadata",
          "Multilingual navigation",
        ],
        caveat:
          "You supply the translations, or we agree how to source them. Automatic translation and translation-management systems are not included unless specifically ordered.",
      },
      {
        id: "ai",
        title: "AI and external integrations",
        summary: "Connecting to the tools you already use.",
        items: [
          "AI-assisted features where they make sense",
          "Chat interface",
          "FAQ assistant",
          "AI-assisted handling of enquiries",
          "External API integrations",
          "CRM integration",
          "Analytics integration",
          "Social media integration",
          "Connections to other business tools",
          "Automated workflows",
        ],
        caveat:
          "AI features and integrations run on external services. Expect API keys, usage fees and ongoing maintenance. I never put access keys in code that runs in the browser.",
      },
      {
        id: "sprava",
        title: "Site management and support",
        summary: "What happens after launch.",
        items: [
          "Content editing options",
          "CMS integration",
          "Editing products and images through an admin area",
          "Help with hosting and domains",
          "Deployment",
          "Changes to an existing site",
          "Bug fixes and maintenance",
          "Extending the site with new features",
          "Technical support within an agreed scope",
        ],
        caveat:
          "A CMS, hosting, maintenance and unlimited revisions are not automatically included in the price. We agree those separately.",
      },
    ],
  },

  testimonials: {
    eyebrow: "Testimonials",
    title: "What belongs here",
    subtitle:
      "This section is ready for real client feedback. For now it shows sample text so you can see how it will look.",
    disclaimer:
      "Sample content. The names, companies and text below are not real testimonials — they are placeholders I'll replace with genuine feedback once I have it, with the clients' permission.",
    badge: "Sample text",
    items: [
      {
        name: "Martin Kováč",
        company: "Sample Company Ltd.",
        role: "director",
        text: "Working on the website was clear throughout and the result looks modern. I particularly appreciated the attention to detail and how easy it is to use.",
      },
      {
        name: "Lenka Hrušková",
        company: "Example Venue",
        role: "owner",
        text: "What helped most was knowing in advance what the site would contain and when it would be finished. No surprises on the invoice.",
      },
      {
        name: "Peter Baláž",
        company: "Demo Workshop",
        role: "sole trader",
        text: "I needed people to find me on a phone and call. That's exactly what the site is built around, and enquiries now come in by phone.",
      },
    ],
    prev: "Previous testimonial",
    next: "Next testimonial",
  },

  pricing: {
    eyebrow: "Pricing",
    title: "Priced to your requirements",
    body: [
      "Every project is different. The final price depends on the scope of the site, the features you need, the design and the technical complexity.",
      "Based on your requirements I prepare an individual quote. It states what is included, what is not, and what any extras would cost.",
    ],
    factorsTitle: "What the price depends on",
    factors: [
      {
        title: "Scope",
        body: "How many pages the site needs, and how many of those have their own structure rather than just different text.",
      },
      {
        title: "Features",
        body: "A contact form is one thing; a booking system or a shop wired to payments is another.",
      },
      {
        title: "Design",
        body: "Whether we build on your existing identity or the visual design starts from scratch.",
      },
      {
        title: "Materials",
        body: "Whether you have text and photography ready, or they need writing and sourcing.",
      },
      {
        title: "Languages",
        body: "Each extra language version means a second set of content and testing.",
      },
      {
        title: "Integrations",
        body: "Connections to external systems extend both the build and the testing.",
      },
    ],
    note:
      "The consultation comes with no obligation. We agree the price before work starts, and if the scope changes during the project I say so up front — not on the invoice.",
    ctaPrimary: "Book a free consultation",
    ctaSecondary: "Request an individual quote",
  },

  faq: {
    eyebrow: "Questions",
    title: "Frequently asked questions",
    subtitle: "What people ask me most often before deciding.",
    items: [
      {
        q: "What does a website cost?",
        a: "I don't publish a fixed price list, because project scopes vary so much. The price depends on the number of pages, the features needed, the design, and whether you have text and photography ready. After a short consultation I can give a specific figure for a specific scope — and that figure holds.",
      },
      {
        q: "How long does it take to build a website?",
        a: "A simpler presentation is usually ready in about a week, a multi-page business site in two to three weeks. An online shop depends on the number of products and integrations. Projects most often slip not because of the build, but because of waiting for text and photos.",
      },
      {
        q: "Will the site work on a phone?",
        a: "Yes, and it isn't an add-on — it's the starting point. Most visitors to small business sites arrive on a phone, so I design and test at real screen widths from a small phone to a wide monitor.",
      },
      {
        q: "Can Google Maps be added?",
        a: "Yes. Depending on the integration it may require an API key and a Google Cloud project with billing enabled. If a simple map link or a directions button is enough, I don't add the integration — that saves you both hassle and cost.",
      },
      {
        q: "Can you build an online shop?",
        a: "Yes. A catalogue, cart and checkout flow I can build — you can click through the demo in the portfolio. A payment gateway, stock and order management are a separate matter: they run on external services and need configuring and testing.",
      },
      {
        q: "Can the site be edited later?",
        a: "Yes. Small text and image changes you can make yourself — I'll show you how. For larger changes, get in touch. If you want to manage the content entirely yourself we can connect a CMS; we agree that up front, because it affects the price.",
      },
      {
        q: "Will you help with launching the site and the domain?",
        a: "Yes. I can arrange the domain and hosting, or configure them on an account you already have. You pay the provider directly and I don't add a margin. The logins stay yours.",
      },
      {
        q: "Can more features be added in future?",
        a: "Yes, I build sites so they can be extended. If you already know you'll eventually want bookings or a shop, say so — I'll account for it in the structure and the later extension will be cheaper.",
      },
      {
        q: "Who will own the website?",
        a: "You will. The domain, hosting and source code are yours and you can take them at any time. I don't use closed systems you can't leave, and I don't charge a fee to hand over your logins.",
      },
    ],
  },

  blog: {
    metaTitle: "Blog — Webora",
    metaDescription:
      "Practical articles about building a website for a small business: what to prepare before ordering, and when it's time for a redesign.",
    heroTitle: "Blog",
    heroSubtitle:
      "I write about what clients ask me most often. No marketing talk, with concrete examples.",
    readTime: "min read",
    backToBlog: "Back to blog",
    previousPost: "Previous article",
    nextPost: "Next article",
    writtenBy: "Written by",
    authorBio:
      "Webora, a web design studio. I build websites for businesses and sole traders and write about what I learn doing it.",
    published: "Published",
    relatedTitle: "More articles",
  },

  about: {
    metaTitle: "About — Webora",
    metaDescription:
      "A small web studio. I take on fewer projects at a time, communicate directly, and hand sites over so clients can run them themselves.",
    heroTitle: "About me",
    heroSubtitle:
      "A small studio building websites for businesses and sole traders. No account manager between you and the person actually working on your site.",
    storyTitle: "What I'm like to work with",
    story: [
      "Webora is a small web studio. I don't have hundreds of projects behind me and I'm not going to pretend otherwise — instead of a long reference list, the portfolio has one real client project and two demonstrations you can click through and judge for yourself.",
      "I deliberately take on fewer projects at a time. It means the person who answers your message is the person designing and building your site, and that you know where things stand without having to ask.",
      "Most of my clients are not technical businesses. They are people who are good at their trade and need customers to find them. I try to communicate accordingly — without jargon, and without selling features you'll never use.",
    ],
    approachTitle: "How I work",
    approach: [
      {
        title: "Questions first, design second",
        body: "Before I draw anything I ask what the site has to achieve. Often it turns out a smaller scope than expected is enough.",
      },
      {
        title: "One point of contact",
        body: "You talk directly to the person doing the work. No messages relayed through a third party.",
      },
      {
        title: "Price agreed up front",
        body: "We agree the price before I start. If the scope changes I say so up front, not on the invoice.",
      },
      {
        title: "I hand you the keys",
        body: "Domain, hosting, code and logins are yours. I show you how to run the site, even if you later go elsewhere.",
      },
    ],
    toolsTitle: "What I build with",
    toolsBody:
      "I don't use drag-and-drop site builders. I write sites as code, which means faster loading, better search rankings, and no lock-in to a platform that might raise its prices tomorrow.",
    tools: ["Next.js", "TypeScript", "Tailwind CSS", "React", "Vercel", "Figma", "Git"],
    founderTitle: "Who's behind it",
    founderRole: "Founder",
    founderBody:
      "I design and build websites for businesses. My favourite moment is showing a client the finished site on their own phone and watching them go through it for the first time.",
    ctaTitle: "Shall we get started?",
    ctaBody: "Send me a few sentences about your business and what you expect from a website.",
    ctaButton: "Send a message",
  },

  contact: {
    metaTitle: "Contact — Webora",
    metaDescription:
      "Tell me what you need. I'll reply with a proposed approach and an individual quote.",
    heroTitle: "Let's work out what you need",
    heroSubtitle:
      "Send a few sentences about your business and what you expect from a website. You don't need a finished brief — I just need to know where to start.",
    formTitle: "Project description",
    name: "Full name",
    company: "Company name",
    email: "Email",
    phone: "Phone",
    projectType: "What kind of site",
    projectTypePlaceholder: "Not sure yet",
    projectTypes: [
      "Informational business website",
      "One-page presentation",
      "Online shop",
      "Gallery site or portfolio",
      "Redesign of an existing site",
      "Something else",
    ],
    message: "Short project description",
    messagePlaceholder:
      "What your business does, what the site needs to achieve, and when you'd need it.",
    consent: "I agree to my details being used to reply to this enquiry.",
    submit: "Send enquiry",
    sending: "Sending…",
    successTitle: "The form is filled in correctly",
    successBody:
      "This is how the confirmation would look after sending. An email from me with the next steps would follow straight after.",
    successNote:
      "Important: this form does not send anything yet. Submission needs to be connected to an email service — see the note in lib/forms.ts. Until then, contact me directly using the details listed.",
    sendAnother: "Fill in again",
    errorTitle: "The form could not be processed",
    errorBody: "Please try again, or contact me directly at the email listed.",
    detailsTitle: "Direct contact",
    emailLabel: "Email",
    phoneLabel: "Phone",
    cityLabel: "Based in",
    responseLabel: "Response time",
    followLabel: "Find me on",
    nextStepsTitle: "What happens next",
    nextSteps: [
      "I get in touch and we pin down what the site actually needs.",
      "I prepare a proposed approach and a quote for that specific scope.",
      "Once you approve the quote, we agree a date and start.",
    ],
    errors: {
      nameRequired: "Please enter your name.",
      emailRequired: "Please enter an email so I can reply.",
      emailInvalid: "That doesn't look like a valid email address.",
      messageRequired: "Please write a few sentences about what you need.",
      messageShort: "Could you expand on that a little — at least 20 characters.",
      consentRequired: "I can't reply without your agreement.",
      phoneInvalid: "That phone number looks incomplete.",
    },
  },

  privacy: {
    metaTitle: "Privacy policy — Webora",
    metaDescription:
      "A template privacy document. It must be reviewed by a lawyer before the site goes live.",
    title: "Privacy policy",
    templateWarning:
      "This is a TEMPLATE, not a finished legal document. The text is generic and has not been reviewed by a lawyer. Have a professional check it and fill in your company's details before launching the site. I make no claim that this text satisfies GDPR or any other regulation.",
    lastUpdated: "Last updated",
    sections: [
      {
        title: "Who processes your data",
        body: [
          "This website is operated by [COMPANY NAME], registered at [ADDRESS], company number [COMPANY ID].",
          "For data protection matters contact me at [EMAIL].",
        ],
      },
      {
        title: "What I collect",
        body: [
          "From the contact form: your name, email, and optionally phone, company name and the content of your message.",
          "You send this voluntarily so that I can reply to your enquiry.",
        ],
      },
      {
        title: "What I use it for",
        body: [
          "Solely to reply to you and, where relevant, to prepare a quote.",
          "I don't send marketing emails unless you explicitly ask for them.",
        ],
      },
      {
        title: "How long I keep it",
        body: [
          'Insert a specific retention period here, for example "for the duration of our correspondence and 12 months afterwards".',
        ],
      },
      {
        title: "Who I share it with",
        body: [
          "List the processors actually used — for example the hosting provider, mailbox provider or analytics tool.",
        ],
      },
      {
        title: "Your rights",
        body: [
          "You have the right to know what data I hold about you, to have it corrected or deleted, and to object to its processing.",
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
    tagline: "Websites for businesses and sole traders.",
    navTitle: "Pages",
    contactTitle: "Contact",
    socialTitle: "Follow me",
    placeholderNote: "Contact details are still placeholders. Fill them in in config/site.ts.",
  },

  chat: {
    launcherLabel: "Open chat",
    title: "Automated assistant",
    subtitle: "Answers come from a program, not a person",
    automatedNotice:
      "This is an automated assistant with pre-written answers. It is not a live person. If you need something specific, use the contact form.",
    greeting:
      "Hello. I can answer common questions about pricing, timelines and what I do. What would you like to know?",
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
