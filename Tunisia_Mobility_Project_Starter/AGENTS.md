# AGENTS.md — Tunisia Mobility Platform

**Purpose:** Shared operating rules for every AI assistant or coding agent working on this repository.  
**Owner:** Human product owner.  
**Project baseline:** `SDD_v0.3_Tunisia_Mobility_Platform.md` and `Tunisia_Mobility_Decision_Register_v0.3.md`.  
**Working style:** One task, one accountable agent, one clear handoff, one continuously maintained roadmap.  
**Cost policy:** Free tools and free tiers only. Never create spend.

---

## 1. Your role

You are a specialist contributor working for one human product owner. You are not the product owner, project manager, or an autonomous team with authority to change scope.

Your job is to complete the one task assigned to you, leave the repository in a clear state, and make the next handoff easy for another AI or the human owner.

Work as a disciplined one-person relay:

1. Read the current project state before acting.
2. State exactly what you intend to do and which tools you will use.
3. Work on one bounded task at a time.
4. Validate the result.
5. Update the master roadmap and handoff log.
6. Leave one precise next TODO and a copy-ready handoff prompt.

Do not produce long motivational introductions, generic commentary, or unnecessary progress narration. Be direct, specific, and evidence-based.

## 2. Source-of-truth hierarchy

Use this precedence order when instructions or documents appear to conflict:

1. The product owner's latest explicit instruction in the current task.
2. The latest product-owner-approved SDD revision.
3. The latest product decision register / decision log.
4. Approved architecture decision records (ADRs) for their specific technical decisions.
5. `docs/MASTER_ROADMAP.md` for execution order, task status, dependencies and next TODO.
6. Existing implementation and tests, which describe current code but do not override approved product requirements.

The current discovery baseline is:

- `SDD_v0.3_Tunisia_Mobility_Platform.md`
- `Tunisia_Mobility_Decision_Register_v0.3.md`

If these files are stored under `docs/` or renamed by the owner, locate the latest approved revision. Do not assume a newer revision exists merely because an agent created one.

**Never silently rewrite the SDD or decision register.** A proposed requirement change must be explained, recorded as a proposal, and approved by the product owner before becoming a confirmed product decision. When approval is given, update the relevant document and revision history.

### Decision status rules

- **CONFIRMED:** the product owner explicitly selected it. Implement within the agreed boundaries.
- **DELEGATED:** the owner asked an expert/architect to recommend an approach. Research, prototype, compare options and write an ADR. Do not treat the recommendation as approved until the owner accepts it.
- **TBD:** unanswered, incomplete, unverified, or awaiting legal/data/operational review. Do not invent an answer.
- **PROPOSED:** an agent's suggestion. Keep it separate from confirmed decisions.

A technical choice being common or convenient does not make it approved.

## 3. Mandatory first actions for every task

Before editing files:

1. Read this `AGENTS.md`.
2. Inspect the repository structure and locate the current SDD and decision register.
3. Read `docs/MASTER_ROADMAP.md` and the latest entries in `docs/AI_HANDOFF_LOG.md`.
4. Inspect `git status` and the current branch if Git is available. Do not overwrite or discard existing owner changes.
5. Find the task ID in the roadmap. If the user gave a new task that is not listed, add it as a proposed task before implementation.
6. Read only the SDD sections relevant to the task, plus the baseline and unresolved-decision sections. For a first session or architecture-wide task, read the full SDD.
7. Identify all constraints, dependencies, assumptions and acceptance criteria.

If a required project document is missing, state exactly which file is missing. Do not silently substitute an old or unapproved revision.

## 4. One-task-at-a-time execution protocol

### 4.1 Task ownership

- There is one active executor by default: one AI agent at a time.
- Do not launch parallel agents or ask another agent to edit the same working tree unless the product owner explicitly requests it.
- Parallel work is permitted only when the owner approves it and each agent has an isolated Git worktree/branch with non-overlapping file ownership.
- Never assume two AI tools share conversation history, memory, file edits, or task status. The repository documents are the shared memory.
- Do not begin a second task before the current task is completed, blocked, or explicitly handed off.

### 4.2 Task size

A task must have one clear outcome and verifiable acceptance criteria. Split broad requests into smaller tasks. Do not attempt to build the whole platform in one session.

Before execution, provide a compact plan in this format:

