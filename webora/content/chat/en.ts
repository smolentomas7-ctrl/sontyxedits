import type { ChatScript } from "./types";

/**
 * English counterpart of chatSk. Same node ids, same follow-up graph — the
 * widget looks up follow-ups by id, so the two scripts must stay in step.
 *
 * As in Slovak: first-person singular, and no figures. Pricing is quoted per
 * project, so no answer here may imply a fixed rate card.
 */
export const chatEn: ChatScript = {
  initialSuggestions: ["pricing", "delivery", "included", "start"],

  fallback: {
    id: "fallback",
    answer:
      "I can't answer that one — I only have prepared answers for common questions. Send me a message through the contact form and I'll reply, usually within 24 hours.",
    followUps: ["pricing", "delivery", "included"],
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
        "There's no fixed rate card. Every site has a different scope, different features and different source material, so I price each one to what you actually need. After a short consultation you get a quote with a fixed price and a date, so you know where you stand before any work starts. What the price depends on is set out in the Pricing section on the home page.",
      followUps: ["included", "delivery", "eshop"],
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
        "A one-page site usually takes about a week, a multi-page business site two to three weeks. An online shop depends on how many products and integrations there are. The date is agreed along with the price. What usually delays a project is waiting for text and photos — if you have those ready, it runs to plan.",
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
        "Every project includes a responsive design for phones and desktops, basic search engine optimisation, a contact form, deployment to hosting and domain setup. At the end I train you so you can change text and images yourself. The domain, hosting and code all stay yours. Everything that can be added on top is listed under What a site can do.",
      followUps: ["pricing", "care", "start"],
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
        "You send me a few sentences about your business through the form. I reply within 24 hours and we arrange a short call to go through what you need. Then I send a quote with a fixed price and a date. The consultation and the quote are free and come with no obligation.",
      followUps: ["delivery", "pricing"],
      offerContact: true,
    },

    eshop: {
      id: "eshop",
      label: "Do you build online shops?",
      keywords: [
        "eshop", "e-shop", "shop", "store", "ecommerce", "e-commerce", "sell",
        "products", "cart", "checkout", "payment", "orders",
      ],
      answer:
        "Yes. I build online shops with a product catalogue, variants, a cart, shipping and a payment gateway, including an admin area for managing orders. Pricing depends on scope — tell me roughly how many products you plan to sell and whether you need stock or accounting integrations. You can walk through a working one in the portfolio, the Nordik demo.",
      followUps: ["pricing", "delivery", "start"],
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
        "Yes. I review the existing site, keep the content and your search rankings, set up redirects and give the site a new look. The price depends on how much content there is and how much of it needs rewriting — I quote it once I've looked at the site. Send me the link and I'll tell you what I'd change.",
      followUps: ["pricing", "delivery", "start"],
      offerContact: true,
    },

    care: {
      id: "care",
      label: "What happens after launch?",
      keywords: [
        "after launch", "maintenance", "support", "care", "backups", "updates",
        "monthly", "ongoing", "look after",
      ],
      answer:
        "For the first month after launch I fix anything that doesn't work as agreed, free of charge. After that you can take a monthly care plan — backups, updates, small text changes and uptime monitoring. The price depends on what the plan needs to cover, and it's optional.",
      followUps: ["included", "start"],
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
        "You do. The domain, hosting and source code are yours and you can take them with you at any time. I don't use closed systems and I don't charge a fee to hand over your logins.",
      followUps: ["care", "included"],
      offerContact: false,
    },
  },
};
