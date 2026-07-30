#!/usr/bin/env fontforge
# -*- coding: utf-8 -*-
"""
Fantasque Sans Mono Custom Build -- Stage 1 driver (Python 2.7).

Runs inside the FontForge embedded Python 2.7 interpreter during Stage 1 of
the multi-stage Docker build (per Spec v1.5 section 4.5 and ADR-0002).
Receives the resolved build arguments from ``Scripts/configure.py`` via
``docker build --build-arg BUILD_ARGS=...``.

Usage (inside Stage 1, WORKDIR=/build):

    fontforge -lang=py -script Scripts/custom_build_driver.py \\
        SOURCES_DIR OUTPUT_DIR [--line-height] [--no-loop-k] [--no-calt]

Contract (Spec section 4.4):

    * Parses ``SOURCES_DIR OUTPUT_DIR`` and the optional flags above.
    * Declares ONLY the active (resolved) options in the ``fontbuilder``
      registry. Legacy ``Scripts/build.py`` declares all options and lets
      ``build_batch`` slice a permutation; the driver side-steps the
      permutation matrix by registering only what the workflow resolved.
    * Replicates the core loop of ``Scripts/fontbuilder.py::_build()`` for
      exactly one combination per ``.sfdir`` in SOURCES_DIR:
        1. ``fontforge.open(sfdir_path)``
        2. Apply non-NoCalt operations (Line, SwapLookup).
        3. ``update_features(fnt)`` to compile the calt/liga lookups.
        4. If ``--no-calt``, apply ``DropCAltAndLiga()`` AFTER step 3 so the
           just-added lookups are removed (legacy order is a no-op because
           the lookups did not yet exist; corrected here to satisfy AC-005
           and the TASK-013(d) gate).
        5. Generate TTF + OTF + SVG into ``OUTPUT_DIR/{TTF,OTF,Webfonts}/``.
    * MUST NOT invoke ``ttfautohint`` / ``sfnt2woff`` / ``woff2_compress``
      (Stage 2 responsibilities per Spec section 1.2 and section 4.4).
    * Sets ``SOURCE_DATE_EPOCH`` in the driver environment to mitigate
      FontForge output non-determinism (PRD US-015, RISK-006). Byte-identity
      is NOT a V1 requirement -- this is mitigation only.
    * Exits with a non-zero code and a single diagnostic line on failure.

CON-001 invariant: ``Scripts/build.py``, ``Scripts/fontbuilder.py`` and
``Scripts/features.py`` are imported here but MUST NOT be modified.
"""

import os
import sys
from os.path import basename, isdir, join, splitext