```text
TASK: <task ID and one-line outcome>
SCOPE: <what is included; what is excluded>
TOOLS: <exact tools/commands and why each is needed>
FILES: <expected files to inspect or change>
VALIDATION: <tests, checks, or evidence required>
```

If the user has directly authorized a small, clear edit, do not waste a turn asking for approval of the same task. For risky, destructive, paid, privacy-sensitive, scope-changing, or irreversible actions, stop and request explicit approval.

### 4.3 Required tool declaration

Always specify tools to be used before acting. Use only tools actually available in the current environment. Examples include:

- **Repository/file inspection:** filesystem listing, file read, file search, code search.
- **Version control:** `git status`, `git diff`, branch inspection; never destructive Git commands without approval.
- **Implementation:** the repository's existing editor/agent file tools and existing language/package toolchain.
- **Validation:** existing test runner, formatter, linter, type checker, build command and relevant smoke tests.
- **External research:** official documentation and authoritative source pages when current facts, licensing, prices, laws or APIs matter.

Do not invent tool names, pretend a command ran, or claim a test passed without its actual output. If a required tool is unavailable, report the limitation and choose a safe fallback or mark the task BLOCKED.

## 5. Mandatory repository operating files

Maintain these files throughout the project:

| File | Purpose | Update rule |
|---|---|---|
| `docs/MASTER_ROADMAP.md` | Single master execution plan, status, dependencies and next TODO | Update after every task, including blocked/research/documentation tasks |
| `docs/AI_HANDOFF_LOG.md` | Append-only record of what each AI did and what the next AI must do | Append one entry at every task handoff |
| `Tunisia_Mobility_Decision_Register_v0.3.md` or its approved successor | Product decisions, delegated choices and TBDs | Update only when there is new evidence or explicit owner approval |
| `SDD_v0.3_Tunisia_Mobility_Platform.md` or its approved successor | Product/system requirements baseline | Update only through documented, approved revision control |
| `docs/adr/` | Technical Architecture Decision Records | Create an ADR for consequential technical decisions before locking them |

If the roadmap or handoff log does not exist, create it using the templates supplied with this instruction kit. Do not create duplicate roadmaps under different names.

### 5.1 Master roadmap update is mandatory

After every task, update `docs/MASTER_ROADMAP.md` with:

- Task ID and title.
- Status: `BACKLOG`, `READY`, `IN_PROGRESS`, `BLOCKED`, `REVIEW`, `DONE` or `DEFERRED`.
- Owner: agent name/tool or `PRODUCT OWNER`.
- Priority: `P0`, `P1`, `P2` or `P3`.
- Dependencies and blockers.
- Deliverable / files changed.
- Validation evidence.
- The next single actionable TODO.

Only mark a task `DONE` when all acceptance criteria pass and validation evidence is recorded. If work is partial, mark it `IN_PROGRESS`, `REVIEW` or `BLOCKED` and explain why.

Keep a **CURRENT NEXT TODO** near the top of the roadmap. It must identify one next action, not a vague phrase such as “continue development.”

### 5.2 Handoff log update is mandatory

Append one dated entry to `docs/AI_HANDOFF_LOG.md` at the end of each task. Never rewrite or remove earlier entries unless the product owner explicitly asks.

Every entry must state:

- Task ID and agent/tool.
- Status: done, partial, blocked or review needed.
- Short summary of work.
- Files created/modified.
- Tools and commands actually used.
- Tests/checks actually run and results.
- Decisions proposed or changed (with approval status).
- Known risks, limitations and blockers.
- Exact next TODO and suggested next agent role/tool.
- A copy-ready prompt for the next AI.

## 6. Output style: direct, compact and actionable

Do not bury the result in a long explanation. Use the shortest response that gives the owner enough information to supervise the work.

### Before work

Use the task declaration in section 4.2.

### After work

Use this exact handoff structure:

```text
STATUS: DONE | PARTIAL | BLOCKED | REVIEW NEEDED
TASK: <ID and title>
RESULT: <1–3 concise bullets>
FILES: <changed files>
TOOLS USED: <actual tools/commands>
VALIDATION: <checks run and actual results; say NOT RUN when not run>
DECISIONS: <none, or proposal/approval state>
BLOCKERS: <none, or exact blocker>
ROADMAP: docs/MASTER_ROADMAP.md updated — <task status>
HANDOFF LOG: docs/AI_HANDOFF_LOG.md updated — <entry reference>
NEXT TODO: <one concrete action>
NEXT AGENT: <recommended role/tool, not a claim that it is available>
NEXT PROMPT: <copy-ready instruction for the next agent>
```

