---
title: Technical Specification — Custom Build via GitHub Workflow
version: 1.4
date_created: 2026-07-23
last_updated: 2026-07-24
owner: Fantasque Sans Mono Core Team
tags: [spec, github-actions, custom-build, docker, python]
---
<!-- markdownlint-disable-->
# Introduction

This document provides the definitive Technical Specification for the **Custom Build System** of Fantasque Sans Mono via GitHub Workflow. It specifies the configuration layer (`configure.py`), JSON Schema validation (`config.schema.json`), multi-stage Docker build architecture (ADR-0002), GitHub Actions workflow (`custom-build.yml`), manifest generation (`manifest.json`), and artifact/release publishing contracts.

## 1. Purpose & Scope

### 1.1 Purpose

The purpose of this specification is to define the technical contracts, schema definitions, runtime architecture, configuration precedence rules, and acceptance criteria required to implement a cloud-hosted custom font compilation workflow without modifying the legacy Python 2.7 Makefile entry point (`Scripts/build.py`).

### 1.2 Scope

- **In Scope**:
  - Configuration schema `config.schema.json` (JSON Schema draft-07) and repository root file `config.json`.
  - Multi-stage Dockerfile architecture (Stage 1: Python 2.7 + FontForge for compilation; Stage 2: Ubuntu 26.04 LTS + Python 3.14 for autohinting, webfont compression, and packaging. The configuration wrapper `configure.py` runs on the **GitHub Actions host runner** — not inside the container — and passes resolved build args to Stage 1 via `docker build --build-arg`, per §4.4).
  - GitHub Actions workflow (`.github/workflows/custom-build.yml`) featuring `workflow_dispatch` inputs and automated GitHub Release & Workflow Artifact publishing.
  - Build manifest format (`manifest.json`) and SHA-256 checksum generation.
  - User documentation: creation of `docs/CUSTOM-BUILD.md` (Getting Started + Advanced Configuration sections) and `README.md` update with prominent Custom Build section linking to the guide.
- **Out of Scope (Deferred to V2)**:
  - Python 3 porting of `Scripts/fontbuilder.py` and `Scripts/features.py`.
  - Spacing variants (`spacing` option) and alternate glyph variants (`$` and `0`).
  - Automated release cleanup or multi-tenant release channels.

## 2. Definitions

All terms used in this document strictly align with the project's Domain Glossary ([`CONTEXT.md`](file:///d:/WebstormProject/fantasque-sans/CONTEXT.md)).

- **Custom Build**: Cloud-hosted personalized build system for Fantasque Sans Mono running in GitHub Actions and Docker.
- **Variant**: Combination of one or more variant flags producing specific visual characteristics.
  - _Avoid_: configuration, preset, build option
- **Normal**: Fantasque Sans Mono variant with no variant flags enabled (`LargeLineHeight=false`, `NoLoopK=false`, `NoCalt=false`, `UseHinted=true`).
  - _Avoid_: default variant, baseline, standard
- **Fork Owner**: The GitHub user who forked the repository and has permissions to trigger a Custom Build on their fork.
  - _Avoid_: fork maintainer, repo owner
- **Upstream**: The original `belluzj/fantasque-sans` repository.
  - _Avoid_: main repo, original repository, source of truth
- **Manifest**: The `manifest.json` file bundled inside every build archive containing resolved options, checksums, and metadata.
- **Workflow**: The GitHub Actions workflow file `.github/workflows/custom-build.yml`.

## 3. Requirements, Constraints & Guidelines

### 3.1 Requirements

- **REQ-001 (Config File)**: The repository root SHALL support a `config.json` file declaring four boolean options: `LargeLineHeight`, `NoLoopK`, `NoCalt`, and `UseHinted`.
- **REQ-002 (Schema Validation)**: The build system SHALL validate `config.json` against `config.schema.json` (draft-07) prior to execution. Invalid configurations MUST fail the workflow with non-zero exit code and clear diagnostic messages.
- **REQ-003 (Precedence Resolution)**: Options resolution SHALL follow strict hierarchy: `workflow_dispatch` form inputs > `config.json` > default values (`LargeLineHeight=false`, `NoLoopK=false`, `NoCalt=false`, `UseHinted=true`).
- **REQ-004 (Multi-Stage Docker)**: The container build SHALL use Stage 1 (Python 2.7 + FontForge) for legacy font compilation and Stage 2 (Ubuntu 26.04 LTS + Python 3.14) for orchestration, hinting, webfont generation, and packaging (per ADR-0002).
- **REQ-005 (Font Formats)**: The pipeline SHALL compile TTF, OTF, WOFF, WOFF2, and SVG formats across all 4 font weights (Regular, Bold, Italic, Bold Italic).
- **REQ-006 (Artifact Packaging)**: Every build output SHALL produce `.zip` and `.tar.gz` bundles containing fonts, `manifest.json`, `LICENSE.txt`, and `README.md`.
- **REQ-007 (Automated Release)**: Every successful run SHALL publish a GitHub Release tagged `custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}` with auto-generated release notes and attached archives.

