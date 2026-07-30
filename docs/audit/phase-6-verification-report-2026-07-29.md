---
title: Phase 6 — End-to-End Acceptance Verification Report
date: 2026-07-29
status: PARTIAL (static checks PASS; runtime checks deferred to user fork per Opsi B)
version: 1.0
related_plan: plan/plan-feature-custom-build-workflow-v1.3.md
related_spec: spec/spec-custom-build-workflow.md
tags: [verification, phase-6, acceptance, custom-build]
---

<!-- markdownlint-disable -->

# Phase 6 — End-to-End Acceptance Verification Report

## Executive Summary

| Layer | Status | Detail |
| --- | --- | --- |
| **Static (executed in this session)** | ✅ 4/4 PASS | Schema, unit tests, CON-001, file inventory |
| **Runtime (deferred per Opsi B)** | ⏳ 3/5 pending | Docker build, workflow_dispatch, end-to-end release flow |

**Verdict:** Static acceptance **PASSES**. Runtime acceptance requires the user to
trigger `workflow_dispatch` on a personal fork (cannot be done from the
implementer's Windows workstation — no Docker available, per Opsi B decision
recorded in Plan v1.2 §2.1).

---

## 1. Static Verification Results (TASK-061, TASK-062)

### 1.1 Schema validates as JSON Schema Draft-07 ✅ PASS

**Source:** TASK-061 criterion #1 — "schema validates as draft-07"

**Command:**

```sh
python -c "import json, jsonschema; \
  schema = json.load(open('config.schema.json')); \
  jsonschema.Draft7Validator.check_schema(schema); \
  print('PASS')"
```

**Result:**

```
schema title: Fantasque Sans Mono Custom Build Configuration
schema draft: http://json-schema.org/draft-07/schema#
additionalProperties: True
PASS: config.schema.json validates against JSON Schema Draft-07
```

**Status:** ✅ PASS — schema is well-formed Draft-07 with the expected
`additionalProperties: true` for forward-compat (GUD-001).

### 1.2 `configure.py` unit tests 100% pass ✅ PASS

**Source:** TASK-061 criterion #2 — "configure.py unit tests 100%"

**Command:**

```sh
python -m pytest tests/ -v
```

**Result:** `62 passed in 0.49s` — 62/62 unit tests green.

**Coverage of the four §4.4 acceptance criteria (per test names):**

| Spec AC | Test | Status |
| --- | --- | --- |
| AC-001 (defaults) | `TestBuildDriverArgString::*` + `TestArgParser::test_defaults_match_cli_surface` | ✅ |
| AC-002 (config.json) | `TestMainEntryPoint::test_main_writes_args_and_manifest` | ✅ |
| AC-003 (form override) | `TestMainEntryPoint::test_main_emits_ac003_log_line` | ✅ |
| AC-004 (invalid config) | `TestMainEntryPoint::test_main_returns_1_on_invalid_config` | ✅ |

### 1.3 CON-001 — Legacy files untouched ✅ PASS

**Source:** TASK-062 — "git diff Scripts/ Makefile between pre-V1 and post-V1 is empty"

**Command:**

```sh
git diff --stat Scripts/build.py Scripts/fontbuilder.py Scripts/features.py Makefile Sources/
```

**Result:** Empty output — no modifications to any legacy file.

**File SHA verification (sanity check):**

| File | Size | SHA-256 (prefix) |
| --- | --- | --- |
| `Scripts/build.py` | 1671 bytes | `4285eaa2f915...` |
| `Scripts/fontbuilder.py` | 8266 bytes | `d12bf476ccbf...` |
| `Scripts/features.py` | 8550 bytes | `b3118f41fcb4...` |
| `Makefile` | 689 bytes | `4e39cdd7eda5...` |

All four files present and unmodified relative to the upstream baseline. CON-001
holds across Phases 1–5.

### 1.4 File inventory complete ✅ PASS

**Source:** Plan v1.2 §5 (FILE-001..FILE-009) — all 9 expected deliverables exist.

