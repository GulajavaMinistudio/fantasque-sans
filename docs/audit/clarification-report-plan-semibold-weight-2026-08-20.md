> [!SUCCESS]
> **REMEDIATION STATUS: RESOLVED**
> This audit report has been remediated by Planner Architect (`/sdlc-plan-tasks`, Phase 3 Post-Audit Revision).
> - **Projected Readiness Score:** 100/100
>
# 🔍 Clarification Report [Review Iteration 1]

**Target Document:** `plan/plan-design-semibold-weight-v1.0.md` (v1.0, 2026-08-20)
**Reference Specification:** `spec/spec-design-semibold-weight.md` (v1.1, 2026-08-20)
**Analyst:** Clarification Analyst
**Date:** 2026-08-20

**Readiness Score:** 96/100
**Status:** Good Enough

**Score Breakdown:**

- **Completeness (max 40):** 39 - All REQs/ACs are mapped to tasks; `Execution Results` evidence tables are present and verbatim-ready; the remaining gap is wording/reorder refinement, not missing structure.
- **Clarity (max 30):** 29 - Every fuzzy or self-contradictory point surfaced during interrogation (environment/ordering, calibration build-path, Q3 "clearly", font.props vs TTF evidence, 4-candidate CI loop, sign-off authority, permutation scope) was resolved by an explicit user decision.
- **Alignment (max 30):** 28 - The written plan still reflects a pre-commit execution model and must be edited to align with the confirmed CI execution model; the misalignment is resolved in substance by the decisions below.
- **Critical Flaw Veto:** None

---

## 1. 🚨 Critical Findings (Blockers)

_None remaining._ The two contradictions that were blocking during interrogation — (a) the Phase-1 pre-commit empirical gates (TASK-004/006/007) require the full build toolchain that only exists in CI, conflicting with TASK-010's commit which precedes them, and (b) TASK-006 artifact #2 referencing `.sfdir` `font.props` while the gate mandates reading from the built TTF/OTF — are now resolved by the user decisions recorded in §2. They MUST be applied to the plan by the Plan agent before execution (see §4 fix list).

---

## 2. 🧩 Resolved Items & Agreements

- **Requirement / Ambiguity:** "TASK-006 and TASK-007 (Phase 1, pre-commit) require building generated sources to TTF/OTF and dumping SFNT metadata, which needs the full toolchain (fontforge + ttfautohint + woff-tools/woff2) only provisioned in CI (`build-make.yml` / `Dockerfile`), not the maintainer's local machine (Windows 11 workstation). TASK-010 (commit) currently precedes TASK-006, creating a sequence contradiction."
  - **Resolution (Q1):** The empirical gates SHALL run via **GitHub Actions CI/CD (build-job runner), exactly like the Medium font build** — not local Docker. Consequence: the plan MUST be reordered so the feature-branch commit+push (TASK-010) precedes the CI-run empirical gates, followed by visual QA (TASK-022) and merge (TASK-023). `INF-001` / `P-ASSUMPTION-002` must be changed from "maintainer machine or build-job runner" to "GitHub Actions CI (build-job runner), same as Medium."

- **Requirement / Ambiguity:** TASK-004 offers a free choice — build each calibration candidate "via the standard `make` path OR via `Scripts/fontbuilder.py` directly" — risking apples-to-oranges comparison against the committed Medium/Bold TTFs (built via the `make` pipeline).
  - **Resolution (Q2):** Candidates SHALL always be built via the **standard `make` path in CI** (place the scratch `.sfdir` under `Sources/`, run `make`, take the TTF from `Variants/Normal/TTF/`), identical to how Medium/Bold neighbors are built and to how `build-make.yml` works. The "OR `fontbuilder.py`" option is removed.

- **Requirement / Ambiguity:** The Q3 two-sided neighbor gate (§4.3 rule 3c) — "clearly heavier than Medium AND clearly lighter than Bold" — is never operationalized with a measurable threshold; the word "clearly" is subjective and could produce arbitrary pass/fail.
  - **Resolution (Q3):** Q3 remains a **maintainer judgment**, BUT it is now auditable: the maintainer MUST record side-by-side specimen captures (Medium vs candidate vs Bold) at 12/14/16px and a brief stem-width ratio estimate (e.g., "SemiBold ≈ 1.8× Medium, ≈ 0.7× Bold") in the `Execution Results` calibration table. This preserves human judgment while preventing a silent Medium-clone/Bold-clone ship.

- **Requirement / Ambiguity:** TASK-006 artifact #1 says read `font.weight` from the built TTF/OTF, but artifact #2 says read "the `Weight:` field in the output `font.props`" — a `.sfdir` file the gate's own rationale says "can lie." Internal contradiction.
  - **Resolution (Q4):** Both artifact #1 and #2 SHALL be read from **`font.weight` of the built TTF/OTF** (open the TTF in FontForge, read `font.weight`). The `font.props` reference in artifact #2 is removed, honoring the gate's own warning that `.sfdir` `font.props` can lie.

- **Requirement / Ambiguity:** TASK-004 iterates 4 candidates (70/60/50/45), each requiring a TTF build + visual inspection, but CI is headless (no FontForge GUI preview). The plan never describes the calibration execution loop.
  - **Resolution (Q5):** The calibration loop SHALL be **per-candidate, full cycle**: for each candidate, edit `STROKE_WIDTH` → commit to the feature branch → push → trigger CI → download the built TTF artifact → inspect locally and record the sub-gate outcomes in `Execution Results`; repeat for 70, 60, 50, 45. TASK-010's allowance to amend/squash until QA passes keeps history clean.