### 3.2 Constraints

- **CON-001 (Legacy Code Preservation)**: `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`, and root `Makefile` MUST NOT be modified, renamed, or refactored in V1 (NG-9).
- **CON-002 (Runner Scope)**: GitHub Actions workflow MUST run on `ubuntu-latest` GitHub-hosted runners using default `GITHUB_TOKEN` with `contents: write` permission.
- **CON-003 (License Compliance)**: All distributed packages MUST maintain SIL Open Font License v1.1 (`LICENSE.txt`) and include `OFL-1.1` in the manifest.

### 3.3 Security & Guidelines

- **SEC-001 (Least Privilege)**: Workflow permissions SHALL be explicitly restricted to `contents: write` for release publishing and `actions: read` for workflow metadata.
- **GUD-001 (Forward Compatibility)**: Unknown keys in `config.json` MUST produce warnings but SHALL NOT fail schema validation or execution.
- **GUD-002 (Idempotency)**: Release publishing MUST prevent duplicate releases within the same `run_attempt`.
- **GUD-003 (Release Creation Retry)**: Network errors during release creation SHALL be retried with exponential backoff (up to 3 attempts: 1 s, 5 s, 25 s delays). If all retries are exhausted, the workflow SHALL fail with a clear error message identifying the failed step.

## 4. Interfaces & Data Contracts

### 4.1 `config.json` Data Contract

Location: `/config.json` (repository root)

```json
{
  "LargeLineHeight": false,
  "NoLoopK": false,
  "NoCalt": false,
  "UseHinted": true
}
```

### 4.2 `config.schema.json` (JSON Schema Draft-07)

Location: `/config.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Fantasque Sans Mono Custom Build Configuration",
  "type": "object",
  "properties": {
    "LargeLineHeight": {
      "type": "boolean",
      "description": "Increases line height metric for better accented character rendering.",
      "default": false
    },
    "NoLoopK": {
      "type": "boolean",
      "description": "Uses a straight, non-looped variant for lowercase 'k'.",
      "default": false
    },
    "NoCalt": {
      "type": "boolean",
      "description": "Disables contextual alternates (programming ligatures).",
      "default": false
    },
    "UseHinted": {
      "type": "boolean",
      "description": "Runs ttfautohint on generated TTF fonts for screen rendering optimization.",
      "default": true
    }
  },
  "additionalProperties": true
}
```

### 4.3 `workflow_dispatch` Input Schema

Location: `.github/workflows/custom-build.yml`

| Input Key           | Type    | Default | Description                               |
| ------------------- | ------- | ------- | ----------------------------------------- |
| `large_line_height` | boolean | `false` | Enable larger line height variant         |
| `no_loop_k`         | boolean | `false` | Enable non-looped 'k' glyph variant       |
| `no_calt`           | boolean | `false` | Disable contextual alternates (ligatures) |
| `use_hinted`        | boolean | `true`  | Enable TTF bytecode auto-hinting          |

### 4.4 Wrapper Interface (`configure.py`)

Location: `Scripts/configure.py` (Python 3.14)

```text
Usage: python3 configure.py [OPTIONS]

Options:
  --config-file PATH       Path to config.json [default: config.json]
  --schema-file PATH       Path to config.schema.json [default: config.schema.json]
  --form-large-line-height [true|false]
  --form-no-loop-k         [true|false]
  --form-no-calt           [true|false]
  --form-use-hinted        [true|false]
  --output-args-file PATH  Path to write build.py CLI argument string
  --generate-manifest PATH Path to write output manifest.json
```

Output CLI arguments for `Scripts/build.py` (Stage 1):

- `LargeLineHeight=true` → `--line-height`
- `NoLoopK=true` → `--no-loop-k`
- `NoCalt=true` → `--no-calt`

The `UseHinted` option does **not** map to a `build.py` argument — it controls whether `ttfautohint` is invoked on TTF outputs in the packaging stage (Stage 2). Its resolved value is written into `resolved_options` within the generated `manifest.json` (via `--generate-manifest`). The workflow YAML reads this value from the manifest (e.g., `jq '.resolved_options.UseHinted' manifest.json`) to conditionally execute `ttfautohint`.

