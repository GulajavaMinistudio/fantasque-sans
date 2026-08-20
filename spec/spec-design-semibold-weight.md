---
title: Fantasque Sans Mono - SemiBold Font Weight Technical Specification
version: 1.1
date_created: 2026-08-20
last_updated: 2026-08-20
owner: Specification Architect
tags: [font, build, semibold-weight, python, fontforge]
---
<!-- markdownlint-disable  -->
# Introduction

This specification defines the technical design for introducing a **SemiBold** (CSS weight 600) and **SemiBold Italic** variant to the Fantasque Sans Mono font family. It completes the weight ladder (400 → 500 → 600 → 700) by reusing the proven algorithmic weight-generation pattern from the shipped Medium feature: a standalone one-shot Python script generates the `.sfdir` sources, which are committed as canonical source files. The existing `Makefile` wildcard discovery, build scripts, CI/CD pipeline, and packaging workflows then compile, validate, and distribute the new variants automatically — zero modifications to core build infrastructure.

The upstream source is PRD `docs/prd-20260818-1636-semibold-font-weight.md` (v1.1, 2026-08-20), which already incorporates the Clarification Report `docs/audit/clarification-report-semibold-font-weight-2026-08-20.md` (Review Iteration 2, Readiness 95/100). All four resolved decisions from that report are encoded into this specification (§1.2, §4.3, §5, §13).

## 1. Purpose & Scope

The purpose of this specification is to define the exact behavior, inputs, and outputs of the `Scripts/generate-semibold-source.py` script, the stroke calibration contract that determines its core constant, the metadata requirements for weight 600, and the validation criteria that ensure the new variants integrate seamlessly with the existing build, packaging, and CI/CD pipelines — without touching the CON-07 zero-touch set.

The intended audience is the developer implementing the feature (Phase Code) and the maintainer performing visual QA sign-off (GH-006).

### 1.1 Out of Scope

