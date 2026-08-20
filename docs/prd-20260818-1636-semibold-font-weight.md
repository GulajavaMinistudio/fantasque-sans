<!-- markdownlint-disable -->
# PRD: Fantasque Sans Mono — SemiBold Font Weight Variant

## 1. Product overview

### 1.1 Document title and version

- PRD: Fantasque Sans Mono — SemiBold Font Weight Variant
- Version: 1.1
- Date: 2026-08-20
- Status: DRAFT
- Upstream source: Approved Discovery Draft `docs/discovery-draft-20260818-1625-semibold-font-weight.md`
- Revision: v1.1 applies the clarification report `docs/audit/clarification-report-semibold-font-weight-2026-08-20.md`

### 1.2 Product summary

Fantasque Sans Mono currently ships six weight/style variants: Regular (400), Medium (500), Bold (700), and their Italic companions. This feature introduces a **SemiBold** weight (CSS weight 600) plus its **SemiBold Italic** companion, positioned visually between Medium and Bold. The result is a complete weight ladder (400 → 500 → 600 → 700), giving the family a consistent, graduated emphasis range.

Because hand-drawn `.sfdir` sources for the SemiBold weight are not available upstream, the feature reuses the proven **algorithmic weight generation** approach from the shipped Medium feature: a standalone one-shot script generates `Sources/FantasqueSansMono-SemiBold.sfdir` and `Sources/FantasqueSansMono-SemiBoldItalic.sfdir` once, and the results are committed as canonical source files.

Once committed, the existing Makefile wildcard discovery, build scripts, CI/CD pipeline, and packaging workflows compile, validate, and distribute the new variants automatically — zero modifications to core build infrastructure. The SemiBold weight is released additively as part of the next regular release bundle, exactly as Medium was.

## 2. Goals

### 2.1 Business goals

- **Complete the weight ladder:** Close the gap between Medium (500) and Bold (700) so the family offers a full 400–500–600–700 progression, fulfilling the roadmap commitment that began with the Medium weight.
- **Improve competitive positioning:** JetBrains Mono, Fira Code, and Cascadia Code already offer SemiBold; adding weight 600 removes a visible feature gap.
- **Minimize engineering effort:** Reuse the battle-tested Medium generation pattern (script, tests, verification workflow, naming conventions) instead of inventing a new pipeline.

### 2.2 User goals

- **A third emphasis tier in code editors:** Developers want to distinguish syntax elements with three graduated weights (e.g., Regular for body, Medium for keywords, SemiBold for function names and headings) without the visual heaviness of Bold.
- **Finer typographic hierarchy:** SemiBold provides an intermediate step for UI themes, terminal prompts, and documentation that need emphasis between Medium and Bold.
- **Consistent family behavior:** Users expect every weight of the family to behave identically (same monospace grid, same ligatures, same build variants).

### 2.3 Non-goals (Out of Scope)

