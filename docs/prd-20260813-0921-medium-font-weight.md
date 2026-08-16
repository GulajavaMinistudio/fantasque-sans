<!-- markdownlint-disable -->
# PRD: Fantasque Sans Mono — Medium Font Weight Variant

## 1. Product overview

### 1.1 Document title and version

- PRD: Fantasque Sans Mono — Medium Font Weight Variant
- Version: 1.3
- Revision: 1.2 — Remediated per Clarification Report (Review Iteration 2, 2026-08-13): resolved PRD findings T-1 (FR-04, GH-007 AC3) and T-3 (§8.1).
- Revision: 1.3 — Remediated per Code Review remediation plan (`plan/plan-refactor-medium-weight-v1.0.md`, 2026-08-16): recorded the maintainer-accepted deviations as `accepted-deviation` markers — residual self-intersections deferred to visual QA (GH-001 AC3, Spec §12) and the `validate-font` `Error in` baseline profile accepted (FR-08, §7.3, GH-003 AC3, Spec §13).

### 1.2 Product summary

Fantasque Sans Mono currently ships with four weight/style variants: Regular (400), Bold (700), Italic (400i), and Bold Italic (700i). Community users have requested an intermediate weight option that sits between Regular and Bold, providing subtler emphasis without the visual heaviness of full Bold. This feature addresses that gap by introducing a **Medium** weight (CSS weight 500) and its **Medium Italic** companion (500i).

The Medium weight will be generated algorithmically from the existing Regular source using FontForge's `ChangeWeight` API, producing canonical `.sfdir` source directories that are committed to the repository. Once committed, the existing Makefile wildcard discovery, build scripts, CI/CD pipeline, and packaging workflows will automatically compile, validate, and distribute the new variants — requiring zero modifications to the core build infrastructure.

The primary value proposition is giving developers a richer typographic palette for their coding environments. Medium weight enables more nuanced visual hierarchy in editors and terminals (e.g., distinguishing keywords, comments, and identifiers) without resorting to the stark contrast of Bold.

## 2. Goals

### 2.1 Business goals

- **Address community demand** for an intermediate font weight, increasing user satisfaction and download adoption.
- **Improve competitive positioning** against other monospace fonts (JetBrains Mono, Fira Code, Cascadia Code) that already offer Medium/Semi-Bold weights.
- **Expand the font family** with minimal engineering effort by leveraging algorithmic weight generation and the project's zero-touch Makefile architecture.

### 2.2 User goals

- **Subtler emphasis in code editors:** Developers want to visually differentiate syntax elements (keywords, type annotations, function names) with a weight that is heavier than Regular but lighter than Bold.
- **Improved readability on high-DPI displays:** Medium weight provides better stroke visibility on high-resolution screens where Regular weight can appear too thin.
- **Terminal and UI theming flexibility:** Users want a Medium weight option for terminal emulators, VS Code themes, and IDE configurations that support per-token font weight customization.

### 2.3 Non-goals (Out of Scope)

- **Runtime font-weight slider in the Custom Build workflow:** The Medium weight is a pre-generated, committed source — not a user-configurable build parameter. No changes to `config.schema.json` or `configure.py` are in scope.
- **Manual hand-tuning of all glyphs:** MVP does not require pixel-perfect manual adjustment of every glyph. Algorithmic generation with automated validation is sufficient for core ASCII glyphs.
- **Adding additional weights (Light, Thin, Semi-Bold, Extra-Bold, Black):** Only Medium (500) is in scope. Other weights may be explored in future iterations.
- **Proportional (non-monospace) Medium variant:** Only the monospace family (`FantasqueSansMono`) receives the Medium weight. The proportional `FantasqueSans` family is excluded.
- **Changes to existing Regular, Bold, Italic, or BoldItalic sources:** The generation script reads from Regular/Italic sources but must never modify them.

## 3. User personas

### 3.1 Key user types

- Software developers using Fantasque Sans Mono in their IDE, code editor, or terminal emulator.
- Font contributors and maintainers who build from source and submit improvements.

### 3.2 Basic persona details

- **Dev Devina (Primary):** A professional software developer who uses Fantasque Sans Mono daily in VS Code / Neovim / JetBrains IDEs. She values readability, aesthetic coding environments, and uses font weight differentiation for syntax highlighting. She installs fonts from GitHub Releases or system package managers.
- **Contributor Carlos (Secondary):** An open-source contributor familiar with FontForge. He clones the repository, builds fonts locally with `make`, and may visually inspect or manually refine generated glyphs before submitting pull requests.

### 3.3 Role-based access

