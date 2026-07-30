# 0002 - Multi-Stage Docker Build with Deferred Engine Port

**Date:** 2026-07-23
**Status:** Accepted

## Context
The V1 Custom Build must compile the font in a cloud-hosted container. The existing build pipeline (`Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`) is written in Python 2.7 (EOL 2020-01-01) and requires FontForge compiled with Python 2.7 support — these are unavailable on modern Ubuntu LTS. `Scripts/build.py` is the Makefile entry point and, per NG-9, must remain unchanged in V1; critically, `build.py` imports `fontbuilder` and `features` **in-process** (`from fontbuilder import *`), so the variant engine cannot be split onto a different Python version than `build.py` without rewriting `build.py` (forbidden by NG-9). Meanwhile V1 introduces a new Python 3.14 configuration layer (`configure.py`) and modern post-build packaging tooling (`ttfautohint`, `sfnt2woff`, `woff2_compress`). The legacy `ubuntu:18.04` base image is EOL. ADR-0001 (Stage 2 = ubuntu:24.04) is superseded.

## Decision
Adopt a **multi-stage Docker build** where:
- **Stage 1** (`ubuntu:18.04` + `ppa:fontforge/fontforge`) provides the Python 2.7 + FontForge runtime and executes the **entire font compilation** (`build.py` + `fontbuilder` + `features`) in-process on Python 2.7.
- **Stage 2** (`Ubuntu 26.04 LTS` with **Python 3.14** installed explicitly via the deadsnakes PPA or pyenv, since the distro default may be 3.13) provides the Python 3.14 runtime for **post-build packaging tooling only**; the `configure.py` wrapper runs on the **GitHub Actions host runner** (not inside the container) and passes resolved build args to Stage 1 via `docker build --build-arg` (per Technical Specification §4.4/§4.5).
- The port of `Scripts/fontbuilder.py` and `Scripts/features.py` to Python 3.14 is **deferred to V2**; they remain Python 2.7 in V1 and run in Stage 1.

## Consequences
- FontForge's Python 2.7 binary from Stage 1 must be verified compatible with Stage 2's glibc; this is a known cross-version risk that the Engineering Team must validate.
- Engine modernization (the Python 3 port) is explicitly a V2 effort, keeping V1 scope tight and avoiding font-reproducibility risk from a Python migration.
- If GitHub Actions ever drops support for the `ubuntu:18.04` container, Stage 1 requires an alternative mechanism.
- Stage 2 provides a forward-looking Python 3.14 surface for post-build packaging tooling (the `configure.py` wrapper runs on the host runner, not in Stage 2; supports BG-5, the "forward-looking" goal).

## Considered Options
- **Partial port (engine to Python 3.14 in Stage 2)**: Rejected during the Clarification checkpoint — `build.py` imports `fontbuilder`/`features` in-process, so they cannot run on Python 3.14 while `build.py` stays on Python 2.7 without violating NG-9.
- **Rewrite `build.py` to Python 3 (relax NG-9)**: Rejected to honor NG-9 and avoid full font-output re-verification; deferred to V2 as a dedicated effort.

## Revision Note (2026-07-23)

The Decision and Consequences were corrected during the Clarification Analyst checkpoint to reflect that the `configure.py` wrapper executes on the **GitHub Actions host runner** (not inside the Stage 2 container) and passes resolved build args to Stage 1 via `docker build --build-arg`. Stage 2's Python 3.14 runtime is used for post-build packaging tooling only. This aligns the ADR with Technical Specification `spec/spec-custom-build-workflow.md` §1.2, §4.4, and §4.5, and with PRD `docs/prd-20260723-1130-custom-build-workflow.md` §4.4 / §8.3. The architectural intent (multi-stage Docker, deferred engine port, NG-9 preservation) is unchanged.
