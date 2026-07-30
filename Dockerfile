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

# FontForge from the team PPA provides the fontforge binary on Ubuntu 26.04.
# software-properties-common enables add-apt-repository; rm -rf keeps the
# layer small. make is kept around for the legacy Makefile smoke path.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        software-properties-common \
        ca-certificates \
    && add-apt-repository -y ppa:fontforge/fontforge \
    && apt-get update \

# python-future provides the 'past' module that fontbuilder.py imports
# (``from past.builtins import xrange`` is a Py2/3 compatibility shim).
    && apt-get install -y --no-install-recommends \
        fontforge \
        python3-fontforge \
        python3-future \
        make \
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
# flags (``--line-height``, ``--no-loop-k``, ``--no-calt``).
ARG BUILD_ARGS=""

# Compile the resolved Variant across all ``.sfdir`` weights into
# ``/build/{TTF,OTF,Webfonts}``. No hinting, no WOFF/WOFF2 here -- those
# are Stage 2 responsibilities per Spec §1.2.
RUN fontforge --quiet -lang=py -script \
        Scripts/custom_build_driver.py \
        Sources /build $BUILD_ARGS


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