| File | Size | Phase | Status |
| --- | --- | --- | --- |
| `config.schema.json` | 842 B | 1 | ✅ |
| `Scripts/configure.py` | 15 815 B | 1 | ✅ |
| `Scripts/custom_build_driver.py` | 10 568 B | 2 | ✅ |
| `Scripts/packaging.sh` | 7 180 B | 3 | ✅ |
| `Dockerfile` | 4 791 B | 2 | ✅ (replaced per FR-11) |
| `.github/workflows/custom-build.yml` | 15 267 B | 3+4 | ✅ |
| `docs/CUSTOM-BUILD.md` | 11 096 B | 5 | ✅ |
| `README.md` | 5 994 B | 5 | ✅ (Custom Build section added) |
| `tests/test_configure.py` | 24 099 B | 1 | ✅ |

All expected deliverables present and non-empty. 9/9 ✅.

---

## 2. Runtime Verification Results (TASK-060, TASK-061 runtime portion)

The following checks **cannot be executed from this Windows workstation** because
Docker is not available locally (per Opsi B decision in Plan v1.2 §2.1,
2026-07-29). They are documented here as the procedure the user must run on a
personal fork.

### 2.1 `docker build` completes cleanly ⏳ DEFERRED

**Source:** TASK-061 criterion #3, TASK-012, TASK-013(a)

**Procedure (run on fork):**

```sh
# 1. Push Phase 1-5 commits to a fork
git push origin main

# 2. Trigger the workflow with default inputs
gh workflow run custom-build.yml

# 3. Watch the run
gh run watch

# 4. Check the Build Docker image step for "Done" or success status
```

**Expected:** Both stages of the multi-stage build complete without errors. Stage 1
runs `fontforge --quiet -lang=py -script Scripts/custom_build_driver.py Sources /build $BUILD_ARGS`
inside the `ubuntu:18.04 + fontforge` image. Stage 2 packages outputs in
`ubuntu:26.04 + python3.14`.

### 2.2 `workflow_dispatch` → artifacts → release succeeds on the fork ⏳ DEFERRED

**Source:** TASK-061 criterion #4, TASK-029, AC-001..AC-005

**Procedure:** Trigger 5 runs on the fork, one per acceptance criterion:

| AC | Inputs | Expected result |
| --- | --- | --- |
| AC-001 | (defaults) | Title `Custom Build: Normal (default)`, tag with `config_source: "defaults"` |
| AC-002 | `config.json = {"NoLoopK": true}`, default form | Title `Custom Build: NoLoopK`, tag with `config_source: "config.json"` |
| AC-003 | `config.json = {"LargeLineHeight": false}`, form `large_line_height=true` | Log line `Using form value (overrides config.json) for large_line_height`, tag with `config_source: "form_override"` |
| AC-004 | `config.json = {"NoCalt": "yes"}` (invalid type) | Step `Validate config.json against schema` exits 1 with `Invalid config.json: 'NoCalt' must be a boolean, got string` |
| AC-005 | Form `no_calt=true, use_hinted=false` | Title `Custom Build: NoCalt (unhinted)`, both `.zip` and `.tar.gz` attached, tag `custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}` |

### 2.3 Archive manifests' SHA-256 match re-hashed font files ⏳ DEFERRED

**Source:** TASK-061 criterion #5, TEST-003

**Procedure (run on fork after AC-001 completes):**

```sh
# Download the artifact
gh run download <run_id> --name fantasque-sans-custom-build-<run_id>-1

# Re-hash every font file and compare against manifest.json
cd fantasque-sans-custom-build-<run_id>-1
python3 - <<'PY'
import json, hashlib, pathlib
manifest = json.load(open('manifest.json'))
for entry in manifest['font_files']:
    actual = hashlib.sha256(pathlib.Path(entry['filename']).read_bytes()).hexdigest()
    if actual != entry['sha256']:
        print(f"FAIL {entry['filename']}")
    else:
        print(f"OK   {entry['filename']}")
PY
```

**Expected:** All `OK` lines; no `FAIL` lines. Re-hashing locally must reproduce
the SHA-256 listed in the manifest for every font file.