- **Proportional `FantasqueSans` family:** Only the monospace family (`FantasqueSansMono`) receives the SemiBold weight.
- **Additional weights (Light, ExtraBold, Black):** Only SemiBold (600) is in scope.
- **Interpolation-based generation:** The unmerged `origin/feature/multi-weight-poc` branch (harmonized masters, interpolation, build-time generation) is NOT adopted — it is far heavier and incompatible with the zero-touch local `make` path.
- **Modifications to the zero-touch set (CON-07):** `Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, `features.py`, and `Scripts/generate-css-decl` must remain untouched. `Scripts/zip-all-variants` auto-discovers variants from the `Variants/` tree and also requires no changes.
- **Runtime font-weight parameter in Custom Build:** SemiBold is a pre-generated, committed source — not a user-configurable build option.
- **Modifications to the shipped Medium artifact:** `Scripts/generate-medium-source.py` and the committed Medium/MediumItalic sources must remain byte-identical (zero regression).
- **Mandatory manual glyph fixes:** Following the Medium precedent, residual algorithmic artifacts are accepted via maintainer exception and deferred to visual QA. Manual fixes are only performed if the maintainer explicitly requests them.

## 3. User personas

### 3.1 Key user types

- Software developers using Fantasque Sans Mono in their IDE, code editor, or terminal emulator.
- Font contributors and maintainers who build from source and submit improvements.

### 3.2 Basic persona details

- **Dev Devina (Primary):** A professional software developer who uses Fantasque Sans Mono daily in VS Code / Neovim / JetBrains IDEs. She already uses Medium (500) for keywords and wants an intermediate 600 weight for stronger emphasis elements (function names, headings, active UI items) without the heaviness of Bold (700).
- **Contributor Carlos (Secondary):** An open-source contributor familiar with FontForge. He clones the repository, builds fonts locally with `make`, and may visually inspect or manually refine generated glyphs before submitting pull requests.
- **Maintainer:** Reviews PRs, performs visual QA sign-off on generated sources, triggers CI builds, and publishes releases.

### 3.3 Role-based access

- **End User (Dev Devina):** Downloads pre-built font binaries (TTF, OTF, WOFF, WOFF2) from GitHub Releases or Custom Build artifacts. No repository access required.
- **Contributor (Contributor Carlos):** Full repository access. Runs build scripts locally, inspects `.sfdir` sources in FontForge, and submits PRs.
- **Maintainer:** Reviews PRs, approves generated sources after visual inspection, triggers CI builds, and publishes releases.

## 4. Functional requirements

- **FR-01: SemiBold Source Generation Script** (Priority: P0 — Critical)
  - A standalone one-shot Python script (`Scripts/generate-semibold-source.py`) SHALL accept the Regular `.sfdir` source path and produce the SemiBold `.sfdir` output.
  - The script SHALL be a standalone copy of the shipped Medium generator with SemiBold constants — the shipped Medium artifact must not be modified (zero regression).
  - The script SHALL apply a single-pass embolden transformation via FontForge `changeWeight(stroke, "LCG", 0, 0, "retain")`. The reference stroke SHALL be selected from the candidate grid (50/60/70 em-units) targeting the 55–70 em-unit band; the exact value SHALL be established empirically through specimen calibration during Phase 1 before sources are committed.
  - The script SHALL follow the calibration rule: choose the highest stroke within the 55–70 em-unit band that passes the GH-006 "discernible counters" test; if none pass, descend step-wise (50, then the 45 em-unit floor) until the test passes. 45 em-units is the hard floor — if the test does not pass at or above the floor, the single-pass approach is declared failed and escalated to a maintainer decision (re-scope / abandon / manual fix), never a silent ship of a Medium-clone result. Manual per-glyph fixes are not an automatic fallback; they occur only if the maintainer explicitly requests them.
  - The script SHALL enforce a uniform advance width of exactly 1060 em-units across all generated glyphs to maintain strict monospace grid alignment.
  - The script SHALL execute `removeOverlap()` and `simplify()` on all generated glyphs to clean up self-intersecting splines.
  - The script SHALL set the OS/2 weight class to `600` and the weight name to `SemiBold` in the generated font metadata.
  - The script SHALL be functionally idempotent — running it multiple times with the same input produces identical contour geometry and metrics.

- **FR-02: SemiBold Italic Source Generation** (Priority: P0 — Critical)
  - The same script SHALL accept `FantasqueSansMono-Italic.sfdir` as input and produce `FantasqueSansMono-SemiBoldItalic.sfdir`; the italic input is detected via the source basename, following the Medium precedent — no separate invocation is required.
  - The SemiBold Italic variant SHALL preserve the italic angle (-11.0) and the OS/2 italic flag from the source Italic while applying the same embolden parameters as SemiBold Upright.

- **FR-03: Canonical Sources & Commit Discipline** (Priority: P0 — Critical)
  - The generated `Sources/FantasqueSansMono-SemiBold.sfdir` and `Sources/FantasqueSansMono-SemiBoldItalic.sfdir` directories SHALL be committed to the Git repository as canonical source files.
  - Generated sources SHALL be committed to a temporary feature branch (not `master`), with amend/squash history rewriting permitted until visual QA passes.
  - Sources SHALL be merged to `master` only after the maintainer visual QA sign-off (GH-006).
  - After commit, the generation script is retained for reproducibility but is not part of the standard build pipeline.

- **FR-04: Automatic Build Pipeline Integration** (Priority: P0 — Critical)
  - The existing `Makefile` wildcard (`SOURCES=$(wildcard Sources/FantasqueSansMono*.sfdir)`) SHALL automatically discover and compile the new SemiBold sources without any Makefile modifications.
  - All four variant permutations produced by the build — `Normal`, `LargeLineHeight`, `NoLoopK`, and `LargeLineHeight-NoLoopK` — SHALL apply to SemiBold and SemiBold Italic identically to other weights.
  - SemiBold SHALL be compiled into TTF, OTF, WOFF, WOFF2, and SVG output files in the appropriate `Variants/` subdirectories.

- **FR-05: CSS Font-Face Declaration** (Priority: P1 — High)
  - `Scripts/generate-css-decl` SHALL dynamically read the OS/2 weight (600) from the SemiBold font and generate correct `@font-face` rules with `font-weight: 600`.

- **FR-06: Packaging and Distribution** (Priority: P1 — High)
  - `Scripts/zip-all-variants` SHALL include SemiBold and SemiBold Italic font files in the generated ZIP/TAR.GZ release archives.
  - GitHub Actions `custom-build.yml` SHALL automatically compile and package SemiBold variants when triggered, with no workflow file changes required.
  - SemiBold SHALL be released additively as part of the next regular release bundle — no standalone release is required.

- **FR-07: Font Metadata Correctness** (Priority: P1 — High)
  - The SFNT name table entries for SemiBold SHALL be: Family Name = "Fantasque Sans Mono", SubFamily = "SemiBold", Full Name = "Fantasque Sans Mono SemiBold", PostScript Name = "FantasqueSansMono-SemiBold".
  - For SemiBold Italic: SubFamily = "SemiBold Italic", Full Name = "Fantasque Sans Mono SemiBold Italic", PostScript Name = "FantasqueSansMono-SemiBoldItalic".

- **FR-08: Validation Script Compatibility** (Priority: P1 — High)
  - `Scripts/validate-font` SHALL pass on the generated SemiBold and SemiBold Italic sources under the recorded maintainer exception: the inherited `Bad Glyph Name` ligature warning plus `ChangeWeight` artifacts constitute the accepted baseline profile for any source in this family. A literal zero-warning run is explicitly out of scope.

- **FR-09: Nerd Fonts Patching Compatibility** (Priority: P2 — Medium)
  - When the `NerdFontPatching` build option is enabled, the Nerd Fonts patcher SHOULD successfully patch SemiBold and SemiBold Italic variants, producing "Fantasque Sans Mono Nerd Font SemiBold" and "Fantasque Sans Mono Nerd Font SemiBold Italic". Same scope and caveat as the Medium FR-09 (patcher dispatch validation is external).

## 5. User experience

### 5.1 Entry points & first-time user flow

- **New users:** Discover SemiBold in the GitHub Release page, where it appears alongside Regular, Medium, Bold, and their Italics in the downloadable font archive. Installation is identical to other weights.
- **Existing users:** Upgrade by downloading the latest release. The SemiBold weight is an additive inclusion — existing weights are unchanged.
- **Custom Build users:** Trigger a new Custom Build via GitHub Actions. The SemiBold weight is automatically included in the output without any configuration changes.

### 5.2 Core experience

- **Download and Install:** User downloads the release archive, extracts it, and installs all font files (including the new SemiBold variants) using their OS font manager.
- **Configure Editor/Terminal:** User sets `font-weight: 600` or selects "Fantasque Sans Mono SemiBold" from the font family dropdown in their IDE settings, terminal configuration, or CSS stylesheet.
- **Visual Verification:** User sees text rendered in SemiBold — distinctly heavier than Medium but clearly lighter than Bold. Glyphs maintain legible inner counters and consistent monospace alignment.

### 5.3 UI/UX highlights & Edge cases

- **Counter Space Legibility (top risk):** Dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`) must maintain legible inner counter spaces after emboldening. The SemiBold stroke is ~1.6×–2.1× the Medium stroke (34 em-units), so the clogging risk is significantly higher than Medium. Calibration fallback rule: choose the highest stroke within the 55–70 em-unit band that passes the GH-006 "discernible counters" test; if none pass, descend step-wise (50, then the 45 em-unit floor) until the test passes. If the test fails at or above the floor, escalate to a maintainer decision — manual per-glyph fixes are not an automatic fallback and are performed only if the maintainer explicitly requests them. Residual artifacts follow the Medium accepted-deviation precedent, deferred to visual QA (GH-006).
- **Monospace Grid Integrity:** All SemiBold glyphs must maintain exactly 1060 em-unit advance width. Any glyph deviating from this breaks monospace alignment in code editors.
- **Font Manager Recognition:** The SemiBold variant must have correct OS/2 (weight 600) and naming metadata to be grouped under the "Fantasque Sans Mono" family alongside the existing weights.
- **Fallback Behavior:** Applications that do not support weight 600 may fall back to Medium (500) or Bold (700). This is expected OS/application behavior and is not a defect.

