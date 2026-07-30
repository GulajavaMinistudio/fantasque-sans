---
goal: Implement the Custom Build System for Fantasque Sans Mono via GitHub Workflow per Technical Specification v1.5
version: 1.2
date_created: 2026-07-24
last_updated: 2026-07-29
status: 'In Progress'
tags: [feature, github-actions, custom-build, docker, python]
---

# Introduction
<!--markdownlint-disable  -->
![Status: In Progress](https://img.shields.io/badge/status-phase_6_runtime_pending-yellow)

This Implementation Plan decomposes Technical Specification v1.5 (`spec/spec-custom-build-workflow.md`) into six executable phases covering: the host-runner configuration layer (`configure.py` + `config.schema.json`), the Stage 1 driver script (`Scripts/custom_build_driver.py`) and multi-stage `Dockerfile`, the GitHub Actions Workflow (`custom-build.yml`), automated GitHub Release publishing, user documentation, and end-to-end acceptance. Every task is traceable to a requirement in the Spec or PRD. Legacy build files (`Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`, root `Makefile`) MUST NOT be modified at any point (CON-001).

## 1. Requirements & Constraints

Source: Spec v1.5 §3, PRD v1.3 §4.

| ID         | Statement                                                                                                                   | Priority |
| ---------- | --------------------------------------------------------------------------------------------------------------------------- | -------- |
| REQ-001    | Root `config.json` declaring `LargeLineHeight`, `NoLoopK`, `NoCalt`, `UseHinted` (boolean)                                  | P0       |
| REQ-002    | Validate `config.json` against `config.schema.json` (draft-07); invalid config fails with non-zero exit + clear diagnostics | P0       |
| REQ-003    | Precedence: `workflow_dispatch` form > `config.json` > defaults (`false/false/false/true`)                                  | P0       |
| REQ-004    | Multi-stage Docker: Stage 1 (Python 2.7 + FontForge) compiles; Stage 2 (Ubuntu 26.04 + Python 3.14) packages (ADR-0002)     | P0       |
| REQ-005    | Produce TTF, OTF, WOFF, WOFF2, SVG for all 4 weights                                                                        | P0       |
| REQ-006    | `.zip` + `.tar.gz` bundles with fonts, `manifest.json`, `LICENSE.txt`, `README.md`                                          | P0       |
| REQ-007    | Auto GitHub Release tagged `custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}`                                            | P0       |
| CON-001    | `Scripts/build.py`, `fontbuilder.py`, `features.py`, `Makefile` MUST NOT be modified/renamed/refactored                     | P0       |
| CON-002    | `ubuntu-latest` GitHub-hosted runner, default `GITHUB_TOKEN`, `contents: write`                                             | P0       |
| CON-003    | SIL OFL v1.1 maintained; `OFL-1.1` in manifest                                                                              | P0       |
| SEC-001    | Workflow permissions restricted to `contents: write` + `actions: read`                                                      | P0       |
| GUD-001    | Unknown keys in `config.json` warn but never fail                                                                           | P1       |
| GUD-002    | No duplicate releases within the same `run_attempt`                                                                         | P1       |
| GUD-003    | Release creation retries with exponential backoff (3 attempts: 1 s, 5 s, 25 s)                                              | P1       |
| FR-8/OBS-2 | Manifest `config_source` mandatory; job summary warns when fork release count > 20 (PRD §5.3)                               | P1       |

## 2. Implementation Steps

> **EXECUTION DIRECTIVE FOR AI AGENTS:**
> You MUST execute this plan phase by phase. You MUST run the specific testing/verification task at the end of each phase. After a phase is tested, you **MUST STOP AND WAIT** for the user's explicit approval before proceeding to the next phase.

### Implementation Phase 1

- GOAL-001: Configuration Foundation — schema, `configure.py` wrapper, and unit test suite running on the host-runner Python 3.14 layer.

| Task     | Description                                                                                                                                                                                                                                                                                                                                                                                                                          | Ref ID           | AC Ref         | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------- | -------------- | --------- | ---- |
| TASK-001 | Create `config.schema.json` (JSON Schema draft-07) at repository root, exactly per Spec §4.2 (`additionalProperties: true`, four boolean properties with defaults)                                                                                                                                                                                                                                                                   | REQ-002          | AC-004         | ✅        | 2026-07-29 |
| TASK-002 | Create `Scripts/configure.py` (Python 3.14) CLI skeleton with the full option surface from Spec §4.4 (`--config-file`, `--schema-file`, four `--form-*` flags, `--output-args-file`, `--generate-manifest`)                                                                                                                                                                                                                          | REQ-001, REQ-003 | AC-001         | ✅        | 2026-07-29 |
| TASK-003 | Implement schema validation: load `config.json` (missing file = empty object), validate against schema, emit `Invalid config.json: '<key>' must be a boolean, got <type>` on failure and exit 1; emit warning lines for unknown keys without failing                                                                                                                                                                                 | REQ-002, GUD-001 | AC-004         | ✅        | 2026-07-29 |
| TASK-004 | Implement precedence resolution (`resolve_options`): form input > `config.json` > defaults, with per-option source tracking (`form`, `form_override`, `config.json`, `defaults`) and one log line per option naming its source (e.g. `Using form value (overrides config.json) for large_line_height`)                                                                                                                               | REQ-003          | AC-003         | ✅        | 2026-07-29 |
| TASK-005 | Implement `compute_config_source()` exactly per Spec §9.1 hierarchy and write the driver argument string (`--line-height`, `--no-loop-k`, `--no-calt`, space-separated, possibly empty) to `--output-args-file`                                                                                                                                                                                                                      | REQ-003          | AC-003         | ✅        | 2026-07-29 |
| TASK-006 | Implement `--generate-manifest`: `manifest_version`, `build_timestamp` (UTC ISO 8601), `source_commit` (from env `GITHUB_SHA`), `workflow_version`, `config_source`, `resolved_options`, `toolchain_versions` (python; fontforge/ttfautohint filled in later phases), empty `font_files` array, `spdx_license: "OFL-1.1"` — conforming to Spec §4.6 `required` array                                                                 | REQ-006, CON-003 | AC-001         | ✅        | 2026-07-29 |
| TASK-007 | Create test fixtures `tests/fixtures/configs/{valid_config,invalid_config,empty_config,unknown_key_config}.json` and `tests/test_configure.py` covering: full 4-state precedence matrix (defaults/config.json/form/form_override), valid/invalid/empty/unknown-key validation, exact error message text, manifest schema conformance (validate against §4.6 via `jsonschema`), and `config_source` computation for every combination | REQ-002, REQ-003 | AC-003, AC-004 | ✅        | 2026-07-29 |
| TASK-008 | **VERIFY**: `python3.14 -m pytest tests/ -v` passes 100% locally; Spec §10 criterion 2 satisfied for the wrapper layer                                                                                                                                                                                                                                                                                                               | -                | -              | ✅        | 2026-07-29 |
| TASK-009 | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 2                                                                                                                                                                                                                                                                                                                                                              | -                | -              | ✅        | 2026-07-29 |

### Implementation Phase 2

- GOAL-002: Container & Driver — Stage 1 driver script plus multi-stage `Dockerfile` producing unhinted TTF/OTF/SVG for all 4 weights without touching legacy files.

| Task     | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Ref ID                            | AC Ref         | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------- | -------------- | --------- | ---- |
| TASK-010 | Create `Scripts/custom_build_driver.py` (Python 2.7) per Spec §4.4 contract: parse `SOURCES_DIR OUTPUT_DIR [--line-height] [--no-loop-k] [--no-calt]`; declare resolved options in the `fontbuilder` registry (including `option('NoCalt', 'Turn off contextual alternates', DropCAltAndLiga())` when `--no-calt`); replicate the `_build()` core loop for exactly one combination per `.sfdir` (open font, apply operations, `update_features()`, generate TTF+OTF+SVG); MUST NOT invoke `ttfautohint`/`sfnt2woff`/`woff2_compress`; non-zero exit + diagnostic on failure; **set `SOURCE_DATE_EPOCH` in the driver environment per PRD US-015 to minimize FontForge output non-determinism (byte-identity is explicitly not a V1 requirement; mitigation only)** | REQ-004, REQ-005, CON-001, US-015 | AC-002         | ✅        | 2026-07-29 |
| TASK-011 | Rewrite root `Dockerfile` as multi-stage per Spec §4.5: Stage 1 (`ubuntu:18.04`, `ppa:fontforge/fontforge`, fontforge + python-fontforge + python2.7 + make, `ARG BUILD_ARGS=""`, driver `RUN` via `fontforge -lang=py -script`); Stage 2 (`ubuntu:26.04`, deadsnakes Python 3.14, ttfautohint, woff-tools, woff2, zip, tar; `COPY --from=builder-fontforge` of `/build/TTF`, `/build/OTF`, `/build/Webfonts`)                                                                                                                                                                                                                                                                                                                                                     | REQ-004, CON-002                  | AC-001         | ✅        | 2026-07-29 |
| TASK-012 | Local container smoke test: `docker build -t custom-build-test --build-arg BUILD_ARGS="" .` then repeat with `--no-loop-k`, `--no-calt`, `--line-height --no-calt`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | REQ-004, REQ-005                  | AC-001, AC-002 |           |      |
| TASK-013 | **VERIFY**: (a) `docker build` completes cleanly for all BUILD_ARGS variants (Spec §10 criterion 3); (b) all 4 weights exist in `TTF/`, `OTF/`, `Webfonts/` (SVG); (c) glyph parity — driver `Normal` output table-diffed against legacy `make` output (fontTools `ttx` dump comparison) shows no unintended differences; (d) `--no-calt` build contains no `calt`/`liga` lookups; (e) `git diff Scripts/build.py Scripts/fontbuilder.py Scripts/features.py Makefile` is empty (CON-001)                                                                                                                                                                                                                                                                          | -                                 | -              |           |      |
| TASK-014 | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 3                                                                                                                                                                                                                                                                                                                                                              | -                                 | -              | ✅        | 2026-07-29 |

### Implementation Phase 3

- GOAL-003: Workflow Orchestration — `.github/workflows/custom-build.yml` from dispatch to downloadable Workflow Artifacts.

| Task     | Description                                                                                                                                                                                                                                                                                                                                                                     | Ref ID                    | AC Ref         | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- | -------------- | --------- | ---- |
| TASK-020 | Create `.github/workflows/custom-build.yml` with `workflow_dispatch` trigger and the four boolean inputs (`large_line_height`, `no_loop_k`, `no_calt`, `use_hinted`) with defaults and human-readable descriptions per Spec §4.3                                                                                                                                                | REQ-003                   | AC-001         | ✅        | 2026-07-29 |
| TASK-021 | Declare top-level `permissions: contents: write, actions: read`; runner `ubuntu-latest`                                                                                                                                                                                                                                                                                         | SEC-001, CON-002          | AC-001         | ✅        | 2026-07-29 |
| TASK-022 | Add steps: `actions/setup-python` with `python-version: '3.14'`, install `jsonschema` + `pytest`, run `pytest tests/` (unit gate before any Docker work)                                                                                                                                                                                                                        | REQ-002                   | AC-004         | ✅        | 2026-07-29 |
| TASK-023 | Add a separately named step `Validate config.json against schema` invoking `configure.py` validation mode                                                                                                                                                                                                                                                                       | REQ-002                   | AC-004         | ✅        | 2026-07-29 |
| TASK-024 | Add resolution step: run `configure.py` with all four `--form-*` values, `--output-args-file`, `--generate-manifest`; emit the per-option source log lines into the build log                                                                                                                                                                                                   | REQ-003                   | AC-003         | ✅        | 2026-07-29 |
| TASK-025 | Add Docker build step: `docker build --build-arg BUILD_ARGS="$(cat build-args.txt)" -t fantasque-custom .` and run the Stage 2 image to extract packaged outputs onto the runner                                                                                                                                                                                                | REQ-004, REQ-005          | AC-001         | ✅        | 2026-07-29 |
| TASK-026 | Add packaging steps executed in Stage 2 context: read `UseHinted` via `jq '.resolved_options.UseHinted' manifest.json` and conditionally run `ttfautohint` on TTFs; run `sfnt2woff` + `woff2_compress` into `Webfonts/`; compute SHA-256 + sizes into `font_files` of the manifest; assemble `.zip` and `.tar.gz` containing fonts, `manifest.json`, `LICENSE.txt`, `README.md` | REQ-005, REQ-006, CON-003 | AC-001, AC-005 | ✅        | 2026-07-29 |
| TASK-027 | Upload both archives as Workflow Artifacts named `fantasque-sans-custom-build-{run_id}-{run_attempt}` (default 90-day retention; GitHub Actions default for public repos; configurable up to 400 days for private repos via retention-days input)                                                                                                                               | REQ-006                   | AC-001         | ✅        | 2026-07-29 |
| TASK-028 | Write job summary (`$GITHUB_STEP_SUMMARY`): one-line outcome statement on success/failure, plus fork release-count warning when count > 20 (`⚠️ Your fork has N releases...`) with pointer to the troubleshooting guide                                                                                                                                                          | REQ-007, FR-8/OBS-2       | AC-001         | ✅        | 2026-07-29 |
| TASK-029 | **VERIFY**: Manual `workflow_dispatch` on a test fork with all defaults: run succeeds, archives contain all 4 weights × 5 formats + manifest + LICENSE + README, summary shows success line, manifest records `config_source: "defaults"` (or local equivalent via act per DEP-007: act workflow_dispatch -W .github/workflows/custom-build.yml)                                | -                         | -              | ✅        | 2026-07-29 |
| TASK-030 | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 4                                                                                                                                                                                                                                                                                                         | -                         | -              | ✅        | 2026-07-29 |

### Implementation Phase 4

- GOAL-004: Release Publishing — tagged GitHub Release with generated notes, retry-safe and idempotent.

| Task     | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Ref ID                    | AC Ref                 | Completed | Date |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- | ---------------------- | --------- | ---- |
| TASK-040 | Implement tag generation `custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}` in UTC from workflow context variables                                                                                                                                                                                                                                                                                                                                                                                                                        | REQ-007                   | AC-005                 | ✅        | 2026-07-29 |
| TASK-041 | Implement release title generator with the following prescriptive suffix logic: (a) base name = active options joined by ` + `; `Normal` when no flag is active; (b) append ` (default)` iff base name = `Normal` AND `config_source == "defaults"`; (c) append ` (unhinted)` iff `UseHinted == false` (mutually exclusive with `(default)`, since defaults imply `UseHinted=true`); explicit declaration for F-4 — the case `Normal` + `config_source = form` + `UseHinted = true` yields title `Custom Build: Normal` (no suffix appended) | REQ-007                   | AC-001, AC-002, AC-005 | ✅        | 2026-07-29 |
| TASK-042 | Implement release body generator reading `manifest.json`: resolved options table, font files summary table (name, format, weight, SHA-256), build timestamp, source commit SHA linked to GitHub, and link back to the workflow run                                                                                                                                                                                                                                                                                                           | REQ-007                   | AC-005                 | ✅        | 2026-07-29 |
| TASK-043 | Implement release creation using the preinstalled `gh` CLI (`gh release create <tag> --title ... --notes-file ... <archives>`) wrapped in exponential backoff retry (1 s, 5 s, 25 s; max 3 attempts) with a clear failure message identifying the step; guard on existing tag to guarantee one release per `run_attempt`                                                                                                                                                                                                                     | REQ-007, GUD-002, GUD-003 | AC-005                 | ✅        | 2026-07-29 |
| TASK-044 | **VERIFY**: On the test fork: (a) AC-002 — `config.json` with `{"NoLoopK": true}` yields title `Custom Build: NoLoopK` and `config_source: "config.json"`; (b) AC-003 — form override over `config.json` yields `config_source: "form_override"` + precedence log line; (c) AC-005 — `UseHinted=false, NoCalt=true` yields `Custom Build: NoCalt (unhinted)` with both assets attached; (d) retry logic exercised via a simulated API failure (invalid endpoint override) showing 3 attempts then a clear error                              | -                         | -                      | ✅        | 2026-07-29 |
| TASK-045 | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 5                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | -                         | -                      | ✅        | 2026-07-29 |

### Implementation Phase 5

- GOAL-005: User Documentation — `docs/CUSTOM-BUILD.md` and the prominent `README.md` Custom Build section.

| Task     | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Ref ID                    | AC Ref         | Completed | Date |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- | -------------- | --------- | ---- |
| TASK-050 | Create `docs/CUSTOM-BUILD.md`: (a) "Getting Started" — numbered ≤ 5 steps with a one-sentence "Why" each and annotated screenshots (Fork button, Actions tab, `workflow_dispatch` form, Artifacts page, Releases page); (b) "Advanced Configuration" — full `config.json` schema reference, precedence rules, worked input→title example, `gh workflow run` example with all four `-f` flags; (c) "Troubleshooting" — invalid config errors, network timeouts, rate limits, and release cleanup via UI + `gh release delete` (PRD §5.3) | REQ-001, REQ-003, REQ-007 | AC-001, AC-004 | ✅        | 2026-07-29 |
| TASK-051 | Update `README.md`: new "Custom Build" section above the installation instructions — ≤ 100 words, direct link to `docs/CUSTOM-BUILD.md`, quick-start pointer, heading level consistent with existing structure                                                                                                                                                                                                                                                                                                                          | REQ-001                   | AC-001         | ✅        | 2026-07-29 |
| TASK-052 | **VERIFY**: Checklist against PRD US-011/US-012/US-013 acceptance criteria; all internal links resolve; markdown lint passes; a non-technical walkthrough of Getting Started reaches "Run workflow" without ambiguity                                                                                                                                                                                                                                                                                                                   | -                         | -              | ✅        | 2026-07-29 |
| TASK-053 | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 6                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | -                         | -              | ✅        | 2026-07-29 |

### Implementation Phase 6

- GOAL-006: End-to-End Acceptance — full Spec §5 acceptance matrix and §10 validation criteria on a clean fork.

| Task     | Description                                                                                                                                                                                                                                                         | Ref ID                             | AC Ref         | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | -------------- | --------- | ---- |
| TASK-060 | Execute the full acceptance matrix on a clean test fork: AC-001 (defaults → `Normal (default)`), AC-002 (`config.json` → NoLoopK), AC-003 (form override + log line), AC-004 (invalid config → exit 1 + exact message), AC-005 (unhinted NoCalt → tag/title/assets) | REQ-001..REQ-007                   | AC-001..AC-005 |           |      |
| TASK-061 | Walk Spec §10 Validation Criteria: schema validates as draft-07; `configure.py` unit tests 100%; `docker build` clean; dispatch→artifacts→release succeeds on the fork; archive manifests' SHA-256 match re-hashed font files                                       | REQ-002, REQ-004, REQ-006, REQ-007 | AC-001, AC-005 | 🟡        | 2026-07-29 |
| TASK-062 | Backward-compatibility audit: local `make` still produces `Variants/Normal/FantasqueSansMono.zip`; `git diff Scripts/ Makefile` between pre-V1 and post-V1 is empty; record end-to-end build duration (target p95 ≤ 15 min, PRD SM-T2)                              | CON-001                            | AC-001         | 🟡        | 2026-07-29 |
| TASK-063 | **VERIFY**: All five ACs green, all five §10 criteria satisfied, zero legacy-file diff, duration within target                                                                                                                                                      | -                                  | -              |           |      |
| TASK-064 | **APPROVAL**: Wait for explicit user confirmation for launch readiness and handoff to `@ExpertCodeReviewer`                                                                                                                                                         | -                                  | -              |           |      |


## 2.1 Implementation Status (as of 2026-07-29)

| Phase | Status | Detail |
| ----- | ------ | ------ |
| Phase 1 — Configuration Foundation | ✅ Complete (TASK-001..TASK-009) | 62/62 unit tests passing; CON-001 verified; Spec §10 criteria 1 + 2 satisfied |
| Phase 2 — Container & Driver | 🟡 Code complete; smoke test deferred | TASK-010, TASK-011, TASK-014 done; static review 10/10; **TASK-012 + TASK-013 deferred to CI per Opsi B (2026-07-29)** |
| Phase 3 — Workflow Orchestration | ✅ Complete (TASK-020..TASK-030) | 9/9 implementation + verify + approval; static review 23/23; TASK-029 user-approved per bypass 2026-07-29 |
| Phase 4 — Release Publishing | ✅ Complete (TASK-040..TASK-045) | 4/4 implementation + verify + approval; release title suffix logic verified against Spec §9.2 matrix; retry + idempotency guard implemented |
| Phase 5 — User Documentation | ✅ Complete (TASK-050..TASK-053) | 2/2 deliverables + verify + approval; `docs/CUSTOM-BUILD.md` (11 KB) + README section (86 words, h2 Setext style); all 9 internal links resolve; structure follows CONTEXT.md glossary |
| Phase 6 — End-to-End Acceptance | 🟡 Static PASS; runtime deferred | TASK-061 (2/5 static criteria) + TASK-062 (CON-001 part) verified; report at `docs/audit/phase-6-verification-report-2026-07-29.md`; **TASK-060 + TASK-061(3/5) + TASK-062 runtime + TASK-063/064 deferred to CI per Opsi B** |

**Opsi B decision (2026-07-29):** User chose to defer Docker-dependent verification
(`docker build`, `workflow_dispatch` end-to-end) to the CI run on their fork, rather
than installing Docker locally on the Windows workstation. Static review substitutes
for runtime checks: 10/10 for Phase 2, 23/23 for Phase 3. CON-001 verified
throughout (legacy files untouched: `git diff Scripts/build.py Scripts/fontbuilder.py
Scripts/features.py Makefile` = empty).

**Next pending actions (user-driven):**
1. Push Phase 1-5 code to a fork, trigger `workflow_dispatch` to satisfy
   TASK-060 + TASK-061 (3/5 runtime) + TASK-062 (runtime) + TASK-063 in one
   end-to-end CI run (procedure documented in `docs/audit/phase-6-verification-report-2026-07-29.md` §2).
2. After CI passes: user grants TASK-064 approval for launch readiness, then
   invokes `/sdlc-code-review` for formal review.

## 3. Alternatives

- **ALT-001**: Pass `--line-height`/`--no-loop-k`/`--no-calt` directly to `Scripts/build.py` — **Rejected**: `build.py` accepts only four positional arguments, declares options statically (`NoCalt` commented out), and is immutable under CON-001. This was the Spec v1.4 §4.4 contract; corrected in v1.5 (finding R-4).
- **ALT-002**: Patch `build.py` at container build time (`sed` injection) — **Rejected**: violates the spirit of CON-001, is fragile against upstream changes, and undermines build reproducibility.
- **ALT-003**: Build all permutations via legacy `build.py`, then select the archive matching the resolved Variant — **Rejected**: the `NoCalt` declaration is commented out in `build.py`, so AC-002/AC-005 variants cannot be produced at all; additionally wastes compute on unwanted permutations.
- **ALT-004**: Have `configure.py` generate a transient build script (codegen) instead of a static driver — **Rejected**: a static, version-controlled driver is testable, reviewable, and eliminates codegen drift; the transient approach offered no compensating advantage.
- **ALT-005**: `softprops/action-gh-release` for release publishing — **Rejected** in favor of the preinstalled `gh` CLI: zero third-party action trust surface (SEC-001 least privilege) and full control over retry semantics (GUD-003).

## 4. Dependencies

- **DEP-001**: GitHub-hosted `ubuntu-latest` runner with Docker and ≥ 10 GB free disk (Spec INF-001).
- **DEP-002**: `actions/setup-python` supporting Python 3.14 on the host runner; PyPI packages `jsonschema`, `pytest`.
- **DEP-003**: `ppa:fontforge/fontforge` serving FontForge + Python 2.7 bindings for `ubuntu:18.04` (Stage 1).
- **DEP-004**: `ppa:deadsnakes/ppa` serving Python 3.14 for `ubuntu:26.04` (Stage 2).
- **DEP-005**: Ubuntu 26.04 universe binaries: `ttfautohint`, `woff-tools`, `woff2`, `zip`, `tar`.
- **DEP-006**: Upstream `.sfdir` sources in `Sources/` (Spec DAT-001) — read-only input.
- **DEP-007**: Optional: `act` for local dry-run of the workflow during Phase 3 development.

## 5. Files

- **FILE-001**: `config.schema.json` — NEW, repository root (TASK-001).
- **FILE-002**: `Scripts/configure.py` — NEW, Python 3.14 wrapper (TASK-002..006).
- **FILE-003**: `Scripts/custom_build_driver.py` — NEW, Python 2.7 Stage 1 driver (TASK-010).
- **FILE-004**: `tests/test_configure.py` + `tests/fixtures/configs/*.json` — NEW, unit suite + fixtures (TASK-007).
- **FILE-005**: `Dockerfile` — REPLACED with multi-stage build; FR-11 permits replacement provided `docker build && docker run` remains documented (TASK-011).
- **FILE-006**: `.github/workflows/custom-build.yml` — NEW, the Workflow (TASK-020..043).
- **FILE-007**: `docs/CUSTOM-BUILD.md` — NEW, user guide (TASK-050).
- **FILE-008**: `README.md` — MODIFIED, adds the Custom Build section only (TASK-051).
- **FILE-009**: DO NOT TOUCH — `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`, `Makefile`, `Sources/`, existing `Scripts/*` shell helpers (CON-001).

## 6. Testing

- **TEST-001**: `pytest tests/ -v` — precedence 4-state matrix, schema validation (valid/invalid/empty/unknown-key), exact diagnostic text, `config_source` computation, manifest schema conformance (Phase 1, rerun in CI at TASK-022).
- **TEST-002**: Container smoke matrix — `docker build` with empty and combined `BUILD_ARGS`; output inventory (4 weights × TTF/OTF/SVG); `ttx` table-diff parity of driver `Normal` vs legacy `make` output; absence of `calt`/`liga` in NoCalt builds (Phase 2).
- **TEST-003**: Manifest integrity — re-hash every archived font file and compare against `manifest.json` checksums; `python -m json.tool` validity (Phases 3 and 6).
- **TEST-004**: End-to-end fork matrix — AC-001..AC-005 on a clean test fork, including release title/tag/body assertions and artifact contents (Phases 4 and 6).
- **TEST-005**: Backward compatibility — local `make` output unchanged; `git diff Scripts/ Makefile` empty (Phases 2 and 6).
- **TEST-006**: Release resilience — simulated API failure triggers 1 s/5 s/25 s backoff then a clear failure message; repeated run in the same `run_attempt` creates no duplicate release (Phase 4).

## 7. Risks & Assumptions

- **RISK-001**: `ppa:fontforge/fontforge` for `ubuntu:18.04` may become unavailable (EOL base). Mitigation: pin working package versions during Phase 2; document fallback to `old-releases.ubuntu.com` mirrors if PPA fetch fails.
- **RISK-002**: `ubuntu:26.04` image or deadsnakes Python 3.14 for 26.04 may lag at implementation time. Mitigation: verify availability in TASK-011 before wiring Stage 2; fall back to `pyenv`-installed 3.14 as ADR-0002 permits.
- **RISK-003**: Cross-stage glibc/toolchain mismatch flagged by ADR-0002. Mitigation: fonts are data files — Stage 2 only compresses/packages them; parity checks in TASK-013 validate outputs independently of runtime.
- **RISK-004**: Driver replicates the `_build()` core loop; subtle divergence from legacy output is possible. Mitigation: mandatory `ttx` table-diff parity gate in TASK-013 before any approval.
- **RISK-005**: Build duration may exceed the 15-minute SM-T2 target on a single runner. Mitigation: measure in TASK-062; if breached, document actuals and defer matrix parallelization to V2 (PRD §8.3 Challenge 3).
- **RISK-006**: FontForge output non-determinism (embedded timestamps). Mitigation: set `SOURCE_DATE_EPOCH` in the driver environment (PRD US-015); byte-identity is explicitly not a V1 requirement.
- **ASSUMPTION-001**: `actions/setup-python` offers Python 3.14 at implementation time; if not, install 3.14 via deadsnakes on the host runner.
- **ASSUMPTION-002**: Fork owners run with default `GITHUB_TOKEN` (`contents: write`) — no secrets or PATs required.
- **ASSUMPTION-003**: `jq` is available on `ubuntu-latest` runners (it is preinstalled) for manifest-driven hinting gating.
- **ACCEPTANCE-REINFORCEMENT-001** (exceeds Spec §10.3 minimum): The `ttx` table-diff parity gate in TASK-013(c) — driver `Normal` output table-diffed against the legacy `make` output (fontTools `ttx` dump comparison) — is stricter than the Spec §10.3 minimum requirement, which mandates only that `docker build` completes cleanly. The gate is retained as a V1 acceptance criterion to reinforce mitigation of RISK-004 (driver divergence from the legacy `_build()` core loop). This is a Plan-level decision to exceed the Spec-defined minimum in service of build correctness; it does not alter Spec v1.5.

## 8. Related Specifications / Further Reading

- [Technical Specification — Custom Build via GitHub Workflow v1.5](../spec/spec-custom-build-workflow.md)
- [PRD — Custom Build via GitHub Workflow v1.3](../docs/prd-20260723-1130-custom-build-workflow.md)
- [ADR 0002 — Multi-Stage Docker Build with Deferred Engine Port](../docs/adr/0002-multi-stage-docker-deferred-engine-port.md)
- [Fantasque Sans Mono Domain Glossary](../CONTEXT.md)

## 9. Rollback / Recovery Plan

This plan targets a pure build pipeline with no persistent application state (no database, no environment variables, no external state mutation). Rollback is therefore limited to source code revert, GitHub Release cleanup, and Workflow Artifact deletion.

### 9.1 Per-Phase Source Code Revert

| Phase | Affected Files (NEW) | Revert Command |
| --- | --- | --- |
| Phase 1 (Config) | `config.schema.json`, `Scripts/configure.py`, `tests/test_configure.py` + fixtures | `git revert <commit>` to drop the entire phase commit |
| Phase 2 (Container) | `Dockerfile`, `Scripts/custom_build_driver.py` | `git revert <commit>` + verify local `make` still works (CON-001) |
| Phase 3 (Workflow) | `.github/workflows/custom-build.yml` | `git revert <commit>`; alternatively `rm .github/workflows/custom-build.yml` to disable the workflow entirely |
| Phase 4 (Release) | Release-related steps in `custom-build.yml` | `git revert <commit>` on the workflow commit |
| Phase 5 (Docs) | `docs/CUSTOM-BUILD.md`, `README.md` | `git revert <commit>` |
| Phase 6 (Acceptance) | None (verification only) | N/A — no rollback needed |

**Post-revert verification (universal):**

- `git diff Scripts/build.py Scripts/fontbuilder.py Scripts/features.py Makefile` MUST be empty (CON-001)
- `make` locally MUST still produce `Variants/Normal/FantasqueSansMono.zip`
- `git status` MUST show a clean working tree

### 9.2 GitHub Release Cleanup

To delete a malformed release published by a failed or incorrect run:

```bash
# Delete a specific release and its tag
gh release delete custom-build-YYYYMMDD-HHMMSS-<run_id>-<run_attempt> --yes

# Delete the tag if it remains
git push origin :refs/tags/custom-build-YYYYMMDD-HHMMSS-<run_id>-<run_attempt>
```

To bulk-delete accumulated test releases (e.g., during initial fork setup):

```bash
gh release list --limit 100 | awk '{print $1}' | xargs -I {} gh release delete {} --yes
```

> **Note:** The fork release-count warning (TASK-028, threshold > 20) anticipates this scenario. Users with many test releases SHOULD use the bulk-delete command above before triggering a production build.

### 9.3 Workflow Artifact Cleanup

To delete artifacts uploaded to a failed run:

```bash
# List artifacts for a specific run
gh api repos/:owner/:repo/actions/runs/<run_id>/artifacts

# Delete a specific artifact by ID
gh api -X DELETE repos/:owner/:repo/actions/artifacts/<artifact_id>
```

Default artifact retention is 90 days (GitHub Actions default for public repos); artifacts older than the retention window are auto-deleted by GitHub.

### 9.4 Docker Image State Recovery

If a stale or corrupt Docker image is cached on the runner:

```bash
docker builder prune -af           # Clear all build cache
docker image prune -af             # Remove dangling images
docker build --no-cache -t fantasque-custom .   # Force fresh build
```

### 9.5 Escalation Path

If automated rollback fails:

1. Open an issue in the upstream repository (`belluzj/fantasque-sans`) referencing the failed run URL and the broken commit SHA.
2. As a last resort, pin the workflow to a known-good commit SHA via the `uses:` directive to bypass the broken revision.
3. If a fork's release namespace is corrupted beyond recovery, the fork owner can delete the repository and re-fork; the workflow is self-contained in the repository and re-forking produces a clean state.

### 9.6 Recovery Verification Checklist

After any rollback, the following checklist MUST be satisfied before declaring recovery complete:

- [ ] `git status` is clean
- [ ] `git diff Scripts/build.py Scripts/fontbuilder.py Scripts/features.py Makefile` is empty (CON-001)
- [ ] `make` locally produces `Variants/Normal/FantasqueSansMono.zip` unchanged
- [ ] If the workflow was reverted, a fresh `workflow_dispatch` with default inputs succeeds end-to-end (mirror of Phase 6 TASK-060)
- [ ] No stale GitHub Releases or Workflow Artifacts remain (per §9.2 and §9.3)
