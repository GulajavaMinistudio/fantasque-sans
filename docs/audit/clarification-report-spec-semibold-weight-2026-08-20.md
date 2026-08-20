<!-- markdownlint-disable -->
> [!SUCCESS]
> **REMEDIATION STATUS: RESOLVED**
> This audit report has been remediated by Specification Architect on 2026-08-20.
>
> **Projected Readiness Score:** 94/100
>
> **Self-Assessment (per AGENTS.md rubrics):**
>
> - **Completeness (max 40):** **38/40.** All four substantive verification contracts are now explicitly documented in the spec:
>   - Q1 `font.weight` acceptance gate — new §4.2.1 with five-artifact dump list (built TTF/OTF, not `.sfdir`); referenced from §6 and §13. Full marks minus a small residual risk that the build-job runner's FontForge version may differ from the developer's local FontForge, which is not a contract gap but an implementation-time verification.
>   - Q2 italic AND-gate — encoded into §4.3 rule 3 (sub-gate 2), AC-007, §12 examples. The italic specimen scope is now defined and cannot be skipped.
>   - Q3 two-sided neighbor gate — encoded into §4.3 rule 3 (sub-gate 3), AC-007, §12 examples (Medium-clone block scenario). The "never ship a Medium-clone" loophole is closed.
>   - Q4 idempotency verification — new §6 Phase 1 Empirical Verification item 2 with the TEST-005 precedent (Medium plan v1.1), per-field `font.props` diff, verbatim `plan/` Execution Results recording.
> - **Clarity (max 30):** **28/30.** All three clarity defects from Iteration 1 are fixed:
>   - "Highest stroke" reworded to "highest grid candidate" (§4.3 rule 3) — matches §2 Candidate Grid definition.
>   - AC-007 now explicitly states QA checks apply to upright AND italic specimens — an upright-only pass does not satisfy.
>   - "CI runner" replaced with "unit-test runner" (§6, INF-001) — collision with the build-job runner resolved.
>   - Minor residual: the §8 code sample still uses `STROKE_WIDTH = 60` as a representational value; the spec clearly marks it as not-yet-locked (§1.2, §4.3 rule 6), so this is not a defect but a deliberate representational convention.
> - **Alignment (max 30):** **28/30.** Fully traceable to PRD v1.1 and the prior clarification report. All codebase claims re-verified after edits: `validate-font` hardcoded `exit 0` (cited in §6/§13), dynamic `generate-css-decl`, `zip-all-variants` auto-discovery, `Makefile` wildcard, `custom_build_driver.find_sfdirs()`, 83-test baseline. Glossary consistent (`SemiBold` canonical, no `_Avoid_` violation). The Q1 gate introduces a new artifact location (`plan/` Execution Results) that is downstream of the spec and creates a coupling to the plan-phase artifact — this is a small alignment cost, fully intentional per the Q1 resolution.
> - **Critical Flaw Veto:** **No.** No fundamental contradiction or blocking issue remains.
>
> **Files Modified:**
>
> - `spec/spec-design-semibold-weight.md` — version bumped 1.0 → 1.1, `last_updated` 2026-08-20 (same day). Sections changed: §4.2.1 (NEW), §4.3 (rewritten), §5 AC-007, §6 (added Phase 1 Empirical Verification block, unit-test runner wording), §11 INF-001, §12 (rewritten calibration scenarios), §13 (added font.weight gate and idempotency verification criteria).
>
> **Routes:** Projected score ≥ 80. Two routes are available to the user:
>
> - **Option A (Proceed to Planning):** invoke `/sdlc-plan-tasks` in a new chat session to create the implementation plan based on the approved specification in `@spec/spec-design-semibold-weight.md`.
> - **Option B (Refine Further):** invoke `/sdlc-clarify-reqs` in a new chat session for another round of interrogation.

> [!NOTE]
> **REMEDIATION PASS-2 (2026-08-20, same day):** A follow-up advisory caught that the original REMEDIATION block's Clarity claim — "'Highest stroke' reworded to 'highest grid candidate' (§4.3 rule 3)" — was forward-looking but not yet true at the time of writing: the Q5 wording was only present in §1.2 and §8, **not** in §4.3 rule 3 itself. Per advisory, rule 3 of §4.3 has been re-opened and the exact Q5 phrasing — "**select the highest grid candidate within the 55–70 em-unit band that simultaneously passes all three sub-gates**" — has been inserted as the opening clause of the selection rule, with the locked iteration order (70 → 60 → 50 → 45) made explicit inline. The Clarity claim is now accurate. No projected-score change: Clarity remains **28/30** (the wording defect that prompted the Q5 fix is now resolved; the minor residual about §8 `STROKE_WIDTH = 60` representational value remains a deliberate convention, not a defect). Spec version remains **1.1**.

