---
goal: Medium Font Weight — Remediate plan-as-record status overstatement (TASK-207) and documentation-precision NITs from the v1.0 refactor round
version: 1.1
date_created: 2026-08-16
last_updated: 2026-08-16
owner: Expert Code Reviewer
status: "Complete"
tags: ["refactor", "clean-code", "documentation", "traceability", "font"]
---
<!-- markdownlint-disable -->
# Introduction

![Status: Complete](https://img.shields.io/badge/status-Complete-brightgreen)

This plan remediates the findings of the second `/sdlc-code-review` of the Medium Font Weight refactor round (commit `96b6b4cc`, diff `49f166bc..96b6b4cc`, reviewed 2026-08-16). The v1.0 remediation itself is verified sound: SFNT naming evidenced, upstream docs synced, supply chain hardened, dead scaffolding removed, pytest 83/83, CON-07 zero-touch clean. This round closes only the residual documentation/traceability gaps — one REQUIRED (B-12: the refactor plan claims "23/23 ✅" while its own TASK-207 deliverable is honestly marked ⏳ pending in the design plan) and five NITs/FYIs of citation precision (A-13, A-14, B-13, B-15, A-17) plus two optional hardening refinements (A-16, A-18). No functional code changes are required.

**Execution Status (2026-08-16):** Phases 1–2 executed and approved — plan-as-record honesty (REQ-101, B-12) and documentation/test-precision NITs closed (DOC-101..104, PRN-101/102; findings A-13, A-14, B-13, B-15, A-17). Gates green: pytest 83/83, YAML parses, markdown lint clean, CON-07 and `.sfdir` zero-touch. **Phase 3 (OPTIONAL, SEC-101/A-16) deferred — maintainer declined the CI re-validation cost; version pins plus documented rationale remain the accepted middle tier (ALT-104); TASK-301/302 not executed, TASK-303 final sign-off recorded.** Plan status `Complete`. Task-ID note: this plan's TASK-207 (Phase 2 approval, signed off 2026-08-16) is distinct from `plan-refactor-medium-weight-v1.0.md` TASK-207 (AC-007 PR reference, externally pending on the `feat/medium-font-weight` PR open).

## 1. Traceability: Requirements & Constraints

- **REQ-101**: Restore plan-as-record honesty for TASK-207 — the AC-007 PR reference cannot be recorded until the `feat/medium-font-weight` PR is opened; both plans must agree on 22/23 complete + 1 externally blocked — finding B-12 (CON-003).
- **DOC-101**: Refresh the stale spec citation in the test module docstring ("Spec v1.2" → "Spec v1.6") — finding A-13.
- **PRN-101**: Initialize `FakeFont.weight` explicitly in the test fake so a dropped assignment fails with a clean assertion, not a raw `AttributeError` — finding A-14.
- **DOC-102**: Amend the TASK-103 verification wording in the v1.0 plan: the upright `font.props` LangName SubFamily slot is empty; FontForge derives name IDs 2/3 from `font.weight` at load/build (proven by the TASK-104 TTF dump) — finding B-13.
- **DOC-103**: Correct the workflow pin-provenance comment — `pytest`/`jsonschema` match the local macro-gate environment; `future` is CI-only — finding B-15.
- **DOC-104**: Sharpen the action-pin comments (resolved release lineage: checkout v7.0.1-prep, upload-artifact v4-lineage merge) for future re-pin audits — finding A-17.
- **PRN-102**: Add a one-line WHY comment in the script documenting that `os2_weight` must precede `weight` (OS2_WeightWidthSlopeOnly) — finding A-18.
- **SEC-101** *(optional)*: Strengthen the pip supply chain with `--require-hashes` via a committed `requirements.txt` — finding A-16. Executable only if the maintainer accepts the CI-verification cost; may be deferred.
- **CON-101**: This plan is documentation-and-test-only for production impact. The CON-07 zero-touch set (`Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, `features.py`) and all committed font sources (`.sfdir`, glyph geometry) MUST NOT change.
- **CON-102**: All plan-status edits must keep the design plan and the refactor plan mutually consistent (no new ✅/⏳ contradictions).

## 2. Implementation Steps

> **⚠️ EXECUTION DIRECTIVE FOR AI AGENTS (`/sdlc-write-code`):**
> You MUST execute this plan phase by phase. You MUST run the specific testing/verification task at the end of each phase. After a phase is tested, you **MUST STOP AND WAIT** for the user's explicit approval before proceeding to the next phase. **DO NOT SKIP PHASES.**

### Implementation Phase 1: Plan-as-Record Honesty (REQ-101)

- **GOAL-001:** Make both plans agree on the true TASK-207 state — 22/23 refactor tasks complete, 1 externally blocked on the PR opening — so downstream auditors never treat AC-007 external evidence as present.

| Task ID  | Description (Include Exact File Paths & Micro-Testing)                                                                                                                                                                                                                                                                                                                                                              | Ref ID  | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | :-------: | :--: |
| TASK-101 | In `plan/plan-refactor-medium-weight-v1.0.md`: change TASK-207's checkbox from `[x]` to `[ ]` (or `⏳`) and annotate it "blocked on PR open — recorded as pending in plan-design Execution Results". Update the Execution Status block and Introduction so "23/23 tasks ✅" becomes "22/23 tasks complete + 1 externally blocked (TASK-207, PR reference pending)". Keep everything else unchanged (surgical edit). | REQ-101 | [x] | 2026-08-16 |
| TASK-102 | In `plan/plan-design-medium-weight-v1.1.md`: confirm the TASK-207 Execution Results row already reads `⏳` pending (it does) and, if the v1.0 plan's "23/23" claim is quoted anywhere in the Execution Updates, amend that quote to "22/23 + 1 pending". Micro-check: `grep -n "23/23" plan/*.md` must return only consistent references to the corrected state. | REQ-101 | [x] | 2026-08-16 |
| TASK-103 | **VERIFY**: `grep -n "23/23" plan/*.md` shows no uncorrected overstatement; `git diff --stat` touches only the two plan files (no source/test/workflow files); both files re-read for ✅/⏳ agreement on TASK-207. | -       | [x] | 2026-08-16 |
| TASK-104 | **APPROVAL**: 🛑 Wait for explicit user confirmation to proceed to Phase 2. | -       | [x] | 2026-08-16 |

### Implementation Phase 2: Documentation & Test Precision (DOC-101..104, PRN-101/102)

- **GOAL-002:** Close the five citation-precision NITs and the two test-hygiene/comment NITs; keep all edits surgical and doc/test-only.

| Task ID  | Description (Include Exact File Paths & Micro-Testing)                                                                                                                                                                                                                                | Ref ID           | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | :-------: | :--: |
| TASK-201 | In `tests/test_generate_medium_source.py` module docstring: replace `(Spec v1.2 section 4.2)` with `(Spec v1.6 section 4.2)`. In `FakeFont.__init__`: add `self.weight = None` beside `self.os2_weight = None` so the new weight tests fail with a clean assertion if the assignment is dropped. | DOC-101, PRN-101 | [x] | 2026-08-16 |
| TASK-202 | In `plan/plan-refactor-medium-weight-v1.0.md` TASK-103 description (or its Execution Status): amend the "upright LangName persists 'Medium' (SubFamily slot)" wording to state the verified behavior — the upright `font.props` LangName SubFamily slot stays empty and FontForge derives name IDs 2/3 from `font.weight = "Medium"` at load/build (TASK-104 TTF dump proves the built font carries SubFamily `Medium`). | DOC-102          | [x] | 2026-08-16 |
| TASK-203 | In `.github/workflows/build-make.yml` install step comment: replace "versions match the local macro-gate environment as of 2026-08-16" with "pytest/jsonschema match the local macro-gate environment as of 2026-08-16; `future` is CI-only (legacy `past.builtins` import, not present locally)". | DOC-103          | [x] | 2026-08-16 |
| TASK-204 | In `.github/workflows/build-make.yml`: sharpen the two pin comments to note the resolved lineage (checkout: v7.0.1 release-prep, 2026-07-17; upload-artifact: v4-lineage merge, 2025-03-19) so future re-pin audits can diff against the exact release. | DOC-104          | [x] | 2026-08-16 |
| TASK-205 | In `Scripts/generate-medium-source.py` metadata block: add a one-line WHY comment above `font.os2_weight = MEDIUM_WEIGHT` — "os2_weight must be set before weight: the inherited OS2_WeightWidthSlopeOnly flag keeps the numeric class authoritative; TASK-104 dump proved no ID 16/17 side effects". | PRN-102          | [x] | 2026-08-16 |
| TASK-206 | **VERIFY**: `python -m pytest tests/ -q` — 83/83 green (A-14 init must not break anything); `python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/build-make.yml'))"` parses; markdown lint the two touched plan files; `git diff --stat` on the CON-07 list empty; `.sfdir` dirs untouched. | -                | [x] | 2026-08-16 |
| TASK-207 | **APPROVAL**: 🛑 Wait for explicit user confirmation to proceed to Phase 3 (or sign off and skip Phase 3). | -                | [x] | 2026-08-16 |

### Implementation Phase 3 (OPTIONAL): Supply-Chain Hash Pinning (SEC-101)

- **GOAL-003:** Raise the pip supply chain from version pins to hash-verified installs. Executable only if the maintainer accepts CI re-validation cost; otherwise record the deferral and skip.

| Task ID  | Description (Include Exact File Paths & Micro-Testing)                                                                                                                                                                                                                                            | Ref ID  | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | :-------: | :--: |
| TASK-301 | Create `.github/workflows/requirements-make.txt` with `pytest==9.1.1 --hash=sha256:...`, `jsonschema==4.26.0 --hash=sha256:...`, `future==1.0.0 --hash=sha256:...` (digests resolved from PyPI at implementation time). Update `build-make.yml` to `sudo pip3 install --break-system-packages --no-cache-dir --require-hashes -r .github/workflows/requirements-make.txt`. | SEC-101 |    [ ]    |      |
| TASK-302 | **VERIFY**: `pip3 install --require-hashes --dry-run -r` on the local machine (Python matching the runner); YAML parses; next workflow dispatch must be green. If the maintainer declines, record `deferred (OPTIONAL, A-16)` in this plan's Execution Status and skip Phase 3. | -       |    [ ]    |      |
| TASK-303 | **APPROVAL**: 🛑 Final user sign-off. | -       | [x] | 2026-08-16 |

## 3. Structural Remedies & Alternatives

- **ALT-101**: *Delete the pending TASK-207 row entirely* instead of marking it ⏳ — rejected; the pending row is the required external trail anchor (CON-003), removing it would hide the gap.
- **ALT-102**: *Rescope TASK-207 to "record pending status" and keep ✅* — rejected; the skill's completion semantics require the deliverable to exist; re-marking the v1.0 plan's task as pending is more honest than redefining it.
- **ALT-103**: *Fix B-13 by writing the LangName SubFamily record into the upright source* — rejected; regeneration with the script already persists `Weight: Medium` and FontForge derives the name table correctly at build (TASK-104 evidence); hand-editing `font.props` LangName would break the idempotency/reproducibility contract (REQ-01).
- **ALT-104**: *Full `--require-hashes` rollout in this round* — deferred to OPTIONAL Phase 3; version pins plus documented rationale are an accepted middle tier (SECURITY-HARDENING), and hash maintenance adds ongoing CI burden for a one-shot verification workflow.

## 4. Dependencies

- **DEP-001**: No new runtime dependencies. Phase 3 (optional) adds only `requirements-make.txt` with PyPI hash digests.
- **DEP-002**: `pytest` (local) for the Phase 2 VERIFY gate — already installed (9.1.1).

## 5. Files Affected

- **FILE-001**: `plan/plan-refactor-medium-weight-v1.0.md` — TASK-207 status + Execution Status/Introduction honesty (REQ-101), TASK-103 wording amendment (DOC-102).
- **FILE-002**: `plan/plan-design-medium-weight-v1.1.md` — quote correction only if the "23/23" claim is echoed (REQ-101).
- **FILE-003**: `tests/test_generate_medium_source.py` — docstring version bump + `FakeFont.weight` init (DOC-101, PRN-101).
- **FILE-004**: `.github/workflows/build-make.yml` — comment precision (DOC-103, DOC-104); Phase 3 adds hash-verified install (SEC-101).
- **FILE-005**: `Scripts/generate-medium-source.py` — one-line WHY comment only (PRN-102); no logic change.
- **FILE-006**: (Phase 3 only) `.github/workflows/requirements-make.txt` — new file.

## 6. Testing Strategy

- **TEST-001**: Regression — `python -m pytest tests/ -q` 83/83 after the `FakeFont` init change (the two weight tests must still pass via the script-set value).
- **TEST-002**: Static — `grep -n "23/23" plan/*.md` must show no uncorrected overstatement; both plans agree on TASK-207 state.
- **TEST-003**: YAML validity — `yaml.safe_load` on `build-make.yml` after comment edits.
- **TEST-004**: Zero-touch — `git diff --stat` on the CON-07 list and the two `.sfdir` trees is empty at every phase gate.
- **TEST-005**: Markdown lint on both touched plan files.
- **TEST-006**: (Phase 3) `pip3 install --require-hashes --dry-run` and the next workflow dispatch.

## 7. Risks & Rollback Plan

- **RISK-001**: *Doc edits accidentally touch task tables beyond TASK-207* — mitigation: surgical edits confined to the named cells; VERIFY re-reads both plans for ✅/⏳ agreement. Rollback: `git restore` the two plan files.
- **RISK-002**: *`FakeFont.weight` init masks a real regression* — the init value is `None`; the tests assert `== "Medium"`, so a dropped script assignment still fails. Rollback: revert the one-line init.
- **RISK-003**: *Phase 3 hashes resolve incorrectly or go stale on next PyPI change* — pinned `==` versions are immutable on PyPI (files are not overwritten); rollback: `git revert` the workflow change.
- **RISK-004**: *Comment-only workflow edit triggers an unexpected dispatch* — YAML validity is re-verified (TEST-003); runtime re-validation happens on the next manual `workflow_dispatch` only. Rollback: revert.