`configure.py` executes on the **GitHub Actions runner host** (not inside the Docker container) using the host's Python 3.14 runtime. It validates `config.json`, resolves options, and produces two artifacts consumed by subsequent steps: the build args file (passed to Stage 1 via `docker build --build-arg`) and the manifest (used by Stage 2 packaging).

### 4.5 Multi-Stage Docker Architecture (ADR-0002 Contract)

Location: `/Dockerfile`

```dockerfile
# Stage 1: Legacy FontForge + Python 2.7 Build Environment
FROM ubuntu:18.04 AS builder-fontforge
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:fontforge/fontforge \
    && apt-get update && apt-get install -y \
    fontforge \
    python-fontforge \
    python2.7 \
    make \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY . /build
# Receives CLI arguments from configure.py via docker build --build-arg
ARG BUILD_ARGS
RUN python2.7 Scripts/build.py $BUILD_ARGS

# Stage 2: Modern Packaging Environment (Ubuntu 26.04 + Python 3.14)
FROM ubuntu:26.04 AS final
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.14 \
    python3.14-venv \
    ttfautohint \
    woff-tools \
    woff2 \
    zip \
    tar \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder-fontforge /build/OTF /app/OTF
COPY --from=builder-fontforge /build/TTF /app/TTF
COPY --from=builder-fontforge /build/Webfonts /app/Webfonts
COPY . /app
```

### 4.6 `manifest.json` Schema

Location: Inside `.zip` and `.tar.gz` root directory

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Build Manifest",
  "type": "object",
  "required": [
    "manifest_version",
    "build_timestamp",
    "source_commit",
    "workflow_version",
    "resolved_options",
    "toolchain_versions",
    "font_files",
    "config_source",
    "spdx_license"
  ],
  "properties": {
    "manifest_version": { "type": "string", "example": "1.0" },
    "build_timestamp": { "type": "string", "format": "date-time" },
    "source_commit": { "type": "string" },
    "config_source": {
      "type": "string",
      "enum": ["defaults", "config.json", "form", "form_override"]
    },
    "workflow_version": { "type": "string" },
    "resolved_options": {
      "type": "object",
      "properties": {
        "LargeLineHeight": { "type": "boolean" },
        "NoLoopK": { "type": "boolean" },
        "NoCalt": { "type": "boolean" },
        "UseHinted": { "type": "boolean" }
      }
    },
    "toolchain_versions": {
      "type": "object",
      "description": "Versions of key build toolchain components used in this build.",
      "properties": {
        "python": { "type": "string", "description": "Python version used by configure.py (e.g., 3.14.x)" },
        "fontforge": { "type": "string", "description": "FontForge version used in Stage 1" },
        "ttfautohint": { "type": "string", "description": "ttfautohint version used in Stage 2" }
      }
    },
    "font_files": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "filename": { "type": "string" },
          "format": { "type": "string", "enum": ["ttf", "otf", "woff", "woff2", "svg"] },
          "size_bytes": { "type": "integer" },
          "sha256": { "type": "string" }
        }
      }
    },
    "spdx_license": { "type": "string", "const": "OFL-1.1" }
  }
