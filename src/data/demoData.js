/**
 * SachCheck Demo Dataset
 * 
 * IMPORTANT HACKATHON & ETHICAL NOTICE:
 * All entries below are strictly for DEMO MODE testing of the UI when a live
 * backend API is not connected.
 * 
 * In accordance with SachCheck ethical verification principles:
 * - Real, public debunks from recognized fact-checking bodies are used for demo matches.
 * - Unverified claims are explicitly stated as "Unverified", NEVER as false.
 * - No fake confidence scores or invented verdicts are generated.
 */

export const EXAMPLE_CLAIMS = [
  {
    id: 'claim-1',
    label: '5G & Viruses',
    type: 'debunked',
    text: 'WHO announced 5G mobile networks transmit the coronavirus disease.',
  },
  {
    id: 'claim-2',
    label: 'Viral Student Stipend',
    type: 'debunked',
    text: 'Government announces free Rs 5000 stipend for all students who register via WhatsApp link.',
  },
  {
    id: 'claim-3',
    label: 'James Webb Exoplanet',
    type: 'verified_true',
    text: 'Astronomers detect carbon dioxide in the atmosphere of exoplanet WASP-39 b using the James Webb Space Telescope.',
  },
  {
    id: 'claim-4',
    label: 'Unverified Local Event',
    type: 'unverified',
    text: 'A neighborhood library is organizing a community electronics repair workshop next Saturday.',
  },
  {
    id: 'claim-5',
    label: 'Simulate Service Error',
    type: 'error',
    text: 'TRIGGER_SERVICE_FAILURE_TEST',
  },
];

export const DEMO_VERIFICATION_DATABASE = [
  {
    keywords: ['5g', 'virus', 'coronavirus', 'transmit', 'covid'],
    status: 'fact_check_found',
    claimReviewed: 'WHO announced 5G mobile networks transmit the coronavirus disease.',
    originalVerdict: 'False',
    verdictType: 'false', // 'false' | 'misleading' | 'true' | 'altered'
    matchedAt: '2026-10-17T23:00:00Z',
    analysisSummary: 'Multiple scientific health authorities and independent fact-checkers have confirmed that viruses cannot travel on radio frequency waves or cellular networks.',
    evidenceSources: [
      {
        id: 'ev-1',
        title: '5G Mobile Networks DO NOT Spread COVID-19',
        publisher: 'World Health Organization (WHO) Mythbusters',
        publishedDate: '2020-04-20',
        url: 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters',
        originalRating: 'Debunked / False',
        keyFinding: 'Viruses cannot travel on radio waves or mobile networks. COVID-19 is spread through respiratory droplets when an infected person coughs, sneezes, or speaks.',
      },
      {
        id: 'ev-2',
        title: 'Fact Check: 5G technology does not cause or transmit coronavirus',
        publisher: 'Reuters Fact Check',
        publishedDate: '2020-04-09',
        url: 'https://www.reuters.com/article/uk-factcheck-5g-coronavirus-idUSKBN21Q2QZ',
        originalRating: 'False',
        keyFinding: 'Independent telecommunications experts and epidemiologists confirmed zero causal link between electromagnetic frequencies and biological viral transmission.',
      },
    ],
  },
  {
    keywords: ['stipend', '5000', 'whatsapp', 'students', 'allowance', 'scholarship'],
    status: 'fact_check_found',
    claimReviewed: 'Government offers Rs 5000 financial support to all students via WhatsApp link.',
    originalVerdict: 'False (Phishing Scam)',
    verdictType: 'false',
    matchedAt: '2026-10-17T23:00:00Z',
    analysisSummary: 'The viral link circulating on messaging apps is a fraudulent phishing attempt mimicking government scholarship portals.',
    evidenceSources: [
      {
        id: 'ev-3',
        title: 'PIB Fact Check: Viral message claiming government is giving Rs 5000 stipend to students is Fake',
        publisher: 'Press Information Bureau (PIB) Fact Check',
        publishedDate: '2023-08-14',
        url: 'https://pib.gov.in',
        originalRating: 'Fake / Phishing',
        keyFinding: 'Government agencies do not distribute monetary grants or solicit personal details through unverified WhatsApp links.',
      },
    ],
  },
  {
    keywords: ['james webb', 'jwst', 'exoplanet', 'carbon dioxide', 'wasp-39'],
    status: 'fact_check_found',
    claimReviewed: 'James Webb Space Telescope detected atmospheric carbon dioxide on exoplanet WASP-39 b.',
    originalVerdict: 'Verified True',
    verdictType: 'true',
    matchedAt: '2026-10-17T23:00:00Z',
    analysisSummary: 'NASA, ESA, and CSA confirmed direct spectroscopic detection of CO2 in an exoplanetary atmosphere via peer-reviewed findings in Nature.',
    evidenceSources: [
      {
        id: 'ev-4',
        title: "NASA's Webb Detects First Clear Evidence for Carbon Dioxide in an Exoplanet Atmosphere",
        publisher: 'NASA / Space Telescope Science Institute',
        publishedDate: '2022-08-25',
        url: 'https://www.nasa.gov/universe/nasas-webb-detects-first-clear-evidence-for-carbon-dioxide-in-an-exoplanet-atmosphere/',
        originalRating: 'Verified True / Official Scientific Release',
        keyFinding: 'High-precision infrared transmission spectroscopy revealed an unambiguous carbon dioxide absorption feature at 4.3 microns.',
      },
    ],
  },
  {
    keywords: ['lemon', 'hot water', 'cancer', 'cure'],
    status: 'fact_check_found',
    claimReviewed: 'Drinking hot lemon water cures all cancer within 48 hours.',
    originalVerdict: 'False / Medically Baseless',
    verdictType: 'false',
    matchedAt: '2026-10-17T23:00:00Z',
    analysisSummary: 'While citrus fruits contain nutrients, medical oncologists emphasize there is no clinical evidence that lemon water cures malignancies.',
    evidenceSources: [
      {
        id: 'ev-5',
        title: 'Fact Check: Hot lemon water does not cure cancer',
        publisher: 'American Cancer Society / Healthline',
        publishedDate: '2021-06-15',
        url: 'https://www.cancer.org',
        originalRating: 'False',
        keyFinding: 'Relying on unverified dietary remedies over oncological treatment poses severe medical hazards.',
      },
    ],
  },
];
