# Setup Guide — AI Lead Qualification & HubSpot CRM Automation

**Project:** Project 01, client-brief-inspired demonstration  
**Status:** Local development implementation; not certified production-ready  
**Stack:** self-hosted n8n (Docker), Groq API, HubSpot developer test CRM, HTML/CSS/JavaScript, Python 3  
**Cost target:** No paid services for development; free-tier quotas and service availability apply.

## 1. Purpose and scope

The system receives individual leads from a website or HTTP client, validates them, obtains structured AI qualification from Groq, creates or updates a HubSpot contact, and tracks submission processing by event ID. A second workflow imports leads from CSV and calls the single-lead production webhook sequentially. The website is a local demonstration frontend, not a public deployment.

**Included:** input validation, lead scoring (0–100), qualification status, contact upsert, event tracking, HTTP success/error responses, retry and duplicate test paths, CSV importer, and local website.

**Not included as production guarantees:** atomic event claiming, guaranteed exactly-once processing, public endpoint security, real customer authorization/consent workflows, guaranteed timeout-free synchronous processing, mature audit/monitoring, or validated disaster recovery.

## 2. Requirements

- Windows/macOS/Linux with Docker and a running n8n Community Edition instance; examples use `http://localhost:5678`.
- Python 3 for the local website server and acceptance script.
- Groq API key with access to the configured model and enough free-tier quota.
- HubSpot developer test account and a credential that permits reading and writing contacts. The precise credential type depends on the current HubSpot/n8n versions.
- Existing exported n8n workflows: `workflows/crm-main-workflow.json` and `workflows/crm-csv-importer.json`. **These must be exported from the actual tested instance; this repository does not assume exports have been provided.**
- A HubSpot test portal with seven custom *contact* properties (table below).

Record actual n8n, node, Docker, Groq model, and HubSpot configuration versions before handing the project to a client.

## 3. HubSpot setup

1. Open the intended **developer test CRM account** and confirm its portal/account ID. Do not accidentally connect a real production portal.
2. In Settings → Properties, select **Contact** and create properties with these suggested internal names. Verify the *actual internal names* after creation: labels and internal names are not interchangeable.

| Label | Suggested internal name | Type |
|---|---|---|
| AI Lead Score | `ai_lead_score` | Number |
| AI Qualification Status | `ai_qualification_status` | Single-line text |
| Requested Service | `requested_service` | Single-line text |
| Customer Budget | `customer_budget` | Number |
| AI Qualification Reason | `ai_qualification_reason` | Multi-line text |
| AI Recommended Action | `ai_recommended_action` | Multi-line text |
| Lead Source | `lead_source` | Single-line text |

3. Create/authorize an appropriate server-to-server HubSpot credential with least-privilege contact read/write access. Property-schema discovery may require additional read permission depending on the authentication method.
4. In n8n, configure the HubSpot node credential for that *specific test portal*. Use Contact → Create or Update with email as the identity key. Map first name, last name, phone, and any supported custom fields. If the native node does not expose custom fields, use the HubSpot CRM Contacts API with the actual internal names.
5. Search the CRM test portal for the fictional test contact after a run. Verify properties from the contact's full property view; do not infer success merely from an HTTP 200.

## 4. Groq setup

1. Generate a Groq API key in Groq Console. Store it in an n8n credential, **not** in a Code node, webpage, or checked-in workflow JSON.
2. Configure the Groq HTTP Request node to POST to `https://api.groq.com/openai/v1/chat/completions` with Authorization header `Bearer <secret>`.
3. Use the compatible model configured for the project (previous tests used `openai/gpt-oss-20b`; check availability and output-format support before future runs).
4. Submit the lead as a user message, include a fixed qualification rubric in the system message, and request an object containing `score`, `status`, `reasoning`, and `recommended_action`.
5. The subsequent Code node parses `choices[0].message.content`, validates score as an integer between 0 and 100, and derives status by thresholds: `0–39 Not Qualified`, `40–69 Needs Review`, `70–100 Qualified`.
6. Treat returned reasoning and recommended actions as model-generated content requiring scrutiny. Empty/malformed output must be flagged for human review, not silently labeled low-quality.

## 5. Event tracking Data Table

Create an n8n Data Table named `crm_lead_events` with columns below, matching the types available in your installation:

| Column | Type | Notes |
|---|---|---|
| `event_id` | String | Submission ID used for deduplication |
| `lead_id` | String | Customer/inquiry identifier; not an event identifier |
| `email` | String | Normalized customer email |
| `status` | String | `processing`, `completed`, `failed` |
| `attempts` | Number | Number of processing attempts |
| `hubspot_id` | String | CRM contact ID, if known |
| `last_error` | String | Internal failure detail; may contain sensitive data |
| `updated_at` | Date | Last state update |