## 6. Narrative

Devina has used Fantasque Sans Mono for months. She sets Regular (400) as her body font and Medium (500) for keywords. But when she tries to emphasize function names and section headings, Medium feels too timid and Bold (700) too shouty. With the new SemiBold release she sets 600 for those elements. Now her editor shows a smooth graduated hierarchy — Regular for comments, Medium for keywords, SemiBold for function names, Bold reserved for rare highlights. Her terminal prompt and status bars gain a crisp, confident weight that stays comfortable through a full workday. The family finally behaves like a complete, professional typeface.

## 7. Success metrics

### 7.1 User-centric metrics

- **Community Feedback:** No more than 2 valid glyph quality issues reported within 30 days of release. *Valid* = a glyph-quality defect confirmed by a maintainer, deduplicated per root cause, and excluding artifacts already recorded as `accepted-deviation`; the ≤ 2 target counts only issues valid under this definition.
- **Editor Compatibility:** SemiBold renders correctly and is selectable by name in the top 5 code editors (VS Code, JetBrains IDEs, Sublime Text, Neovim with GUI, Terminal.app / Windows Terminal). Measurement method: manual QA checklist (qualitative) — not a CI gate.

### 7.2 Business metrics

- **Weight Ladder Completeness:** 400/500/600/700 weights (plus Italics) are all present, correctly named, and selectable in a single family.
- **Release Bundle Completeness:** 100% of release archives include SemiBold and SemiBold Italic variants (sole quantitative adoption metric).
- **GitHub Stars Growth:** Monitor if the feature announcement correlates with a measurable increase in repository stars (qualitative indicator).

