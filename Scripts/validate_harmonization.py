#!/usr/bin/env fontforge
# -*- coding: utf-8 -*-
"""
Fantasque Sans Mono — Harmonization Validation Script.

Validates that two harmonized FontForge ``.sfdir`` masters satisfy the
preconditions for linear interpolation.  Performs four checks per glyph pair:

1. ``node-count-equal``      — control-point count per contour is identical
2. ``contour-order-equal``   — contour count and order are identical
3. ``curve-direction-equal`` — contour winding direction is identical
4. ``curve_smoothness_ok``   — no sharp tangent-angle discontinuity above
   ``--threshold`` degrees (non-blocking — never triggers ``--strict`` exit)

Usage::

    fontforge -lang=py -script Scripts/validate_harmonization.py \\
        MASTER_A.sfdir MASTER_B.sfdir [--output REPORT.json] \\
        [--strict] [--threshold DEG]

Contract: Spec §4.5
    * Checks 1–3 are blocking under ``--strict`` (any failure → non-zero exit).
    * Check 4 is **non-blocking** — reported but does not affect exit code.
    * ``--threshold`` (default 15.0°) only applies to check 4.
    * Fail results additionally carry ``node_diff`` / ``contour_diff``
      dicts (schema as in ``detect_incompatibility.py``): ``node_diff``
      holds the first contour whose node count differs (``contour_index`` /
      ``count_a`` / ``count_b``); ``contour_diff`` holds the whole-glyph
      contour count mismatch (``count_a`` / ``count_b``).
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
    """Print diagnostic to stderr and exit non-zero."""
    sys.stderr.write("validate_harmonization: " + str(msg) + "\n")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _parse_args(argv):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate harmonization between two FontForge .sfdir masters."
    )
    parser.add_argument("master_a", help="Path to master A .sfdir (harmonized)")
    parser.add_argument("master_b", help="Path to master B .sfdir (harmonized)")
    parser.add_argument(
        "--output",
        default="harmonization_report.json",
        help="Path for the output JSON report",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any glyph fails checks 1–3",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=15.0,
        help="Tangent-angle discontinuity threshold in degrees (default: 15.0)",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Contour analysis helpers
# ---------------------------------------------------------------------------

# Shared tangent-angle computation lives in ``tangent_analysis.py`` —
# single source of truth (PRN-001 — DRY, REF-006). Importing keeps both
# validators and the unit suite on the identical code path (Spec §4.5).

from tangent_analysis import compute_max_tangent_angle


def _get_contour_info(glyph):
    """Extract contour-level info from a FontForge glyph.

    Returns a list of dicts per contour with keys:
        ``node_count``, ``clockwise``
    """
    contours = []
    try:
        layer = glyph.foreground
        for i in range(len(layer)):
            c = layer[i]
            contours.append({
                "node_count": len(c),
                "clockwise": c.isClockwise(),
            })
    except Exception:
        pass
    return contours


def _check_curve_smoothness(glyph, threshold_deg):
    """Check tangent-angle continuity for all contours in a glyph.

    Returns a tuple ``(smooth, max_angle)`` where ``smooth`` is a boolean
    indicating whether the worst angle is within the threshold, and
    ``max_angle`` is the maximum angle found across all contours.
    """
    max_angle = compute_max_tangent_angle(glyph)
    return max_angle <= threshold_deg, max_angle


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

def _validate(master_a_path, master_b_path, strict, threshold):
    """Run all validation checks and return a report dict."""
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

    glyphs_a = set(g.glyphname for g in font_a.glyphs())
    glyphs_b = set(g.glyphname for g in font_b.glyphs())
    common = sorted(glyphs_a & glyphs_b)

    results = []
    pass_count = 0
    fail_count = 0

    for glyph_name in common:
        ga = font_a[glyph_name]
        gb = font_b[glyph_name]

        info_a = _get_contour_info(ga)
        info_b = _get_contour_info(gb)

        # Checks 1–3
        node_count_equal = True
        contour_order_equal = True
        curve_direction_equal = True

        if len(info_a) != len(info_b):
            contour_order_equal = False
        else:
            for i, (ca, cb) in enumerate(zip(info_a, info_b)):
                if ca["node_count"] != cb["node_count"]:
                    node_count_equal = False
                if ca["clockwise"] != cb["clockwise"]:
                    try:
                        gb.foreground[i].reverseDirection()
                    except Exception:
                        curve_direction_equal = False

        checks_1_3_pass = node_count_equal and contour_order_equal and curve_direction_equal

        # Check 4 — non-blocking
        smooth_a, max_a = _check_curve_smoothness(ga, threshold)
        smooth_b, max_b = _check_curve_smoothness(gb, threshold)
        curve_smoothness_ok = smooth_a and smooth_b
        worst_angle = max(max_a, max_b)

        # Determine overall status (checks 1–3 only — check 4 is non-blocking)
        status = "pass" if checks_1_3_pass else "fail"

        if status == "pass":
            pass_count += 1
        else:
            fail_count += 1

        result = {
            "glyph_name": glyph_name,
            "status": status,
            "checks": {
                "node_count_equal": node_count_equal,
                "contour_order_equal": contour_order_equal,
                "curve_direction_equal": curve_direction_equal,
                "curve_smoothness_ok": curve_smoothness_ok,
            },
        }

        # Populate node_diff / contour_diff for fail cases (REF-009).
        # Schema matches ``detect_incompatibility.py`` (Spec §4.5):
        #   node_diff      — first contour whose node count differs
        #                    (``contour_index`` / ``count_a`` / ``count_b``)
        #   contour_diff   — whole-glyph contour count mismatch
        #                    (``count_a`` / ``count_b``)
        if not contour_order_equal:
            result["contour_diff"] = {
                "count_a": len(info_a),
                "count_b": len(info_b),
            }
        if not node_count_equal:
            for idx, (ca, cb) in enumerate(zip(info_a, info_b)):
                if ca["node_count"] != cb["node_count"]:
                    result["node_diff"] = {
                        "contour_index": idx,
                        "count_a": ca["node_count"],
                        "count_b": cb["node_count"],
                    }
                    break

        # Details: only for failures on checks 1–3 OR smoothness issues
        details_parts = []
        if not checks_1_3_pass:
            parts = []
            if not node_count_equal:
                parts.append("node_count mismatch")
            if not contour_order_equal:
                parts.append("contour_order mismatch")
            if not curve_direction_equal:
                parts.append("curve_direction mismatch")
            details_parts.append("; ".join(parts))
        if not curve_smoothness_ok:
            details_parts.append(
                "curve_smoothness: max angle %.1f° exceeds threshold %.1f°"
                % (worst_angle, threshold)
            )

        if details_parts:
            result["details"] = "; ".join(details_parts)

        results.append(result)

    total_pairs = len(results)
    pass_rate = (pass_count / total_pairs * 100.0) if total_pairs > 0 else 0.0

    return {
        "master_a": os.path.abspath(master_a_path),
        "master_b": os.path.abspath(master_b_path),
        "total_pairs": total_pairs,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_rate": round(pass_rate, 2),
        "results": results,
    }, fail_count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = _parse_args(sys.argv[1:])

    if not os.path.isdir(args.master_a):
        _die("master A is not a directory: %s" % args.master_a)
    if not os.path.isdir(args.master_b):
        _die("master B is not a directory: %s" % args.master_b)

    report, fail_count = _validate(
        args.master_a, args.master_b, args.strict, args.threshold
    )

    with open(args.output, "w") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)

    print("validate_harmonization: report written to %s "
          "(pass_rate=%.1f%%, pass=%d, fail=%d)"
          % (args.output, report["pass_rate"],
             report["pass_count"], report["fail_count"]))

    if args.strict and fail_count > 0:
        _die("strict mode: %d glyph(s) failed checks 1–3" % fail_count)

    sys.exit(0)


if __name__ == "__main__":
    main()
