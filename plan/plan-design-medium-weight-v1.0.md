---
goal: Medium Font Weight — Generate, commit, and verify Medium (500) and Medium Italic sources through the zero-touch build pipeline
version: 1.0
date_created: 2026-08-13
last_updated: 2026-08-13
owner: Planner Architect
status: Planned
tags: [font, design, medium-weight, python, fontforge, build]
---

<!-- markdownlint-disable -->

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan implements the **Medium Font Weight** feature as defined in the approved Technical Specification `spec/spec-design-medium-weight.md` (v1.2) and PRD `docs/prd-20260813-0921-medium-font-weight.md` (v1.2).

The feature introduces a Medium (CSS weight 500) and Medium Italic variant to the Fantasque Sans Mono family. A single standalone Python script (`Scripts/generate-medium-source.py`) algorithmically emboldens the existing Regular and Italic sources via FontForge's `ChangeWeight` API. The resulting `.sfdir` sources are committed directly to the repository, after which the existing Makefile wildcard, variant builder, CSS declaration generator, packaging scripts, and CI/CD pipeline compile and distribute the new variants with **zero modifications** to the core build infrastructure.

## 1. Requirements & Constraints

### Requirements (from Spec §3)

- **REQ-01**: A single Python script `Scripts/generate-medium-source.py` must generate the Medium `.sfdir` sources.
- **REQ-02**: The script must accept exactly two arguments: the input source `.sfdir` path and the output `.sfdir` path.
- **REQ-03**: The script must preserve the italic angle and all other style-specific metrics of the input source. For Medium Italic, the OS/2 italic flag must remain set.

### Constraints (from Spec §3)

