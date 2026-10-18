/**
 * SachCheck API Service
 *
 * Communicates with the FastAPI backend.
 * Endpoints used:
 *   POST /claims/check    — submit and verify a claim
 *   GET  /claims/trending — fetch trending claims (last 24 h)
 *   GET  /stats           — platform-wide statistics
 *   GET  /health          — backend health check
 *
 * In development, Vite proxies /claims, /stats, /health → http://localhost:8000
 * In production, set VITE_API_BASE_URL to your deployed backend URL.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') ?? '';

/** Unique pseudonymous visitor ID stored in sessionStorage */
function getVisitorId() {
  let id = sessionStorage.getItem('sc_visitor_id');
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem('sc_visitor_id', id);
  }
  return id;
}

/**
 * Submit a claim for verification.
 * @param {string} claimText
 * @returns {Promise<object>} ClaimCheckResponse from the backend
 */
export async function verifyClaim(claimText) {
  const trimmed = claimText?.trim();
  if (!trimmed) throw new Error('Please enter a claim to verify.');

  const url = `${API_BASE}/claims/check`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      'X-Visitor-ID': getVisitorId(),
    },
    body: JSON.stringify({ claim_text: trimmed }),
  });

  if (!response.ok) {
    let detail = `Server error ${response.status}`;
    try {
      const err = await response.json();
      detail = err?.detail ?? detail;
    } catch { /* ignore */ }
    throw new Error(detail);
  }

  return response.json();
}

/**
 * Fetch trending claims from the last 24 hours.
 * @param {number} limit  max 100
 * @returns {Promise<Array>} array of TrendingClaimItem
 */
export async function fetchTrending(limit = 10) {
  const url = `${API_BASE}/claims/trending?limit=${limit}`;
  const response = await fetch(url, {
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) throw new Error(`Failed to fetch trending: ${response.status}`);
  return response.json();
}

/**
 * Fetch platform-wide statistics.
 * @returns {Promise<object>} stats object
 */
export async function fetchStats() {
  const url = `${API_BASE}/stats`;
  const response = await fetch(url, {
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) throw new Error(`Failed to fetch stats: ${response.status}`);
  return response.json();
}

/**
 * Check backend health.
 * @returns {Promise<object>}
 */
export async function checkHealth() {
  const url = `${API_BASE}/health`;
  const response = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error('Backend unavailable');
  return response.json();
}