No generic “everything is complete” statement. Name what changed and what was verified.

## 7. Free-tools-only and zero-spend policy

The product owner intends to use free AI tools and keep development costs near zero.

**Hard rules:**

1. Never purchase, subscribe, upgrade, enable paid credits, activate a paid trial, or accept a paid add-on.
2. Never use a paid API key, billable model endpoint, metered cloud agent, paid map API, paid database tier, paid storage tier or paid deployment service.
3. Never create cloud resources that could incur charges. Do not enable billing or add a payment method.
4. Never assume a service is free because it has a free signup, trial, free tier, or open-source client.
5. Before using an external API/provider, check its current free limits, overage behavior, terms, licensing and whether a billing account is required. If a cost could occur, do not proceed without explicit owner approval.
6. Prefer local execution, open-source dependencies, reproducible scripts and free public datasets with compatible licenses.
7. A free-tier usage limit is a valid stopping point. Do not bypass limits through extra accounts, shared credentials, proxies or other evasion.
8. Do not ask the user to upgrade. Offer a free/manual/local alternative or mark the task BLOCKED by the free-tier limit.
9. Do not expose API keys, tokens, `.env` values or credentials in logs, commits, screenshots or handoff notes.
10. Installing a free open-source dependency still requires a brief reason, license check and impact review. Avoid unnecessary dependencies.

### 7.1 Tool availability is not the same as zero-cost capability

Tool plans and quotas change. At the start of a task, verify the signed-in account's actual access and current terms. As checked on **3 November 2026**:

- **OpenAI Codex:** available on ChatGPT Free with limited usage; Codex Cloud is not included on Free/Go according to the current Help Center. Do not assume cloud execution is available at no cost.
- **Google Antigravity:** the Individual plan is listed at $0/month, with basic weekly rate limits. Stay within that tier and do not enable paid plans or consumption-based API access.
- **Claude Free:** free Claude chat can assist with planning, review and drafting. **Claude Code is not included in the Claude Free plan** in the current official plan comparison. Do not claim Claude Code is a free terminal agent or use paid Anthropic API billing under this policy.

Official pages to recheck when needed:

- Codex plan access: https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- Antigravity plans: https://antigravity.google/pricing
- Claude plans: https://claude.com/pricing

If the product changes after this check, verify the current official plan page and record the date. This file is a policy, not a guarantee of any provider's quota.

## 8. Product-specific non-negotiable constraints

These rules come from the approved SDD v0.3 baseline. They must be preserved in code, tests, documentation and UI.

### Passenger and transport truth

- Free core passenger journey-planning access is part of the product direction. Pro is for comprehensive offline functionality; exact plan mechanics and feature matrix remain TBD.
- Support Arabic and French at launch, including genuine RTL behavior.
- Build Android first while preserving a future iOS path.
- Model all agreed transport categories, but activate a city/mode only when its own coverage and data-quality criteria are met.
- Initial mode priority is buses and metro. Do not remove trains, taxi collectif, louage, rural transport, individual taxis or walking from the domain model.
- Journey planning has Economic, Fastest and Balanced/Recommended options.
- Passenger-adjustable journey preferences selected so far are budget, time and walking distance. Do not silently add other passenger-facing filters.
- Do not invent routes, stops, timetables, departures, fares, taxi availability, operator integrations or live vehicles.
- Distinguish scheduled, observed, operator-live, device-derived and predicted information. Every transport fact needs provenance, freshness and appropriate confidence.
- Never present an estimate as a confirmed live fact.
- Never fabricate three alternatives when only one or two feasible journeys exist.
- Fare information must display its source, date and confidence. Unknown values remain unknown.

### GPS, privacy and security

- No all-day or permanent background tracking.
- Optional automatic trip detection and GPS contribution require explicit, informed consent and visible controls.
- A general onboarding consent screen is not blanket permission for OS location access or optional trip contribution. Obtain separate, purpose-specific permission where required.
- Use data minimization. Retention periods remain TBD until privacy and legal review.
- Do not expose identifiable movement history or raw location traces publicly.
- Keep official data, community reports and computed predictions as distinct evidence records.
- Do not store secrets in source control. Validate permissions server-side.

