# Portfolio Case Study — AI Lead Qualification and CRM Automation

**Project type:** Self-directed implementation based on publicly advertised client requirements; **not a paid client engagement**.  
**Environment:** Local development and HubSpot developer test portal.  
**Core tools:** n8n, Groq API, HubSpot CRM, JavaScript, Python, Docker, HTML/CSS, CSV.

## Problem

Small service businesses receive leads through website forms and CSV lists. Reviewing them manually, qualifying their fit and keeping CRM records updated can become repetitive and error-prone. The challenge is to automate intake, standardize the data, obtain a structured lead qualification assessment and maintain a CRM record with traceable outcomes.

## Solution

I built a modular workflow that receives individual inquiries through a webhook and a browser form, validates lead details, sends valid leads to an AI qualification step, creates or updates contacts in HubSpot, and records event processing states. A separate CSV workflow imports sample records sequentially and collects results. The workflow includes validation-error responses and duplicate-event suppression for sequential test submissions.

## Scope and demonstration

- Local website form → n8n webhook → validation → Groq qualification → HubSpot contact.
- CSV Form Trigger → CSV extraction → normalized rows → per-row CRM submission.
- Qualification outputs: score (0–100), `Qualified`, `Needs Review`, or `Not Qualified`, reasoning and next action.
- Repeat submission identified by stable `event_id`; HubSpot contact updated based on normalized email.
- Error branches and state tracking for demonstrative recovery behavior.

## Testing and evidence

Use only measurements from a final verified run. Add screenshots/video of: first new lead, valid qualification JSON, HubSpot test record, duplicate replay skipping downstream nodes, invalid request HTTP 400, CSV results, and website success screen. Link to `docs/test-results.md` when populated.

**Observed metrics:** [Fill after verified testing. Do not invent time savings, ROI, throughput or conversion results.]

## Constraints and future improvements

This is a local reference build, not a publicly deployed commercial service. For production, add authentication, concurrency-safe atomic event claiming, stale-event recovery, CRM reconciliation, asynchronous queues, rate-limited retries and explicit privacy controls. See `docs/known-limitations.md`.

## Links

- GitHub source: [add after publishing and security review]
- Demo video: [add after recording]
- Portfolio case-study page: [add after publishing]

**Role:** End-to-end workflow design, integration, implementation and testing of the demo.
