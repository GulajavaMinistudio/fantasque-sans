---
title: "PRD — Custom Build via GitHub Workflow"
status: DRAFT (Phase 1 — pending approval)
date: 2026-07-23
version: 1.2
phase: SDLC Phase 1 (PRD)
project: Fantasque Sans Mono
upstream_discovery: docs/discovery-draft-20260723-1058-custom-build-workflow.md
downstream_phase: "@ClarificationAnalyst → @SpecificationArchitect"
---

## PRD: Custom Build via GitHub Workflow
<!-- markdownlint-disable  -->
## 1. Product overview

### 1.1 Document title and version

- **PRD**: Custom Build via GitHub Workflow
- **Version**: 1.2 (DRAFT — pending stakeholder approval)
- **SDLC Phase**: Phase 1 (PRD) — upstream: Phase 0 Discovery (approved); downstream: Clarification Checkpoint → Technical Specification
- **Date**: 2026-07-23
- **Author**: Product Manager PRD persona
- **Upstream artifact**: [`docs/discovery-draft-20260723-1058-custom-build-workflow.md`](/docs/discovery-draft-20260723-1058-custom-build-workflow.md)
- **Target release window**: After V1 implementation completes, no fixed calendar date
- **License impact**: None — all outputs remain under SIL Open Font License (OFL); no relicensing or rebranding

### 1.2 Product summary

This PRD defines the requirements for a **Custom Build System** that lets any GitHub user produce a personalized variant of the Fantasque Sans Mono font directly from the cloud, without installing FontForge, Python, or any other local build toolchain locally — the entire build runs in a cloud-hosted Docker container. Users fork the repository, declare their preferred variant combination through either a `config.json` file or an interactive `workflow_dispatch` form, and receive a fully compiled font bundle (`.zip` and `.tar.gz`) published automatically as a GitHub Release and a Workflow Artifact.