- **End User (Dev Devina):** Downloads pre-built font binaries (TTF, OTF, WOFF, WOFF2) from GitHub Releases or Custom Build artifacts. No repository access required.
- **Contributor (Contributor Carlos):** Full repository access. Runs build scripts locally, inspects `.sfdir` sources in FontForge, and submits PRs.
- **Maintainer:** Reviews PRs, approves generated sources after visual inspection, triggers CI builds, and publishes releases.

## 4. Functional requirements

- **FR-01: Medium Source Generation Script** (Priority: P0 — Critical)
  - A one-off Python script (`Scripts/generate-medium-source.py`) SHALL accept a Regular `.sfdir` source path and produce a Medium `.sfdir` output.
  - The script SHALL apply an incremental embolden transformation using FontForge's `ChangeWeight` API to produce a visually distinct weight between Regular and Bold. (A stroke expansion of +30 to +40 em-units is a suggested starting point for the Technical Specification phase.)
  - The script SHALL enforce uniform advance width of exactly 1060 em units across all generated glyphs to maintain strict monospace grid alignment.
  - The script SHALL execute `removeOverlap()` and `simplify()` on all generated glyphs to clean up self-intersecting splines.
  - The script SHALL set the OS/2 weight class to `500` (Medium) in the generated font metadata.
  - The script SHALL be functionally idempotent — running it multiple times with the same input produces identical contour geometry and metrics. Differences in non-functional metadata (e.g., timestamps) are permitted.

- **FR-02: Medium Italic Source Generation** (Priority: P0 — Critical)
  - The same script (or a clearly documented invocation) SHALL accept `FantasqueSansMono-Italic.sfdir` as input and produce `FantasqueSansMono-MediumItalic.sfdir`.
  - The Medium Italic variant SHALL preserve the italic angle and other style-specific metrics from the source Italic while applying the same embolden transformation parameters as Medium Upright.

- **FR-03: Committed Canonical Sources** (Priority: P0 — Critical)
  - The generated `Sources/FantasqueSansMono-Medium.sfdir` and `Sources/FantasqueSansMono-MediumItalic.sfdir` directories SHALL be committed to the Git repository as canonical source files.
  - After commit, the generation script is retained for reproducibility but is not part of the standard build pipeline.

- **FR-04: Automatic Build Pipeline Integration** (Priority: P0 — Critical)
  - The existing `Makefile` wildcard (`SOURCES=$(wildcard Sources/FantasqueSansMono*.sfdir)`) SHALL automatically discover and compile the new Medium sources without any Makefile modifications.
  - `Scripts/generate-font-variants` SHALL process Medium sources identically to Regular/Bold/Italic — producing TTF, OTF, SVG output files in `Variants/Normal/TTF/`, `Variants/Normal/OTF/`, etc.
  - All four variant permutations produced by the build — `Normal`, `LargeLineHeight`, `NoLoopK`, and `LargeLineHeight-NoLoopK` (all combinations of the two active build options) — SHALL apply to Medium and Medium Italic identically to other weights.

- **FR-05: CSS Font-Face Declaration** (Priority: P1 — High)
  - `Scripts/generate-css-decl` SHALL dynamically read the OS/2 weight (500) from the Medium font and generate correct `@font-face` rules with `font-weight: 500`.

- **FR-06: Packaging and Distribution** (Priority: P1 — High)
  - `Scripts/zip-all-variants` SHALL include Medium and Medium Italic font files in the generated ZIP/TAR.GZ release archives.
  - GitHub Actions `custom-build.yml` SHALL automatically compile and package Medium variants when triggered, with no workflow file changes required.

- **FR-07: Font Metadata Correctness** (Priority: P1 — High)
  - The SFNT name table entries for Medium SHALL be correctly set: Family Name = "Fantasque Sans Mono", SubFamily = "Medium", Full Name = "Fantasque Sans Mono Medium", PostScript Name = "FantasqueSansMono-Medium".
  - For Medium Italic: SubFamily = "Medium Italic", Full Name = "Fantasque Sans Mono Medium Italic", PostScript Name = "FantasqueSansMono-MediumItalic".

- **FR-08: Validation Script Compatibility** (Priority: P1 — High)
  - `Scripts/validate-font` SHALL pass without errors on the generated Medium and Medium Italic sources.

- **FR-09: Nerd Fonts Patching Compatibility** (Priority: P2 — Medium)
  - When the `NerdFontPatching` build option is enabled, the Nerd Fonts patcher SHALL successfully patch Medium and Medium Italic variants, producing "Fantasque Sans Mono Nerd Font Medium" and "Fantasque Sans Mono Nerd Font Medium Italic".

