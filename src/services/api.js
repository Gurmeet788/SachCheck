/**
 * SachCheck Unified Verification Service Dispatcher
 * 
 * Orchestrates calls between the dedicated Mock Service (`mockApi.js`)
 * and the Real HTTP API Service (`realApi.js`).
 * 
 * Environment Configuration:
 * - VITE_USE_DEMO: Set to 'true' to force demo mode, or 'false' to use the real backend.
 * - VITE_API_BASE_URL: The base URL of our teammate's FastAPI backend (e.g. http://localhost:8000/api).
 * 
 * Both services return the exact same standardized response format.
 */

import { mockVerifyClaim } from './mockApi';
import { realVerifyClaim } from './realApi';

const RAW_USE_DEMO = import.meta.env.VITE_USE_DEMO;
const RAW_API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const API_BASE_URL = RAW_API_BASE_URL ? RAW_API_BASE_URL.trim() : '';

/**
 * Determines whether demo mode is active.
 * Defaults to true if VITE_USE_DEMO is explicitly 'true' or if no API_BASE_URL is provided.
 */
export function isDemoMode() {
  if (RAW_USE_DEMO === 'true') return true;
  if (RAW_USE_DEMO === 'false') return false;
  // If not explicitly set, run in demo mode when no backend URL is specified
  return !API_BASE_URL;
}

/**
 * Checks whether a live backend API is active and configured.
 */
export function isBackendConfigured() {
  return !isDemoMode() && Boolean(API_BASE_URL);
}

/**
 * Returns a human-readable description of current endpoint status.
 */
export function getBackendEndpoint() {
  if (isDemoMode()) {
    return 'Demo Mode (Mock Service Active)';
  }
  return API_BASE_URL || 'No Backend URL Configured';
}

/**
 * Primary verification function consumed by the UI.
 * Transparently delegates to mockVerifyClaim or realVerifyClaim.
 * 
 * @param {string} claimText - The user's input claim
 * @returns {Promise<object>} Standardized VerificationResponse
 */
export async function verifyClaim(claimText) {
  if (isDemoMode()) {
    return await mockVerifyClaim(claimText);
  }

  return await realVerifyClaim(claimText, API_BASE_URL);
}
