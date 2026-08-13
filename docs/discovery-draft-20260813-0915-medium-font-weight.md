---
title: Project Discovery & Architecture Summary - Medium Font Weight Variant
status: DRAFT (Phase 0)
date_analyzed: 2026-08-13
---
<!-- markdownlint-disable -->
# Project Discovery Summary: Medium Font Weight Variant

## 1. Project Overview

Fantasque Sans Mono currently provides 4 standard weight/style variants: Regular, Bold, Italic, and Bold Italic across all built options (Normal, NoLoopK, LargeLineHeight). The objective of this feature is to introduce a **Medium** font weight variant (`FantasqueSansMono-Medium` and optional `FantasqueSansMono-MediumItalic`), positioning it visually between Regular (CSS weight 400) and Bold (CSS weight 700) at approximately CSS weight 500/600.

Since hand-drawn font sources (`.sfdir`) for the Medium weight are not available upstream, the project will employ an automated, script-driven **Algorithmic Weight Generation (Embolden/ChangeWeight)** approach using FontForge Python API to generate `Sources/FantasqueSansMono-Medium.sfdir` once, which will then be committed as canonical source files.

## 2. Technology Stack & Infrastructure

*(Refer to [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) for full project stack.)*

- **Font Processing Engine:** FontForge Python API (`fontforge` module)
- **Scripting Language:** Python 3 (running via containerized FontForge environment or local FontForge Python interpreter)
- **Build Pipeline Integration:** GNU `Makefile` (wildcard matching `Sources/FantasqueSansMono*.sfdir`)
- **CI/CD & Cloud Build:** GitHub Actions (`custom-build.yml`), Docker (`ubuntu:26.04` multi-stage)

## 3. Current Architecture Assessment

- **Strengths:** 
  - **Zero-touch Makefile integration:** The existing `Makefile` discovers sources via `SOURCES=$(wildcard Sources/FantasqueSansMono*.sfdir)`. Once `Sources/FantasqueSansMono-Medium.sfdir` exists in the repository, `make` and `Scripts/generate-font-variants` will automatically detect and build TTF, OTF, WOFF, WOFF2, and ZIP archives without breaking legacy constraints (CON-001).
  - **Custom Build Cloud Compatibility:** The host runner/container driver processes all `.sfdir` files present in `Sources/`, requiring zero changes to `config.schema.json` or `configure.py` for core weight inclusion.
- **Tech Debt & Risks:**
  - **Incompatible Master Splines:** Regular and Bold glyphs do not have 1:1 point/contour topology compatibility (e.g., lowercase `a` has 20 points in Regular vs 19 points in Bold). Interpolation (`fontforge.interpolateFonts`) is unviable without manual vector editing.
  - **Algorithmic Emboldening Risks:** Applying `ChangeWeight` algorithmically on Regular glyphs may cause inner counter space shrinkage/clogging in dense glyphs (e.g., `e`, `a`, `s`, `@`, `%`, `&`, `8`).
  - **Monospace Width Maintenance:** FontForge weight transformation functions can alter advance width metrics. Scripts MUST explicitly re-enforce uniform advance width (1200 em units) across all generated glyphs to maintain strict monospace grid alignment.

## 4. Operational Workflows & Feasibility Analysis

1. **Workflow A: One-off Source Generation (`Scripts/generate-medium-source.py`)**
   - Script accepts `Sources/FantasqueSansMono-Regular.sfdir` as input.
   - Applies an incremental embolden transformation (e.g. +30 to +40 em-units stroke expansion).
   - Enforces uniform advance width (1200 em units) and cleans up self-intersecting splines (`simplify()` and `removeOverlap()`).
   - Exports output to `Sources/FantasqueSansMono-Medium.sfdir`.
   - Repeats process for `Italic` to produce `FantasqueSansMono-MediumItalic.sfdir` if desired.
   - The generated `.sfdir` directory is visually inspected and committed to Git.

2. **Workflow B: Automated Build Execution**
   - Running `make` compiles Regular, Bold, Italic, BoldItalic, and the new Medium variants into `Variants/Normal/TTF/`.
   - `Scripts/zip-all-variants` packages the new Medium font binaries into release bundles.

## 5. Handoff Notes for Product Manager (/sdlc-draft-prd)

Before drafting the PRD via `/sdlc-draft-prd`, the PM should note:
- **Scope Limitation:** This feature adds pre-generated Medium `.sfdir` sources to the repository using a one-off Python utility script, rather than adding runtime font-weight sliders to the Custom Build workflow.
- **Glyph Quality Criteria:** Acceptance Criteria must mandate visual validation for core ASCII/English glyphs (A-Z, a-z, 0-9, common programming symbols `->`, `=>`, `!=`, `//`) to ensure inner counters remain legible and advance widths stay strictly 1200 em units.
- **Delivery Scope:** Decide whether Medium Italic (`FantasqueSansMono-MediumItalic.sfdir`) is included in MVP or if MVP only targets `FantasqueSansMono-Medium.sfdir`.