- **CON-01**: The script must use FontForge's `ChangeWeight` API to add weight.
- **CON-02**: Every generated glyph must have its advance width strictly set to exactly `1060`.
- **CON-03**: The script must call `removeOverlap()` and `simplify()` on all modified glyphs.
- **CON-04**: The generated `.sfdir` source must have its `os2_weight` property set to `500`.
- **CON-05**: The script must be functionally idempotent — running it multiple times with the same input produces identical contour geometry and metrics. Differences in non-functional metadata (e.g., timestamps) are permitted.
- **CON-06**: The script must never modify the input source `.sfdir` in place. It may only read from the input path and write to the output path.
- **CON-07** *(plan-level, from Spec §9)*: Zero-touch mandate — `Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, and `features.py` MUST NOT be modified by any task in this plan.

### Guidelines (from Spec §3)

- **GUD-01**: The stroke expansion applied via `ChangeWeight` should fall within +30 to +40 em-units (reference value: 34) to produce a weight visually distinct from both Regular and Bold.

### Traceability Anchors (PRD)

- **GH-001**: Generate Medium font source from Regular.
- **GH-002**: Generate Medium Italic font source from Italic.
- **GH-003**: Build Medium variants through standard Makefile.
- **GH-004**: Correct SFNT metadata for Medium weight.
- **GH-005**: CSS font-face declarations for Medium weight.
- **GH-006**: Visual quality validation of core ASCII glyphs.
- **GH-007**: Release packaging includes Medium variants.
- **GH-008**: CI/CD pipeline builds Medium variants.

## 2. Implementation Steps

> **EXECUTION DIRECTIVE FOR AI AGENTS:**
> You MUST execute this plan phase by phase. You MUST run the specific testing/verification task at the end of each phase. After a phase is tested, you **MUST STOP AND WAIT** for the user's explicit approval before proceeding to the next phase.

### Implementation Phase 1: Generation Script & Medium Upright Source

- GOAL-001: Deliver the `Scripts/generate-medium-source.py` script with unit tests, generate the Medium upright source from Regular, and prove automated correctness (metadata, monospace grid, idempotency) — AC-001 closed end-to-end.

| Task | Description | Ref ID | AC Ref | Dep | Files | Completed | Date |
| ---- | ----------- | ------ | ------ | --- | ----- | --------- | ---- |
| TASK-001 | **Create `Scripts/generate-medium-source.py`** (Spec §4.1, §4.2, §8): A maintainer runs `python Scripts/generate-medium-source.py <input.sfdir> <output.sfdir>` and gets a valid Medium `.sfdir`. Implement: (a) two-positional-argument parsing via `sys.argv` with usage message and non-zero exit on wrong argument count (REQ-02); (b) guard `input_sfdir == output_sfdir` → error exit (CON-06); (c) `generate_medium(input_sfdir, output_sfdir)`: open input, detect italic via `os.path.basename(input_sfdir).startswith("FantasqueSansMono-Italic")`, set `font.os2_weight = 500`, `familyname = "Fantasque Sans Mono"`, `fontname`/`fullname` per Spec §4.2 table, plus `font.appendSFNTName('English (US)', ...)` for Family/SubFamily/Fullname/PostScriptName ("Medium" or "Medium Italic"); (d) `font.selection.all()`, `font.changeWeight(34, "LCG", 0, 0, "Retain")`, `font.removeOverlap()`, `font.simplify()` (CON-01, CON-03, GUD-01); (e) loop `for glyph in font.glyphs(): glyph.width = 1060` (CON-02); (f) `font.save(output_sfdir)`, `font.close()` — never writes to the input path (CON-06). Italic angle and OS/2 italic flag are preserved by non-modification (REQ-03). Deterministic operation order, no timestamp/random-dependent logic (CON-05). Use Python 3 (the `python` launcher), matching the host runner environment. | REQ-01, REQ-02, REQ-03, CON-01, CON-02, CON-03, CON-04, CON-05, CON-06, GUD-01 | AC-001, AC-002 | - | 1 | | |
| TASK-002 | **Add unit tests `tests/test_generate_medium_source.py`**: Tests must run WITHOUT a real fontforge installation (the CI host runner only has `jsonschema` + `pytest`). Inject a fake `fontforge` module via `sys.modules` (monkeypatch) before importing the script module. Cover: (a) zero/one/three arguments → non-zero exit with usage; (b) `input == output` path → error exit (CON-06); (c) upright input → `os2_weight == 500`, `fontname == "FantasqueSansMono-Medium"`, `fullname == "Fantasque Sans Mono Medium"`, SFNT SubFamily == "Medium"; (d) italic-detected input → `fontname == "FantasqueSansMono-MediumItalic"`, SFNT SubFamily == "Medium Italic"; (e) `changeWeight` called with `(34, "LCG", 0, 0, "Retain")`; (f) `removeOverlap` and `simplify` called once each; (g) every mock glyph `width` set to `1060`; (h) `save` called only with the output path (never the input path). Existing 69 tests in `tests/test_configure.py` remain untouched. | REQ-02, CON-01, CON-02, CON-03, CON-04, CON-05, CON-06 | AC-001 | TASK-001 | 1 | | |
| TASK-003 | **Generate `Sources/FantasqueSansMono-Medium.sfdir`**: Run `python Scripts/generate-medium-source.py Sources/FantasqueSansMono-Regular.sfdir Sources/FantasqueSansMono-Medium.sfdir` from the repository root. The output directory is produced with all glyphs emboldened and metadata set. *High Risk — ASSUMPTION-002 (34 em-unit stroke is the reference value; visual tuning may follow later).* | REQ-01, GUD-01 | AC-001 | TASK-001 | 1 | | |
| TASK-004 | **VERIFY**: (a) Run `python -m pytest tests/ -v` — all tests pass with 0 failures (69 existing + new script tests). (b) Run `Scripts/validate-font Sources/FantasqueSansMono-Medium.sfdir` and confirm the output contains **no** `Error in ...` line (exit code is always `0` by design — output inspection is the signal). (c) Metadata: `fontforge -lang=py -c 'import fontforge,sys; f=fontforge.open(sys.argv[1]); print(f.os2_weight)' Sources/FantasqueSansMono-Medium.sfdir` prints `500`. (d) Monospace grid: all glyphs report `width == 1060` (fontforge one-liner iterating `font.glyphs()`). (e) Idempotency: run the script twice into two scratch output dirs and confirm `diff -r` on the per-glyph files reports no differences in contour geometry/metrics. | - | AC-001 | TASK-002, TASK-003 | - | | |
| TASK-005 | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 2. | - | - | TASK-004 | - | | |

### Implementation Phase 2: Medium Italic Source & Canonical Commit

- GOAL-002: Generate the Medium Italic source with italic metrics preserved, verify SFNT naming correctness, and commit both `.sfdir` sources as canonical repository inputs — AC-002 and FR-03 closed.

| Task | Description | Ref ID | AC Ref | Dep | Files | Completed | Date |
| ---- | ----------- | ------ | ------ | --- | ----- | --------- | ---- |
| TASK-006 | **Generate `Sources/FantasqueSansMono-MediumItalic.sfdir`**: Run `python Scripts/generate-medium-source.py Sources/FantasqueSansMono-Italic.sfdir Sources/FantasqueSansMono-MediumItalic.sfdir`. The script auto-detects the italic source by basename and applies the identical embolden transformation. Italic angle and OS/2 italic flag are carried over unchanged (REQ-03). *High Risk — ASSUMPTION-002 applies equally to the italic output.* | REQ-03, GUD-01 | AC-002 | TASK-001 | 1 | | |
| TASK-007 | **Commit canonical sources** (Spec §1.2 ASSUMPTION-001, PRD FR-03): `git add Sources/FantasqueSansMono-Medium.sfdir Sources/FantasqueSansMono-MediumItalic.sfdir` and commit with a descriptive message (e.g., `Add Medium and Medium Italic source .sfdir directories`). The script itself is retained for reproducibility but is not part of the standard build pipeline. *High Risk — ASSUMPTION-001 (committed generated sources; run manually once, not in CI).* | FR-03 | AC-003, AC-006 | TASK-003, TASK-006 | 2 | | |
| TASK-008 | **VERIFY**: (a) `Scripts/validate-font Sources/FantasqueSansMono-MediumItalic.sfdir` — no `Error in ...` in output. (b) Metadata: `font.os2_weight == 500` for Medium Italic; `font.italicangle` equals the value read from `Sources/FantasqueSansMono-Italic.sfdir` (preserved); OS/2 italic flag remains set on the generated Medium Italic (carried by non-modification). (c) SFNT names per Spec §4.2: Family `Fantasque Sans Mono`, SubFamily `Medium Italic`, Fullname `Fantasque Sans Mono Medium Italic`, PostScriptName `FantasqueSansMono-MediumItalic`. (d) Monospace grid: all glyph widths == `1060`. (e) Zero-touch check: `git diff --stat` on `Makefile`, `config.schema.json`, `configure.py`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, `features.py` is empty. | - | AC-002 | TASK-007 | - | | |
| TASK-009 | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 3. | - | - | TASK-008 | - | | |

### Implementation Phase 3: Build Pipeline, Packaging & CI/CD Verification

- GOAL-003: Prove the committed sources flow through every downstream integration point untouched — `make`, CSS declarations, release archives, and the Custom Build workflow — closing AC-003 through AC-006.

| Task | Description | Ref ID | AC Ref | Dep | Files | Completed | Date |
| ---- | ----------- | ------ | ------ | --- | ----- | --------- | ---- |
| TASK-010 | **Verify `make` compiles Medium variants across all 4 permutations** (AC-003, GH-003): Run `make clean && make`. Confirm: (a) `Variants/Normal/TTF/FantasqueSansMono-Medium.ttf` and `FantasqueSansMono-MediumItalic.ttf` exist, plus their `.otf` counterparts in `Variants/Normal/OTF/`; (b) each of the 4 Variant subdirectories (`Normal`, `LargeLineHeight`, `NoLoopK`, `LargeLineHeight-NoLoopK`) contains the Medium and Medium Italic basenames alongside the existing 4 weights; (c) WOFF/WOFF2 files for Medium exist in the `Webfonts/` subdirectories (produced by `generate-other-formats`). The Makefile wildcard discovers the new sources without modification. | FR-04, GH-003 | AC-003 | TASK-007 | - | | |
| TASK-011 | **Verify CSS declarations for Medium weight** (AC-004, GH-005): After the `make` build, inspect `Variants/Normal/Webfonts/FantasqueSansMono-Medium-decl.css`: it must contain `font-weight: 500;` and `font-style: normal;`, with `.woff2` and `.woff` referenced in the `src` descriptor. `Variants/Normal/Webfonts/FantasqueSansMono-MediumItalic-decl.css` must contain `font-weight: 500;` and `font-style: italic;` (derived from the non-zero `italicangle` read by `generate-css-decl`). | FR-05, GH-005 | AC-004 | TASK-010 | - | | |
| TASK-012 | **Verify release archives include Medium variants** (AC-005, GH-007): Confirm `Variants/FantasqueSansMono-Normal.zip` (produced by `zip-all-variants` during `make`) contains `FantasqueSansMono-Medium.ttf`, `FantasqueSansMono-Medium.otf`, `FantasqueSansMono-MediumItalic.ttf`, `FantasqueSansMono-MediumItalic.otf` plus their WOFF/WOFF2 web fonts — via `unzip -l Variants/FantasqueSansMono-Normal.zip | grep -i medium`. Repeat for the other 3 Variant archives. | FR-06, GH-007 | AC-005 | TASK-010 | - | | |
| TASK-013 | **Verify Custom Build workflow compiles and packages Medium** (AC-006, GH-008, FR-09): (a) Push the committed sources to a test fork branch and trigger `custom-build.yml` via `workflow_dispatch`. Confirm the workflow requires **no** YAML changes: `custom_build_driver.py`'s `find_sfdirs()` discovers the new `.sfdir` dirs automatically. (b) Verify the uploaded release artifact contains Medium and Medium Italic TTF/OTF files for the selected Variant. (c) Optionally trigger with `NerdFontPatching=true` and confirm the patcher output includes `Fantasque Sans Mono Nerd Font Medium` and `Fantasque Sans Mono Nerd Font Medium Italic` (the workflow's dynamic glob loops handle the 12 files automatically — FR-09, Spec §13). | GH-008, FR-06, FR-09 | AC-006 | TASK-007 | - | | |
| TASK-014 | **VERIFY**: (a) `python -m pytest tests/ -v` — 0 failures after the sources are committed (GH-008 AC). (b) Re-confirm zero-touch: `git diff --stat` against the forbidden list from CON-07 is empty. (c) Cross-check the local `make` outputs against AC-003/AC-004/AC-005 evidence collected in TASK-010..TASK-012. (d) Confirm the CI artifact evidence from TASK-013. | - | AC-003, AC-004, AC-005, AC-006 | TASK-013 | - | | |
| TASK-015 | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 4. | - | - | TASK-014 | - | | |

### Implementation Phase 4: Visual QA Sign-off & Final Gate

- GOAL-004: Close the visual quality acceptance criterion (AC-007) with maintainer sign-off and run the macro-level test gate before declaring the feature complete.

| Task | Description | Ref ID | AC Ref | Dep | Files | Completed | Date |
| ---- | ----------- | ------ | ------ | --- | ----- | --------- | ---- |
| TASK-016 | **Visual QA inspection and maintainer sign-off** (AC-007, GH-006): Open the generated Medium and Medium Italic sources in FontForge (waterfall preview) or on a rendered specimen page. Verify: (a) uppercase A–Z, lowercase a–z, digits 0–9 legible at 12px, 14px, and 16px; (b) dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`) retain discernible inner counters; (c) programming symbol clusters (`->`, `=>`, `!=`, `//`, `/*`, `*/`, `||`, `&&`, `<=`, `>=`, `::`, `<-`, `++`, `--`) render without glyph collisions. At least one maintainer records approval via PR review comment or approval. *High Risk — ASSUMPTION-002. If counters are clogged, STOP: per Spec §9 "Ask first" boundary, manual counter-space fixes are a separate post-generation task and must be raised with the user before any glyph tuning.* | GH-006 | AC-007 | TASK-007 | - | | |
| TASK-017 | **Final macro-level gate**: (a) `python -m pytest tests/ -v` — 0 failures. (b) `Scripts/validate-font` on both Medium sources — no `Error in ...` output. (c) Advance-width check: all glyphs == `1060` on both sources. (d) Fresh `make clean && make` completes successfully with all 4 Variant subdirectories populated. | - | AC-001, AC-002, AC-003 | TASK-016 | - | | |
| TASK-018 | **APPROVAL**: Final user sign-off. Feature is complete. | - | - | TASK-017 | - | | |

