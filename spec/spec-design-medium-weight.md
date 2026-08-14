---
title: Fantasque Sans Mono - Medium Font Weight Technical Specification
version: 1.4
date_created: 2026-08-13
last_updated: 2026-08-14
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

## 1. Purpose & Scope

The purpose of this specification is to define the exact behavior, inputs, and outputs of the `generate-medium-source.py` script. It covers the FontForge API methods used, the metadata modifications required for the Medium weight, and the validation criteria to ensure the new font variants integrate seamlessly with the existing packaging and CI/CD pipelines.

## 1.1 Out of Scope

- Modifications to the existing `Makefile`, `custom-build.yml`, or any existing build scripts (`build.py`, `fontbuilder.py`, `generate-css-decl`).
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
- **REQ-02**: The script must accept two arguments: the input source `.sfdir` path and the output `.sfdir` path.
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

### 4.2 Font Metadata Modifications

The script must explicitly set the following properties on the `fontforge.font` object before saving:

| Property     | Value (Medium)               | Value (Medium Italic)               |
| :----------- | :--------------------------- | :---------------------------------- |
| `os2_weight` | `500`                        | `500`                               |
| `familyname` | `Fantasque Sans Mono`        | `Fantasque Sans Mono`               |
| `fontname`   | `FantasqueSansMono-Medium`   | `FantasqueSansMono-MediumItalic`    |
| `fullname`   | `Fantasque Sans Mono Medium` | `Fantasque Sans Mono Medium Italic` |

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
- **AC-006**: Given a `workflow_dispatch` trigger of `custom-build.yml`, When the workflow runs, Then Medium and Medium Italic variants are compiled and packaged without any workflow modifications, and the uploaded release artifact contains the Medium and Medium Italic font files for the selected variant.
- **AC-007**: Given the generated Medium sources, When a maintainer performs visual inspection of the core ASCII glyphs (A–Z, a–z, 0–9) in FontForge or on a rendered specimen page, Then the glyphs are legible, dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`) retain discernible inner counters, and at least one maintainer records approval via PR review comment or approval.

## 6. Test Automation Strategy & Testing Seams

- **Testing Seams**: The boundary is the standard `Makefile` build output and the output of `Scripts/validate-font`.
- **Test Levels**: 
  - **Unit Testing**: Run `pytest tests/` to ensure no regressions in existing build logic.
  - **Validation Testing**: Run `Scripts/validate-font` against the newly generated `Sources/FantasqueSansMono-Medium.sfdir`.
  - **Monospace Integrity**: Verify all glyph advance widths in the output `.sfdir` files equal `1060`.

> [!WARNING]
> **Codebase note:** `Scripts/validate-font` currently always exits with code `0` (a hardcoded `exit 0` precedes `exit $error` in the script). Validation success must therefore be determined by inspecting the script output for `Error in ...` messages, not by the exit code.

## 7. Project Structure & Commands

### Project Structure
- `Scripts/generate-medium-source.py`: [NEW] The Python script that generates the font sources.
- `Sources/FantasqueSansMono-Medium.sfdir`: [NEW] Output directory (to be committed).
- `Sources/FantasqueSansMono-MediumItalic.sfdir`: [NEW] Output directory (to be committed).

### Commands
- **Generate Sources:** `python Scripts/generate-medium-source.py Sources/FantasqueSansMono-Regular.sfdir Sources/FantasqueSansMono-Medium.sfdir`
- **Build Fonts:** `make`
- **Validate Sources:** `Scripts/validate-font Sources/FantasqueSansMono-Medium.sfdir`

## 8. Code Style & Conventions

```python
import fontforge
import os
import sys

def generate_medium(input_sfdir, output_sfdir):
    font = fontforge.open(input_sfdir)
    
    # Example logic for setting metadata
    is_italic = os.path.basename(input_sfdir).startswith("FantasqueSansMono-Italic")
    sub_family = "Medium Italic" if is_italic else "Medium"
    
    font.os2_weight = 500
    font.familyname = "Fantasque Sans Mono"
    # ... set other names ...

    font.selection.all()
    # Stroke expansion of 34 em-units; "retain" preserves inner counters per PRD GH-006.
    font.changeWeight(34, "LCG", 0, 0, "retain")
    font.removeOverlap()
    font.simplify()
    # Italic preservation (REQ-03): changeWeight does not modify font.italicangle or
    # the OS/2 fsSelection italic bit, so they are carried over by non-modification.

    # Enforce monospace grid
    for glyph in font.glyphs():
        glyph.width = 1060

    font.save(output_sfdir)
    font.close()

if __name__ == "__main__":
    generate_medium(sys.argv[1], sys.argv[2])
```

## 9. Implementation Boundaries

- **Always do:** Retain the idempotency of the Python script. Validate advance widths after any geometry alteration.
- **Ask first:** Before committing any manual counter-space fixes to specific glyphs.
- **Never do:** Modify `Makefile`, `config.schema.json`, `configure.py`, `custom_build_driver.py`, or any **existing** GitHub Actions workflow (`custom-build.yml`) to accommodate the Medium weight build process. (A new verification-only workflow `.github/workflows/build-make.yml` — standard `make clean && make` — was added during execution to evidence AC-003/004/005.)

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

- `Scripts/validate-font` reports no `Error in ...` messages **beyond the documented baseline/artifact profile** for both Medium and Medium Italic sources (inherited `Bad Glyph Name` on `slash_asterisk_asterisk_slash.liga` + documented `ChangeWeight` artifacts — accepted by maintainer exception; exit code is always `0` by design, so output inspection is the effective signal).
- SFNT metadata reports `font-weight: 500`.
- Advance width strictly equals `1060` across all glyphs.
- Successfully verified by `make` and outputs standard TTF, OTF, and web font formats.
- Release archives produced by `Scripts/zip-all-variants` include Medium and Medium Italic TTF/OTF files plus WOFF/WOFF2 web fonts for all variant permutations.
- **Nerd Font Patching**: Successfully patches when NerdFontPatching is enabled, generating "Fantasque Sans Mono Nerd Font Medium" and "Fantasque Sans Mono Nerd Font Medium Italic".

## 14. Related Specifications / Further Reading

- [Fantasque Sans Mono - Medium Font Weight PRD](../docs/prd-20260813-0921-medium-font-weight.md)