**Important:** Lookup followed by upsert is not atomic. Do not advertise this table as a concurrency-safe exactly-once queue.

## 6. Import the main n8n workflow

1. Start Docker Desktop and the existing n8n container; open `http://localhost:5678`.
2. Import the **actual exported** `crm-main-workflow.json` into n8n. Reconnect credentials for Groq, HubSpot, and Data Tables as appropriate.
3. Inspect all nodes before executing. The intended path is:

   `Webhook → Validate and Normalize Lead → IF(valid) → event lookup/decision → register processing → Groq → parse result → HubSpot upsert → mark completed → Respond to Webhook`.

4. Invalid submissions go through a validation-error response (HTTP 400). Completed event replays return a duplicate response (HTTP 200). In-progress events return a conflict response (HTTP 409). Configured API failure branches persist failed status and return HTTP 503 for the demo.
5. Webhook: POST path `crm-new-lead`, **Respond using Respond to Webhook Node**.
6. Test listener URL: `http://localhost:5678/webhook-test/crm-new-lead` (listen once before a test). Production URL: `http://localhost:5678/webhook/crm-new-lead` (requires published/active workflow).
7. Confirm every branch terminates with a response and no branch can erroneously claim success after an API failure.

## 7. Import the CSV workflow

1. Import `crm-csv-importer.json`, and reconnect the Form Trigger, Extract From File, Data Table (if used), and HTTP Request nodes.
2. Form Trigger accepts one CSV file. Verify the actual file binary field name from the trigger output.
3. Extract From File converts the CSV into one item per row. Header cleanup should remove UTF-8 BOM (`\uFEFF`) and whitespace in keys. A real test encountered a leading-BOM `event_id` header.
4. Prepare CSV Leads checks required columns, normalizes values, ensures unique non-empty `event_id`s in the file, and caps the demo batch at 100 rows.
5. Loop Over Items uses batch size 1. The HTTP Request posts each lead to the **production** URL of the main workflow; the final Wait node loops back to Loop Over Items. Done output triggers summary generation.
6. Configure HTTP response status/body capture and continue on per-row HTTP rejection. Re-upload the same file to test replay handling.
7. **Verify the actual Done output counts every row correctly.** If it doesn't, persist one result per row and aggregate from that store. A green workflow execution is not proof of accurate summary counts.

## 8. Local website

1. Place `website/index.html` in the project website directory. Serve it locally: `python -m http.server 5500`.
2. Open `http://localhost:5500` in a browser. Ensure your webpage posts to the correct webhook URL; changing a domain or port requires updating configuration.
3. If website origin differs from n8n, configure CORS carefully. CORS is **not security/authentication**.
4. Submit a fictional test lead, verify the n8n execution history, and inspect HubSpot's resulting contact and event-tracking row.
5. Do **not** publish an unauthenticated localhost test webhook on a public endpoint. The browser must never contain private Groq/HubSpot keys.

## 9. Run acceptance tests

Ensure the main workflow is published. Run `python tests/test_crm.py` if that file is included in your working project. It makes calls to the **production** webhook and uses fictional test contacts. Capture its console result and then manually verify the HubSpot and Data Table side effects. More detail: `docs/test-results.md`.

## 10. Handover / troubleshooting

- **JSON Body invalid:** In a JSON-expression field, confirm the expression evaluates to a valid JSON string; some node versions display `[object Object]` for a plain object.
- **Custom properties missing in n8n:** Check nested Custom Properties selector, portal identity, credential permissions, or use HubSpot CRM API with verified internal names.
- **Webhook test URL fails:** Start listening again; test registration is temporary. Production URL requires published workflow.
- **CSV missing `event_id`:** Strip leading BOM and whitespace from column names, then re-run.
- **Groq 429 or 5xx:** Review quota and rate limits; use bounded retries. Do not expose error payloads to users.
- **HubSpot contact absent despite HTTP 200:** Verify portal ID, workflow run, real HubSpot response and contact search, and check for swallowed failures.
- **Event stuck `processing`:** Reconcile with HubSpot before retrying; see `known-limitations.md`.

## 11. Safe delivery checklist

- Export actual validated workflows; redact embedded secrets and private/synthetic-only tokens.
- Remove real personal data from test logs and screenshots.
- Include internal-name mappings, required credential scopes, Docker/n8n versions, and any nondefault settings.
- Provide test outcome evidence, known limitations, and an explicit statement of whether the deliverable is a local demo or production deployment.
