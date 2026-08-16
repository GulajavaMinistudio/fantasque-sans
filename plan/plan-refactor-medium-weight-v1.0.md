---
goal: Medium Font Weight — Remediate SFNT naming correctness, sync upstream docs to accepted deviations, harden build-make.yml supply chain, and clean test scaffolding
version: 1.0
date_created: 2026-08-14
last_updated: 2026-08-16
owner: Expert Code Reviewer
status: "Complete"
tags: ["refactor", "clean-code", "architecture", "security", "font"]
---
<!-- markdownlint-disable  -->
# Introduction

![Status: Complete](https://img.shields.io/badge/status-Complete-brightgreen)

This refactoring plan remediates the findings of the `/sdlc-code-review` of `plan-design-medium-weight-v1.1.md` (branch `feat/medium-font-weight`, diff `abf07716..HEAD`, reviewed 2026-08-14). The feature implementation itself is functionally correct — all 18 plan tasks complete, pytest 81/81 green, CON-07 zero-touch verified empty, width 1060 verified on all glyphs, italic metrics preserved. The remaining work is: (1) close the highest-risk gap — the committed upright Medium source does not persist its SFNT SubFamily record and the built TTF's name table was never dumped as evidence, so the output font could be silently labeled `Regular`; (2) sync the upstream PRD (still v1.2) to the maintainer-accepted deviations recorded only at plan/spec level; (3) close unevidenced criteria (Nerd Font patching, idempotency record placement); (4) apply supply-chain hygiene to the new `build-make.yml`; (5) remove dead test scaffolding from the reverted `intersect()` approach.

**Execution Status (2026-08-16):** All 4 phases complete — 23/23 tasks marked ✅ (final user sign-off recorded). Remediation closed: SFNT naming evidenced (SEC-002), upstream docs synced (REQ-001..003, DOC-001..003, CON-003), workflow supply chain hardened (SEC-001), test scaffolding cleaned (PRN-001/002).

## 1. Traceability: Requirements & Constraints

- **SEC-001**: Harden the new `.github/workflows/build-make.yml` supply chain — pin third-party actions to commit SHAs and version-constrain apt/pip installs (or document baseline-consistent acceptance) — findings A-01, A-02, A-07.
- **SEC-002**: Guarantee and evidence correct SFNT naming (`SubFamily = "Medium"` / `"Medium Italic"`, Family, Fullname, PostScriptName) and `usWeightClass 500` in the **built** TTF/OTF for both Medium weights — findings A-03, B-04 (GH-004 AC1/AC3, PRD FR-07, Spec §4.2).
- **REQ-001**: Sync PRD to v1.3 recording the maintainer-accepted deviations (residual self-intersections deferred to visual QA; `validate-font` `Error in` baseline profile) — finding B-01 (PRD GH-001 AC3, FR-08, §7.3, GH-003 AC3).
- **REQ-002**: Close the Nerd Font patching evidence gap (PRD FR-09 / Spec §13) — execute and record, or add an explicit not-executed caveat — finding B-02.
- **REQ-003**: Move/duplicate the idempotency verification evidence (currently only at `.agents/instructions/memory.instructions.md:227`) into the plan Execution Results for traceability — finding B-03 (downgraded to NIT).
- **PRN-001**: Remove dead-code scaffolding in `tests/test_generate_medium_source.py` (`FakeGlyph.intersect`/`round`/`remove_overlap_calls` from the reverted per-glyph cleanup) — finding A-04.
- **PRN-002**: Strengthen the geometry operation-order assertion to cover `selection.all() → changeWeight → removeOverlap → simplify` and deduplicate `_selection_called` into `_operation_log` — findings A-05, A-06.
- **CON-001**: Documentation-only tasks must not modify the CON-07 zero-touch set (`Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, `features.py`) — verified empty diff must stay empty.
- **CON-002**: Any regeneration of the `.sfdir` sources must preserve glyph geometry — idempotency record (memory.instructions.md:227) shows re-runs change only `font.props ModificationTime`; adding `font.weight` must not alter contours. Visual QA sign-off (AC-007) stays valid.
- **DOC-001**: Resolve the CON-07 forbidden-list enumeration inconsistency between spec §1.1/§9 (`generate-css-decl` included) and plan CON-07/§5 (omitted) to one canonical list — finding B-05.
- **DOC-002**: Bump stale spec version citations (script docstring "Spec v1.2", plan §8/intro) to the current spec version — finding B-06.
- **DOC-003**: Tighten Spec §5 AC-006 wording to match the single-variant-per-dispatch reality ("selected variant(s)") — finding B-08.
- **CON-003**: Externalize the AC-007 visual-QA sign-off trail — record the PR review/approval reference in the plan execution record so it is not assertion-only — finding B-11.

## 2. Implementation Steps

> **⚠️ EXECUTION DIRECTIVE FOR AI AGENTS (`/sdlc-write-code`):**
> You MUST execute this plan phase by phase. You MUST run the specific testing/verification task at the end of each phase. After a phase is tested, you **MUST STOP AND WAIT** for the user's explicit approval before proceeding to the next phase. **DO NOT SKIP PHASES.**

### Implementation Phase 1: SFNT Naming Correctness & Evidence (SEC-002)

- **GOAL-001:** Eliminate the stale `font.weight` risk, persist correct SFNT records in the committed sources, and record a post-build name-table dump as proof for GH-004 AC1/AC3.

| Task ID  | Description (Include Exact File Paths & Micro-Testing)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Ref ID                                                                         |    Completed     | Date  |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ | :--------------: | :---: |
| TASK-101 | **Set `font.weight` explicitly** in `Scripts/generate-medium-source.py` `generate_medium()` (metadata block, after `os2_weight`): add module constant `MEDIUM_WEIGHT_NAME = "Medium"` and assign `font.weight = MEDIUM_WEIGHT_NAME` for BOTH upright and italic outputs (the current sources inherit `Weight: Regular` / `Weight: Book` from the inputs; FontForge can derive SFNT name ID 3/16/17 from the weight string when the name record is absent — the upright record is missing, see B-04). Do NOT change the glyph pipeline. | SEC-002 | [x] | 2026-08-16 |
| TASK-102 | **Micro-Test:** extend `tests/test_generate_medium_source.py` — assert `font.weight == "Medium"` in both `TestUprightGeneration` and `TestItalicDetection`; extend the existing order test (PRN-002) to assert `selection.all()` precedes `changeWeight` via `_operation_log`. Run `python -m pytest tests/ -q` — full suite must stay green (81 + new). | SEC-002, PRN-002 | [x] | 2026-08-16 |
| TASK-103 | **Regenerate both sources** with the updated script: `python Scripts/generate-medium-source.py Sources/FantasqueSansMono-Regular.sfdir Sources/FantasqueSansMono-Medium.sfdir` and the equivalent Italic command. Confirm via `git diff --stat` that ONLY `font.props` metadata lines change (glyph geometry must be untouched per the idempotency record). Verify `font.props` now shows `Weight: Medium` and the upright `LangName` persists `"Medium"` (SubFamily slot). | SEC-002, CON-002 | [x] | 2026-08-16 |
| TASK-104 | **VERIFY (evidence):** build both weights locally (`make` or fontforge TTF/OTF export) and dump the SFNT name table + OS/2: `fontforge -lang=py -c 'import fontforge,sys; f=fontforge.open(sys.argv[1]); print(f.os2_weight); [print(n) for n in f.sfnt_names]'` on the built binaries. Assert: Family `Fantasque Sans Mono`, SubFamily `Medium` (upright) / `Medium Italic`, Fullname, PostScriptName, `os2_weight == 500` (GH-004 AC1). Record the dump output verbatim in `plan/plan-design-medium-weight-v1.1.md` Execution Results (new row) so GH-004 AC1/AC3 are evidenced in-repo. | SEC-002 | [x] | 2026-08-16 |
| TASK-105 | **VERIFY (regression):** `python -m pytest tests/ -q` 0 failures; width grid re-check `grep -h '^Width' Sources/FantasqueSansMono-Medium*.sfdir/*.glyph \| sort -u` → only `1060`; zero-touch `git diff --stat` on the CON-07 list empty. | SEC-002, CON-001 | [x] | 2026-08-16 |
| TASK-106 | **APPROVAL**: 🛑 Wait for explicit user confirmation to proceed to Phase 2. | - | [x] | 2026-08-16 |

### Implementation Phase 2: Upstream Doc-Sync & Evidence Closure (REQ-001..003)

- **GOAL-002:** Bring the PRD, spec, and plan into mutual consistency with the accepted deviations, and close every unevidenced criterion with either a recorded result or an explicit caveat.

| Task ID  | Description (Include Exact File Paths & Micro-Testing)                                                                                                                                                                                                                                                                                                                                                                                                      | Ref ID  | Completed | Date  |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | :-------: | :---: |
| TASK-201 | **PRD → v1.3** (`docs/prd-20260813-0921-medium-font-weight.md`): append a revision note recording the maintainer exception — residual self-intersections (252 upright / 465 italic) deferred to visual QA (GH-001 AC3 re-scoped), `validate-font` `Error in` baseline profile accepted (FR-08, §7.3, GH-003 AC3), mirroring how T-1/T-3 were remediated. Keep the AC text but mark the two criteria as `accepted-deviation` with reference to Spec §12/§13. | REQ-001 | [x] | 2026-08-16 |
| TASK-202 | **Nerd Font patching (FR-09 / Spec §13):** EITHER trigger a `custom-build` dispatch with `NerdFontPatching=true` on the test fork and record the output (`Fantasque Sans Mono Nerd Font Medium` / `... Medium Italic`) in the plan Execution Results, OR add an explicit `not executed (P2 optional, TASK-013(c))` caveat to Spec §13 so the criterion no longer overstates verified status. Record which option was taken. | REQ-002 | [x] | 2026-08-16 |
| TASK-203 | **Idempotency evidence placement:** add a row to `plan/plan-design-medium-weight-v1.1.md` Execution Results citing the recorded verification (`only font.props ModificationTime differs between two runs` — memory.instructions.md:227) or attach the fresh `diff -r` summary from TASK-103. | REQ-003 | [x] | 2026-08-16 |
| TASK-204 | **CON-07 list parity:** either add `generate-css-decl` to plan `CON-07`/§5 forbidden list (spec §1.1/§9 claim it as part of "the full CON-07 zero-touch set") or qualify the spec wording — pick one canonical list. | DOC-001 | [x] | 2026-08-16 |
| TASK-205 | **Version citations:** bump `Scripts/generate-medium-source.py` docstring ("Spec v1.2" → current) and `plan/plan-design-medium-weight-v1.1.md` §8/intro citations to spec v1.5 (PRD v1.2 citation stays valid). | DOC-002 | [x] | 2026-08-16 |
| TASK-206 | **AC-006 wording:** rephrase Spec §5 AC-006 "the selected variant" → "the selected variant(s)" for precision with the single-variant-per-dispatch reality. | DOC-003 | [x] | 2026-08-16 |
| TASK-207 | **AC-007 external trail:** record the PR review/approval reference (URL/comment) for the visual-QA sign-off in the plan execution record, externalizing the currently assertion-only trail. | CON-003 | [x] | 2026-08-16 |
| TASK-208 | **VERIFY:** markdown lint all touched docs; `git diff --stat` on the CON-07 list empty; `python -m pytest tests/ -q` still green; confirm no production build files changed. | CON-001 | [x] | 2026-08-16 |
| TASK-209 | **APPROVAL**: 🛑 Wait for explicit user confirmation to proceed to Phase 3. | - | [x] | 2026-08-16 |

### Implementation Phase 3: Supply-Chain Hygiene for build-make.yml (SEC-001)

- **GOAL-003:** Make the new workflow's third-party surface reviewable and deterministic, consistent with the security baseline (the repo's Dockerfile/custom-build.yml are unpinned — any stricter choice is an improvement, not a regression).

| Task ID  | Description (Include Exact File Paths & Micro-Testing)                                                                                                                                                                                                                                                                                          | Ref ID  | Completed | Date  |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | :-------: | :---: |
| TASK-301 | **Pin actions to commit SHAs** in `.github/workflows/build-make.yml`: resolve `actions/checkout@v7` and `actions/upload-artifact@v4` to full SHAs (e.g. `actions/checkout@<full-sha>`) with a comment noting the resolved tag/date. Follow the repo's existing workflow convention if it already pins somewhere; otherwise document the choice. | SEC-001 | [x] | 2026-08-16 |
| TASK-302 | **Version-constrain installs:** pin explicit versions for the `apt-get install` packages and `pip3 install pytest jsonschema future` (or add a comment documenting acceptance of the unpinned baseline inherited from Dockerfile Stages 1/2). Add `rm -rf /var/lib/apt/lists/*` after install to match the Dockerfile cache-cleanup convention. | SEC-001 | [x] | 2026-08-16 |
| TASK-303 | **VERIFY:** YAML validity (`python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/build-make.yml'))"`), review the resolved SHAs, and confirm the workflow still references only existing inputs/outputs. Full GH Actions execution is external — record a note that runtime re-validation happens on next dispatch. | SEC-001 | [x] | 2026-08-16 |
| TASK-304 | **APPROVAL**: 🛑 Wait for explicit user confirmation to proceed to Phase 4. | - | [x] | 2026-08-16 |

### Implementation Phase 4: Test Scaffolding Cleanup (PRN-001, PRN-002)

- **GOAL-004:** Remove misleading dead code from the reverted `intersect()` approach and make the operation-order assertion cover the full mandated sequence.

| Task ID  | Description (Include Exact File Paths & Micro-Testing)                                                                                                                                                                                                                                                                                                           | Ref ID           | Completed | Date  |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | :-------: | :---: |
| TASK-401 | **Remove dead scaffolding** from `tests/test_generate_medium_source.py` `FakeGlyph` (lines ~55-66): drop `remove_overlap_calls`, `intersect_calls`, `round_calls` counters and the `removeOverlap`/`intersect`/`round` methods if unasserted (keep only what the script actually invokes). | PRN-001 | [x] | 2026-08-16 |
| TASK-402 | **Order assertion completeness:** record `selection.all()` in `_operation_log` (extend `_FakeSelection.all()`), assert full order `["selection.all", "changeWeight", "removeOverlap", "simplify"]` in `test_geometry_operations_run_in_plan_order`, and replace the `_selection_called` boolean with a log-based assertion in `test_embolden_and_cleanup_calls`. | PRN-002 | [x] | 2026-08-16 |
| TASK-403 | **VERIFY:** `python -m pytest tests/ -q` — 0 failures, suite count matches expectations (81 + new weight/order tests); review the diff is tests-only. | PRN-001, PRN-002 | [x] | 2026-08-16 |
| TASK-404 | **APPROVAL**: 🛑 Final user sign-off. | - | [x] | 2026-08-16 |

## 3. Structural Remedies & Alternatives

- **ALT-001**: *Decompose `generate_medium()`* into `_apply_metadata(font, names)` and `_apply_geometry(font)` (A-10) — considered; deferred as OPTIONAL since the function is ~40 lines and unit-tested end-to-end via mocks. Revisit if a third pipeline variant appears.
- **ALT-002**: *Wrap `font.save()` in `try/finally: font.close()`* (A-11) — considered; rejected for a manually-run one-shot tool per Spec ASSUMPTION-001 (a failed save leaves no partial source; FontForge raises before writing).
- **ALT-003**: *Canonicalize symlinks in the input==output guard* (`os.path.realpath`, A-12) — considered; rejected as speculative — the maintainer invocation contract (REQ-02) uses literal paths; note the residual gap in a comment.
- **ALT-004**: *Reject or rewrite the feature* — rejected; the implementation is functionally correct and visually approved; findings are evidence/traceability/verification gaps, not functional defects.
- **ALT-005**: *Regenerate sources via a metadata-only fontforge one-liner instead of the script* — rejected; re-running the script is the reproducibility path (REQ-01) and the idempotency record proves geometry stays identical.

## 4. Dependencies

- **DEP-001**: `fontforge` (local) — required for TASK-103 regeneration and TASK-104 name-table dump verification (already present on the maintainer machine).
- **DEP-002**: `pytest` + `jsonschema` — already installed (unit gates).
- **DEP-003**: (Optional, TASK-202) a test fork + GitHub Actions access for the NerdFontPatching dispatch.
- **DEP-004**: (Phase 3) resolution of exact SHAs for `actions/checkout` and `actions/upload-artifact` at pin time. No new runtime dependencies introduced.

## 5. Files Affected

- **FILE-001**: `Scripts/generate-medium-source.py` — add `MEDIUM_WEIGHT_NAME` constant + `font.weight` assignment; docstring version bump.
- **FILE-002**: `tests/test_generate_medium_source.py` — new weight assertions, order assertion extension, dead-scaffolding removal.
- **FILE-003**: `Sources/FantasqueSansMono-Medium.sfdir/` + `Sources/FantasqueSansMono-MediumItalic.sfdir/` — regenerated (metadata-only changes per idempotency).
- **FILE-004**: `docs/prd-20260813-0921-medium-font-weight.md` — v1.3 revision note + accepted-deviation markers.
- **FILE-005**: `spec/spec-design-medium-weight.md` — §5 AC-006 wording, §13 Nerd Font caveat (if option b of TASK-202), §1.1/§9 list parity resolution.
- **FILE-006**: `plan/plan-design-medium-weight-v1.1.md` — Execution Results rows (name-table dump, idempotency, Nerd Font, AC-007 reference), CON-07 parity, §8 citations.
- **FILE-007**: `.github/workflows/build-make.yml` — pinned action SHAs, version-constrained installs, apt cache cleanup.

## 6. Testing Strategy

- **TEST-001**: Unit — `font.weight == "Medium"` assertion on both upright/italic mock paths (new).
- **TEST-002**: Unit — full geometry order `selection.all → changeWeight → removeOverlap → simplify` via `_operation_log` (extended).
- **TEST-003**: Integration — SFNT name-table dump of built TTF/OTF for both weights: Family/SubFamily/Fullname/PostScriptName + `os2_weight 500` (GH-004 AC1/AC3 evidence).
- **TEST-004**: Regression — width grid `1060` on all regenerated glyphs; zero-touch CON-07 diff empty; pytest suite 0 failures after every phase.
- **TEST-005**: Regression — idempotency re-run diff (geometry identical, `font.props` metadata-only).
- **TEST-006**: (Conditional) NerdFontPatching dispatch result recorded, or §13 caveat added.

## 7. Risks & Rollback Plan

- **RISK-001**: *Regeneration diff noise* — a script re-run could alter glyph files beyond metadata. **Mitigation**: idempotency record proves metadata-only deltas; TASK-103 gates on `git diff --stat` showing only `font.props`. **Rollback**: `git restore` the two `.sfdir` dirs; no geometry ever lost.
- **RISK-002**: *`font.weight` side effects on preferred names (ID 16/17)* — setting `"Medium"` may shift auto-derived preferred-family records. **Mitigation**: TASK-104 dump captures the full name table; if ID 16/17 regress, drop the assignment and rely on explicit `appendSFNTName` records + verify.
- **RISK-003**: *Pinning actions to SHAs breaks on next runner change* — SHAs are immutable; only a forced action upgrade requires re-pin (documented in the workflow comment). **Rollback**: revert the pin commit.
- **RISK-004**: *PRD revision rejected by stakeholder* — the deviation was maintainer-approved at plan/spec level; if product rejects, the alternative is to keep PRD v1.2 and accept the documented traceability gap (recorded in the audit trail). No code rollback needed.
- **RISK-005**: *GH Actions runtime behavior differs from static review (TASK-303)* — the workflow already ran green once; the next dispatch re-validates. **Rollback**: `git revert` the workflow change; custom-build path unaffected.
