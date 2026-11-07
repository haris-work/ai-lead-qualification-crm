# Test Results and Acceptance Evidence — Project 01

**Important:** This is a **ready-to-complete test record**, not an assertion that an independent test suite has passed. The project was built iteratively in local n8n; the owner must attach the actual final run output/screenshots and fill every status before claiming acceptance.

**Tested by:** [Your name]  
**Run date/time:** [YYYY-MM-DD, local timezone]  
**n8n version:** [fill]  
**Groq model:** [fill]  
**HubSpot test portal ID:** [redacted or safe identifier]  
**Git commit SHA:** [fill]

## 1. Automated test run

From the project root (while the main workflow is published/active):

```powershell
python tests/test_crm.py
```

Paste the complete output or link to `tests/evidence/automated-test-output.txt` here. The proposed script checks HTTP 200 success, duplicate 200 handling, invalid-email HTTP 400 handling, a new event for the same customer, and consistency of returned HubSpot contact IDs. A 10/10 pass alone does not prove all external side effects occurred.

| Metric | Actual result |
|---|---|
| Assertions passed | [fill] |
| Assertions failed | [fill] |
| Run duration | [fill] |
| Exit code | [fill] |
| Unexpected errors | [fill] |

## 2. Acceptance test matrix

Use `PASS`, `FAIL`, `BLOCKED` or `NOT RUN`, plus evidence links. Never convert an untested scenario into a pass.

| ID | Scenario | Expected result | Actual status | Evidence |
|---|---|---|---|---|
| T01 | Valid first-time lead | 200, HubSpot contact exists, status completed | NOT RUN | [link] |
| T02 | Exact replay of completed event | 200 duplicate, Groq and HubSpot skipped | NOT RUN | [link] |
| T03 | New event, same email | Contact ID unchanged, relevant fields updated | NOT RUN | [link] |
| T04 | Invalid email | 400; Groq and HubSpot skipped | NOT RUN | [link] |
| T05 | Name too short | 400, clear error details | NOT RUN | [link] |
| T06 | Negative/non-numeric budget | 400, clear error details | NOT RUN | [link] |
| T07 | Missing service | 400, no CRM write | NOT RUN | [link] |
| T08 | Missing/invalid event ID | 400, no CRM write | NOT RUN | [link] |
| T09 | Unsupported Groq model | Failed status stored; HTTP 503 from configured branch | NOT RUN | [link] |
| T10 | Retry same previously failed event | Attempts increments; eventual completion after issue fixed | NOT RUN | [link] |
| T11 | HubSpot API/credential failure | Failed status captured; no false success | NOT RUN | [link] |
| T12 | First CSV import (5 rows) | Four processed, one rejected, full report | NOT RUN | [link] |
| T13 | Identical CSV re-upload | Four duplicate, one rejected; no repeat AI/CRM calls | NOT RUN | [link] |
| T14 | BOM-prefixed CSV header | Header normalized, `event_id` recognized | NOT RUN | [link] |
| T15 | Website valid submission | Confirmation, event record, HubSpot contact | NOT RUN | [link] |
| T16 | Website field validation | Invalid input blocked/clear message | NOT RUN | [link] |
| T17 | Website timeout/retry | Same event reused; outcome reconciled | NOT RUN | [link] |
| T18 | Restart n8n and inspect persisted Data Table | Existing event rows remain | NOT RUN | [link] |
| T19 | Simultaneous identical event submissions | At most one claim/process path (known gap) | BLOCKED | Atomic claim not yet implemented |
| T20 | Stale processing / interrupted execution | Recovery after CRM reconciliation (known gap) | BLOCKED | Recovery mechanism not yet implemented |
| T21 | HubSpot succeeded, event-state write failed | Reconciliation without harmful replay (known gap) | BLOCKED | Partial-success recovery not yet implemented |
| T22 | Older failed event retried after newer success | Must not overwrite newer CRM data (known gap) | BLOCKED | Event-order protection not yet implemented |
| T23 | Public webhook security | Auth, TLS, rate limiting and abuse protection | BLOCKED | Local-only demo |

## 3. Detailed evidence to capture

1. **n8n execution screenshots:** valid run, invalid run, duplicate run, Groq failure/recovery, HubSpot failure/recovery, CSV processing path.
2. **HubSpot:** record with contact ID (redact as necessary), AI score, status, requested service and budget; before/after changed inquiry.
3. **Data Table:** event_id, status, attempts and hubspot_id for test events; redact emails and error details if publishing.
4. **CSV:** first import results and second-upload duplicate result; reconcile totals with all 5 source rows.
5. **Website:** form screen, success/error notification, network response status (without API secrets).
6. **Automation:** exact Python test output, n8n version, and exported JSON workflow revision.

## 4. Example outcome calculation

For the provided sample file, the *expected* initial result (not a measured result) is 5 total, 4 processed, 1 rejected. Expected re-upload result is 4 duplicate, 1 rejected. API failures, stale events, or prior test data can change actual outcomes.

**Acceptance decision:** [NOT YET SIGNED OFF / ACCEPTED FOR LOCAL DEMO / ACCEPTED FOR PRODUCTION]

**Reason:** [write measured evidence and unresolved issues]

**Reviewer:** [name]  
**Date:** [YYYY-MM-DD]