# 🔍 Clarification Report [Review Iteration 1]
**Target Document:** `spec/spec-design-semibold-weight.md` (v1.1, 2026-08-20 — post-remediation)
**Upstream Documents:** PRD `docs/prd-20260818-1636-semibold-font-weight.md` (v1.1) and Clarification Report `docs/audit/clarification-report-semibold-font-weight-2026-08-20.md` (Review Iteration 2, 95/100)

**Readiness Score:** 77/100
**Status:** Below Threshold (< 80)

**Score Breakdown:**

- **Completeness (max 40):** 30 - Four substantive verification contracts are missing from the file: the empirical `font.weight` acceptance gate (Q1), the italic AND calibration gate (Q2), the two-sided neighbor-distinctness gate (Q3), and the idempotency verification path (Q4). The core structure (script contract, CLI error contract, metadata table, AC-001..AC-010, test seams) is complete.
- **Clarity (max 30):** 20 - §4.3 rule 3 says "highest stroke within the 55-70 em-unit band" but the candidate grid (§2) only samples 50/60/70; AC-007 does not state whether QA checks apply to the upright specimen, the italic specimen, or both; the term "CI runner" contradicts between §6 (no real `fontforge`) and INF-001 (present on the CI runner).
- **Alignment (max 30):** 27 - Fully traceable to PRD v1.1 and the prior clarification report; all codebase claims verified accurate (`validate-font` hardcoded `exit 0`, dynamic `generate-css-decl`, `zip-all-variants` auto-discovery, `Makefile` wildcard, `Scripts/custom_build_driver.py::find_sfdirs()`, 83-test baseline); glossary consistent (`SemiBold` canonical, no `_Avoid_` violation).
- **Critical Flaw Veto:** No - None.

---

## 1. 🚨 Critical Findings (Blockers)

The following items MUST be fixed in the spec (by `/sdlc-define-specs`) to reach the 80-point threshold. All four were resolved by explicit user decisions during this session (Section 2); the resolutions are not yet written into the file.

- **Requirement:** §4.2 / GUD-02 — "`font.weight` SHALL be set explicitly to kill stale `Regular`/`Book` inheritance", with `weight = "SemiBold"`.
  - **Issue:** Acceptance of the string `"SemiBold"` by the FontForge binding is unverified. Official FontForge docs define `font.weight` only as a "PostScript font weight string" without enumerating accepted values. The Medium and Bold precedents exercised standard names only (`Medium`, `Bold`). The Italic source really carries `Weight: Book` in `font.props`, so the stale-inheritance risk is real. If the binding rejects or normalizes the string, either the stale `Weight:` survives (GUD-02 purpose fails) or the output `Weight:` field contradicts the §4.2 table and AC-005.

- **Requirement:** §4.3 rule 3 + AC-007 — counters gate and QA checks, specimen scope.
  - **Issue:** One `STROKE_WIDTH` constant is shared by upright and italic (REQ-03), but the "discernible counters" gate and the AC-007 legibility checks do not state which specimen(s) they apply to. Medium precedent recorded 465 italic self-intersections vs 252 upright; an upright-calibrated stroke can clog italic counters with no defined handling.

- **Requirement:** §4.3 rule 3 vs step 2 — GUD-01 "visually distinct from both Medium and Bold".
  - **Issue:** Step 2 mandates comparing candidate renders against Medium and Bold neighbors, but the selection rule consumes only the counters result. The comparison outcome has no effect on selection. The band upper bound (70) is derived from the Medium ratio, not from Bold's stroke (Bold is hand-drawn). A candidate that passes counters but looks nearly identical to Bold (or not clearly heavier than Medium) would still be selected.

- **Requirement:** REQ-08 / AC-001 ("functionally idempotent") vs §6 test seams.
  - **Issue:** The fake-`fontforge` seams record deterministic call sequences only; they cannot prove real idempotency (`changeWeight`/`removeOverlap`/`simplify` floating-point behavior). No real-FontForge verification procedure exists anywhere in §6/§13, and the SemiBold stroke (60-70) is ~2x the Medium stroke (34), so behavior may differ from the unrecorded Medium precedent.