The architecture, inspired by [Maple Mono's build workflow](https://github.com/subframe7536/maple-font), uses a **configuration-layer strategy**: the Makefile entry-point script (`Scripts/build.py`) is preserved in Python 2.7 to keep the local `make` workflow unchanged, and the variant engine and feature generator (`Scripts/fontbuilder.py`, `Scripts/features.py`) **also remain in Python 2.7 for V1 — their port to Python 3.14 is deferred to V2** (see §8.3 Challenge 1). A new Python 3.14 configuration layer (`configure.py`) and a `custom-build.yml` GitHub Actions workflow orchestrate the build and translate user-facing configuration into pipeline arguments. This preserves the proven Makefile entry point and the existing font compilation pipeline while modernizing only the user-facing configuration and the distribution surfaces.

The system targets **two user personas with equal priority** (per Phase 1 clarification, 2026-07-23): (1) **Casper**, a non-technical end-user who wants a pre-configured variant through a web form, and (2) **Penny**, a developer or power user who wants declarative, version-controlled configuration through `config.json`. The success of V1 will be measured primarily by **adoption and distribution** — number of forks that trigger builds, number of published releases, and total download count.

## 2. Goals

### 2.1 Business goals

- **BG-1**: Increase Fantasque Sans Mono adoption by eliminating the technical barrier (no local build toolchain) to obtaining a customized variant
- **BG-2**: Create a sustainable, decentralized distribution model in which every fork becomes a self-service build node, reducing the maintainer's release-publishing burden
- **BG-3**: Drive community engagement and contribution by making variant experimentation low-cost and reversible
- **BG-4**: Establish a foundation for future feature expansion (alternate glyphs once designed, custom weights, brand-aligned derivatives) without re-architecting the build system
- **BG-5**: Strengthen the project's reputation as a forward-looking, contributor-friendly open-source font by adopting modern CI/CD patterns

### 2.2 User goals

- **UG-1** (Power User / Penny): Configure, build, and distribute a custom Fantasque Sans Mono variant from a forked repository without installing any local development tools
- **UG-2** (Power User / Penny): Declare build preferences in a version-controlled `config.json` file so the configuration travels with the fork
- **UG-3** (Casual User / Casper): Download a pre-built, customized font bundle in fewer than 5 minutes from first-time fork to final download
- **UG-4** (Both personas): Trust that the build is reproducible, secure, and isolated from other users' builds
- **UG-5** (Power User / Penny): Override committed `config.json` values on a one-off basis via form inputs without committing changes

### 2.3 Non-goals (Out of Scope)

The following items are **explicitly excluded** from V1 and will not be delivered in this release:

- **NG-1**: Alternate glyph variants for `$` and `0` — blocked until the corresponding `.glyph` files are created in the source `.sfdir` directories by the font designer (per Discovery Draft §5.1)
- **NG-2**: Custom font family renaming or rebranding — would conflict with the SIL Open Font License and the original brand
- **NG-3**: Windows runners and self-hosted runners — V1 uses `ubuntu-latest` GitHub-hosted runners only
- **NG-4**: Direct integration with IDEs, terminal emulators, or package managers (Homebrew Cask, apt, pacman, etc.)
- **NG-5**: Build caching or incremental compilation — every build runs from a clean source state for determinism
- **NG-6**: Telemetry, usage analytics, crash reporting, or any data collection from fork users — privacy by default
- **NG-7**: Email, Slack, Discord, or any push-notification system for build status — users monitor their own builds via the GitHub Actions tab
- **NG-8**: Cryptographic signing (GPG, cosign, sigstore) of built artifacts — the security model relies on GitHub's existing trust mechanisms
- **NG-9**: Full rewrite of `Scripts/build.py` (the Makefile entry point) to Python 3 — `Scripts/build.py` remains Python 2.7 in V1 to keep the local `make` workflow stable. NOTE: `Scripts/fontbuilder.py` and `Scripts/features.py` also remain Python 2.7 in V1 (their port to Python 3.14 is **deferred to V2**, see §8.3 Challenge 1); only the new `configure.py` wrapper runs on Python 3.14
- **NG-10**: Multi-tenant or shared release channels — each fork publishes only to its own Releases namespace
- **NG-11**: Custom spacing presets (`spacing` choice: `normal` | `loose` | `half-loose` | `half-tight` | `tight`) — **deferred to V2**. Originally scoped into V1 by the Discovery "Grilling Decision #1"; excluded from V1 to keep the configuration surface to four boolean options (`LargeLineHeight`, `NoLoopK`, `NoCalt`, `UseHinted`) and to align with the deferred engine port (Clarification Resolution #3).

## 3. User personas

### 3.1 Key user types

- **Casper** — Casual End-User: A non-technical user who wants a customized font variant without any build tooling
- **Penny** — Power User / Fork Maintainer: A developer comfortable with GitHub Actions, JSON configuration, and the Git fork workflow
- **Quinn** — Quality Reviewer / Downstream Maintainer: The original Fantasque Sans Mono maintainer, downstream packager, or trusted community member who audits fork outputs for quality and license compliance

### 3.2 Basic persona details

**Casper (Casual End-User)**

A graphic designer, writer, or developer who discovered Fantasque Sans Mono through a blog post, social media, or word-of-mouth. They want a specific variant (for example, "no-loop k with larger line height") but have never compiled a font before. They are comfortable with GitHub's web UI but not with command-line build tools, Python, or FontForge. They expect to fork the repository, click a button, fill in a form, and download a `.zip` file within minutes. They do not intend to modify the font source or contribute code back; they only want a working build.

Casper's success criteria: obtain a usable `.zip` file in fewer than 5 minutes without ever opening a terminal.

**Penny (Power User / Fork Maintainer)**

A software developer, DevOps engineer, or font enthusiast who wants full control over their font build. They are familiar with Git workflows, JSON configuration, and the basics of GitHub Actions. They prefer declarative configuration over GUI forms when possible. They may maintain their own custom build for personal use, or they may maintain a community fork that publishes a curated set of variants for their team or community. They expect documentation that respects their technical background and provides escape hatches (CLI flags, `gh` commands, environment variables) when needed.

Penny's success criteria: declare their team's preferred variant in `config.json`, trigger the build via `gh workflow run`, and have the result automatically published to a versioned release — all without leaving the command line.

**Quinn (Quality Reviewer / Downstream Maintainer)**

The original Fantasque Sans Mono maintainer, a downstream package maintainer (for example, a Linux distribution packager), or a trusted community reviewer. Their role is non-blocking but important: they spot-check popular forks to ensure variants remain faithful to the original design intent and license. They do not actively trigger builds themselves; they consume published releases and may file issues when they spot problems.

Quinn's success criteria: verify a fork's output quickly by reading the `manifest.json` and inspecting a small number of glyphs, without running the build locally.

### 3.3 Role-based access

| Role                             | Permissions and surface area                                                                                                                                                                                                                                 |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Fork Owner** (any GitHub user) | Can fork the upstream repository, modify `config.json` in their own fork, trigger the `workflow_dispatch` workflow, and have releases published to their own fork only. Cannot modify the upstream repository or any other fork.                             |
| **Upstream Maintainer**          | Has full administrative control over the upstream `belluzj/fantasque-sans` repository. Can update the workflow template, revoke bad actors, change defaults, or deprecate the feature. Receives no automatic notifications about fork activity.              |
| **Anonymous Downloader**         | Can browse and download any release or artifact published by any public fork via the GitHub web interface. No write access, no build triggering, no account required.                                                                                        |
| **GitHub Actions Bot**           | System role that executes the workflow on behalf of the fork owner. Has a scoped `GITHUB_TOKEN` with `contents: write` permission sufficient for artifact upload and release creation within the fork only. Token is automatically scoped per-run by GitHub. |

## 4. Functional requirements

### 4.1 FR-1: Configuration File (config.json) — Priority P0 (Must Have)

- A `config.json` file at the repository root shall declare the fork owner's preferred build options
- The file shall be a single JSON object with a flat key-value structure and no nested objects
- The four supported keys are: `LargeLineHeight` (boolean), `NoLoopK` (boolean), `NoCalt` (boolean), and `UseHinted` (boolean, default: `true`)
- An absent `config.json` shall fall back to the build defaults without failing the build
- A malformed `config.json` shall fail the build with a clear, actionable error message (see FR-7)
- Unknown keys in `config.json` shall produce a warning but shall not fail the build (forward compatibility)

### 4.2 FR-2: Interactive Form (workflow_dispatch) — Priority P0 (Must Have)

- The workflow shall expose a `workflow_dispatch` trigger with the following inputs:
  - `large_line_height` (boolean, default: `false`)
  - `no_loop_k` (boolean, default: `false`)
  - `no_calt` (boolean, default: `false`)
  - `use_hinted` (boolean, default: `true`)
- All form inputs shall be optional with sensible defaults
- The form shall be accessible via the GitHub Actions tab → "Custom Build" → "Run workflow" UI
- A human-readable description shall be shown next to each input via the `description` field

### 4.3 FR-3: Configuration Precedence — Priority P0 (Must Have)

- The build system shall resolve final option values using the following precedence (highest priority first):
  1. `workflow_dispatch` form input (highest)
  2. `config.json` value in the repository
  3. Build defaults baked into the workflow (lowest)
- The resolution logic shall be implemented in a Python 3.14 wrapper script (`configure.py`) that translates the resolved options into command-line arguments for the build pipeline (passed to `Scripts/build.py` for V1)
- The resolution shall be logged in the workflow output, one line per option, naming the source (`form`, `config.json`, or `default`). When no `config.json` is present and form inputs are provided, the per-option source is `form`; when a form input overrides a `config.json` value, the source is logged as `form_override` for that option (see FR-8 for the `config_source` manifest value mapping)
- The `UseHinted` option can be set via both the `config.json` key and the form input (`use_hinted`), resolved with the same precedence rules as all other options

### 4.4 FR-4: Build Execution — Priority P0 (Must Have)

The workflow shall execute the build inside an isolated environment using a Docker container based on **Ubuntu 26.04 LTS** (latest LTS as of V1 release) — the `ubuntu:18.04` base image in the existing `Dockerfile` is end-of-life and shall not be used. The multi-stage build retains a separate Stage 1 image that provides a Python 2.7 runtime (required to execute `Scripts/build.py` and the variant engine); Stage 2 uses Ubuntu 26.04 LTS and provides the Python 3.14 runtime for **packaging tooling only** — the configuration wrapper `configure.py` runs on the **GitHub Actions host runner** (not inside the container) and passes resolved build args to Stage 1 via `docker build --build-arg` (per Technical Specification §4.4)
The container shall bundle all required dependencies: a multi-stage Docker build where Stage 1 provides a Python 2.7 + FontForge pair (built against Python 2.7, executed by `Scripts/build.py`) and runs the variant engine (`Scripts/fontbuilder.py`, `Scripts/features.py`) in the same Python 2.7 process; Stage 2 uses **Ubuntu 26.04 LTS** with **Python 3.14** (installed explicitly via deadsnakes PPA or pyenv, since the distro default may be 3.13), and provides the Python 3.14 runtime for post-build packaging tools. The configuration wrapper `configure.py` runs on the **GitHub Actions host runner** (not inside the container) and passes resolved build args to Stage 1 via `docker build --build-arg`. Modern tooling (`ttfautohint`, `sfnt2woff` from the `woff-tools` package, and `woff2_compress` from the Google WOFF2 tools) is installed directly from the Ubuntu 26.04 universe repository. **ADR-0001 is *Superseded*; ADR-0002 (multi-stage Docker: Stage 1 Python 2.7 + Stage 2 Ubuntu 26.04/Python 3.14) must be created in the Spec/Plan phase** to document this new architecture; for V1, see the description in §8.3 Challenge 1 & 2
The build shall invoke `Scripts/build.py` (preserved as Python 2.7) for the Makefile entry point and orchestration; `Scripts/build.py` imports `Scripts/fontbuilder.py` and `Scripts/features.py` in-process (all on Python 2.7) for variant generation and OpenType feature compilation — their port to Python 3.14 is deferred to V2 (see §8.3 Challenge 1). The local `make` workflow remains unchanged because `Scripts/build.py` is untouched
- The build shall produce TTF, OTF, WOFF, WOFF2, and SVG outputs for all 4 weights of Fantasque Sans Mono (Regular, Bold, Italic, Bold Italic) with the resolved variant options applied
- The `use_hinted` form input shall control whether `ttfautohint` is invoked on the TTF outputs (default: yes)

### 4.5 FR-5: Artifact Publishing — Priority P0 (Must Have)

- Build outputs shall be packaged into two archives: `.zip` (primary, Windows-friendly) and `.tar.gz` (secondary, Unix-friendly)
- The archives shall be uploaded as GitHub Actions Artifacts with names following the pattern `fantasque-sans-custom-build-{run_id}-{run_attempt}`
- Artifacts shall be retained for at least 90 days (the default GitHub Actions retention)
- A `manifest.json` shall be included in each archive (see FR-8)
- The original `LICENSE.txt` and a top-level `README.md` (pointing to upstream) shall be included in each archive for license compliance

### 4.6 FR-6: GitHub Releases Publishing — Priority P0 (Must Have)

- The workflow shall automatically create a GitHub Release on the fork on every successful build
- The release tag shall follow the pattern `custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}` (UTC, to avoid timezone ambiguity). The `{run_id}` and `{run_attempt}` suffix prevents tag collision when concurrent workflow runs target the same fork
- The release title shall be human-readable and reflect the resolved variant combination — for example: `Custom Build: LargeLineHeight + NoLoopK` or `Custom Build: Normal (default)`. When `UseHinted=false`, append `(unhinted)` — for example: `Custom Build: NoCalt (unhinted)`
- The release body (auto-generated notes) shall include: resolved options table, list of included font files with SHA-256 checksums (a summary — the full manifest with complete checksums is inside the archive), build timestamp, source commit SHA, and a link back to the workflow run
- Only one release shall be created per workflow **run attempt** (`run_attempt`); the workflow shall not create a duplicate release within the same `run_attempt`. A manual workflow re-run produces a new `run_attempt` and therefore a new, uniquely tagged release (by design, per US-006). Internal network retries of the release-creation API call (see FR-10) are idempotent and do not create additional releases

### 4.7 FR-7: Configuration Schema Validation — Priority P1 (Should Have)

- A `config.schema.json` file (JSON Schema draft-07) shall be provided at the repository root, describing the valid structure of `config.json`
- The workflow shall validate `config.json` against the schema before invoking the build
- Invalid configurations shall fail the build with a non-zero exit code and a clear error message identifying the offending key and its expected type — for example: `Invalid config.json: 'LargeLineHeight' must be a boolean, got string at line 2 column 18`
- The validation step shall be a named, separately viewable step in the Actions UI so users can find it quickly
- Unknown keys shall produce a warning but shall not fail validation (forward compatibility for future schema versions)

### 4.8 FR-8: Build Manifest — Priority P1 (Should Have)

- Every archive shall include a `manifest.json` file at the root level
  - `config_source` (one of `form` | `config.json` | `form_override` | `defaults`), and `workflow_version` (semver or commit SHA). `config_source: "defaults"` applies when no `config.json` is present, when the file is an empty object (`{}`), or when the file contains no overrides and no form inputs are provided — an empty `config.json` is treated identically to a missing file. `config_source: "form"` applies when one or more `workflow_dispatch` form inputs differ from the build defaults **and no `config.json` is present** in the fork (the form is the sole source of configuration). `config_source: "config.json"` applies when a `config.json` is present and supplies the resolved values without any form override. `config_source: "form_override"` applies when a form input overrides a value present in `config.json`
- SHA-256 checksums in the manifest shall match the actual file checksums (verified by re-hashing during CI)
- The manifest shall be valid JSON (passes `python -m json.tool`)

### 4.9 FR-9: Documentation — Priority P1 (Should Have)

- A `docs/CUSTOM-BUILD.md` guide shall be created covering the user-facing "how to use" workflow
- The guide shall have two clearly separated sections: a "Getting Started" tutorial for Casper and an "Advanced Configuration" reference for Penny
- The `README.md` shall be updated with a prominent new section (above the existing installation instructions) titled "Custom Build" that links to `docs/CUSTOM-BUILD.md`
- The "Getting Started" section shall be a numbered list of no more than 5 steps, each with a one-sentence "Why" explanation
- The "Advanced Configuration" section shall include: full `config.json` schema reference, configuration precedence rules, a worked example (input → output mapping), and a `gh workflow run` CLI example
- Annotated screenshots shall be provided for the GitHub Actions UI steps: Fork button, Actions tab, workflow_dispatch form, Artifacts download page, Releases page

### 4.10 FR-10: Error Handling & User Feedback — Priority P1 (Should Have)

- Build failures shall surface clear, non-cryptic error messages in the workflow log
- Common failure modes (invalid `config.json`, network timeouts, missing tools, `ttfautohint` errors) shall be explicitly handled with user-facing messages
- The workflow summary at the top of each run page shall include a one-line "what happened" statement: on success `Build published to release custom-build-XXXX`; on failure `Build failed at step X: <reason>`
- No silent failures: every failure shall be visible in the GitHub UI
- Network errors during release creation shall be retried with exponential backoff (up to 3 attempts)

### 4.11 FR-11: Backward Compatibility — Priority P2 (Could Have)

- The existing local build (`make`) workflow shall remain fully functional and unchanged
- The custom build system shall not modify, remove, or rename any file in `Scripts/`, `Sources/`, or the root `Makefile`
- The legacy `Dockerfile` may be replaced (base image upgrade) but the new `Dockerfile` shall continue to support `docker build && docker run` as a documented alternative to the GitHub Actions path
- The custom build workflow shall be opt-in and shall not interfere with any other CI/CD that may be added to the repository in the future

## 5. User experience

### 5.1 Entry points & first-time user flow

**Casper's first-time flow (no technical background):**

1. Visits the Fantasque Sans Mono GitHub page (linked from the official site or a blog post)
2. Clicks the prominent "Custom Build" link near the top of the `README.md`
3. Lands on `docs/CUSTOM-BUILD.md` and reads the 3-step illustrated "Getting Started" tutorial
4. Clicks the "Fork this repository" button (Step 1 of the guide)
5. Navigates to the "Actions" tab in their newly created fork (Step 2)
6. Selects the "Custom Build" workflow from the left sidebar and clicks "Run workflow" (Step 3)
7. Optionally fills in the form fields (LargeLineHeight, NoLoopK, NoCalt, use_hinted) or skips to accept defaults
8. Waits for the build to complete (typical: 8-15 minutes; progress visible in the Actions tab)
9. Downloads the resulting `.zip` from either the workflow run's "Artifacts" section or the auto-created Release page

**Penny's first-time flow (experienced developer):**

1. Forks the repository via the GitHub web UI or `gh repo fork belluzj/fantasque-sans`
2. Clones the fork locally: `git clone https://github.com/<username>/fantasque-sans.git && cd fantasque-sans`
3. Edits `config.json` to declare their preferred variant combination
4. Commits and pushes the change: `git commit -am "feat: my preferred variant" && git push`
5. Triggers the workflow either via the GitHub UI or via CLI: `gh workflow run custom-build.yml`
6. Monitors the build via `gh run watch` or the Actions tab
7. Downloads the published release via `gh release download custom-build-<timestamp>` or the web UI
8. (Optional) Installs the font in their system: `unzip FantasqueSansMono.zip -d ~/.fonts && fc-cache -f`

### 5.2 Core experience

- **Triggering the build**: A single, predictable action in the GitHub UI — no scripts, no CLI, no environment setup required
- **Monitoring build progress**: Standard GitHub Actions UI with live log streaming and a visible progress indicator
- **Downloading the result**: Two equally valid paths — Workflow Artifacts (per-run, ephemeral) or GitHub Releases (persistent, discoverable, with auto-generated notes)
- **Re-running a build**: A single "Re-run" button in the Actions UI; the same form values are pre-populated for quick iteration
- **Customizing the configuration**: Two complementary surfaces (form for quick tweaks, file for declarative control) with a clearly documented precedence rule
- **Verifying the build**: Open the `manifest.json` inside the archive to see the resolved options and checksums; diff against the previous manifest to detect changes

### 5.3 UI/UX highlights & edge cases

- **Highlight**: Form input names use snake_case (`large_line_height`, `no_loop_k`) to match common naming conventions in developer tooling, while `config.json` keys use PascalCase (`LargeLineHeight`, `NoLoopK`) to match the existing Python build script conventions — the wrapper script bridges the two naming styles
- **Highlight**: Form input defaults are visible inline in the form, so users know what they will get before clicking "Run workflow"
- **Highlight**: The release title is auto-generated in plain English, so users can identify the variant at a glance from the Releases page — for example: `Custom Build: NoLoopK + NoCalt` or `Custom Build: Normal (default)`. When hinting is disabled, `(unhinted)` is appended: `Custom Build: LargeLineHeight (unhinted)`
- **Edge case — user submits the form with all defaults**: Build proceeds with the pipeline's baseline (Normal variant, hinting enabled); release is titled `Custom Build: Normal (default)`
- **Edge case — user commits an invalid `config.json`**: Schema validation step fails fast with a clear pointer to the offending key and the expected type
- **Edge case — user triggers a build while another is in progress**: The second build queues normally and runs after the first completes; no resource contention
- **Edge case — user forks but never triggers a build**: No side effects; no orphan artifacts, no releases, no GitHub Actions minutes consumed
- **Edge case — GitHub API rate limit hit during release creation**: Workflow retries with exponential backoff (up to 3 attempts, 1s/5s/25s delays); if all retries fail, the workflow fails with a clear message
- **Edge case — fork is private**: Releases on a private fork are not discoverable by the public; this is expected GitHub behavior, not a system bug
- **Edge case — user triggers many builds over time**: Each successful build creates a new GitHub Release, which accumulates over time. Fork owners who experiment with many configurations may accumulate dozens of releases. **Mitigation**: the workflow summary displays the total number of releases present in the fork and warns when the count exceeds 20 (for example: "⚠️ Your fork has 25 releases. Consider deleting old releases to keep your repository organized. See troubleshooting guide."). The troubleshooting documentation (`docs/CUSTOM-BUILD.md`) includes a guide for deleting old releases via the GitHub UI and the `gh release delete` CLI. V1 does not provide automated release cleanup
- **Accessibility**: All form inputs have descriptive labels and `description` fields; error messages include the input name and the actual value received for screen-reader compatibility

## 6. Narrative

Imagine a graphic designer, **Casper**, who has been using Fantasque Sans Mono for years but always wished for a version with larger line height to better accommodate accented capitals in their client work. Before V1, Casper would have had to install FontForge, a Python 2.7 runtime (for the Makefile entry point), a Python 3.14 runtime (for the variant engine), and a long list of system libraries, then run `make` from a terminal — a non-starter for someone who only wants a font. After V1, Casper visits the Fantasque Sans Mono GitHub page, clicks the prominent "Custom Build" link, follows a 3-step illustrated guide, and downloads their custom font bundle as a `.zip` file within five minutes — no terminal, no Python, no toolchain. The `.zip` contains every weight, every format, and a `manifest.json` that records exactly what was built and when.

Across town, **Penny**, a senior developer and font enthusiast, maintains a curated fork for their open-source team's monospace needs. They commit a `config.json` to their fork declaring `{"NoLoopK": true, "UseHinted": false}` and trigger the build whenever they update their configuration. Each new release comes with auto-generated notes; every team member can `gh release download` the latest bundle without ever cloning the repository or installing build tools. **Quinn**, the original maintainer, is happy because they no longer receive "can you add a no-loop K variant?" issues, and because the system requires zero ongoing maintenance from them — the workflow is self-contained in the upstream repository. The result: Casper gets exactly what they want, Penny's team gets a reliable automated pipeline, and Quinn keeps their evenings free.

## 7. Success metrics

### 7.1 User-centric metrics

- **SM-U1**: Median time from first-time fork to successful build download ≤ 5 minutes for ≥ 80% of first-time users
- **SM-U2**: ≥ 90% of first-time users successfully complete a build without consulting external help (measured by the absence of "stuck on step X" issues)
- **SM-U3**: ≥ 4.0 / 5.0 average satisfaction score, if a post-build feedback mechanism is added (out of scope for V1 measurement, but tracked opportunistically)
- **SM-U4**: ≥ 70% of fork owners who trigger one build trigger a second build within 30 days (proxy for stickiness)
- **SM-U5**: Median documentation-to-completion time for Casper (no terminal) ≤ 7 minutes from first page load to download click

### 7.2 Business metrics (PRIMARY — per Phase 1 clarification)

- **SM-B1**: ≥ 100 unique forks trigger the Custom Build workflow within 90 days of release (primary adoption signal)
- **SM-B2**: ≥ 50 GitHub Releases published by community forks within 90 days of release (primary distribution signal)
- **SM-B3**: ≥ 1,000 total downloads (Releases + Artifacts combined) across all forks within 90 days (primary reach signal)
- **SM-B4**: ≤ 10% decrease in "how do I build X variant?" issues opened on the upstream repository within 90 days (deflection signal — these issues should be self-served)
- **SM-B5**: ≥ 5 community contributions (new config presets, documentation improvements, bug reports) to the upstream repository within 180 days (engagement signal)
- **SM-B6**: ≥ 3 downstream packagers or community members cite the Custom Build workflow as the reason they adopted or stayed with Fantasque Sans Mono (qualitative, collected via maintainer outreach)

### 7.3 Technical metrics

- **SM-T1**: ≥ 95% build success rate across all workflow runs, excluding user-error failures (invalid `config.json`, cancelled runs)
- **SM-T2**: p95 build duration ≤ 15 minutes on `ubuntu-latest` GitHub-hosted runner
- **SM-T3**: Zero security incidents related to the workflow's `GITHUB_TOKEN` permissions (token over-scoping, secret leakage, cross-fork contamination)
- **SM-T4**: 100% of published releases include a valid `manifest.json` with accurate checksums
- **SM-T5**: Zero silent build failures — every failure produces a user-visible error message in the Actions UI
- **SM-T6**: ≤ 2 P1 bugs reported in the first 90 days post-release

## 8. Technical considerations (Input for Engineering Team)

### 8.1 Integration points

- **GitHub Actions** — `workflow_dispatch` event for manual triggering; `ubuntu-latest` hosted runner for execution
- **GitHub Releases API** — auto-creation of releases with tagged artifacts (implementation will be evaluated by the Engineering Team; candidates include `softprops/action-gh-release` and the official `gh` CLI)
- **GitHub Artifacts API** — upload of `.zip` and `.tar.gz` archives as workflow artifacts
- **Docker Hub or GitHub Container Registry** — V1 builds the container image on-the-fly within the workflow (`docker build` directly on the runner), without relying on an external registry (neither GHCR nor Docker Hub). No pre-built image is pushed to a public registry. Every workflow run builds the image from the `Dockerfile` present in the repository
  - **Existing build pipeline** — `Scripts/build.py` (Python 2.7) is preserved unchanged for the local `make` workflow and imports `Scripts/fontbuilder.py`/`Scripts/features.py` in-process (all Python 2.7). The port of `Scripts/fontbuilder.py` and `Scripts/features.py` to Python 3.14 is **deferred to V2** (see §8.3 Challenge 1); for V1 they remain Python 2.7 and run in Stage 1
- **JSON Schema (draft-07)** — `config.schema.json` for validation and editor auto-completion in IDEs
- **SIL Open Font License (OFL)** — every archive must include the original `LICENSE.txt`; the license permits subsetting, modification, and redistribution without renaming, so custom builds are license-compliant by default

### 8.2 Data storage & privacy

- **No persistent user data** — the system does not store any user information beyond what GitHub already collects for Actions runs (the Actions run log, the release metadata)
- **No telemetry** — no usage analytics, no error reporting to external services, no third-party tracking pixels, no cookies
- **No outbound network calls** beyond what the existing build pipeline already requires (FontForge font metadata lookups, system package downloads inside the container)
- **No secrets required** — the workflow uses only the default `GITHUB_TOKEN` with minimal, explicitly declared permissions
- **License compliance** — every build output remains under SIL OFL; the `manifest.json` shall include the SPDX license identifier `OFL-1.1`
- **Cross-fork isolation** — a fork's `GITHUB_TOKEN` can only access its own fork, so there is no risk of cross-tenant data leakage

### 8.3 Scalability & potential technical challenges

- **Challenge 1 — Python 2.7 EOL (2020-01-01)**: `Scripts/build.py` (the Makefile entry point) remains written in Python 2.7 for V1 to preserve the stability of the local `make` workflow. `Scripts/fontbuilder.py` and `Scripts/features.py` **have not been ported and remain running on Python 2.7 for V1** — the port to Python 3.14 is **deferred to V2** (clarification result: `build.py` imports both in-process via `from fontbuilder import *`, so splitting them across Python versions is impossible without violating NG-9). The Stage 1 Docker build provides a Python 2.7 + FontForge runtime compiled with Python 2.7 support and executes the entire font compilation (build.py + fontbuilder + features). Stage 2 (`ubuntu:26.04` with Python 3.14) provides the Python 3.14 runtime for post-build packaging tooling. The configuration wrapper `configure.py` runs on the **GitHub Actions host runner** (not inside the container) and passes resolved build args to Stage 1 via `docker build --build-arg`. The Engineering Team must verify that the Stage 1 FontForge binary is compatible with the Stage 2 environment, and this architecture will be formally documented as **ADR-0002** in the next Spec/Plan phase (replacing the *Superseded* status of ADR-0001).
- **Challenge 2 — Container base image upgrade (Stage 2)**: The Stage 2 multi-stage Docker build uses **Ubuntu 26.04 LTS** with **Python 3.14 installed explicitly** via the deadsnakes PPA or pyenv (the Ubuntu 26.04 default Python is likely 3.13, so 3.14 cannot be relied upon from the distro). The Engineering Team must verify that `ttfautohint`, `sfnt2woff`, `woff2_compress` are compatible with the Ubuntu 26.04 system libraries. `configure.py` (Python 3.14) runs on the **GitHub Actions host runner** (not inside the container, per Challenge 1 and Technical Specification §4.4), so its compatibility with the host runner's Python 3.14 is what matters, not the Stage 2 Ubuntu 26.04 image. Stage 1 continues to use the legacy image that provides the Python 2.7 runtime for font compilation (see Challenge 1)
- **Challenge 3 — Build time**: The full pipeline (4 weights × format conversion × ZIP packaging) takes significant time on a single runner. A future optimization could parallelize per-weight builds via a matrix strategy, but V1 runs them sequentially to keep the implementation simple
- **Challenge 4 — GITHUB_TOKEN permissions**: The release-creation step requires `contents: write` permission, which is broader than the read-only default. The workflow must declare this explicitly in the `permissions:` block to follow the principle of least privilege and pass GitHub's security audits
- **Challenge 5 — Fork isolation**: Each fork has its own release namespace, but artifact storage is per-repository. The workflow must ensure artifacts are uploaded using the **fork's** token, not the upstream's token, so the artifacts land in the correct namespace
- **Challenge 6 — Schema evolution**: If the schema evolves in a future version (for example, a new option is added), forks with old `config.json` files must still build. The wrapper must ignore unknown keys (already specified in FR-1 and FR-7) and warn about them
- **Challenge 7 — FontForge determinism**: FontForge's binary output is not perfectly byte-deterministic across runs (timestamps, build IDs embedded in the font). The Engineering Team should investigate setting `SOURCE_DATE_EPOCH` and other reproducibility flags to minimize variation, but perfect reproducibility is not a V1 requirement

## 9. Milestones & sequencing

### 9.1 Project estimate & Team composition

- **Size**: Medium (M) — 6-8 weeks end-to-end
- **Team composition** (roles per SDLC phase, sequential not parallel):
  - 1 Product Manager — Phase 1 (this PRD)
  - 1 Specification Architect — Phase 2
  - 1 Implementation Planner — Phase 3
  - 1 Senior Engineer — Phase 4 (implementation)
  - 1 Code Reviewer / QA — Phase 4 (testing & review)
  - 1 Documentation Architect — Phase 5
- **Total team size**: 5-6 contributors, most in sequence

### 9.2 Suggested phases

- **M1 — Specification (1 week)**: Specification Architect produces `/spec/` documents covering Docker base image upgrade, `configure.py` wrapper API, workflow file structure, and JSON Schema. Output: `docs/spec-*.md` artifacts. Gate: Clarification Checkpoint (`@ClarificationAnalyst`) must pass.
- **M2 — Implementation Planning (0.5 weeks)**: Planner Architect produces `/plan/` with phased task breakdown, dependencies, and risk mitigation. Output: `docs/plan-*.md` artifacts. Gates: Clarification Checkpoint + Consistency Check (`@ArtifactConsistencyChecker`).
- **M3 — Foundation: Container & Wrapper (2 weeks)**: Upgrade Docker base image; implement `configure.py` wrapper; define `config.schema.json`; local smoke tests.
- **M4 — Workflow & Build Integration (1.5 weeks)**: Implement `custom-build.yml` workflow; integrate with existing `Scripts/build.py`; validate output structure matches the manifest spec.
- **M5 — Release & Artifact Publishing (1 week)**: Integrate release creation; integrate artifact upload; generate `manifest.json`; compute checksums.
- **M6 — Documentation & Launch (1 week)**: Write `docs/CUSTOM-BUILD.md`; update `README.md`; create user tutorials; publish release announcement.
- **M7 — Post-Launch Monitoring (ongoing)**: Track SM-B1 through SM-B5; iterate based on user feedback; revisit the Non-Goals list quarterly to determine what can be moved to the Goals list in V2.

## 10. User stories & Acceptance Criteria

### 10.1 US-001: Trigger Custom Build via Form (No Config)

- **ID**: GH-001
- **Story**: As a **casual user (Casper)**, I want to **trigger a build using the GitHub Actions form with default values**, so that **I can get a baseline Fantasque Sans Mono build without editing any files**.
- **Priority**: P0
- **Acceptance criteria**:
  - [ ] Workflow file `.github/workflows/custom-build.yml` exists in the repository and is discoverable in the Actions tab
  - [ ] Workflow has a `workflow_dispatch` trigger with all four inputs (`large_line_height`, `no_loop_k`, `no_calt`, `use_hinted`) as optional with sensible defaults
  - [ ] Submitting the form with all defaults produces a successful build that publishes a Release tagged with a timestamp
  - [ ] Release title reads `Custom Build: Normal (default)` for the default-variant build
  - [ ] `.zip` artifact is downloadable from both the workflow run's "Artifacts" section and the auto-created Release
  - [ ] Median time from "Run workflow" click to artifact availability is ≤ 15 minutes
  - [ ] The workflow summary at the top of the run page shows a one-line success message
  - [ ] The `manifest.json` records `config_source: "defaults"` when the build is triggered via the form with no `config.json` overrides

### 10.2 US-002: Configure Custom Build via config.json

- **ID**: GH-002
- **Story**: As a **power user (Penny)**, I want to **declare my preferred variant options in a `config.json` file at the repository root**, so that **I have a version-controlled, declarative way to specify my build configuration**.
- **Priority**: P0
- **Acceptance criteria**:
  - [ ] `config.json` at the repository root is read by the wrapper before any form input is applied
  - [ ] The file accepts a flat JSON object with keys `LargeLineHeight`, `NoLoopK`, `NoCalt`, and `UseHinted`
  - [ ] A valid `config.json` with `{"LargeLineHeight": true, "NoCalt": true}` produces a build tagged `Custom Build: LargeLineHeight + NoCalt`
  - [ ] Committing a new `config.json` and re-triggering the workflow (without form changes) picks up the new values
  - [ ] The build log includes a line per option stating its source: `Loaded config.json: LargeLineHeight=true, NoCalt=true`
  - [ ] The `manifest.json` records `config_source: "config.json"` when the file is used

### 10.3 US-003: Form Input Overrides config.json

- **ID**: GH-003
- **Story**: As a **power user (Penny)**, I want to **override my committed `config.json` values with a one-off form input**, so that **I can experiment with variants without committing changes to my fork**.
- **Priority**: P0
- **Acceptance criteria**:
  - [ ] When both `config.json` and form inputs are provided, form values take precedence
  - [ ] Form input `large_line_height: true` overrides `LargeLineHeight: false` in `config.json`
  - [ ] Form input `no_calt: true` overrides `NoCalt: false` in `config.json`
  - [ ] Form input `use_hinted: false` overrides `UseHinted: true` in `config.json`
  - [ ] The build log explicitly states the precedence resolution: `Using form value (overrides config.json) for large_line_height`
  - [ ] No commit to the fork is required for the override to take effect
  - [ ] The `manifest.json` records `config_source: "form_override"` when an override occurs from form over `config.json` values

### 10.4 US-004: Default Fallback When No Config Exists

- **ID**: GH-004
- **Story**: As a **casual user (Casper)**, I want to **trigger a build even if I have not edited any files**, so that **I can get a working font without any setup**.
- **Priority**: P0
- **Acceptance criteria**:
  - [ ] Workflow succeeds when no `config.json` is present in the repository
  - [ ] Workflow succeeds when `config.json` is present but is an empty object `{}` — treated identically to no file present
  - [ ] Default values applied are: `LargeLineHeight=false`, `NoLoopK=false`, `NoCalt=false`, `UseHinted=true`
  - [ ] The build log reports whether `config.json` was found and which values were resolved (for example, `No config.json found, using build defaults` or `Loaded config.json (no overrides), using build defaults`). An empty `config.json` (`{}`) produces the same log output and behavior as a missing file
  - [ ] Resulting release title reflects the default variant: `Custom Build: Normal (default)`
  - [ ] The `manifest.json` records `config_source: "defaults"` (applies when no `config.json` is present, when the file is an empty object `{}`, or when the file contains no overrides and no form inputs are provided)

### 10.5 US-005: Configuration Schema Validation

- **ID**: GH-005
- **Story**: As a **power user (Penny)**, I want to **receive a clear error message if my `config.json` is invalid**, so that **I can fix the problem quickly without debugging cryptic build failures**.
- **Priority**: P1
- **Acceptance criteria**:
  - [ ] `config.schema.json` is a valid JSON Schema (draft-07) file at the repository root
  - [ ] Workflow validates `config.json` against the schema before invoking the build
  - [ ] An invalid `config.json` (for example, `{"LargeLineHeight": "yes"}` instead of boolean) fails the build with a non-zero exit code
  - [ ] Error message identifies the offending key and expected type: `Invalid config.json: 'LargeLineHeight' must be a boolean, got string`
  - [ ] The validation step is clearly named in the workflow summary so users can find it quickly (for example, "Validate config.json against schema")
  - [ ] Unknown keys in `config.json` produce a warning but do not fail the build (forward compatibility)
  - [ ] The schema enables auto-completion in editors that support JSON Schema (VS Code, JetBrains IDEs)

### 10.6 US-006: Download Build from GitHub Releases

- **ID**: GH-006
- **Story**: As a **casual user (Casper)**, I want to **download my build from a GitHub Release page**, so that **I have a stable, bookmarkable URL for the font bundle**.
- **Priority**: P0
- **Acceptance criteria**:
  - [ ] A new GitHub Release is created automatically on every successful build
  - [ ] Release tag follows the pattern `custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}` (UTC)
  - [ ] Release title is human-readable: for example, `Custom Build: NoLoopK + LargeLineHeight` or `Custom Build: NoCalt (unhinted)`
  - [ ] Release body (notes) includes: resolved options table, list of included font files with SHA-256 checksums, build timestamp, source commit SHA, and a link back to the workflow run
  - [ ] Both `.zip` and `.tar.gz` are attached as release assets
  - [ ] Release is published as a regular release (not a draft) and not marked as pre-release

### 10.7 US-007: Download Build from Workflow Artifacts

- **ID**: GH-007
- **Story**: As a **casual user (Casper)**, I want to **download my build directly from the workflow run's Artifacts section**, so that **I can get the file even before the Release is fully published**.
- **Priority**: P0
- **Acceptance criteria**:
  - [ ] The `.zip` and `.tar.gz` archives are uploaded as GitHub Actions Artifacts
  - [ ] Artifact names follow the pattern `fantasque-sans-custom-build-{run_id}-{run_attempt}`
  - [ ] Artifacts are retained for at least 90 days (default GitHub retention)
  - [ ] A successful download produces an archive that contains all 4 weights (Regular, Bold, Italic, Bold Italic) in TTF, OTF, WOFF, WOFF2, and SVG formats
  - [ ] Archive contents include `manifest.json`, the original `LICENSE.txt`, and a top-level `README.md`

### 10.8 US-008: Generate Manifest with Build Metadata

- **ID**: GH-008
- **Story**: As a **quality reviewer (Quinn)**, I want to **inspect a `manifest.json` in each build archive**, so that **I can verify what options were used, when the build ran, and verify file integrity via checksums**.
- **Priority**: P1
- **Acceptance criteria**:
  - [ ] `manifest.json` is generated by the wrapper and included in every archive
  - [ ] Manifest contains all fields specified in FR-8: `build_timestamp`, `resolved_options`, `font_files`, `toolchain_versions`, `source_commit`, `config_source`, `workflow_version`
  - [ ] SHA-256 checksums in the manifest match the actual file checksums (verified by re-hashing during CI)
  - [ ] Manifest is valid JSON (passes `python -m json.tool` or equivalent)
  - [ ] Manifest includes the SPDX license identifier `OFL-1.1` for license tracking

### 10.9 US-009: Existing Local Build Still Works

- **ID**: GH-009
- **Story**: As a **maintainer (Quinn)**, I want to **ensure that the existing `make`-based local build still works unchanged**, so that **no existing contributor workflow is broken by the new custom build system**.
- **Priority**: P2
- **Acceptance criteria**:
  - [ ] `make` at the repository root still produces `Variants/Normal/FantasqueSansMono.zip` exactly as before
  - [ ] The custom build system adds new files (`configure.py`, `custom-build.yml`, `Dockerfile`, `config.schema.json`) but does **not** modify `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`, or the root `Makefile` in V1 (the engine port is deferred to V2, see §8.3 Challenge 1); verifiable via `git diff Scripts/ Makefile` between pre-V1 and post-V1 commits showing zero changes to existing `Scripts/` files and `Makefile`
  - [ ] The custom build system adds new files but does not remove or rename any existing files
  - [ ] The legacy `Dockerfile` (if replaced) continues to support `docker build && docker run` as a documented alternative

### 10.10 US-010: Custom Build Runs in Isolated Environment

- **ID**: GH-010
- **Story**: As a **casual user (Casper)**, I want to **be confident that my build runs in a clean, isolated environment**, so that **I can trust the output regardless of what other builds have run**.
- **Priority**: P0
- **Acceptance criteria**:
  - [ ] Workflow uses `ubuntu-latest` (or a pinned LTS version) GitHub-hosted runner
  - [ ] Build runs inside a Docker container specified by the workflow
  - [ ] Container is built from a `Dockerfile` (or workflow-defined image) with all dependencies pre-installed
  - [ ] Container Stage 2 base image is Ubuntu 26.04 LTS (latest LTS as of V1 release); Stage 1 may use a legacy image only to provide a Python 2.7 runtime for `Scripts/build.py` (see §8.3 Challenge 1)
  - [ ] Each workflow run starts with a fresh container (no persistent state between runs)
  - [ ] No data from one user's build is visible to another user's build (cross-fork isolation)

### 10.11 US-011: Documentation for Casual Users

- **ID**: GH-011
- **Story**: As a **casual user (Casper)**, I want to **follow a beginner-friendly illustrated guide**, so that **I can complete my first build without prior GitHub Actions experience**.
- **Priority**: P1
- **Acceptance criteria**:
  - [ ] `docs/CUSTOM-BUILD.md` exists with a "Getting Started" section aimed at non-technical users
  - [ ] Guide includes annotated screenshots of: the Fork button, the Actions tab, the workflow_dispatch form, the Artifacts download page, and the Releases page
  - [ ] Guide has ≤ 5 numbered steps
  - [ ] Each step includes a one-sentence "Why" explanation
  - [ ] Guide links to a troubleshooting section for common errors (for example, "I forked but I don't see the workflow")

### 10.12 US-012: Documentation for Power Users

- **ID**: GH-012
- **Story**: As a **power user (Penny)**, I want to **reference detailed documentation of the `config.json` schema, override semantics, and CLI triggers**, so that **I can integrate the custom build into my team's workflow**.
- **Priority**: P1
- **Acceptance criteria**:
  - [ ] `docs/CUSTOM-BUILD.md` includes an "Advanced Configuration" section covering: full `config.json` schema reference, configuration precedence rules, and a `gh` CLI example for triggering the workflow
  - [ ] The schema reference includes each key's type, default, and effect on the output
  - [ ] At least one worked example is provided: a `config.json` → resulting release title mapping
  - [ ] The `gh workflow run` command is provided with all four form inputs as flags (`-f large_line_height=true -f no_loop_k=false -f no_calt=false -f use_hinted=true`)
  - [ ] A troubleshooting section covers: invalid config error messages, network timeouts, and rate limits

### 10.13 US-013: README Updated with Prominent Link

- **ID**: GH-013
- **Story**: As a **casual user (Casper)**, I want to **find the Custom Build link easily from the project README**, so that **I can discover the feature without browsing the repository**.
- **Priority**: P1
- **Acceptance criteria**:
  - [ ] `README.md` includes a new section titled "Custom Build" (or equivalent) near the top of the file, above the existing installation instructions
  - [ ] The section is a single paragraph (≤ 100 words) explaining what the custom build is and who it is for
  - [ ] A direct link to `docs/CUSTOM-BUILD.md` is included
  - [ ] A "Quick start" code block or link to the GitHub Actions UI is provided
  - [ ] The section uses a heading level consistent with the existing README structure

### 10.14 US-014: Build Error Produces User-Visible Failure

- **ID**: GH-014
- **Story**: As a **casual user (Casper)**, I want to **see a clear error message if the build fails**, so that **I know what went wrong and can take action**.
- **Priority**: P1
- **Acceptance criteria**:
  - [ ] Any non-zero exit from the build pipeline fails the workflow with a non-zero status
  - [ ] The workflow summary at the top of the run page includes a one-line statement: `Build failed at step [X]: [error message]`
  - [ ] The full build log is accessible via the standard "build" step in the Actions UI
  - [ ] Common failure modes (invalid `config.json`, network timeout, missing tool) produce specific, actionable messages
  - [ ] No silent failures: every failure is visible in the GitHub UI

### 10.15 US-015: Build Reproducibility and Audit Trail

- **ID**: GH-015
- **Story**: As a **quality reviewer (Quinn)**, I want to **be confident that a build is reproducible and traceable**, so that **I can verify that two builds of the same configuration produce functionally equivalent fonts and can identify the exact source commit that produced any given build**.
- **Priority**: P2
- **Acceptance criteria**:
  - [ ] The `manifest.json` includes the source commit SHA so reviewers can trace the build back to the exact code state
  - [ ] The same `config.json` + same source commit + same workflow version produces functionally equivalent TTF outputs (byte-identical is not guaranteed due to embedded timestamps; functional equivalence is verified by opening both files in FontForge)
  - [ ] The wrapper sets known reproducibility environment variables (for example, `SOURCE_DATE_EPOCH`) to minimize variation
  - [ ] Documentation explains what factors affect reproducibility (source commit, workflow version, toolchain versions, locale settings)

---

## Revision history

| Version | Date       | Author                      | Changes                                                                              |
| ------- | ---------- | --------------------------- | ------------------------------------------------------------------------------------ |
| 1.0     | 2026-07-23 | Product Manager PRD persona | Initial DRAFT based on `docs/discovery-draft-20260723-1058-custom-build-workflow.md` |
| 1.1     | 2026-07-23 | Product Manager PRD persona | Clarification Checkpoint update — 12 changes: removed spacing (deferred to V2), removed UG-5 (deferred to V2), added UseHinted to config.json, FR-4 multi-stage Docker, FR-6 tag format & release title, SM-T2 8→15 minutes, §8.1 on-the-fly build without registry, §8.3 Challenge 1 Python 2.7 mechanism via multi-stage Docker, §5.3 release accumulation mitigation, US-004 empty config ≡ missing file, cleaned up spacing references across all user stories & narrative |
| 1.2     | 2026-07-23 | Product Manager PRD persona | Team decision: switch to Ubuntu 26.04 LTS + Python 3.14; retain Scripts/build.py in Python 2.7 for Makefile compatibility; **subsequently corrected by Clarification 1.3 — the port of Scripts/fontbuilder.py and Scripts/features.py to Python 3.14 is deferred to V2**; update FR-3, FR-4, NG-9, §1.2, §6, §8.1, §8.3 Challenge 1 & 2, US-009 & US-010; ADR-0001 deferred to Spec/Plan phase |
| 1.3     | 2026-07-23 | Clarification Analyst        | Clarification checkpoint resolutions: deferred the port of Scripts/fontbuilder.py and Scripts/features.py to Python 3.14 to V2 (they remain Python 2.7 in V1, running in Stage 1 with Scripts/build.py); locked Stage 2 to Ubuntu 26.04 LTS + Python 3.14 for configure.py + packaging; added NG-11 (spacing deferred to V2); clarified config_source 'form' mapping (FR-3, FR-8); clarified FR-6 retry semantics vs FR-10; ADR-0001 marked *Superseded*, ADR-0002 required in Spec/Plan |

---

## Next SDLC phase

This PRD is **DRAFT** and pending stakeholder approval. Once approved, the next steps in the SDLC pipeline are:

1. **Clarification Checkpoint** (recurring) — open a new chat session and invoke:
   ```text
   @ClarificationAnalyst Analyze the approved PRD in @docs/prd-20260723-1130-custom-build-workflow.md for ambiguities, missing edge cases, and hidden assumptions.
   ```
2. **Artifact Consistency Audit** (recurring) — verify PRD ↔ Spec ↔ Plan traceability once the Spec and Plan are drafted
3. **Technical Specification** — open a new chat session and invoke `@SpecificationArchitect` to produce the `/spec/` documents
4. **Implementation Planning** — open a new chat session and invoke `@PlannerArchitect` to produce the `/plan/` documents
5. **Code Execution** — open a new chat session and invoke `@GodModeDev` to execute the approved plan

> **Reminder (per AGENTS.md Strict Session Isolation rule):** Each SDLC phase must be executed in a new chat session to prevent context mixing. Do not invoke `@SpecificationArchitect` or `@PlannerArchitect` in this same session.
