# SachCheck — Backend Integration Guide (FastAPI)

This guide documents the API contract between the **SachCheck React Frontend** and your team's **FastAPI Backend**.

---

## 1. Architecture Overview

To ensure smooth pair programming during the hackathon, the frontend uses two separated service modules:

1. [`src/services/mockApi.js`](file:///src/services/mockApi.js) — Handles local test scenarios and demo mode. All mock responses are tagged with `isDemo: true` and a clear demo warning.
2. [`src/services/realApi.js`](file:///src/services/realApi.js) — Dispatches genuine HTTP requests to your FastAPI server with `isDemo: false`.
3. [`src/services/api.js`](file:///src/services/api.js) — The single dispatcher consumed by the UI. It switches between mock and real requests without requiring any UI code changes.

### Environment Variable Control:
In your `.env` file:
```env
# Set to 'false' when connecting to your live FastAPI backend
VITE_USE_DEMO=false

# Your FastAPI backend base URL
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## 2. API Endpoint Specification

### Endpoint: `POST /verify`
- **Method:** `POST`
- **Path:** `/verify` (relative to `VITE_API_BASE_URL`, e.g., `http://localhost:8000/api/verify`)
- **Headers:**
  - `Content-Type: application/json`
  - `Accept: application/json`

### Request Body:
```json
{
  "claim": "WHO announced 5G mobile networks transmit the coronavirus disease."
}
```

---

## 3. Standardized Response Format

Both the mock service and your FastAPI backend return this exact JSON schema:

```json
{
  "status": "fact_check_found",
  "claimReviewed": "WHO announced 5G mobile networks transmit the coronavirus disease.",
  "originalVerdict": "False",
  "verdictType": "false",
  "analysisSummary": "Scientific health authorities have confirmed that viruses cannot travel on radio frequency waves.",
  "evidenceSources": [
    {
      "id": "ev-1",
      "title": "5G Mobile Networks DO NOT Spread COVID-19",
      "publisher": "World Health Organization (WHO) Mythbusters",
      "publishedDate": "2020-04-20",
      "url": "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters",
      "originalRating": "Debunked / False",
      "keyFinding": "Viruses cannot travel on radio waves or mobile networks."
    }
  ],
  "error": null,
  "message": null,
  "guidance": null
}
```

### Field Definitions:

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `status` | `string` | **Yes** | One of: `"fact_check_found"`, `"unverified"`, `"unable_to_check"`. |
| `claimReviewed` | `string` | **Yes** | The cleaned claim string that was verified. |
| `originalVerdict` | `string` \| `null` | No | The publisher's exact rating (e.g. `"False"`, `"Verified True"`, `"Misleading"`). |
| `verdictType` | `string` \| `null` | No | Color classification: `"false"`, `"true"`, `"misleading"`, or `"altered"`. |
| `analysisSummary` | `string` \| `null` | No | 1-2 sentence executive summary of the findings. |
| `evidenceSources` | `Array<EvidenceSource>` | **Yes** | List of cited articles/reports (empty array if none found). |
| `error` | `string` \| `null` | No | Detailed error message when `status` is `"unable_to_check"`. |
| `message` | `string` \| `null` | No | Human-readable explanation (used primarily for unverified status). |
| `guidance` | `string` \| `null` | No | Recommended next steps for the user. |

---

## 4. The 3 Required Verification Status Scenarios

### Outcome A: `fact_check_found`
Use this when your backend or fact-checking API (e.g. Google Fact Check Tools API) matches an accredited fact-check:

```json
{
  "status": "fact_check_found",
  "claimReviewed": "Government announces free Rs 5000 stipend via WhatsApp link",
  "originalVerdict": "False (Phishing Scam)",
  "verdictType": "false",
  "analysisSummary": "The circulating link is a fraudulent phishing attempt mimicking official government schemes.",
  "evidenceSources": [
    {
      "title": "PIB Fact Check: Viral message claiming government is giving Rs 5000 stipend is Fake",
      "publisher": "Press Information Bureau (PIB)",
      "publishedDate": "2023-08-14",
      "url": "https://pib.gov.in",
      "originalRating": "Fake / Scam",
      "keyFinding": "Government bodies do not disburse scholarships or funds via unverified WhatsApp links."
    }
  ]
}
```

### Outcome B: `unverified`
> [!IMPORTANT]
> **Ethical Rule:** Missing evidence is **NEVER** proof that a claim is false! If your search returns no accredited debunks, return `status: "unverified"`, **never** `"false"`.

```json
{
  "status": "unverified",
  "claimReviewed": "The municipal library will host a book exchange this weekend.",
  "originalVerdict": null,
  "verdictType": null,
  "analysisSummary": null,
  "evidenceSources": [],
  "message": "No matching fact-checks found in accredited fact-checking repositories.",
  "guidance": "Unverified does NOT mean false. It means no accredited fact-checking organization has formally investigated this claim yet. Check primary local sources directly."
}
```

### Outcome C: `unable_to_check`
Use when an upstream service (e.g. database timeout, rate limit, or external API failure) occurs:

```json
{
  "status": "unable_to_check",
  "claimReviewed": "Sample claim",
  "evidenceSources": [],
  "error": "Upstream fact-checking API rate limit reached or service timeout."
}
```

---

## 5. Ready-to-Use FastAPI Implementation Template

Here is a ready-to-copy Python snippet for your teammate using FastAPI and Pydantic:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="SachCheck Backend API", version="1.0.0")

# Enable CORS for the React/Vite frontend (running on port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VerificationRequest(BaseModel):
    claim: str

class EvidenceSource(BaseModel):
    id: Optional[str] = None
    title: str
    publisher: str
    publishedDate: Optional[str] = None
    url: str
    originalRating: Optional[str] = None
    keyFinding: Optional[str] = None

class VerificationResponse(BaseModel):
    status: str  # 'fact_check_found' | 'unverified' | 'unable_to_check'
    claimReviewed: str
    originalVerdict: Optional[str] = None
    verdictType: Optional[str] = None  # 'false' | 'true' | 'misleading' | 'altered'
    analysisSummary: Optional[str] = None
    evidenceSources: List[EvidenceSource] = []
    error: Optional[str] = None
    message: Optional[str] = None
    guidance: Optional[str] = None

@app.post("/api/verify", response_model=VerificationResponse)
async def verify_claim(payload: VerificationRequest):
    claim = payload.claim.strip()
    if not claim:
        raise HTTPException(status_code=400, detail="Claim cannot be empty")

    # TODO: Connect your real fact-checking API / search logic here
    # Example: Google Fact Check Tools API / HuggingFace / Perplexity / DuckDuckGo News
    
    # Return standardized response:
    return VerificationResponse(
        status="unverified",
        claimReviewed=claim,
        message="No verified fact-check found in public registries.",
        guidance="Unverified does NOT mean false. Please consult primary sources.",
        evidenceSources=[]
    )

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "SachCheck Verification Engine"}
```
