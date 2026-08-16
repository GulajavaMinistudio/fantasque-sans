---
title: Fantasque Sans Mono - Medium Font Weight Technical Specification
version: 1.6
date_created: 2026-08-13
last_updated: 2026-08-16
owner: Specification Architect
tags: [font, build, medium-weight, python, fontforge]
---
<!-- markdownlint-disable  -->
# Introduction

This document specifies the technical design for introducing a Medium (weight 500) and Medium Italic variant to the Fantasque Sans Mono font family. The design relies on algorithmic generation using FontForge's Python API to create the `.sfdir` sources, which will be committed directly to the repository to leverage the existing `Makefile` build pipeline without requiring architectural changes.

**Revision 1.1** — Remediated per gap analysis against PRD v1.1 (2026-08-13): added italic preservation, packaging, CI/CD, and visual QA acceptance criteria; clarified validation criteria and implementation boundaries.

**Revision 1.2** — Remediated per Clarification Report [Review Iteration 2] (2026-08-13): corrected variant permutations enumeration to 4 (Normal, LargeLineHeight, NoLoopK, LargeLineHeight-NoLoopK) per `Scripts/build.py` option matrix; applied `counter_type="retain"` per user decision (T-2) to preserve inner counters per PRD GH-006; clarified italic detection and preservation in §8 code sample (T-4).

