---
title: Project Discovery & Architecture Summary — Multi-Weight Nerd Font Patching
status: DRAFT (Phase 0)
date_analyzed: 2026-08-06
---
<!-- markdownlint-disable -->

# Project Discovery Summary: Multi-Weight Nerd Font Patching

## 1. Project Overview

Fantasque Sans Mono is a handcrafted programming font repository whose build system now includes a Multi-Weight Variants pipeline. The pipeline harmonizes FontForge masters, generates Medium and SemiBold static weights through FontForge interpolation, validates the results, and packages multiple font formats through the existing Custom Build Workflow.

The current harmonization work has reached a shape-preserving ceiling. The tracking file contains 427 native glyphs that remain incompatible between masters: 374 have contour or topology mismatches, and 53 cannot be equalized by the available exact operations. These glyphs include native Latin, Greek, Cyrillic, and punctuation glyphs rather than Nerd Font icons. The current plan assigns them to type-designer review.

This discovery explores a proposed scope change: temporarily use the Regular outline as a fallback for those native glyphs, then create separate Nerd Font artifacts by running the pinned Nerd Fonts Patcher v3.5.0 after the base fonts are generated. The proposal does not claim that Nerd Fonts Patcher repairs master incompatibility; it separates native-glyph fallback from post-build icon augmentation.

## 2. Technology Stack & Infrastructure

The repository architecture is pipeline-based. Existing architecture information is documented in `docs/ARCHITECTURE.md`, but that map predates the current harmonization and multi-weight changes and requires an update before the next specification phase.

- **Core Font Authoring:** FontForge `.sfdir` sources with one `.glyph` file per glyph.
- **Build and Interpolation:** FontForge Python 3 bindings, `font.interpolateFonts()`, and legacy build scripts protected by CON-001.
- **Harmonization and Validation:** `Scripts/detect_incompatibility.py`, `Scripts/validate_harmonization.py`, `Scripts/validate_interpolation.py`, and the session tooling under `build/poc/`.
- **Build Orchestration:** Docker multi-stage build and GitHub Actions `workflow_dispatch` through `.github/workflows/custom-build.yml`.
- **Post-Processing:** `ttfautohint`, `sfnt2woff`, `woff2_compress`, checksum/manifest generation, and archive packaging in `Scripts/packaging.sh`.
- **Proposed Icon Augmentation:** Nerd Fonts Patcher v3.5.0, pinned to the official release tag and executed in a FontForge-capable stage.
- **Testing:** `pytest`, FontForge-dependent tests in the Stage 1 container, and visual review using the specimen generator and Visual Quality Rubric.

## 3. Current Architecture Assessment

The repository has a clear pipeline boundary between FontForge source authoring, multi-weight preparation, legacy variant expansion, and Stage 2 packaging. The proposed fallback and Nerd Font flavor can fit this architecture only if they remain explicit stages with separate outputs.

### Strengths

- `Sources/Harmonized/` separates generated harmonized masters from protected legacy `.sfdir` sources. This preserves the CON-001 boundary and makes fallback preparation auditable.
- `Scripts/validate_harmonization.py` and `Scripts/validate_interpolation.py` provide structured reports and fail-fast behavior for critical contour failures before packaging.
- `Scripts/multi_weight_driver.py` keeps FontForge interpolation as a single authoritative interpolation interface. This avoids divergent per-glyph blending semantics and supports deterministic factor contracts for Medium and SemiBold.
- The Docker stages already separate FontForge compilation from hinting, webfont conversion, manifest generation, and archive packaging. A FontForge-dependent Patcher stage can run before Stage 2 without adding FontForge to the final packaging image.
- Separate Nerd Font artifacts preserve the existing base font as a rollback and comparison point. This is the safest boundary for the user-selected overwrite policy.

### Tech Debt & Risks

1. **Architecture map drift:** `docs/ARCHITECTURE.md` was last updated before the current harmonization engine, `Sources/Harmonized/tracking.json`, and multi-weight build stages were added. Downstream SDLC agents may otherwise infer an obsolete architecture.
2. **Missing fallback boundary:** The current validation contract assumes incompatible glyphs are fatal, while the proposed product accepts `fallback_regular`. The repository has no status, report field, or gate semantics for this new outcome.
3. **Interpolation coupling:** `Scripts/multi_weight_driver.py` calls `font.interpolateFonts()` for the complete font and has no native fallback path for common glyphs with incompatible contours. Bypassing the validator alone cannot produce a valid interpolated font.
4. **Weight inconsistency:** A Regular outline copied into Medium or SemiBold remains visually Regular for that glyph. The result may be renderable but cannot be described as fully proportional across all glyphs without a separate visual-quality classification.
5. **Post-processing mutation:** Nerd Fonts Patcher copies, scales, rounds, renames, and may overwrite existing glyphs. It also normalizes vertical metrics and adjusts glyph widths. Running it in place on base outputs would violate the intended isolation of the base flavor.
6. **Format and metadata divergence:** Patching TTF/OTF outputs requires regenerating WOFF/WOFF2, updating checksums and manifests, and defining separate names and archives. Leaving existing webfont files untouched would create inconsistent artifacts.
7. **Reproducibility:** The Patcher source and icon data must be pinned to the v3.5.0 release and verified by checksum. Tracking a moving `master` branch would undermine the repository's deterministic-build contract.
8. **Licensing and attribution:** Nerd Fonts aggregates multiple icon sets. The proposed release flavor must carry the required upstream licenses and attribution alongside the existing Fantasque license rather than assuming `LICENSE.txt` is sufficient.
9. **Visual review burden:** Overwrite-on-collision is acceptable only for the separate Nerd Font flavor. It still requires collision reports and visual checks so that valid Fantasque Box Drawing, PUA, and other existing glyphs are not changed unknowingly.

