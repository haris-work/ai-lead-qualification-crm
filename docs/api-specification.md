# API Specification — AI Lead Qualification CRM

**Version:** development v1  
**Base URL:** `http://localhost:5678` (local demonstration only)  
**Endpoint:** `POST /webhook/crm-new-lead` (published workflow)  
**Test endpoint:** `POST /webhook-test/crm-new-lead` (requires test listener)

## 1. Request

`Content-Type: application/json` preferred for backend clients. The website may send form-encoded input; ensure `$json.body` contains the expected fields. For this demo, the webhook is unauthenticated and **must remain local**.

```json
{
  "event_id": "EVENT-901",
  "lead_id": "LEAD-901",
  "name": "Taylor Smith",
  "email": "taylor@example.com",
  "phone": "+15550100901",
  "company": "Example Studio",
  "service": "CRM Automation",
  "budget": 2500,
  "timeline": "Within 30 days",
  "message": "We need automated lead routing.",
  "source": "website_form"
}
```

| Field | Required | Rules / meaning |
|---|---|---|
| `event_id` | Yes | 6–100 characters `[A-Za-z0-9_-]`, stable per submission/retry |
| `lead_id` | Recommended | Stable identity for logical lead; not used as the event deduplication key |
| `name` | Yes | Trimmed, minimum 2 characters |
| `email` | Yes | Trimmed, lowercased; basic syntax validation, not deliverability verification |
| `phone` | No | String, not fully normalized in this demo |
| `company` | No | String |
| `service` | Yes | Non-empty string |
| `budget` | No | Numeric or numeric string; must be non-negative when supplied |
| `timeline` | No | Free text |
| `message` | No | Free text treated as untrusted lead input |
| `source` | No | String such as `website_form`, `csv_import` |

**Notes:** The current validation code may impose fewer length and content restrictions than a public API would require. API consumers should not assume email ownership, user identity or authorization is verified. For reproducible real-world testing, add maximum-length and payload-size limits before production use.

## 2. Success — HTTP 200

Example: lead processed and CRM contact updated. Fields shown are the **expected contract for the configured workflow**, not a claim that every installation has identical response mappings.

```json
{
  "success": true,
  "duplicate": false,
  "message": "Lead processed successfully",
  "event_id": "EVENT-901",
  "lead_id": "LEAD-901",
  "email": "taylor@example.com",
  "qualification": {
    "score": 85,
    "status": "Qualified",
    "reasoning": "Illustrative model-generated reason",
    "recommended_action": "Schedule a discovery call",
    "requires_manual_review": false
  },
  "crm": {"provider": "HubSpot", "contact_id": "EXAMPLE_ID"}
}
```

AI scores and recommendation text are nondeterministic; no particular score is promised. In a public version, omit `reasoning` and internal CRM metadata from browser responses.

## 3. Duplicate submission — HTTP 200

```json
{
  "success": true,
  "duplicate": true,
  "message": "This submission was already processed",
  "event_id": "EVENT-901",
  "lead_id": "LEAD-901",
  "hubspot_id": "EXAMPLE_ID"
}
```

Semantics: an event with this ID was previously marked `completed`. The current demo does **not** guarantee this response under simultaneous requests or after partial database failures.

## 4. Validation failure — HTTP 400

```json
{
  "success": false,
  "error": "VALIDATION_FAILED",
  "message": "The submitted lead contains invalid data.",
  "lead_id": "LEAD-902",
  "details": ["Invalid email address", "Service is required"]
}
```

The current invalid-response node may not echo `event_id` or `email`; correlate with n8n execution history during testing. Never echo a full customer payload to public callers.

## 5. Event already processing — HTTP 409

```json
{
  "success": false,
  "error": "EVENT_IN_PROGRESS",
  "message": "This submission is already being processed",
  "event_id": "EVENT-901"
}
```

The client should not create a new event ID solely to evade this response. A future asynchronous API should provide a status endpoint and backoff guidance.

## 6. Downstream failure — HTTP 503 (configured failure branches)

Groq example:

```json
{
  "success": false,
  "error": "AI_SERVICE_FAILED",
  "message": "Lead processing could not be completed",
  "event_id": "EVENT-901",
  "retryable": true
}
```

HubSpot example uses `error: "CRM_SERVICE_FAILED"` and the message `CRM synchronization could not be completed`. Current demo errors are labeled retryable generically; clients must **not** assume 401/403/configuration failures can be fixed by repeated requests.

## 7. Other errors

An uncaught n8n exception, a failed Data Table write, or a request timeout may not return one of the neatly formatted response bodies above. The sender should preserve the original `event_id` and reconcile state before replaying. Request/response paths must be tested in the actual running version of n8n.

## 8. CSV import interface

The bulk workflow has a separate **n8n Form Trigger**, not a guaranteed stable public REST API. It accepts a CSV file with header columns:

```text
event_id,lead_id,name,email,phone,company,service,budget,timeline,message,source
```

Demo constraints: 100 rows maximum; sequential per-lead submission; event IDs should be stable and unique within each file. The importer invokes the main `POST /webhook/crm-new-lead` production endpoint. Per-row outcomes include successful, duplicate, rejected, in_progress, or failed.

CSV extraction must normalize BOM (`\uFEFF`) and whitespace from header names. Large or long-running imports need an asynchronous job/report API; synchronous calls may time out.

## 9. External integrations

**Groq** — `POST https://api.groq.com/openai/v1/chat/completions` with credential-managed Authorization header; body contains messages, model and structured-output specification. Parse `choices[0].message.content` as JSON, validate score and status separately.

**HubSpot** — Contact Create/Update through n8n native HubSpot node or CRM Contacts API. Lookup/upsert is keyed on normalized email. Custom property mapping uses the portal's actual internal names: `ai_lead_score`, `ai_qualification_status`, `requested_service`, `customer_budget`, `ai_qualification_reason`, `ai_recommended_action`, `lead_source` (verify these names).

## 10. Security, rate limits and idempotency

- This local API is **not authenticated**; never expose it on a public network without server-side protection, HTTPS, size/rate limits, abuse defenses, and consent/privacy controls.
- Never ship Groq/HubSpot secrets in frontend code or JSON exports.
- Source text can contain prompt-injection instructions; treat it only as untrusted data.
- Groq and HubSpot impose variable quotas. Implement bounded retries and respect returned rate-limit guidance.
- Event tracking is **best-effort sequential deduplication**, not atomic exactly-once delivery.
- Before production, document and implement privacy retention requirements, per-customer authorization, and an asynchronous status/retry design.