## 3. Alternatives

- **ALT-001: `interpolateFonts()` between Regular and Bold masters**: Rejected. The Regular and Bold sources have non-matching point/contour topology (e.g., lowercase `a`: 20 points in Regular vs 19 in Bold), which rules out interpolation between masters (Spec §10).
- **ALT-002: Modify the Makefile to list Medium sources explicitly**: Rejected. The existing `SOURCES=$(wildcard Sources/FantasqueSansMono*.sfdir)` wildcard already discovers the new sources; touching the Makefile violates the zero-touch mandate (CON-07).
- **ALT-003: Generate the Medium weight on-the-fly during standard builds**: Rejected. PRD §2.3 lists runtime generation as a non-goal; pre-generated committed sources keep the CI pipeline untouched (Spec §10 trade-off accepted: repository size increase for pipeline simplicity).
- **ALT-004: Call the script from the CI pipeline**: Rejected. Spec §1.2 ASSUMPTION-001 states the script is run manually once by the maintainer and is not executed in CI.

## 4. Dependencies

- **DEP-001**: `fontforge` (Python module) — required to execute `generate-medium-source.py` locally (Spec §11 INF-001). Available on the maintainer's machine and inside the Stage 1 Docker image.
- **DEP-002**: Standard build toolchain for local `make` verification: `fontforge`, `ttfautohint`, `sfnt2woff`, `woff2_compress`, `zip`, `tar` (already required by the existing pipeline).
- **DEP-003**: A test fork of the repository plus GitHub Actions access for the AC-006 workflow verification (TASK-013).
- **DEP-004**: `pytest` + `jsonschema` for the unit-test gates (already installed by the Custom Build workflow; local dev environments require `pip install pytest jsonschema`).