## 5. User experience

### 5.1 Entry points & first-time user flow

- **New users:** Discover Medium weight in the GitHub Release page, where it appears alongside Regular, Bold, Italic, and BoldItalic in the downloadable font archive. Installation is identical to other weights.
- **Existing users:** Upgrade by downloading the latest release. The Medium weight is an additive inclusion — existing Regular, Bold, and Italic fonts are unchanged.
- **Custom Build users:** Trigger a new Custom Build via GitHub Actions. The Medium weight is automatically included in the output without any configuration changes.

### 5.2 Core experience

- **Download and Install:** User downloads the release archive, extracts it, and installs all font files (including the new Medium variants) using their OS font manager.
- **Configure Editor/Terminal:** User sets `font-weight: 500` or selects "Fantasque Sans Mono Medium" from the font family dropdown in their IDE settings, terminal configuration, or CSS stylesheet.
- **Visual Verification:** User sees text rendered in Medium weight — noticeably heavier than Regular but distinctly lighter than Bold. Glyphs maintain clean inner counters and consistent monospace alignment.

### 5.3 UI/UX highlights & Edge cases

- **Counter Space Legibility:** Dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`) must maintain legible inner counter spaces after emboldening. If algorithmic generation produces clogged counters, those specific glyphs require post-generation manual correction by contributors.
- **Monospace Grid Integrity:** All Medium glyphs must maintain exactly 1060 em-unit advance width. Any glyph deviating from this breaks monospace alignment in code editors.
- **Font Manager Recognition:** Some font managers and operating systems group font weights by family. The Medium variant must have correct OS/2 and naming metadata to be grouped correctly under the "Fantasque Sans Mono" family alongside existing weights.
- **Fallback Behavior:** Applications that do not support weight 500 may fall back to Regular (400) or Bold (700). This is expected OS/application behavior and is not a defect.

## 6. Narrative

Devina opens her VS Code workspace on a Monday morning. She has recently switched to Fantasque Sans Mono for its playful, handwriting-like aesthetic. She loves it, but finds Regular too thin for keywords and Bold too heavy — it shouts at her from the screen. She checks the latest Fantasque Sans Mono release and discovers a new Medium weight. She downloads it, installs the font, and updates her VS Code settings to use `"editor.fontWeight": "500"` for keyword tokens. The result is subtle, elegant emphasis that makes her code more scannable without visual fatigue. Her terminal prompt, configured with Medium weight for the hostname, now stands out just enough. It is the Goldilocks weight she has been waiting for.

## 7. Success metrics

### 7.1 User-centric metrics

- **Adoption Rate:** ≥ 10% of font downloads include the Medium weight within 3 months of the first release containing it.
- **Community Feedback:** Positive reception in GitHub Issues/Discussions — no more than 2 valid glyph quality issues reported within 30 days of release.
- **Editor Compatibility:** Medium weight renders correctly and is selectable by name in the top 5 code editors (VS Code, JetBrains IDEs, Sublime Text, Neovim with GUI, Terminal.app / Windows Terminal).

### 7.2 Business metrics

- **Release Bundle Completeness:** 100% of release archives include Medium and Medium Italic variants.
- **GitHub Stars Growth:** Monitor if the feature announcement correlates with a measurable increase in repository stars (qualitative indicator).

### 7.3 Technical metrics

- **Build Pipeline Zero-Touch:** The Medium weight compiles successfully in CI without any modifications to `Makefile`, `config.schema.json`, `configure.py`, `custom-build.yml`, or `custom_build_driver.py`.
- **Monospace Grid Compliance:** 100% of generated Medium glyphs have exactly 1060 em-unit advance width (automated test).
- **Validation Pass Rate:** `Scripts/validate-font` passes with zero errors on both Medium and Medium Italic sources.
- **Test Suite Green:** All existing unit tests (`pytest tests/`) pass with zero regressions after the Medium sources are added.

## 8. Technical considerations (Input for Engineering Team)

### 8.1 Integration points

- **FontForge Python API (`fontforge` module):** Used for `ChangeWeight`, `removeOverlap`, `simplify`, and SFNT metadata manipulation.
- **Makefile wildcard discovery:** `SOURCES=$(wildcard Sources/FantasqueSansMono*.sfdir)` — automatic detection.
- **`Scripts/build.py` → `fontbuilder.py`:** Medium SFNT naming is written into the generated `.sfdir` sources by the generation script before commit (see §8.3), not derived from the source directory basename. Note: `Variation(name)` in `fontbuilder.py` appends a name to `familyname` and is not invoked by `build.py`; it must not be relied upon for Medium naming.
- **`Scripts/generate-css-decl`:** Reads `font.os2_weight` dynamically — must correctly map weight 500 to CSS `font-weight: 500`.
- **`Scripts/validate-font`:** Must accept Medium sources without structural validation errors.

### 8.2 Data storage & privacy

- No user data is collected, stored, or transmitted. Font files are static binary assets.
- Generated `.sfdir` source directories are committed to the public Git repository (MIT License).

### 8.3 Scalability & potential technical challenges

- **Incompatible Master Splines:** Regular and Bold sources have non-matching point/contour topology (e.g., lowercase `a`: 20 points in Regular vs 19 in Bold). This rules out `interpolateFonts()` and mandates `ChangeWeight` algorithmic emboldening.
- **Counter Space Clogging:** Algorithmic emboldening on dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`) risks shrinking inner counter spaces below legibility thresholds. Post-generation visual inspection of core ASCII glyphs is mandatory.
- **Advance Width Drift:** FontForge `ChangeWeight` may alter advance widths. The generation script must explicitly re-set all advance widths to 1060 em-units after emboldening.
- **SFNT Naming:** The generation script must ensure the SFNT metadata (`SubFamily = "Medium"`) is written correctly into the generated `.sfdir` sources before they are committed to the repository.

