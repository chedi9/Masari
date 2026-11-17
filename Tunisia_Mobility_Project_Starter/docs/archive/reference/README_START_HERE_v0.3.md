# Tunisia Mobility Platform — Project Starter Folder

This folder is a ready-to-open project workspace for the Tunisia Mobility Platform. It contains the approved discovery baseline, AI-agent instructions, one master roadmap, and the handoff log.

## Fast setup

1. Download and extract `Tunisia_Mobility_Project_Starter.zip`.
2. Open the extracted `Tunisia_Mobility_Project_Starter` folder itself in your coding environment (for example, VS Code, Codex, or Google Antigravity). Do not point the agent at the ZIP file.
3. Before assigning work, ask the agent to read `AGENTS.md`, `SDD_v0.3_Tunisia_Mobility_Platform.md`, `Tunisia_Mobility_Decision_Register_v0.3.md`, `docs/MASTER_ROADMAP.md`, and the latest entries in `docs/AI_HANDOFF_LOG.md`.
4. Give it the first task below. It must inspect the folder and report its findings before writing application code.

If you already have a Git repository for this product, use this package as the source for the project instructions and documentation: copy these files into that repository's root, preserving the `docs/` structure. Do not overwrite newer owner-approved versions. Check `git status` first and keep existing human work safe.

## Which instruction file is used?

- Codex and other compatible agents: root `AGENTS.md`.
- Google Antigravity: root `AGENTS.md` as workspace/project guidance where supported by the current version.
- Claude Code: root `CLAUDE.md`, which imports the shared `AGENTS.md`.
- Claude web chat: attach the SDD, decision register and `docs/CHATGPT_HANDOFF_PROMPT.txt`; it does not automatically read this local folder.

## First task — do not skip

Copy this exact prompt to the first coding agent:

```text
Read AGENTS.md completely. Read the SDD and Decision Register, then inspect docs/MASTER_ROADMAP.md and docs/AI_HANDOFF_LOG.md. Do not start building the application.

Execute TUM-P0-001 — Repository and source-of-truth audit only. Inspect the current workspace, directory structure and Git state (if Git is initialized). Verify that the project documents agree with each other. Identify missing evidence, missing files, contradictions, and any changes needed to make this a safe working repository. Do not invent product decisions, city choices, transport data, APIs, licenses, prices, or technical stack decisions.

Use only tools and services that can be used at zero cost. Do not activate billing, paid APIs, paid subscriptions, metered credits or paid cloud resources. Before acting, list the tools/commands you intend to use and why. Preserve all existing human work.

At the end, update docs/MASTER_ROADMAP.md and append one dated entry to docs/AI_HANDOFF_LOG.md. Mark the task status accurately. Leave exactly one clear next TODO with its task ID, objective, inputs, tools to use, expected files, acceptance criteria, blockers and a copy-ready prompt for the next agent. Report changed files, checks run, evidence, costs (must be zero), and anything requiring my approval. Do not claim a test or audit was performed unless you actually performed it.
```

## Single source of truth

- Product/system requirements: `SDD_v0.3_Tunisia_Mobility_Platform.md`.
- Owner decisions and open items: `Tunisia_Mobility_Decision_Register_v0.3.md`.
- Execution order and next task: `docs/MASTER_ROADMAP.md`.
- Append-only agent handoffs: `docs/AI_HANDOFF_LOG.md`.
- ChatGPT continuation instructions: `docs/CHATGPT_HANDOFF_PROMPT.txt`.
- Cross-agent operating rules: `AGENTS.md` (Claude Code imports it through `CLAUDE.md`).

Do not create competing roadmap files. Do not change confirmed product decisions or turn TBD/delegated items into approvals without the product owner's explicit approval.

## Cost policy

This project is to be developed with free tools/free tiers only. Free tiers may have usage limits. Never add billing, buy credits, enable a paid API, create paid cloud resources, or incur a charge. Stop and ask the owner if a task cannot be completed within the zero-spend policy.

## Important project status

The project is in discovery/feasibility. The full application is not yet authorized for implementation. Complete the Phase 0 evidence and approval gates in the SDD and master roadmap first, unless the owner explicitly changes that gate.
