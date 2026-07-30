# 0001 - Multi-Stage Docker Build for Legacy Toolchain
**Date:** 2026-07-23
**Status:** Superseded by ADR-0002

## Context
The Fantasque Sans Mono build pipeline (`Scripts/build.py`, `Scripts/fontbuilder.py`) is written in Python 2.7 and requires FontForge compiled with Python 2.7 support. Both dependencies are unavailable on Ubuntu 24.04 LTS: the DeadSnakes PPA no longer builds Python 2.7 for Ubuntu 22.04+ (it requires `libssl<3`), and `ppa:fontforge/fontforge` does not support releases after Eoan 19.10. On the other hand, the V1 Custom Build requires a container based on a modern Ubuntu LTS (24.04 or 22.04) for security and long-term support — `ubuntu:18.04` has been EOL since April 2023. The "Wrap, Don't Rewrite" principle forbids modifying or rewriting the existing build pipeline.

## Decision
Use a **multi-stage Docker build** strategy: Stage 1 (`ubuntu:18.04` + `ppa:fontforge/fontforge`) provides the Python 2.7 and FontForge binaries (with Python 2.7 support). Stage 2 (`ubuntu:24.04`) copies those binaries together with their library dependencies and serves as the final container where the build runs. Other modern tools (`ttfautohint`, `sfnt2woff`, `woff2_compress`) are installed directly from the Ubuntu 24.04 universe repository.

## Consequences
- **Positive**: The existing build pipeline is left entirely untouched — fully honoring "Wrap, Don't Rewrite". The final container runs on Ubuntu 24.04, which still receives security patches until 2029.
- **Negative**: The Dockerfile becomes more complex (two stages, manual binary copying). Python 2.7 and FontForge binary compatibility across glibc versions (2.27 → 2.39) must be verified and may cause hard-to-debug runtime issues. If GitHub Actions ever drops support for the `ubuntu:18.04` container, Stage 1 must be replaced with an alternative mechanism.
- **Long-term risk**: This is a tactical, not strategic, solution. The build pipeline must eventually be migrated to Python 3 — when that happens, this ADR becomes obsolete and the multi-stage build can be removed.

## Considered Options
- **Rewrite build scripts to Python 3**: Rejected because it fundamentally violates "Wrap, Don't Rewrite" and requires full verification of font output (reproducibility, FontForge Python 3 API compatibility).
- **Drop to Ubuntu 22.04 + focal repo**: Rejected because mixing different Ubuntu version repositories risks dependency conflicts that are hard to maintain, and does not solve the Python 2.7 problem (still unavailable on 22.04).
- **Use base image `python:2.7-slim` (Debian Buster)**: Rejected because mixing Debian and Ubuntu ecosystems in one container increases library incompatibility risk, and Debian Buster is also EOL.

## Supersession Note (2026-07-23)

This decision was superseded by the clarified PRD v1.2 (after the Clarification Analyst checkpoint), which further revised the strategy from **"Wrap, Don't Rewrite"** to a **deferred-engine-port** approach:

- **`Scripts/build.py`** (Makefile entry point) remains in Python 2.7 — Stage 1 Docker is still required to provide the Python 2.7 + FontForge runtime.
- **`Scripts/fontbuilder.py`** and **`Scripts/features.py`** are **NOT ported**; they remain on Python 2.7 for V1 and run in Stage 1 alongside `build.py` (because `build.py` imports them in-process via `from fontbuilder import *`, splitting across Python versions is impossible without violating NG-9). Their port to Python 3.14 is **deferred to V2**.
- **Stage 2** uses **Ubuntu 26.04 LTS** (up from 24.04) with **Python 3.14** (installed explicitly via deadsnakes PPA or pyenv), hosting only `configure.py` (Python 3.14) and the post-build packaging tooling.

ADR-0002 documents this new multi-stage Docker architecture formally. Until ADR-0002 is ratified in the Spec/Plan phase, PRD v1.2 §8.3 Challenge 1 & 2 is the authoritative reference for the build architecture decision.
