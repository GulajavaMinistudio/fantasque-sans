# =============================================================================
# Fantasque Sans Mono -- Custom Build (multi-stage, per Spec v1.5 §4.5 /
# ADR-0002).
#
# Stage 1 ("builder-fontforge") compiles the font using the legacy
# Python 2.7 + FontForge toolchain -- ``Scripts/build.py`` /
# ``Scripts/fontbuilder.py`` / ``Scripts/features.py`` are imported by
# ``Scripts/custom_build_driver.py`` and MUST NOT be modified (CON-001).
#
# Stage 2 ("final") packages the compiled outputs on a modern
# Ubuntu 26.04 + Python 3.14 image. Stage 2 is responsible for ttfautohint,
# WOFF/WOFF2 compression, manifest assembly, and zip/tar packaging
# (Spec §4.5). The build args resolved by ``Scripts/configure.py`` on
# the host runner are forwarded into Stage 1 via the ``BUILD_ARGS`` ARG.
# =============================================================================


# -----------------------------------------------------------------------------
# Stage 1: legacy FontForge + Python 3.x build environment
# -----------------------------------------------------------------------------
FROM ubuntu:26.04 AS builder-fontforge

ENV DEBIAN_FRONTEND=noninteractive

# FontForge from the default Ubuntu 26.04 (resolute) repos. The team PPA
# ``ppa:fontforge/fontforge`` does NOT support ``resolute`` (404) so we
# use the distro package.
# ``python3-fontforge`` (apt) installs the SYSTEM FontForge Python module:
# the bindings embedded in the FontForge binary are NOT visible to the
# system ``python3`` that runs pytest, so without this package the four
# FontForge-dependent test files would always be importorskip-skipped
# (clarification r5 B1).
# ``ca-certificates`` is required for ``apt-get update`` over HTTPS.
# ``python3-pip`` is required because ``python3-future`` was removed
# from Ubuntu 26.04 main repos; we install ``future`` from PyPI instead
# (legacy ``from past.builtins import xrange`` in fontbuilder.py needs it).
# pytest/jsonschema/pytest-cov are installed UNCONDITIONALLY (r3 K2,
# r5 MO-1, r6 Q-02) — the multi-weight RUN chain runs the unit suite with
# coverage inside Stage 1.
# ``make`` is kept around for the legacy ``Makefile`` smoke path.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        fontforge \
        python3-fontforge \
        python3-pip \
        make \
    && pip3 install --break-system-packages --no-cache-dir future pytest jsonschema pytest-cov \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build

# The driver script reads ``Sources/`` relative to WORKDIR; the entire
# repository is needed at this stage so that ``Scripts/custom_build_driver.py``
# and the legacy ``fontbuilder.py`` / ``features.py`` are importable.
# ``COPY . /build`` keeps the layout identical to the local checkout.
COPY . /build

# Resolved build args forwarded by ``Scripts/configure.py`` (host runner).
# Default is empty so a no-flag dispatch produces the ``Normal`` variant
# (Spec AC-001). The driver parses this as a list of space-separated
# flags (``--line-height``, ``--no-loop-k``, ``--no-calt``) — the
# build-level ``--multi-weight`` flag is stripped before the driver
# invocation (see the final RUN below).
ARG BUILD_ARGS=""

# T_FINAL: tangent-angle fail-fast threshold for interpolation validation
# (Spec r5 B2 + §4.11). Sourced at BUILD time from
# docs/audit/phase0-experiments-{date}.md + docs/audit/visual-quality-rubric.md
# (r5 B2); ``15.0`` is the PRE-CALIBRATION default until the PoC two-pass
# protocol lands (plan TASK-4.2 / NOTE-4.2). Override per build with:
#   docker build --build-arg T_FINAL=<calibrated-value> ...
ARG T_FINAL=15.0
ENV T_FINAL=${T_FINAL}

# Base ``build/`` directory: Stage 2 ``COPY --from=builder-fontforge
# /build/build /app/build-reports`` requires the source path to exist in
# BOTH modes, so the base dir is created unconditionally. The
# ``build/reports/`` subdirectory (coverage.xml) is created inside the
# multi-weight RUN chain only — single-weight mode keeps it empty
# (NIT-002, TASK-304; clarification r5 H3, r6 Q-02).
RUN mkdir -p build

