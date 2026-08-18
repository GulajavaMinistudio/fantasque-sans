---
title: Project Discovery & Architecture Summary - SemiBold Font Weight Variant
status: DRAFT (Phase 0)
date_analyzed: 2026-08-18
---
<!-- markdownlint-disable -->
# Project Discovery Summary: SemiBold Font Weight Variant

## 1. Project Overview

Fantasque Sans Mono currently provides 6 weight/style variants: Regular, Medium, Bold, Italic, Medium Italic, and Bold Italic across all built options (Normal, LargeLineHeight, NoLoopK, LargeLineHeight-NoLoopK). The objective of this feature is to introduce a **SemiBold** font weight variant (`FantasqueSansMono-SemiBold` and `FantasqueSansMono-SemiBoldItalic`), positioning it visually between Medium (CSS weight 500) and Bold (CSS weight 700) at CSS weight 600.

Since hand-drawn font sources (`.sfdir`) for the SemiBold weight are not available upstream, the project reuses the proven **Algorithmic Weight Generation (Embolden/ChangeWeight)** approach from the shipped Medium Weight feature (`spec-design-medium-weight.md` v1.6, plans v1.0/v1.1): a standalone script generates `Sources/FantasqueSansMono-SemiBold.sfdir` (and the Italic counterpart) once, and the results are committed as canonical source files.

## 2. Technology Stack & Infrastructure

*(Refer to [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) for the full project stack.)*

- **Font Processing Engine:** FontForge Python API (`fontforge` module) — `changeWeight(..., "LCG", ..., "retain")`, font-level `removeOverlap()` + `simplify()`.
- **Scripting Language:** Python 3 — standalone one-shot maintainer tool, not executed in CI (Medium Spec ASSUMPTION-001 precedent).
- **Build Pipeline Integration:** GNU `Makefile` wildcard `Sources/FantasqueSansMono*.sfdir` — zero modifications required (proven by Medium AC-003..AC-006).
- **Downstream Tooling:** `generate-css-decl` (reads `os2_weight` dynamically), `zip-all-variants`, `custom_build_driver.py` `find_sfdirs()`, and the evidence workflow `build-make.yml`.
- **Testing:** `pytest` with fake-`fontforge` module injection (the CI runner has no real FontForge); current macro gate is 83/83 tests.

## 3. Current Architecture Assessment

