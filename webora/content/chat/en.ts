import type { ChatScript } from "./types";

/**
 * English counterpart of chatSk. Same node ids, same follow-up graph — the
 * widget looks up follow-ups by id, so the two scripts must stay in step.
 *
 * As in Slovak: first-person singular, and no figures. Pricing is quoted per
 * project, so no answer here may imply a fixed rate card.
 */
export const chatEn: ChatScript = {
  initialSuggestions: ["pricing", "delivery", "included", "contact"],

  fallback: {
    id: "fallback",
    answer:
      "I can't answer that one — I only have prepared answers for common questions. Email me at weboraeurope@gmail.com or message me on WhatsApp and I'll reply, usually within 24 hours.",
    followUps: ["contact", "pricing", "delivery"],
    offerContact: true,
  },

  nodes: {
    pricing: {
      id: "pricing",
      label: "What does a website cost?",
      keywords: [
        "price", "pricing", "cost", "costs", "how much", "budget", "expensive",
        "cheap", "quote", "eur", "€", "pay", "invoice", "rate",
      ],
      answer:
        "There's no fixed rate card. Every site has a different scope, different features and different source material, so I price each one to what you actually need. Describe the brief and you get a quote with a fixed price and a date, so you know where you stand before any work starts. What the price depends on is set out in the Pricing section on the home page.",
      followUps: ["included", "delivery", "contact"],
      offerContact: true,
    },

    delivery: {
      id: "delivery",
      label: "How long will it take?",
      keywords: [
        "how long", "when", "timeline", "deadline", "fast", "quick", "weeks",
        "days", "delivery", "turnaround", "ready",
      ],
      answer:
        "A one-page site usually takes about a week, a multi-page business site one to two weeks. An online shop depends on how many products and integrations there are. The date is agreed along with the price. What usually delays a project is waiting for text and photos — if you have those ready, it runs to plan.",
      followUps: ["start", "included", "pricing"],
      offerContact: true,
    },

    included: {
      id: "included",
      label: "What's included?",
      keywords: [
        "included", "include", "what do i get", "contains", "part of",
        "comes with", "covered", "scope",
      ],
      answer:
        "Every project includes a responsive design for phones and desktops, basic search engine optimisation, contact links, deployment to hosting and domain setup. At the end I train you so you can change text and images yourself. The domain, hosting and code all stay yours. Everything that can be added on top is listed under What a site can do.",
      followUps: ["pricing", "contact", "start"],
      offerContact: true,
    },

    start: {
      id: "start",
      label: "How do we start?",
      keywords: [
        "start", "begin", "get started", "first step", "order", "process",
        "how does it work", "next step",
      ],
      answer:
        "You send me an email or a WhatsApp message — a few sentences about your business and what you expect from a site is enough. I reply within 24 hours and we settle what the site actually needs. Then I send a quote with a fixed price and a date.",
      followUps: ["contact", "delivery", "pricing"],
      offerContact: true,
    },

    redesign: {
      id: "redesign",
      label: "Do you redesign old sites?",
      keywords: [
        "redesign", "rebuild", "old site", "existing site", "refresh", "modernise",
        "modernize", "update my website", "improve",
      ],
      answer:
        "Yes. I review the existing site, keep the content and your search rankings, set up redirects and give the site a new look. The price depends on how much content there is and how much of it needs rewriting — I quote it once I've looked at the site. Email me the link and I'll tell you what I'd change.",
      followUps: ["pricing", "delivery", "contact"],
      offerContact: true,
    },

    contact: {
      id: "contact",
      label: "How do I get in touch?",
      keywords: [
        "contact", "email", "e-mail", "mail", "whatsapp", "reach", "get in touch",
        "phone", "number", "call", "message you", "form",
      ],
      answer:
        "Two ways: by email at weboraeurope@gmail.com, or on WhatsApp at +421 918 757 493. There is deliberately no form on this site — both routes reach me directly and I reply faster. A few sentences about what your business does and what kind of site you need is enough.",
      followUps: ["start", "pricing", "delivery"],
      offerContact: true,
    },

    ownership: {
      id: "ownership",
      label: "Who owns the website?",
      keywords: [
        "own", "owns", "ownership", "belong", "access", "source code", "lock-in",
        "lock in", "take it with me",
      ],
      answer:
        "You do. The domain, hosting and source code are yours and you can take them with you at any time. I don't use closed systems and I don't charge a fee to hand over your logins. I don't offer ongoing website management, precisely so you aren't tied to me.",
      followUps: ["included", "contact"],
      offerContact: false,
    },
  },
};
