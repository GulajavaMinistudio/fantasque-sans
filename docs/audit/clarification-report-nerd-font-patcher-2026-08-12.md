<!-- markdownlint-disable MD024 -->

# 🔍 Clarification Report [Review Iteration 2]

> [!SUCCESS]
> **REMEDIATION STATUS: RESOLVED**
> This audit report has been remediated by Specification Architect.
> - **Projected Readiness Score:** 97/100

**Target Document:** [`spec/spec-process-nerd-font-patcher.md`](../../spec/spec-process-nerd-font-patcher.md) (v1.0)
**Upstream Document:** [`docs/prd-20260811-1351-nerd-font-patcher.md`](../prd-20260811-1351-nerd-font-patcher.md) (v1.0)
**Date:** 2026-08-12
**Analyst:** Clarification Analyst (`/sdlc-clarify-reqs`)

**Readiness Score:** 92/100 (current document) → **97/100 (projected after all resolutions applied)**
**Status:** Good Enough ✅

**Score Breakdown (current document, pre-fix):**

- **Completeness (max 40):** 35 — All 14 PRD user stories map 1:1 to spec ACs (AC-101..AC-114). All 10 FRs map to REQs. 9 ASSUMPTION tags present. Deductions: ASSUMPTION-009 undercount (-1), unconditional staging gap (-1), missing `LargeLineHeight` × `--adjust-line-height` edge case (-1), missing staging error isolation (-1), §4.5 code sample inaccuracy (-1).
- **Clarity (max 30):** 27 — Exceptionally structured with code samples, invocation matrices, edge case catalog. Deductions: §4.5 undefined shell variables (-1), manifest divergence not explained (-1), `nf_failure` output unused (-1).
- **Alignment (max 30):** 28 — Full PRD traceability via GH/FR/REQ references. Domain terms match CONTEXT.md. Deductions: PRD FR-004 vs ASSUMPTION-003 (-0.5), PRD GH-011 vs ASSUMPTION-009 (-0.5), PRD §8.1 "3 steps" vs 4+ (-0.5), release title `true+failed` case (-0.5).
- **Critical Flaw Veto:** No — All findings resolved during interactive session.

**Score Breakdown (projected, post-fix):**

- **Completeness:** 39/40 — All gaps addressed by user-approved resolutions.
- **Clarity:** 29/30 — All code samples corrected, semantics documented.
- **Alignment:** 29/30 — All PRD tensions resolved with documented rationale.
- **Projected Total:** 97/100

---

## 1. 🚨 Critical Findings (Blockers)

None. All critical findings were resolved during the interactive session (see §2 below).

---

## 2. 🧩 Resolved Items & Agreements

### FINDING-001: Unconditional Font Staging in `packaging.sh` Violates REQ-010 (CRITICAL → RESOLVED)

- **Requirement:** REQ-010 — *"no new steps execute, no new output files are produced"* when `NerdFontPatching=false`; PRD GH-011 — *"produces identical output to the current V1 pipeline"*
- **Issue:** Spec §4.5 adds a font staging block to `packaging.sh` that copies TTF/OTF files to `output/TTF/` and `output/OTF/` **unconditionally** — even when `NerdFontPatching=false`. This creates new output files on the runner filesystem that did not exist in V1, violating the "no new output files" contract.
- **Resolution:** **Conditional staging via environment variable.** The workflow SHALL pass `-e NERD_FONT_STAGING=true` to the Docker container (Step 7) **only** when `NerdFontPatching` resolves to `true`. `packaging.sh` SHALL wrap the staging block in an `if [ "${NERD_FONT_STAGING:-false}" = "true" ]` guard. When `NerdFontPatching=false`, `packaging.sh` behaves 100% identically to V1 — zero side effects.
- **Spec Impact:** §4.5 code sample must be rewritten with the conditional guard. §4.6 must specify that Step 7 passes the `NERD_FONT_STAGING` env var to Docker. REQ-010 and AC-111 wording remain unchanged.