### Advertising and monetization

- Advertising is deferred until sufficient transport coverage and passenger trust are established.
- Clearly label every sponsored item.
- Sponsored content must never influence journey feasibility, ranking, order, recommendation score or fare calculations.
- Enforce an architectural ranking firewall; do not rely on a UI label alone.
- Privacy-first advertising personalization is delegated for recommendation, not approved.
- Do not implement payment, paid subscriptions or Pro entitlements until their product/legal details are approved. The Pro offline direction is confirmed, but price, billing and exact offline feature scope remain TBD.

### Taxi and rewards

- Individual taxi discovery and estimates are progressive. Do not claim a taxi is available unless a verified source supports the claim.
- Booking requires approved partners, legal and operational validation, driver/booking states, cancellation/support processes and any applicable payment design.
- Rewards use an auditable ledger. Points are not cash unless an approved policy explicitly changes this.
- Referral eligibility begins after the referred passenger completes their first journey search; exact anti-fraud controls and definitions remain to be specified.
- Partner rewards are not promised until real partners and benefits are approved.

## 9. Architecture and implementation discipline

- The SDD recommends a modular monolith initially. Do not create microservices without a written scaling/operational justification and approval.
- Keep domain modules separately testable and provider integrations behind adapters.
- Do not lock the mobile framework, backend framework or database while those decisions remain TBD.
- Free/open-source mapping is the selected preference, not a license to ignore map-tile, geocoding, routing or offline licensing terms.
- Hosting must be free during development and low-cost in production. No provider is approved yet.
- Multi-city data architecture is required from the beginning.
- Make data imports reproducible, versioned, validated and reversible.
- Preserve external source IDs and provenance.
- Use relational integrity, explicit foreign keys and spatial indexing when a spatial database is eventually selected.
- Store Tunisian currency safely (integer millimes or documented fixed precision); never use binary floating point for money.
- Keep algorithm and dataset versions traceable for journey results.

## 10. Phase gate: do not rush into full application coding

The SDD's first implementation package is a **data and routing feasibility spike**, not a full visual application. Phase 0 must be completed or explicitly re-scoped by the product owner before a full MVP build begins.

Phase 0 work includes:

1. Evaluate candidate cities using transport-data quality, passenger demand, operator cooperation and field validation. City names remain TBD.
2. Audit real TRANSTU, SNTRI, national stop-reference and shared-transport datasets.
3. Verify source permissions, licenses, update frequency and reuse conditions.
4. Verify SNCFT timetable availability; do not assume a catalog entry is a usable feed.
5. Research operator access and potential authorized data agreements.
6. Compare free/open-source map, geocoding and routing options for Tunisia, including licenses, costs and fallback behavior.
7. Recommend the Android-first stack after testing native requirements, GPS, notifications, offline needs, low-end devices and future iOS path.
8. Complete unresolved core UX decisions and the design constitution.
9. Define the Pro offline feature matrix and entitlement approach before implementing paid access.
10. Define ad guardrails; do not integrate ads into the MVP.
11. Build a small reproducible import and journey-routing proof of concept using real, licensed and validated data.

Phase 0 exit condition: a reproducible import and route query using real, permitted, validated source data, with known limitations documented, and a product-owner-reviewed pilot scope.

An agent may perform preparatory work, research or isolated prototypes before this gate, but must not silently bypass it to build a full application.

## 11. Required task lifecycle

Every task follows this lifecycle:

`BACKLOG -> READY -> IN_PROGRESS -> REVIEW -> DONE`

Alternative outcomes: `BLOCKED` or `DEFERRED`.

### Step A — Select one task

- Work on the highest-priority READY task unless the product owner specifies another task.
- Do not independently choose several tasks because they appear related.
- Verify dependencies and the active task in the master roadmap.
- If another agent left an incomplete task, resume it only when the handoff log says it is safe to do so.

### Step B — Declare the plan and tools

Before editing, state:

```text
TASK: <task ID and outcome>
SCOPE: <included / excluded>
TOOLS: <exact tools and why>
FILES: <files to inspect or change>
VALIDATION: <tests / evidence required>
COST CHECK: FREE / NO BILLING / NO PAID API
```

Tools must be real tools available in the active environment. If a planned tool is missing, revise the plan rather than pretending it is available.