# ---------------------------------------------------------------------------
# Determinism mitigation (RISK-006 / PRD US-015)
# ---------------------------------------------------------------------------
# Set BEFORE importing fontforge so the embedded Python interpreter sees the
# value. Pinned to a fixed UTC instant (2026-01-01T00:00:00Z = 1735689600).
# Byte-identity is NOT guaranteed; this only reduces variation in embedded
# timestamps. See plan Risk 006 and Assumption 002.
SOURCE_DATE_EPOCH = "1735689600"
os.environ["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH

# ---------------------------------------------------------------------------
# Import path setup so the legacy engine modules are reachable.
# ---------------------------------------------------------------------------
SCRIPTS_DIR = os.path.dirname(os.path.realpath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# fontforge is provided by the Stage 1 base image; the import will fail
# under a stock Python interpreter (which is the expected behavior outside
# ``fontforge -lang=py -script``).
import fontforge  # noqa: E402

from fontbuilder import (  # noqa: E402
    Line,
    SwapLookup,
    DropCAltAndLiga,
    option as _register_option,
)
from features import update_features as _update_features  # noqa: E402


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def _die(msg):
    """Print diagnostic to stderr and exit non-zero (Spec section 4.4: fail-fast)."""
    sys.stderr.write("custom_build_driver: " + str(msg) + "\n")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args(argv):
    """Parse ``SOURCES_DIR OUTPUT_DIR [--line-height] [--no-loop-k] [--no-calt]``.

    Returns a 5-tuple ``(sources_dir, output_dir, line_height, no_loop_k, no_calt)``
    on success, or ``None`` when usage is invalid (after printing the usage).
    """
    if len(argv) < 3:
        sys.stderr.write(
            "Usage: fontforge -lang=py -script custom_build_driver.py "
            "SOURCES_DIR OUTPUT_DIR [--line-height] [--no-loop-k] [--no-calt]\n"
        )
        return None

    sources_dir = argv[1]
    output_dir = argv[2]
    flags = set(argv[3:])

    known_flags = ("--line-height", "--no-loop-k", "--no-calt")
    unknown = sorted(flags - set(known_flags))
    if unknown:
        _die("unknown flag(s): " + " ".join(unknown))

    return (
        sources_dir,
        output_dir,
        "--line-height" in flags,
        "--no-loop-k" in flags,
        "--no-calt" in flags,
    )


# ---------------------------------------------------------------------------
# Option registry population
# ---------------------------------------------------------------------------

def declare_options(line_height, no_loop_k, no_calt):
    """Register the resolved Variant in the ``fontbuilder`` option registry.

    Only the active options are declared; the legacy engine's
    ``_expand_options(bitmap)`` is bypassed by the driver (it iterates the
    registry directly to avoid the permutation matrix).
    """
    if line_height:
        # Mirrors ``Scripts/build.py`` line 36 exactly (Line(1750, 498)).
        _register_option(
            "LargeLineHeight", "Large Line Height", Line(1750, 498)
        )

    if no_loop_k:
        # Mirrors ``Scripts/build.py`` line 41 (SwapLookup('ss01')).
        _register_option("NoLoopK", "No loop k", SwapLookup("ss01"))

    if no_calt:
        # The legacy ``build.py`` has this declaration commented out (line
        # 52). The driver re-enables it for the V1 workflow -- the actual
        # removal happens AFTER ``update_features()`` runs (see
        # ``build_one_weight``) so the lookups are actually dropped.
        _register_option(
            "NoCalt", "Turn off contextual alternates", DropCAltAndLiga()
        )


# ---------------------------------------------------------------------------
# Source discovery
# ---------------------------------------------------------------------------

def find_sfdirs(sources_dir):
    """Yield absolute ``.sfdir`` paths under ``sources_dir`` (sorted).

    Sorting keeps the build order deterministic across hosts (FontForge
    does not guarantee directory iteration order).
    """
    if not isdir(sources_dir):
        _die("SOURCES_DIR does not exist or is not a directory: " + sources_dir)

    found = sorted(
        join(sources_dir, name)
        for name in os.listdir(sources_dir)
        if name.endswith(".sfdir")
    )
    if not found:
        _die("no .sfdir sources found in " + sources_dir)
    return found


# ---------------------------------------------------------------------------
# Per-weight build
# ---------------------------------------------------------------------------

def _apply_registry_op(fnt, abbrev):
    """Apply every operation registered under ``abbrev`` to ``fnt``."""
    from fontbuilder import option as _opt
    operations = _opt.operations.get(abbrev)
    if not operations:
        _die(
            "internal: option '{0}' is not in the fontbuilder registry"
            .format(abbrev)
        )
    for oper in operations:
        oper(fnt)


def _ensure_dir(path):
    try:
        os.makedirs(path)
    except OSError:
        # Directory already exists -- not an error.
        pass


def build_one_weight(sfdir_path, output_dir, line_height, no_loop_k, no_calt):
    """Open one ``.sfdir``, apply the resolved Variant, and emit TTF/OTF/SVG.

    Mirrors the body of ``Scripts/fontbuilder.py::_build()`` with two
    intentional V1 adjustments:

      * The output directory is the caller-supplied ``output_dir`` directly
        (no per-variant subdirectory) because the driver compiles exactly
        one Variant. Spec section 4.4 mandates ``OUTPUT_DIR/TTF/`` etc.
      * The legacy ``subprocess.check_call`` to ``generate-other-formats``
        and ``generate-css-decl`` is INTENTIONALLY OMITTED. WOFF/WOFF2
        compression is Stage 2 territory (Spec section 4.4: "MUST NOT
        invoke ... ``sfnt2woff`` / ``woff2_compress``"), and the CSS
        declaration is regenerated by the workflow from the manifest.
    """
    name = splitext(basename(sfdir_path))[0]
    print("Generating " + name)

    fnt = fontforge.open(sfdir_path)
    try:
        # Phase A: non-NoCalt operations (no lookup-table side effects).
        if line_height:
            _apply_registry_op(fnt, "LargeLineHeight")
        if no_loop_k:
            _apply_registry_op(fnt, "NoLoopK")

        # Phase B: compile calt/liga lookups from the .liga glyphs.
        _update_features(fnt)

        # Phase C: drop the just-added calt/liga lookups when --no-calt
        # was requested. Must run AFTER update_features -- see module
        # docstring for the legacy-order bug rationale.
        if no_calt:
            _apply_registry_op(fnt, "NoCalt")

        # Phase D: ensure output dirs exist and generate the three formats.
        ttf_dir = join(output_dir, "TTF")
        otf_dir = join(output_dir, "OTF")
        web_dir = join(output_dir, "Webfonts")
        for d in (ttf_dir, otf_dir, web_dir):
            _ensure_dir(d)

        fnt.generate(
            join(ttf_dir, name + ".ttf"),
            flags=("opentype", "dummy-dsig"),
        )
        fnt.generate(
            join(otf_dir, name + ".otf"),
            flags=("opentype", "dummy-dsig"),
        )
        fnt.generate(join(web_dir, name + ".svg"))
    finally:
        fnt.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv):
    parsed = parse_args(argv)
    if parsed is None:
        return 2  # usage error

    sources_dir, output_dir, line_height, no_loop_k, no_calt = parsed

    declare_options(line_height, no_loop_k, no_calt)

    for sfdir in find_sfdirs(sources_dir):
        build_one_weight(sfdir, output_dir, line_height, no_loop_k, no_calt)

    print("custom_build_driver: done")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
