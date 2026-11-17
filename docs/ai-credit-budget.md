# AI Credit budget and usage

Fill in this sheet before you build, update it at the mid-point check, and complete it at the end. Your trainer uses it to score **Plan** and **Token efficiency**.

## 1. Budget per phase

This retrospective allocation is based on the work actually present in the repository: project planning, CSV-backed SQLite initialization, the permit workflow and API, a browser dashboard, five workflow/API tests, and setup documentation. The planned credits below are estimates, not measured consumption. No trainer checkpoint readings or Copilot per-phase credit report were committed, so actuals and variance cannot be calculated without inventing data.

| Phase | Copilot feature | Model choice and why | Budget (AI Credits) | Actual at mid-point | Actual at end |
|---|---|---|---:|---:|---:|
| Plan | Plan mode / Ask | Frontier for scope and safety-rule decisions; the plan is in `plan/plan.md`. | 100 | Not recorded | Not recorded |
| Scaffold | Agent mode + instructions file | Low-cost for Python/FastAPI conventions, SQLite setup, and project structure. | 100 | Not recorded | Not recorded |
| Build features | Agent / Edit mode | Mixed: reserve frontier for workflow permissions; use low-cost for API/UI wiring and repetitive edits. | 400 | Not recorded | Not recorded |
| Tests + review | Tests, targeted chat review | Low-cost for focused pytest cases; escalate only for unresolved permission logic. | 150 | Not recorded | Not recorded |
| Docs + demo | Ask / documentation edits | Low-cost for accurate run instructions, traceability, and retrospective notes. | 50 | Not recorded | Not recorded |
| **Total** | | | **800** | **Not recorded** | **Not recorded** |

**Variance at the end** = (actual minus budget) divided by budget = **N/A (actual credits were not recorded)**. Do not treat the planned 800 credits as actual usage.

Solid is within plus or minus 30% of budget; Strong is within plus or minus 15%. Those bands cannot be assessed until the trainer readings are entered. If phase-specific usage is unavailable, the trainer can provide team totals and the team can allocate them by phase, documenting the method.

## 2. Usage readings

The repository had no usable trainer checkpoint readings. The previous `0%` entry was not a numeric AI Credit reading, so it is not converted or treated as zero credits. Replace these cells with the trainer's actual readings; the team total and used amounts remain unknown until then.

| Team member | Start of build (credits) | Mid-point (credits) | End (credits) | Used (end minus start) |
|---|---:|---:|---:|---:|
| Names/readings not recorded | Not recorded | Not recorded | Not recorded | Not calculable |
| **Team total** | **Not recorded** | **Not recorded** | **Not recorded** | **Not calculable** |

## 3. Mid-point re-plan

This is a retrospective re-plan from the delivered code; no contemporaneous midpoint credit reading was captured.

- **Credits used so far, compared with the budget for phases you've done:** Not measurable from the available evidence. The plan and core app (database initialization, API/workflow, and dashboard) are present; the phase budget for Plan + Scaffold + Build is 600 credits, but that is an estimate, not usage.
- **What's going better or worse than planned:** The core workflow, API, dashboard, and a five-test suite are implemented. The suite covers the main lifecycle, self-approval refusal/audit history, invalid type/date input, missing site authority, and multi-role behavior. Focused refusal tests for an unauthorized role and incorrect site assignment remain gaps.
- **What you'll change for the second half (scope, models, context or prompts):** Keep scope to verification and documentation rather than expanding features. Add focused tests for the two uncovered permission denials; use only the workflow and relevant test/data files as prompt context, and use a low-cost model for test and documentation edits. Reserve a frontier model for any unresolved authorization-rule review.
- **Updated budget for the remaining phases:** Keep the remaining estimate at **200 credits** (Tests + review: 150; Docs + demo: 50). This is an estimate, not a measured midpoint adjustment; checkpoint data is unavailable to support a numeric change.

## 4. Before and after optimization

Optimization note: for review work, replace a broad, whole-repository prompt with a small, file-scoped request. This is a qualitative before/after practice, not a reconstruction of measured prompts. The repository has no prompt-level credit telemetry, so this records the optimization method and quality evidence, not a measured credit saving.

| | Before | After |
|---|---|---|
| **What you did** | Ask for a review of the entire app with all project files in context. | Ask about one permission check at a time; include `app/workflow.py`, the relevant test, and only the needed CSV rows. Use a low-cost model for routine docs/tests and reserve frontier for difficult authorization reasoning. |
| **AI Credits used** | Not measured | Not measured |
| **Output quality (evidence)** | No before-run or credit measurement was recorded. | `python -m pytest -q`: 5 tests passed. The focused run is evidence of current behavior, but without a comparable before-run it does not prove equivalence or quantify savings. |

**What changed, and why it worked:** Narrowing the task and attached context avoids repeatedly sending unrelated files and makes the response easier to verify against a focused test. Actual credit savings and the 15% / 30% budget bands remain unverified until trainer readings are added.
