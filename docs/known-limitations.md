# Known Limitations, Risks and Production Roadmap

**Release classification:** Local zero-cost learning/demo implementation based on a real marketplace brief; not yet a hardened public service.

## Severity key

- **Critical:** do not deploy publicly before mitigation.
- **High:** must be resolved before claiming reliable production operation.
- **Medium:** acceptable for constrained local demonstration if documented and monitored.

| ID | Severity | Limitation | Consequence | Required improvement |
|---|---|---|---|---|
| L01 | Critical | Public webhook currently unauthenticated | Anyone could submit/abuse requests | Server-side authentication, TLS, rate limiting, bot/abuse protection |
| L02 | High | Data Table lookup and upsert are separate operations | Concurrent duplicate events can both be processed | PostgreSQL unique `event_id` and atomic claim/transaction |
| L03 | High | No complete recovery of stale `processing` events | Docker restart may leave permanently stuck events | Lease/expiry, reconciliation worker and safe retry state machine |
| L04 | High | HubSpot succeeds but completion record fails | Partial success can replay an already-applied action | Persistent outbox/inbox records, CRM reconciliation, idempotent writes |
| L05 | High | Old failed event may replay after newer success | Stale data overwrites latest contact fields | Event timestamps/versions and ordered/conflict-aware updates |
| L06 | High | Long synchronous webhook + AI + CRM work | Client/importer timeouts despite downstream success | Queue jobs, immediate 202 acknowledgment, job-status endpoint |
| L07 | High | Test/development webhook and production behavior may differ | Incorrect assumptions about activation, CORS, response | Validate deployed URL and every response branch |
| L08 | High | Generic API retries treat some permanent errors as transient | Wasted quota, false retryable responses | Inspect HTTP codes: 429/5xx retry, 4xx config/input failure requires action; respect Retry-After |
| L09 | High | Free-tier quotas and service changes | Throttling, 429 errors or unavailable models | Quota observability, configurable model, backoff, queue controls |
| L10 | High | Lead submission includes personal data | Privacy, disclosure, retention risks | Consent, minimization, retention policy, encryption/access limits |
| L11 | High | Source lead text is untrusted | Prompt injection attempts and improper tool suggestions | Prompt isolation, strict schemas, deterministic validation and review |
| L12 | Medium | Basic email regex does not verify mailbox ownership | Undeliverable/impersonated leads accepted | Verification/consent workflow if needed |
| L13 | Medium | Name/phone/company formatting rudimentary | Poor CRM data quality | E.164 phone normalization, length bounds, standardized company rules |
| L14 | Medium | AI scoring is heuristic, not calibrated | Scoring differences and inconsistent business value | Versioned rubric, labeled evaluation set, model comparison, manual review |
| L15 | Medium | AI output may be inconsistent/malformed | Misrouting of leads | Schema validation, explicit uncertainty handling, evaluation tests |
| L16 | Medium | CSV file has 100-row demo limit | Large files rejected | Asynchronous bulk import, resumable chunks, durable checkpoints |
| L17 | Medium | CSV `event_id` supplied by file | Bad/missing IDs or cross-batch collisions | Import batch ID + stable external source ID, uniqueness policy |
| L18 | Medium | Import result correlation incomplete for some errors | Missing email/row identification in report | Carry row index/event ID through error path and persist each outcome |
| L19 | Medium | Loop Done summary depends on returned items | Incorrect totals if loop output shape differs | Persist per-row outcomes, aggregate from database, reconcile to input count |
| L20 | Medium | Website demo requires local n8n and local server | Public visitors cannot use it | Deploy separate hardened backend/API and static frontend after security review |
| L21 | Medium | n8n Data Tables have size/capability constraints | Growth and query/locking limitations | PostgreSQL for durable event/status storage |
| L22 | Medium | Workflow export may include environment assumptions | Cannot directly reproduce on another n8n installation | Version pinning, env/credential setup guide, migration checklist |
| L23 | Medium | No validated backup/restore drills | Data or automation state could be lost | Scheduled backup and restore test |
| L24 | Medium | No mature notifications/alert dashboard | Failures go unnoticed | Centralized structured logs, alerting, failure queue, metrics |
| L25 | Medium | AI recommendation may expose internal context to caller | Unnecessary data disclosure | Public response minimization; admin-only qualification details |

## Release gates

### Local demo release

- Verify core individual-lead, duplicate, invalid, CSV, and website tests using only fictional data.
- Keep services bound to local development or restricted trusted networks.
- Do not publish credentials or identifiable real test customer data.
- State all unimplemented features honestly.

### Limited supervised pilot (future)

- Replace unprotected webhook with authenticated backend entry point.
- Persist events in PostgreSQL with atomic uniqueness and transaction-aware claims.
- Implement recovery and partial-success reconciliation.
- Add rate-limit-aware retry policy and a queue or asynchronous job status.
- Restrict employee/customer data access and define consent/retention.
- Log and alert on failed/repeated requests; test backups and restores.

### Production release (future)

- Perform concurrent load/idempotency testing, security review, dependency patching and rollback drill.
- Document operational SLOs, incident contacts, on-call process, usage costs and quotas.
- Confirm data protection obligations for client locale and sector.
- Obtain explicit client approval for business rules and AI qualification behavior.

## Workarounds for current learning environment

For sequential local tests, the Data Table tracking can demonstrate repeat-event suppression. If it encounters an ambiguous state, **stop and reconcile** in HubSpot/Data Tables instead of generating a new `event_id`. This is safer than claiming that retries are exactly-once.

No production uptime, revenue uplift, conversion lift, cost savings, or completed-client outcome should be claimed without independent measurement.
