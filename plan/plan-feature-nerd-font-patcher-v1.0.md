---
goal: Nerd Font Patcher Integration — Add optional post-build patching stage to the Custom Build pipeline
version: 1.0
date_created: 2026-08-12
last_updated: 2026-08-12
owner: Fantasque Sans Mono Core Team
status: Completed
tags: [feature, github-actions, nerd-fonts, docker, post-build-patching]
---

<!-- markdownlint-disable -->

# Introduction

![Status: Completed](https://img.shields.io/badge/status-Completed-brightgreen)

This plan implements the **Nerd Font Patcher Integration** feature as defined in the approved Technical Specification `spec/spec-process-nerd-font-patcher.md` (v1.1) and PRD `docs/prd-20260811-1351-nerd-font-patcher.md` (v1.0).

The feature adds an **optional Stage 3** to the existing Custom Build pipeline. When `NerdFontPatching=true`, the workflow pulls the `nerdfonts/patcher:v3.5.0` Docker image, patches all 10 TTF/OTF font files with 10,000+ developer icons, packages them into separate archives (`fantasque-sans-nerd-font.zip`/`.tar.gz`), and integrates with GitHub Release assets, release title/notes, and job summary — all with graceful failure isolation ensuring the base build is never affected.

## 1. Requirements & Constraints

### Requirements (from Spec §3.1)

- **REQ-001**: `NerdFontPatching` boolean option (default `false`) across all 4 configuration channels (schema, workflow_dispatch, config.json, CLI), following existing precedence hierarchy.
- **REQ-002**: Execute Nerd Fonts Patcher against all 10 TTF/OTF files with correct per-variant flags (`--complete`, `--mono` for Mono only, `--adjust-line-height`, never `--careful`).
- **REQ-003**: Package patched fonts into separate `fantasque-sans-nerd-font.zip`/`.tar.gz` archives.
- **REQ-004**: Extend `manifest.json` with `nerd_font_version` (present only on patching success).
- **REQ-005**: Release integration — NF archives as release assets, `NerdFont` title label, patcher version in notes.
- **REQ-006**: Graceful failure handling — base build NEVER fails due to NF failure.
- **REQ-007**: Job summary shows 3-state NF status (disabled/enabled+success/enabled+FAILED).
- **REQ-008**: Separate CI artifact upload (`nerd-font-build`).
- **REQ-009**: User documentation update (`docs/CUSTOM-BUILD.md`).
- **REQ-010**: Backward compatibility — zero change when `NerdFontPatching=false`.

### Constraints (from Spec §3.2)

- **CON-001**: `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`, and `Makefile` MUST NOT be modified.
- **CON-002**: Workflow runs on `ubuntu-latest` with `contents: write`.
- **CON-003**: SIL OFL 1.1 license compliance. No Reserved Font Name — patcher naming is compliant.
- **CON-004**: Patcher image pinned to `v3.5.0`. Using `latest` is strictly prohibited.
- **CON-005**: `Scripts/packaging.sh` may be modified (outside CON-001 set), but only additively per Spec §4.5.
- **CON-006**: Base archives and their embedded manifest MUST remain byte-identical. NF metadata only in run manifest and NF archive manifest.

### Security (from Spec §3.3)

- **SEC-001**: No new permissions, secrets, or PATs.
- **GUD-004**: Every Stage 3 step captures exit status into step output; failures never propagate to the job.

## 2. Implementation Steps

> **EXECUTION DIRECTIVE FOR AI AGENTS:**
> You MUST execute this plan phase by phase. You MUST run the specific testing/verification task at the end of each phase. After a phase is tested, you **MUST STOP AND WAIT** for the user's explicit approval before proceeding to the next phase.

### Implementation Phase 1: Configuration Layer (Foundation)

- GOAL-001: Add `NerdFontPatching` boolean option to the configuration pipeline — schema, configure.py, CLI flag, unit tests, and manifest fixture — so all downstream workflow steps can consume the resolved value.

| Task | Description | Ref ID | AC Ref | Dep | Files | Completed | Date |
| ---- | ----------- | ------ | ------ | --- | ----- | --------- | ---- |
| TASK-001 | **Add `NerdFontPatching` property to `config.schema.json`**: Add `"NerdFontPatching": {"type": "boolean", "description": "Patches generated fonts with 10,000+ developer icons from Nerd Fonts (Powerline, Font Awesome, Material Design, Octicons, etc.).", "default": false}` to the `properties` object. `additionalProperties: true` stays unchanged. | REQ-001 | AC-101, AC-102 | - | 1 | [x] | 2026-08-12 |
| TASK-002 | **Extend `Scripts/configure.py` with `NerdFontPatching` support**: (a) Add `"NerdFontPatching": False` to `DEFAULTS` dict (with inline comment: `# Post-build option: controls Stage 3 (Nerd Font patching), not a Stage 1 driver flag (mirrors UseHinted). See spec-process-nerd-font-patcher §4.3.`). (b) Add `"nerd_font_patching": "NerdFontPatching"` to `FORM_KEY_TO_OPTION`. (c) Do NOT add to `OPTION_TO_DRIVER_FLAG` — this is a post-build option. (d) Add `--form-nerd-font-patching` argparse flag (`type=_parse_bool`, `default=None`). (e) Add `form_inputs["nerd_font_patching"] = args.form_nerd_font_patching` to `main()`. (f) Bump `WORKFLOW_VERSION` from `"1.3"` to `"1.4"`. `MANIFEST_VERSION` stays `"1.0"`. | REQ-001 | AC-101, AC-103, AC-111, AC-114 | TASK-001 | 1 | [x] | 2026-08-12 |
| TASK-003 | **Extend `tests/fixtures/manifest_schema.json`**: (a) Add `"NerdFontPatching": {"type": "boolean"}` to `resolved_options.properties`. (b) Add top-level optional property `"nerd_font_version": {"type": "string"}`. Neither is added to the `required` array. | REQ-004 | AC-106 | TASK-001 | 1 | [x] | 2026-08-12 |
| TASK-004 | **Update mechanical 4-option fixtures in `tests/test_configure.py` to 5 options**: (a) Rename `test_schema_has_four_boolean_properties` → `test_schema_has_five_boolean_properties` and update assertion count from 4 → 5. (b) Update `test_all_defaults` in `TestResolveOptions` to expect `NerdFontPatching: False` in resolved dict. (c) Update `test_emits_one_line_per_option` comment from "4 total" → "5 total" and assertion from 4 → 5. (d) Update `test_mixed_precedence_all_four_sources` and related docstrings to reference the 5-option surface. (e) Update any other hard-coded 4-option references found via `grep -n "four\|4" tests/test_configure.py`. | REQ-010 | AC-111, AC-114 | TASK-002 | 1 | [x] | 2026-08-12 |
| TASK-005 | **Add new GH-014 unit tests in `tests/test_configure.py`**: (a) `test_nerd_font_patching_in_defaults`: Assert `"NerdFontPatching"` in `DEFAULTS` with value `False`. (b) `test_nerd_font_patching_form_key_mapping`: Assert `FORM_KEY_TO_OPTION["nerd_font_patching"] == "NerdFontPatching"`. (c) `test_nerd_font_patching_not_in_driver_flags`: Assert `"NerdFontPatching" not in OPTION_TO_DRIVER_FLAG`. (d) `test_nerd_font_patching_precedence_config_json`: Provide `config.json` with `NerdFontPatching: true`, no form input → resolved is `true`. (e) `test_nerd_font_patching_precedence_form_override`: Form `true` overrides config.json `false`. (f) `test_nerd_font_patching_precedence_defaults`: No config, no form → defaults to `false`. (g) Verify `test_defaults_match_schema_defaults` passes (existing test, validates schema↔DEFAULTS sync). | REQ-001 | AC-114 | TASK-002, TASK-003, TASK-004 | 1 | [x] | 2026-08-12 |
| TASK-006 | **VERIFY**: Run `python -m pytest tests/ -v` from the repository root. All tests (existing + new) must pass with 0 failures. Verify: (a) test count increased (was 62, expect ~70+), (b) `test_schema_has_five_boolean_properties` passes, (c) `test_defaults_match_schema_defaults` passes (schema↔DEFAULTS sync), (d) `test_nerd_font_patching_not_in_driver_flags` passes, (e) `test_nerd_font_patching_precedence_*` tests pass. Run: `python3 Scripts/configure.py --schema-file config.schema.json --form-nerd-font-patching true --output-args-file /dev/null --generate-manifest /tmp/test_manifest.json` and verify `NerdFontPatching: true` in manifest. | - | - | TASK-005 | - | [x] | 2026-08-12 |
| TASK-007 | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 2. | - | - | TASK-006 | - | | |

---

### Implementation Phase 2a: Font Staging & Patcher Execution

- GOAL-002a: Add font staging in `packaging.sh`, wire the `nerd_font_patching` workflow input, resolve the enablement from the manifest, pull the patcher image, and execute all 10 patcher invocations — with full failure isolation at every step.

| Task | Description | Ref ID | AC Ref | Dep | Files | Completed | Date |
| ---- | ----------- | ------ | ------ | --- | ----- | --------- | ---- |
| TASK-008 | **Add font staging block to `Scripts/packaging.sh`** (Spec §4.5): After the archive assembly step (Step 6, around line 173), append a conditional font staging block: `if [ "${NERD_FONT_STAGING:-false}" = "true" ]; then ( mkdir -p "${OUTPUT_DIR}/TTF" "${OUTPUT_DIR}/OTF"; shopt -s nullglob; for ttf in "${APP_DIR}/TTF"/*.ttf; do cp "${ttf}" "${OUTPUT_DIR}/TTF/"; done; for otf in "${APP_DIR}/OTF"/*.otf; do cp "${otf}" "${OUTPUT_DIR}/OTF/"; done; shopt -u nullglob; ) || echo "::warning::Font staging for Nerd Font patching failed. Stage 3 will be skipped."; fi`. This copies only `*.ttf` and `*.otf` (post-hinting). Subshell error isolation ensures staging failure doesn't kill the packaging script. | REQ-002, CON-005 | AC-111 | TASK-007 | 1 | [x] | 2026-08-12 |
| TASK-009 | **Add `nerd_font_patching` workflow_dispatch input** to `.github/workflows/custom-build.yml` (Spec §4.2): Add input `nerd_font_patching` with `description: "Patch fonts with Nerd Font glyphs (10,000+ icons)"`, `type: boolean`, `required: false`, `default: false`. Position it after `use_hinted`. | REQ-001 | AC-101 | TASK-007 | 1 | [x] | 2026-08-12 |
| TASK-010 | **Pass `--form-nerd-font-patching` to `configure.py` in the Resolve step** (Step 6, ID `resolve`): Add `--form-nerd-font-patching '${{ inputs.nerd_font_patching }}'` to the `configure.py` invocation in the existing resolve step. | REQ-001 | AC-101, AC-103 | TASK-009 | 1 | [x] | 2026-08-12 |
| TASK-011 | **Add NF enablement resolution step** (new step after existing Step 7 / "Run Stage 2 packaging"): Read `jq -r '.resolved_options.NerdFontPatching' output/manifest.json` and export as `steps.nf_enable.outputs.nerd_font_patching` (ASSUMPTION-006 — read from resolved manifest, not raw input). Step ID: `nf_enable`. | REQ-002 | AC-111 | TASK-010 | 1 | [x] | 2026-08-12 |
| TASK-012 | **Pass `NERD_FONT_STAGING` env var to Stage 2 Docker run** (Spec §4.6): Modify existing Step 8 ("Run Stage 2 packaging") `docker run` command to include `-e NERD_FONT_STAGING=${{ steps.nf_enable.outputs.nerd_font_patching }}`. This activates the conditional staging block in `packaging.sh`. | REQ-002 | AC-111 | TASK-008, TASK-011 | 1 | [x] | 2026-08-12 |
| TASK-013 | **Update `timeout-minutes` from 30 to 45** in the workflow `jobs.build` section (ASSUMPTION-005, Spec §11 INF-002). | REQ-002 | - | TASK-009 | 1 | [x] | 2026-08-12 |
| TASK-014 | **Add Step 7.1 — Pull Nerd Fonts Patcher image** (Spec §4.6, §8): New step `nf_pull` with `if: steps.nf_enable.outputs.nerd_font_patching == 'true'`. Uses `set +e` / `set -e` pattern to capture `docker pull nerdfonts/patcher:v3.5.0` exit code. On success: `pull_ok=true`. On failure: `pull_ok=false`, `nf_failure=image-pull`, `::warning::Failed to pull nerdfonts/patcher:v3.5.0 (Docker Hub down/rate-limited). Skipping Nerd Font patching — base build unaffected.`. Pin version in `env: NF_TAG: nerdfonts/patcher:v3.5.0`. | REQ-002, REQ-006, CON-004, GUD-004 | AC-107, AC-113 | TASK-011 | 1 | [x] | 2026-08-12 |
| TASK-015 | **Add Step 7.2 — Patch fonts** (Spec §4.6, §4.6.1): New step `nf_patch` with `if: steps.nf_pull.outputs.pull_ok == 'true'`. Creates `nf-staging/TTF` + `nf-staging/OTF` directories. Runs 10 `docker run` invocations (wrapped in `timeout 15m docker run ...` to prevent workflow hangs): 4 Mono weights × 2 formats (TTF/OTF) with `--complete --mono --adjust-line-height`, plus 1 proportional × 2 formats with `--complete --adjust-line-height` (NO `--mono`). All paths quoted (patched filenames contain spaces). On any invocation failure (or timeout): abort remaining, `::warning::` naming the file, `patch_ok=false`. On all success: `patch_ok=true`, record `nf_file_count` (calculated dynamically via `find nf-staging -type f \| wc -l`) and `nf_duration_s`. `--careful` is NEVER passed. | REQ-002, REQ-006, GUD-004 | AC-104, AC-107, AC-112 | TASK-014 | 1 | [x] | 2026-08-12 |
| TASK-016 | **VERIFY**: (a) Verify `packaging.sh` font staging by running a local Docker build with `NERD_FONT_STAGING=true` and confirming `output/TTF/*.ttf` and `output/OTF/*.otf` exist post-Stage-2. (b) Push to test fork with `NerdFontPatching=true` and verify Steps 7.1-7.2 execute: patcher image pulls successfully, 10 patching invocations complete, `nf-staging/` directories are populated. (c) Verify graceful failure: push with an intentionally invalid patcher tag (e.g., `v0.0.0-invalid`) and confirm `pull_ok=false`, `::warning::` logged, base build unaffected. (d) Verify `NerdFontPatching=false` run produces zero Stage 3 steps (existing behavior intact). | - | - | TASK-015 | - | [x] | 2026-08-12 |
| TASK-017 | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 2b. | - | - | TASK-016 | - | [x] | 2026-08-12 |

---

### Implementation Phase 2b: NF Archive Packaging & Artifact Upload

- GOAL-002b: Package patched fonts into separate NF archives, stamp `nerd_font_version` in the run manifest (but NOT in the base archive manifest), upload as a separate CI artifact, and update the base artifact upload to use explicit paths.

| Task | Description | Ref ID | AC Ref | Dep | Files | Completed | Date |
| ---- | ----------- | ------ | ------ | --- | ----- | --------- | ---- |
| TASK-018 | **Add Step 7.3 — Package NF archives** (Spec §4.6, §4.7): New step `nf_package` with `if: steps.nf_patch.outputs.patch_ok == 'true'`. Assembles `output/fantasque-sans-nerd-font.zip` and `.tar.gz` from `nf-staging/` with internal structure: `TTF/`, `OTF/`, `manifest.json`, `LICENSE.txt`, `README.md`. The NF archive manifest is a copy of `output/manifest.json` with `nerd_font_version` injected via `jq '. + {"nerd_font_version": "3.5.0"}' output/manifest.json > nf-staging/manifest.json`. `LICENSE.txt` and `README.md` copied from repo root. On success: `package_ok=true`. On failure: remove partial archives (`rm -f output/fantasque-sans-nerd-font.zip output/fantasque-sans-nerd-font.tar.gz`), `::warning::`, `package_ok=false`. The host-level `output/manifest.json` is stamped with `nerd_font_version` ONLY after archives succeed (ASSUMPTION-004). | REQ-003, REQ-004, CON-006 | AC-105, AC-106 | TASK-017 | 1 | [x] | 2026-08-12 |
| TASK-019 | **Add Step 7.4 — Upload NF artifact** (Spec §4.6): New step with `if: steps.nf_package.outputs.package_ok == 'true'`. Uses `actions/upload-artifact@v4`, name `nerd-font-build`, path includes `output/fantasque-sans-nerd-font.zip` and `output/fantasque-sans-nerd-font.tar.gz`, `if-no-files-found: error`. | REQ-008 | AC-105 | TASK-018 | 1 | [x] | 2026-08-12 |
| TASK-020 | **Fix base artifact upload path** (Spec §4.6 "Step 8 modification"): Change the existing Upload build artifacts step's `path` from the glob pattern (`output/*.zip`, `output/*.tar.gz`, etc.) to **explicit** paths: `output/fantasque-sans-custom-build.zip`, `output/fantasque-sans-custom-build.tar.gz`, `output/manifest.json`, `output/LICENSE.txt`, `output/README.md`. This prevents the NF archives from being captured by the base artifact. | REQ-003, CON-006 | AC-105, AC-111 | TASK-017 | 1 | [x] | 2026-08-12 |
| TASK-021 | **VERIFY**: (a) Push to test fork with `NerdFontPatching=true` and verify: `fantasque-sans-nerd-font.zip` and `.tar.gz` exist in `output/`, each containing `TTF/`, `OTF/`, `manifest.json` (with `nerd_font_version`), `LICENSE.txt`, `README.md`. (b) Verify `nerd-font-build` artifact appears in Actions UI. (c) Verify `custom-build` artifact contains ONLY base files (no NF archives). (d) Verify `output/manifest.json` contains `nerd_font_version: "3.5.0"`. (e) Verify base archives' embedded manifests do NOT contain `nerd_font_version`. | - | - | TASK-020 | - | [x] | 2026-08-12 |
| TASK-022 | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 3. | - | - | TASK-021 | - | [x] | 2026-08-12 |

---

### Implementation Phase 3: Release Integration & Job Summary

- GOAL-003: Complete the release pipeline integration — append `NerdFont` label to release title, add Nerd Font Variant section to release notes, include NF archives as release assets (guarded by file existence), and display the 3-state NF status in the job summary with patched file count and duration.

| Task | Description | Ref ID | AC Ref | Dep | Files | Completed | Date |
| ---- | ----------- | ------ | ------ | --- | ----- | --------- | ---- |
| TASK-023 | **Modify Step 10 (release metadata)** to include NerdFont label (Spec §4.8): When `steps.nf_package.outputs.package_ok == 'true'`, append `, NerdFont` to the computed `TITLE` variable (ASSUMPTION-008). Example: `Custom Build: NoLoopK, NerdFont`. When `NerdFontPatching` is `false` or patching failed, title is unchanged. Add a **Nerd Font Variant** section to the release notes mentioning patcher version (read from `output/manifest.json` via `jq -r '.nerd_font_version // empty'`) and a short description of included icon sets (Powerline, Font Awesome, Material Design, Octicons, Codicons, Weather). | REQ-005 | AC-109 | TASK-022 | 1 | [x] | 2026-08-12 |
| TASK-024 | **Modify Step 11 (create release)** to include NF assets (Spec §4.6): Add `output/fantasque-sans-nerd-font.zip` and `.tar.gz` to the `gh release create` asset list, guarded by `[ -f ... ]` checks so the release succeeds with or without NF archives. | REQ-005 | AC-105, AC-109 | TASK-023 | 1 | [x] | 2026-08-12 |
| TASK-025 | **Modify Step 9 (job summary)** to include NF status block (Spec §4.6, REQ-007): Add a Nerd Font status block that shows exactly one of: (a) `NerdFontPatching: disabled` when `nf_enable` is `false`; (b) `NerdFontPatching: enabled (nerdfonts/patcher v3.5.0) — N files patched in Xs` when `package_ok == 'true'` (using dynamically calculated `nf_file_count` and `nf_duration_s` from Step 7.2); (c) `NerdFontPatching: enabled (FAILED — base build unaffected)` when enabled but any step failed. | REQ-007 | AC-107, AC-108 | TASK-022 | 1 | [x] | 2026-08-12 |
| TASK-026 | **VERIFY**: (a) Push to test fork with `NerdFontPatching=true` + other options (e.g., `NoLoopK=true`) and verify: release title contains `Custom Build: NoLoopK, NerdFont`, release notes contain Nerd Font Variant section with patcher version, release assets include both NF archives AND both base archives. (b) Verify `NerdFontPatching=false` run: release title has no `NerdFont` label, no NF assets on release, job summary shows `NerdFontPatching: disabled`. (c) Verify failure-path run (invalid tag): release title has no `NerdFont`, job summary shows `FAILED — base build unaffected`, base build release assets still present. | - | - | TASK-025 | - | [x] | 2026-08-12 |
| TASK-027 | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 4. | - | - | TASK-026 | - | [x] | 2026-08-12 |

---

### Implementation Phase 4: Documentation & End-to-End Validation

- GOAL-004: Complete user-facing documentation, update architecture reference, and perform the comprehensive end-to-end validation checklist confirming all 14 acceptance criteria are met.

| Task | Description | Ref ID | AC Ref | Dep | Files | Completed | Date |
| ---- | ----------- | ------ | ------ | --- | ----- | --------- | ---- |
| TASK-028 | **Update `docs/CUSTOM-BUILD.md`** per GH-010 (Spec §4.6, REQ-009): (a) Add `Nerd Font Patching` row to the Form Input & Default table: Input=`nerd_font_patching`, Default=`off`, Effect="Patches generated fonts with 10,000+ developer icons from Nerd Fonts (Powerline, Font Awesome, Material Design, Octicons, etc.). Output is packaged in a separate archive." (b) Add a **Nerd Fonts** subsection explaining what Nerd Fonts are, what icon sets are included (`--complete`), the separate archive concept, and the expected file size increase (~30–40 MB). (c) Add `config.json` example with `"NerdFontPatching": true`. (d) Add `gh workflow run` example with `--field nerd_font_patching=true`. (e) Update the release title suffix table with the `NerdFont` label row. | REQ-009 | AC-110 | TASK-027 | 1 | [x] | 2026-08-12 |
| TASK-029 | **Update `docs/ARCHITECTURE.md`** to reference Stage 3 (Spec §7): (a) In the High-Level Architecture section, add Stage 3 to the containerization layer description: `Stage 3: nerdfonts/patcher (host-runner docker run, optional NF patching)`. (b) In the Data Flow section, add a Stage 3 block describing the Nerd Font patching pipeline. (c) In the Directory Purposes section, note that `nf-staging/` is a transient workspace used during Stage 3 NF patching. (d) Update the Mermaid workflow diagram to include the Stage 3 conditional branch. | REQ-009 | AC-110 | TASK-027 | 1 | [x] | 2026-08-12 |
| TASK-030 | **End-to-end validation checklist** (Spec §13): Execute the following validation runs on a test fork and confirm: (1) `config.schema.json` validates as Draft-07 and `NerdFontPatching` is boolean defaulting to `false`. (2) `Scripts/configure.py` passes 100% of unit suite (`pytest tests/ -v`). (3) `packaging.sh` produces `output/TTF/` and `output/OTF/` with `NerdFontPatching=true`; base archives byte-identical with `NerdFontPatching=false`. (4) Test-fork run with `NerdFontPatching=true` yields both NF archives with correct contents, `nerd_font_version` in manifest, `nerd-font-build` artifact, `NerdFont` release label, and NF assets on the release. (5) Failure-path run yields base artifacts + release, warning logs, `FAILED` summary line, exit code 0. (6) Every patched file passes `fontTools` validation and has ≥10,000 glyphs. (7) `docs/CUSTOM-BUILD.md` meets all GH-010 criteria. | - | AC-101 through AC-114 | TASK-028, TASK-029 | - | [x] | 2026-08-12 |
| TASK-031 | **Run full unit test suite** to confirm macro-level gate: `python -m pytest tests/ -v`. All tests MUST pass with 0 failures. | - | AC-111, AC-114 | TASK-030 | - | [x] | 2026-08-12 |
| TASK-032 | **APPROVAL**: Final user sign-off. Feature is complete. | - | - | TASK-031 | - | [x] | 2026-08-12 |

## 3. Alternatives

- **ALT-001: Integrate patcher inside Dockerfile (as a Docker build stage)**: Rejected. ADR-0002 establishes the pattern of host-side orchestration around immutable Docker stages. Stage 3 follows this pattern by running `docker run` on the host runner. Embedding the patcher inside the Dockerfile would couple the patcher version to the Docker image build, complicate failure isolation, and break the host-runner orchestration pattern.
- **ALT-002: Extract fonts from base archives as patcher input**: Rejected per PRD §8.3 — "The workflow must not rely on re-archiving or re-extracting the base build archives." The chosen approach copies fonts from the Stage 2 working directory via `packaging.sh` staging (ASSUMPTION-001).
- **ALT-003: Run `configure.py` to emit `nerd_font_version`**: Rejected per ASSUMPTION-002. `nerd_font_version` is a workflow-level constant (single source of truth in `custom-build.yml`), stamped via `jq` post-patching. This mirrors the existing `toolchain_versions.ttfautohint` pattern.
- **ALT-004: Use `continue-on-error: true` for failure isolation**: Rejected per GUD-004. `continue-on-error` masks diagnostics and prevents downstream `if` conditions from distinguishing success/failure. The chosen `set +e` / exit-code capture pattern provides explicit step outputs (`pull_ok`, `patch_ok`, `package_ok`) for precise conditional logic.

## 4. Dependencies

- **DEP-001**: `nerdfonts/patcher:v3.5.0` Docker image from Docker Hub (SVC-001). ~500 MB. Availability NOT assumed — graceful degradation on pull failure.
- **DEP-002**: `fontTools` Python package (for patcher output validation in TASK-030 only, not a runtime dependency). Install via `pip install fonttools` during validation.
- **DEP-003**: `jq` CLI tool — already available on `ubuntu-latest` runners and inside the Stage 2 Docker container. Used for manifest stamping.
- **DEP-004**: `actions/upload-artifact@v4` GitHub Action — already in use; a second invocation added for the `nerd-font-build` artifact.
- **DEP-005**: Stage 2 output (post-hinting TTF/OTF files in `output/TTF/`, `output/OTF/`) — produced by `packaging.sh` font staging (TASK-008).

## 5. Files

| ID | File | Change Type | Phase | Purpose |
| -- | ---- | ----------- | ----- | ------- |
| FILE-001 | `config.schema.json` | edit | 1 | Add `NerdFontPatching` boolean property |
| FILE-002 | `Scripts/configure.py` | edit | 1 | `DEFAULTS`, `FORM_KEY_TO_OPTION`, `--form-nerd-font-patching`, `WORKFLOW_VERSION` bump |
| FILE-003 | `tests/fixtures/manifest_schema.json` | edit | 1 | Optional `nerd_font_version` + `NerdFontPatching` fields |
| FILE-004 | `tests/test_configure.py` | edit | 1 | 5-option fixture updates + new GH-014 unit tests |
| FILE-005 | `Scripts/packaging.sh` | edit | 2a | Font staging block (conditional copy of TTF/OTF to `output/`) |
| FILE-006 | `.github/workflows/custom-build.yml` | edit | 2a, 2b, 3 | `workflow_dispatch` input, timeout, NF enable resolution, Steps 7.1-7.4, Step 8 path fix, Step 9 summary, Steps 10-11 release |
| FILE-007 | `docs/CUSTOM-BUILD.md` | edit | 4 | Nerd Font options table row, explanation, examples, size note |
| FILE-008 | `docs/ARCHITECTURE.md` | edit | 4 | Stage 3 reference in architecture overview |

## 6. Testing

### Micro-Level (Per-Change Unit Tests)

- **TEST-001**: All `test_configure.py` GH-014 tests pass — `NerdFontPatching` in DEFAULTS, FORM_KEY_TO_OPTION mapping, NOT in OPTION_TO_DRIVER_FLAG, precedence (3 sources), schema sync.
- **TEST-002**: All mechanical 4→5 option fixture updates pass — `test_schema_has_five_boolean_properties`, `test_all_defaults`, `test_emits_one_line_per_option`.
- **TEST-003**: Manifest schema conformance — `test_conforms_to_spec_4_6_schema` passes with extended `manifest_schema.json`.

### Macro-Level (Full Suite Gate)

- **TEST-004**: `python -m pytest tests/ -v` — ALL tests pass with 0 failures before each phase is declared complete.

### Integration (Workflow-Level)

- **TEST-005**: Test-fork run with `NerdFontPatching=true` → 2 NF archives in artifacts + release, `nerd_font_version` present, base archives byte-identical to `false` run.
- **TEST-006**: Test-fork run with `NerdFontPatching=false` → no NF artifacts, byte-identical output to V1.
- **TEST-007**: Failure-path test (invalid patcher tag) → base artifacts + release produced, `FAILED` summary, exit code 0.
- **TEST-008**: Patcher output validation — every patched file: `fontTools.ttLib.TTFont(path)` opens without error AND `font['maxp'].numGlyphs >= 10000`.

## 7. Risks & Assumptions

### Risks

- **RISK-001 (Docker Hub availability)**: Docker Hub may be down or rate-limit pulls during CI. **Mitigation**: Graceful failure isolation (REQ-006/GUD-004); base build always proceeds. **Impact**: Medium. **Tasks affected**: TASK-014, TASK-015.
- **RISK-002 (Patcher version compatibility)**: `nerdfonts/patcher:v3.5.0` may have undocumented breaking changes or OOM on GH runner. **Mitigation**: Explicit version pinning (CON-004); subshell error capture; manual test-fork validation. **Impact**: Low. **Tasks affected**: TASK-015.
- **RISK-003 (Patched filename spaces)**: Patcher emits filenames with spaces (e.g., `FantasqueSansMono Nerd Font-Regular.ttf`). **Mitigation**: All globs and paths are quoted; validated in TASK-016. **Impact**: Low.
- **RISK-004 (Archive size increase)**: NF archives are ~30–40 MB vs ~2–3 MB for base. **Mitigation**: Documented in CUSTOM-BUILD.md; accepted as expected behavior (out of scope for mitigation per PRD §2.3). **Impact**: Low.

### Assumptions (Extracted from Spec §1.3)

- **ASSUMPTION-001**: Font staging via `packaging.sh` — `packaging.sh` copies TTF/OTF to host-mounted `output/` directory. Confirmed by user on 2026-08-11 (Option A). **Tasks affected**: TASK-008, TASK-012. **Risk**: Low (confirmed).
- **ASSUMPTION-002**: `nerd_font_version` written by workflow via `jq`, not by `configure.py`. **Tasks affected**: TASK-018. **Risk**: Low.
- **ASSUMPTION-003**: `nerd_font_version` emitted only on patching success. **Tasks affected**: TASK-018. **Risk**: Low.
- **ASSUMPTION-004**: Base archives are immutable — NF metadata only in run manifest and NF archive manifest. **Tasks affected**: TASK-018, TASK-020. **Risk**: Low.
- **ASSUMPTION-005**: `timeout-minutes` increases from 30 to 45. **Tasks affected**: TASK-013. **Risk**: Low.
- **ASSUMPTION-006**: NF enablement read from resolved manifest, not raw input. **Tasks affected**: TASK-011. **Risk**: Low.
- **ASSUMPTION-007**: Patched file names are not hard-coded; use globs with quoted paths. **Tasks affected**: TASK-015, TASK-018. **Risk**: Low.
- **ASSUMPTION-008**: Release title suffix order — `NerdFont` appended after all base labels. **Tasks affected**: TASK-023. **Risk**: Low.
- **ASSUMPTION-009**: Existing tests with 4-option surface updated to 5 options. **Tasks affected**: TASK-004. **Risk**: Low.

## 8. Related Specifications / Further Reading

- [Technical Specification — Nerd Font Patcher Integration](../spec/spec-process-nerd-font-patcher.md) (v1.1)
- [PRD — Nerd Font Patcher Integration](../docs/prd-20260811-1351-nerd-font-patcher.md) (v1.0)
- [Technical Specification — Custom Build via GitHub Workflow](../spec/spec-custom-build-workflow.md) (v1.6)
- [ADR 0002 — Multi-Stage Docker Build with Deferred Engine Port](../docs/adr/0002-multi-stage-docker-deferred-engine-port.md)
- [Fantasque Sans Mono Domain Glossary](../CONTEXT.md)
- [Nerd Fonts Patcher repository](https://github.com/ryanoasis/nerd-fonts)

## 9. Rollback / Recovery Plan

### Phase 1 (Configuration Layer)

1. `git revert` the commits touching `config.schema.json`, `Scripts/configure.py`, `tests/test_configure.py`, and `tests/fixtures/manifest_schema.json`.
2. Run `python -m pytest tests/ -v` to confirm all original tests pass.
3. No runtime or CI impact — configuration changes are pure code.

### Phase 2-3 (Workflow / Packaging / Release)

1. `git revert` all commits touching `.github/workflows/custom-build.yml` and `Scripts/packaging.sh`.
2. The workflow reverts to V1 behavior: no Stage 3 steps, no font staging, no NF archives, original glob paths in artifact upload, `timeout-minutes: 30`.
3. Push to trigger a test run confirming the V1 pipeline works identically.

### Phase 4 (Documentation)

1. `git revert` commits touching `docs/CUSTOM-BUILD.md` and `docs/ARCHITECTURE.md`.
2. No runtime impact — documentation only.

### Emergency Rollback (All Phases)

1. `git revert --no-commit HEAD~N..HEAD` (where N = number of feature commits).
2. `git commit -m "Revert: Nerd Font Patcher Integration"`.
3. Push to `main`. The next Custom Build run will use the reverted V1 pipeline.
4. Any existing GitHub Releases with NF assets are unaffected (GitHub Release assets are immutable once published).