### FINDING-002: ASSUMPTION-009 Undercounts Affected Tests (SIGNIFICANT → RESOLVED)

- **Requirement:** ASSUMPTION-009 — *"Existing tests asserting the exact 4-option surface MUST be updated to 5 options"*
- **Issue:** The spec explicitly names 4 tests that need updating, but codebase verification reveals **~10 locations** in `tests/test_configure.py` that hard-code the 4-option surface, including:
  1. `test_schema_has_four_boolean_properties` (named in spec)
  2. `test_all_defaults` in `TestResolveOptions` (named in spec)
  3. `test_mixed_precedence_all_four_sources` (named in spec)
  4. `test_emits_one_line_per_option` (named in spec)
  5. `empty_form` fixture (NOT named)
  6. `test_all_defaults` in `TestComputeConfigSource` (NOT named)
  7. `test_empty_string_when_all_defaults` (NOT named)
  8. `test_use_hinted_is_not_a_driver_flag` (NOT named)
  9. `test_single_flag` (NOT named)
  10. `test_multiple_flags_space_separated` (NOT named)
- **Resolution:** **Generalize ASSUMPTION-009 wording.** Replace the explicit 4-test list with a generalized instruction: *"ALL tests and fixtures that hard-code the 4-option surface (dictionary keys, counts, log-line assertions) MUST be updated to 5 options. Use `grep -n` for `UseHinted` across `test_configure.py` to enumerate all affected locations (~10 at time of writing)."* The current 4 test names are retained as examples, not as an exhaustive list.
- **Spec Impact:** ASSUMPTION-009 text must be rewritten. AC-111 wording ("The four mechanical 4-option test fixtures") should reference the generalized instruction.

### FINDING-003: PRD FR-004 vs ASSUMPTION-003 — `nerd_font_version` Presence Semantics (SIGNIFICANT → RESOLVED)

- **Requirement:** PRD FR-004 — *"When `NerdFontPatching = true`, the `manifest.json` MUST include `nerd_font_version`"*; Spec ASSUMPTION-003 — *"`nerd_font_version` is emitted only on patching success"*
- **Issue:** PRD FR-004 literally implies `nerd_font_version` is always present when the option is `true`. The spec refines this: only emit when patching actually succeeds. When `NerdFontPatching=true` but Docker Hub is down → no `nerd_font_version` in manifest.
- **Resolution:** **ASSUMPTION-003 accepted as a valid refinement of PRD FR-004.** PRD FR-004 implicitly assumes the success path. The spec correctly handles the failure path: a key representing a version "used" is semantically dishonest when the patcher was never executed. Key absence is more truthful than a sentinel value (`"FAILED"`, `null`). This interpretation is consistent with AC-106 which already distinguishes success vs failure cases.
- **Spec Impact:** None — ASSUMPTION-003 is already correctly worded. This report documents the rationale for future auditors.

### FINDING-004: Manifest Divergence in `custom-build` Artifact (MODERATE → RESOLVED)

- **Requirement:** CON-006 — *"base archives MUST be byte-identical to V1 output"*; ASSUMPTION-004 — *"`nerd_font_version` is stamped into the host-level `output/manifest.json`"*
- **Issue:** After NF success, Step 7.3 stamps `nerd_font_version` into `output/manifest.json`. Step 8 then uploads this stamped manifest as part of the `custom-build` artifact. The manifest inside the base zip/tar.gz (sealed in Stage 2) does NOT contain `nerd_font_version`. The `custom-build` artifact contains two manifests with different contents.
- **Resolution:** **Accept divergence, document semantics.** The standalone `output/manifest.json` serves as the *"run manifest"* (describing the entire build run including NF outcome). The manifest inside each archive serves as the *"archive manifest"* (describing only the contents of that specific archive). This is a logical consequence of CON-006 and is not a bug.
- **Spec Impact:** §4.4 must add 1–2 sentences clarifying the "run manifest" vs "archive manifest" distinction.