- **Modifications to the CON-07 zero-touch set**: `Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, `features.py`, `Scripts/generate-css-decl`, and `Scripts/zip-all-variants` must remain untouched. Both scripts already behave dynamically: `generate-css-decl` reads `font.os2_weight` and `font.italicangle` at runtime, and `zip-all-variants` auto-discovers variant directories via `find "$variants"/* -maxdepth 0 -type d`.
- **Modifications to the shipped Medium artifact**: `Scripts/generate-medium-source.py` and the committed `Sources/FantasqueSansMono-Medium*.sfdir` sources must remain byte-identical (zero regression).
- **Interpolation-based generation**: the unmerged `origin/feature/multi-weight-poc` branch (harmonized masters, interpolation, build-time generation) is not adopted.
- **Weights other than 600 (SemiBold)**: Light, ExtraBold, and Black are out of scope.
- **Proportional `FantasqueSans` family**: only the monospace family (`FantasqueSansMono`) receives the SemiBold weight.
- **Runtime font-weight parameter in Custom Build**: SemiBold is a pre-generated, committed source — not a user-configurable build option.
- **Mandatory manual glyph fixes**: residual algorithmic artifacts are accepted via maintainer exception and deferred to visual QA (GH-006). Manual fixes are only performed if the maintainer explicitly requests them (see §4.3 escalation path).
- **A literal zero-warning `validate-font` run**: unachievable for any source in this family (inherited `Bad Glyph Name` ligature + `ChangeWeight` artifacts); the recorded maintainer baseline exception is re-recorded, not re-litigated (§13).

### 1.2 Open Questions & Assumptions

> [!WARNING]
> **ASSUMPTION:** The generated sources are committed to version control. The generation script (`generate-semibold-source.py`) is run manually once by the developer/maintainer during Phase 1/2 and is never executed in the CI pipeline (same contract as the Medium feature).
>
> [!WARNING]
> **ASSUMPTION:** The reference stroke used in the §8 code sample is **60 em-units** (mid-point of the candidate grid 50/60/70). The final value is NOT a free design choice: it must be established empirically via the calibration contract in §4.3 and locked before the sources are committed. The §8 constant is a representational value only.
>
> [!WARNING]
> **ASSUMPTION:** The new unit-test module mirrors the structure of `tests/test_generate_medium_source.py` (fake `fontforge` module; the exact added test count is determined at implementation). The full suite — the 83-test baseline plus the new SemiBold generation tests — must pass with zero failures before the Code phase is complete.
>
> [!NOTE]
> **RESOLVED DECISION (Clarification Report Iteration 2, 2026-08-20; superseded by Spec v1.1 composite AND gate):** The stroke calibration contract is explicit — choose the **highest grid candidate** in the 55–70 em-unit band that passes the **composite AND gate** (§4.3 rule 3): (a) upright specimen passes the GH-006 "discernible counters" test, (b) italic specimen **simultaneously** passes the same test, AND (c) the render is clearly heavier than Medium (34 em-units) AND clearly lighter than Bold (Q3 two-sided neighbor gate). If no grid candidate in the band passes, descend step-wise — first 50, then the 45 em-unit floor — until the composite gate passes. Manual per-glyph fixes are **not** an automatic fallback. 45 em-units is the hard floor; failing at or above the floor declares the single-pass approach failed and escalates to a maintainer decision (re-scope / abandon / manual fix) — never a silent ship of a Medium-clone result.
>
> [!NOTE]
> **RESOLVED DECISION (Medium precedent, erratum 1.3):** `counter_type="retain"` (lowercase) is used in the `changeWeight` call. FontForge's Python binding is case-sensitive and only accepts the lowercase spelling.
>
> [!NOTE]
> **RESOLVED DECISION (Medium precedent):** Italic input is detected via the source basename prefix `FantasqueSansMono-Italic`; one script serves both upright and italic — no separate invocation is required (FR-02).

## 2. Definitions

- **SemiBold**: A Fantasque Sans Mono weight variant positioned between Medium (CSS weight 500) and Bold (CSS weight 700) at CSS weight 600. Canonical term per `CONTEXT.md`. _Avoid_: semibold, semi bold, demi bold, DemiBold.
- **Em-unit**: The internal coordinate unit used in FontForge. Fantasque Sans Mono relies on a strict advance width of 1060 em-units to maintain monospace integrity.
- **SFNT**: The table structure used by TrueType and OpenType fonts to store metadata (e.g., Family and SubFamily names).
- **Stroke Band**: The target reference-stroke range for the SemiBold `ChangeWeight` expansion — 55 to 70 em-units inclusive.
- **Candidate Grid**: The empirical specimen-render grid — 50, 60, and 70 em-units — used to select the reference stroke. 50 is the first step-down below the band.
- **Hard Floor**: The absolute lower bound for the reference stroke — 45 em-units. Failing at or above the floor escalates to a maintainer decision.
- **Discernible Counters Test**: The GH-006 pass/fail gate that checks dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`) for legible, distinguishable inner counter spaces after emboldening.
- **Maintainer Baseline Exception**: The recorded acceptance that a literal clean `validate-font` run is unachievable for any source in this family (inherited `Bad Glyph Name` ligature warning plus `ChangeWeight` artifacts). Recorded for Medium; re-recorded for SemiBold without re-litigation.
- **accepted-deviation**: A documented limitation of algorithmic `ChangeWeight` (e.g., residual self-intersections) accepted via maintainer exception and deferred to visual QA, rather than fixed.
- **Zero-Touch Set (CON-07)**: The canonical 8-file set that must not be modified: `Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, `features.py` — plus `Scripts/generate-css-decl` and `Scripts/zip-all-variants`, which are zero-touch by feature design.

## 3. Requirements, Constraints & Guidelines

- **REQ-01**: A single standalone Python script `Scripts/generate-semibold-source.py` SHALL generate the SemiBold `.sfdir` sources. It SHALL be a standalone copy of the shipped Medium generator (`Scripts/generate-medium-source.py`) with SemiBold constants — the shipped Medium artifact must not be modified (FR-01).
- **REQ-02**: The script SHALL accept exactly two positional arguments — the input source `.sfdir` path and the output `.sfdir` path. Any other argument count SHALL print the usage message to stderr and exit non-zero (FR-01; Medium CLI contract).
- **REQ-03**: The script SHALL detect italic input via the source basename prefix `FantasqueSansMono-Italic` and produce the SemiBold Italic output; it SHALL preserve the italic angle (-11.0) and the OS/2 italic flag from the source Italic while applying the same embolden parameters as the upright (FR-02).
- **REQ-04**: The script SHALL apply a single-pass embolden transformation via FontForge `changeWeight(stroke, "LCG", 0, 0, "retain")`, where `stroke` is the reference stroke established per the §4.3 calibration contract (FR-01).
- **REQ-05**: Every generated glyph SHALL have its advance width strictly set to exactly `1060` em-units after emboldening (FR-01; monospace grid integrity).
- **REQ-06**: The script SHALL call font-level `removeOverlap()` and `simplify()` (applied across all glyphs) after `ChangeWeight` (FR-01). Per-glyph `intersect()` cleanup is forbidden (Medium plan Dead-End #11 — Boolean intersect destroys non-overlapping outer/inner contours).
- **REQ-07**: The generated `.sfdir` source SHALL have `os2_weight` set to `600` and the weight name set to `SemiBold`; SFNT name table entries SHALL follow FR-07 (§4.2) (FR-01, FR-07).
- **REQ-08**: The script SHALL be functionally idempotent — running it multiple times with the same input produces identical contour geometry and metrics. Differences in non-functional metadata (e.g., timestamps) are permitted (FR-01).
- **REQ-09**: The script SHALL never modify the input source `.sfdir` in place. It may only read from the input path and write to the output path (Medium CON-06 contract).
- **REQ-10**: The generated sources SHALL be committed to a temporary feature branch (not `master`), with amend/squash history rewriting permitted until visual QA passes; sources SHALL merge to `master` only after maintainer visual QA sign-off (GH-006) (FR-03).
- **REQ-11**: The script SHALL be retained for reproducibility after commit but SHALL NOT be part of the standard build pipeline (FR-03).
- **CON-01**: No modifications to the zero-touch set (see §2, §1.1) are required for SemiBold compilation, CSS generation, or packaging (FR-04, FR-05, FR-06, FR-08).
- **CON-02**: The reference stroke SHALL be selected per the §4.3 calibration contract before the sources are committed; no stroke value may be hard-coded without calibration (FR-01, GH-006).
- **CON-03**: All four variant permutations (`Normal`, `LargeLineHeight`, `NoLoopK`, `LargeLineHeight-NoLoopK`) SHALL apply to SemiBold and SemiBold Italic identically to other weights via the existing `Makefile` wildcard `SOURCES=$(wildcard Sources/FantasqueSansMono*.sfdir)` (FR-04).
- **CON-04**: SemiBold SHALL be compiled into TTF, OTF, WOFF, WOFF2, and SVG output files in the appropriate `Variants/` subdirectories (FR-04; verified pipeline: `fontbuilder.py` emits TTF/OTF/SVG, `generate-other-formats` emits WOFF/WOFF2).
- **CON-05**: SemiBold SHALL be released additively as part of the next regular release bundle — no standalone release (FR-06).
- **GUD-01**: The reference stroke should target the 55–70 em-unit band (~1.6×–2.1× the Medium stroke of 34 em-units) to produce a weight visually distinct from both Medium and Bold, with 45 em-units as the hard floor (FR-01, §8.3 PRD).
- **GUD-02**: `os2_weight` SHALL be assigned before `font.weight` (OS/2 WeightWidthSlopeOnly precedence); `font.weight` SHALL be set explicitly to kill stale `Regular`/`Book` inheritance from the input source (FR-07; learned from Medium TASK-104).
- **GUD-03**: Watch for preferred-family records (SFNT IDs 16/17) appearing as a side effect of metadata assignment; the Medium TASK-104 dump proved no such side effects for the documented assignment order — the SemiBold script SHALL follow the same order and the same expectation is verified at Phase 2.

## 4. Interfaces & Data Contracts

### 4.1 Script Execution Interface

```bash
python Scripts/generate-semibold-source.py <input.sfdir> <output.sfdir>
```

**Example (SemiBold):**

```bash
python Scripts/generate-semibold-source.py Sources/FantasqueSansMono-Regular.sfdir Sources/FantasqueSansMono-SemiBold.sfdir
```

**Example (SemiBold Italic):**

```bash
python Scripts/generate-semibold-source.py Sources/FantasqueSansMono-Italic.sfdir Sources/FantasqueSansMono-SemiBoldItalic.sfdir
```

**CLI Error Contract (mirrors the implemented Medium `main()`):**

- Wrong argument count (anything other than exactly two): print `Usage: python generate-semibold-source.py <input.sfdir> <output.sfdir>` to stderr, exit code `1` (REQ-02).
- `input == output` (after `os.path.abspath` normalization): print `Error: input and output paths must differ` to stderr, exit code `1` (REQ-09).

### 4.2 Font Metadata Modifications

The script SHALL explicitly set the following properties on the `fontforge.font` object before saving:

| Property       | Value (SemiBold)                  | Value (SemiBold Italic)                  |
| :------------- | :-------------------------------- | :--------------------------------------- |
| `os2_weight`   | `600`                             | `600`                                    |
| `weight`       | `SemiBold`                        | `SemiBold`                               |
| `familyname`   | `Fantasque Sans Mono`             | `Fantasque Sans Mono`                    |
| `fontname`     | `FantasqueSansMono-SemiBold`      | `FantasqueSansMono-SemiBoldItalic`       |
| `fullname`     | `Fantasque Sans Mono SemiBold`    | `Fantasque Sans Mono SemiBold Italic`    |

`weight` is set to `"SemiBold"` so the generated sources do not inherit the stale `Weight: Regular` / `Weight: Book` strings from their inputs (GUD-02).

The script SHALL also update the SFNT names in `font.appendSFNTName('English (US)', ...)`:

- `Family`: `"Fantasque Sans Mono"`
- `SubFamily`: `"SemiBold"` or `"SemiBold Italic"`
- `Fullname`: `"Fantasque Sans Mono SemiBold"` or `"Fantasque Sans Mono SemiBold Italic"`
- `PostScriptName`: `"FantasqueSansMono-SemiBold"` or `"FantasqueSansMono-SemiBoldItalic"`

For SemiBold Italic, the script SHALL additionally preserve `italicangle` (-11.0) and the OS/2 italic flag from the source Italic font. These style-specific values are carried over unchanged and must not be reset by the script — `ChangeWeight` does not touch them, so preservation holds by non-modification (REQ-03).

### 4.2.1 Empirical `font.weight` Acceptance Gate (Phase 1, Q1 Resolution)

The string `"SemiBold"` assigned to `font.weight` (GUD-02) is unverified against the FontForge Python binding: official docs only define `font.weight` as a "PostScript font weight string" without enumerating accepted values, the Medium/Bold precedents exercised only standard names (`Medium`, `Bold`), and the **Italic source really carries `Weight: Book` in `font.props`** — so the stale-inheritance risk is real and concentrated on the Italic input. If the binding rejects or normalizes the string, either the stale `Weight:` survives (GUD-02 purpose fails) or the output `Weight:` field contradicts the §4.2 table and AC-005. **A single invocation (e.g., Regular→SemiBold only) does NOT close this gate** — the stale `Weight: Book` originates from the Italic source, so the Italic→SemiBoldItalic run is the run that actually exercises the binding against the documented risk.

Therefore, during Phase 1 the developer SHALL run the generator with **real FontForge** for **both invocations** (no skip, no shortcut), and dump from the **built TTF/OTF** (not only the `.sfdir` — `.sfdir` `font.props` can lie; built TTF/OTF is the canonical record) the following five artifacts for **each** invocation independently:

| # | Artifact | Acceptance criterion (per invocation) |
|---|---|---|
| 1 | The resulting `font.weight` value (re-read after the save round-trip) | Equals `"SemiBold"` (not `"Regular"`, `"Book"`, `"DemiBold"`, or empty) |
| 2 | The `Weight:` field in the output `font.props` | Equals `"SemiBold"` (not `"Regular"`, `"Book"`, `"DemiBold"`, or empty) |
| 3 | SFNT name IDs 2 (Style), 4 (Full Name), 6 (PostScript Name) | Match the §4.2 table for the variant being generated (SemiBold or SemiBold Italic) |
| 4 | ID 16/17 side-effect check (preferred-family records must not appear) | No preferred-family records are emitted; the documented assignment order produces no such side effects (GUD-03) |
| 5 | `os2_weight` | Equals `600` |

**Mandatory invocations (both required):**

- **Run A — Upright:** `python Scripts/generate-semibold-source.py Sources/FantasqueSansMono-Regular.sfdir Sources/FantasqueSansMono-SemiBold.sfdir` — then build the resulting source to TTF/OTF; record the five artifacts for this run.
- **Run B — Italic:** `python Scripts/generate-semibold-source.py Sources/FantasqueSansMono-Italic.sfdir Sources/FantasqueSansMono-SemiBoldItalic.sfdir` — then build the resulting source to TTF/OTF; record the five artifacts for this run. **Run B is the gating run for the stale `Weight: Book` risk** — Run A passing alone does not satisfy the gate.

Evidence MUST be recorded **verbatim** in the `plan/` Execution Results section, with the five artifacts tabulated separately for Run A and Run B (no combined-row elision). The PR description is only a copy/additional QA trail — the authoritative evidence lives in `plan/`. If `"SemiBold"` does not stick on **either** run (binding rejects or normalizes), the developer SHALL escalate to a maintainer/spec-update decision; no premature naming fallback (e.g., silent substitution of `"DemiBold"`) is committed. This gate is independent of the CI gate — Phase 1 happens once before commit and is a manual evidence path, not a CI step.

### 4.3 Stroke Calibration Contract

The reference stroke for `changeWeight()` is **not** a free design constant. It SHALL be established empirically via specimen renders during Phase 1 (PRD §9.2) before any source is committed, per the following contract (Clarification Report Resolutions Q2 & Q3, Iteration 1, 2026-08-20):

1. Render specimen pages at the **candidate grid**: 50, 60, and 70 em-units, targeting the **stroke band** 55–70 em-units. The grid is the empirical search set; the band is the design target window.
2. Compare the candidate renders visually against the Medium (34 em-units) and Bold neighbors (GH-006 AC4). The comparison outcome is **gating**, not advisory.
3. **Selection rule (composite AND gate, Q5 wording):** **select the highest grid candidate within the 55–70 em-unit band that simultaneously passes all three sub-gates.** The iteration proceeds in locked descending order (**70 → 60** as in-band grid candidates, then step-down **50**, then the **45 em-unit hard floor**) — at each candidate the candidate **passes** iff **all three** sub-gates hold:
   1. **Upright counters gate** — the upright specimen passes the GH-006 "discernible counters" test on dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`).
   2. **Italic counters gate** — the italic specimen **simultaneously** passes the same "discernible counters" test. This is the Q2 AND gate: one `STROKE_WIDTH` is shared by upright and italic (REQ-03), and Medium precedent recorded 465 italic vs 252 upright self-intersections — an upright-calibrated stroke that clogs italic counters is not acceptable. If a candidate passes upright but fails italic, descend to the next candidate per the locked iteration order — never an immediate escalation on the first italic failure.
   3. **Two-sided neighbor gate (Q3)** — the render is **clearly heavier than Medium (34 em-units)** AND **clearly lighter than Bold** (Bold is hand-drawn; no numeric stroke). Failing either side means descend to the next candidate; this strengthens the existing "never ship a Medium-clone" rule (e.g., 45 passing counters but not clearly heavier than Medium escalates instead of shipping silently).
4. **Fallback rule:** if no candidate in the 55–70 band passes the composite gate, descend step-wise — first **50** (first step-down below the band), then the **45 em-unit hard floor** — until the composite gate passes.
5. **Escalation rule:** if the composite gate does not pass at or above the 45 em-unit floor, the single-pass approach is declared failed and escalated to a maintainer decision (re-scope / abandon / manual fix). Manual per-glyph fixes are **not** an automatic fallback — they occur only if the maintainer explicitly requests them. A Medium-clone result must never be shipped silently.
6. The selected stroke SHALL be locked into the script constant (`STROKE_WIDTH`, §8) and recorded in the commit message and PR description before the sources are committed.

Rationale for the band: the SemiBold stroke is ~1.6×–2.1× the Medium stroke (34 em-units), so counter-clogging risk on dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`) is significantly higher than Medium; the band and floor bound this risk explicitly. The two-sided neighbor gate (Q3) closes the loophole where a counters-passing candidate could still be visually indistinguishable from Medium or Bold.

## 5. Acceptance Criteria

- **AC-001**: Given a Regular `.sfdir` source, When `python Scripts/generate-semibold-source.py Sources/FantasqueSansMono-Regular.sfdir Sources/FantasqueSansMono-SemiBold.sfdir` is run, Then a valid SemiBold `.sfdir` directory is produced with `os2_weight` set to `600`, the weight name `SemiBold`, all glyph advance widths exactly `1060`, and no avoidable self-intersecting splines (all glyphs pass `removeOverlap` and `simplify`) — residual self-intersections are `accepted-deviation` per GH-001 AC3. The script is functionally idempotent (GH-001).
- **AC-002**: Given an Italic `.sfdir` source, When the same script is run with `Sources/FantasqueSansMono-Italic.sfdir` and `Sources/FantasqueSansMono-SemiBoldItalic.sfdir`, Then a valid SemiBold Italic `.sfdir` is produced with `os2_weight` set to `600`, the italic angle (-11.0) preserved, and the OS/2 italic flag set (GH-002).
- **AC-003**: Given the generated sources present in `Sources/`, When `make` is executed, Then TTF, OTF, WOFF, WOFF2, and SVG output files for SemiBold and SemiBold Italic are produced in the appropriate `Variants/` subdirectories for all four variant permutations (`Normal`, `LargeLineHeight`, `NoLoopK`, `LargeLineHeight-NoLoopK`), with no modifications to the zero-touch set, and all existing variants continue to build identically (GH-003).
- **AC-004**: Given the generated SemiBold sources, When `Scripts/validate-font` is run against them, Then no `Error in ...` messages appear beyond the recorded maintainer baseline exception (inherited `Bad Glyph Name` ligature + `ChangeWeight` artifacts). Note: the script always exits `0` by design — output inspection is the effective signal (GH-003).
- **AC-005**: The SemiBold TTF/OTF SFNT name table SHALL contain Family = "Fantasque Sans Mono", SubFamily = "SemiBold", Full Name = "Fantasque Sans Mono SemiBold", PostScript Name = "FantasqueSansMono-SemiBold"; SemiBold Italic SHALL contain SubFamily = "SemiBold Italic", Full Name = "Fantasque Sans Mono SemiBold Italic", PostScript Name = "FantasqueSansMono-SemiBoldItalic". The variants SHALL group under the "Fantasque Sans Mono" family in macOS Font Book, Windows Font Settings, and Linux `fc-list` (GH-004).
- **AC-006**: The generated CSS SHALL contain a `@font-face` rule for SemiBold with `font-weight: 600` and `font-style: normal`, and for SemiBold Italic with `font-weight: 600` and `font-style: italic`, referencing WOFF2, WOFF, TTF, and SVG files in the `src` descriptor (GH-005).
- **AC-007**: Given the generated SemiBold sources, When a maintainer performs visual QA on specimen renders at the candidate grid (50/60/70 em-units) compared against Medium and Bold neighbors, Then the reference stroke is selected per the §4.3 calibration contract (composite AND gate: upright AND italic counters pass; render clearly heavier than Medium AND clearly lighter than Bold), and the QA checks (legibility at 12px/14px/16px; programming-symbol clusters without collisions; dense-glyph discernible counters; at least one maintainer PR review comment or approval) apply to **both** the upright specimen **and** the italic specimen independently — not the upright alone. An upright-only pass does not satisfy AC-007 (GH-006).
- **AC-008**: The ZIP release archive SHALL contain `FantasqueSansMono-SemiBold.ttf`, `FantasqueSansMono-SemiBold.otf`, `FantasqueSansMono-SemiBoldItalic.ttf`, and `FantasqueSansMono-SemiBoldItalic.otf`; the web font archive SHALL include WOFF, WOFF2, and SVG variants; all four variant permutations SHALL include the SemiBold weight in their output directories (GH-007).
- **AC-009**: Given a `workflow_dispatch` trigger of `custom-build.yml`, When the workflow runs, Then SemiBold and SemiBold Italic variants are compiled and packaged without any workflow modifications; the `build-make.yml` evidence workflow compiles the standard-make path with SemiBold sources present; `pytest tests/` passes with zero failures including the new SemiBold generation tests; and the release artifact uploaded by CI contains all SemiBold variant font files (GH-008).
- **AC-010**: `git diff` on `Scripts/generate-medium-source.py` and the committed Medium sources is empty throughout the feature (zero regression on Medium; PRD §7.3).

## 6. Test Automation Strategy & Testing Seams

- **Testing Seams**: The boundaries are (1) the generation script's public interface (CLI + `generate_semibold()` behavior) exercised through a fake `fontforge` module, and (2) the standard `Makefile` build output plus the output of `Scripts/validate-font`. These are the same seams as the Medium feature — no new seams are introduced.
- **Test Levels**:
  - **Unit Testing**: `tests/test_generate_semibold_source.py` — new module mirroring `tests/test_generate_medium_source.py` (fake `fontforge` injected into `sys.modules`; the **unit-test runner** has no real `fontforge`; added test count finalized at implementation). The build runner is a separate job and IS provisioned with `fontforge` per the Dockerfile (INF-001). Covers: CLI argument-count contract (REQ-02), `input == output` guard (REQ-09), upright/italic metadata mapping including `font.weight == "SemiBold"` (REQ-07, §4.2), `changeWeight(<stroke>, "LCG", 0, 0, "retain")` call, `removeOverlap`/`simplify` invocation and runtime order including `selection.all()` (REQ-06), width enforcement to 1060 (REQ-05), save-target correctness (REQ-09). Run `pytest tests/` — full suite is the 83-test baseline plus the new SemiBold generation tests, 0 failures.
  - **Phase 1 Empirical Verification (Manual Evidence Path)**: Not a CI gate. Two manual verifications happen before commit, recorded in `plan/` Execution Results:
    1. **`font.weight` acceptance gate (Q1, §4.2.1)** — run the generator with real FontForge **for both invocations** (Regular→SemiBold **and** Italic→SemiBoldItalic — Run B is the gating run for the stale `Weight: Book` risk and cannot be skipped), build each output to TTF/OTF, dump the **five artifacts per run** (independently tabulated for Run A and Run B in `plan/`, no combined-row elision): `font.weight` value, `Weight:` field in `font.props`, SFNT IDs 2/4/6, ID 16/17 side-effect check, `os2_weight` = 600. Each artifact's acceptance criterion is defined in §4.2.1. Recorded verbatim.
    2. **Idempotency verification (Q4, REQ-08)** — follows the **TEST-005 precedent** (Medium plan v1.1): two clean runs into separate output directories; all `.glyph` files and their contours are byte-identical; metrics (advance widths, `os2_weight`, `weight`, family/fontname/fullname) are identical; `font.props` is diffed **per-field** with only non-functional metadata (e.g., `ModificationTime`) allowed to differ. The whole `font.props` MUST NOT be exempted — it holds the `Weight:`/SFNT fields and a full-file exemption could hide metadata regressions. Recorded verbatim. The fake-`fontforge` unit-test seam records deterministic call sequences only; this manual real-FontForge check is the only path that proves real idempotency.
  - **Validation Testing**: Run `Scripts/validate-font` against the newly generated `Sources/FantasqueSansMono-SemiBold.sfdir` and `Sources/FantasqueSansMono-SemiBoldItalic.sfdir`; inspect output for `Error in ...` messages beyond the maintainer baseline exception (AC-004).
  - **Monospace Integrity**: Verify all glyph advance widths in the output `.sfdir` files equal exactly `1060`.
  - **Calibration Evidence**: The Phase 1 specimen renders (candidate grid vs Medium/Bold neighbors) and the selected stroke per §4.3 are recorded in the PR description — this is a manual QA evidence path (GH-006), not a CI gate.

> [!WARNING]
> **Codebase note:** `Scripts/validate-font` currently always exits with code `0` (a hardcoded `exit 0` precedes `exit $error`). Validation success must be determined by inspecting the script output for `Error in ...` messages (or `Font ... is not valid` from the `42` exit path), not by the exit code.

## 7. Project Structure & Commands

### Project Structure

- `Scripts/generate-semibold-source.py`: [NEW] The Python script that generates the font sources (standalone copy of the Medium generator with SemiBold constants).
- `tests/test_generate_semibold_source.py`: [NEW] Unit tests using a fake `fontforge` module, mirroring the Medium test module (see §6).
- `Sources/FantasqueSansMono-SemiBold.sfdir`: [NEW] Output directory (to be committed).
- `Sources/FantasqueSansMono-SemiBoldItalic.sfdir`: [NEW] Output directory (to be committed).

No existing file is modified.

### Commands

- **Generate Sources:** `python Scripts/generate-semibold-source.py Sources/FantasqueSansMono-Regular.sfdir Sources/FantasqueSansMono-SemiBold.sfdir`
- **Generate Italic Source:** `python Scripts/generate-semibold-source.py Sources/FantasqueSansMono-Italic.sfdir Sources/FantasqueSansMono-SemiBoldItalic.sfdir`
- **Build Fonts:** `make`
- **Validate Sources:** `Scripts/validate-font Sources/FantasqueSansMono-SemiBold.sfdir`
- **Unit Tests:** `python -m pytest tests/` (83-test baseline plus new SemiBold tests, 0 failures)

## 8. Code Style & Conventions

The script SHALL be a standalone copy of `Scripts/generate-medium-source.py` with SemiBold constants — the shipped Medium artifact remains unmodified. Expected structure (mirroring the implemented Medium script):

```python
#!/usr/bin/env python3
"""Generate a SemiBold (weight 600) font source from a Regular or Italic source."""

import os
import sys

import fontforge

# Reference stroke in em-units, selected per the calibration contract
# (Spec v1.1 section 4.3): highest grid candidate in the 55-70 band
# passing the COMPOSITE AND gate (upright counters AND italic counters
# AND clearly heavier than Medium AND clearly lighter than Bold); else
# descend 50, then the 45 em-unit floor. Failing at or above the floor
# escalates to a maintainer decision.
# Reference value 60 (mid candidate grid) — final value locked during
# Phase 1 calibration BEFORE sources are committed.
STROKE_WIDTH = 60
EMBOLDEN_TYPE = "LCG"
COUNTER_TYPE = "retain"  # lowercase only; FontForge binding is case-sensitive
MONOSPACE_WIDTH = 1060   # REQ-05
SEMIBOLD_WEIGHT = 600    # REQ-07
SEMIBOLD_WEIGHT_NAME = "SemiBold"  # §4.2; kills stale "Regular"/"Book" inheritance

FAMILY_NAME = "Fantasque Sans Mono"
ITALIC_PREFIX = "FantasqueSansMono-Italic"

UPRIGHT_NAMES = {
    "fontname": "FantasqueSansMono-SemiBold",
    "fullname": "Fantasque Sans Mono SemiBold",
    "sub_family": "SemiBold",
}
ITALIC_NAMES = {
    "fontname": "FantasqueSansMono-SemiBoldItalic",
    "fullname": "Fantasque Sans Mono SemiBold Italic",
    "sub_family": "SemiBold Italic",
}

USAGE = "Usage: python generate-semibold-source.py <input.sfdir> <output.sfdir>"


def generate_semibold(input_sfdir, output_sfdir):
    font = fontforge.open(input_sfdir)

    is_italic = os.path.basename(os.path.normpath(input_sfdir)).startswith(
        ITALIC_PREFIX
    )
    names = ITALIC_NAMES if is_italic else UPRIGHT_NAMES

    # Weight and family metadata (REQ-07, §4.2). os2_weight MUST be set
    # before weight (OS/2 WeightWidthSlopeOnly precedence); weight MUST be
    # explicit to kill stale "Regular"/"Book" inheritance (GUD-02).
    font.os2_weight = SEMIBOLD_WEIGHT
    font.weight = SEMIBOLD_WEIGHT_NAME
    font.familyname = FAMILY_NAME
    font.fontname = names["fontname"]
    font.fullname = names["fullname"]

    # SFNT name table entries (§4.2).
    font.appendSFNTName("English (US)", "Family", FAMILY_NAME)
    font.appendSFNTName("English (US)", "SubFamily", names["sub_family"])
    font.appendSFNTName("English (US)", "Fullname", names["fullname"])
    font.appendSFNTName("English (US)", "PostScriptName", names["fontname"])

    # Embolden every glyph (REQ-04). ChangeWeight does not touch the italic
    # angle or the OS/2 italic flag, so REQ-03 holds by non-modification.
    font.selection.all()
    font.changeWeight(STROKE_WIDTH, EMBOLDEN_TYPE, 0, 0, COUNTER_TYPE)

    # Geometric cleanup (REQ-06): font-level removeOverlap + simplify.
    # Per-glyph intersect() cleanup is forbidden (Medium Dead-End #11).
    font.removeOverlap()
    font.simplify()

    # Enforce the monospace grid (REQ-05).
    for glyph in font.glyphs():
        glyph.width = MONOSPACE_WIDTH

    font.save(output_sfdir)
    font.close()


def main(argv):
    """CLI entry point. Returns the process exit code."""
    if len(argv) != 3:
        print(USAGE, file=sys.stderr)
        return 1

    input_sfdir = argv[1]
    output_sfdir = argv[2]

    if os.path.abspath(input_sfdir) == os.path.abspath(output_sfdir):
        print("Error: input and output paths must differ", file=sys.stderr)
        return 1

    generate_semibold(input_sfdir, output_sfdir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

## 9. Implementation Boundaries

- **Always do:** Retain the functional idempotency of the Python script. Validate advance widths after any geometry alteration. Follow the §4.3 calibration contract and record the selected stroke in the commit message/PR description before committing sources. Run `pytest tests/` and confirm 0 failures before declaring the Code phase complete. Verify `git diff` on the Medium artifact is empty.
- **Ask first:** Manual counter-space fixes to specific glyphs (only performed if the maintainer explicitly requests them — never as an automatic fallback). Any deviation from the §4.3 calibration contract (e.g., selecting a stroke outside the band/floor rules). Adding new dependencies or modifying CI configuration.
- **Never do:** Modify the zero-touch set (`Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, `features.py`, `Scripts/generate-css-decl`, `Scripts/zip-all-variants`). Modify `Scripts/generate-medium-source.py` or the committed Medium sources. Commit generated sources directly to `master` before maintainer visual QA sign-off (GH-006). Use per-glyph `intersect()` for cleanup. Ship a Medium-clone result silently when the calibration contract fails (escalate instead).

## 10. Rationale, Context & Architecture Decisions (ADRs)

The SemiBold sources are pre-generated by a standalone script and committed as canonical source files, following the Medium precedent. This leverages the existing zero-touch build pipeline (`Makefile` wildcard discovery, `custom_build_driver.find_sfdirs()`, dynamic `generate-css-decl`, auto-discovering `zip-all-variants`) at the cost of repository size — the same trade-off accepted for Medium.

`ChangeWeight` is mandated over interpolation because the Regular and Bold sources have non-matching point/contour topology, which rules out master-based interpolation; the `origin/feature/multi-weight-poc` interpolation branch is explicitly out of scope (PRD §2.3).

The stroke reference for weight 600 is unknown upstream — no calibrated reference exists (Medium used +34, range +30..+40). The §4.3 calibration contract replaces the Medium feature's single reference value with an empirical selection procedure plus an explicit failure/escalation path, per Clarification Report Resolutions 1 and 2.

**ADR decision:** No new ADR is created. The calibration band/floor policy is per-feature policy, not a hard-to-reverse architectural decision (Clarification Report §4), and the design reuses the already-recorded Medium architectural decisions. No conflict with existing ADRs (`0001-multi-stage-docker-legacy-tools.md`, `0002-multi-stage-docker-deferred-engine-port.md` — Docker toolchain records, unrelated to weight generation).

**Domain Glossary:** Term `SemiBold` already exists in `CONTEXT.md` (canonical, weight 600 between Medium and Bold; `_Avoid_`: semibold, semi bold, demi bold, DemiBold). No glossary change is required.

## 11. Dependencies & External Integrations

### Infrastructure Dependencies

- **INF-001**: `fontforge` (Python module) — required to execute `generate-semibold-source.py`. Present in the build toolchain (Dockerfile Stages 1/2 and the build-job runner); NOT present on the unit-test runner job, hence the fake-module test approach (§6). Real-FontForge verification (§4.2.1 font.weight gate, §6 idempotency verification) is performed on the build-job runner during Phase 1, not the unit-test runner.

### Third-Party Services

- **SVC-001**: Nerd Font patcher — optional (P2, FR-09). When `NerdFontPatching` is enabled in `config.schema.json` (boolean, default `false`), the patcher SHOULD successfully patch SemiBold and SemiBold Italic, producing "Fantasque Sans Mono Nerd Font SemiBold" and "Fantasque Sans Mono Nerd Font SemiBold Italic". Same scope and caveat as the Medium FR-09: patcher dispatch validation is external (not executed until a `NerdFontPatching=true` dispatch runs).

### Infrastructure Dependencies (build pipeline, zero-touch)

- **INF-002**: Build toolchain consumed by the existing pipeline, unchanged: `ttfautohint` (hinting), `woff-tools`/`sfnt2woff` (WOFF), `woff2`/`woff2_compress` (WOFF2), `zip`/`tar` (archives) — all already provisioned by the Dockerfile and CI workflows.

### Data Dependencies

- **DAT-001**: Input sources `Sources/FantasqueSansMono-Regular.sfdir` and `Sources/FantasqueSansMono-Italic.sfdir` — committed, static. No user data is collected, stored, or transmitted; font files are static binary assets (PRD §8.2).

## 12. Examples & Edge Cases

**Calibration scenarios (per §4.3, composite AND gate — every candidate must pass upright counters, italic counters, and the two-sided neighbor gate):**

- **In-band pass (composite pass):** 70 fails one or more sub-gates (e.g., italic counters or heavier-than-Bold); 60 passes all three → select **60** (highest grid candidate passing the composite gate in the 55–70 band).
- **Italic-only failure:** 70 passes upright counters and the two-sided neighbor gate but fails italic counters → descend to **60** per locked iteration order (Q2 AND-gate rule: a candidate must pass upright AND italic — never immediate escalation on the first italic failure). If 60 also fails italic, descend to 50, then 45.
- **Medium-clone block (Q3 two-sided gate):** 70 fails the "clearly heavier than Medium" side; 60, 50 also fail → descend. If 45 passes counters but is not clearly heavier than Medium (i.e., looks like a Medium-clone), the candidate is rejected → escalate to a maintainer decision. Never silently ship a Medium-clone result.
- **Band fail, step-down pass:** 70, 60 fail the composite gate; 50 passes → select **50** (first step-down below the band).
- **Floor pass:** 70, 60, 50 fail; 45 passes → select **45** (hard floor).
- **Escalation:** 70, 60, 50, 45 all fail the composite gate → single-pass approach declared failed → escalate to a maintainer decision (re-scope / abandon / manual fix). Never silently ship a Medium-clone or Bold-clone result.

**Geometric edge cases:**

- If algorithmic generation causes inner counter spaces (e.g., inside `e` or `a`) to overlap or collapse, the script prioritizes geometric validity (`removeOverlap`) over aesthetic legibility; the aesthetic outcome is governed by the §4.3 selection contract, and residual self-intersections from the LCG stroke are documented `accepted-deviation` deferred to Phase 4 visual QA (GH-006) — the Medium precedent recorded 252 upright / 465 italic self-intersecting glyphs, and SemiBold's ~1.6×–2.1× stroke raises this count; that is expected and accepted, not a defect.
- Advance-width drift: `ChangeWeight` may alter advance widths — the script re-sets all glyph widths to exactly 1060 after emboldening (REQ-05).
- Metadata pitfalls (learned from Medium): `os2_weight` before `weight`; explicit `weight = "SemiBold"`; lowercase `"retain"` counter type; watch for preferred-family records (IDs 16/17) as a side effect (GUD-03) — the Medium TASK-104 dump proved the documented assignment order produces no such side effects, and the SemiBold script follows the identical order.

**Idempotency:**

- Running the script twice on the same input produces identical contour geometry and metrics; only non-functional metadata (e.g., timestamps) may differ (REQ-08).

## 13. Validation Criteria

- **Unit suite:** `python -m pytest tests/` passes with 0 failures (83-test baseline plus the new SemiBold generation tests).
- **`Scripts/validate-font`** reports no `Error in ...` messages **beyond the recorded maintainer baseline exception** for both SemiBold and SemiBold Italic sources (inherited `Bad Glyph Name` on `slash_asterisk_asterisk_slash.liga` + documented `ChangeWeight` artifacts — accepted by maintainer exception; exit code is always `0` by design, so output inspection is the effective signal) (AC-004).
- **SFNT metadata** reports `font-weight: 600`, family grouping under "Fantasque Sans Mono" (§4.2, AC-005).
- **Advance width** strictly equals `1060` across all glyphs (AC-001).
- **Calibration:** the reference stroke is selected per §4.3 (composite AND gate — upright AND italic counters pass; render clearly heavier than Medium AND clearly lighter than Bold) and recorded in the commit/PR before sources are committed; QA checks apply to **both** the upright specimen and the italic specimen (AC-007).
- **`font.weight` acceptance gate (Q1, §4.2.1):** evidence recorded verbatim in `plan/` Execution Results, **independently tabulated for Run A (Regular→SemiBold) and Run B (Italic→SemiBoldItalic)** — Run B is the gating run for the stale `Weight: Book` risk and cannot be skipped; no combined-row elision is permitted. For each run: `font.weight` = `"SemiBold"` post-save, `Weight:` field in `font.props` = `"SemiBold"`, SFNT IDs 2/4/6 match the §4.2 table, no ID 16/17 preferred-family side effects, `os2_weight` = 600. Evidence is taken from the built TTF/OTF (not `.sfdir`).
- **Idempotency verification (Q4, REQ-08):** TEST-005 precedent (Medium plan v1.1) — two clean runs into separate output directories; all `.glyph` files and contours byte-identical; metrics (advance widths, `os2_weight`, `weight`, family/fontname/fullname) identical; `font.props` diffed **per-field** with only non-functional metadata (e.g., `ModificationTime`) allowed to differ. Evidence recorded verbatim in `plan/` Execution Results.
- **Build:** `make` succeeds and outputs standard TTF, OTF, SVG, WOFF, WOFF2 formats for all four variant permutations; evidenced via the standard-make workflow `.github/workflows/build-make.yml` (`make clean && make`, full `Variants/` upload) and via the `custom-build` workflow dispatch (compiles and packages the selected variant with no workflow modifications) (AC-003, AC-009).
- **Packaging:** release archives produced by `Scripts/zip-all-variants` include SemiBold and SemiBold Italic TTF/OTF files plus WOFF/WOFF2/SVG web fonts for all variant permutations (AC-008).
- **Zero regression:** `git diff` on `Scripts/generate-medium-source.py` and the committed Medium sources is empty; the zero-touch set is unmodified (AC-010).
- **Nerd Font patching** (P2 optional, FR-09): not executed until a `custom-build` dispatch with `NerdFontPatching=true` runs; the expected outputs ("Fantasque Sans Mono Nerd Font SemiBold" / "Fantasque Sans Mono Nerd Font SemiBold Italic") remain unrecorded until such a dispatch runs.

## 14. Related Specifications / Further Reading

- [Fantasque Sans Mono - SemiBold Font Weight PRD](../docs/prd-20260818-1636-semibold-font-weight.md)
- [Fantasque Sans Mono - Medium Font Weight Technical Specification](./spec-design-medium-weight.md) — the pattern this feature replicates
- [Clarification Report - SemiBold Font Weight](../docs/audit/clarification-report-semibold-font-weight-2026-08-20.md)
- [Domain Glossary - Custom Build Context](../CONTEXT.md)
- [Fantasque Sans Mono - Custom Build Workflow Specification](./spec-custom-build-workflow.md)
- [Fantasque Sans Mono - Nerd Font Patcher Specification](./spec-process-nerd-font-patcher.md)
