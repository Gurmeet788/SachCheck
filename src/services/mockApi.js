/**
 * SachCheck Mock API Service
 * 
 * Dedicated mock service module for hackathon UI testing and demonstrations.
 * NEVER present mock data as real fact-check findings.
 * 
 * All mock responses guarantee:
 * - isDemo: true
 * - Explicit demo metadata & disclaimer
 * - Same response shape as the real FastAPI backend
 */

import { DEMO_VERIFICATION_DATABASE } from '../data/demoData';

/**
 * Simulates claim verification against local demo records.
 * 
 * @param {string} claimText - The input text to verify
 * @returns {Promise<object>} Standardized VerificationResponse
 */
export async function mockVerifyClaim(claimText) {
  const trimmed = claimText ? claimText.trim() : '';

  if (!trimmed) {
    throw new Error('Please enter a claim or news statement to verify.');
  }

  // Simulate realistic network latency for UI feedback (650ms - 850ms)
  await new Promise((resolve) => setTimeout(resolve, 750));

  // Simulated service error test trigger
  if (trimmed.includes('TRIGGER_SERVICE_FAILURE_TEST')) {
    return {
      status: 'unable_to_check',
      claimReviewed: trimmed,
      error: 'Simulated connection timeout: The fact-check verification service could not be reached.',
      evidenceSources: [],
      isDemo: true,
      demoNote: 'DEMO MODE: This failure state was intentionally simulated for UI error handling testing.',
    };
  }

  const lower = trimmed.toLowerCase();

  // Search local demo database by keyword
  const match = DEMO_VERIFICATION_DATABASE.find((item) =>
    item.keywords.some((keyword) => lower.includes(keyword))
  );

  if (match) {
    return {
      status: match.status,
      claimReviewed: trimmed,
      originalVerdict: match.originalVerdict,
      verdictType: match.verdictType,
      analysisSummary: match.analysisSummary,
      evidenceSources: match.evidenceSources || [],
      isDemo: true,
      demoNote: 'DEMO MODE: Matching demo scenario from local test database. Not a live verification query.',
    };
  }

  // Default demo fallback: Unverified
  // Crucial Rule: Missing evidence is NEVER proof that a claim is false!
  return {
    status: 'unverified',
    claimReviewed: trimmed,
    originalVerdict: null,
    verdictType: null,
    analysisSummary: null,
    evidenceSources: [],
    message: 'No recorded fact-check or verified evidence found in recognized public databases.',
    guidance:
      'An Unverified status does NOT mean this statement is false. It simply indicates that accredited fact-checking organizations have not published a formal review of this claim yet. Exercise healthy skepticism, avoid forwarding, and consult official primary sources.',
    isDemo: true,
    demoNote: 'DEMO MODE: Simulated unverified outcome for claims without local demo matches.',
  };
}
