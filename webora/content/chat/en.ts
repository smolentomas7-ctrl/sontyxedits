import type { ChatScript } from "./types";

export const chatEn: ChatScript = {
  initialSuggestions: ["pricing", "delivery", "included", "start"],

  fallback: {
    id: "fallback",
    answer:
      "I can't answer that one — I only have prepared answers for common questions. Send us a message through the contact form and a person will reply, usually within 24 hours.",
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
        "A one-page site starts at €490, a business site with several pages and a blog at €990. Online shops are built to order, so we quote those after a consultation. The pricing page also has a calculator where you can set the scope and see an indicative figure straight away.",
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
        "A one-page site takes 7 days, a business site 2 to 3 weeks. An online shop depends on how many products there are. What usually delays a project is waiting for text and photos — if you have those ready, it runs to plan.",
      followUps: ["start", "included", "pricing"],
      offerContact: true,
    },

    included: {
      id: "included",
      label: "What's included?",
      keywords: [
        "included", "include", "what do i get", "contains", "part of", "package",
        "comes with", "covered",
      ],
      answer:
        "Every project includes a responsive design for phones and desktops, basic search engine optimisation, a contact form, deployment to hosting and domain setup. At the end we train you so you can change text and images yourself. The domain, hosting and code all stay yours.",
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
        "You send us a few sentences about your business through the form. We reply within 24 hours and arrange a short call to go through what you need. Then we send a quote with a fixed price and a date. The consultation and the quote are free and come with no obligation.",
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
        "Yes. We build online shops with a product catalogue, variants, a cart, shipping and a payment gateway, including an admin area for managing orders. Pricing depends on scope — tell us roughly how many products you plan to sell. You can try a working shop in our portfolio, the Nordik demo.",
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
        "Yes, redesigns start at €690. We review the existing site, keep the content and your search rankings, set up redirects and give the site a new look. At the end we show you a before and after speed comparison.",
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
        "For the first month after launch we fix anything that doesn't work as agreed, free of charge. After that you can take a monthly care plan at €39 — backups, updates, small text changes and uptime monitoring. It's optional.",
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
        "You do. The domain, hosting and source code are yours and you can take them with you at any time. We don't use closed systems and we don't charge a fee to hand over your logins.",
      followUps: ["care", "included"],
      offerContact: false,
    },
  },
};