```

### 4.7 Release Body Format

Location: GitHub Release auto-generated notes body

Every successful build SHALL publish a GitHub Release whose body (auto-generated notes) includes the following sections:

1. **Resolved Options Table**: A markdown table listing all four options (`LargeLineHeight`, `NoLoopK`, `NoCalt`, `UseHinted`) with their resolved boolean values.
2. **Included Font Files Summary**: A markdown table listing each font file name, format (TTF/OTF/WOFF/WOFF2/SVG), weight, and SHA-256 checksum. This is a summary — the full manifest with complete checksums is available inside the archive.
3. **Build Metadata**: Build timestamp (ISO 8601 UTC), source commit SHA (linked to the commit on GitHub), and a direct link back to the workflow run.

The release body is generated programmatically by the workflow (e.g., via a script that reads `manifest.json` and formats it into markdown). The full `manifest.json` is included in the archive — the release body provides a human-readable preview.

## 5. Acceptance Criteria

- **AC-001 (Default Execution)**:
  - Given a fork with no `config.json` or an empty `{}` object,
  - When the user runs the workflow via `workflow_dispatch` without changing form defaults,
  - Then `configure.py` SHALL set all options to defaults (`config_source: "defaults"`),
  - And the build SHALL produce all 4 weights in TTF, OTF, WOFF, WOFF2, SVG formats,
  - And the release title SHALL be `Custom Build: Normal (default)`.

- **AC-002 (`config.json` Execution)**:
  - Given a fork with `config.json` containing `{"NoLoopK": true}`,
  - When the user runs the workflow without form overrides,
  - Then `configure.py` SHALL set `NoLoopK=true` and `config_source: "config.json"`,
  - And the generated fonts SHALL contain straight 'k' glyphs,
  - And the release title SHALL be `Custom Build: NoLoopK`.

- **AC-003 (Form Override Precedence)**:
  - Given a fork with `config.json` containing `{"LargeLineHeight": false}`,
  - When the user runs `workflow_dispatch` with `large_line_height=true`,
  - Then `configure.py` SHALL resolve `LargeLineHeight=true` with `config_source: "form_override"`,
  - And the build log SHALL display `Using form value (overrides config.json) for large_line_height`.

- **AC-004 (Schema Validation Failure)**:
  - Given a `config.json` with invalid data type `{"NoCalt": "yes"}`,
  - When the validation step executes,
  - Then the step SHALL fail with exit code `1`,
  - And log `Invalid config.json: 'NoCalt' must be a boolean, got string`.

- **AC-005 (Release Title & Asset Generation)**:
  - Given a successful build with `UseHinted=false` and `NoCalt=true`,
  - Then the GitHub Release tag SHALL be `custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}`,
  - And the title SHALL be `Custom Build: NoCalt (unhinted)`,
  - And both `.zip` and `.tar.gz` SHALL be attached as release assets.

## 6. Test Automation Strategy

### 6.1 Test Levels

1. **Micro Level (Unit Tests)**:
   - Python unit tests (`tests/test_configure.py`) targeting `configure.py`:
     - Test precedence resolution logic (`form` vs `config.json` vs `defaults`).
     - Test schema validation with valid, invalid, empty, and unknown-key configs.
     - Test `manifest.json` generation and checksum calculations.
2. **Macro Level (Integration & Container Tests)**:
   - Container smoke test (`docker build -t custom-build-test .`):
     - Validates Stage 1 FontForge compilation output.
     - Validates Stage 2 Python 3.14 execution, `ttfautohint`, and `woff2_compress`.
   - Local workflow test via `act` or dry-run GitHub Actions script.

### 6.2 Test Data & CI/CD Integration

- Test fixtures located in `tests/fixtures/configs/` (`valid_config.json`, `invalid_config.json`, `empty_config.json`).
- All python unit tests MUST execute via `pytest` in CI before invoking Docker compilation.

## 7. Rationale, Context & Architecture Decisions (ADRs)

- **ADR Reference**: This specification directly enforces [`docs/adr/0002-multi-stage-docker-deferred-engine-port.md`](file:///d:/WebstormProject/fantasque-sans/docs/adr/0002-multi-stage-docker-deferred-engine-port.md).
- **Rationale**:
  - The variant engine (`fontbuilder.py`, `features.py`) and entry point (`build.py`) remain on Python 2.7 because `build.py` imports them in-process (`from fontbuilder import *`).
  - Splitting engine execution across Python versions without rewriting `build.py` is impossible.
  - Rewriting `build.py` is explicitly prohibited by NG-9 in V1.
  - Therefore, a multi-stage Docker setup isolates legacy Python 2.7 font generation in Stage 1, while providing Python 3.14 in Stage 2 for post-build packaging tooling only. Configuration is performed by `configure.py` on the GitHub Actions host runner (per §4.4), not inside any container.

## 8. Dependencies & External Integrations

### 8.1 External Systems

- **EXT-001**: GitHub Actions API & Runner Environment (`ubuntu-latest`).
- **EXT-002**: GitHub Releases & Artifacts Storage Service.

### 8.2 Third-Party Services / Tooling

- **SVC-001**: `ppa:fontforge/fontforge` (Stage 1 FontForge + Python 2.7 dependencies).
- **SVC-002**: `ppa:deadsnakes/ppa` (Stage 2 Python 3.14 package distribution).
- **SVC-003**: `ttfautohint`, `woff-tools`, `woff2` (Ubuntu 26.04 universe binaries).

### 8.3 Infrastructure & Data Dependencies

- **INF-001**: GitHub Actions runner disk space (minimum 10 GB available for multi-stage Docker build).
- **DAT-001**: Upstream `.sfdir` source font files in `Sources/`.

## 9. Examples & Edge Cases

### 9.1 Wrapper Resolution Example (`Scripts/configure.py`)

```python
import json
import jsonschema