### FINDING-005: Missing Edge Case — `LargeLineHeight=true` × `--adjust-line-height` Interaction (MODERATE → RESOLVED)

- **Requirement:** REQ-002 — patcher uses `--adjust-line-height` on all variants; existing build option `LargeLineHeight` also modifies font line height metrics.
- **Issue:** Both `LargeLineHeight` (Stage 1) and `--adjust-line-height` (Stage 3 patcher) modify the same font metrics (OS/2 `sTypoAscender`/`sTypoDescender`, hhea `ascent`/`descent`). When both are active, the patcher's `--adjust-line-height` likely **overrides** Stage 1's `LargeLineHeight` adjustment. The Nerd Font Variant may not preserve the user's intended `LargeLineHeight` setting. This interaction is not documented in §12.2 (which covers `UseHinted=false` but not `LargeLineHeight=true`).
- **Resolution:** **Document as known behavior in §12.2.** Add edge case: *"When `LargeLineHeight=true`, the patcher's `--adjust-line-height` may override the Stage 1 line height adjustment. The Nerd Font Variant's line height is determined by the patcher, not by the `LargeLineHeight` option. This is accepted because `--adjust-line-height` is necessary for correct Powerline glyph rendering. Users can adjust line height in their terminal emulator settings."* `--adjust-line-height` remains unconditional (not gated on `LargeLineHeight`) to avoid Powerline glyph clipping.
- **Spec Impact:** §12.2 must add this edge case entry.

### FINDING-006: Staging Copy Failure Inside `packaging.sh` Could Fail Base Build (MODERATE → RESOLVED)

- **Requirement:** REQ-006 — *"The base build MUST NEVER fail due to a Nerd Font failure"*; `packaging.sh` runs with `set -euo pipefail` (§8 Code Style).
- **Issue:** The font staging block (§4.5) runs **inside** `packaging.sh`, which uses `set -euo pipefail`. If the staging copy fails (e.g., disk full, I/O error), `set -e` terminates the entire script, causing Step 7 (Stage 2 packaging) to fail — thus failing the base build. This violates REQ-006 because the staging copy is a NF-only operation whose failure should never propagate to the base build.
- **Resolution:** **Subshell error isolation.** The staging block SHALL be wrapped in a subshell `(...)` with `|| echo "::warning::Font staging for Nerd Font patching failed. Stage 3 will be skipped."`. The subshell isolates `set -e` — a failure inside it does not terminate the parent script. The warning is emitted for diagnostic purposes and can be consumed by Step 7.1 to determine whether patching should proceed.
- **Spec Impact:** §4.5 code sample must wrap the staging block in a subshell with error-safe fallback. Combined with FINDING-001's conditional guard.

---

## 3. ⚠️ Assumed / Auto-Resolved / Out of Scope (The 20% We Skip)

### INFO-001: §4.5 Code Sample Uses Undefined Shell Variables

- **Scenario / Question:** The code sample in Spec §4.5 (lines 247–254) references `${TTF_DIR}` and `${OTF_DIR}`, but `Scripts/packaging.sh` does not define these variables. The script defines `readonly APP_DIR="/app"` and `readonly OUTPUT_DIR="${APP_DIR}/output"`. Font files reside at `/app/TTF` and `/app/OTF`.
- **Handling:** `[Assumed / Auto-Resolved]` — The Spec author MUST replace `${TTF_DIR}` with `"${APP_DIR}/TTF"` and `${OTF_DIR}` with `"${APP_DIR}/OTF"` (or define new `readonly` variables) when revising §4.5. This is a factual correction, not a design decision.

### INFO-002: `nf_failure` Step Output Set But Never Consumed

