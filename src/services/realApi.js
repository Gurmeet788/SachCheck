/**
 * SachCheck Real API Service
 * 
 * Handles real HTTP communication with our teammate's FastAPI backend.
 * 
 * Rules:
 * - Makes genuine network requests to `${API_BASE_URL}/verify`.
 * - Never injects mock data, fabricated citations, or invented confidence scores.
 * - Always returns responses with `isDemo: false`.
 * - Returns the exact same standardized response shape as mockApi.js.
 */

/**
 * Sends a claim to the real backend verification endpoint.
 * 
 * @param {string} claimText - The input text to verify
 * @param {string} apiBaseUrl - The backend base URL (e.g., http://localhost:8000/api)
 * @returns {Promise<object>} Standardized VerificationResponse
 */
export async function realVerifyClaim(claimText, apiBaseUrl) {
  const trimmed = claimText ? claimText.trim() : '';

  if (!trimmed) {
    throw new Error('Please enter a claim or news statement to verify.');
  }

  const cleanBaseUrl = (apiBaseUrl || '').replace(/\/+$/, '');

  if (!cleanBaseUrl) {
    return {
      status: 'unable_to_check',
      claimReviewed: trimmed,
      error: 'Backend API URL is not configured. Please set VITE_API_BASE_URL in your .env file.',
      evidenceSources: [],
      isDemo: false,
    };
  }

  try {
    const response = await fetch(`${cleanBaseUrl}/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ claim: trimmed }),
    });

    if (!response.ok) {
      let errDetail = `Server returned HTTP ${response.status} (${response.statusText})`;
      try {
        const errorJson = await response.json();
        if (errorJson?.detail) {
          errDetail = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        } else if (errorJson?.error || errorJson?.message) {
          errDetail = errorJson.error || errorJson.message;
        }
      } catch {
        // Fall back to HTTP status message if response is not JSON
      }

      return {
        status: 'unable_to_check',
        claimReviewed: trimmed,
        originalVerdict: null,
        verdictType: null,
        analysisSummary: null,
        evidenceSources: [],
        error: errDetail,
        isDemo: false,
      };
    }

    const data = await response.json();

    // Standardize the response to ensure consistent UI rendering
    return {
      status: data.status || 'unverified', // 'fact_check_found' | 'unverified' | 'unable_to_check'
      claimReviewed: data.claimReviewed || trimmed,
      originalVerdict: data.originalVerdict || null,
      verdictType: data.verdictType || null,
      analysisSummary: data.analysisSummary || null,
      evidenceSources: Array.isArray(data.evidenceSources) ? data.evidenceSources : [],
      error: data.error || null,
      message: data.message || null,
      guidance: data.guidance || null,
      isDemo: false,
    };
  } catch (networkError) {
    return {
      status: 'unable_to_check',
      claimReviewed: trimmed,
      originalVerdict: null,
      verdictType: null,
      analysisSummary: null,
      evidenceSources: [],
      error: `Network failure connecting to ${cleanBaseUrl}: ${networkError.message}. Ensure the FastAPI server is running and CORS is enabled.`,
      isDemo: false,
    };
  }
}
