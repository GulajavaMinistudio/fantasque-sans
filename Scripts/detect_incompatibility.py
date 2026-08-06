#!/usr/bin/env fontforge
# -*- coding: utf-8 -*-
"""
Fantasque Sans Mono — Contour Incompatibility Detection Script.

Detects glyph-level incompatibilities between two FontForge ``.sfdir`` masters
that would prevent successful interpolation.  Compares node count per contour,
contour count, and curve direction for every glyph in the union of both masters.

Runs inside the FontForge embedded Python interpreter.  Not importable under a
stock CPython interpreter.

Usage::

    fontforge -lang=py -script Scripts/detect_incompatibility.py \\
        MASTER_A.sfdir MASTER_B.sfdir [--output REPORT.json]

Contract: Spec §4.4
    * Exit code 0 when the report is successfully generated (regardless of
      glyph compatibility status).
    * Exit code non-zero + message to stderr when input is invalid (missing
      directories, unopenable masters, zero glyphs).

Output JSON schema: Spec §4.4 (Incompatibility Detection Report).
"""

from __future__ import print_function

import argparse
import json
import os
import sys


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def _die(msg):
    """Print diagnostic to stderr and exit non-zero (Spec §4.4: fail-fast)."""
    sys.stderr.write("detect_incompatibility: " + str(msg) + "\n")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _parse_args(argv):
    """Parse command-line arguments.

    Returns a namespace with ``master_a``, ``master_b``, and ``output``.
    """
    parser = argparse.ArgumentParser(
        description="Detect contour incompatibilities between two FontForge .sfdir masters."
    )
    parser.add_argument(
        "master_a",
        help="Path to master A .sfdir directory",
    )
    parser.add_argument(
        "master_b",
        help="Path to master B .sfdir directory",
    )
    parser.add_argument(
        "--output",
        default="incompatibility_report.json",
        help="Path for the output JSON report (default: incompatibility_report.json)",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Glyph compatibility analysis
# ---------------------------------------------------------------------------

def _get_contour_info(glyph):
    """Extract contour information from a FontForge glyph.

    Returns a list of dicts, one per contour, each containing:
        ``node_count`` — number of nodes in the contour
        ``clockwise`` — whether the contour is clockwise
    """
    contours = []
    try:
        layer = glyph.foreground
        for i in range(len(layer)):
            contour = layer[i]
            contours.append({
                "node_count": len(contour),
                "clockwise": contour.isClockwise(),
            })
    except Exception:
        # Glyph may have no foreground layer (e.g. empty glyph)
        pass
    return contours


def _compare_glyphs(name, glyph_a, glyph_b):
    """Compare two glyphs and return a status dict.

    Returns a dict with ``name``, ``status``, and optional ``node_diff`` /
    ``contour_diff`` fields.
    """
    info_a = _get_contour_info(glyph_a)
    info_b = _get_contour_info(glyph_b)

    # --- Contour count mismatch ---
    if len(info_a) != len(info_b):
        return {
            "name": name,
            "status": "incompatible",
            "contour_diff": {
                "count_a": len(info_a),
                "count_b": len(info_b),
            },
        }

    # --- Per-contour comparison ---
    for idx, (ca, cb) in enumerate(zip(info_a, info_b)):
        # Node count per contour
        if ca["node_count"] != cb["node_count"]:
            return {
                "name": name,
                "status": "incompatible",
                "node_diff": {
                    "contour_index": idx,
                    "count_a": ca["node_count"],
                    "count_b": cb["node_count"],
                },
            }

        # Curve direction per contour
        if ca["clockwise"] != cb["clockwise"]:
            return {
                "name": name,
                "status": "incompatible",
            }

    # All checks passed
    return {
        "name": name,
        "status": "compatible",
    }


def _detect(master_a_path, master_b_path):
    """Run incompatibility detection between two masters.

    Returns a dict matching the output JSON schema (Spec §4.4).
    """
    import fontforge

    # --- Open masters ---
    try:
        font_a = fontforge.open(master_a_path)
    except Exception as exc:
        _die("cannot open master A (%s): %s" % (master_a_path, exc))

    try:
        font_b = fontforge.open(master_b_path)
    except Exception as exc:
        _die("cannot open master B (%s): %s" % (master_b_path, exc))

    # --- Collect glyph names ---
    glyphs_a = set(g.glyphname for g in font_a.glyphs())
    glyphs_b = set(g.glyphname for g in font_b.glyphs())

    if len(glyphs_a) == 0:
        _die("master A (%s) contains zero glyphs" % master_a_path)
    if len(glyphs_b) == 0:
        _die("master B (%s) contains zero glyphs" % master_b_path)

    all_glyphs = sorted(glyphs_a | glyphs_b)

    only_in_a = sorted(glyphs_a - glyphs_b)
    only_in_b = sorted(glyphs_b - glyphs_a)
    common = sorted(glyphs_a & glyphs_b)

    # --- Build report ---
    results = []

    for name in all_glyphs:
        if name in only_in_a:
            results.append({"name": name, "status": "only_in_a"})
        elif name in only_in_b:
            results.append({"name": name, "status": "only_in_b"})
        else:
            results.append(_compare_glyphs(name, font_a[name], font_b[name]))

    compatible_count = sum(1 for r in results if r["status"] == "compatible")
    incompatible_count = sum(1 for r in results if r["status"] == "incompatible")

    return {
        "master_a": os.path.abspath(master_a_path),
        "master_b": os.path.abspath(master_b_path),
        "total_glyphs": len(all_glyphs),
        "compatible_count": compatible_count,
        "incompatible_count": incompatible_count,
        "only_in_a_count": len(only_in_a),
        "only_in_b_count": len(only_in_b),
        "glyphs": results,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = _parse_args(sys.argv[1:])

    if not os.path.isdir(args.master_a):
        _die("master A is not a directory: %s" % args.master_a)
    if not os.path.isdir(args.master_b):
        _die("master B is not a directory: %s" % args.master_b)

    report = _detect(args.master_a, args.master_b)

    with open(args.output, "w") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)

    print("detect_incompatibility: report written to %s (%d glyphs, %d compatible, %d incompatible)"
          % (args.output, report["total_glyphs"], report["compatible_count"], report["incompatible_count"]))

    sys.exit(0)


if __name__ == "__main__":
    main()