**Revision 1.3** — Erratum applied during Phase 1 execution (2026-08-13): corrected `counter_type` spelling from `"Retain"` to `"retain"` (lowercase) in §1.2 and §8. FontForge's Python binding is case-sensitive and only accepts the lowercase spelling (`co_types` flaglist in `fontforge/python.cpp`); the capitalized form raises `ValueError: Unknown counter type` at runtime.
**Revision 1.4** — Sync to implementation (2026-08-14): the per-glyph `intersect()` cleanup deviation was **reverted** during Phase 2 (Boolean intersect destroyed 661 glyph outlines — plan Dead-End #11); the script follows the plan-exact pipeline (`changeWeight(34, "LCG", 0, 0, "retain")` → font-level `removeOverlap()` + `simplify()` → width 1060). Residual self-intersections (252 upright / 465 italic) are a documented limitation deferred to visual QA (§12). `validate-font` "no `Error in`" is unachievable for any source (inherited `Bad Glyph Name` ligature + `ChangeWeight` artifacts) — accepted by maintainer exception (§13). AC-003/004/005 evidenced via the new standard-make workflow `build-make.yml`; AC-006 via `custom-build`.
**Revision 1.5** — Sync to plan v1.1 completion state (2026-08-14): plan `plan-design-medium-weight-v1.1.md` is `status: Complete` with all 18 tasks closed (TASK-004/007/008 carry ⚠️ markers documenting maintainer-accepted exceptions/deviations, not open work). §4.1 now specifies the CLI error contract (wrong argument count → usage + exit 1; `input == output` → error + exit 1) per the implemented `main()`; §6/§7 add the 12 mock-`fontforge` unit tests (81 total suite) and `tests/test_generate_medium_source.py`; §8 code sample replaced with the exact implemented script (no placeholders); §9 never-do list extended to the full CON-07 zero-touch set (`build.py`, `fontbuilder.py`, `features.py`); AC-007 gains the programming-symbol-cluster criterion from plan TASK-016.
**Revision 1.6** — Code-review remediation sync (`plan/plan-refactor-medium-weight-v1.0.md` Phases 1–2, 2026-08-16): §5 AC-006 wording corrected to "the selected variant(s)" (DOC-003/B-08); §13 Nerd Font patching marked `not executed` — P2 optional, TASK-013(c) (REQ-002/B-02); §1.1 CON-07 enumeration qualified to the canonical 8-file set (DOC-001/B-05); §4.2 documents the `weight = "Medium"` property and §8 code sample includes it (SEC-002/B-04); §6/§7/§13 unit-test counts updated to 14 script tests / 83 total.

## 1. Purpose & Scope

The purpose of this specification is to define the exact behavior, inputs, and outputs of the `generate-medium-source.py` script. It covers the FontForge API methods used, the metadata modifications required for the Medium weight, and the validation criteria to ensure the new font variants integrate seamlessly with the existing packaging and CI/CD pipelines.

## 1.1 Out of Scope

- Modifications to the existing `Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, or `features.py` (the CON-07 zero-touch set; see §9), nor to `generate-css-decl` (zero-touch by feature design — FR-05 requires it to read `os2_weight` dynamically without modification).
- Algorithmic adjustment or manual tuning of individual glyph counter spaces within the script (this will be a manual post-generation task if necessary).
- Generation of the Medium variant on-the-fly during standard builds.
- Generation of weights other than 500 (Medium).
- Proportional `FantasqueSans` family generation.

## 1.2 Open Questions & Assumptions

> [!WARNING]
> **ASSUMPTION:** The generated sources will be committed to version control. The generation script (`generate-medium-source.py`) is run manually once by the developer/maintainer and is not executed in the CI pipeline.

> [!NOTE]
> **RESOLVED DECISION (Clarification Iteration 2, 2026-08-13; erratum 1.3):** `counter_type="retain"` (lowercase, per FontForge's case-sensitive Python binding) is used in the `changeWeight` call to preserve inner counters, aligning with PRD GH-006 counter-legibility AC (T-2).

> [!WARNING]
> **ASSUMPTION:** A stroke expansion of 34 em-units (within the PRD's suggested +30 to +40 range) is used as the reference value in this specification. Final tuning may occur after post-generation visual inspection.

## 2. Definitions

- **Medium**: A font weight variant corresponding to CSS `font-weight: 500`, sitting visually between Regular (400) and Bold (700).
- **Em-unit**: The internal coordinate unit used in FontForge. Fantasque Sans Mono relies on specific advance widths (1060 em-units) to maintain monospace integrity.
- **SFNT**: The table structure used by TrueType and OpenType fonts to store metadata (like Family and SubFamily names).

## 3. Requirements, Constraints & Guidelines

- **REQ-01**: A single Python script `Scripts/generate-medium-source.py` must generate the Medium `.sfdir` sources.
- **REQ-02**: The script must accept exactly two arguments: the input source `.sfdir` path and the output `.sfdir` path. Any other argument count must print the usage message to stderr and exit non-zero.
- **CON-01**: The script must use FontForge's `ChangeWeight` API to add weight.
- **CON-02**: Every generated glyph must have its advance width strictly set to exactly `1060`.
- **CON-03**: The script must call font-level `removeOverlap()` and `simplify()` (applied across all glyphs) after `ChangeWeight`.
- **CON-04**: The generated `.sfdir` source must have its `os2_weight` property set to `500`.
- **CON-05**: The script must be functionally idempotent — running it multiple times with the same input produces identical contour geometry and metrics. Differences in non-functional metadata (e.g., timestamps) are permitted.
- **CON-06**: The script must never modify the input source `.sfdir` in place. It may only read from the input path and write to the output path.
- **REQ-03**: The script must preserve the italic angle and all other style-specific metrics of the input source. For Medium Italic, the OS/2 italic flag must remain set.
- **GUD-01**: The stroke expansion applied via `ChangeWeight` should fall within +30 to +40 em-units (reference value: 34) to produce a weight visually distinct from both Regular and Bold.

## 4. Interfaces & Data Contracts

### 4.1 Script Execution Interface

```bash
python Scripts/generate-medium-source.py <input.sfdir> <output.sfdir>
```

**Example (Medium):**
```bash
python Scripts/generate-medium-source.py Sources/FantasqueSansMono-Regular.sfdir Sources/FantasqueSansMono-Medium.sfdir
```

**Example (Medium Italic):**
```bash
python Scripts/generate-medium-source.py Sources/FantasqueSansMono-Italic.sfdir Sources/FantasqueSansMono-MediumItalic.sfdir
```

**CLI Error Contract (implemented in `main()`):**
- Wrong argument count (anything other than exactly two): print `Usage: python generate-medium-source.py <input.sfdir> <output.sfdir>` to stderr, exit code `1`.
- `input == output` (after `os.path.abspath` normalization): print `Error: input and output paths must differ` to stderr, exit code `1` (CON-06).

### 4.2 Font Metadata Modifications

The script must explicitly set the following properties on the `fontforge.font` object before saving:

| Property     | Value (Medium)               | Value (Medium Italic)               |
| :----------- | :--------------------------- | :---------------------------------- |
| `os2_weight` | `500`                        | `500`                               |
| `weight`     | `Medium`                     | `Medium`                            |
| `familyname` | `Fantasque Sans Mono`        | `Fantasque Sans Mono`               |
| `fontname`   | `FantasqueSansMono-Medium`   | `FantasqueSansMono-MediumItalic`    |
| `fullname`   | `Fantasque Sans Mono Medium` | `Fantasque Sans Mono Medium Italic` |

`weight` is set to `"Medium"` so the generated sources do not inherit the stale `Weight: Regular` / `Weight: Book` strings from their inputs (code-review remediation finding B-04, refactor plan SEC-002).

The script must also update the SFNT names in `font.appendSFNTName('English (US)', ...)`:
- `Family`: `"Fantasque Sans Mono"`
- `SubFamily`: `"Medium"` or `"Medium Italic"`
- `Fullname`: `"Fantasque Sans Mono Medium"` or `"Fantasque Sans Mono Medium Italic"`
- `PostScriptName`: `"FantasqueSansMono-Medium"` or `"FantasqueSansMono-MediumItalic"`

For Medium Italic, the script must additionally preserve `italicangle` and the OS/2 italic flag from the source Italic font. These style-specific values must be carried over unchanged into the generated Medium Italic source and must not be reset by the script.

## 5. Acceptance Criteria

- **AC-001**: Given a Regular `.sfdir` source, When the generation script is run, Then a Medium `.sfdir` directory is produced with `os2_weight` set to `500`.
- **AC-002**: Given an Italic `.sfdir` source, When the generation script is run, Then a Medium Italic `.sfdir` directory is produced with `os2_weight` set to `500`, the italic angle preserved, and the OS/2 italic flag set.
- **AC-003**: The system shall compile the Medium variants correctly into TTF, OTF, and web fonts for all variant permutations (Normal, LargeLineHeight, NoLoopK, LargeLineHeight-NoLoopK) in the appropriate `Variants/` subdirectories when `make` is executed, without any modifications to `Makefile`.
- **AC-004**: The system shall generate a valid CSS declaration for the Medium variants specifying `font-weight: 500`, with `font-style: normal` for Medium and `font-style: italic` for Medium Italic, referencing WOFF2 and WOFF files in the `src` descriptor.
- **AC-005**: The system shall include Medium and Medium Italic font files (TTF, OTF) plus their WOFF and WOFF2 web fonts in the release archives produced by `Scripts/zip-all-variants`.
- **AC-006**: Given a `workflow_dispatch` trigger of `custom-build.yml`, When the workflow runs, Then Medium and Medium Italic variants are compiled and packaged without any workflow modifications, and the uploaded release artifact contains the Medium and Medium Italic font files for the selected variant(s).
- **AC-007**: Given the generated Medium sources, When a maintainer performs visual inspection of the core ASCII glyphs (A–Z, a–z, 0–9) in FontForge or on a rendered specimen page, Then the glyphs are legible at 12px, 14px, and 16px, dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`) retain discernible inner counters, programming symbol clusters (`->`, `=>`, `!=`, `//`, `/*`, `*/`, `||`, `&&`, `<=`, `>=`, `::`, `<-`, `++`, `--`) render without glyph collisions, and at least one maintainer records approval via PR review comment or approval.