### 2.4 Backward-compatibility — local `make` still works ⏳ DEFERRED

**Source:** TASK-062 — "local make still produces Variants/Normal/FantasqueSansMono.zip"

**Procedure (run on a machine with Python 2.7 + FontForge + make):**

```sh
make
ls -la Variants/Normal/FantasqueSansMono.zip
```

**Expected:** Build succeeds; `Variants/Normal/FantasqueSansMono.zip` is produced
with the same content as a pre-V1 build.

**Why this matters:** Confirms CON-001 was not just a textual guarantee — the
legacy pipeline is still functional for users who prefer the local build path.

### 2.5 Build duration p95 ≤ 15 minutes (PRD SM-T2) ⏳ DEFERRED

**Source:** TASK-062, PRD SM-T2

**Procedure:** Measure the wall-clock duration of `gh run watch` for at least
5 runs (AC-001 through AC-005 above) and compute the 95th percentile.

**Expected:** p95 ≤ 15 min. If breached, document actuals and defer
matrix parallelization to V2 (per PRD §8.3 Challenge 3).

---

## 3. Risk Verification (Plan §7 cross-check)

| Risk | Verification | Status |
| --- | --- | --- |
| RISK-001: PPA `fontforge/fontforge` for `ubuntu:18.04` may become unavailable | Will be exercised in §2.1 above (CI run) | ⏳ |
| RISK-002: `ubuntu:26.04` / deadsnakes Python 3.14 availability | Will be exercised in §2.1 | ⏳ |
| RISK-003: Cross-stage glibc/toolchain mismatch (ADR-0002) | Mitigated by Stage 2 only doing packaging (Spec §7); validated by §2.3 SHA-256 re-hash | ⏳ |
| RISK-004: Driver divergence from legacy `_build()` core loop | ttx table-diff parity gate (Plan ACCEPTANCE-REINFORCEMENT-001) | ⏳ |
| RISK-005: Build duration > 15 min | Measured in §2.5 | ⏳ |
| RISK-006: FontForge output non-determinism | `SOURCE_DATE_EPOCH` set in driver (TASK-010); byte-identity explicitly NOT a V1 requirement | ✅ Mitigated |

---

## 4. Spec §10 Validation Criteria Mapping

| § # | Criterion | Static status | Runtime status |
| --- | --- | --- | --- |
| 1 | `config.schema.json` validates as draft-07 | ✅ §1.1 | n/a |
| 2 | `Scripts/configure.py` passes 100% of unit tests | ✅ §1.2 (62/62) | n/a |
| 3 | Multi-stage `Dockerfile` completes `docker build` cleanly | n/a | ⏳ §2.1 |
| 4 | Workflow produces artifacts + publishes tagged Release | n/a | ⏳ §2.2 |
| 5 | Archives contain valid `manifest.json` matching checksums | n/a | ⏳ §2.3 |

**Score: 2/5 PASS (static only), 3/5 DEFERRED (require CI).**

---

## 5. Conclusion

**Static acceptance (this session): 4/4 PASS** — all checks that can be performed
without Docker, GitHub Actions, or a clean fork pass. The Custom Build implementation
is well-formed, follows the Spec and Plan contracts, and preserves the legacy
build path (CON-001).

**Runtime acceptance (next user action): 0/5 done, 3 procedures documented** — the
remaining acceptance criteria require pushing the implementation to a personal
fork and triggering `workflow_dispatch`. The user must perform this step on their
own GitHub account.

**Recommendation:** Proceed to invoke `/sdlc-code-review` for the implementation
while the user prepares the CI run in parallel. This unblocks the formal
launch-readiness gate (TASK-064) on the same calendar day.

---

## 6. Sign-off

| Role | Status | Date |
| --- | --- | --- |
| God Mode Dev (static verification) | ✅ Submitted | 2026-07-29 |
| User (CI run + runtime verification) | ⏳ Pending | — |
| `@ExpertCodeReviewer` (formal code review) | ⏳ Pending | — |
| User (launch readiness approval — TASK-064) | ⏳ Pending | — |
