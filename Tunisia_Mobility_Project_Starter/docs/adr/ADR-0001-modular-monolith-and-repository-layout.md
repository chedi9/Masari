# ADR-0001 — Modular monolith and repository layout

- **Status:** ACCEPTED
- **Date:** 3 November 2026
- **Owner approval:** APPROVED — the owner requested a modular structure and instructed us to work by it.
- **Context:** The product needs an Android-first Expo app, Python/FastAPI backend, spatial relational data, reproducible transport imports and room for future iOS. The Phase 0 gate requires feasibility evidence before full application coding.
- **Constraints:** Free tools/services only; no paid API or cloud resource. Preserve the confirmed stack. The owner later approved data-independent mobile coding with conspicuously labeled placeholders while Phase 0 research proceeds; real transport records, integrations, operational claims and production rollout remain behind the evidence/review gate.
- **Options considered:**
  1. Single repository with clearly bounded product modules and a single API deployment.
  2. Multiple repositories split by client, backend and data pipeline.
  3. Microservices split by product/domain capability.
- **Comparison:**

| Option | Fit | Cost / operations | Reversibility |
|---|---|---|---|
| One monorepo, modular monolith | Fits coordinated mobile/API/contracts/import changes and current team size | Lowest operational complexity; no added infrastructure | High; modules can later be extracted with evidence |
| Multiple repositories | Strong isolation but slower cross-cutting changes and duplicated setup | More maintenance overhead | Medium |
| Microservices | Independent deployment is possible | Adds network, deployment and monitoring burden before scale evidence; conflicts with near-zero cost goals | Lower |

- **Decision:** Use one repository with feature-based mobile modules, a single FastAPI modular monolith, isolated data-import/routing packages, explicit contracts and provider adapters. The exact tree and boundaries are in `docs/architecture/PROJECT_STRUCTURE.md`.
- **Consequences and risks:** Imports and module dependencies need enforcement through review/tests. Placeholder data must never be mistaken for service facts. Avoid premature abstractions and extraction; preserve the Phase 0 gate for production transport data and operational behavior.
- **Reversibility:** High. Repository folders can be moved and well-bounded modules extracted later.
- **Validation/prototype evidence:** Architectural choice is based on the owner-confirmed stack and SDD modular-monolith direction; implementation-level validation remains pending Phase 0.
