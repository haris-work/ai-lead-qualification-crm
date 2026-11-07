# AI Lead Qualification & HubSpot CRM Automation

A **client-brief-inspired, self-directed, zero-cost local demonstration** of AI lead processing with n8n, Groq and HubSpot test CRM. **Not a paid client case study and not production certified.**

## Features

- Individual lead intake by n8n webhook and local website form.
- Validation and normalization, HTTP 400 error response for invalid leads.
- Groq qualification with structured scoring and follow-up recommendations.
- HubSpot contact create/update using normalized email.
- Event tracking, duplicate suppression in sequential tests, and configured failure branches.
- Separate CSV importer with loop/batch processing and reporting.

## Architecture

```text
Local website / HTTP client ---> n8n single-lead webhook
                                      |
                             Validate + normalize
                                      |
                             Check event + record
                                      |
                                 Groq model
                                      |
                             Parse + score result
                                      |
                             HubSpot contact upsert
                                      |
                            Completion + HTTP reply

CSV upload form -> Extract CSV -> Prepare rows -> Loop -> webhook above
```

## Repository layout

```text
workflows/   actual n8n exports (add after verification)
website/     local lead capture frontend (add your tested index.html)
tests/       actual test script and fictional CSV sample (add after verification)
docs/        setup, API, test results, limitations, case study
```

## Getting started

Read [`docs/setup-guide.md`](docs/setup-guide.md). Use fictional data and your own developer credentials. Do not publish the local unauthenticated webhook to the public internet.

## Evidence

See [`docs/test-results.md`](docs/test-results.md) for the acceptance checklist and add actual evidence from your verified run. Read [`docs/known-limitations.md`](docs/known-limitations.md) before reuse.

## Disclaimer

This project demonstrates a use case found in freelance-marketplace job requirements. It is not claimed to be a client-delivered project, nor does it use client credentials or client data. All showcased data should be synthetic.