From a Clean Architecture perspective, the safest design is to keep native-glyph fallback in the interpolation preparation boundary and keep icon augmentation in a separate artifact-producing boundary. Combining both responsibilities inside the existing interpolation driver would make failure diagnosis and quality ownership less clear.

## ⚙️ Operational Workflow

### 1. Workflow A: Native Multi-Weight Base Font

1. The build reads the protected Regular, Bold, Italic, and BoldItalic sources and runs the existing incompatibility detection and master validation reports.
2. The 427 unresolved native glyphs remain visible in `tracking.json`, but the proposed policy classifies them as `fallback_regular` instead of treating them as silently approved.
3. A temporary interpolation input is prepared without modifying the protected masters. For each fallback glyph used by the Regular-to-Bold interpolation, the corresponding Bold-side outline is made identical to the Regular outline so the output glyph remains renderable and deterministic.
4. `font.interpolateFonts()` generates Medium and SemiBold from the temporary interpolation input. Compatible glyphs continue to use the normal Regular-to-Bold interpolation factors; fallback glyphs resolve to the Regular outline by construction.
5. The validation report distinguishes structural interpolation passes from fallback glyphs and records the fallback count, glyph names, source master, and reason. The Visual Quality Rubric must explicitly classify the weight inconsistency as an accepted limitation or a release blocker.
6. The existing variant expansion and Stage 2 packaging produce the base font artifacts. These artifacts remain free of Nerd Font icon augmentation and preserve the current rollback path.

### 2. Workflow B: Separate Nerd Font Flavor

1. The FontForge-capable build stage consumes the generated base TTF and OTF files for every released monospace weight: Regular, Bold, Italic, BoldItalic, Medium, SemiBold, and any stretch weight that passes its release gate.
2. The build invokes the official Nerd Fonts Patcher v3.5.0 from a pinned, checksum-verified distribution. The `--complete` policy enables the full available icon set, and the selected collision policy permits existing glyphs to be overwritten in the Nerd Font flavor only.
3. The Patcher writes to a separate output namespace with distinct family/full names and file names. It never writes over the base TTF, OTF, `.sfdir`, or existing webfont output.
4. Stage 2 runs the normal hinting and conversion steps over the patched TTF files, regenerates OTF/webfont outputs according to the chosen source-of-truth policy, and computes independent manifest checksums.
5. The release package includes the Nerd Fonts icon-set licenses and attribution required by the bundled glyph data. The base package remains unchanged and carries only its existing contents.
6. A separate validation gate compares the patched flavor with its pre-patch inputs. The gate records codepoint collisions, changes to native glyphs, vertical metrics, advance widths, family naming, and output completeness before publication.

### 3. Current Failure Boundary

The current Dockerfile stops at strict master validation or native FontForge interpolation before any final font exists. Therefore, adding Workflow B alone cannot unblock the build. Workflow A must first introduce and document the fallback policy; only then can Workflow B run as a post-generation augmentation stage.

## 5. Handoff Notes for Product Manager (/sdlc-draft-prd)

The Product Manager must treat this proposal as a deliberate scope change to the approved Multi-Weight Variants initiative. The PRD should define the following user-visible behavior before any technical specification is written:

1. **Two product flavors:** The base Fantasque Sans Mono artifacts remain available and unchanged by Nerd Fonts Patcher. A separate Nerd Font flavor contains the complete v3.5.0 icon patch for every released monospace weight.
2. **Native fallback disclosure:** The 427 unresolved native glyphs are not repaired by Nerd Fonts Patcher. The proposed fallback copies the Regular outline into the affected new weights and must be disclosed as a known visual limitation. The PRD must define whether this limitation is acceptable for release and how it is surfaced to users.
3. **Weight coverage:** The Nerd Font flavor covers every monospace weight that passes the release gates, including core weights and approved stretch weights. The proportional variant is outside this proposal.
4. **Collision policy:** The Nerd Font flavor may overwrite existing glyphs at icon codepoints. The base flavor must never be overwritten. The PRD should require a collision report and visual review for the patched flavor.
5. **Artifact and format parity:** Base and Nerd Font flavors require independent TTF, OTF, WOFF, WOFF2, manifests, checksums, archive names, family names, and release notes. A patched TTF without regenerated webfont outputs is incomplete.
6. **Toolchain policy:** The Nerd Fonts Patcher is pinned to official release `v3.5.0`, not the moving `master` branch. The release process must retain the checksum and the upstream icon-set license/attribution files.
7. **Backward compatibility:** Existing builds with multi-weight disabled must retain the current base output behavior. Enabling the new flavor must not mutate or replace the base artifacts.

### Decisions Required Before the Technical Specification

- The exact fallback preparation mechanism and the boundary between `compatible`, `fallback_regular`, and `needs_harmonization` statuses.
- The visual acceptance threshold for fallback glyphs and whether the base flavor may ship while the manual harmonization backlog remains open.
- The exact Nerd Font naming convention and archive layout for each monospace weight.
- The authoritative source for patched OTF and webfont files, plus the required post-patch metric and checksum gates.
- The complete license/attribution manifest for every icon set enabled by the `--complete` policy.
- The collision report format and the visual review owner for the separate Nerd Font flavor.

This document is a Phase 0 discovery draft, not a PRD, technical specification, implementation plan, or code change. After the draft is reviewed and approved, start a new session with `/sdlc-draft-prd` and attach this file as the upstream discovery artifact.