<!-- markdownlint-disable -->

---
goal: "Fix Code Review Findings — Multi-Weight Variants Implementation (Review v1.0)"
version: 1.0
date_created: 2026-08-05
last_updated: 2026-08-05
owner: Fantasque Sans Mono Core Team
status: "Planned"
tags: ["refactor", "clean-code", "spec-compliance", "test-quality", "code-review"]
---

# Refactoring Plan — Multi-Weight Variants Code Review Findings

![Status: Planned](https://img.shields.io/badge/status-Planned-lightgrey)

## Introduction

This refactoring plan addresses the findings of the code review performed on the
Multi-Weight Variants implementation (Plan v1.13 / Spec v1.8) on 2026-08-05.
The review identified **2 CRITICAL**, **12 REQUIRED**, **5 NIT**, **2 OPTIONAL**,
and **1 FYI** finding across two axes (Standards vs Spec).

**Critical findings** (test bugs that will fail in container Stage 1, and
interpolation fallback divergence from `fontforge.interpolateFonts`) block the
spec-mandated coverage gate (§6.7) and break the determinism contract (GUD-001).

**Required findings** span spec compliance gaps (test #11 partial coverage,
hardcoded `T_FINAL` placeholder, missing `--cov-fail-under=90` enforcement),
code duplication (tangent-angle logic in two scripts), and defensive scripting
gaps (assembly silent skip on missing master, `packaging.sh` WOFF2 glob
without `nullglob`).

**Nit findings** are minor maintainability improvements (centralized weight
mapping, HTML escaping, `_parse_bool` over-acceptance).

The execution preserves CON-001 (legacy code untouched) and CON-002 (Workflow A).
All changes are surgical — minimum necessary modifications to existing files,
no scope creep into adjacent features.

> **EXECUTION DIRECTIVE FOR AI AGENTS (`/sdlc-write-code`):**
> You MUST execute this plan phase by phase. You MUST run the specific
> VERIFY task at the end of each phase. After a phase is tested, you
> **MUST STOP AND WAIT** for the user's explicit approval before
> proceeding to the next phase. **DO NOT SKIP PHASES.**

## 1. Traceability: Requirements & Constraints

Every task in Section 2 MUST trace back to one of the IDs below. New IDs
(`REF-XXX`) are introduced to capture code-review findings; existing IDs
(`REQ-XXX`, `PRN-XXX`, `SEC-XXX`, `CON-XXX`) are referenced from the parent
documents (Spec v1.8, Plan v1.13).

### 1.1 Code Review Findings (REF-XXX)

- **REF-001**: Fix parameter ordering bug in `tests/test_multi_weight_driver.py` — 6 test cases call `_interpolate_weight` with wrong positional argument order; tests would fail in container Stage 1 but are masked by `importorskip` in host runner.
- **REF-002**: Remove per-glyph blending fallback path in `_interpolate_weight` — diverges silently from `fontforge.interpolateFonts` semantics; Spec §4.6 mandates `font.interpolateFonts()` as the only interpolation interface.
- **REF-003**: Replace `T_FINAL=15.0` placeholder in Dockerfile with sourced-from-rubric mechanism; Spec r5 B2 + §4.11 requires calibrated value.
- **REF-004**: Extend `test_metadata_injection` to cover all weights (Light 300 → ExtraBold 800) and assert `os2_weight` per Spec r6 Q-08.
- **REF-005**: Fix `_generate_overlay` in `validate_interpolation.py` — current implementation exports only interpolated glyph, not side-by-side comparison despite docstring.
- **REF-006**: Extract shared tangent-angle computation into `Scripts/tangent_analysis.py` — DRY violation (identical logic in `validate_harmonization.py` and `validate_interpolation.py`).
- **REF-007**: Strengthen substance of weak tests in `test_validate_interpolation.py` and `test_multi_weight_driver.py` — multiple tests assert only `total_glyphs > 0` without verifying the specific status they claim to test.
- **REF-008**: Add `--cov-fail-under=90` to pytest invocation in Dockerfile RUN chain — Spec §6.7 mandates ≥ 90% coverage in container, currently unenforced.
- **REF-009**: Add `node_diff` and `contour_diff` fields in `validate_harmonization.py` fail-status output — Spec §4.5 schema requires these fields for fail cases.
- **REF-010**: Add fail-fast master existence validation in `_assemble_build_sources` — currently silent skip on missing master, producing incomplete assembly without diagnostic.
- **REF-011**: Make TTF output unconditional in `poc_interpolation.py` — Spec r3 K11 + AC-P02 require dual output (`.sfdir` + TTF), currently conditional on `--ttf` flag.
- **REF-012**: Improve `validate_config` in `configure.py` — surface all schema errors, not only the first; current behavior extends debugging cycle.
- **REF-013**: Fix incorrect x-height fallback in `generate_specimen.py` — currently uses `post.underlinePosition` (underline position, not x-height) as fallback for `os2.sxHeight`.
- **REF-014**: Centralize weight name → OS/2 number mapping in single constant — currently duplicated across 3 sites (multi_weight_driver, generate_specimen × 2).
- **REF-015**: Add `shopt -s nullglob` before WOFF2 glob in `packaging.sh` — current `set -euo pipefail` + `zip` + zero-matches causes failure.
- **REF-016**: Add HTML output escaping in `generate_specimen.py` — current `%` formatting injects raw text into HTML; safe today (hardcoded literals), fragile to future changes.

### 1.2 Architectural Principles (PRN-XXX)

- **PRN-001 (DRY)**: Don't Repeat Yourself — single source of truth for shared logic.
- **PRN-002 (Defensive Programming)**: Fail-fast with informative messages (GUD-002); never silently skip missing prerequisites.
- **PRN-003 (Spec Adherence)**: All implementation must trace to a Spec requirement; spec is the contract.

### 1.3 Security & Constraints

- **SEC-001**: No user data — no user data is collected, stored, or transmitted (Spec §3.3).
- **CON-001**: Legacy Code Preservation — `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`, root `Makefile` MUST NOT be modified.
- **CON-002**: Workflow A — FontForge `.sfdir` + `font.interpolateFonts()` only.
- **CON-007**: GitHub Actions Free-Tier — build MUST run on `ubuntu-latest` with time limit 360 minutes.
- **GUD-001**: Deterministic Build — two runs with identical input MUST produce byte-identical font files.
- **GUD-002**: Fail-Fast on Critical Error — heavy contour distortion MUST halt pipeline with non-zero exit + diagnostic.

## 2. Implementation Steps

> **⚠️ EXECUTION DIRECTIVE FOR AI AGENTS (`/sdlc-write-code`):**
> You MUST execute this plan phase by phase. You MUST run the specific
> VERIFY task at the end of each phase. After a phase is tested, you
> **MUST STOP AND WAIT** for the user's explicit approval before
> proceeding to the next phase. **DO NOT SKIP PHASES.**

### Implementation Phase 1: Critical Fixes — Test Bugs & Interpolation Contract

- **GOAL-001:** Eliminate the 2 CRITICAL findings — fix test parameter ordering
  bug (REF-001) and remove the divergent interpolation fallback path
  (REF-002). After this phase, the full test suite must pass in the
  `builder-fontforge` container Stage 1.

| Task ID  | Description (Include Exact File Paths)                                                                                                                                  | Ref ID  | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | :-------: | :--: |
| TASK-101 | **Fix test parameter ordering in `tests/test_multi_weight_driver.py`** — convert all 6 invocations of `_interpolate_weight` (tests #1, #3, #4, #5, #7, #9, #11) to use keyword arguments. Current signature: `_interpolate_weight(regular_font, bold_font, bold_path, factor, weight_name, output_dir, dry_run)`. Current test calls pass `(font_reg, font_bold, 0.5, "Medium", out_dir, dry_run=False)` — positionally assigns `0.5` to `bold_path`, `"Medium"` to `factor`, etc. After fix: each call uses `regular_font=`, `bold_font=`, `bold_path=`, `factor=`, `weight_name=`, `output_dir=`, `dry_run=` keyword form. | REF-001 |    [ ]    |      |
| TASK-102 | **Remove fallback per-glyph blending in `Scripts/multi_weight_driver.py` `_interpolate_weight`** (lines 150–225) — keep only the `fontforge.interpolateFonts(factor, bold_path)` branch. The fallback (a) does not preserve off-curve control point metadata, (b) silently skips contours with `len(ca) != len(cb)`, and (c) produces subtly different output from `interpolateFonts` — all silent failures violating GUD-001 determinism. Add fail-fast pre-check: `if not hasattr(fontforge, 'font') or not hasattr(ff.font(), 'interpolateFonts'): _die("fontforge.interpolateFonts not available — required by Spec §4.6")`. | REF-002 |    [ ]    |      |
| TASK-103 | **Improve substance of weak tests in `tests/test_validate_interpolation.py`** — strengthen assertions: (a) `test_warning_status`: assert `report["warning_count"] >= 1` and `report["fail_count"] == 0` (not just `total_glyphs > 0`); (b) `test_fail_status`: assert `report["fail_count"] >= 1` and `g["status"] == "fail"` for the bowtie glyph; (c) `test_overlay_png_generated`: actually require PNG file to exist after `os.listdir(overlay_dir)`; (d) `test_report_json_valid`: also assert `status` enum validity per Spec §4.11. | REF-007 |    [ ]    |      |
| TASK-104 | **Strengthen `test_metadata_injection` in `tests/test_multi_weight_driver.py`** (test #11) — loop through `(Regular, 400)`, `(Medium, 500)`, `(SemiBold, 600)`, `(Bold, 700)`, `(Light, 300)`, `(ExtraBold, 800)`. For each: assert `result.familyname == "Fantasque Sans Mono"`, `result.fullname == "Fantasque Sans Mono {Weight}"`, `result.os2_weight == {numeric}`. Uses keyword-arg invocation per TASK-101 fix. Trace: Spec r6 Q-08, §4.6 metadata contract, §5.3 AC-I03. | REF-004 |    [ ]    |      |
| TASK-105 | **Make TTF output unconditional in `Scripts/poc_interpolation.py`** — change `_interpolate_subset(regular_dir, bold_dir, output_dir, ttf_path)` signature so TTF generation always occurs. Replace `if ttf_path:` guard (line 232) with default path: `ttf_path = ttf_path or os.path.join(os.path.dirname(output_dir), "Medium.ttf")`. Spec r3 K11 + §5.2 AC-P02 require dual output unconditionally. Update docstring to clarify this is a fixed contract. | REF-011 |    [ ]    |      |
| TASK-10X | **VERIFY (Phase 1)**: Run the full pytest suite inside the `builder-fontforge` container Stage 1. Steps: (1) `docker build -t fantasque-test --build-arg BUILD_ARGS="--multi-weight" .`; (2) `docker run --rm fantasque-test bash -c "cd /build && pytest tests/ -v --cov=Scripts --cov-fail-under=90"`. All 4 FontForge-dependent test files MUST execute (not skip), all 30+ test cases MUST pass, coverage MUST be ≥ 90% (note: TASK-208 in Phase 2 enforces this gate). | -       |    [ ]    |      |
| TASK-10Y | **APPROVAL** 🛑 Wait for explicit user confirmation to proceed to Phase 2 | -       |    [ ]    |      |

### Implementation Phase 2: Spec Compliance & Code Quality

- **GOAL-002:** Address the 8 REQUIRED findings — Spec compliance gaps
  (`T_FINAL` placeholder, coverage gate, `node_diff`/`contour_diff` schema,
  metadata verification), code duplication (tangent-angle module), defensive
  scripting (assembly master check, WOFF2 nullglob, x-height fallback), and
  test improvements (validate_config error reporting).

| Task ID  | Description (Include Exact File Paths)                                                                                                                                  | Ref ID  | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | :-------: | :--: |
| TASK-201 | **Extract shared tangent-angle module to `Scripts/tangent_analysis.py`** — create new module with two exported functions: `compute_max_tangent_angle(glyph) -> float` and `extract_on_curve_triples(contour) -> List[Tuple[Point, Point, Point]]`. Refactor `Scripts/validate_harmonization.py` (lines 95–175) to import from new module; same for `Scripts/validate_interpolation.py` (lines 95–145). Add docstring noting Spec §4.5 / §4.11 contracts. Trace: PRN-001 (DRY), REF-006. | REF-006 |    [ ]    |      |
| TASK-202 | **Replace `T_FINAL=15.0` placeholder in `Dockerfile`** (line 95) with sourced-from-rubric mechanism. Recommended approach: `ARG T_FINAL` + `ENV T_FINAL=${T_FINAL:-15.0}` with comment explaining that `15.0` is pre-calibration default. The actual calibrated value should be passed at `docker build` time from `docs/audit/visual-quality-rubric.md` by the runbook. Update Plan Resolution F (which normalized the numbering but did not address the placeholder itself). Add comment block referencing Spec r5 B2 + §4.11 protocol. Trace: REF-003, Spec r5 B2, §4.11. | REF-003 |    [ ]    |      |
| TASK-203 | **Add `--cov-fail-under=90` to pytest in `Dockerfile`** (line 89) — extend the pytest command: `pytest tests/ -v --cov=Scripts --cov-report=term-missing --cov-report=xml:build/reports/coverage.xml --cov-fail-under=90`. The `--cov-fail-under=90` flag causes non-zero exit if coverage drops below 90% — this is what Spec §6.7 requires (currently unenforced). Trace: REF-008, Spec §6.7, Plan Resolution C (2026-08-04). | REF-008 |    [ ]    |      |
| TASK-204 | **Fix `_generate_overlay` in `Scripts/validate_interpolation.py`** (lines 148–185) — the function claims to produce a side-by-side comparison but only exports the interpolated glyph. Options: (a) Use Pillow to composite the two glyph bitmaps into one image; (b) Use FontForge's `font.draw()` API to draw both glyphs into a shared bitmap. Implement option (b) if Pillow is not available; fall back to (a) if Pillow is installed. Either way, the function MUST produce a file containing BOTH glyphs visually. Update docstring to match actual behavior. Trace: REF-005, Spec REQ-S04. | REF-005 |    [ ]    |      |
| TASK-205 | **Add `node_diff` and `contour_diff` fields in `Scripts/validate_harmonization.py` fail-status output** — in `_validate()` (lines 195–265), when a glyph fails `node_count_equal` or `contour_order_equal`, populate the corresponding `node_diff`/`contour_diff` dict (matching `detect_incompatibility.py` schema). Update the JSON Schema documentation in the script docstring. Add test cases to `tests/test_validate_harmonization.py` to verify the new fields are populated correctly on fail. Trace: REF-009, Spec §4.5 schema. | REF-009 |    [ ]    |      |
| TASK-206 | **Add fail-fast master existence validation in `_assemble_build_sources` in `Scripts/multi_weight_driver.py`** (lines 245–300) — before the copy loop, verify all 4 harmonized masters exist: `for master in ("Regular", "Bold", "Italic", "BoldItalic"): if not os.path.isdir(os.path.join(harmonized, master)): _die("harmonized master missing: %s" % os.path.join(harmonized, master))`. This mirrors the Dockerfile guard (r4 R5) and prevents silent incomplete assembly. Trace: REF-010, GUD-002, Plan r4 R5. | REF-010 |    [ ]    |      |
| TASK-207 | **Improve `validate_config` error reporting in `Scripts/configure.py`** (lines 130–152) — accumulate ALL schema errors and raise with a multi-line message listing up to 5 errors. Current behavior surfaces only `errors[0]`, extending debugging cycle. Change `if errors: ...` block to: `if errors: msgs = [f"  - {list(e.path)}: {e.message}" for e in errors[:5]]; raise ConfigValidationError("Invalid config.json:\n" + "\n".join(msgs))`. Add test case in `tests/test_configure.py` verifying multi-error reporting. Trace: REF-012, PRN-002. | REF-012 |    [ ]    |      |
| TASK-208 | **Fix x-height fallback in `Scripts/generate_specimen.py` `_extract_metrics`** (line 175) — current fallback `getattr(post, "underlinePosition", None)` is incorrect (`underlinePosition` is the underline position, not x-height). Better fallback: read from the `x` glyph's bbox (`glyf["x"].yMax`). Simplest fix: leave x-height as `None` and display "—" in the metrics table if `os2.sxHeight` is missing. This is honest about the limitation rather than reporting wrong data. Trace: REF-013. | REF-013 |    [ ]    |      |
| TASK-209 | **Add `shopt -s nullglob` before WOFF2 glob in `Scripts/packaging.sh`** (line 158) — current `( cd "${TTF_DIR}" && zip -q -r ... ./*.woff2 )` will fail under `set -euo pipefail` if zero `.woff2` files exist (e.g., woff2_compress failure). Wrap with nullglob and pre-check: `shopt -s nullglob; woff2_files=("${TTF_DIR}"/*.woff2); if [ ${#woff2_files[@]} -gt 0 ]; then ( cd "${TTF_DIR}" && zip -q -r ... ); fi`. Trace: REF-015, PRN-002. | REF-015 |    [ ]    |      |
| TASK-20X | **VERIFY (Phase 2)**: Re-run the full test suite in container Stage 1 (same as TASK-10X). All previous tests MUST still pass; NEW tests for TASK-201 (tangent module), TASK-205 (node_diff/contour_diff fields), TASK-207 (multi-error config) MUST pass. Confirm coverage gate triggers appropriately (test by temporarily lowering threshold and asserting failure). | -       |    [ ]    |      |
| TASK-20Y | **APPROVAL** 🛑 Wait for explicit user confirmation to proceed to Phase 3 | -       |    [ ]    |      |

### Implementation Phase 3: Code Hygiene & Documentation

- **GOAL-003:** Address the remaining 5 NIT + 2 OPTIONAL + 1 FYI findings —
  centralize weight mapping, add HTML escaping, remove `_parse_bool`
  over-acceptance, conditional `mkdir` cleanup, and update plan/SPEC
  documentation to match implementation reality.

| Task ID  | Description (Include Exact File Paths)                                                                                                                                  | Ref ID  | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | :-------: |      |
| TASK-301 | **Centralize weight name → OS/2 number mapping** — create `Scripts/font_weights.py` with `WEIGHT_OS2_CLASS = {"Light": 300, "Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700, "ExtraBold": 800}`. Refactor: (a) `Scripts/multi_weight_driver.py` (line 35, `WEIGHT_CLASS`) to import; (b) `Scripts/generate_specimen.py` `_weight_number()` (line 525) and inline dict in `_css_font_faces()` (line 195) to import. Trace: REF-014, PRN-001. | REF-014 |    [ ]    |      |
| TASK-302 | **Add HTML output escaping in `Scripts/generate_specimen.py`** — replace raw `%` formatting in `_write_*` functions with `html.escape()` calls on dynamic content. Currently safe (hardcoded `SAMPLE_TEXTS`), but fragile. Add `import html` at top of file. Trace: REF-016, SEC-001. | REF-016 |    [ ]    |      |
| TASK-303 | **Remove `yes`/`no` acceptance in `_parse_bool` in `Scripts/configure.py`** (line 380) — GitHub Actions `workflow_dispatch` boolean inputs only emit `true`/`false`. Remove `if s in ("true", "1", "yes")` and `if s in ("false", "0", "no")` mappings to only `true`/`false`/`1`/`0`. Update docstring. Trace: NIT, Spec consistency. | NIT-001 |    [ ]    |      |
| TASK-304 | **Clean up Dockerfile `mkdir -p build/reports` placement** — currently unconditional (line 70), creating empty directory in single-weight mode. Move into the `if echo "$BUILD_ARGS" | grep -q -- "--multi-weight"; then` branch (line 78+). Trade-off: minor (cleanup of artifact upload noise). Trace: NIT, Plan Resolution F. | NIT-002 |    [ ]    |      |
| TASK-305 | **Documentation sync** — update the following to reflect the post-refactor reality: (a) Plan v1.13 — TASK-0.X description mentions "pip3 install" but Dockerfile already does this; (b) Plan v1.13 — TASK-4.X verification "metadata Layer 2" should be backed by an actual test or shell-based verification (optional — defer if not feasible); (c) Spec v1.8 — confirm `os2_weight` range documented in test #11 description. | DOC-001 |    [ ]    |      |
| TASK-30X | **VERIFY (Phase 3)**: Run `pytest tests/ -v` in host runner (no FontForge, so all FontForge-dependent tests skip via `importorskip`). Confirm: (a) `python3 Scripts/configure.py --help` works; (b) `python3 Scripts/configure.py --form-large-line-height yes` now FAILS with clear error (ref NIT-001); (c) `python3 -c "from Scripts.font_weights import WEIGHT_OS2_CLASS; print(WEIGHT_OS2_CLASS)"` returns the expected dict; (d) `bash Scripts/packaging.sh --version` (or dry-run check) confirms nullglob is active. | -       |    [ ]    |      |
| TASK-30Y | **APPROVAL** 🛑 Wait for explicit user confirmation to finalize refactoring | -       |    [ ]    |      |

## 3. Structural Remedies & Alternatives

- **ALT-001 (Fallback path removal vs graceful degradation)**: Original
  implementation had per-glyph blending as fallback when `interpolateFonts`
  unavailable. Refactoring removes this entirely per REF-002. Alternative
  considered: keep fallback with a loud `::warning::` message to the build
  log. Rejected: silent degradation violates GUD-001 determinism contract,
  and the spec mandates `font.interpolateFonts()` as the only interpolation
  interface (§4.6). Fail-fast is correct.

- **ALT-002 (Tangent module location)**: Considered creating the shared
  module as `Scripts/_tangent.py` (private, underscore prefix) vs
  `Scripts/tangent_analysis.py` (public, importable from tests). Chose
  public naming because the unit tests in `tests/` will import from it
  (TASK-201 includes new tests for the module). Private prefix would
  signal "internal use only" and discourage test coverage.

- **ALT-003 (HTML escaping approach)**: Three options for output escaping
  in `generate_specimen.py`: (a) `html.escape()` on every dynamic value
  (minimal, no dependencies); (b) Jinja2 templates (cleaner, new dep);
  (c) Mako templates (similar trade-off). Chose (a) — minimal change,
  no new dependencies, sufficient for hardcoded sample text. Spec
  already requires `fontTools` as dev dependency; adding Jinja2 would
  expand dependency surface unnecessarily.

- **ALT-004 (T_FINAL sourcing)**: Three approaches considered for the
  threshold placeholder: (a) ARG-based with build-time override; (b)
  shell variable sourced from `visual-quality-rubric.md` at build time
  (parse markdown); (c) hardcode after PoC completes. Chose (a) — minimal
  change, allows CI to pass any value, doesn't require parsing markdown
  in Dockerfile. Spec r5 B2 explicitly rejects option (b) for runtime
  flexibility, but (a) is build-time, not runtime, and is the cleanest
  trade-off.

## 4. Dependencies

No new runtime dependencies are introduced by this refactoring plan.

- **DEP-001 (existing)**: FontForge Python 3 API (`fontforge` module) on
  ubuntu:26.04 (Spec DEP-001).
- **DEP-002 (existing)**: `pytest`, `jsonschema`, `pytest-cov` in Stage 1
  Docker image (already installed per r3 K2 + r5 MO-1).
- **DEP-003 (existing)**: `fontTools` for `generate_specimen.py` metric
  extraction (already a dev dependency).
- **DEP-NEW-001 (optional, deferred)**: Pillow (PIL) for `_generate_overlay`
  side-by-side composition (TASK-204). If FontForge's native `draw()` API
  suffices, Pillow is not needed. Decision deferred to implementation.

## 5. Files Affected

- **FILE-001** [MODIFY]: `Scripts/multi_weight_driver.py`
  - TASK-102: Remove fallback path in `_interpolate_weight`
  - TASK-301: Import `WEIGHT_OS2_CLASS` from new module
  - TASK-306: Add fail-fast master validation in `_assemble_build_sources`
  *(Note: FILE-006 in plan v1.13)*

- **FILE-002** [MODIFY]: `Scripts/validate_harmonization.py`
  - TASK-201: Import tangent functions from new module
  - TASK-205: Add `node_diff`/`contour_diff` fields in fail status
  *(Note: FILE-002 in plan v1.13)*

- **FILE-003** [MODIFY]: `Scripts/validate_interpolation.py`
  - TASK-201: Import tangent functions from new module
  - TASK-204: Fix `_generate_overlay` to produce real comparison
  *(Note: FILE-003 in plan v1.13)*

- **FILE-004** [MODIFY]: `Scripts/generate_specimen.py`
  - TASK-301: Import `WEIGHT_OS2_CLASS` from new module
  - TASK-302: Add `html.escape()` on dynamic content
  - TASK-303: Fix `_extract_metrics` x-height fallback
  *(Note: FILE-004 in plan v1.13)*

- **FILE-005** [MODIFY]: `Scripts/configure.py`
  - TASK-207: Improve `validate_config` to surface all errors
  - TASK-303: Remove `yes`/`no` in `_parse_bool`
  *(Note: FILE-009 in plan v1.13)*

- **FILE-006** [MODIFY]: `Scripts/poc_interpolation.py`
  - TASK-105: Make TTF output unconditional
  *(Note: FILE-005 in plan v1.13)*

- **FILE-007** [MODIFY]: `Scripts/packaging.sh`
  - TASK-209: Add `shopt -s nullglob` before WOFF2 glob
  *(Note: FILE-012 in plan v1.13)*

- **FILE-008** [MODIFY]: `Dockerfile`
  - TASK-202: Replace `T_FINAL=15.0` with ARG-based sourcing
  - TASK-203: Add `--cov-fail-under=90` to pytest invocation
  - TASK-304: Move `mkdir -p build/reports` into multi-weight branch
  *(Note: FILE-010 in plan v1.13)*

- **FILE-009** [MODIFY]: `tests/test_multi_weight_driver.py`
  - TASK-101: Fix parameter ordering (keyword args)
  - TASK-104: Extend `test_metadata_injection` for all weights
  *(Note: FILE-016 in plan v1.13)*

- **FILE-010** [MODIFY]: `tests/test_validate_interpolation.py`
  - TASK-103: Strengthen weak test assertions
  - TASK-201: New tests for tangent module integration
  *(Note: FILE-023 in plan v1.13)*

- **FILE-011** [MODIFY]: `tests/test_validate_harmonization.py`
  - TASK-201: New tests for tangent module integration
  - TASK-205: New tests for `node_diff`/`contour_diff` fields
  *(Note: FILE-015 in plan v1.13)*

- **FILE-012** [MODIFY]: `tests/test_configure.py`
  - TASK-207: New test for multi-error reporting
  *(Note: FILE-NEW, not in plan v1.13)*

- **FILE-013** [NEW]: `Scripts/tangent_analysis.py`
  - TASK-201: New shared module with `compute_max_tangent_angle()` and
    `extract_on_curve_triples()` functions
  *(Note: FILE-NEW, not in plan v1.13)*

- **FILE-014** [NEW]: `Scripts/font_weights.py`
  - TASK-301: New module with `WEIGHT_OS2_CLASS` constant
  *(Note: FILE-NEW, not in plan v1.13)*

- **FILE-015** [NEW]: `tests/test_tangent_analysis.py`
  - TASK-201: New unit tests for shared module
  *(Note: FILE-NEW, not in plan v1.13)*

## 6. Testing Strategy

The existing test suite (Plan v1.13 §6) forms the baseline. This refactoring
strengthens existing tests and adds new tests for new modules.

- **TEST-REF-001**: Verify TASK-101 fix — `test_multi_weight_driver.py` test
  cases #1, #3, #4, #5, #7, #9, #11 now invoke `_interpolate_weight` with
  keyword arguments and pass when run in container Stage 1 with FontForge
  available.

- **TEST-REF-002**: Verify TASK-102 fix — when `fontforge.interpolateFonts`
  is not available, `_interpolate_weight` exits non-zero with the expected
  error message. Mock the FontForge module in test to simulate missing API.

- **TEST-REF-004**: Verify TASK-104 — `test_metadata_injection` iterates
  through 6 weights (Light 300, Regular 400, Medium 500, SemiBold 600,
  Bold 700, ExtraBold 800) and asserts `familyname`, `fullname`, `os2_weight`
  for each.

- **TEST-REF-006**: Verify TASK-201 — `tests/test_tangent_analysis.py`
  unit tests for `compute_max_tangent_angle()` and `extract_on_curve_triples()`.
  Test cases: square glyph (90° corners), triangle (60° corners), degenerate
  cases (collinear points, < 3 points).

- **TEST-REF-008**: Verify TASK-203 — temporarily lower `--cov-fail-under`
  to 50% in a test build, confirm pytest exits non-zero. Restore to 90%
  and confirm exit 0.

- **TEST-REF-012**: Verify TASK-207 — provide a `config.json` with 2+ invalid
  fields, confirm `validate_config` raises `ConfigValidationError` with all
  errors listed (not just the first).

- **TEST-REF-015**: Verify TASK-209 — simulate `woff2_compress` failure
  (no `.woff2` files in TTF_DIR), confirm `packaging.sh` does NOT exit
  with error in single-weight mode.

- **TEST-REF-001-VERIFY (Phase 1)**: Run `pytest tests/ -v --cov=Scripts
  --cov-fail-under=90` in `builder-fontforge` container. All 30+ test
  cases pass; coverage ≥ 90%.

- **TEST-REF-002-VERIFY (Phase 2)**: Re-run Phase 1 verification after
  Phase 2 changes. All previous tests still pass; new tests for tangent
  module, `node_diff`/`contour_diff`, multi-error config all pass.

- **TEST-REF-003-VERIFY (Phase 3)**: Run host-runner smoke test (no
  FontForge) to confirm `_parse_bool` change, weight module import,
  HTML escaping do not break host-side tests.

## 7. Risks & Rollback Plan

- **RISK-001 (Coverage gate enforcement)**: Adding `--cov-fail-under=90`
  (TASK-203) may cause the build to fail if current coverage is below 90%.
  Mitigation: measure current coverage before enabling the gate; if below,
  add missing tests as part of Phase 2 rather than disabling the gate.
  Rollback: remove `--cov-fail-under=90` flag from Dockerfile (revert
  TASK-203 in isolation).

- **RISK-002 (Fallback removal breaks edge case)**: Removing the per-glyph
  blending fallback (TASK-102) means that if `fontforge.interpolateFonts`
  raises an exception for a specific glyph combination, the whole build
  fails. This is intended (fail-fast per GUD-002) but may surface latent
  issues. Mitigation: ensure the fail-fast pre-check distinguishes
  "FontForge API missing" from "interpolation failure for specific glyph"
  to provide informative error messages. Rollback: re-introduce fallback
  with loud `::warning::` (degraded but functional) if needed.

- **RISK-003 (Side-by-side overlay dependency)**: TASK-204 may require
  Pillow or FontForge's `draw()` API which has version-specific behavior.
  Mitigation: implement option (a) Pillow-based first; fall back to option
  (b) FontForge native; document any visual diff. Rollback: keep current
  behavior (export only interpolated glyph) with corrected docstring if
  visual side-by-side cannot be reliably produced.

- **RISK-004 (Centralized weight module breaks imports)**: Creating
  `Scripts/font_weights.py` (TASK-301) and refactoring 3 import sites
  may introduce circular imports or path issues. Mitigation: ensure the
  module has no imports beyond stdlib; verify all 3 refactored sites
  can `import` the new module in isolation. Rollback: revert imports
  to inline dicts.

- **RISK-005 (T_FINAL ARG change)**: Switching from inline `T_FINAL=15.0`
  to ARG-based `ARG T_FINAL` (TASK-202) means the build will fail without
  explicit `--build-arg T_FINAL=...` if default is not set. Mitigation:
  provide reasonable default in `ENV T_FINAL=15.0`; document the ARG in
  Plan v1.13 task description. Rollback: revert to inline assignment.

## 8. Related Specifications / Further Reading

- [Plan v1.13 — Multi-Weight Variants Implementation](../plan-feature-multi-weight-variants-v1.13.md)
- [Spec v1.8 — Multi-Weight Variants Technical Specification](../spec/spec-multi-weight-variants.md)
- [Code Review Report — Multi-Weight Variants Implementation (2026-08-05)](../docs/audit/code-review-multi-weight-variants-2026-08-05.md)
- [Clarification Report r6 — Spec Multi-Weight Variants (2026-08-01)](../docs/audit/clarification-report-spec-multi-weight-variants-2026-08-01-r6.md)
- [Clarification Report — Implementation Plan (2026-08-04)](../docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-04.md)

## 9. Changelog

| Version | Date       | Changes                                                              |
| ------- | ---------- | -------------------------------------------------------------------- |
| 1.0     | 2026-08-05 | Initial refactoring plan based on code review findings (2026-08-05) |

## 10. Rollback / Recovery Plan

If any phase of this refactoring breaks the build:

1. **Phase 1 rollback**: `git revert <commit-hash>` for all Phase 1
   changes. The container test suite returns to skipping FontForge-
   dependent tests via `importorskip`. Build succeeds but the original
   bugs return.

2. **Phase 2 rollback**: Revert Phase 2 commits. The shared tangent
   module is removed; each script reverts to inline tangent logic. The
   master existence validation in `_assemble_build_sources` is removed
   (relying on the Dockerfile guard as the sole validation point).

3. **Phase 3 rollback**: Revert Phase 3 commits. The weight number mapping
   is duplicated again across 3 sites; HTML escaping removed; `_parse_bool`
   accepts `yes`/`no` again.

4. **Full rollback**: `git revert <range-of-commits>` for the entire
   refactoring branch. The implementation returns to the pre-refactor
   state with the code review findings unaddressed.

5. **Alternative — partial rollback**: If only specific tasks cause
   issues, each task is small enough to be reverted individually with
   `git revert <commit>`.