# Multi-weight branch (active iff BUILD_ARGS contains ``--multi-weight``).
# Contract: Spec §4.9 + plan TASK-4.2 (i)-(v). Order per r6 Q-02:
#   (v) existence guard for harmonized sources — FIRST (r4 R5)
#   (i) detect_incompatibility.py — informative/audit baseline (r6 Q-16)
#   (ii) validate_harmonization.py --strict for BOTH master pairs (r3 K4)
#   (iii) pytest --cov — BEFORE interpolation (r6 Q-02)
#   (iv) multi_weight_driver.py — core weights + build/sources/ assembly
#   (v) fail-fast loop validate_interpolation.py --threshold ${T_FINAL}
#       --fail-fast per core weight (GUD-002, r3 K8)
# T_FINAL comes from the ``ARG T_FINAL`` / ``ENV T_FINAL`` declared above
# (REF-003): the value can be overridden at build time by the runbook once
# the calibration protocol lands (docs/audit/visual-quality-rubric.md,
# r5 B2). The default ``15.0`` is the pre-calibration placeholder (plan
# TASK-4.2 / NOTE-4.2).
RUN if echo "$BUILD_ARGS" | grep -q -- "--multi-weight"; then \
        echo "::notice::multi-weight build: checking harmonized sources..." \
        && python3 -c "import fontforge" \
        && { test -d Sources/Harmonized/Regular && test -d Sources/Harmonized/Bold \
             && test -d Sources/Harmonized/Italic && test -d Sources/Harmonized/BoldItalic; } \
        || { echo "::error::multi-weight build requires harmonized sources (Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}); sync upstream or run harmonization first" >&2; exit 1; } \
        && echo "::notice::multi-weight build: Detecting incompatibilities..." \
        && fontforge --quiet -lang=py -script Scripts/detect_incompatibility.py \
               Sources/FantasqueSansMono-Regular.sfdir Sources/FantasqueSansMono-Bold.sfdir \
               --output build/incompatibility_report.json \
        && echo "::notice::multi-weight build: Harmonizing (validating masters, --strict, both pairs)..." \
        && fontforge --quiet -lang=py -script Scripts/validate_harmonization.py \
               Sources/Harmonized/Regular Sources/Harmonized/Bold \
               --strict --output build/harmonization_report-rb.json \
        && fontforge --quiet -lang=py -script Scripts/validate_harmonization.py \
               Sources/Harmonized/Italic Sources/Harmonized/BoldItalic \
               --strict --output build/harmonization_report-ib.json \
        && mkdir -p build/reports \
        && echo "::notice::multi-weight build: running unit tests with coverage (Spec §6.7 gate: --cov-fail-under=90, REF-008)..." \
        && pytest tests/ -v --cov=Scripts --cov-report=term-missing \
               --cov-report=xml:build/reports/coverage.xml \
               --cov-fail-under=90 \
        && echo "::notice::multi-weight build: Interpolating core weights (Medium 500, SemiBold 600)..." \
        && fontforge --quiet -lang=py -script Scripts/multi_weight_driver.py \
               --sources Sources --output Sources/Harmonized/Interpolated \
        && echo "::notice::multi-weight build: Validating interpolated weights (fail-fast, T_FINAL=${T_FINAL})..." \
        && fontforge --quiet -lang=py -script Scripts/validate_interpolation.py \
               --interpolated Sources/Harmonized/Interpolated/Medium \
               --masters Sources/Harmonized --threshold "${T_FINAL}" --fail-fast \
               --output build/interpolation-medium.json \
        && fontforge --quiet -lang=py -script Scripts/validate_interpolation.py \
               --interpolated Sources/Harmonized/Interpolated/SemiBold \
               --masters Sources/Harmonized --threshold "${T_FINAL}" --fail-fast \
               --output build/interpolation-semibold.json \
        && echo "::notice::multi-weight build: assembled build/sources/ (7 .sfdir)"; \
    fi

# Compile the resolved Variant across all ``.sfdir`` weights. Multi-weight
# mode feeds the assembled ``build/sources/`` (4 harmonized masters +
# Medium + SemiBold + FantasqueSans); normal mode keeps the legacy
# ``Sources/`` root — byte-identical output (AC-B03). ``--multi-weight``
# is STRIPPED from ``$BUILD_ARGS`` before the driver invocation —
# ``parse_args()`` _die's on unknown flags (clarification r3 K1).
RUN FONTS=Sources; \
    if echo "$BUILD_ARGS" | grep -q -- "--multi-weight"; then FONTS=build/sources; fi; \
    DRIVER_ARGS=$(printf '%s' "$BUILD_ARGS" | sed 's/--multi-weight//g'); \
    fontforge --quiet -lang=py -script \
        Scripts/custom_build_driver.py \
        "$FONTS" /build $DRIVER_ARGS


# -----------------------------------------------------------------------------
# Stage 2: modern packaging environment (Ubuntu 26.04 + Python 3.14)
# -----------------------------------------------------------------------------
FROM ubuntu:26.04 AS final

ENV DEBIAN_FRONTEND=noninteractive

# Ubuntu 26.04 universe ships ``ttfautohint`` / ``woff-tools`` / ``woff2``;
# Python 3.14 is pulled from the deadsnakes PPA (SPEC DEP-004) because
# 26.04's default python3 may lag. ``zip`` / ``tar`` are mandatory for
# the archive assembly in Phase 3 TASK-026.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        software-properties-common \
        ca-certificates \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        python3.14 \
        python3.14-venv \
        ttfautohint \
        woff-tools \
        woff2 \
        zip \
        tar \
        jq \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the compiled outputs from Stage 1. Three COPYs keep the layer
# graph explicit (no glob, no ``COPY --chown`` surprises).
COPY --from=builder-fontforge /build/OTF /app/OTF
COPY --from=builder-fontforge /build/TTF /app/TTF
COPY --from=builder-fontforge /build/Webfonts /app/Webfonts

# Copy the multi-weight build reports (JSON validation reports +
# coverage.xml) so Stage 2 can surface them to ``output/reports/``
# (clarification r5 H3, r6 Q-02). Present in both modes (empty in
# single-weight mode).
COPY --from=builder-fontforge /build/build /app/build-reports

# Copy the repository root so packaging tooling (Phase 3 workflow steps)
# can reach ``LICENSE.txt``, ``README.md``, and the manifest mount point.
# Mounting ``manifest.json`` at runtime is the workflow's responsibility
# (Phase 3 TASK-026 -- ``docker run -v``).
COPY . /app

# Default entry point: the packaging driver implemented in Phase 3. The
# V1 build pipeline is triggered by the GitHub Actions workflow, not by
# ``docker run`` directly, so this CMD is a documentation aid only
# (per Spec §1.2 "FR-11 permits replacement provided ``docker build &&
# docker run`` remains documented").
CMD ["bash", "-c", "echo 'Use the GitHub Actions workflow or run configure.py + docker build per docs/CUSTOM-BUILD.md' && exit 0"]