- **Scenario / Question:** Step 7.1 sets `nf_failure=image-pull` on pull failure (Spec §4.6, line 270), but no downstream step reads this output. If intended for job summary diagnostics, the consumption mechanism should be specified. If not needed, it should be removed.
- **Handling:** `[Assumed / Auto-Resolved]` — Recommend retaining `nf_failure` as a diagnostic output for the job summary step (Step 9). The Spec author should either (a) add `nf_failure` consumption in §4.6 Step 9 description, or (b) remove the output if granular failure typing is not needed. Low impact either way.

### INFO-003: PRD §8.1 Says "3 New Conditional Steps" But Spec Defines 4+

- **Scenario / Question:** PRD §8.1 states *"Add `workflow_dispatch` input + 3 new conditional steps after Stage 2 packaging"* but the spec defines 4 new steps (7.1 Pull, 7.2 Patch, 7.3 Package, 7.4 Upload) plus an enablement resolution step.
- **Handling:** `[Assumed / Out of Scope]` — PRD §8 is labeled "Technical considerations (Input for Engineering Team)" and is informational, not normative. The actual functional requirements (FR-002, FR-003, FR-006, FR-008) define the required behavior, and these are fully covered by the spec's 4-step design. No action required.

### INFO-004: Release Title for `NerdFontPatching=true` + Patching Failed

- **Scenario / Question:** PRD GH-009 defines two cases: `true` → include `NerdFont` label, `false` → no label. The spec adds a third case (§4.8): `true + failed` → no `NerdFont` label. This is not explicitly covered by the PRD.
- **Handling:** `[Assumed / Auto-Resolved]` — Same principle as FINDING-003: the PRD assumes the success path. The spec's refinement is logically correct — the release title should reflect what is actually IN the release. If NF archives are not attached (because patching failed), the title should not claim `NerdFont`. Consistent with the spec's overall graceful-failure design (REQ-006).

---

## 4. 📝 Next Steps

1. **Spec Revision Required:** The Spec author (`/sdlc-define-specs`) MUST apply the following changes to [`spec/spec-process-nerd-font-patcher.md`](../../spec/spec-process-nerd-font-patcher.md) and bump to **v1.1**:

   | Finding | Spec Section | Change Required |
   |---------|-------------|-----------------|
   | FINDING-001 | §4.5 | Rewrite code sample with conditional `if [ "${NERD_FONT_STAGING:-false}" = "true" ]` guard |
   | FINDING-001 | §4.6 | Specify Step 7 Docker run passes `-e NERD_FONT_STAGING=...` |
   | FINDING-002 | ASSUMPTION-009 | Generalize from 4-test list to grep-based enumeration (~10 locations) |
   | FINDING-002 | AC-111 | Update "four mechanical" reference to generalized instruction |
   | FINDING-003 | (none) | No change needed — rationale documented in this report |
   | FINDING-004 | §4.4 | Add "run manifest" vs "archive manifest" clarification |
   | FINDING-005 | §12.2 | Add `LargeLineHeight × --adjust-line-height` edge case |
   | FINDING-006 | §4.5 | Wrap staging block in subshell `(...)` with `|| echo "::warning::"` |
   | INFO-001 | §4.5 | Replace `${TTF_DIR}`/`${OTF_DIR}` with `${APP_DIR}/TTF`/`${APP_DIR}/OTF` |
   | INFO-002 | §4.6 | Clarify `nf_failure` consumption in Step 9, or remove |

2. **No CONTEXT.md Updates Needed:** All domain terms are already present and correct.

3. **No New ADR Needed:** All resolved findings are implementation-level, reversible, and do not meet the triple-gate criteria.

4. **Next SDLC Phase:** After spec revision (v1.1), proceed to `/sdlc-plan-tasks` to create the implementation plan.

---

> **User Decision Prompt:**
> The document has achieved a current Readiness Score of **92/100** (projected **97/100** after all 6 resolutions are applied). It is ready for the next phase. Do you want to **PROCEED** to the next phase (`/sdlc-plan-tasks`), or do you want to **REFINE** and clarify further?