### 7.3 Technical metrics

- **Build Pipeline Zero-Touch:** The SemiBold weight compiles successfully in CI without any modifications to the CON-07 zero-touch set (`Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, `features.py`, `Scripts/generate-css-decl`).
- **Monospace Grid Compliance:** 100% of generated SemiBold glyphs have exactly 1060 em-unit advance width (automated test).
- **Validation Pass Rate:** `Scripts/validate-font` passes under the recorded maintainer baseline exception for both SemiBold and SemiBold Italic sources.
- **Test Suite Green:** All existing unit tests (`pytest tests/`, 83/83 baseline) pass with zero regressions, and the new SemiBold generation tests are added and green.
- **Zero Regression on Medium:** `git diff` on `Scripts/generate-medium-source.py` and the committed Medium sources is empty throughout the feature.

## 8. Technical considerations (Input for Engineering Team)

### 8.1 Integration points

- **FontForge Python API (`fontforge` module):** `changeWeight(stroke, "LCG", 0, 0, "retain")` for single-pass emboldening; `removeOverlap()` and `simplify()` for cleanup; SFNT metadata manipulation.
- **Makefile wildcard discovery:** `SOURCES=$(wildcard Sources/FantasqueSansMono*.sfdir)` — automatic detection of the new sources.
- **`Scripts/generate-css-decl`:** Reads `font.os2_weight` dynamically — must correctly map weight 600 to CSS `font-weight: 600`.
- **`Scripts/zip-all-variants`:** Includes SemiBold binaries in variant archives with no changes.
- **`custom_build_driver.py` `find_sfdirs()`:** Discovers the new `.sfdir` sources for Custom Build dispatch with no changes.
- **`.github/workflows/build-make.yml`:** Provides the standard-make CI evidence path for the SemiBold variants.
- **`Scripts/validate-font`:** Must accept SemiBold sources under the recorded maintainer baseline exception.

### 8.2 Data storage & privacy

- No user data is collected, stored, or transmitted. Font files are static binary assets.
- Generated `.sfdir` source directories are committed to the public Git repository (MIT License).

### 8.3 Scalability & potential technical challenges

- **Stroke Reference Unknown (primary assumption):** Medium used +34 em-units (range +30..+40). No calibrated reference exists for weight 600. The reference stroke MUST be established empirically via specimen renders at the candidate grid (50/60/70 em-units) targeting the 55–70 em-unit band, compared against the Medium and Bold neighbors, before sources are committed. 50 is the first step-down below the band; 45 em-units is the hard floor (see the FR-01 calibration rule).
- **Counter Space Clogging Scales with Stroke (top risk):** The Medium stroke already left residual self-intersections (252 upright / 465 italic, accepted via maintainer exception). A ~1.6×–2.1× stroke significantly raises the clogging risk on dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`). Calibration contract: choose the highest stroke in the 55–70 em-unit band that passes the GH-006 "discernible counters" test; descend step-wise (50, then the 45 em-unit floor) until it passes. Manual per-glyph fixes are not an automatic fallback — they occur only if the maintainer explicitly requests them; failing at or above the floor escalates to a maintainer decision (re-scope / abandon / manual fix).
- **Advance Width Drift:** FontForge `ChangeWeight` may alter advance widths. The generation script must explicitly re-set all advance widths to 1060 em-units after emboldening.
- **SFNT Naming Pitfalls (learned from Medium):** `os2_weight` must be assigned before `font.weight` (OS/2 WeightWidthSlopeOnly precedence); `font.weight` must be set explicitly to kill stale `Regular`/`Book` inheritance; `counter_type` must be the lowercase `"retain"` spelling. Watch for preferred-family records (ID 16/17) appearing as a side effect.
- **`validate-font` Baseline Profile:** A literal clean run is unachievable for any source in this family (inherited ligature `Bad Glyph Name` plus `ChangeWeight` artifacts). The maintainer exception precedent from Medium must be re-recorded, not re-litigated.

