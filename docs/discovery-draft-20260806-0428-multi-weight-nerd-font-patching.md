---
title: Project Discovery & Architecture Summary — Multi-Weight Nerd Font Patching
status: DRAFT (Phase 0)
date_analyzed: 2026-08-06
---
<!-- markdownlint-disable -->

> **Revision 3 (2026-08-06):** Placement decision recorded — **[PROPOSED TARGET ARCHITECTURE — NOT IMPLEMENTED]** the Nerd Font Patcher will run as a **dedicated Docker build stage between Stage 1 (`builder-fontforge`) and Stage 2 (`final`)**, executed inside the `docker build` step of `.github/workflows/custom-build.yml` (verified as the repository's only artifact-producing workflow; `test-multi-weight.yml` is a pytest-only smoke gate that produces no artifacts). The workflow file keeps its current step structure; the change lands in the `Dockerfile` (new stage + `COPY --from`) and `Scripts/packaging.sh` (flavor packaging and independent manifest).
>
> **Revision 2 (2026-08-06):** Session clarification — Nerd Fonts Patcher **adds** icon glyphs; it never replaces native glyphs. Added verified collision-surface audit (15 PUA codepoints) and corrected the Box Drawing assumption (full 160/160 coverage means the patcher skips that range by design).

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
- **Proposed Icon Augmentation:** Nerd Fonts Patcher v3.5.0, pinned to the official release tag and executed in a dedicated Docker build stage (`builder-nerd-patcher`) between Stage 1 and Stage 2, inside the `docker build` step of `custom-build.yml` — the repository's only artifact-producing workflow.
- **Testing:** `pytest`, FontForge-dependent tests in the Stage 1 container, and visual review using the specimen generator and Visual Quality Rubric.

## 3. Current Architecture Assessment

The repository has a clear pipeline boundary between FontForge source authoring, multi-weight preparation, legacy variant expansion, and Stage 2 packaging. The proposed fallback and Nerd Font flavor can fit this architecture only if they remain explicit stages with separate outputs.

### Strengths

- `Sources/Harmonized/` separates generated harmonized masters from protected legacy `.sfdir` sources. This preserves the CON-001 boundary and makes fallback preparation auditable.
- `Scripts/validate_harmonization.py` and `Scripts/validate_interpolation.py` provide structured reports and fail-fast behavior for critical contour failures before packaging.
- `Scripts/multi_weight_driver.py` keeps FontForge interpolation as a single authoritative interpolation interface. This avoids divergent per-glyph blending semantics and supports deterministic factor contracts for Medium and SemiBold.
- The Docker stages already separate FontForge compilation from hinting, webfont conversion, manifest generation, and archive packaging. A FontForge-dependent Patcher stage can run before Stage 2 without adding FontForge to the final packaging image. Because the Patcher stage executes inside `docker build`, `custom-build.yml` keeps its current step structure — only the Dockerfile gains a stage.
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
9. **Visual review burden:** Overwrite-on-collision is acceptable only for the separate Nerd Font flavor. It still requires collision reports and visual checks so that valid Fantasque Box Drawing, PUA, and other existing glyphs are not changed unknowingly. *(2026-08-06: Box Drawing has full 160/160 coverage and is skipped by the patcher by design; the actual overwrite surface is the 15 PUA codepoints listed in the audit below.)*

From a Clean Architecture perspective, the safest design is to keep native-glyph fallback in the interpolation preparation boundary and keep icon augmentation in a separate artifact-producing boundary. Combining both responsibilities inside the existing interpolation driver would make failure diagnosis and quality ownership less clear.

### Verified Clarification: Add, Not Replace (2026-08-06 Review)

A session review resolved a scope question: the Nerd Fonts Patcher **merges icon glyphs into the font** — it never replaces native glyphs. The patcher copies the input font and inserts icon glyphs from bundled icon sets (Pomicons, Powerline Symbols, Seti-UI, Devicons, Font Awesome, Material Design Icons) at Private Use Area codepoints. Native Latin, Greek, Cyrillic, digit, and punctuation glyphs remain untouched. The only overwrite surface is codepoint collision. The `--careful` flag ("Do not overwrite existing glyphs if detected") preserves original glyphs on collision; the default policy overwrites them.

#### Collision Surface Audit (Verified Against Master Sources)

Audit of `Sources/FantasqueSansMono-Regular.sfdir/` codepoints against the Nerd Fonts v3.5.0 icon codepoint inventory:

| Fantasque PUA area | Content | Nerd Fonts icon range | Collision |
| --- | --- | --- | --- |
| U+E000–E007 | Stylistic alternates (`quotedbl.old`, `k.noloop`, etc.) | Pomicons U+E000–E00A | ⚠️ Overwritten by default |
| U+E0A0–E0A2, U+E0B0–E0B3 | Native Powerline symbols | Powerline Symbols U+E0A0–E0A2, U+E0B0–E0B3 | ⚠️ Overwritten by default |
| U+E035–E03F, U+E100–E12C | Ligatures (`::`, `=>`, `!=`, etc.) | No icon set in this range | ✅ Safe |
| U+2500–259F | Box Drawing (160/160 coverage) | Patcher skips Box Drawing when the font already has full coverage | ✅ Safe |

**Implications:**

1. The effective overwrite surface is exactly **15 codepoints** (U+E000–E007, U+E0A0–E0A2, U+E0B0–E0B3), all in the PUA — no native letter is ever touched. The overwrite affects Fantasque stylistic alternates and native Powerline symbols **in the Nerd Font flavor only**; the base flavor is unaffected.
2. The ligature ranges (U+E035–E03F, U+E100–E12C) overlap no Nerd Fonts icon set and remain intact after patching.
3. Box Drawing (risk #9) is mitigated by design: Fantasque covers the full U+2500–259F range, so the patcher skips that block entirely. The collision report must still be generated to verify no drift against future icon-set additions.

### Placement Decision (Resolved 2026-08-06)

> **[PROPOSED TARGET ARCHITECTURE — NOT IMPLEMENTED]** The verified `Dockerfile` currently has only two stages (`builder-fontforge` and `final`); the `builder-nerd-patcher` stage described below does not exist yet and is the agreed target design.

- **Decision:** In the target architecture, the Patcher runs in a dedicated Docker build stage (`builder-nerd-patcher`) between Stage 1 and Stage 2, inside the `docker build` step of `custom-build.yml`. Its outputs are copied into Stage 2 via `COPY --from=builder-nerd-patcher` before `Scripts/packaging.sh` runs.
- **Rationale (verified against `Dockerfile`):** Stage 2 (`final`) ships no FontForge runtime — only `ttfautohint`, `woff-tools`, `woff2`, `python3.14`, `zip`, `tar`, and `jq`. The Patcher requires FontForge, so the stage derives from Stage 1 (`FROM builder-fontforge`) and inherits the verified FontForge toolchain without bloating the final packaging image.
- **Workflow impact (verified against `.github/workflows/`):** `custom-build.yml` (job `build`, steps 6–7) is the only workflow that produces font artifacts — `docker build` compiles the font and `docker run` runs Stage 2 packaging, after which artifacts are uploaded and a release is created. Both steps keep their current command form. `test-multi-weight.yml` runs only `pytest tests/ -v` on `feature/multi-weight-*` pushes and is unaffected.
- **Rejected alternative:** a host-runner patching step between `docker build` and `docker run` would split build logic out of the container, violating ADR-0002 (all build steps inside Docker) and requiring FontForge on the runner.
- **Remaining open decision:** how the flavor is activated (new `workflow_dispatch` input vs. always-on output) stays with the PRD; today's five boolean inputs have no Nerd Font toggle.

## ⚙️ Operational Workflow

### 1. Workflow A: Native Multi-Weight Base Font

1. The build reads the protected Regular, Bold, Italic, and BoldItalic sources and runs the existing incompatibility detection and master validation reports.
2. The 427 unresolved native glyphs remain visible in `tracking.json`, but the proposed policy classifies them as `fallback_regular` instead of treating them as silently approved.
3. A temporary interpolation input is prepared without modifying the protected masters. For each fallback glyph used by the Regular-to-Bold interpolation, the corresponding Bold-side outline is made identical to the Regular outline so the output glyph remains renderable and deterministic.
4. `font.interpolateFonts()` generates Medium and SemiBold from the temporary interpolation input. Compatible glyphs continue to use the normal Regular-to-Bold interpolation factors; fallback glyphs resolve to the Regular outline by construction.
5. The validation report distinguishes structural interpolation passes from fallback glyphs and records the fallback count, glyph names, source master, and reason. The Visual Quality Rubric must explicitly classify the weight inconsistency as an accepted limitation or a release blocker.
6. The existing variant expansion and Stage 2 packaging produce the base font artifacts. These artifacts remain free of Nerd Font icon augmentation and preserve the current rollback path.

### 2. Workflow B: Separate Nerd Font Flavor (Proposed — Not Implemented)

1. A dedicated Docker build stage (`builder-nerd-patcher`), derived from Stage 1 so it inherits the FontForge runtime, consumes the generated base TTF and OTF files for every released monospace weight: Regular, Bold, Italic, BoldItalic, Medium, SemiBold, and any stretch weight that passes its release gate. The stage runs inside the `docker build` step of `custom-build.yml`; no new Actions step or workflow is added.
2. The build invokes the official Nerd Fonts Patcher v3.5.0 from a pinned, checksum-verified distribution. The `--complete` policy enables the full available icon set, and the selected collision policy permits existing glyphs to be overwritten in the Nerd Font flavor only.
3. The Patcher writes to a separate output namespace with distinct family/full names and file names, inside the stage's own output directory. It never writes over the base TTF, OTF, `.sfdir`, or existing webfont output; Stage 2 consumes the patched files via `COPY --from=builder-nerd-patcher`.
4. Stage 2 runs the normal hinting and conversion steps over the patched TTF files in the existing `docker run` packaging step, regenerates OTF/webfont outputs according to the chosen source-of-truth policy, and computes independent manifest checksums.
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
8. **Pipeline placement:** In the target architecture, the Patcher stage executes inside the existing `docker build` step of `custom-build.yml` as a dedicated Docker stage between Stage 1 and Stage 2. No new workflow, job, or Actions step is required, and `test-multi-weight.yml` (a pytest-only smoke gate) is unaffected.

### Decisions Required Before the Technical Specification

*(Resolved 2026-08-06: Patcher placement — dedicated Docker build stage between Stage 1 and Stage 2, inside `docker build` in `custom-build.yml`, the repository's only artifact-producing workflow. See "Placement Decision".)*

- The exact fallback preparation mechanism and the boundary between `compatible`, `fallback_regular`, and `needs_harmonization` statuses.
- The visual acceptance threshold for fallback glyphs and whether the base flavor may ship while the manual harmonization backlog remains open.
- The exact Nerd Font naming convention and archive layout for each monospace weight.
- The authoritative source for patched OTF and webfont files, plus the required post-patch metric and checksum gates.
- The complete license/attribution manifest for every icon set enabled by the `--complete` policy.
- The collision report format and the visual review owner for the separate Nerd Font flavor.

### Scope Clarification Recorded (2026-08-06)

The exploration session confirmed the product intent for the Nerd Font flavor: **icon augmentation is additive** — the patched flavor keeps all native Fantasque glyphs and adds the complete v3.5.0 icon set on every monospace weight. The PRD must not describe the patcher as "replacing" glyphs. The only overwrite surface is the verified 15 PUA codepoints (stylistic alternates and native Powerline symbols); the collision-policy requirement in Handoff Note #4 can reference this exact list and require the patcher's collision report to confirm no drift.

This document is a Phase 0 discovery draft, not a PRD, technical specification, implementation plan, or code change. After the draft is reviewed and approved, start a new session with `/sdlc-draft-prd` and attach this file as the upstream discovery artifact.