## 9. Milestones & sequencing

### 9.1 Project estimate & Team composition

- Small-Medium project: 3–5 days of focused work | Team: 1 developer (FontForge/Python), 1 reviewer (maintainer for visual QA)

### 9.2 Suggested phases

- **Phase 1 — Source Generation & Validation (2 days):** Create the `generate-medium-source.py` script. Generate `FantasqueSansMono-Medium.sfdir` and `FantasqueSansMono-MediumItalic.sfdir`. Run automated validation (advance width check, overlap removal, validate-font). Perform visual inspection of core ASCII glyphs in FontForge.
- **Phase 2 — Build Integration & Testing (1 day):** Commit generated sources. Verify `make` compiles all variants successfully. Run existing test suite. Verify CSS declarations and packaging scripts include Medium variants.
- **Phase 3 — CI/CD Verification & Release (1 day):** Trigger GitHub Actions custom build. Verify release archives contain Medium fonts. Verify Nerd Font patching (if applicable). Tag and publish release.

## 10. User stories & Acceptance Criteria

### 10.1. Generate Medium font source from Regular

- **ID**: GH-001
- **Story**: As a font maintainer, I want to run a Python script that generates Medium weight sources from the existing Regular source, so that I can produce a consistent Medium variant without manual glyph editing.
- **Acceptance criteria**:
  - [ ] Running `python Scripts/generate-medium-source.py Sources/FantasqueSansMono-Regular.sfdir Sources/FantasqueSansMono-Medium.sfdir` produces a valid `.sfdir` directory.
  - [ ] All generated glyphs have an advance width of exactly 1060 em units.
  - [ ] No self-intersecting splines exist in the output (all glyphs pass `removeOverlap` and `simplify`).
    - **Status: `accepted-deviation`** — residual self-intersections (252 upright / 465 italic) are a documented limitation of algorithmic `ChangeWeight`, deferred to visual QA (GH-006) and visually accepted by the maintainer. Reference: Spec §12. See Revision 1.3 note.
  - [ ] The output font's OS/2 weight class is set to 500.
  - [ ] The script is functionally idempotent — running it twice produces identical contour geometry and metrics.

### 10.2. Generate Medium Italic font source from Italic

- **ID**: GH-002
- **Story**: As a font maintainer, I want to generate a Medium Italic variant from the existing Italic source using the same script, so that the Medium family includes both upright and italic styles.
- **Acceptance criteria**:
  - [ ] Running `python Scripts/generate-medium-source.py Sources/FantasqueSansMono-Italic.sfdir Sources/FantasqueSansMono-MediumItalic.sfdir` produces a valid `.sfdir` directory.
  - [ ] The italic angle from the source Italic is preserved in the output.
  - [ ] All generated glyphs have an advance width of exactly 1060 em units.
  - [ ] The output font's OS/2 weight class is set to 500 and the italic flag is set.

### 10.3. Build Medium variants through standard Makefile