## 9. Milestones & sequencing

### 9.1 Project estimate & Team composition

- Small-Medium project: 3–5 days of focused work | Team: 1 developer (FontForge/Python), 1 maintainer (visual QA reviewer)

### 9.2 Suggested phases

- **Phase 1 — Stroke Calibration & Source Generation (2 days):** Render specimen pages at the candidate grid (50/60/70 em-units; target band 55–70, floor 45) and compare against Medium and Bold neighbors; select the reference stroke per the FR-01 calibration rule. Create `generate-semibold-source.py`. Generate `FantasqueSansMono-SemiBold.sfdir` and `FantasqueSansMono-SemiBoldItalic.sfdir`. Run automated validation (advance width check, overlap removal, `validate-font`). Perform visual inspection of core ASCII glyphs.
- **Phase 2 — Build Integration & Testing (1 day):** Commit generated sources to a temporary feature branch. Verify `make` compiles all four variant permutations. Add and run SemiBold generation tests (`pytest`, 83/83 baseline plus new tests). Verify CSS declarations and packaging scripts include SemiBold variants. Confirm zero regression on the Medium artifact and the CON-07 zero-touch set.
- **Phase 3 — CI Verification, Visual QA Sign-off & Merge (1 day):** Run the `build-make.yml` evidence workflow; trigger a Custom Build dispatch. Perform maintainer visual QA sign-off (GH-006) via PR review. Merge the feature branch to `master`. SemiBold is included in the next release bundle.

