
> [!SUCCESS]
> **REMEDIATION STATUS: RESOLVED**
> This audit report has been remediated by Planner Architect (2026-08-05).
> - **Projected Readiness Score:** 95/100
> - **Resolutions applied:** A (TASK-3.X metadata clause — familyname identik, os2_weight/fullname unique and not identical to master), B (TASK-4.4 Ref ID REQ-D05 → REQ-B05), D (TASK-4.1 BUILD_LEVEL_FLAGS mechanism), F (TASK-4.2 numbering normalized to (i)–(v)). Resolutions C (Spec --cov-fail-under=90) and E (CONTEXT.md 0.67 eksak) completed outside Plan scope.
> - **Plan version:** v1.13

<!-- markdownlint-disable -->

# 🔍 Clarification Report [Review Iteration 6]

**Target Document:** `plan/plan-feature-multi-weight-variants-v1.12.md` (Implementation Plan — Multi-Weight Font Variants)

**Upstream Context:** `spec/spec-multi-weight-variants.md` (v1.8)

**Date:** 2026-08-04

**Readiness Score:** 93/100

**Status:** Good Enough

**Score Breakdown:**

- **Completeness (max 40):** 37 - All phases (0–5), tasks with Ref/AC/Dep/Files, per-phase verification & approval gates, the 10-step release runbook, TEST-001–007, risks, rollback, and changelog are present. After resolutions A–F no functional gaps remain; only extreme edge cases appropriate for `[Assumed / Backlog]` annotation.
- **Clarity (max 30):** 28 - All values are measurable and contract-bound (exact `0.67`, `15.0°`, ≤ 2%, ≤ 240 min, ≤ 500 KB, ≥ 90%). Residual ambiguous phrasing (TASK-3.X metadata clause, `REQ-D05`, coverage enforcement, flag mapping) was closed during this session.
- **Alignment (max 30):** 28 - Traceability to Spec v1.8 and the PRD is restored after the `REQ-D05` → `REQ-B05` fix and the CONTEXT.md synchronization. Remainder: the scheduled Spec §4.9 amendment (`--cov-fail-under=90` + `BUILD_LEVEL_FLAGS` mapping) via `/sdlc-define-specs` — a normal amendment mechanism, not a plan defect.
- **Critical Flaw Veto:** No - None.

---

## 1. 🚨 Critical Findings (Blockers)

None — every finding raised in this session was resolved within the session (see Sections 2 and 3). No blocking ambiguity remains after the resolutions below.

## 2. 🧩 Resolved Items & Agreements

- **Requirement:** TASK-3.X (Phase 3 VERIFY) — *"Metadata verification Layer 1: one-liner FontForge checks `.sfdir` (os2_weight, familyname, fullname unique per weight and not identical to master)."*
  - **Resolution (User decision: Option A):** The clause *"not identical to master"* applies ONLY to `os2_weight` and `fullname`. `familyname` = `"Fantasque Sans Mono"` is IDENTICAL across all weights (including masters), consistent with r6 Q-08, Spec §4.6, TASK-0.7, and test #11. A literal reading of the old phrasing would always fail, because the master familyname is also `"Fantasque Sans Mono"`. Plan TASK-3.X is to be corrected in v1.13.

- **Requirement:** TASK-4.4 Ref ID column — *"REQ-D05, REQ-D03"*
  - **Resolution (User decision: Option A):** `REQ-D05` does not exist in Spec v1.8 (only `REQ-D01`–`REQ-D04`) nor in the PRD — verified via repository-wide grep; the only occurrence in the repository is this Plan row. Corrected to `REQ-B05` (Packaging Update — the only requirement literally targeting the `packaging.sh` modification) combined with `REQ-D03` (already present). Traceability restored.

- **Requirement:** TEST-007 — *"Coverage ≥ 90% in container mandatory to pass TASK-4.2 RUN chain (Spec §6.7)."*
  - **Resolution (User decision: Option A):** `pytest-cov` without `--cov-fail-under` never exits non-zero on low coverage (verified: no `--cov-fail-under` appears anywhere in the Plan or Spec). Add `--cov-fail-under=90` to the pytest command in the RUN chain (Spec §4.9) and synchronize Plan TASK-4.2 / TEST-007 — mechanical, fail-fast enforcement consistent with GUD-002.

## 3. ⚠️ Assumed / Auto-Resolved / Out of Scope (The 20% we skip)

- **Scenario / Question:** TASK-4.1 claims `--multi-weight` is *"mapped to driver flag via `FORM_KEY_TO_OPTION`/`OPTION_TO_DRIVER_FLAG` pattern"* — but `OPTION_TO_DRIVER_FLAG` semantically maps options to `custom_build_driver.py` flags (`--line-height`, `--no-loop-k`, `--no-calt`), while `--multi-weight` must be stripped before the driver invocation (the driver `_die`s on unknown flags; verified at `custom_build_driver.py:111-113`).
  - **Handling:** `[Assumed / Auto-Resolved]` - Introduce a separate constant (e.g. `BUILD_LEVEL_FLAGS`) consumed by `build_driver_arg_string()` as a build-level flag → `BUILD_ARGS` → RUN chain, then stripped before the driver. This keeps `OPTION_TO_DRIVER_FLAG` semantics pure and eliminates the risk of an implementer forwarding `--multi-weight` to the driver. Minor Spec §4.9 wording + Plan TASK-4.1 amendment scheduled.

- **Scenario / Question:** CONTEXT.md *Core Weight* entry still reads *"factor ~0.67"* — conflicting with the exact `0.67` contract (r4 R3: `~0.67` is a misleading presentation rounding; `0.67` vs `2/3` yields different coordinates and violates GUD-001).
  - **Handling:** `[Assumed / Auto-Resolved]` - CONTEXT.md was updated inline during this session (`"factor 0.67 eksak"`); no new canonical terms, no `_Avoid_` changes.

- **Scenario / Question:** TASK-4.2 contains duplicated numbering "(iii)/(iv)" while describing the RUN chain order.
  - **Handling:** `[Assumed / Auto-Resolved]` - Editorial normalization to (i)–(v) in Plan v1.13; no contract change.

## 4. 📝 Next Steps

- **Plan** MUST be updated to v1.13 by `/sdlc-plan-tasks`: resolution A (TASK-3.X metadata clause), resolution B (TASK-4.4 Ref ID → `REQ-B05, REQ-D03`), resolution D (TASK-4.1 `BUILD_LEVEL_FLAGS` mechanism), resolution F (TASK-4.2 numbering normalization).
- **Spec** MUST be amended to v1.9 by `/sdlc-define-specs`: resolution C (§4.9 RUN chain pytest command + `--cov-fail-under=90`; §6.7/TEST-007 wording sync) and resolution D (§4.9 flag mapping wording).
- **Domain Glossary (`CONTEXT.md`):** UPDATED this session (resolution E) — no further action required.
- **ADR:** None — no decision meets the triple-gate (hard to reverse / surprising without context / real trade-off); all resolutions are easily reversible and fall under spec-level resolutions (Spec §8.5).
- Add this report to the Plan §8 (Related Specifications) and to the Spec header `clarification_reference` (scheduled together with the respective amendments).

---
> **User Decision Prompt:**
> The document has achieved a Readiness Score of 93/100. It is ready for the next phase. Do you want to **PROCEED** to the next phase, or do you want to **REFINE** and clarify further?