- **Requirement / Ambiguity:** TASK-022 ("Maintainer visual QA and sign-off") closes AC-007 (which requires "at least one maintainer PR review comment or approval"), but the plan does not state (a) whether the source author may self-sign-off, or (b) what recorded evidence constitutes sign-off.
  - **Resolution (Q6):** The **PR review approval is the recorded sign-off evidence**. Self-review is permitted ONLY with an explicit single-maintainer constraint note, and TASK-022 MUST attach the side-by-side specimen captures plus an explicit statement in the PR. This makes the gate auditable and closes the silent-ship risk.

- **Requirement / Ambiguity:** The build produces 4 permutations (`Normal`, `LargeLineHeight`, `NoLoopK`, `LargeLineHeight-NoLoopK`), but TASK-004/TASK-022/AC-007 only mention "upright specimen AND italic specimen" without scoping which permutations require inspection.
  - **Resolution (Q7):** Calibration and visual QA SHALL cover only the **`Normal` permutation (+ its Italic)**. Glyph counter/stem geometry is identical across permutations (`LargeLineHeight` changes only vertical metrics; `NoLoopK` changes only the `k` glyph, which is outside the `e a s @ % & 8 #` counter-test set). This removes implementer ambiguity without reducing real coverage.

- **Verified Fact (not a decision):** The §4.2.1 / RISK-002 premise that the Italic source carries `Weight: Book` (and Regular carries `Weight: Regular`) was confirmed by reading `Sources/FantasqueSansMono-Italic.sfdir/font.props` and `Sources/FantasqueSansMono-Regular.sfdir/font.props`. The stale-`Weight: Book` risk framing is factually correct.

---

## 3. ⚠️ Assumed / Auto-Resolved / Out of Scope (The 20% we skip)

- **Scenario / Question:** TASK-011(b) states "alongside the existing 5 weights."
  - **Handling:** `[Assumed / Auto-Resolved]` - The monospace family currently has only **3 weights** (Regular/Medium/Bold; 6 `.sfdir` sources counting italics). The phrase is corrected to "3 existing weights." Verified via `glob Sources/*.sfdir`.

- **Scenario / Question:** TASK-004/005/006 still offer "via `make` OR `Scripts/fontbuilder.py` directly."
  - **Handling:** `[Assumed / Auto-Resolved]` - Pinned uniformly to **`make`** per Q2 resolution.

- **Scenario / Question:** FontForge version in CI is unpinned (`build-make.yml` deliberately leaves apt packages version-unpinned, matching Medium). The calibrated stroke is version-sensitive.
  - **Handling:** `[Assumed / Auto-Resolved]` - Left **unpinned** to match Medium and because CI modification is out-of-scope (Spec §1.1). Reproducibility risk is **accepted**; the FontForge version is recorded alongside the TASK-004/006/007 evidence.

- **Scenario / Question:** TASK-006 artifact #3 checks SFNT IDs 2/4/6 but omits ID 1 (Family), which AC-005 also requires.
  - **Handling:** `[Assumed / Auto-Resolved]` - Add **ID 1 (Family = "Fantasque Sans Mono")** to the TASK-006 #3 acceptance check for completeness; covered by TASK-015 cross-check regardless.

- **Scenario / Question:** The §4.2.1 five-artifact dump needs a FontForge script; the plan does not state where it lives.
  - **Handling:** `[Assumed / Auto-Resolved]` - The dump is a **one-off FontForge one-liner** (open TTF, print `font.weight` + SFNT names + `os2_weight`), not committed to the build pipeline (consistent with REQ-11 / zero-touch).

---

## 4. 📝 Next Steps

- The upstream plan (`plan/plan-design-semibold-weight-v1.0.md`) MUST be updated by the Plan agent with the seven resolutions above. Concrete mandatory fixes:
  1. **Reorder phases:** commit+push feature branch (TASK-010) BEFORE the empirical gates (TASK-006/TASK-007); visual QA (TASK-022) then merge (TASK-023) follow. The "pre-commit" framing of Phase 1 is retired.
  2. **Update `INF-001` / `P-ASSUMPTION-002`:** "GitHub Actions CI (build-job runner), same as Medium" — remove "maintainer machine or".
  3. **TASK-004:** remove the `fontbuilder.py` alternative; state the per-candidate CI loop (edit → commit → push → CI build → download → inspect → record), repeated for 70/60/50/45; scope inspection to `Normal` (+Italic).
  4. **TASK-005/006:** build uniformly via `make` in CI; remove `fontbuilder.py` alternative.
  5. **TASK-006:** both artifact #1 and #2 read `font.weight` from the built TTF/OTF; delete the `font.props` reference; add ID 1 (Family) to artifact #3.
  6. **TASK-011(b):** correct "5 weights" → "3 existing weights".
  7. **TASK-022 / AC-007:** state that PR review approval is the recorded sign-off, self-review permitted only with single-maintainer note + attached side-by-side specimen captures and explicit PR statement; scope QA to `Normal` (+Italic).
  8. **TASK-004 / TASK-022:** require the auditable Q3 evidence (side-by-side specimens + stem-width ratio estimate) in `Execution Results`.
- **Domain Glossary (`CONTEXT.md`):** No change required. The term `SemiBold` is already canonical (Spec §10 confirms it exists in `CONTEXT.md`; `_Avoid_`: semibold, semi bold, demi bold, DemiBold). No new domain term was resolved in this session.
- **ADR:** None created. The resolved decisions are per-feature calibration/execution policy, not hard-to-reverse architectural choices (consistent with Spec §10 ADR rationale). Triple-gate validation fails on "hard to reverse," so no ADR is warranted.

---

> **User Decision Prompt:** The document has achieved a Readiness Score of 96/100. It is ready for the next phase. The user chose to **PROCEED** (save this report). The Plan agent SHOULD apply the §4 fix list before `/sdlc-plan-tasks` execution begins.