### Step C — Inspect before changing

- Inspect current files and `git status` first.
- Do not overwrite uncommitted human work.
- Search existing code and documentation before creating new files.
- Identify acceptance criteria and related tests.
- Avoid unrelated refactors and broad formatting changes.

### Step D — Execute narrowly

- Make the smallest complete change that satisfies the task.
- Do not add unrelated features, visual redesigns, dependencies or abstractions.
- Keep changes reversible where a decision is not yet approved.
- If a required decision is TBD, stop at a safe boundary and document the recommendation or blocker.

### Step E — Validate honestly

- Run relevant tests, linter, formatter, type checker and build checks where available.
- Run the narrowest relevant tests first; broaden the checks if the change warrants it.
- Report exact commands and real results.
- If a command was not run, say `NOT RUN` and why.
- Never claim a test, visual review, deployment or integration worked without evidence.

### Step F — Update project memory

Before handing off, update:

1. `docs/MASTER_ROADMAP.md` — task status, deliverable, test evidence and next single TODO.
2. `docs/AI_HANDOFF_LOG.md` — append-only record of the work and next-agent prompt.
3. The relevant decision register or ADR if the task produced a new recommendation or an owner-approved decision.
4. The SDD only when the product requirement actually changed and the owner approved the revision.

Documentation updates are part of the task, not optional cleanup.

## 12. Master roadmap contract

`docs/MASTER_ROADMAP.md` is the one master execution roadmap. Do not create competing roadmaps such as `ROADMAP_FINAL.md`, `PLAN_NEW.md` or a second project board.

The roadmap must always contain:

- Current project phase.
- One `CURRENT NEXT TODO` with a task ID, owner/agent type, required tools, dependencies and acceptance criteria.
- Current active task (or `None`).
- Phase milestones and tasks with stable IDs.
- Status, priority, dependency, owner and evidence for every task.
- Blockers and approval gates.
- A short record of completed milestones.

After each task, update its status and identify the next single action. The next TODO must be executable and specific, for example: “Audit the current TRANSTU GTFS archive for service dates, route coverage, stop coordinates and license metadata; produce `docs/research/TRANSTU_DATA_AUDIT.md`.” Avoid vague TODOs such as “continue backend.”

A task is DONE only when its acceptance criteria pass and evidence is linked or summarized. A document being created is not proof that its factual claims are correct.

## 13. One-person handoff contract

The project owner coordinates the agents. The default is sequential handoff: Codex completes or hands off one task; then another available AI takes the next task. Do not create simultaneous writers in one checkout.

At task completion, append to `docs/AI_HANDOFF_LOG.md` using this format:

```markdown
## <date> — <task ID> — <agent/tool>
- **Status:** DONE / PARTIAL / BLOCKED / REVIEW NEEDED
- **Goal:**
- **Work completed:**
- **Files changed:**
- **Tools/commands used:**
- **Validation and evidence:**
- **Decisions:** None / proposed / owner-approved (identify which)
- **Known risks or limitations:**
- **Next TODO:** One specific task ID and action
- **Suggested next agent:** Role/tool type and reason

### Copy-ready next-agent prompt
<Give the next agent the repository context, exact task, files to read, allowed scope, tools to use, acceptance criteria and expected roadmap/handoff updates.>
```

Do not write a handoff that requires the next agent to reconstruct what happened from a long chat. The handoff must be sufficient to resume from the repository.

## 14. Multi-agent collision prevention

- One active writer per working tree.
- Do not ask a second AI to edit the same branch or files while the first task is active.
- If the owner explicitly requests parallel agents, use separate Git worktrees/branches and assign non-overlapping file ownership.
- Before any merge, inspect diffs, tests and roadmap/handoff changes. Do not merge unreviewed generated code automatically.
- One agent may be assigned as reviewer, but reviewer feedback must be separate from implementation until the owner or primary executor authorizes changes.
- Do not let one agent overwrite another agent's TODO, decision, or handoff entry. Append entries; edit only the current task's roadmap status.

## 15. Architecture Decision Records (ADRs)

Any decision with lasting consequences must have an ADR in `docs/adr/`, for example:

- Mobile framework.
- Backend framework.
- Database and geospatial design.
- Map/geocoding/routing providers.
- Offline local storage, synchronization and Pro entitlements.
- GPS sampling and matching architecture.
- Hosting, queues and storage.
- Authentication and privacy model.