## 10. User stories & Acceptance Criteria

### 10.1. Generate SemiBold font source from Regular

- **ID**: GH-001
- **Story**: As a font maintainer, I want to run a Python script that generates SemiBold weight sources from the existing Regular source, so that I can produce a consistent SemiBold variant without manual glyph editing.
- **Acceptance criteria**:
  - [ ] Running `python Scripts/generate-semibold-source.py Sources/FantasqueSansMono-Regular.sfdir Sources/FantasqueSansMono-SemiBold.sfdir` produces a valid `.sfdir` directory.
  - [ ] All generated glyphs have an advance width of exactly 1060 em units.
  - [ ] No avoidable self-intersecting splines exist in the output (all glyphs pass `removeOverlap` and `simplify`).
    - **Status: `accepted-deviation`** — residual self-intersections are a documented limitation of algorithmic `ChangeWeight` (Medium precedent: 252 upright / 465 italic), deferred to visual QA (GH-006) and accepted via maintainer exception.
  - [ ] The output font's OS/2 weight class is set to 600 and the weight name is `SemiBold`.
  - [ ] The script is functionally idempotent — running it twice produces identical contour geometry and metrics.
  - [ ] `Scripts/generate-medium-source.py` and the committed Medium sources are unmodified (zero regression).

### 10.2. Generate SemiBold Italic font source from Italic

- **ID**: GH-002
- **Story**: As a font maintainer, I want to generate a SemiBold Italic variant from the existing Italic source using the same script, so that the SemiBold family includes both upright and italic styles.
- **Acceptance criteria**:
  - [ ] Running `python Scripts/generate-semibold-source.py Sources/FantasqueSansMono-Italic.sfdir Sources/FantasqueSansMono-SemiBoldItalic.sfdir` produces a valid `.sfdir` directory.
  - [ ] The italic angle (-11.0) from the source Italic is preserved in the output.
  - [ ] All generated glyphs have an advance width of exactly 1060 em units.
  - [ ] The output font's OS/2 weight class is set to 600 and the italic flag is set.

### 10.3. Build SemiBold variants through standard Makefile

