import type { LocaleContent } from "./types";

export const en: LocaleContent = {
  locale: "en",
  htmlLang: "en",

  common: {
    skipToContent: "Skip to content",
    callCta: "Call the workshop",
    callAria: "Call the workshop on +421 918 918 109",
    servicesCta: "Our services",
    contactCta: "Send an enquiry",
    navigateCta: "Get directions",
    readMore: "More about this service",
    backToServices: "Back to services",
    home: "Home",
    openNow: "Open now — closing at {time}",
    closedNow: "Closed now — opening {day} at {time}",
    breakNow: "On a lunch break — open again at {time}",
    breakLabel: "Lunch break",
    closedToday: "Closed today",
    today: "today",
    hoursHeading: "Opening hours",
    addressHeading: "Address",
    phoneHeading: "Phone",
    days: {
      mon: "Monday",
      tue: "Tuesday",
      wed: "Wednesday",
      thu: "Thursday",
      fri: "Friday",
      sat: "Saturday",
      sun: "Sunday",
    },
    closedLabel: "Closed",
    menu: "Menu",
    closeMenu: "Close menu",
    languageLabel: "Language",
    switchTo: "Slovensky",
    copyAddress: "Copy address",
    addressCopied: "Address copied",
    relatedServices: "Related services",
  },

  nav: {
    services: "Services",
    about: "About",
    contact: "Contact",
    privacy: "Privacy policy",
  },

  home: {
    meta: {
      title: "Car repair workshop in Ružomberok | M.I.Auto s.r.o.",
      description:
        "Independent car workshop in Ružomberok. Diagnostics, ECU software, wheel alignment, tyre service, electrics, timing belts and A/C. Call +421 918 918 109.",
    },
    heroTitle: "Car workshop in Ružomberok",
    heroTitleSecond: "Diagnostics, electronics, timing systems.",
    heroLead:
      "We work faults from the warning light to the repair. Diagnostics, ECU software, wheel alignment, tyre service, Volkswagen Group vehicle electrics, timing system replacement and A/C service.",
    heroImageAlt:
      "The M.I.Auto workshop in Ružomberok, two vehicles with bonnets open during servicing",
    servicesHeading: "What we do",
    servicesLead:
      "Seven services. Most faults start with diagnostics, which is why it comes first.",
    signatureHeading: "From warning light to repair",
    signatureLead:
      "There are five steps between a lit warning light and a repaired car. Drag the slider to see what happens at each one, and why none of them can be skipped.",
    whyHeading: "Why bring it here",
    why: [
      {
        title: "Seven services in one place",
        body:
          "Diagnostics, ECU software, wheel alignment, tyre service, Volkswagen Group vehicle electrics, timing system replacement and A/C service.",
      },
      {
        title: "Cause first, repair second",
        body:
          "A fault code is a lead, not a diagnosis. We narrow a fault down by measuring, so parts that are fine do not get replaced.",
      },
      {
        title: "Volkswagen Group vehicle electrics",
        body:
          "Electrical and electronic faults on Volkswagen Group vehicles are traced by measurement and elimination, against the wiring diagram.",
      },
      {
        title: "Timing systems on 2.0 TDI and 3.0 TDI",
        body:
          "We replace timing systems on 2.0 TDI and 3.0 TDI engines. This is work where waiting for the failure is the expensive option.",
      },
    ],
    mapHeading: "Where to find us",
    mapLead:
      "We are on Sládkovičova in Ružomberok. Call before you set off and we will know to expect you.",
    mapLoadButton: "Show the map",
    mapLoadNote:
      "The map loads from Google's servers only once you click. Until then this page sends nothing to Google.",
    finalHeading: "Call and tell us what the car is doing",
    finalLead:
      "The phone is the fastest route to an answer. Outside opening hours, use the enquiry form.",
    finalFormCta: "I would rather write",
  },

  servicesPage: {
    meta: {
      title: "Services | M.I.Auto s.r.o. Ružomberok",
      description:
        "Diagnostics, ECU software, wheel alignment, tyre service, Volkswagen Group electrics, timing systems and A/C service in Ružomberok. Call +421 918 918 109.",
    },
    h1: "Services",
    lead:
      "Seven areas we work in. Each one covers when to deal with it, how we go about it, and something you can try out for yourself.",
    faqHeading: "Common questions",
    ctaHeading: "Not sure which service your fault belongs to?",
    ctaLead:
      "That is normal — most faults show up somewhere other than where they start. Call and describe what the car is doing.",
  },

  services: {
    "diagnostika-vozidiel": {
      slug: "diagnostika-vozidiel",
      name: "Vehicle diagnostics",
      h1: "Vehicle diagnostics",
      icon: "scan-line",
      cardDescription:
        "We read the fault codes and look for the cause behind the warning light, not just clear the message.",
      lead:
        "A warning light tells you a control unit has recorded a fault. It does not tell you what caused it. Diagnostics is the step from the message to the cause — we read the stored fault codes, look at live sensor data, and compare it against how the vehicle is actually behaving.",
      overview:
        "A fault code tells you which circuit is reporting a problem, not which part has failed. Diagnostics is the work between those two sentences.",
      covers: [
        "Reading stored and current fault codes",
        "Checking live sensor data",
        "Narrowing the fault to a specific circuit or component",
      ],
      when: [
        "The engine, ABS, airbag or another warning light is on.",
        "The car is down on power, hesitating, idling roughly or harder to start.",
        "Fuel consumption has risen with no obvious reason.",
        "Something has stopped working — air conditioning, lights, electric windows.",
        "The warning light came back on after a previous repair.",
      ],
      what: [
        "We connect to the OBD port and read both stored and current fault codes.",
        "We verify the code by measuring and by live sensor data, so a healthy part is not replaced.",
        "We narrow the fault down to a specific circuit or component.",
        "We tell you what we found and agree what happens next.",
      ],
      related: ["cipovanie-ecu", "elektroinstalacia-vw"],
      meta: {
        title: "Vehicle diagnostics in Ružomberok | M.I.Auto s.r.o.",
        description:
          "Warning light on? In Ružomberok we read the fault codes and look for the cause, not just the symptom. Call +421 918 918 109 and tell us what it is doing.",
      },
    },

    "cipovanie-ecu": {
      slug: "cipovanie-ecu",
      name: "ECU software and chiptuning",
      h1: "ECU software and chiptuning",
      icon: "cpu",
      cardDescription:
        "Software modification of the engine control unit. What is possible depends on the specific vehicle.",
      lead:
        "Chiptuning means changing the software in the engine control unit. It is not a one-size-fits-all job — what can and cannot be done depends on the particular engine, its condition, and what you want from the vehicle. That is why we discuss it by phone about your specific car rather than from a price list.",
      overview:
        "Software modification of the engine control unit. The answer to “what can be done with my car” only exists for a specific vehicle.",
      covers: [
        "Software modification of the engine control unit",
        "Assessment of what is possible on a specific vehicle",
        "Discussed by phone, about your engine",
      ],
      when: [
        "You are considering an engine software change and want to know what is possible on your vehicle at all.",
        "After a previous software change the vehicle behaves differently than you expected.",
        "You want to talk it through before deciding anything.",
      ],
      what: [
        "We establish which vehicle and engine it is and what you expect from the change.",
        "We go through what is and is not possible on that specific vehicle.",
        "Scope and approach are agreed by phone, about your car.",
      ],
      note:
        "Before deciding, consider the circumstances of your own vehicle and how you use it. Specific questions are best handled on the phone.",
      related: ["diagnostika-vozidiel", "elektroinstalacia-vw"],
      meta: {
        title: "ECU software and chiptuning in Ružomberok | M.I.Auto s.r.o.",
        description:
          "Engine control unit software work in Ružomberok. What is possible on your engine is a phone conversation, not a price list — call +421 918 918 109.",
      },
    },

    "geometria-kolies": {
      slug: "geometria-kolies",
      name: "Wheel alignment",
      h1: "Wheel alignment",
      icon: "crosshair",
      cardDescription:
        "Measuring and adjusting wheel geometry. Fixes pulling to one side and uneven tyre wear.",
      lead:
        "Wheel geometry is how the wheels sit relative to the road and to each other. When the settings drift — off a kerb, after a suspension part is replaced, or gradually through wear — the car pulls to one side, the steering wheel sits off centre and the tyres wear unevenly. Measuring shows the real figures so they can be set.",
      overview:
        "When a car pulls to one side, or the tyres wear along one edge, the cause is usually geometry. Measuring settles it.",
      covers: [
        "Measuring the actual geometry figures",
        "Adjusting to the values specified for the vehicle",
        "Checking the suspension for play before measuring",
      ],
      when: [
        "The car pulls to one side on a level road.",
        "The steering wheel is off centre when driving straight.",
        "Tyres are worn more on the inner or outer edge.",
        "After a suspension part has been replaced, or after hitting a kerb.",
        "After a tyre change, when you want new tyres to wear evenly.",
      ],
      what: [
        "We prepare the vehicle and check the suspension for play that would distort the measurement.",
        "We measure the actual figures and compare them against the values for that vehicle.",
        "We adjust whatever is adjustable on that vehicle.",
        "We go through the figures with you, before and after.",
      ],
      related: ["pneuservis", "diagnostika-vozidiel"],
      meta: {
        title: "Wheel alignment in Ružomberok | M.I.Auto s.r.o.",
        description:
          "Is your car pulling to one side, or are the tyres wearing unevenly? We measure and set the wheel geometry in Ružomberok. Call +421 918 918 109.",
      },
    },

    pneuservis: {
      slug: "pneuservis",
      name: "Tyre service",
      h1: "Tyre service",
      icon: "circle-dot",
      cardDescription:
        "Work on tyres and wheels. Tread depth decides braking distance more than most drivers assume.",
      lead:
        "Tyres are the only part of a car that touches the road. Braking distance and how the car behaves in a corner both depend on their condition, and on a wet surface the gap between nearly new and worn-out tread is wider than people expect. We look at the tyres and the wheels and tell you where they stand.",
      overview:
        "Tyres are a car's only contact with the road. As tread depth approaches the legal minimum, wet braking distance grows sharply.",
      covers: [
        "Work on tyres and wheels",
        "Assessment of condition and tread depth",
        "Seasonal changeover by arrangement",
      ],
      when: [
        "The season is turning and you need to change to winter or summer tyres.",
        "A tyre is losing pressure, or you have driven over something sharp.",
        "You feel vibration through the steering wheel or the seat at speed.",
        "Tread is close to the legal minimum, or worn unevenly.",
      ],
      what: [
        "We look at the condition of the tyres and wheels and measure the tread depth.",
        "We tell you what we see, and which of it actually needs dealing with.",
        "We agree the work and a time — call and tell us which vehicle it is.",
      ],
      related: ["geometria-kolies", "diagnostika-vozidiel"],
      meta: {
        title: "Tyre service in Ružomberok | M.I.Auto s.r.o.",
        description:
          "Tyre service in Ružomberok — work on tyres and wheels at an independent workshop. Call +421 918 918 109 to confirm what we can do for your car.",
      },
    },

    "elektroinstalacia-vw": {
      slug: "elektroinstalacia-vw",
      name: "Volkswagen Group vehicle electrics",
      h1: "Volkswagen Group vehicle electrics",
      icon: "cable",
      cardDescription:
        "Tracing and repairing electrical and electronic faults on Volkswagen Group vehicles.",
      lead:
        "An electrical fault rarely shows itself where it starts. A broken conductor, a corroded contact or a communication fault between control units surfaces as equipment that will not work, or as a warning light. We trace the cause by measuring and eliminating, not by replacing parts blind.",
      overview:
        "An electrical fault surfaces somewhere other than where it starts. It is found by measurement and elimination, against that vehicle's wiring diagram.",
      covers: [
        "Tracing electrical and electronic faults",
        "Measuring the affected circuit against the wiring diagram",
        "Repairs to wiring and contacts",
      ],
      when: [
        "Electrical equipment has stopped working — windows, mirrors, lights, central locking.",
        "The fault comes and goes, often after rain or over bumps.",
        "The battery goes flat while the car is standing.",
        "Something stopped working after accessories were fitted or the wiring was worked on.",
      ],
      what: [
        "We get the fault described — when it appears and under what conditions.",
        "We measure voltage and resistance in the affected circuit and compare against the diagram.",
        "We narrow the fault to a specific conductor, contact or control unit.",
        "We repair what can be repaired and tell you what needs replacing.",
      ],
      note:
        "M.I.Auto s.r.o. is an independent workshop. We are not an authorised Volkswagen service centre. “Volkswagen Group vehicles” simply describes what we work on.",
      related: ["diagnostika-vozidiel", "cipovanie-ecu"],
      meta: {
        title: "Volkswagen Group vehicle electrics in Ružomberok | M.I.Auto s.r.o.",
        description:
          "Electrical and electronic faults on Volkswagen Group vehicles, traced by measurement in Ružomberok. Independent workshop. Call +421 918 918 109.",
      },
    },

    "vymena-rozvodov": {
      slug: "vymena-rozvodov",
      name: "Timing system replacement",
      h1: "Timing system replacement",
      icon: "cog",
      cardDescription:
        "Timing system replacement on 2.0 TDI and 3.0 TDI engines. A neglected timing belt wrecks the engine.",
      lead:
        "The timing system keeps the crankshaft and camshaft moving in step. When a belt or chain fails, pistons and valves meet and the damage is usually extensive. That is why timing systems are replaced preventively, at the manufacturer's interval. We do this work on 2.0 TDI and 3.0 TDI engines.",
      overview:
        "Timing systems are replaced preventively, at the manufacturer's interval. We do this work on 2.0 TDI and 3.0 TDI engines.",
      covers: [
        "Timing system replacement on 2.0 TDI engines",
        "Timing system replacement on 3.0 TDI engines",
        "Checking the condition of pulleys and the tensioner",
      ],
      when: [
        "The vehicle is approaching the replacement interval set by the manufacturer.",
        "You do not know whether a previous owner ever had it changed.",
        "There is whining, squealing or rattling from the timing end of the engine.",
        "The engine is harder to start or runs roughly and the timing is suspect.",
      ],
      what: [
        "We establish which engine it is and what is specified for it.",
        "We open up the timing area and check the belt, pulleys and tensioner.",
        "We replace the parts and set the timing to the manufacturer's figures.",
        "Once it is back together we check the engine running.",
      ],
      related: ["diagnostika-vozidiel", "elektroinstalacia-vw"],
      meta: {
        title: "Timing belt replacement, 2.0 TDI and 3.0 TDI | M.I.Auto Ružomberok",
        description:
          "Timing system replacement on 2.0 TDI and 3.0 TDI engines in Ružomberok. Do not leave it — call +421 918 918 109 and check the interval for your engine.",
      },
    },

    "servis-klimatizacie": {
      slug: "servis-klimatizacie",
      name: "Air conditioning service",
      h1: "Air conditioning service",
      icon: "snowflake",
      cardDescription:
        "Air conditioning that stops cooling is usually refrigerant or a leak. It fades gradually.",
      lead:
        "Air conditioning loses refrigerant even without a fault, through the small leaks inherent in the system. When cooling gradually weakens, the reason is usually a shortage of refrigerant or a leak. That is why drivers notice it in summer, although the system has been losing performance for months.",
      overview:
        "Cooling fades gradually, so most drivers notice it in summer. Vent temperature says more about the charge than the way it feels.",
      covers: [
        "Assessment of the air conditioning system",
        "Check of cooling performance",
        "Discussed for your specific vehicle",
      ],
      when: [
        "The air conditioning cools less than it used to, or not at all.",
        "There is a smell from the vents when it is switched on.",
        "The windows take longer to demist in winter than they used to.",
        "You have not had the system looked at in years and want to know its condition.",
      ],
      what: [
        "You describe how the air conditioning behaves and since when.",
        "We look at the system and measure how well it cools.",
        "We tell you what we found and agree what happens next.",
      ],
      related: ["diagnostika-vozidiel", "elektroinstalacia-vw"],
      meta: {
        title: "Air conditioning service in Ružomberok | M.I.Auto s.r.o.",
        description:
          "Air conditioning not cooling like it used to? We will look at it and measure how it performs. Call +421 918 918 109 — Ružomberok, Sládkovičova.",
      },
    },
  },

  about: {
    meta: {
      title: "About the workshop | M.I.Auto s.r.o. Ružomberok",
      description:
        "M.I.Auto s.r.o. is an independent car workshop on Sládkovičova in Ružomberok. Diagnostics, electronics, timing systems, tyres and A/C. Call +421 918 918 109.",
    },
    h1: "About the workshop",
    lead:
      "M.I.Auto s.r.o. is an independent car workshop on Sládkovičova in Ružomberok. We work on diagnostics, vehicle electronics and mechanical repairs.",
    whatWeDoHeading: "What we work on",
    quietHeading: "How we go about it",
    quietBody: [
      "Most faults show up somewhere other than where they start. An engine warning light does not say which part has failed — it says that a control unit recorded a value outside what it expected. All of the work lives between those two sentences.",
      "So a fault code gets verified by measurement. That is slower than replacing the part the code mentions, but it is the only way to avoid replacing a part that was fine.",
      "The same holds for electrics and for timing systems. Electrical faults are worked through the wiring diagram, by elimination. Timing systems are not left until they fail, because once a timing system fails the repair is no longer about the timing system.",
    ],
    ownersHeading: "Owners",
    ownerRoles: {
      owner: "Owner",
      coOwner: "Co-owner",
    },
    experience: {
      heading: "Experience, expertise and honest work",
      lead: "Your car in the hands of people who know it.",
      body:
        "Behind our work are more than 10 years of experience servicing and maintaining cars. Our grounding also comes from completed studies at a motor mechanics school, where we achieved excellent results. We put that knowledge and that practical experience into the day-to-day care of our customers' vehicles.",
      points: [
        {
          title: "More than 10 years of experience",
          body: "Hands-on experience servicing and maintaining cars.",
        },
        {
          title: "Technical education in the trade",
          body: "Completed studies at a motor mechanics school.",
        },
        {
          title: "An emphasis on quality",
          body: "A precise approach, responsible work and care for every vehicle.",
        },
      ],
    },
    factsHeading: "Where to find us",
    interiorAlt: "Inside the M.I.Auto workshop, vehicles in for service",
    detail01Alt: "A vehicle raised on the two-post lift in the M.I.Auto workshop",
    detail02Alt: "An off-road vehicle on the lift in the M.I.Auto workshop",
  },

  contact: {
    meta: {
      title: "Contact | M.I.Auto s.r.o. Ružomberok",
      description:
        "Sládkovičova 2528/108, 034 01 Ružomberok, Slovakia. Open Monday to Friday 07:00–17:00, with a break from 12:00 to 13:00. Call +421 918 918 109 or send an enquiry through the form.",
    },
    h1: "Contact",
    lead:
      "The phone is the quickest way to sort something out. Outside opening hours, use the form below.",
    mapHeading: "Map",
    mapTitle: "Map showing M.I.Auto s.r.o., Sládkovičova 2528/108, Ružomberok",
    mapDisclosure:
      "This map is embedded from Google Maps. Loading it connects you to Google's servers.",
    mapDisclosureLink: "More in the privacy policy",
    formHeading: "Send an enquiry",
    formLead:
      "The more specifically you describe what the car is doing, the better we can prepare.",
  },

  form: {
    name: "Name",
    namePlaceholder: "Jane Smith",
    phone: "Phone",
    phonePlaceholder: "+421 900 000 000",
    email: "Email",
    emailOptional: "optional",
    vehicle: "Vehicle",
    vehiclePlaceholder: "Škoda Octavia 2.0 TDI, 2016",
    vehicleHint: "Make, model and year — it helps us prepare.",
    service: "Service",
    serviceOther: "Something else",
    servicePrompt: "Choose a service",
    message: "Message",
    messagePlaceholder:
      "Describe what the car is doing, since when, and under what conditions it happens.",
    consent:
      "I agree to my details being processed in order to answer this enquiry.",
    consentLink: "Privacy policy",
    submit: "Send enquiry",
    submitting: "Sending…",
    disabledReason:
      "Sending is not available yet: fill in your name, phone, message and tick the consent box.",
    successHeading: "Enquiry sent",
    successBody:
      "We have your enquiry and will get back to you. If it is urgent, call us directly.",
    errorHeading: "The enquiry could not be sent",
    errorBody:
      "Sending failed and your enquiry did not go through. Try again, or call us directly — that is faster anyway.",
    charactersLeft: "{n} characters left",
    errors: {
      nameRequired: "Please enter your name.",
      nameLength: "Name must be between 2 and 80 characters.",
      phoneRequired: "Please enter a phone number.",
      phoneInvalid: "That does not look like a phone number.",
      emailInvalid: "Please check the email address.",
      messageRequired: "Please tell us what we can help with.",
      messageLength: "The message must be between 10 and 1500 characters.",
      consentRequired: "We cannot process the enquiry without your consent.",
      tooFast: "The form was submitted too quickly. Please try again.",
    },
  },

  faq: [
    {
      id: "sluzby",
      q: "What services do you offer?",
      a: "Vehicle diagnostics, ECU software, wheel alignment, tyre service, Volkswagen Group vehicle electrics, timing system replacement and air conditioning service.",
    },
    {
      id: "kde",
      q: "Where are you?",
      a: "Sládkovičova 2528/108, 034 01 Ružomberok. The contact page has a map and a directions link.",
    },
    {
      id: "hodiny",
      q: "What are your opening hours?",
      a: "Monday to Friday, 07:00 to 17:00, with a lunch break from 12:00 to 13:00. Closed on Saturday and Sunday.",
    },
    {
      id: "termin",
      q: "How do I arrange a visit?",
      a: "Call +421 918 918 109. Outside opening hours, use the form on the contact page.",
    },
    {
      id: "priprava",
      q: "What should I have ready when I call?",
      a: "The make, model and year, the engine if you know it, a description of what the car is doing, since when, and which warning lights are on.",
    },
    {
      id: "vw",
      q: "Do you work on Volkswagen Group vehicles?",
      a: "Yes, Volkswagen Group vehicle electrics is one of our services. M.I.Auto s.r.o. is an independent workshop, not an authorised Volkswagen service centre.",
    },
    {
      id: "ecu",
      q: "Do you do ECU work?",
      a: "Yes. What is possible on a particular engine depends on the vehicle, so we discuss it by phone.",
    },
  ],

  privacy: {
    meta: {
      title: "Privacy policy | M.I.Auto s.r.o.",
      description:
        "What the enquiry form collects, how long we keep it, how the embedded map and the automated assistant work, and what rights you have.",
    },
    h1: "Privacy policy",
    reviewNotice:
      "This document has not been legally reviewed. It must be checked and completed by someone legally qualified before this site goes live. We make no claim that it complies with the GDPR or any other regulation.",
    updated: "Last updated: on deployment of this site",
    controller: {
      heading: "Who processes the data",
      intro:
        "The controller deciding how personal data from this site is processed is:",
    },
    sections: [
      {
        heading: "The enquiry form",
        body: [
          "The form on the contact page collects a name, a phone number, optionally an email address, optionally a note about the vehicle, the service selected and the text of the message.",
          "We process this solely in order to reply to your enquiry and arrange a time if needed. We do not use it for marketing and do not pass it to third parties for their own purposes.",
          "The legal basis is our legitimate interest in answering an enquiry you sent us yourself, or steps taken prior to entering into a contract if we agree on a repair.",
          "A submitted form is processed by Netlify Forms, operated by Netlify, which stores the message and makes it available to us; the data sits on its infrastructure. Netlify acts as a processor here.",
          "We keep submitted enquiries for 12 months after the enquiry is dealt with, then delete them. If an enquiry turns into a job, the data belonging to that job follows the retention periods for accounting and tax records. Only the owners of the workshop have access to the messages.",
        ],
      },
      {
        heading: "Photographs of the owners",
        body: [
          "The About page shows photographs of the workshop's owners together with their names. A photograph of an identifiable person is personal data, and it is published with the consent of the people concerned.",
          "That consent can be withdrawn at any time using the contact details above; once withdrawn, we remove the photograph from the site.",
        ],
      },
      {
        heading: "The embedded Google map",
        body: [
          "The contact page embeds a map from Google Maps. When the map loads, your browser connects to Google's servers, and Google may process your IP address and other technical data under its own terms.",
          "On the home page the map does not load by itself. It appears only after you click a button, so until you do, the home page sends nothing to Google.",
        ],
      },
      {
        heading: "The automated assistant",
        body: [
          "There is an automated assistant in the bottom right corner. It is not a person, and the panel header says so.",
          "The transcript is kept only in your own browser (sessionStorage) and disappears when you close the tab. We do not retain transcripts on our side.",
          "When the assistant is connected to a language model, the text of your question is sent to the model provider — Anthropic — so it can answer. Your name, phone number and email are not sent; the assistant does not ask for them and has no access to them. It is also instructed not to collect personal data.",
          "We record only technical data about each request: the time, the language of the page, how long the answer took, how many tokens were processed, whether a fallback answer was used, and which section of the site the answer drew on. We do not record message text, and these records are not linked to your identity.",
          "If you click thumbs up or thumbs down under an answer, only that signal and the answer's position in the conversation are recorded — not its text, and not the text of your question.",
        ],
      },
      {
        heading: "Cookies and analytics",
        body: [
          "This site sets no tracking cookies and has no analytics installed. That is also why there is no consent banner — there would be nothing to consent to.",
          "Your browser remembers only your chosen language and the conversation in progress with the assistant. Neither leaves your device.",
        ],
      },
      {
        heading: "Fonts and external content",
        body: [
          "Fonts are served from this site itself. Nothing is fetched from an external font service.",
          "External content consists of the Google map described above and, when the assistant is switched on, its requests to the model provider.",
        ],
      },
      {
        heading: "Your rights",
        body: [
          "As a data subject you have the following rights in relation to your personal data:",
          "Right of access — you may ask for confirmation of whether we process data about you, and for a copy of it.",
          "Right to rectification — if the data is inaccurate or incomplete, you may ask us to correct or complete it.",
          "Right to erasure — you may ask us to delete the data, in particular where it is no longer needed for the purpose it was collected for.",
          "Right to restriction of processing — you may ask us to store the data only, for example while its accuracy is being verified.",
          "Right to data portability — data you provided to us can be supplied to you in a commonly used, machine-readable format.",
          "Right to object — you may object at any time to processing based on legitimate interest.",
          "Right to withdraw consent — where processing is based on consent, you may withdraw it at any time; withdrawal does not affect the lawfulness of processing before it.",
          "Right to lodge a complaint — you may contact the Office for Personal Data Protection of the Slovak Republic, Hraničná 12, 820 07 Bratislava.",
          "You can exercise these rights using the contact details at the top of this document. We will respond without undue delay.",
        ],
      },
    ],
  },

  castrol: {
    eyebrow: "Partnership",
    heading: "Castrol Service partner",
    lead: "Quality you can rely on.",
    body:
      "We work with Castrol Service, and we use Castrol oils for engine oil changes. For every vehicle we choose the oil according to the manufacturer's requirements, the specifications it needs and the recommendations for that particular engine.",
    points: [
      "A contractual partnership with Castrol Service",
      "Castrol engine oils",
      "Oil chosen to the vehicle manufacturer's specification",
      "An emphasis on quality and the correct service procedure",
    ],
  },

  signature: {
    title: "From warning light to repair",
    hint: "Drag the slider to step through the five stages.",
    keyboardHint:
      "Arrow keys move in small steps, Page Up and Page Down move a stage at a time, Home and End jump to the ends.",
    svgTitle:
      "An instrument cluster with a diagnostic tool connected. In the final stage the cluster shows no warning lights.",
    stageLabel: "Stage",
    stages: [
      {
        name: "Warning light on",
        body: "A control unit recorded a value outside what it expected and lit the lamp. What caused it cannot be read from the lamp itself.",
      },
      {
        name: "Diagnostics connected",
        body: "The tool plugs into the OBD port and starts talking to the control units. Only then can we see what they recorded.",
      },
      {
        name: "Fault codes read",
        body: "The codes say which circuit is reporting a problem. They are leads, not a diagnosis — one code can have several different causes.",
      },
      {
        name: "Repair",
        body: "Measuring narrows the circuit down to one point, and that point gets repaired. This is the step you cannot skip by replacing whatever the code names.",
      },
      {
        name: "Cleared, warning lights out",
        body: "After the repair the memory is cleared and we check the lamp stays out. Clearing it without the repair only postpones the problem.",
      },
    ],
    codes: [
      { id: "P0401", label: "EGR circuit" },
      { id: "P0299", label: "boost pressure" },
      { id: "P0133", label: "oxygen sensor" },
    ],
    displayTitle: "FAULT CODES — ILLUSTRATION",
    circuitTitle: "CIRCUIT TEST",
    circuitPoints: ["supply", "fuse", "connector", "ground"],
    dialRpm: "rpm × 1000",
    dialSpeed: "km/h",
    odo: "124 870",
  },

  chat: {
    launcherLabel: "Open the automated assistant",
    panelTitle: "Automated assistant",
    panelSubtitle: "Answers from the content of this site",
    automatedBadge: "Automated assistant, not a person",
    greeting:
      "Hello. I can answer questions about the services, opening hours and where to find the workshop. I cannot give prices, appointments or repair times — those come from the phone.",
    inputLabel: "Your question",
    inputPlaceholder: "Type a question…",
    send: "Send",
    stop: "Stop",
    close: "Close",
    sourceLabel: "Source",
    errorMessage:
      "I cannot answer right now. Call +421 918 918 109 and someone will help straight away.",
    turnLimit:
      "That is as far as I can take it. For a specific vehicle, +421 918 918 109 is the place to go.",
    suggestedLabel: "You could ask",
    starterChips: [
      "My engine warning light is on",
      "Do you do wheel alignment?",
      "What are your opening hours?",
      "Where are you?",
    ],
    scriptedNotice:
      "Right now I can only answer basic questions. For anything else, call {phone}.",
    thinking: "Writing a reply",
    feedbackUp: "This helped",
    feedbackDown: "This did not help",
    feedbackThanks: "Thank you.",
  },

  widgets: {
    dyno: {
      heading: "What a remap does to the power curve",
      lead: "The slider adds power and the chart alongside shows what happens to the curve. Grey is the baseline, orange the modified one. Power is calculated from torque as P = M × n / 9549, so the two curves always agree with each other.",
      disclaimer:
        "This illustrates the principle on a representative 2.0 TDI. It is not a measurement of your vehicle and not a promise of a result. What is possible on a particular engine depends on its condition and is discussed by phone:",
      sliderLabel: "Power increase",
      power: "Power",
      torque: "Torque",
      stock: "standard",
      sceneAlt: "A vehicle on a rolling road, its wheels turning on the rollers.",
      chartAlt: "Chart of power and torque against engine speed.",
      legendPower: "power (kW)",
      legendTorque: "torque (Nm)",
      legendStock: "standard",
    },
    diagnostics: {
      heading: "From symptom to cause",
      lead: "Pick what the car is doing. You will see how many causes are in play and how measuring narrows them to one. This is what diagnostics actually is — a fault code is a lead, not a diagnosis.",
      disclaimer:
        "A simplified illustration of the process. The real number and order of steps depend on the vehicle and on what the measurements show. Tell us what your car is doing:",
      pick: "What the car is doing",
      remaining: "Causes remaining",
      narrowed: "Narrowed to",
      stepLabel: "Measurement step",
      reset: "Start again",
      sceneAlt: "A list of possible causes being narrowed down by measurement.",
      symptoms: [
        {
          id: "mil",
          label: "Engine warning light is on",
          causes: [
            "manifold pressure sensor",
            "intake system leak",
            "recirculation valve",
            "turbocharger",
            "air mass sensor",
            "injection",
          ],
          steps: [
            "We read the stored codes and the conditions they were recorded under.",
            "We compare requested and actual boost pressure in the live data.",
            "A leak test rules out a leak in the intake tract.",
            "One cause is left, and we confirm it by measuring at the component.",
          ],
        },
        {
          id: "power",
          label: "Down on power",
          causes: [
            "blocked fuel filter",
            "boost pressure control",
            "air mass sensor",
            "play in the timing system",
            "exhaust restriction",
          ],
          steps: [
            "We check whether the control unit is limiting power, and why.",
            "We measure fuel pressure under load.",
            "We compare boost pressure against the requested value.",
            "One cause is left, and we confirm it by measuring.",
          ],
        },
        {
          id: "cold",
          label: "Hard to start from cold",
          causes: [
            "glow plugs",
            "fuel system tightness",
            "rail pressure",
            "temperature sensor",
            "battery condition",
          ],
          steps: [
            "We measure battery voltage while cranking.",
            "We check the glow system and the resistance of each plug.",
            "We check whether the fuel system holds pressure overnight.",
            "One cause is left, and we confirm it by measuring.",
          ],
        },
      ],
    },
    alignment: {
      heading: "How geometry wears a tyre out",
      lead: "Move the toe and camber settings and watch what they do to the tyre and to the way the car behaves. With the right values the tread wears evenly and the car holds its line.",
      disclaimer:
        "An illustration of the principle. Correct values differ for every vehicle, are set by the manufacturer, and can only be measured on the car itself:",
      toe: "Toe",
      camber: "Camber",
      wear: "Tread wear",
      pull: "Pulling",
      ok: "Within range",
      sceneAlt: "A suspension diagram and a tyre cross-section showing the wear pattern.",
      wearInner: "on the inner edge",
      wearOuter: "on the outer edge",
      wearEven: "even",
      pullLeft: "to the left",
      pullRight: "to the right",
      pullNone: "none",
      frontView: "front view — camber",
      topView: "top view — toe",
      section: "tyre in section",
      exaggerated: "Angles are drawn larger than they are, so they can be seen.",
    },
    tyres: {
      heading: "Tread depth and braking distance",
      lead: "Move the tread depth from a new tyre down to the legal minimum and see what it does to braking distance on a wet road.",
      disclaimer:
        "Indicative figures from publicly published wet-braking tests, not a measurement of your tyre. Real distance depends on the tyre, the surface and the depth of water. We can measure the state of yours:",
      depth: "Tread depth",
      braking: "Wet braking distance",
      legalMin: "legal minimum",
      versusNew: "compared with a new tyre",
      fromSpeed: "from 80 km/h",
      sceneAlt: "A tyre cross-section with diminishing tread, and a braking distance comparison.",
    },
    electrics: {
      heading: "Finding a break in a circuit",
      lead: "Click the points along the circuit and measure where voltage is still present and where it is not. The fault lies between the last point with voltage and the first without.",
      disclaimer:
        "A simplified circuit, to illustrate the method. A real wiring diagram has considerably more branches and connectors:",
      instruction: "Measure voltage at each point",
      measure: "Measure",
      reset: "Start again",
      found: "The break is between these points",
      notMeasured: "not measured",
      sceneAlt: "A circuit diagram running from supply through fuse and connector to the load and ground.",
      points: [
        { id: "supply", label: "Supply" },
        { id: "fuse", label: "After the fuse" },
        { id: "connector", label: "After the connector" },
        { id: "load", label: "At the load" },
      ],
    },
    timing: {
      heading: "Why you do not wait on a timing belt",
      lead: "Move the mileage and watch what happens to the belt. You can run what happens when it snaps at any point — and that is the reason a timing belt is replaced on an interval rather than on condition.",
      disclaimer:
        "An illustration of wear, not a prediction for your vehicle. The replacement interval is set by the manufacturer for the specific engine, and we will check it for you:",
      mileage: "Mileage since last replacement",
      condition: "Belt condition",
      interval: "illustrative replacement interval",
      run: "Run the failure scenario",
      reset: "Back",
      sceneAlt: "A timing belt running over its sprockets, and its wear.",
      states: ["no visible wear", "tooth wear beginning", "cracking, past the interval"],
      failure: "Belt snapped",
      failureBody:
        "The camshaft stops, the crankshaft keeps turning. A piston meets an open valve. A timing belt job has just become cylinder head work.",
    },
    aircon: {
      heading: "Refrigerant charge and vent temperature",
      lead: "Move the refrigerant charge and watch how the air coming out of the vents responds. Cooling does not fail suddenly — it fades, which is why drivers notice it in summer.",
      disclaimer:
        "An illustration of the principle at a cabin temperature of around 30 °C, not a measurement of your air conditioning. We can establish its real condition on the car:",
      charge: "Refrigerant charge",
      ventTemp: "Vent temperature",
      state: "State",
      sceneAlt: "An air conditioning circuit with compressor, condenser and evaporator.",
      states: ["badly undercharged", "low charge", "correct charge"],
      parts: ["compressor", "condenser", "expansion valve", "evaporator"],
      cabin: "cabin",
    },
  },

  footer: {
    tagline: "Independent car workshop in Ružomberok.",
    servicesHeading: "Services",
    contactHeading: "Contact",
    legalHeading: "Documents",
    rights: "All rights reserved.",
    icoLabel: "Company number",
    dicLabel: "Tax number",
    icDphLabel: "VAT number",
    registryLabel: "Registered",
  },

  notFound: {
    title: "Page not found",
    body: "This address does not exist. Try the services or the contact page.",
    cta: "Go to the home page",
  },
};