## 5. Files

| ID | File | Change Type | Phase | Purpose |
| -- | ---- | ----------- | ----- | ------- |
| FILE-001 | `Scripts/generate-medium-source.py` | new | 1 | Standalone generation script (REQ-01) |
| FILE-002 | `tests/test_generate_medium_source.py` | new | 1 | Unit tests with mock `fontforge` injection |
| FILE-003 | `Sources/FantasqueSansMono-Medium.sfdir/` | new (generated) | 1, 2 | Canonical Medium source (committed) |
| FILE-004 | `Sources/FantasqueSansMono-MediumItalic.sfdir/` | new (generated) | 2 | Canonical Medium Italic source (committed) |

**Zero-touch (must show empty `git diff --stat` at every phase gate):** `Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, `features.py`.

## 6. Testing

### Micro-Level (Per-Change Unit Tests)

- **TEST-001**: `tests/test_generate_medium_source.py` — CLI argument contract (REQ-02), input/output path guard (CON-06), metadata mapping for upright and italic (Spec §4.2), `changeWeight(34, "LCG", 0, 0, "Retain")` call, `removeOverlap`/`simplify` invocation (CON-03), width enforcement to 1060 (CON-02), save-target correctness. Runs without a real `fontforge` (mock module injection).

### Macro-Level (Full Suite Gate)

- **TEST-002**: `python -m pytest tests/ -v` — ALL tests (existing 69 + new) pass with 0 failures before each phase is declared complete.

### Validation & Integration

- **TEST-003**: `Scripts/validate-font` output inspection — no `Error in ...` lines for both Medium sources (exit code is always `0`; output is the effective signal).
- **TEST-004**: Monospace grid audit — every glyph advance width == `1060` on both sources (fontforge one-liner).
- **TEST-005**: Idempotency diff — two runs into separate dirs produce identical glyph geometry (CON-05).
- **TEST-006**: `make clean && make` — all 4 Variant permutations compile, including WOFF/WOFF2 (AC-003).
- **TEST-007**: CSS declaration assertions — `font-weight: 500`, correct `font-style`, `.woff2`/`.woff` in `src` (AC-004).
- **TEST-008**: Archive contents — `unzip -l` shows Medium TTF/OTF/WOFF/WOFF2 in all 4 Variant archives (AC-005).
- **TEST-009**: Workflow dispatch on a test fork — release artifact contains Medium files; optional Nerd Font patching yields "Nerd Font Medium" naming (AC-006, FR-09).
- **TEST-010**: Visual QA sign-off — maintainer approval recorded on the PR (AC-007).

## 7. Risks & Assumptions

### Risks

- **RISK-001 (Counter clogging on dense glyphs)**: The 34 em-unit stroke may shrink inner counters of dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`) below legibility. **Mitigation**: `counter_type="Retain"` in `changeWeight` (Spec §1.2 resolved decision); mandatory visual QA (TASK-016); manual counter-space fixes are a documented post-generation follow-up (Spec §12 — "Ask first" boundary). **Impact**: Medium. **Tasks affected**: TASK-003, TASK-006, TASK-016.
- **RISK-002 (Advance width drift)**: `ChangeWeight` may alter advance widths, breaking the monospace grid. **Mitigation**: CON-02 enforces explicit re-set to 1060; automated width audit in every VERIFY gate. **Impact**: Low. **Tasks affected**: TASK-001, TASK-004, TASK-008.
- **RISK-003 (Repository size growth)**: Two additional committed `.sfdir` source directories increase repo size. **Mitigation**: Accepted trade-off documented in Spec §10 (pipeline simplicity over size); no action required. **Impact**: Low. **Tasks affected**: TASK-007.
- **RISK-004 (False-green validation)**: `Scripts/validate-font` always exits `0`, so exit-code-based checks would silently pass broken fonts. **Mitigation**: All gates inspect script output for `Error in ...` lines (Spec §6 codebase note). **Impact**: Medium. **Tasks affected**: TASK-004, TASK-008, TASK-017.
- **RISK-005 (Local-only verification gap for CI)**: The AC-006 workflow run cannot be fully verified without pushing to a fork. **Mitigation**: TASK-013 explicitly executes the fork dispatch; local `make` evidence covers the build engine equivalence. **Impact**: Low-Medium. **Tasks affected**: TASK-013.