- **ID**: GH-003
- **Story**: As a font maintainer, I want `make` to automatically discover and compile SemiBold sources, so that no build infrastructure changes are needed.
- **Acceptance criteria**:
  - [ ] Running `make` with SemiBold `.sfdir` sources present in `Sources/` produces TTF, OTF, WOFF, WOFF2, and SVG output files for SemiBold and SemiBold Italic in the appropriate `Variants/` subdirectories.
  - [ ] All four variant permutations (`Normal`, `LargeLineHeight`, `NoLoopK`, `LargeLineHeight-NoLoopK`) include SemiBold and SemiBold Italic.
  - [ ] No modifications to the CON-07 zero-touch set (`Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, `custom_build_driver.py`, `build.py`, `fontbuilder.py`, `features.py`, `Scripts/generate-css-decl`) are required.
  - [ ] `Scripts/validate-font` passes for both SemiBold and SemiBold Italic sources under the recorded maintainer baseline exception.
  - [ ] All existing font variants (Regular, Medium, Bold, and their Italics) continue to build identically (zero regression).

### 10.4. Correct SFNT metadata for SemiBold weight

- **ID**: GH-004
- **Story**: As a developer (end user), I want the SemiBold font to be correctly identified by my OS and editor font picker, so that I can select "Fantasque Sans Mono SemiBold" from the font family dropdown.
- **Acceptance criteria**:
  - [ ] The SemiBold TTF/OTF file's SFNT name table contains: Family = "Fantasque Sans Mono", SubFamily = "SemiBold", Full Name = "Fantasque Sans Mono SemiBold", PostScript Name = "FantasqueSansMono-SemiBold".
  - [ ] The SemiBold Italic TTF/OTF file contains: SubFamily = "SemiBold Italic", Full Name = "Fantasque Sans Mono SemiBold Italic", PostScript Name = "FantasqueSansMono-SemiBoldItalic".
  - [ ] The font is grouped correctly under the "Fantasque Sans Mono" family in macOS Font Book, Windows Font Settings, and Linux `fc-list`.

### 10.5. CSS font-face declarations for SemiBold weight

- **ID**: GH-005
- **Story**: As a web developer, I want the web font package to include correct `@font-face` CSS declarations for SemiBold weight, so that I can use `font-weight: 600` in my stylesheets.
- **Acceptance criteria**:
  - [ ] The generated CSS file contains a `@font-face` rule for SemiBold with `font-weight: 600` and `font-style: normal`.
  - [ ] The generated CSS file contains a `@font-face` rule for SemiBold Italic with `font-weight: 600` and `font-style: italic`.
  - [ ] WOFF2, WOFF, and SVG files for SemiBold are referenced in the CSS `src` descriptor.

### 10.6. Visual quality validation of core glyphs

- **ID**: GH-006
- **Story**: As a developer, I want the SemiBold weight glyphs to be visually legible and free of rendering artifacts, so that my code is comfortable to read.
- **Acceptance criteria**:
  - [ ] All uppercase Latin letters (A–Z), lowercase Latin letters (a–z), and digits (0–9) are visually legible in the SemiBold weight at 12px, 14px, and 16px rendering sizes.
  - [ ] Common programming symbol clusters (`->`, `=>`, `!=`, `//`, `/*`, `*/`, `||`, `&&`, `<=`, `>=`, `::`, `<-`, `++`, `--`) render without glyph collisions or clogged counters.
  - [ ] Dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`) maintain discernible inner counter spaces; this "discernible counters" check is the pass/fail gate of the FR-01 calibration rule (choose the highest stroke in the 55–70 em-unit band that passes; descend step-wise 50 → 45 floor; failing at or above the floor escalates to a maintainer decision). Residual self-intersections follow the `accepted-deviation` precedent (GH-001 AC3).
  - [ ] Specimen renders at the candidate grid (50/60/70 em-units) are visually compared against the Medium and Bold neighbors, and the reference stroke is selected per the FR-01 calibration rule, before sources are committed.
  - [ ] Visual quality sign-off is approved when at least one maintainer confirms acceptance via PR review comment or approval.

### 10.7. Release packaging includes SemiBold variants

- **ID**: GH-007
- **Story**: As an end user, I want the GitHub Release archive to include SemiBold and SemiBold Italic font files, so that I can install the complete font family from a single download.
- **Acceptance criteria**:
  - [ ] The ZIP release archive contains `FantasqueSansMono-SemiBold.ttf`, `FantasqueSansMono-SemiBold.otf`, `FantasqueSansMono-SemiBoldItalic.ttf`, and `FantasqueSansMono-SemiBoldItalic.otf`.
  - [ ] WOFF, WOFF2, and SVG variants for SemiBold and SemiBold Italic are included in the web font archive.
  - [ ] All four variant permutations (`Normal`, `LargeLineHeight`, `NoLoopK`, `LargeLineHeight-NoLoopK`) include the SemiBold weight in their respective output directories.

### 10.8. CI/CD pipeline builds SemiBold variants

- **ID**: GH-008
- **Story**: As a maintainer, I want the GitHub Actions pipeline to automatically build and package SemiBold variants when triggered, so that releases are fully automated.
- **Acceptance criteria**:
  - [ ] A `workflow_dispatch` trigger of `custom-build.yml` successfully compiles SemiBold and SemiBold Italic variants.
  - [ ] No modifications to `custom-build.yml` are required for SemiBold variant compilation.
  - [ ] The `build-make.yml` evidence workflow compiles the standard-make path with SemiBold sources present.
  - [ ] The existing test suite (`pytest tests/`) passes with zero failures, including the new SemiBold generation tests.
  - [ ] The release artifact uploaded by CI contains all SemiBold variant font files.
