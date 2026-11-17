# Permit-to-work app plan

## Problem and approach

This project builds a permit-to-work workflow for hazardous work approvals. The core risk is unauthorized approval and missing evidence. The implementation should keep the workflow simple, auditable, and testable: persist the synthetic data in SQLite, enforce role/site checks and separation of duties in one workflow layer, and expose the actions through a small API with filterable permit history.

## Phase-by-phase AI credit budget

- Plan: 150 credits
  - Use a frontier model for scope validation, workflow decisions, and risk checks before implementation.
- Scaffold: 120 credits
  - Use a low-cost model for conventions, file layout, boilerplate, and initial project setup.
- Build features: 450 credits
  - Mixed model usage: frontier for the state machine and tricky logic, low-cost model for repetitive edits and UI wiring.
- Tests + review: 180 credits
  - Use low-cost prompts for test generation and targeted review of checks, edge cases, and permission gaps.
- Docs + demo: 60 credits
  - Low-cost model for final README run instructions, budget summary, and demo notes.
- Total: 960 credits

## Workstreams

1. Set conventions and stack
   - Define the project stack in `.github/copilot-instructions.md`.
   - Keep the safety checks centralized so API and UI enforce the same logic.

2. Import and normalize data
   - Load the CSV datasets into SQLite.
   - Handle the deliberate data-quality issues before building the workflow.

3. Implement workflow engine
   - Enforce `REQUESTED` -> `APPROVED` -> `CLOSED` transitions.
   - Add `ROLE_REQUIRED`, `SITE_ASSIGNMENT`, and `SEPARATION_OF_DUTIES` checks.
   - Record both accepted and refused actions in permit history.

4. Build API endpoints
   - Expose endpoints to request, approve, close, list permits, and read history.
   - Return explicit check IDs and reason strings for refusal cases.

5. Build front end
   - Show a permit list filtered by site and status.
   - Provide permit history and action buttons driven by the API.

6. Test and review
   - Cover all transitions and edge cases.
   - Validate user role combinations, invalid requests, and missing area authorities.

7. Finalize docs and demo
   - Add clear run instructions and test commands.
   - Capture the actual budget comparison and summarize optimization choices.

## Key design decisions

- Use SQLite to keep the app local and easy to run.
- Treat failed attempts as audit evidence by retaining them in the history.
- Keep the API contract explicit and consistent with the README brief.
- Use the cheapest effective model at each phase while reserving frontier usage for higher-risk reasoning.