### Assumptions (Extracted from Spec §1.2)

- **ASSUMPTION-001**: Generated sources are committed to version control; the generation script is run manually once by the developer/maintainer and is not executed in the CI pipeline. **Tasks affected**: TASK-007, TASK-013. **Risk**: Low (per Spec; accepted design decision).
- **ASSUMPTION-002**: A stroke expansion of 34 em-units (within the PRD's suggested +30 to +40 range) is used as the reference value. Final tuning may occur after post-generation visual inspection. **Tasks affected**: TASK-003, TASK-006, TASK-016 (flagged *High Risk* in the task table). **Risk**: Medium.

### Planning Assumptions

- **ASSUMPTION-003** *(planning)*: The CI host runner's pytest environment has no `fontforge` module; unit tests for the generation script therefore inject a fake `fontforge` into `sys.modules`, while real-fontforge behavior is proven by the validation gates (TEST-003/004/005). **Tasks affected**: TASK-002.
- **ASSUMPTION-004** *(planning)*: The generation script targets Python 3 (the `python` launcher on the maintainer machine and in the Stage 1 image), consistent with the modernized toolchain per ADR-0002. **Tasks affected**: TASK-001.

## 8. Related Specifications / Further Reading

- [Technical Specification — Medium Font Weight](../spec/spec-design-medium-weight.md) (v1.2)
- [PRD — Medium Font Weight Variant](../docs/prd-20260813-0921-medium-font-weight.md) (v1.2)
- [Clarification Report — Medium Font Weight](../docs/audit/clarification-report-medium-font-weight-2026-08-13.md)
- [ADR 0002 — Multi-Stage Docker Build with Deferred Engine Port](../docs/adr/0002-multi-stage-docker-deferred-engine-port.md)
- [Fantasque Sans Mono Domain Glossary](../CONTEXT.md)
- [FontForge changeWeight API documentation](https://fontforge.org/docs/scripting/python/fontforge.html)

## 9. Rollback / Recovery Plan

### Phase 1 (Script + Medium Upright Source)

1. Delete the generated source: `rm -rf Sources/FantasqueSansMono-Medium.sfdir`.
2. Delete the script and its tests: `git restore Scripts/generate-medium-source.py tests/test_generate_medium_source.py` (or `rm` if untracked).
3. Run `python -m pytest tests/ -v` to confirm the original 69-test suite passes.

### Phase 2 (Medium Italic + Commit)

1. `git revert` the commit that added both `.sfdir` directories (or `git reset --soft HEAD~1` if not yet pushed).
2. `rm -rf Sources/FantasqueSansMono-Medium.sfdir Sources/FantasqueSansMono-MediumItalic.sfdir` if the revert leaves untracked remnants.
3. `make clean` to purge `Variants/` outputs.
4. Verify `git diff --stat` on all zero-touch files is empty.

### Phase 3-4 (Verification Only)

1. No production code changes exist in these phases; rollback equals the Phase 2 revert.
2. Any fork-side CI test runs, artifacts, or releases created during TASK-013 are external to this repository and may be deleted via the GitHub UI (see `docs/CUSTOM-BUILD.md` for bulk-release cleanup).

### Emergency Rollback (All Phases)

1. `git revert --no-commit HEAD~N..HEAD` (where N = number of feature commits).
2. `git commit -m "Revert: Medium Font Weight sources"`.
3. Push to `main`. The build pipeline immediately returns to the 4-weight state — the Makefile wildcard and CI driver simply stop discovering the removed sources.