## 6. Test Automation Strategy & Testing Seams

- **Testing Seams**: The boundary is the standard `Makefile` build output and the output of `Scripts/validate-font`.
- **Test Levels**: 
  - **Unit Testing**: `tests/test_generate_medium_source.py` — 14 tests with a fake `fontforge` module injected into `sys.modules` (the CI runner has no real `fontforge`). Covers: CLI argument-count contract (REQ-02), `input == output` guard (CON-06), upright/italic metadata mapping including `font.weight == "Medium"` (CON-04, §4.2), `changeWeight(34, "LCG", 0, 0, "retain")` call, `removeOverlap`/`simplify` invocation and runtime order including `selection.all()` (CON-03), width enforcement to 1060 (CON-02), save-target correctness (CON-06). Run `pytest tests/` — full suite is 83 tests (69 existing + 14 new), 0 failures.
  - **Validation Testing**: Run `Scripts/validate-font` against the newly generated `Sources/FantasqueSansMono-Medium.sfdir`.
  - **Monospace Integrity**: Verify all glyph advance widths in the output `.sfdir` files equal `1060`.

> [!WARNING]
> **Codebase note:** `Scripts/validate-font` currently always exits with code `0` (a hardcoded `exit 0` precedes `exit $error` in the script). Validation success must therefore be determined by inspecting the script output for `Error in ...` messages, not by the exit code.