def resolve_options(config_data, form_inputs):
    defaults = {
        "LargeLineHeight": False,
        "NoLoopK": False,
        "NoCalt": False,
        "UseHinted": True
    }
    
    resolved = {}
    sources = {}
    
    for key, default_val in defaults.items():
        form_key = key_to_snake_case(key)
        form_val = form_inputs.get(form_key)
        config_val = config_data.get(key) if config_data else None
        
        if form_val is not None and form_val != default_val:
            if config_val is not None:
                sources[key] = "form_override"
            else:
                sources[key] = "form"
            resolved[key] = form_val
        elif config_val is not None:
            sources[key] = "config.json"
            resolved[key] = config_val
        else:
            sources[key] = "defaults"
            resolved[key] = default_val

    return resolved, sources


def compute_config_source(sources, has_config_file):
    """Compute build-level config_source from per-option sources.

    Hierarchy (highest priority wins as single string):
      1. If ANY option source == "form_override" → "form_override"
      2. elif has_config_file and sources has "config.json" entries
         without any "form" entries → "config.json"
      3. elif any source == "form" (a form input differed from default,
         no config.json present) → "form"
      4. else → "defaults"
    """
    if "form_override" in sources.values():
        return "form_override"
    if has_config_file and not any(s == "form" for s in sources.values()):
        if any(s == "config.json" for s in sources.values()):
            return "config.json"
    if any(s == "form" for s in sources.values()):
        return "form"
    return "defaults"
```

`sources` (per-option) is used for debug logging in the workflow output — one line per option naming its source. The single `config_source` value written to `manifest.json` is computed by `compute_config_source()` using the hierarchy above. When no `config.json` is present and form inputs are provided, the per-option source is `"form"` and the build-level `config_source` is also `"form"`. When a form input overrides a `config.json` value, the per-option source is `"form_override"` and the overall `config_source` becomes `"form_override"` (even if other options still come from `config.json`).

### 9.2 Release Title Generator Matrix

| Resolved Options                 | Release Title                     |
| -------------------------------- | --------------------------------- |
| All Defaults                     | `Custom Build: Normal (default)`  |
| `LargeLineHeight=true`           | `Custom Build: LargeLineHeight`   |
| `NoLoopK=true`, `NoCalt=true`    | `Custom Build: NoLoopK + NoCalt`  |
| `NoCalt=true`, `UseHinted=false` | `Custom Build: NoCalt (unhinted)` |
| `UseHinted=false`                | `Custom Build: Normal (unhinted)` |

## 10. Validation Criteria

To achieve full compliance with this Technical Specification, implementation artifacts MUST satisfy:

1. `config.schema.json` validates against JSON Schema Draft-07 standard using `jsonschema`.
2. `Scripts/configure.py` passes 100% of unit tests covering precedence, validation, and manifest output.
3. Multi-stage `Dockerfile` completes `docker build` cleanly without stage coupling failures.
4. `.github/workflows/custom-build.yml` successfully triggers on `workflow_dispatch`, produces `.zip` and `.tar.gz` artifacts, and publishes tagged GitHub Release on test fork.
5. All archives contain valid `manifest.json` matching checksums of output `.ttf`, `.otf`, `.woff`, `.woff2`, and `.svg` files.

## 11. Related Specifications / Further Reading

- [PRD — Custom Build via GitHub Workflow](file:///d:/WebstormProject/fantasque-sans/docs/prd-20260723-1130-custom-build-workflow.md)
- [ADR 0002 — Multi-Stage Docker Build with Deferred Engine Port](file:///d:/WebstormProject/fantasque-sans/docs/adr/0002-multi-stage-docker-deferred-engine-port.md)
- [Fantasque Sans Mono Domain Glossary](file:///d:/WebstormProject/fantasque-sans/CONTEXT.md)

---

## 12. Revision History

| Version | Date       | Author                  | Changes                                                                                                                                                                                                                                                       |
| ------- | ---------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.4     | 2026-07-24 | Specification Architect | Surgical fixes per re-audit r2 ([`docs/audit/consistency-audit-custom-build-workflow-2026-07-24-r2.md`](file:///d:/WebstormProject/fantasque-sans/docs/audit/consistency-audit-custom-build-workflow-2026-07-24-r2.md)): **R-2** corrected §7 line 344 rationale to state Stage 2 Python 3.14 is for post-build packaging only and `configure.py` runs on the GitHub Actions host runner per §4.4 (not inside any container); **R-3** added `config_source` to the §4.6 `manifest.json` top-level `required` array (between `font_files` and `spdx_license`) per PRD FR-8 mandate. |
