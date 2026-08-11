<!-- markdownlint-disable MD024 -->

## PRD: Nerd Font Patcher Integration

## 1. Product overview

### 1.1 Document title and version

- PRD: Nerd Font Patcher Integration
- Version: 1.0
- Date: 2026-08-11
- Status: DRAFT
- Upstream: [discovery-draft-20260811-1200-nerd-font-patcher.md](discovery-draft-20260811-1200-nerd-font-patcher.md)

### 1.2 Product summary

Fantasque Sans Mono is a popular open-source programming font with a distinctive handwriting-like style. The repository's Custom Build feature currently allows Fork Owners to generate personalized font variants (with options like `LargeLineHeight`, `NoLoopK`, `NoCalt`, `UseHinted`) via a cloud-based GitHub Actions pipeline — requiring zero local toolchain setup.

This PRD defines the integration of the [Nerd Fonts Patcher](https://github.com/ryanoasis/nerd-fonts) as an **optional post-build patching step** within the existing Custom Build pipeline. When enabled, the patcher injects 10,000+ developer-focused icons (Powerline, Font Awesome, Material Design, Octicons, Codicons, Weather, and more) into the generated font files, producing a separate "Nerd Font" variant archive alongside the standard build output.

Fantasque Sans Mono is already listed in the [official Nerd Fonts patched fonts catalog](https://github.com/ryanoasis/nerd-fonts#patched-fonts) (v1.8.0). This feature brings the patching **in-house**, enabling every Custom Build to optionally produce a Nerd Font variant that incorporates the user's chosen build options — something the pre-patched official Nerd Fonts release cannot offer.

## 2. Goals

### 2.1 Business goals

- **Increase Custom Build adoption:** Offering Nerd Font patching as a one-click option makes the Custom Build pipeline more compelling, driving more users to fork and use the workflow.
- **Reduce support burden:** Users currently must manually download the Nerd Fonts patcher, run it locally against Fantasque Sans Mono, and deal with version mismatches and toolchain issues. An integrated option eliminates this friction entirely.
- **Differentiate from official Nerd Fonts catalog:** The official Nerd Fonts release of Fantasque Sans Mono uses vanilla build options. The in-house patcher allows users to combine Nerd Font glyphs with **any** Custom Build option combination (e.g., `NoLoopK` + `NerdFontPatching`).
- **Keep patcher version pinned and auditable:** By controlling the patcher version in CI, the project can ensure reproducible, auditable font output with a known patcher version recorded in the manifest.

### 2.2 User goals

- **One-click Nerd Font generation:** Fork Owners want to toggle a single checkbox in the GitHub Actions UI (or a single key in `config.json`) to produce Nerd Font variants — no local Docker, FontForge, or Python required.
- **Combined build options:** Users want Nerd Font patching applied *on top of* their personalized variant (e.g., large line height + no loop k + Nerd Fonts).
- **Predictable output:** Users expect the Nerd Font archive to be clearly separated from the base build, with consistent naming, and downloadable from the same GitHub Release page.
- **Transparency:** Users want to know exactly which patcher version was used, via the manifest metadata.

### 2.3 Non-goals (Out of Scope)

- **Icon set selection UI:** Users will NOT be able to choose individual icon sets (e.g., "only Powerline + DevIcons"). The patcher will use `--complete` to include all icons. Per-icon-set selection is deferred to a future release.
- **WOFF/WOFF2 Nerd Font output:** Web font formats are out of scope for the Nerd Font variant. The patched output will contain only TTF and OTF files, which are the primary formats for terminal and IDE usage.
- **Modification of legacy build scripts:** Per architectural constraint CON-001, `build.py`, `fontbuilder.py`, `features.py`, and `Makefile` MUST NOT be modified. The Nerd Font feature operates exclusively on the **output** of the existing pipeline.
- **Automatic patcher version updates:** The patcher Docker image tag will be manually pinned. Automatic update mechanisms (e.g., Dependabot for Docker images) are out of scope.
- **Custom font naming overrides:** The patcher's default naming convention (appending "Nerd Font" to the family name) will be used. User-configurable font naming is out of scope.
- **`--careful` mode toggle:** The patcher will NOT use the `--careful` flag. Existing glyphs at conflicting codepoints will be replaced by Nerd Font glyphs. This is the intended and expected behavior.
- **Artifact storage limit mitigation:** The increased size of the Nerd Font archives (~30-40MB vs ~2-3MB for the base build) is accepted as expected behavior. Mitigation of GitHub Actions artifact storage limits is out of scope for this PRD.

## 3. User personas

### 3.1 Key user types

- **Terminal Developer (primary):** A developer who uses Fantasque Sans Mono in their terminal emulator (Alacritty, kitty, WezTerm, Windows Terminal, iTerm2) and wants Powerline segments, file icons, and developer glyphs rendered inline.
- **IDE Power User:** A developer using VS Code, JetBrains IDEs, or Neovim with plugins that render Nerd Font icons (e.g., nvim-tree, lualine, telescope).
- **Fork Owner (Custom Build User):** A GitHub user who has forked the repository to run Custom Builds. They may or may not care about Nerd Fonts specifically, but want access to all available options.

### 3.2 Basic persona details

- **Dev Reza (Terminal Developer):** Uses Fantasque Sans Mono in kitty terminal with a Powerline-based prompt (Starship). Currently downloads the official Nerd Fonts patched version but wants the `NoLoopK` variant with Nerd Font glyphs — which the official release does not offer. Reza is comfortable with GitHub Actions but does not want to set up Docker or FontForge locally.

- **Dev Lina (IDE Power User):** Uses Fantasque Sans Mono in VS Code with the Material Icon Theme. Wants Nerd Font icons to render correctly in the integrated terminal and file explorer sidebar. Lina prefers the `LargeLineHeight` option for better readability on her high-DPI monitor.

- **Andi (Fork Owner):** Maintains a personal fork of Fantasque Sans Mono to generate builds for their team. Wants to offer Nerd Font variants alongside standard builds in the same release. Andi is technically proficient and reviews manifest metadata for audit purposes.

### 3.3 Role-based access

- **Fork Owner (workflow_dispatch trigger):** Has permission to trigger the Custom Build workflow, including the new `nerd_font_patching` toggle. This is the same permission model as existing build options — no new roles or permissions are required.
- **Downstream Consumer (release downloader):** Downloads the generated Nerd Font archive from the GitHub Release page. No GitHub account required for public forks.

## 4. Functional requirements

- **FR-001: NerdFontPatching Configuration Option** (Priority: P0 — Must Have)
  - Add a new `NerdFontPatching` boolean option (default: `false`) to the configuration layer.
  - The option MUST be available via:
    - `config.schema.json` as a validated property
    - `workflow_dispatch` input in the GitHub Actions UI
    - `config.json` file for programmatic builds
    - GitHub CLI (`gh workflow run`) via `--field nerd_font_patching` parameter
  - The option MUST follow the existing precedence hierarchy: `workflow_dispatch` form > `config.json` > `DEFAULTS`.
  - The resolved value MUST be written into `manifest.json` under `resolved_options`.

- **FR-002: Nerd Font Patching Execution** (Priority: P0 — Must Have)
  - When `NerdFontPatching = true`, the workflow MUST execute the Nerd Fonts Patcher against all generated font files after Stage 2 packaging completes.
  - The patcher MUST use the `nerdfonts/patcher` Docker image pinned to a specific version tag (initial: `v3.5.0`).
  - Patching flags MUST be:
    - `--complete`: Include all icon sets (10,000+ glyphs)
    - `--mono`: Applied ONLY to Mono variants (FantasqueSansMono-*)
    - `--adjust-line-height`: Applied to all variants
    - `--outputdir`: Directs output to a separate staging directory
    - `--careful` MUST NOT be used (existing glyphs at conflicting codepoints are replaced)
  - Both TTF and OTF formats MUST be patched for all variants:
    - Mono: Regular, Bold, Italic, BoldItalic (4 weights × 2 formats = 8 files)
    - Proportional: FantasqueSans (1 weight × 2 formats = 2 files)
    - Total: 10 patcher invocations

- **FR-003: Nerd Font Output Packaging** (Priority: P0 — Must Have)
  - Patched fonts MUST be packaged into separate archives:
    - `fantasque-sans-nerd-font.zip`
    - `fantasque-sans-nerd-font.tar.gz`
  - The Nerd Font archive MUST contain:
    - `TTF/` directory with all patched TTF files
    - `OTF/` directory with all patched OTF files
    - `manifest.json` (copy from base build, with NF metadata)
    - `LICENSE.txt` (copy from repository root)
    - `README.md` (copy from repository root)
  - The base build archives (`fantasque-sans-custom-build.zip/.tar.gz`) MUST remain unchanged regardless of the `NerdFontPatching` toggle.

- **FR-004: Manifest Metadata Extension** (Priority: P0 — Must Have)
  - When `NerdFontPatching = true`, the `manifest.json` MUST include an additional top-level key:
    - `nerd_font_version`: The version string of the `nerdfonts/patcher` Docker image used (e.g., `"3.5.0"`)
  - The `resolved_options.NerdFontPatching` field MUST reflect the resolved boolean value.

- **FR-005: Release Integration** (Priority: P0 — Must Have)
  - When `NerdFontPatching = true`, the GitHub Release MUST include the Nerd Font archives as additional release assets alongside the base build archives.
  - The release title MUST include a `NerdFont` label when patching is enabled (following the existing naming pattern, e.g., `Custom Build: NoLoopK, NerdFont`).
  - The release notes MUST mention the Nerd Font patcher version used.

- **FR-006: Graceful Failure Handling** (Priority: P0 — Must Have)
  - If the `nerdfonts/patcher` Docker image fails to pull (e.g., Docker Hub is down, rate-limited, or the tag is missing), the workflow MUST:
    - Log a clear warning message explaining the failure
    - Skip the Nerd Font patching and packaging steps
    - Continue to produce and release the base build artifacts normally
    - Add a warning to the job summary indicating that Nerd Font patching was requested but failed
  - If the patching process itself fails (e.g., Out of Memory inside the container, or a patcher script crash), the workflow MUST:
    - Log a clear warning message identifying the failed step (pull, patch, or package)
    - Abort the creation of the Nerd Font archives
    - Continue to produce and release the base build artifacts normally
    - Add a warning to the job summary indicating that Nerd Font patching was attempted but failed
  - The base build MUST NEVER fail due to a Nerd Font failure, whether it occurs during image pull, patching, or packaging.

- **FR-007: Job Summary Enhancement** (Priority: P1 — Should Have)
  - The job summary (Step 9) MUST display the Nerd Font patching status:
    - `NerdFontPatching: enabled (nerdfonts/patcher v3.5.0)` — when patching succeeds
    - `NerdFontPatching: enabled (FAILED — base build unaffected)` — when patching fails
    - `NerdFontPatching: disabled` — when the option is not enabled
  - The summary SHOULD list the number of patched font files and total patching duration.

- **FR-008: CI Artifact Upload** (Priority: P0 — Must Have)
  - When `NerdFontPatching = true` and patching succeeds, the Nerd Font archives MUST be uploaded as GitHub Actions artifacts alongside the base build artifacts.
  - The artifact name SHOULD be `nerd-font-build` (separate from the existing `custom-build` artifact).

- **FR-009: User Documentation** (Priority: P1 — Should Have)
  - The `docs/CUSTOM-BUILD.md` file MUST be updated to:
    - Add `Nerd Font Patching` to the build options table with its description, default value, and behavior
    - Explain what Nerd Fonts are and what icon sets are included
    - Show an example `config.json` with `NerdFontPatching: true`
    - Show an example `gh workflow run` command with `--field nerd_font_patching=true`
    - Document the separate Nerd Font archive and its contents

- **FR-010: Backward Compatibility** (Priority: P0 — Must Have)
  - When `NerdFontPatching = false` (the default), the entire pipeline MUST behave identically to the current V1 workflow.
  - No existing tests may break. All existing build configurations MUST continue to produce identical output.
  - Zero regression risk for users who do not enable the option.

## 5. User experience

### 5.1 Entry points and first-time user flow

- **GitHub Actions UI:** Fork Owner navigates to the "Actions" tab → selects "Custom Build" workflow → clicks "Run workflow" → sees the new `Nerd Font Patching` checkbox (unchecked by default) alongside existing options → checks it → clicks "Run workflow".
- **config.json:** Fork Owner adds `"NerdFontPatching": true` to their `config.json` file in their fork. The next workflow run picks up the option automatically.
- **GitHub CLI:** Fork Owner runs `gh workflow run custom-build.yml --field nerd_font_patching=true` from their terminal.

### 5.2 Core experience

- **Step 1 — Toggle:** User enables `Nerd Font Patching` via any of the three entry points (UI checkbox, config.json, or CLI).
- **Step 2 — Build:** The workflow runs normally through Stage 1 (FontForge compilation) and Stage 2 (packaging). The user sees familiar progress in the Actions log.
- **Step 3 — Patch:** After Stage 2, the workflow pulls the `nerdfonts/patcher` Docker image and patches all generated font files. The user sees progress logs for each font being patched.
- **Step 4 — Package:** Patched fonts are packaged into separate `fantasque-sans-nerd-font.zip` and `.tar.gz` archives.
- **Step 5 — Download:** The user downloads the Nerd Font archive from the GitHub Release page or the Actions artifacts. The base build archive is also available as usual.

### 5.3 UI/UX highlights and edge cases

- **Default is OFF:** The `NerdFontPatching` option defaults to `false` to avoid surprising users with longer build times or unexpected output.
- **Clear separation:** Nerd Font output is packaged in a separate archive, not mixed into the base build. Users who do not want Nerd Font glyphs are never affected.
- **Job summary transparency:** The job summary clearly indicates whether Nerd Font patching was enabled, whether it succeeded, and which patcher version was used.
- **Edge case — Docker Hub outage:** If the patcher image cannot be pulled, the build continues normally. The user gets a warning in the job summary but still receives their base fonts.
- **Edge case — Patching process failure:** If the patcher crashes mid-run (e.g., Out of Memory inside the container), the workflow aborts Nerd Font archive creation but still completes and releases the base build. The job summary shows the failure status.
- **Edge case — Proportional font patching:** Proportional fonts (FantasqueSans, non-Mono) are also patched. While less common for terminal usage, some users may want Nerd Font icons in a proportional font for GUI applications.
- **Edge case — Large archive size:** Nerd Font patched TTFs can be 3-4MB per weight (vs ~300KB unpatched). The Nerd Font archive will be significantly larger than the base build. This is expected behavior and should be documented.
- **Edge case — Workflow timeout:** Patching 10 font files (5 weights × 2 formats) adds ~5-10 minutes. If the total workflow approaches the 30-minute GitHub Actions timeout, the `timeout-minutes` value should be increased. This is a CI configuration concern, not a user-facing issue.

## 6. Narrative

Dev Reza opens their fork of Fantasque Sans Mono on GitHub. They navigate to the Actions tab and select the Custom Build workflow. Today, they want something special: their favorite `NoLoopK` variant, but with Nerd Font icons for their Starship prompt in kitty terminal. They check the new "Nerd Font Patching" box alongside "No Loop K", and click "Run workflow."

Ten minutes later, the build completes. Reza downloads two archives from the release page: their usual `fantasque-sans-custom-build.zip` with the `NoLoopK` variant, and a new `fantasque-sans-nerd-font.zip` containing the same variant — now enriched with 10,000+ developer icons. They install the Nerd Font version in kitty, and their Powerline segments, git status icons, and file type glyphs all render beautifully. No Docker installed. No FontForge. No manual patching. Just a checkbox and a download.

## 7. Success metrics

### 7.1 User-centric metrics

- **Adoption rate:** ≥30% of Custom Build runs should enable `NerdFontPatching` within 3 months of release.
- **Zero-friction experience:** Users should be able to enable Nerd Font patching and download the result with no additional steps beyond the existing Custom Build workflow.
- **Documentation clarity:** Zero GitHub Issues opened asking "how do I get Nerd Font icons" within the first release cycle after documentation is updated.

### 7.2 Business metrics

- **Fork growth:** Track whether the availability of in-house Nerd Font patching correlates with increased fork count (baseline: current fork count at launch).
- **Issue reduction:** Decrease in GitHub Issues related to "Nerd Font version mismatch" or "how to patch Fantasque Sans Mono with Nerd Fonts."

### 7.3 Technical metrics

- **Build success rate:** ≥99% of builds with `NerdFontPatching = true` should complete successfully (excluding Docker Hub outages).
- **Patching duration:** The total Nerd Font patching step (pull + patch + package) should complete in ≤15 minutes.
- **Font file validity:** 100% of patched font files must pass `fontTools` validation (valid TTF/OTF structure).
- **Glyph count verification:** Patched fonts must contain ≥10,000 glyphs (baseline Fantasque Sans Mono has ~2,500).
- **Backward compatibility:** 100% of existing tests must pass without modification when `NerdFontPatching = false`.

## 8. Technical considerations (Input for Engineering Team)

### 8.1 Integration points

- **`config.schema.json`:** Add `NerdFontPatching` boolean property (default: `false`).
- **`Scripts/configure.py`:** Add to `DEFAULTS`, `FORM_KEY_TO_OPTION`. Do NOT add to `OPTION_TO_DRIVER_FLAG` — this is a post-build option, not a Stage 1 driver flag.
- **`.github/workflows/custom-build.yml`:** Add `workflow_dispatch` input + 3 new conditional steps after Stage 2 packaging.
- **`docs/CUSTOM-BUILD.md`:** Update build options table and add Nerd Font section.
- **`tests/test_configure.py`:** Add test cases for the new option.

### 8.2 Data storage and privacy

- **No user data involved.** The Nerd Font patching process operates entirely on font binary files within the CI runner. No user data, credentials, or personal information is collected, stored, or transmitted.
- **License compliance:** Fantasque Sans Mono uses SIL OFL without Reserved Font Names (RFN). No font name substitution is required. The patcher's default naming convention (appending "Nerd Font") is compliant.
- **Third-party image trust:** The `nerdfonts/patcher` Docker image is pulled from Docker Hub. The project trusts this image as it is maintained by the official Nerd Fonts organization.

### 8.3 Scalability and potential technical challenges

- **Docker image pull latency:** The `nerdfonts/patcher` image is ~500MB+. Initial pull adds ~2-3 minutes to CI build time. Mitigation: Consider caching the Docker image layer in CI if supported by the runner.
- **Patching execution time:** Each font file takes ~30-60 seconds to patch. With 10 files (5 weights × 2 formats), total patching time is ~5-10 minutes. This is within acceptable limits but should be monitored.
- **GitHub Actions timeout:** The combined pipeline (compile + package + patch) may approach the 30-minute default timeout. The workflow should set an appropriate `timeout-minutes` value (e.g., 45 minutes).
- **Font file size increase:** Patched TTF files grow from ~300KB to ~3-4MB per weight. The total Nerd Font archive will be ~30-40MB. This is expected and consistent with official Nerd Fonts releases.
- **Patcher version pinning:** The Docker image tag MUST be pinned (e.g., `nerdfonts/patcher:v3.5.0`). Using `latest` is strictly prohibited to ensure reproducible builds.
- **Proportional font patching caveats:** The `--mono` flag should ONLY be applied to Mono variants. Proportional variants (FantasqueSans) should be patched WITHOUT `--mono` to avoid forced single-width icons in a variable-width font.
- **Stage 2 font extraction:** The NF patching step reads the TTF/OTF files directly from the Stage 2 temporary output directory before the final archiving steps are completed. The workflow must not rely on re-archiving or re-extracting the base build archives.
- **Architectural constraint CON-001:** `build.py`, `fontbuilder.py`, `features.py`, and `Makefile` MUST NOT be modified. The entire NF feature is additive — operating on pipeline output only.

## 9. Milestones and sequencing

### 9.1 Project estimate and Team composition

- **Size:** Small-Medium | **Estimate:** 3-5 days | **Team:** 1 developer (with CI/Docker experience)

### 9.2 Suggested phases

- **Phase 1 — Configuration Layer** (1 day)
  - Add `NerdFontPatching` to `config.schema.json`
  - Update `Scripts/configure.py` (DEFAULTS, FORM_KEY_TO_OPTION)
  - Add unit tests for the new option
  - Verify all existing tests pass

- **Phase 2 — Workflow Integration** (2 days)
  - Add `nerd_font_patching` input to `workflow_dispatch`
  - Implement Docker image pull step (conditional)
  - Implement patching step with correct flags per variant type (conditional)
  - Implement Nerd Font output packaging step (conditional)
  - Implement graceful failure handling (fallback to base build on Docker pull failure)
  - Update artifact upload and release steps to include NF archives

- **Phase 3 — Validation and Documentation** (1-2 days)
  - Run end-to-end test: Custom Build with `NerdFontPatching = true`
  - Validate patched font files (glyph count, file validity, visual spot-check)
  - Verify backward compatibility with `NerdFontPatching = false`
  - Update `docs/CUSTOM-BUILD.md`
  - Update `docs/ARCHITECTURE.md` to reference Stage 3
  - Update job summary to include NF status

## 10. User stories and Acceptance Criteria

### 10.1. Enable Nerd Font Patching via UI

- **ID**: GH-001
- **Story**: As a Fork Owner, I want to check a "Nerd Font Patching" checkbox in the GitHub Actions workflow dispatch UI, so that my Custom Build includes Nerd Font icons without any local toolchain setup.
- **Acceptance criteria**:
  - [ ] The `workflow_dispatch` UI shows a `nerd_font_patching` boolean input with label "Patch fonts with Nerd Font glyphs (10,000+ icons)"
  - [ ] The input defaults to `false` (unchecked)
  - [ ] When checked, the resolved value is passed to `configure.py` and written to `manifest.json` as `resolved_options.NerdFontPatching: true`

### 10.2. Enable Nerd Font Patching via config.json

- **ID**: GH-002
- **Story**: As a Fork Owner, I want to set `"NerdFontPatching": true` in my `config.json` file, so that Nerd Font patching is enabled by default for all my Custom Builds without manually checking a box each time.
- **Acceptance criteria**:
  - [ ] `config.schema.json` includes a `NerdFontPatching` property of type `boolean` with default `false`
  - [ ] A `config.json` file with `"NerdFontPatching": true` is validated successfully against the schema
  - [ ] The config.json value is correctly resolved through the precedence hierarchy (form > config.json > defaults)
  - [ ] A `config.json` without the `NerdFontPatching` key is still valid and defaults to `false`

### 10.3. Enable Nerd Font Patching via CLI

- **ID**: GH-003
- **Story**: As a Fork Owner using the GitHub CLI, I want to trigger a Custom Build with Nerd Font patching via `gh workflow run`, so that I can automate builds from my terminal or CI scripts.
- **Acceptance criteria**:
  - [ ] Running `gh workflow run custom-build.yml --field nerd_font_patching=true` successfully triggers a build with Nerd Font patching enabled
  - [ ] The `nerd_font_patching` field is correctly mapped to the `NerdFontPatching` option via `FORM_KEY_TO_OPTION`

### 10.4. Nerd Font patching produces valid output

- **ID**: GH-004
- **Story**: As a Terminal Developer, I want the Nerd Font patching step to produce valid, installable font files with all icon glyphs included, so that I can use them in my terminal without rendering issues.
- **Acceptance criteria**:
  - [ ] All Mono variants (Regular, Bold, Italic, BoldItalic) are patched with `--complete --mono --adjust-line-height` flags
  - [ ] The Proportional variant (FantasqueSans) is patched with `--complete --adjust-line-height` flags (without `--mono`)
  - [ ] Both TTF and OTF formats are patched for all variants (10 files total)
  - [ ] The `--careful` flag is NOT used (existing glyphs at conflicting codepoints are replaced)
  - [ ] The patcher Docker image is pinned to a specific version tag (e.g., `nerdfonts/patcher:v3.5.0`)
  - [ ] Each patched font file is a structurally valid TTF or OTF (passes fontTools validation)
  - [ ] Each patched font contains ≥10,000 glyphs

### 10.5. Nerd Font output is packaged separately

- **ID**: GH-005
- **Story**: As a Fork Owner, I want the Nerd Font patched fonts packaged in a separate archive from the base build, so that I can distribute them independently and existing users are not affected.
- **Acceptance criteria**:
  - [ ] Nerd Font output is packaged as `fantasque-sans-nerd-font.zip` and `fantasque-sans-nerd-font.tar.gz`
  - [ ] The archive contains `TTF/` and `OTF/` directories with all patched font files
  - [ ] The archive includes `manifest.json`, `LICENSE.txt`, and `README.md`
  - [ ] The base build archives (`fantasque-sans-custom-build.zip/.tar.gz`) are unchanged and contain only unpatched fonts
  - [ ] Both archives are uploaded as GitHub Actions artifacts
  - [ ] Both archives are attached to the GitHub Release

### 10.6. Manifest includes Nerd Font metadata

- **ID**: GH-006
- **Story**: As a Fork Owner who audits build output, I want the manifest to include the Nerd Font patcher version, so that I can verify exactly which patcher version was used for reproducibility.
- **Acceptance criteria**:
  - [ ] When `NerdFontPatching = true`, `manifest.json` includes `"nerd_font_version": "3.5.0"` (matching the pinned Docker tag)
  - [ ] When `NerdFontPatching = false`, `manifest.json` does NOT include the `nerd_font_version` key
  - [ ] `resolved_options.NerdFontPatching` correctly reflects `true` or `false` in all cases

### 10.7. Graceful failure on Docker pull or patching error

- **ID**: GH-007
- **Story**: As a Fork Owner, I want the build to still succeed with base fonts if the Nerd Font patcher image cannot be pulled OR if the patching process itself fails (e.g., Out of Memory or a script crash inside the container), so that I am never left without a build due to an external dependency or patching failure.
- **Acceptance criteria**:
  - [ ] If `docker pull nerdfonts/patcher:v3.5.0` fails, the workflow logs a clear warning message
  - [ ] If the patching process fails (e.g., Out of Memory or a patcher script crash inside the container), the workflow logs a clear warning message and aborts Nerd Font archive creation
  - [ ] In both failure cases, the Nerd Font patching and packaging steps are skipped, and the base build artifacts (`fantasque-sans-custom-build.zip/.tar.gz`) are produced and uploaded normally
  - [ ] In both failure cases, the GitHub Release is created with base build artifacts only
  - [ ] In both failure cases, the job summary includes a warning: `NerdFontPatching: enabled (FAILED — base build unaffected)`
  - [ ] In both failure cases, the workflow exit code is still 0 (success)

### 10.8. Job summary shows Nerd Font status

- **ID**: GH-008
- **Story**: As a Fork Owner reviewing a completed build, I want the job summary to clearly show whether Nerd Font patching was enabled, whether it succeeded, and the patcher version used, so that I can quickly assess the build output.
- **Acceptance criteria**:
  - [ ] When patching succeeds: summary shows `NerdFontPatching: enabled (nerdfonts/patcher v3.5.0)`
  - [ ] When patching fails: summary shows `NerdFontPatching: enabled (FAILED — base build unaffected)`
  - [ ] When patching is disabled: summary shows `NerdFontPatching: disabled`
  - [ ] The summary includes the number of patched font files and total patching duration (when successful)

### 10.9. Release includes Nerd Font label

- **ID**: GH-009
- **Story**: As a downstream consumer browsing GitHub Releases, I want the release title to indicate when Nerd Font patching was applied, so that I can quickly identify which releases include Nerd Font variants.
- **Acceptance criteria**:
  - [ ] When `NerdFontPatching = true`, the release title includes `NerdFont` as a label (e.g., `Custom Build: NoLoopK, NerdFont`)
  - [ ] When `NerdFontPatching = false`, the release title does NOT include `NerdFont`
  - [ ] The release notes include a section describing the Nerd Font patcher version used and a brief description of the included icon sets

### 10.10. User documentation is updated

- **ID**: GH-010
- **Story**: As a new Fork Owner, I want the Custom Build documentation to explain the Nerd Font Patching option, so that I understand what it does and how to enable it before I run my first build.
- **Acceptance criteria**:
  - [ ] `docs/CUSTOM-BUILD.md` includes `Nerd Font Patching` in the build options table with description: "Patches generated fonts with 10,000+ developer icons from Nerd Fonts (Powerline, Font Awesome, Material Design, Octicons, etc.)" and default: `Off`
  - [ ] The documentation explains that patched fonts are packaged separately and do not affect the base build
  - [ ] A `config.json` example with `"NerdFontPatching": true` is provided
  - [ ] A `gh workflow run` example with `--field nerd_font_patching=true` is provided
  - [ ] The documentation notes the expected file size increase for patched fonts

### 10.11. Backward compatibility is preserved

- **ID**: GH-011
- **Story**: As an existing Fork Owner who does not want Nerd Fonts, I want my existing Custom Build workflow to behave identically after this feature is added, so that I experience zero regression or unexpected changes.
- **Acceptance criteria**:
  - [ ] All existing unit tests pass without modification when `NerdFontPatching` is added to the configuration layer
  - [ ] A build with `NerdFontPatching = false` (the default) produces identical output to the current V1 pipeline
  - [ ] No new workflow steps execute when `NerdFontPatching = false`
  - [ ] The existing `config.json` files without `NerdFontPatching` key remain valid and produce default behavior
  - [ ] `NerdFontPatching` is NOT mapped to `OPTION_TO_DRIVER_FLAG` (no impact on Stage 1 compilation)

### 10.12. Nerd Font Patching for Proportional variants

- **ID**: GH-012
- **Story**: As a developer using FantasqueSans (proportional, non-Mono) in a GUI application, I want the Nerd Font patcher to also patch the proportional variant, so that I have Nerd Font icons available in non-terminal contexts.
- **Acceptance criteria**:
  - [ ] The proportional variant (`FantasqueSans.ttf`, `FantasqueSans.otf`) is patched when `NerdFontPatching = true`
  - [ ] The `--mono` flag is NOT applied to the proportional variant (icons are proportionally spaced)
  - [ ] The `--complete` and `--adjust-line-height` flags ARE applied to the proportional variant
  - [ ] The patched proportional font is included in the Nerd Font archive alongside the Mono variants

### 10.13. Nerd Font patcher version is pinned

- **ID**: GH-013
- **Story**: As a Fork Owner who values reproducible builds, I want the Nerd Font patcher Docker image to be pinned to a specific version tag, so that my builds produce consistent output regardless of when they run.
- **Acceptance criteria**:
  - [ ] The workflow references `nerdfonts/patcher:v3.5.0` (or the current pinned version), never `latest`
  - [ ] The pinned version is documented in the workflow file and in `docs/CUSTOM-BUILD.md`
  - [ ] The pinned version is recorded in `manifest.json` as `nerd_font_version`

### 10.14. Unit tests for NerdFontPatching configuration

- **ID**: GH-014
- **Story**: As a developer maintaining the Custom Build codebase, I want comprehensive unit tests for the NerdFontPatching configuration option, so that any regression in option resolution is caught immediately.
- **Acceptance criteria**:
  - [ ] `test_configure.py` verifies that `NerdFontPatching` exists in `DEFAULTS` with value `False`
  - [ ] `test_configure.py` verifies that `"nerd_font_patching"` maps to `"NerdFontPatching"` in `FORM_KEY_TO_OPTION`
  - [ ] `test_configure.py` verifies that `NerdFontPatching` is NOT present in `OPTION_TO_DRIVER_FLAG`
  - [ ] The existing `test_defaults_match_schema_defaults` test passes with the updated schema and defaults
  - [ ] Precedence tests cover `NerdFontPatching` flowing correctly through config.json, form data, and CLI overrides
