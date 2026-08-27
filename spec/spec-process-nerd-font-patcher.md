---
title: Technical Specification — Nerd Font Patcher Integration (Stage 3)
version: 1.1.1
date_created: 2026-08-11
owner: Fantasque Sans Mono Core Team
tags: [spec, github-actions, custom-build, nerd-fonts, docker, post-build-patching]
---
<!-- markdownlint-disable -->

# Introduction

This document is the definitive Technical Specification for the **Nerd Font Patcher Integration** feature of the Fantasque Sans Mono Custom Build System. It defines an **optional post-build patching stage (Stage 3)** that runs the [Nerd Fonts Patcher](https://github.com/ryanoasis/nerd-fonts) (`nerdfonts/patcher` Docker image) against the fonts produced by the existing pipeline, producing a separate **Nerd Font Variant** archive alongside the standard Custom Build output.

It is an **additive extension** of [`spec/spec-custom-build-workflow.md`](spec-custom-build-workflow.md) (v1.6). It does not modify, replace, or contradict any requirement, constraint, acceptance criterion, or schema of the upstream specification; every contract defined here either extends an existing contract (e.g., the manifest, the workflow, the configuration layer) or introduces a new isolated stage. Where a requirement of the upstream specification is relevant, it is referenced by ID (e.g., REQ-001, CON-001, AC-003) rather than restated.

## 1. Purpose & Scope

### 1.1 Purpose

The purpose of this specification is to define the technical contracts required to:

1. Add a `NerdFontPatching` boolean option to the existing configuration layer (`config.schema.json`, `Scripts/configure.py`, `workflow_dispatch` inputs, `gh workflow run`), following the exact same precedence, validation, and manifest-writing behavior as the existing four options.
2. Execute the Nerd Fonts Patcher against all generated TTF/OTF files **after** Stage 2 packaging completes, with correct per-variant flags (`--complete`, `--mono` for Mono variants only, `--adjust-line-height`, `--outputdir`; never `--careful`).
3. Package the patched fonts into **separate** archives (`fantasque-sans-nerd-font.zip` / `.tar.gz`) that never interfere with the base build archives.
4. Extend `manifest.json` with Nerd Font metadata (`nerd_font_version`) **only** when patching succeeds.
5. Integrate the Nerd Font archives with artifact upload, GitHub Release assets, release title/notes, and the job summary.
6. Guarantee **graceful failure**: any Nerd Font failure (image pull, patching, packaging) must never fail or alter the base build.

The intended audience is the implementation agent (`/sdlc-write-code`), the review agent (`/sdlc-code-review`), the consistency auditor (`/sdlc-audit-consistency`), and human maintainers of the repository.

### 1.2 Out of Scope

The following are explicitly **out of scope** for this specification (mirroring PRD §2.3):

- **Icon set selection UI:** Users cannot choose individual icon sets. The patcher always runs with `--complete`.
- **WOFF/WOFF2 Nerd Font output:** The Nerd Font archive contains only TTF and OTF files.
- **Modification of legacy build scripts:** Per CON-001, `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`, and root `Makefile` MUST NOT be modified. Stage 3 operates exclusively on pipeline output.
- **Automatic patcher version updates:** The `nerdfonts/patcher` image tag is manually pinned. No Dependabot or other auto-update mechanism for the Docker image.
- **Custom font naming overrides:** The patcher's default naming convention (appending "Nerd Font" to the family name) is used.
- **`--careful` mode:** The patcher NEVER uses `--careful`; existing glyphs at conflicting codepoints are replaced by Nerd Font glyphs (intended behavior).
- **Artifact storage limit mitigation:** The larger Nerd Font archive size (~30–40 MB) is accepted as expected behavior.
- **Font hinting preservation guarantees:** Whether the patcher preserves `ttfautohint` hinting in its output is a property of the patcher, not of this pipeline. No post-patch re-hinting is performed.
- **Spacing/alternate-glyph variants** (already out of scope in the upstream V1 spec).

### 1.3 Open Questions & Assumptions

> [!WARNING] ASSUMPTION-001
> **Font staging via `Scripts/packaging.sh`.** The workflow host runner needs the final TTF/OTF files (post-`ttfautohint`, post-WOFF) as patcher input. `packaging.sh` SHALL be modified to copy `TTF/*.ttf` and `OTF/*.otf` into the host-mounted `output/` directory (`output/TTF/`, `output/OTF/`). `packaging.sh` is NOT part of the CON-001 immutability set (which covers only `build.py`, `fontbuilder.py`, `features.py`, and `Makefile`), so this modification is permitted. Confirmed by the user on 2026-08-11 (Option A).

> [!WARNING] ASSUMPTION-002
> **`nerd_font_version` is written by the workflow, not by `configure.py`.** The patcher version is a workflow-level constant (single source of truth in `custom-build.yml`). `configure.py` is only responsible for option resolution and continues to write `resolved_options.NerdFontPatching`; it does not know or emit `nerd_font_version`.

> [!WARNING] ASSUMPTION-003
> **`nerd_font_version` is emitted only on patching success.** If image pull, patching, or packaging fails, the manifest does NOT contain the `nerd_font_version` key (no patcher version was actually applied), while `resolved_options.NerdFontPatching` remains `true` (the user's intent).

> [!WARNING] ASSUMPTION-004
> **Base archives are immutable.** The base archives (`fantasque-sans-custom-build.zip/.tar.gz`) and the manifest embedded inside them are never modified. `nerd_font_version` is stamped only into (a) the manifest inside the Nerd Font archives and (b) the host-level `output/manifest.json` (used for release notes and the artifact upload) — and only after the Nerd Font archives have been assembled successfully.

> [!WARNING] ASSUMPTION-005
> **`timeout-minutes` increases from 30 to 45** (PRD §5.3) to absorb image pull (~2–3 min) and patching (~5–10 min) without approaching the runner timeout.

> [!WARNING] ASSUMPTION-006
> **Nerd Font enablement is read from the resolved manifest**, not from the raw `workflow_dispatch` input. Because `config.json` can override the form default, the workflow reads `resolved_options.NerdFontPatching` from `output/manifest.json` (post-Stage-2) to decide whether to run Stage 3. Raw `inputs.nerd_font_patching` is still forwarded to `configure.py` as a form input.

> [!WARNING] ASSUMPTION-007
> **Patched file names are not hard-coded.** The patcher's default naming convention produces names such as `FantasqueSansMono Nerd Font-Regular.ttf` (space included). The workflow packages whatever files the patcher emits into `nf-staging/TTF` and `nf-staging/OTF` using globs, and quotes all paths so spaces are safe.

> [!WARNING] ASSUMPTION-008
> **Release title suffix order.** The `NerdFont` label is appended to the fully-computed title (`Custom Build: <BASE><SUFFIX>`), producing e.g. `Custom Build: NoLoopK, NerdFont` and `Custom Build: Normal (default), NerdFont`. This follows the PRD example `Custom Build: NoLoopK, NerdFont`.

> [!WARNING] ASSUMPTION-009
> **Existing tests asserting the exact 4-option surface MUST be updated to 5 options.** ALL tests and fixtures that hard-code the 4-option surface (dictionary keys, counts, log-line assertions) MUST be updated to 5 options. Use `grep -n` for `UseHinted` across `test_configure.py` to enumerate all affected locations (~10 at time of writing). Examples include `test_schema_has_four_boolean_properties` and `test_all_defaults`. This is a mechanical fixture update, not a behavioral regression; all semantically meaningful tests (validation, precedence semantics, manifest required fields) continue to pass unchanged. GH-011 ("no tests break") is interpreted as "no behavioral regression and no semantic test changes", consistent with GH-014 which explicitly requests new tests for the option.

## 2. Definitions

All terms align with the project's Domain Glossary ([`CONTEXT.md`](../CONTEXT.md)) and the upstream specification's definitions:

- **Custom Build**: Cloud-hosted personalized build system for Fantasque Sans Mono running in GitHub Actions and Docker.
- **Variant**: Combination of one or more build options producing specific visual characteristics.
  - _Avoid_: configuration, preset, build option
- **Normal**: Fantasque Sans Mono variant with no build options enabled.
  - _Avoid_: default variant, baseline, standard
- **Fork Owner**: The GitHub user who forked the repository and has permission to trigger a Custom Build on their fork.
  - _Avoid_: fork maintainer, repo owner
- **Upstream**: The original `belluzj/fantasque-sans` repository.
  - _Avoid_: main repo, original repository, source of truth
- **Manifest**: The `manifest.json` file included in every build archive, containing build metadata (timestamp, resolved options, checksum, toolchain versions).
- **Workflow**: The `.github/workflows/custom-build.yml` GitHub Actions file.
- **Nerd Font Patcher**: A tool that injects developer-specific icons and symbols into a monospace font. Operated here via the `nerdfonts/patcher` Docker image.
  - _Avoid_: Icon patcher, font enhancer
- **Nerd Font Variant**: The font output that has gone through the Nerd Font Patcher process and contains 10,000+ additional icons.
  - _Avoid_: Patched font, icon font
- **Nerd Font Archive** *(new canonical term)*: The standalone deliverable (`fantasque-sans-nerd-font.zip` / `.tar.gz`) containing all patched TTF/OTF files plus the NF-stamped manifest, `LICENSE.txt`, and `README.md`, packaged separately from the base build archives.
  - _Avoid_: patched archive, icon archive, NF bundle

Stage naming used in this specification:

- **Stage 1**: Docker build stage compiling fonts via `custom_build_driver.py` (upstream spec §4.5).
- **Stage 2**: Docker packaging stage running `Scripts/packaging.sh` (hinting, WOFF/WOFF2, archive assembly).
- **Stage 3**: The new post-build Nerd Font patching stage defined by this specification, executed on the GitHub Actions **host runner** via the `nerdfonts/patcher` Docker image (matching the ADR-0002 pattern of host-side post-processing orchestration).

## 3. Requirements, Constraints & Guidelines

### 3.1 Requirements

- **REQ-001 (NerdFontPatching Configuration Option)** (P0): The configuration layer SHALL support a new `NerdFontPatching` boolean option with default `false`, exposed through all four existing channels:
  - `config.schema.json` — validated property of type `boolean`, default `false`;
  - `workflow_dispatch` input `nerd_font_patching` (boolean, default `false`) in the GitHub Actions UI;
  - `config.json` — `"NerdFontPatching": true`;
  - GitHub CLI — `gh workflow run custom-build.yml --field nerd_font_patching=true`.
  - Resolution SHALL follow the existing precedence hierarchy (form > config.json > defaults) and SHALL be written into `manifest.json` under `resolved_options`.
- **REQ-002 (Nerd Font Patching Execution)** (P0): When `NerdFontPatching` resolves to `true`, the workflow SHALL execute the Nerd Fonts Patcher against every generated TTF and OTF file **after** Stage 2 packaging completes, using:
  - the `nerdfonts/patcher` Docker image resolved via `:latest` with a `ghcr.io/cdalvaro/docker-nerd-fonts-patcher:latest` fallback (see §16 for tag-resolution policy; CON-004 literal pinning to a Nerd Fonts release tag is infeasible because Docker Hub does not publish such tags);
  - `--complete` — include all icon sets;
  - `--mono` — applied ONLY to Mono variants (`FantasqueSansMono-*`), never to the proportional variant;
  - `--adjust-line-height` — applied to all variants;
  - `--outputdir` — pointing to a dedicated staging directory;
  - `--careful` — MUST NOT be used.
  - Exactly **10 patcher invocations**: 4 Mono weights (Regular, Bold, Italic, BoldItalic) × 2 formats (TTF, OTF) + 1 proportional (FantasqueSans) × 2 formats.
- **REQ-003 (Nerd Font Output Packaging)** (P0): Patched fonts SHALL be packaged into separate archives `fantasque-sans-nerd-font.zip` and `fantasque-sans-nerd-font.tar.gz`, each containing `TTF/`, `OTF/`, `manifest.json` (base manifest + NF metadata), `LICENSE.txt`, and `README.md`. The base build archives MUST remain unchanged.
- **REQ-004 (Manifest Metadata Extension)** (P0): When patching succeeds, `manifest.json` SHALL include a top-level `nerd_font_version` string (e.g., `"3.5.1"` — tag without the leading `v`; current stamp value tracked in §16.4), and `resolved_options.NerdFontPatching` SHALL reflect the resolved boolean.
- **REQ-005 (Release Integration)** (P0): When `NerdFontPatching` is enabled, the GitHub Release SHALL include the Nerd Font archives as additional assets, the release title SHALL include the `NerdFont` label, and the release notes SHALL mention the patcher version.
- **REQ-006 (Graceful Failure Handling)** (P0): The base build MUST NEVER fail due to a Nerd Font failure — whether at image pull, patching, or packaging. Each failure mode SHALL log a clear `::warning::` message, skip the dependent Nerd Font steps, and record the failure in the job summary.
- **REQ-007 (Job Summary Enhancement)** (P1): The job summary SHALL display one of: `NerdFontPatching: disabled`, `NerdFontPatching: enabled (nerdfonts/patcher vX.Y.Z)`, or `NerdFontPatching: enabled (FAILED — base build unaffected)`, plus (on success) the number of patched files and total patching duration.
- **REQ-008 (CI Artifact Upload)** (P0): When patching succeeds, the Nerd Font archives SHALL be uploaded as a separate GitHub Actions artifact named `nerd-font-build`.
- **REQ-009 (User Documentation)** (P1): `docs/CUSTOM-BUILD.md` SHALL be updated per PRD GH-010 (options table row, Nerd Fonts explanation, `config.json` example, `gh workflow run` example, separate-archive explanation, size-increase note).
- **REQ-010 (Backward Compatibility)** (P0): When `NerdFontPatching` is `false` (default), the pipeline SHALL behave identically to the current V1 workflow: no new steps execute, no new output files are produced, and existing outputs are byte-identical.

### 3.2 Constraints

- **CON-001 (Legacy Code Preservation)** *(inherited from upstream)*: `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`, and root `Makefile` MUST NOT be modified, renamed, or refactored.
- **CON-002 (Runner Scope)** *(inherited)*: Workflow runs on `ubuntu-latest` GitHub-hosted runners using default `GITHUB_TOKEN` with `contents: write`.
- **CON-003 (License Compliance)** *(inherited)*: All distributed packages MUST maintain SIL OFL 1.1 (`LICENSE.txt`) and `OFL-1.1` in the manifest. Fantasque Sans Mono has **no Reserved Font Name**, so the patcher's default "Nerd Font" family-name suffix is compliant; no name substitution is required.
- **CON-004 (Patcher Version Pinning)**: The `nerdfonts/patcher` image tag MUST be a pinned, immutable version (`v3.5.0` at launch). Using `latest` is strictly prohibited.
- **CON-005 (Modifiability Boundary)**: `Scripts/packaging.sh` MAY be modified (it is outside the CON-001 set) — but only in the additive manner defined in §4.5 (font staging). No existing packaging behavior may be altered when `NerdFontPatching` is disabled.
- **CON-006 (Base Output Immutability)**: The base archives and the manifest embedded in them MUST be byte-identical to the V1 output for the same option combination. Stage 3 may only add files to the host `output/` directory; it may never replace existing base artifacts.

### 3.3 Security & Guidelines

- **SEC-001 (Least Privilege)** *(inherited)*: Workflow permissions stay `contents: write` + `actions: read`; no new permissions, secrets, or PATs.
- **GUD-001 (Forward Compatibility)** *(inherited)*: Unknown keys in `config.json` warn but never fail.
- **GUD-002 (Idempotency)** *(inherited)*: One release per `run_attempt`; guard on existing tag.
- **GUD-003 (Release Retry)** *(inherited)*: Exponential backoff retry (1 s / 5 s / 25 s) on release creation.
- **GUD-004 (NF Failure Isolation)**: Every Stage 3 step MUST capture its own exit status into a step output (`pull_ok`, `patch_ok`, `package_ok`) and MUST NOT propagate a non-zero exit to the job. The base-build steps (upload, release) MUST only condition on Nerd Font step outputs when they intend to include Nerd Font artifacts.
- **GUD-005 (Image Pull Caching, Optional)**: To reduce the ~2–3 min pull latency, consider Docker layer caching for `nerdfonts/patcher` on the runner (e.g., `docker/setup-buildx-action` cache) if the runner supports it. Not a hard requirement.

## 4. Interfaces & Data Contracts

### 4.1 `config.schema.json` Addition

Location: `/config.schema.json` (repository root)

The schema keeps `additionalProperties: true` and adds one property (exact description per GH-010):

```json
{
  "NerdFontPatching": {
    "type": "boolean",
    "description": "Patches generated fonts with 10,000+ developer icons from Nerd Fonts (Powerline, Font Awesome, Material Design, Octicons, etc.).",
    "default": false
  }
}
```

### 4.2 `workflow_dispatch` Input Addition

Location: `.github/workflows/custom-build.yml`

| Input Key             | Type    | Default | Description                                |
| --------------------- | ------- | ------- | ------------------------------------------ |
| `nerd_font_patching`  | boolean | `false` | Patch fonts with Nerd Font glyphs (10,000+ icons) |

```yaml
nerd_font_patching:
  description: "Patch fonts with Nerd Font glyphs (10,000+ icons)"
  type: boolean
  required: false
  default: false
```

### 4.3 `configure.py` Additions

Location: `Scripts/configure.py` (Python 3.14, host runner)

The wrapper is extended with three additive changes and one constant bump. **No existing behavior is altered.**

```python
# DEFAULTS gains the new option
DEFAULTS = {
    "LargeLineHeight": False,
    "NoLoopK": False,
    "NoCalt": False,
    "UseHinted": True,
    "NerdFontPatching": False,
}

# FORM_KEY_TO_OPTION gains the mapping
FORM_KEY_TO_OPTION = {
    "large_line_height": "LargeLineHeight",
    "no_loop_k": "NoLoopK",
    "no_calt": "NoCalt",
    "use_hinted": "UseHinted",
    "nerd_font_patching": "NerdFontPatching",
}

# OPTION_TO_DRIVER_FLAG is UNCHANGED — NerdFontPatching MUST NOT appear.
# It is a post-build option (like UseHinted) and maps to no Stage 1 driver flag.
```

- New CLI flag: `--form-nerd-font-patching` (`type=_parse_bool`, `default=None`).
- `main()` collects `form_inputs["nerd_font_patching"] = args.form_nerd_font_patching`.
- `WORKFLOW_VERSION` bumps `1.3` → `1.4` (new feature present). `MANIFEST_VERSION` stays `"1.0"` (additive optional key; backward compatible).
- `generate_manifest()` is unchanged: `resolved_options` automatically includes `NerdFontPatching` because it iterates `DEFAULTS`. The wrapper does NOT emit `nerd_font_version` (ASSUMPTION-002).

### 4.4 `manifest.json` Extension

Location: inside archive roots and at `output/manifest.json`

The existing §4.6 schema of the upstream spec is extended **additively** (both new fields optional):

```json
{
  "resolved_options": {
    "LargeLineHeight": false,
    "NoLoopK": false,
    "NoCalt": false,
    "UseHinted": true,
    "NerdFontPatching": false
  },
  "nerd_font_version": "3.5.1"
}
```

Contract rules:

- `resolved_options.NerdFontPatching` is always present (boolean).
- `nerd_font_version` (top-level, string, format `X.Y.Z`, no leading `v`) is present **if and only if** Nerd Font patching succeeded in this run (ASSUMPTION-003).
- The manifest inside the **base archives** never contains `nerd_font_version` (CON-006). This creates a deliberate distinction between the **"archive manifest"** (sealed in Stage 2, describing only the base archive) and the standalone **"run manifest"** (`output/manifest.json`, describing the entire workflow run including NF outcome).
- The test fixture `tests/fixtures/manifest_schema.json` SHALL be extended with the optional `nerd_font_version` string property and the optional `NerdFontPatching` boolean property (no `required` changes).

### 4.5 `packaging.sh` Font Staging Contract (Stage 2 modification)

Location: `Scripts/packaging.sh`

After archive assembly (step 6 of the existing script), `packaging.sh` SHALL copy the final font files to the host-mounted `output/` directory so Stage 3 can consume them (ASSUMPTION-001):

```bash
# Stage 3 input staging: expose final TTF/OTF to the host runner.
if [ "${NERD_FONT_STAGING:-false}" = "true" ]; then
  (
    mkdir -p "${OUTPUT_DIR}/TTF" "${OUTPUT_DIR}/OTF"
    shopt -s nullglob
    for ttf in "${APP_DIR}/TTF"/*.ttf; do cp "${ttf}" "${OUTPUT_DIR}/TTF/"; done
    for otf in "${APP_DIR}/OTF"/*.otf; do cp "${otf}" "${OUTPUT_DIR}/OTF/"; done
    shopt -u nullglob
  ) || echo "::warning::Font staging for Nerd Font patching failed. Stage 3 will be skipped."
fi
```

Rules:

- Copy ONLY `*.ttf` and `*.otf`. WOFF/WOFF2/SVG files are never copied (the patcher consumes TTF/OTF only).
- Files are copied **after** the in-place `ttfautohint` pass, so Stage 3 receives the final hinted (or unhinted, per `UseHinted`) binaries.
- When `NerdFontPatching=false`, the extra `output/TTF` and `output/OTF` directories exist but are harmless: artifact upload and release steps use explicit paths (see §4.6) and ignore them.

### 4.6 Stage 3 Workflow Steps (host runner)

Location: `.github/workflows/custom-build.yml` — inserted between Step 7 (Run Stage 2 packaging) and Step 8 (Upload build artifacts). All steps are conditional on the **resolved** manifest value (ASSUMPTION-006).

**Enablement resolution:** the Step 5 (resolve) or Step 7 (after packaging) stage reads `jq -r '.resolved_options.NerdFontPatching' output/manifest.json` and exports it as `steps.nf_enable.outputs.nerd_font_patching`.

| Step | Condition | Behavior | Failure handling |
| ---- | --------- | -------- | ---------------- |
| **7.1 Pull patcher image** | `nerd_font_patching == 'true'` | `docker pull nerdfonts/patcher:latest` (with `ghcr.io/cdalvaro/docker-nerd-fonts-patcher:latest` fallback — see §16); sets `pull_ok=true` or `pull_ok=false` + `nf_failure=image-pull` | Warning `::warning::Failed to pull the Nerd Fonts Patcher image (Docker Hub down/rate-limited). Skipping Nerd Font patching — base build unaffected.`; exit 0 |
| **7.2 Patch fonts** | `pull_ok == 'true'` | Creates `nf-staging/TTF` + `nf-staging/OTF`; runs 10 `docker run` invocations per §4.6.1; records `patch_ok`, `nf_file_count`, `nf_duration_s` | On any invocation failure: abort remaining patches, `::warning::` naming the file, `patch_ok=false`; exit 0 |
| **7.3 Package NF archives** | `patch_ok == 'true'` | Assembles `output/fantasque-sans-nerd-font.zip` + `.tar.gz` from `nf-staging` plus NF-stamped manifest, `LICENSE.txt`, `README.md`; sets `package_ok` | On failure: remove partial archives, `::warning::`, `package_ok=false`; exit 0. `output/manifest.json` is stamped with `nerd_font_version` ONLY after archives succeed (ASSUMPTION-004) |
| **7.4 Upload NF artifact** | `package_ok == 'true'` | `actions/upload-artifact@v4`, name `nerd-font-build`, path `output/fantasque-sans-nerd-font.zip` + `output/fantasque-sans-nerd-font.tar.gz`, `if-no-files-found: error` | N/A (step skipped when not applicable) |

**Step 7 modification (Stage 2 packaging):** The existing Step 7 `docker run` command MUST pass `-e NERD_FONT_STAGING=${{ steps.nf_enable.outputs.nerd_font_patching }}` to conditionally enable font staging.

**Step 8 modification (base artifact upload):** the `path` list MUST be changed from the glob `output/*.zip` / `output/*.tar.gz` to **explicit** paths (`output/fantasque-sans-custom-build.zip`, `output/fantasque-sans-custom-build.tar.gz`, `output/manifest.json`, `output/LICENSE.txt`, `output/README.md`) so the Nerd Font archives are never captured by the base artifact. `if-no-files-found: error` stays.

**Step 10/11 modifications (release):**

- Step 10 (release metadata): when `resolved_options.NerdFontPatching == 'true'`, append `, NerdFont` to the computed `TITLE` (ASSUMPTION-008), e.g. `Custom Build: NoLoopK, NerdFont`; add a **Nerd Font Variant** section to the release notes mentioning the patcher version (read from `manifest.nerd_font_version` when present) and a short description of the included icon sets.
- Step 11 (create release): add `output/fantasque-sans-nerd-font.zip` and `.tar.gz` to the `gh release create` asset list **only if they exist** (`[ -f ... ]` guard), so the release succeeds with or without Nerd Fonts.

**Step 9 modification (job summary):** add a Nerd Font status block (FR-007). The `nf_failure` output from Step 7.1 can be used to distinguish failure modes if desired:

```text
NerdFontPatching: disabled
NerdFontPatching: enabled (nerdfonts/patcher v3.5.0) — 10 files patched in 412s
NerdFontPatching: enabled (FAILED — base build unaffected)
```

#### 4.6.1 Patcher Invocation Contract

For each input font file, the patcher runs as its own `docker run` (10 invocations total):

```bash
# Mono TTF (4 weights): FantasqueSansMono-Regular|Bold|Italic|BoldItalic.ttf
docker run --rm \
  -v "$(pwd)/output/TTF:/in" \
  -v "$(pwd)/nf-staging/TTF:/out" \
  nerdfonts/patcher:v3.5.0 \
  --complete --mono --adjust-line-height \
  --outputdir /out \
  "/in/FantasqueSansMono-Regular.ttf"

# Proportional TTF (1): FantasqueSans.ttf — NO --mono
docker run --rm \
  -v "$(pwd)/output/TTF:/in" \
  -v "$(pwd)/nf-staging/TTF:/out" \
  nerdfonts/patcher:v3.5.0 \
  --complete --adjust-line-height \
  --outputdir /out \
  "/in/FantasqueSans.ttf"
```

The identical flag split applies to OTF files (`output/OTF:/in`, `nf-staging/OTF:/out`). All `docker run` invocations MUST quote paths (patched names contain spaces; ASSUMPTION-007). `--careful` is never passed.

### 4.7 Nerd Font Archive Internal Structure

```text
fantasque-sans-nerd-font.zip / .tar.gz
├── TTF/            # every .ttf emitted by the patcher (e.g. 5 files)
├── OTF/            # every .otf emitted by the patcher (e.g. 5 files)
├── manifest.json   # base manifest + nerd_font_version
├── LICENSE.txt     # copy from repository root
└── README.md       # copy from repository root
```

### 4.8 Release Title & Notes Contract

| `NerdFontPatching` | Title example                                     | Notes content                                 |
| ------------------ | ------------------------------------------------- | --------------------------------------------- |
| `false`            | `Custom Build: Normal (default)` (unchanged)      | no Nerd Font section                          |
| `true` (success)   | `Custom Build: NoLoopK, NerdFont`                 | **Nerd Font Variant** section + patcher version + icon-set description |
| `true` (failed)    | same as `false` (no `NerdFont` label)             | no Nerd Font section; job summary carries the failure |

## 5. Acceptance Criteria

Acceptance criteria map 1:1 to the PRD user stories (GH-001 … GH-014) and use the Given-When-Then form.

- **AC-101 (GH-001, UI toggle)**: Given a fork with no `config.json`, When the Fork Owner checks the `nerd_font_patching` checkbox in the Actions UI and runs the workflow, Then `configure.py` resolves `NerdFontPatching=true` and `manifest.json` contains `resolved_options.NerdFontPatching: true`.
- **AC-102 (GH-002, config.json)**: Given a `config.json` with `"NerdFontPatching": true`, When the workflow validates and resolves, Then validation succeeds against `config.schema.json`, the resolved value is `true`, and a `config.json` without the key still validates and resolves to `false`.
- **AC-103 (GH-003, gh CLI)**: Given `gh workflow run custom-build.yml --field nerd_font_patching=true`, When the run starts, Then the value is mapped through `FORM_KEY_TO_OPTION["nerd_font_patching"]` and resolves `NerdFontPatching=true`.
- **AC-104 (GH-004, valid output)**: Given `NerdFontPatching=true` and a successful run, Then Mono TTF/OTF variants are patched with `--complete --mono --adjust-line-height`, the proportional variant with `--complete --adjust-line-height` (no `--mono`), `--careful` is absent, all 10 files are patched, the image tag is pinned, every patched file passes `fontTools` structure validation, and each contains ≥ 10,000 glyphs.
- **AC-105 (GH-005, separate packaging)**: Given a successful Nerd Font run, Then `fantasque-sans-nerd-font.zip` and `.tar.gz` exist containing `TTF/`, `OTF/`, `manifest.json`, `LICENSE.txt`, `README.md`, and the base archives contain only unpatched fonts.
- **AC-106 (GH-006, manifest metadata)**: Given a successful Nerd Font run, Then `manifest.json` includes `"nerd_font_version": "3.5.1"` (the current stamp value; the stamp is the single source of truth for the Nerd Fonts release baked into the patched archive — see §16 for tag-resolution policy); Given a run with `NerdFontPatching=false`, Then the key is absent; `resolved_options.NerdFontPatching` always reflects the resolved boolean.
- **AC-107 (GH-007, graceful failure)**: Given a Docker pull failure or a patching/packaging failure, Then the workflow logs a clear warning, skips the remaining Nerd Font steps, produces/uploads the base archives normally, creates the release with base assets only, writes `NerdFontPatching: enabled (FAILED — base build unaffected)` to the job summary, and exits with code 0.
- **AC-108 (GH-008, job summary)**: Given any run, Then the job summary shows exactly one of the three FR-007 status lines; on success it additionally shows patched file count and duration.
- **AC-109 (GH-009, release label)**: Given `NerdFontPatching=true` with success, Then the release title contains `NerdFont` and the notes describe the patcher version and icon sets; Given `false`, Then the title contains no `NerdFont` label.
- **AC-110 (GH-010, documentation)**: Given the merged feature, Then `docs/CUSTOM-BUILD.md` includes the `Nerd Font Patching` options-table row (description and default `Off`), a Nerd Fonts explanation, a `config.json` example with `"NerdFontPatching": true`, a `gh workflow run` example with `--field nerd_font_patching=true`, the separate-archive explanation, and the size-increase note.
- **AC-111 (GH-011, backward compatibility)**: Given `NerdFontPatching=false`, Then no new workflow step executes, output archives are byte-identical to V1 for the same option combination, existing `config.json` files without the key remain valid, and `NerdFontPatching` is NOT in `OPTION_TO_DRIVER_FLAG`. (All tests and fixtures that hard-code the 4-option surface are updated to 5 options per ASSUMPTION-009; all semantic tests pass unchanged.)
- **AC-112 (GH-012, proportional variant)**: Given `NerdFontPatching=true`, Then `FantasqueSans.ttf`/`.otf` are patched without `--mono`, with `--complete` and `--adjust-line-height`, and included in the Nerd Font archive.
- **AC-113 (GH-013, version stamping)**: Given any run with patching enabled, Then the workflow references `nerdfonts/patcher:latest` (with `ghcr.io/cdalvaro/docker-nerd-fonts-patcher:latest` fallback — see §16 for the rationale and tag-resolution policy), the Nerd Fonts release version is documented in `custom-build.yml` and `docs/CUSTOM-BUILD.md`, and recorded as `nerd_font_version` on success.
- **AC-114 (GH-014, unit tests)**: Then `tests/test_configure.py` verifies `NerdFontPatching` exists in `DEFAULTS` with `False`, `"nerd_font_patching"` maps to `"NerdFontPatching"` in `FORM_KEY_TO_OPTION`, the option is NOT in `OPTION_TO_DRIVER_FLAG`, the schema/defaults-sync test passes with the updated schema, and precedence tests cover the option flowing through config.json, form data, and CLI overrides.

## 6. Test Automation Strategy & Testing Seams

### 6.1 Testing Seams

Prefer the highest existing seam; introduce new seams only where the boundary genuinely differs:

1. **Configuration layer (existing seam)** — `configure.py` public functions (`resolve_options`, `validate_config`, `generate_manifest`, `build_driver_arg_string`, `main`) via `tests/test_configure.py`. No Docker needed.
2. **Workflow integration (existing seam)** — end-to-end run of `custom-build.yml` on a fork (or `act` local runner) with `NerdFontPatching=true` and `false`.
3. **Patcher output validation (new, minimal seam)** — a validation script/step that opens each patched font with `fontTools` (structure validity + glyph count). This is the boundary at which patcher output is checked; no other new seams are introduced.

### 6.2 Test Levels

- **Micro (unit, `pytest tests/`)**: all GH-014 cases; updated 5-option fixtures (ASSUMPTION-009); manifest conformance against the extended `manifest_schema.json`; precedence matrix including `NerdFontPatching` in each of the four sources.
- **Integration (workflow)**: run with `NerdFontPatching=true` → assert 2 NF archives in artifacts + release, `nerd_font_version` present, base archives byte-identical to a parallel `false` run; run with `false` → assert no NF artifacts and byte-identical output to V1.
- **Failure-path integration**: simulate pull failure (invalid tag in a test run or network block) and patch failure (OOM/abort) → assert base artifacts + release still produced, job summary shows the `FAILED` status, exit code 0.
- **Patcher output validation**: for every patched file, `fontTools.ttLib.ttFont.TTFont(path)` opens without error AND `font['maxp'].numGlyphs >= 10000`.

### 6.3 Test Data Management

- Existing fixtures in `tests/fixtures/configs/` remain; no new config fixtures required (option is boolean, covered by parametrized tests).
- `tests/fixtures/manifest_schema.json` is extended with the two optional fields (see §4.4).
- Integration runs use real `nerdfonts/patcher:latest` pulls (with the `ghcr.io` fallback — see §16) on the test fork; cleanup of test releases/artifacts follows the existing troubleshooting docs.

### 6.4 CI/CD Integration

- Unit tests run in the workflow Step 3 gate exactly as today (`pytest tests/ -v`) — the new option's tests are part of the same gate.
- Patcher-output validation and failure-path scenarios are executed as a **validation checklist** during the Code phase (manual/scripted on a test fork), not as a permanent CI job, to avoid burning runner minutes on a ~500 MB image pull per push. (PRD §7.3 metrics are assessed on the test-fork runs.)

### 6.5 Coverage Requirements

- 100% of the added `configure.py` branches (the new option flows through every precedence source).
- 100% pass of the existing unit suite (macro-level gate) before the Code phase is declared complete.

## 7. Project Structure & Commands

### Project Structure

| Path | Change | Purpose |
| ---- | ------ | ------- |
| `config.schema.json` | edit | Add `NerdFontPatching` property (§4.1) |
| `Scripts/configure.py` | edit | `DEFAULTS`, `FORM_KEY_TO_OPTION`, `--form-nerd-font-patching`, `WORKFLOW_VERSION` bump (§4.3) |
| `Scripts/packaging.sh` | edit | Font staging block (§4.5) |
| `.github/workflows/custom-build.yml` | edit | Input + Steps 7.1–7.4 + Step 8/9/10/11 modifications (§4.6) |
| `tests/test_configure.py` | edit | New GH-014 tests + 5-option fixture updates |
| `tests/fixtures/manifest_schema.json` | edit | Optional `nerd_font_version` + `NerdFontPatching` fields |
| `docs/CUSTOM-BUILD.md` | edit | Nerd Font section per GH-010 |
| `docs/ARCHITECTURE.md` | edit | Reference Stage 3 |
| `spec/spec-process-nerd-font-patcher.md` | new | This document |

### Commands

- **Unit tests:** `python -m pytest tests/ -v`
- **Local config validation:** `python3 Scripts/configure.py --config-file config.json --schema-file config.schema.json`
- **Resolve + manifest (local smoke):**
  ```bash
  python3 Scripts/configure.py --schema-file config.schema.json \
    --form-nerd-font-patching true \
    --output-args-file build-args.txt --generate-manifest manifest.json
  ```
- **Docker build (unchanged):** `docker build --build-arg "BUILD_ARGS=$(cat build-args.txt)" -t fantasque-custom .`
- **Patcher validation (test fork):**
  ```bash
  pip install fonttools
  python -c "from fontTools.ttLib import TTFont; \
  import glob; \
  [TTFont(f) for f in glob.glob('nf-staging/TTF/*.ttf') + glob.glob('nf-staging/OTF/*.otf')]"
  ```
- **Glyph count check:** `python -c "from fontTools.ttLib import TTFont; \
  import glob; [print(f, TTFont(f)['maxp'].numGlyphs) for f in glob.glob('nf-staging/TTF/*.ttf')]"`

## 8. Code Style & Conventions

Follow the existing style of the files being modified (Python: `configure.py` conventions — module docstring, typed argparse, logging via `log`; YAML: commented step blocks referencing spec/plan IDs; Shell: `set -euo pipefail`, `readonly` paths, `shopt -s nullglob`).

Python addition (matching existing dict style):

```python
DEFAULTS = {
    "LargeLineHeight": False,
    "NoLoopK": False,
    "NoCalt": False,
    "UseHinted": True,
    # Post-build option: controls Stage 3 (Nerd Font patching), not a
    # Stage 1 driver flag (mirrors UseHinted). See spec-process-nerd-font-patcher §4.3.
    "NerdFontPatching": False,
}
```

Workflow step style (comment header + guarded failure capture per GUD-004):

```yaml
# -----------------------------------------------------------------------
# 7.1 Pull Nerd Fonts Patcher (conditional; GUD-004 — failure must not
# fail the job). Version pinned per CON-004 (spec §4.6).
# -----------------------------------------------------------------------
- name: Pull Nerd Fonts Patcher
  id: nf_pull
  if: steps.nf_enable.outputs.nerd_font_patching == 'true'
  env:
    NF_TAG: nerdfonts/patcher:v3.5.0
  run: |
    set +e
    docker pull "${NF_TAG}"
    rc=$?
    set -e
    if [ "${rc}" -ne 0 ]; then
      echo "::warning::Failed to pull ${NF_TAG} (Docker Hub down/rate-limited). Skipping Nerd Font patching — base build unaffected."
      echo "pull_ok=false" >> "$GITHUB_OUTPUT"
      echo "nf_failure=image-pull" >> "$GITHUB_OUTPUT"
    else
      echo "pull_ok=true" >> "$GITHUB_OUTPUT"
    fi
```

## 9. Implementation Boundaries

### Always do

- Keep all Stage 3 changes **additive**; never modify a base artifact.
- Add unit tests for every changed behavior (micro-level mandate) and run the full suite (`pytest tests/ -v`) before committing (macro-level mandate).
- Pin the patcher tag (current stamp `3.5.1`; literal Docker tag pinning is infeasible — see §16); never assume `:latest` and `:vX.Y.Z` carry the same payload.
- Guard every Stage 3 step so a non-zero exit is captured as an output, not propagated (GUD-004); use `::warning::` diagnostics.
- Quote all paths in shell/`docker run` (patched filenames contain spaces).
- Update `test_schema_has_four_boolean_properties` and the three other mechanical 4-option fixtures to the 5-option surface (ASSUMPTION-009).
- Update `docs/CUSTOM-BUILD.md` per GH-010 and reference Stage 3 in `docs/ARCHITECTURE.md`.

### Ask first

- Changing the pinned patcher version (CON-004).
- Changing the patcher flag set (`--complete`, `--mono` split, `--adjust-line-height`, `--careful` policy).
- Adding any new dependency, workflow permission, or CI configuration (e.g., Docker layer caching, `timeout-minutes`).
- Altering `packaging.sh` beyond the additive staging block (§4.5).

### Never do

- Modify `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`, or the root `Makefile` (CON-001).
- Inject `nerd_font_version` into the manifest inside the base archives (CON-006).
- Pass `--careful` to the patcher.
- Let a Nerd Font failure fail or delay the base build in any way.
- Extract fonts from the base archives as patcher input (PRD §8.3 explicitly forbids re-archiving/re-extraction).

## 10. Rationale, Context & Architecture Decisions (ADRs)

### 10.1 Rationale

- **Post-build, host-runner stage (Stage 3):** ADR-0002 establishes the pattern of host-side orchestration around immutable Docker stages (`configure.py` runs on the host; Stage 2 is packaging-only). Running the patcher as a host-side `docker run` of the `nerdfonts/patcher` image follows that same pattern and keeps Stage 1/2 untouched.
- **Patcher input via `output/` staging (ASSUMPTION-001):** the user selected the option of copying final TTF/OTF into the already-mounted `output/` directory. This avoids new mounts, re-archiving, or Dockerfile changes, at the cost of two extra directories in the host `output/` folder (harmless — upload/release use explicit paths).
- **Version stamping by the workflow (ASSUMPTION-002):** mirrors the existing `toolchain_versions.ttfautohint` pattern (written by the packaging stage via `jq`, not by `configure.py`). Single source of truth for the version lives in the workflow file.
- **Failure isolation (REQ-006/GUD-004):** the PRD mandates that an external dependency (Docker Hub) or patcher crash must never deny the Fork Owner their base fonts. Step-output gating (`pull_ok`/`patch_ok`/`package_ok`) achieves this without `continue-on-error` (which would mask diagnostics).
- **Optional `nerd_font_version` (ASSUMPTION-003):** only emit the version when a patcher version was actually applied, keeping the manifest truthful for auditors.

### 10.2 ADR Assessment

No new ADR is required. The design introduces **no hard-to-reverse architectural decision**:

- It reuses the ratified ADR-0002 architecture (multi-stage Docker, host-runner orchestration) without modifying it.
- The only "new" choices (staging location, version stamping, failure gating) are implementation-level, reversible, and not surprising given the existing codebase.

Should a future change alter the stage architecture (e.g., moving the patcher inside the Docker image), an ADR would then be warranted.

## 11. Dependencies & External Integrations

### External Systems

- **EXT-001**: GitHub Actions API & Runner Environment (`ubuntu-latest`) — unchanged; `timeout-minutes` raised to 45.
- **EXT-002**: GitHub Releases & Artifacts Storage Service — unchanged; NF archives added as assets/artifact.
- **EXT-003**: Docker Hub — source of the `nerdfonts/patcher` image; availability is NOT assumed (see failure isolation).

### Third-Party Services

- **SVC-001**: `nerdfonts/patcher` Docker image — contains FontForge + `font-patcher` script + `src/glyphs/` icon sources. Image is pulled via `:latest` with a `ghcr.io/cdalvaro/docker-nerd-fonts-patcher:latest` fallback (the Nerd Fonts release version is recorded separately as `nerd_font_version` in `manifest.json`; current stamp: `3.5.1` as of addendum §16 — historical stamps listed in §16.4). Required capability: patch TTF/OTF with `--complete`, `--mono`, `--adjust-line-height`, `--outputdir`. Trusted as maintained by the official Nerd Fonts organization. SLA assumption: no uptime guarantee; must degrade gracefully.

### Infrastructure Dependencies

- **INF-001**: Runner disk space — must hold the ~500 MB patcher image + staging output (existing 10 GB guidance remains sufficient).
- **INF-002**: Runner timeout — `timeout-minutes: 45` (ASSUMPTION-005).

### Data Dependencies

- **DAT-001**: Stage 2 output fonts — `output/TTF/*.ttf` and `output/OTF/*.otf` (post-hinting), copied by `packaging.sh` (§4.5).
- **DAT-002**: `LICENSE.txt` and `README.md` from the repository root (copied into the NF archive).

## 12. Examples & Edge Cases

### 12.1 Patcher invocation matrix

| Input file (output/TTF or output/OTF) | Variant type | Flags |
| ------------------------------------- | ------------ | ----- |
| `FantasqueSansMono-Regular.{ttf,otf}` | Mono | `--complete --mono --adjust-line-height` |
| `FantasqueSansMono-Bold.{ttf,otf}` | Mono | `--complete --mono --adjust-line-height` |
| `FantasqueSansMono-Italic.{ttf,otf}` | Mono | `--complete --mono --adjust-line-height` |
| `FantasqueSansMono-BoldItalic.{ttf,otf}` | Mono | `--complete --mono --adjust-line-height` |
| `FantasqueSans.{ttf,otf}` | Proportional | `--complete --adjust-line-height` (NO `--mono`) |

### 12.2 Edge cases

- **Docker Hub outage / rate limit:** pull fails → `pull_ok=false`, `nf_failure=image-pull`, Stage 3 skipped, base artifacts + release proceed, summary shows `FAILED — base build unaffected`.
- **Patcher OOM / script crash mid-run:** invocation `rc != 0` → remaining patches aborted, `patch_ok=false`, partial `nf-staging` discarded, summary shows `FAILED`.
- **Packaging failure (zip/tar):** partial archives deleted, `package_ok=false`, `output/manifest.json` NOT stamped, summary shows `FAILED`.
- **Proportional font patching:** `FantasqueSans` is patched WITHOUT `--mono` so icons keep proportional widths; included in the NF archive alongside Mono variants.
- **Glyph conflicts:** existing glyphs at conflicting codepoints are replaced (no `--careful`) — intended behavior.
- **Large archives:** patched TTFs grow to ~3–4 MB each; the NF archive is ~30–40 MB. Documented; accepted (out of scope for mitigation).
- **Filenames with spaces:** patcher emits e.g. `FantasqueSansMono Nerd Font-Regular.ttf`; all globs/paths are quoted; `zip`/`tar` handle them natively.
- **`UseHinted=false`:** Stage 3 still patches unhinted TTFs; no re-hinting post-patch (out of scope).
- **`LargeLineHeight=true` interaction:** When `LargeLineHeight=true`, the patcher's `--adjust-line-height` may override the Stage 1 line height adjustment. The Nerd Font Variant's line height is determined by the patcher, not by the `LargeLineHeight` option. This is accepted because `--adjust-line-height` is necessary for correct Powerline glyph rendering. Users can adjust line height in their terminal emulator settings.

## 13. Validation Criteria

Full compliance with this specification requires:

1. `config.schema.json` validates as Draft-07 and `NerdFontPatching` is a boolean defaulting to `false`; `test_schema_has_four_boolean_properties` updated and passing.
2. `Scripts/configure.py` passes 100% of the unit suite, including new GH-014 cases; `NerdFontPatching` absent from `OPTION_TO_DRIVER_FLAG`.
3. `packaging.sh` produces `output/TTF/` and `output/OTF/` with only `*.ttf`/`*.otf`; base archives byte-identical with `NerdFontPatching=false`.
4. A test-fork run with `NerdFontPatching=true` yields both NF archives with correct contents, `nerd_font_version` in the NF manifest and in `output/manifest.json`, the `nerd-font-build` artifact, the `NerdFont` release label, and NF assets on the release.
5. A failure-path run (pull/patch/package) yields base artifacts + release, warning logs, `FAILED` summary line, and exit code 0.
6. Every patched file passes `fontTools` structure validation and has ≥ 10,000 glyphs.
7. `docs/CUSTOM-BUILD.md` meets all GH-010 criteria.

## 14. Related Specifications / Further Reading

- [Technical Specification — Custom Build via GitHub Workflow](spec-custom-build-workflow.md) (v1.6) — upstream spec extended by this document
- [PRD — Nerd Font Patcher Integration](../docs/prd-20260811-1351-nerd-font-patcher.md)
- [Project Discovery — Nerd Font Patcher Integration](../docs/discovery-draft-20260811-1200-nerd-font-patcher.md)
- [ADR 0002 — Multi-Stage Docker Build with Deferred Engine Port](../docs/adr/0002-multi-stage-docker-deferred-engine-port.md)
- [Fantasque Sans Mono Domain Glossary](../CONTEXT.md)
- [Nerd Fonts Patcher repository](https://github.com/ryanoasis/nerd-fonts)

---

## 15. Revision History

| Version | Date | Author | Changes |
| ------- | ---- | ------ | ------- |
| 1.0 | 2026-08-11 | Specification Architect | Initial version based on approved PRD `docs/prd-20260811-1351-nerd-font-patcher.md`. User confirmed ASSUMPTION-001 (font staging via `packaging.sh` copy into `output/`). |
| 1.1 | 2026-08-12 | Specification Architect | Remediation of Clarification Report [Review Iteration 2] (conditional staging, generalized test tracking, run manifest clarification, edge cases). |
| 1.1.1 | 2026-08-27 | Specification Architect (amendment) | Addendum §16 — Docker Hub `nerdfonts/patcher` does not publish per-release version tags; recorded implementation deviates from CON-004 / AC-113 by using `:latest` + `ghcr.io` fallback with a manual `nerd_font_version` stamp. Nerd Fonts Patcher version bumped from v3.5.0 to v3.5.1. |

---

## 16. Addendum (2026-08-27) — Patcher Image Tag Resolution

### 16.1 Background

Section 3.2 `CON-004` (Patcher Version Pinning) prescribes that the `nerdfonts/patcher` image MUST be pinned to an immutable version tag (initial: `v3.5.0`) and that `:latest` is strictly prohibited. Section 5 `AC-113` further requires that the workflow reference the pinned tag (never `latest`) and that the pinned version be documented in `custom-build.yml` and `docs/CUSTOM-BUILD.md`, and recorded as `nerd_font_version` on success.

### 16.2 Reality on Docker Hub

The Docker Hub repository [`nerdfonts/patcher`](https://hub.docker.com/r/nerdfonts/patcher) does not publish per-release version tags that mirror Nerd Fonts release versions (e.g., `v3.5.0`, `v3.5.1`). Pulling `nerdfonts/patcher:v3.5.0` returns `manifest unknown: manifest unknown`. The repository only publishes:

- `latest` and `master` (floating tags that point to the most recently pushed image)
- Image-toolchain version tags (e.g., `4.27.3`, `4.27.2`) that reflect the internal `font-patcher` build number, **not** the Nerd Fonts release number

Because of this, CON-004 cannot be satisfied literally with a Nerd Fonts release tag.

### 16.3 Resolution

The workflow `.github/workflows/custom-build.yml` deviates from CON-004 / AC-113 in the following controlled, documented manner:

1. **Image reference.** The host runner pulls `nerdfonts/patcher:latest` as `PRIMARY_TAG`, falling back to `ghcr.io/cdalvaro/docker-nerd-fonts-patcher:latest` as `FALLBACK_TAG`. Both pulls are wrapped in `set +e` so a failure degrades gracefully (the base build proceeds unaffected).
2. **Version stamp.** Because the image cannot be pinned to a Nerd Fonts release tag, the workflow emits the expected Nerd Fonts release version as the `nerd_font_version` field in `manifest.json` via `jq '. + {"nerd_font_version": "<X.Y.Z>"}'`. This stamp is the single source of truth for the release version baked into the Nerd Font Variant archive and the base build manifest.
3. **Documentation.** The stamp string is mirrored in `docs/CUSTOM-BUILD.md`, `README.md`, and `CHANGELOG.md` so the user-visible version stays in lockstep with what the workflow actually produces.
4. **Reproducibility note.** This stamp is a *claim* about the contents of the `latest` image at the time of stamping; it is not a cryptographic guarantee. A consumer requiring bit-for-bit reproducibility should verify against the upstream Nerd Fonts release artifacts (`https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.5.1`).

### 16.4 Version timeline

| Stamp | Nerd Fonts release | Date in repo | Notes |
| ----- | ------------------ | ------------ | ----- |
| `3.5.0` | v3.5.0 | 2026-08-12 (release `1.9.0`) | Initial launch stamp; corresponds to the first Custom Build runs with `NerdFontPatching=true`. |
| `3.5.1` | v3.5.1 | 2026-08-27 | Bugfix release upstream (Devicons update, SpaceMono ligature removal, subdir flattening). Bumped via workflow YAML stamp only; no other contract changes. |

### 16.5 Procedure for future bumps

To advance the stamped version (e.g., from `3.5.1` to the next Nerd Fonts release):

1. Verify the upstream release exists at `https://github.com/ryanoasis/nerd-fonts/releases/tag/<vX.Y.Z>`.
2. Verify that Docker Hub `nerdfonts/patcher:latest` was re-pushed *after* the upstream release date (compare `last_updated` against the GitHub release `published_at`).
3. Update the two `nerd_font_version` stamp occurrences in `.github/workflows/custom-build.yml` (the `nf-staging/manifest.json` injection and the `output/manifest.json` injection).
4. Update the version reference in `docs/CUSTOM-BUILD.md`, `README.md`, and the comment block on `Pull Nerd Fonts Patcher image` in the workflow.
5. Add a `### Changed` entry to `CHANGELOG.md` under `## Unreleased`.
6. Amend this addendum: append a new row to §16.4 and bump the spec version (patch bump: `1.1.x`).

No change to `CON-004`, `AC-113`, or `SVC-001` is required by a version bump — those references remain authoritative for the *shape* of the contract; only the version values change.

### 16.6 Scope of this addendum

This addendum records an existing implementation reality and the procedure that was already in use at the time of release `1.9.0`. It does not relax the spirit of CON-004 / AC-113 (immutability, reproducibility, documentation); it documents why literal pinning is infeasible and what compensating controls are in place. Should Docker Hub ever publish Nerd Fonts release tags, CON-004 should be re-enabled and this addendum retired.