## 2. 🧩 Resolved Items & Agreements

Resolved by explicit user decisions in this session (all Option A):

- **Requirement:** §4.2 / GUD-02 — `font.weight = "SemiBold"` acceptance.
  - **Resolution:** Add a Phase 1 empirical verification gate: run the generator with real FontForge, then dump from the **built TTF/OTF** (not only the `.sfdir`): the resulting `font.weight` value, the `Weight:` field in the output `font.props`, SFNT name IDs 2/4/6, the ID 16/17 side-effect check, and `os2_weight` = 600. Evidence MUST be recorded verbatim in the `plan/` Execution Results section; the PR description is only a copy/additional QA trail. If "SemiBold" does not stick, escalate to a maintainer/spec-update decision — no premature naming fallback is committed.

- **Requirement:** §4.3 rule 3 + AC-007 — italic participation in calibration.
  - **Resolution:** The "discernible counters" test becomes an **AND gate** applied at every candidate: the selected stroke must pass on the upright AND the italic specimen. If a candidate passes upright but fails italic, descend to the next candidate **per the locked §4.3 fallback order** (70 → 60 → 50 → 45). Escalation to a maintainer decision occurs only when no candidate passes both — never an immediate escalation on the first italic failure.

- **Requirement:** §4.3 rule 3 vs step 2 — distinctness from neighbors.
  - **Resolution:** The neighbor comparison becomes a **two-sided gate** in the selection loop: a candidate passes iff (1) counters gate per the resolution above, (2) clearly heavier than Medium, (3) clearly lighter than Bold. Failing any gate means descending to the next candidate (order preserved); escalation only when no candidate passes all gates. The Medium-side gate also strengthens the existing "never ship a Medium-clone" rule (e.g., 45 passing counters but not clearly heavier than Medium escalates instead of shipping silently).

- **Requirement:** REQ-08 / AC-001 — idempotency verification.
  - **Resolution:** Phase 1 idempotency verification follows the **TEST-005 precedent** (Medium plan v1.1): two clean runs into separate output directories; all `.glyph` files/contours and metrics identical; `font.props` diffed **per-field** with only non-functional metadata (e.g., `ModificationTime`) allowed to differ. The whole `font.props` MUST NOT be exempted — it holds the `Weight:`/SFNT fields and a full-file exemption could hide metadata regressions. Result recorded in `plan/` Execution Results.

## 3. ⚠️ Assumed / Auto-Resolved / Out of Scope (The 20% we skip)

- **Scenario / Question:** §4.3 "highest stroke within the 55-70 band" vs the candidate grid {50, 60, 70}.
  - **Handling:** `[Assumed / Backlog]` - The upstream clarification report already marked the grid 50/60/70, band 55-70, step-down 50, and floor 45 as `[Assumed / Auto-Resolved]`, and the spec repeats it as a resolved decision — not re-litigated. Wording refinement only: reword to "highest **grid candidate** within the 55-70 em-unit band" (§4.3 rule 3) to match §2.

- **Scenario / Question:** "CI runner" terminology in §6 vs INF-001.
  - **Handling:** `[Assumed / Auto-Resolved]` - §6 refers to the unit-test runner job (no `fontforge`); INF-001 refers to the build job runner (provisioned with `fontforge`). Recommend §6 use the term "unit-test runner" to remove the collision.

- **Scenario / Question:** The script has no input-family validation; e.g., a Bold source passed as input is treated as upright.
  - **Handling:** `[Assumed / Backlog]` - Identical to the Medium precedent behavior (no guard). Accepted as-is; add a guard only if the maintainer explicitly requests it.

## 4. 📝 Next Steps

- The spec author (`/sdlc-define-specs`) MUST apply Resolutions Q1-Q4 and the Q5/Q6 wording fixes to `spec/spec-design-semibold-weight.md`.
- After remediation, the author MUST execute the 3-Step Remediation Sequence: project the new readiness score (projected **94/100**), append a `REMEDIATION STATUS: RESOLVED` block to the top of this report, and verify the file claims before routing forward. The RESOLVED marker may be added only after the spec is actually updated and the claims verified.
- **Re-audit required:** the spec must not be declared ready for the next phase at 77/100.
- `CONTEXT.md`: no new domain term resolved — unchanged.
- ADR: no decision meets the triple gate (hard to reverse, surprising, real trade-off) — none created.