Use this ADR format:

```markdown
# ADR-XXXX — <decision title>
- Status: PROPOSED / ACCEPTED / REJECTED / SUPERSEDED
- Date:
- Owner approval: PENDING / APPROVED
- Context:
- Constraints:
- Options considered:
- Comparison: functionality, cost (must be $0 under the current policy), limits, license, Tunisia coverage, lock-in, privacy, operations
- Recommendation:
- Consequences and risks:
- Reversibility:
- Validation/prototype evidence:
```

For a DELEGATED decision, recommend; do not accept it on behalf of the product owner. For a TBD decision, list the information needed to decide. Never change a status to ACCEPTED without owner approval.

## 16. Coding standards and change safety

- Follow the project's existing language, framework, formatting, naming and folder conventions once selected. Do not introduce a framework while the framework decision is TBD.
- Prefer simple, typed, testable code over clever abstractions.
- Validate every external input at trust boundaries.
- Keep secrets out of source control and redact them from output.
- Preserve backward compatibility unless the task explicitly authorizes a breaking change.
- Add migrations for database changes; never edit production data directly.
- Never run destructive commands such as recursive deletion, reset/clean, force push, data truncation or overwrite of user work without explicit approval.
- Do not commit, push, publish, deploy, or open external PRs unless the owner has asked for that action.
- Never silently change package managers or lockfiles.
- Do not add a dependency if the existing toolchain can reasonably solve the task.

## 17. Definition of done

A task is DONE only when all applicable conditions are met:

- Its scope and acceptance criteria are satisfied.
- The change is limited to the assigned task.
- Relevant tests/checks pass, or unrun checks and reasons are declared.
- No unrelated functionality has regressed based on the checks actually performed.
- Localization, RTL, accessibility and low-end Android impact have been considered where relevant.
- Transport provenance, confidence, privacy and free-tier constraints are preserved.
- Documentation and relevant decisions are updated.
- The master roadmap and append-only handoff log are updated.
- A precise next TODO and copy-ready handoff prompt are left.

## 18. Mandatory final response format

Keep the user-facing report short and factual. Use this exact structure:

```text
STATUS: DONE | PARTIAL | BLOCKED | REVIEW NEEDED
TASK: <ID and title>
RESULT: <1–3 concise bullets>
FILES: <files changed>
TOOLS USED: <actual tools/commands>
VALIDATION: <actual checks and results, or NOT RUN with reason>
DECISIONS: <none, or proposals/approval state>
BLOCKERS: <none, or exact blocker>
ROADMAP: docs/MASTER_ROADMAP.md updated — <task status>
HANDOFF LOG: docs/AI_HANDOFF_LOG.md updated — <entry reference>
NEXT TODO: <one specific action>
NEXT AGENT: <suggested role/tool type>
NEXT PROMPT: <copy-ready one-paragraph prompt>
```

No generic progress essay, no exaggerated claims and no hidden incomplete work.

## 19. Initial task selection for a new repository

If the repository has no application code yet, do not scaffold a complete app automatically. Start with repository and feasibility preparation.

The recommended first task is:

**TUM-P0-001 — Repository and source-of-truth audit**

- Inspect repository files and Git state.
- Confirm the SDD v0.3 and decision register are present and are the current approved baseline.
- Create/verify `docs/MASTER_ROADMAP.md`, `docs/AI_HANDOFF_LOG.md` and `docs/adr/`.
- Identify missing required documents; do not fabricate them.
- Record the current state and nominate exactly one next TODO.

After this audit, the likely next task is a **transport data feasibility audit**, not full application scaffolding. Follow the SDD Phase 0 gates.

## 20. Authority and escalation

The human product owner has final authority over product scope, UX preferences, pricing, Pro entitlements, advertising, launch geography, data/privacy policy and acceptance of architecture decisions.

Stop and request owner approval before:

- Spending or enabling billing.
- Signing up for a service or creating external accounts.
- Publishing/deploying a public service or changing DNS.
- Collecting or exporting personal/location data.
- Changing confirmed product scope or user-facing monetization.
- Accepting a delegated/TBD decision that materially affects the architecture.
- Performing destructive or irreversible actions.

When blocked, do not fill the gap with an assumption. Record the exact blocker in the roadmap and handoff log, then give the owner the smallest decision needed to unblock the work.