- **ID**: GH-003
- **Story**: As a font maintainer, I want `make` to automatically discover and compile Medium sources, so that no build infrastructure changes are needed.
- **Acceptance criteria**:
  - [ ] Running `make` with Medium `.sfdir` sources present in `Sources/` produces TTF, OTF, and web font (WOFF, WOFF2) output files for Medium and Medium Italic in the appropriate `Variants/` subdirectories.
  - [ ] No modifications to `Makefile`, `config.schema.json`, `configure.py`, or `custom_build_driver.py` are required.
  - [ ] `Scripts/validate-font` passes for both Medium and Medium Italic sources.
    - **Status: `accepted-deviation`** — the `Error in` baseline profile (inherited `Bad Glyph Name` on the ligature glyph + `ChangeWeight` artifacts) is accepted by maintainer exception; a zero-`Error in` run is unachievable for any source in this family. Reference: Spec §13. See Revision 1.3 note.
  - [ ] All existing font variants (Regular, Bold, Italic, BoldItalic) continue to build identically (zero regression).

### 10.4. Correct SFNT metadata for Medium weight

- **ID**: GH-004
- **Story**: As a developer (end user), I want the Medium font to be correctly identified by my OS and editor font picker, so that I can select "Fantasque Sans Mono Medium" from the font family dropdown.
- **Acceptance criteria**:
  - [ ] The Medium TTF/OTF file's SFNT name table contains: Family = "Fantasque Sans Mono", SubFamily = "Medium", Full Name = "Fantasque Sans Mono Medium".
  - [ ] The Medium Italic TTF/OTF file contains: SubFamily = "Medium Italic", Full Name = "Fantasque Sans Mono Medium Italic".
  - [ ] The font is grouped correctly under the "Fantasque Sans Mono" family in macOS Font Book, Windows Font Settings, and Linux `fc-list`.

### 10.5. CSS font-face declarations for Medium weight

- **ID**: GH-005
- **Story**: As a web developer, I want the web font package to include correct `@font-face` CSS declarations for Medium weight, so that I can use `font-weight: 500` in my stylesheets.
- **Acceptance criteria**:
  - [ ] The generated CSS file contains a `@font-face` rule for Medium with `font-weight: 500` and `font-style: normal`.
  - [ ] The generated CSS file contains a `@font-face` rule for Medium Italic with `font-weight: 500` and `font-style: italic`.
  - [ ] WOFF2 and WOFF files for Medium are referenced in the CSS `src` descriptor.

### 10.6. Visual quality validation of core ASCII glyphs

- **ID**: GH-006
- **Story**: As a developer, I want the Medium weight glyphs to be visually legible and free of rendering artifacts, so that my code is comfortable to read.
- **Acceptance criteria**:
  - [ ] All uppercase Latin letters (A–Z), lowercase Latin letters (a–z), and digits (0–9) are visually legible in the Medium weight at 12px, 14px, and 16px rendering sizes.
  - [ ] Common programming symbols (`->`, `=>`, `!=`, `//`, `/*`, `*/`, `||`, `&&`, `<=`, `>=`, `::`, `<-`, `++`, `--`) render without glyph collisions or clogged counters.
  - [ ] Dense glyphs (`e`, `a`, `s`, `@`, `%`, `&`, `8`, `#`) maintain discernible inner counter spaces.
  - [ ] Visual inspection is performed by at least one reviewer using FontForge waterfall preview or a rendered specimen page.
  - [ ] Visual quality sign-off is approved when at least one maintainer confirms acceptance via PR review comment or approval.

### 10.7. Release packaging includes Medium variants

- **ID**: GH-007
- **Story**: As an end user, I want the GitHub Release archive to include Medium and Medium Italic font files, so that I can install the complete font family from a single download.
- **Acceptance criteria**:
  - [ ] The ZIP release archive contains `FantasqueSansMono-Medium.ttf`, `FantasqueSansMono-Medium.otf`, `FantasqueSansMono-MediumItalic.ttf`, and `FantasqueSansMono-MediumItalic.otf`.
  - [ ] WOFF and WOFF2 variants for Medium and Medium Italic are included in the web font archive.
  - [ ] All four variant permutations (`Normal`, `LargeLineHeight`, `NoLoopK`, `LargeLineHeight-NoLoopK`) include the Medium weight in their respective output directories.

### 10.8. CI/CD pipeline builds Medium variants

- **ID**: GH-008
- **Story**: As a maintainer, I want the GitHub Actions pipeline to automatically build and package Medium variants when triggered, so that releases are fully automated.
- **Acceptance criteria**:
  - [ ] A `workflow_dispatch` trigger of `custom-build.yml` successfully compiles Medium and Medium Italic variants.
  - [ ] No modifications to `custom-build.yml` are required for Medium variant compilation.
  - [ ] The existing test suite (`pytest tests/`) passes with zero failures after Medium sources are added.
  - [ ] The release artifact uploaded by CI contains all Medium variant font files.