## 7. Project Structure & Commands

### Project Structure
- `Scripts/generate-medium-source.py`: [NEW] The Python script that generates the font sources.
- `tests/test_generate_medium_source.py`: [NEW] 14 unit tests using a fake `fontforge` module (see §6).
- `Sources/FantasqueSansMono-Medium.sfdir`: [NEW] Output directory (to be committed).
- `Sources/FantasqueSansMono-MediumItalic.sfdir`: [NEW] Output directory (to be committed).

### Commands
- **Generate Sources:** `python Scripts/generate-medium-source.py Sources/FantasqueSansMono-Regular.sfdir Sources/FantasqueSansMono-Medium.sfdir`
- **Build Fonts:** `make`
- **Validate Sources:** `Scripts/validate-font Sources/FantasqueSansMono-Medium.sfdir`
- **Unit Tests:** `python -m pytest tests/` (83 tests, 0 failures)

## 8. Code Style & Conventions

```python
#!/usr/bin/env python3
"""Generate a Medium (weight 500) font source from a Regular or Italic source."""

import os
import sys

import fontforge

STROKE_WIDTH = 34        # em-units (GUD-01: +30 to +40; reference value 34)
EMBOLDEN_TYPE = "LCG"
COUNTER_TYPE = "retain"  # lowercase only; FontForge binding is case-sensitive
MONOSPACE_WIDTH = 1060   # CON-02
MEDIUM_WEIGHT = 500      # CON-04
MEDIUM_WEIGHT_NAME = "Medium"  # §4.2; kills stale "Regular"/"Book" inheritance

FAMILY_NAME = "Fantasque Sans Mono"
ITALIC_PREFIX = "FantasqueSansMono-Italic"

UPRIGHT_NAMES = {
    "fontname": "FantasqueSansMono-Medium",
    "fullname": "Fantasque Sans Mono Medium",
    "sub_family": "Medium",
}
ITALIC_NAMES = {
    "fontname": "FantasqueSansMono-MediumItalic",
    "fullname": "Fantasque Sans Mono Medium Italic",
    "sub_family": "Medium Italic",
}

USAGE = "Usage: python generate-medium-source.py <input.sfdir> <output.sfdir>"


def generate_medium(input_sfdir, output_sfdir):
    font = fontforge.open(input_sfdir)

    is_italic = os.path.basename(os.path.normpath(input_sfdir)).startswith(
        ITALIC_PREFIX
    )
    names = ITALIC_NAMES if is_italic else UPRIGHT_NAMES

    # Weight and family metadata (CON-04, section 4.2).
    font.os2_weight = MEDIUM_WEIGHT
    font.weight = MEDIUM_WEIGHT_NAME
    font.familyname = FAMILY_NAME
    font.fontname = names["fontname"]
    font.fullname = names["fullname"]

    # SFNT name table entries (section 4.2).
    font.appendSFNTName("English (US)", "Family", FAMILY_NAME)
    font.appendSFNTName("English (US)", "SubFamily", names["sub_family"])
    font.appendSFNTName("English (US)", "Fullname", names["fullname"])
    font.appendSFNTName("English (US)", "PostScriptName", names["fontname"])

    # Embolden every glyph (CON-01, GUD-01). ChangeWeight does not touch the
    # italic angle or the OS/2 italic flag, so REQ-03 holds by non-modification.
    font.selection.all()
    font.changeWeight(STROKE_WIDTH, EMBOLDEN_TYPE, 0, 0, COUNTER_TYPE)

    # Geometric cleanup (CON-03): font-level removeOverlap + simplify.
    # Per-glyph intersect() cleanup is forbidden (see section 12).
    font.removeOverlap()
    font.simplify()

    # Enforce the monospace grid (CON-02).
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

    generate_medium(input_sfdir, output_sfdir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

## 9. Implementation Boundaries

- **Always do:** Retain the idempotency of the Python script. Validate advance widths after any geometry alteration.
- **Ask first:** Before committing any manual counter-space fixes to specific glyphs.
- **Never do:** Modify `Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, or `features.py` to accommodate the Medium weight build process. (A new verification-only workflow `.github/workflows/build-make.yml` — standard `make clean && make` — was added during execution to evidence AC-003/004/005.)