- **Strengths:**
  - **Zero-touch integration is already proven.** The Medium feature shipped on `master` with the same wildcard discovery, dynamic CSS weight mapping, archive packaging, and CI evidence path. A new `.sfdir` pair flows through the entire pipeline with zero core-infrastructure changes (CON-07 set).
  - **Established naming and metadata conventions.** The Medium round fixed the critical SFNT pitfalls: `font.weight` must be set explicitly to kill stale `Regular`/`Book` inheritance (finding B-04), `os2_weight` must be assigned before `weight` (OS2_WeightWidthSlopeOnly precedence, PRN-102), and `counter_type` must be the lowercase `"retain"` spelling (Spec erratum 1.3).
  - **Reusable test and verification patterns.** The 14 mock-injection unit tests, idempotency diff checks, width-grid audit (1060), SFNT name-table dump, and `build-make.yml` evidence workflow map 1:1 onto the SemiBold variant.
  - **Codified dead-ends.** Per-glyph `intersect()` cleanup destroys outlines (Dead-End #11); `validate-font` always exits 0 so output inspection is the real signal.
- **Tech Debt & Risks:**
  - **Counter clogging scales with stroke width (top risk).** The Medium stroke of 34 em-units already left 252 upright / 465 italic residual self-intersections, accepted via maintainer exception and deferred to visual QA. A SemiBold stroke (approximately double) raises the clogging risk on dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`) significantly. Manual glyph fixes may become necessary (Spec §9 "Ask first" boundary).
  - **Stroke reference value unknown.** Medium used +34 em-units (GUD-01 range +30..+40). No calibrated reference exists for weight 600; it must be established empirically via specimen renders at candidate values (e.g., 50/60/70 em-units) against the Medium and Bold neighbors.
  - **`validate-font` baseline profile carries over.** A literal clean run is unachievable for any source (inherited `Bad Glyph Name` ligature plus `ChangeWeight` artifacts) — the maintainer exception precedent from Medium must be re-recorded, not re-litigated.
  - **Unmerged interpolation alternative.** Branch `origin/feature/multi-weight-poc` (19 commits ahead of `master`) contains a full harmonized-master interpolation pipeline with a SemiBold contract (factor 0.67 exact, `os2_weight 600`, `"SemiBold"` weight name). It is NOT recommended for adoption — it is far heavier (harmonization, tangent analysis, build-time generation) and incompatible with the zero-touch local `make` path — but it is a historical naming/weight-ladder reference.

## 4. Operational Workflows & Feasibility Analysis

1. **Workflow A: One-off Source Generation (`Scripts/generate-semibold-source.py`)**
   - Standalone copy of the Medium generator with SemiBold constants — no modification to the shipped Medium artifact (zero-regression).
   - Accepts `Sources/FantasqueSansMono-Regular.sfdir` (and `-Italic`) as input; single-pass `changeWeight(stroke, "LCG", 0, 0, "retain")` with a calibrated stroke (~55–70 em-units, reference value pending specimen calibration).
   - Sets `os2_weight = 600`, `font.weight = "SemiBold"`, family `Fantasque Sans Mono`, `fontname` `FantasqueSansMono-SemiBold`, fullname `Fantasque Sans Mono SemiBold` (+ Italic counterparts), plus explicit SFNT names (Family/SubFamily/Fullname/PostScriptName).
   - Enforces the monospace grid (width 1060), preserves italic metrics by non-modification (`italicangle` -11.0, OS/2 italic flag).
   - Outputs are visually inspected (specimen at candidate stroke values) and committed to a temporary feature branch.

2. **Workflow B: Automated Build Execution (Zero-Touch)**
   - `make` discovers the new sources via wildcard and compiles TTF/OTF/WOFF/WOFF2 into all 4 `Variants/` permutations.
   - `generate-css-decl` emits `font-weight: 600` automatically from `os2_weight`.
   - `zip-all-variants` packages the SemiBold binaries into the variant archives; `build-make.yml` evidences the standard-make path; `custom-build.yml` dispatches compile the selected variant without workflow changes.

## 5. Handoff Notes for Product Manager (/sdlc-draft-prd)

Before drafting the PRD via `/sdlc-draft-prd`, the PM should note:

- **Locked decisions (Discovery brainstorming 2026-08-18):** standalone generation script (no regression to the shipped Medium artifact); single-pass emboldening from Regular/Italic; MVP includes SemiBold Italic; official naming `"SemiBold"` (`os2_weight 600`).
- **Stroke calibration assumption [ASSUMPTION]:** the SemiBold reference stroke (~55–70 em-units) must be resolved through specimen calibration during execution; the PRD must require visual QA acceptance criteria covering dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`) and programming symbol clusters (`->`, `=>`, `!=`, `//`, `/*`, `*/`, `||`, `&&`, `<=`, `>=`, `::`, `<-`, `++`, `--`) at 12/14/16 px.
- **Carry-over exceptions to record explicitly:** `validate-font` baseline profile (inherited ligature + `ChangeWeight` artifacts), residual self-intersections deferred to visual QA, Nerd Font patching caveat (Medium Spec §13 `not executed`), and the AC-007 external PR-review trail.
- **Spec strategy:** create a separate spec file (`spec-design-semibold-weight.md`) per the established modular-escalation pattern, rather than appending to the approved Medium spec.
- **Commit strategy:** commit generated sources to a temporary feature branch with amend/squash safety until visual QA passes — do not repeat the Medium deviation of committing to `master` pre-QA.
- **Terminology:** `SemiBold` (weight 600). _Avoid_: semibold, semi bold, demi bold, DemiBold.
- **Out of scope:** proportional `FantasqueSans` generation, Light/ExtraBold weights, interpolation-based generation, and modifications to the CON-07 zero-touch set (`Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, `features.py`).