## 10. Rationale, Context & Architecture Decisions (ADRs)

The PRD explicitly states the Medium weight must not introduce changes to the core build infrastructure or `Makefile`. Therefore, the Medium weight source `.sfdir` files will be pre-generated by a standalone script and committed directly to the repository as canonical sources. This trade-off significantly reduces CI pipeline complexity at the cost of repository size.

Additionally, `ChangeWeight` is mandated over `interpolateFonts()` because the Regular and Bold sources have non-matching point/contour topology (e.g., lowercase `a`: 20 points in Regular vs 19 in Bold), which rules out interpolation between masters.

## 11. Dependencies & External Integrations

### Infrastructure Dependencies
- **INF-001**: `fontforge` (Python Module) - Required to execute the `generate-medium-source.py` script.

## 12. Examples & Edge Cases

If algorithmic generation causes inner counter spaces (e.g., inside the letters `e` or `a`) to overlap or collapse completely, the script must prioritize geometric validity (`removeOverlap`) over aesthetic legibility, leaving the aesthetic fix as a subsequent manual process. Residual self-intersections from the algorithmic `ChangeWeight` stroke (252 upright / 465 italic glyphs via `selfIntersects()`) are a documented limitation deferred to Phase 4 visual QA (visually accepted by the maintainer). The script MUST NOT use per-glyph `intersect()` for cleanup — Boolean intersect destroys non-overlapping outer/inner contours (plan Dead-End #11).

Visual QA must additionally confirm that programming symbol clusters (`->`, `=>`, `!=`, `//`, `/*`, `*/`, `||`, `&&`, `<=`, `>=`, `::`, `<-`, `++`, `--`) render without glyph collisions, and that all uppercase and lowercase Latin letters and digits remain legible at 12px, 14px, and 16px rendering sizes.

## 13. Validation Criteria

- Unit suite: `python -m pytest tests/` passes with 0 failures (83 tests: 69 existing + 14 new for the generation script).
- `Scripts/validate-font` reports no `Error in ...` messages **beyond the documented baseline/artifact profile** for both Medium and Medium Italic sources (inherited `Bad Glyph Name` on `slash_asterisk_asterisk_slash.liga` + documented `ChangeWeight` artifacts — accepted by maintainer exception; exit code is always `0` by design, so output inspection is the effective signal).
- SFNT metadata reports `font-weight: 500`.
- Advance width strictly equals `1060` across all glyphs.
- Successfully verified by `make` and outputs standard TTF, OTF, and web font formats. AC-003/004/005 are evidenced via the standard-make workflow `.github/workflows/build-make.yml` (`make clean && make`, full `Variants/` upload); AC-006 via the `custom-build` workflow dispatch (compiles and packages the selected variant with no workflow modifications).
- Release archives produced by `Scripts/zip-all-variants` include Medium and Medium Italic TTF/OTF files plus WOFF/WOFF2 web fonts for all variant permutations.
- **Nerd Font Patching** (`not executed` — P2 optional, TASK-013(c)): not verified by a `custom-build` dispatch with `NerdFontPatching=true`; the expected outputs ("Fantasque Sans Mono Nerd Font Medium" / "Fantasque Sans Mono Nerd Font Medium Italic") remain unrecorded until such a dispatch runs.

## 14. Related Specifications / Further Reading

- [Fantasque Sans Mono - Medium Font Weight PRD](../docs/prd-20260813-0921-medium-font-weight.md)
