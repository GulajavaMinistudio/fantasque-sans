#!/usr/bin/env fontforge
# -*- coding: utf-8 -*-
"""
Fantasque Sans Mono — Interpolation Validation Script.

Validates interpolated weight glyphs against the nearest harmonized masters.
Classifies each glyph as ``pass``, ``warning`` (minor tangent-angle artifact),
or ``fail`` (self-intersection / closed counter / broken contour).

Usage::

    fontforge -lang=py -script Scripts/validate_interpolation.py \\
        --interpolated INTERPOLATED_DIR \\
        --masters MASTER_DIR \\
        [--threshold DEG] [--output REPORT.json] \\
        [--overlay-dir PNG_DIR] [--fail-fast]

Contract: Spec §4.11
    * ``warning`` = tangent-angle discontinuity > ``--threshold`` degrees
    * ``fail``    = self-intersection / broken contour
    * ``--fail-fast`` → non-zero exit code on first ``fail``
    * ``--masters`` accepts a parent directory containing ``Regular/``
      and ``Bold/`` subdirectories.
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
    sys.stderr.write("validate_interpolation: " + str(msg) + "\n")
    sys.exit(1)


def _warn(msg):
    """Print warning to stderr."""
    sys.stderr.write("validate_interpolation: WARNING: " + str(msg) + "\n")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _parse_args(argv):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate interpolation results against harmonized masters."
    )
    parser.add_argument(
        "--interpolated",
        required=True,
        help="Path to the interpolated .sfdir directory",
    )
    parser.add_argument(
        "--masters",
        required=True,
        help="Parent directory containing Regular/ and Bold/ subdirectories",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=15.0,
        help="Tangent-angle discontinuity threshold in degrees (default: 15.0)",
    )
    parser.add_argument(
        "--output",
        default="interpolation_report.json",
        help="Path for the output JSON report",
    )
    parser.add_argument(
        "--overlay-dir",
        default=None,
        help="Directory to write overlay PNG files (optional)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Exit non-zero on first glyph with status 'fail'",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Tangent-angle analysis
# ---------------------------------------------------------------------------
# Shared computation lives in ``tangent_analysis.py`` — single source of
# truth (PRN-001 — DRY, REF-006). Importing keeps both validators and the
# unit suite on the identical code path (Spec §4.5 / §4.11).

from tangent_analysis import compute_max_tangent_angle


# ---------------------------------------------------------------------------
# Self-intersection / contour integrity check
# ---------------------------------------------------------------------------

def _has_self_intersection(glyph):
    """Check whether a glyph has self-intersecting or broken contours.

    Uses FontForge's built-in validation where available, falling back to
    simple heuristics when the Python API does not expose the C-level
    intersection detection directly.
    """
    try:
        # FontForge exposes ``selfIntersects()`` as a METHOD on the glyph
        # (fontforge.org/docs/scripting/python/fontforge.html). It must be
        # CALLED — a bound-method property access is always truthy and would
        # classify every glyph as failing.
        if hasattr(glyph, "selfIntersects") and glyph.selfIntersects():
            return True
        if hasattr(glyph, "intersects") and glyph.intersects():
            return True
    except Exception:
        pass

    # Heuristic: validate the glyph via FontForge's built-in validation
    try:
        glyph.validate()
    except Exception:
        # ``validate()`` may raise on severe errors
        return True

    # Additional heuristic: if any contour has < 2 points, it's broken
    try:
        layer = glyph.foreground
        for i in range(len(layer)):
            if len(layer[i]) < 2:
                return True
    except Exception:
        pass

    return False


# ---------------------------------------------------------------------------
# Overlay PNG generation
# ---------------------------------------------------------------------------

def _generate_overlay(glyph, master_glyph, weight_name, glyph_name, overlay_dir):
    """Generate a side-by-side overlay PNG: interpolated (left) vs master (right).

    Builds a scratch font holding both glyphs — the interpolated glyph at
    its original position and the master glyph shifted one em to the right —
    merges the two into a single composite glyph, and exports it as a PNG
    (200 px em-size). FontForge-only: the ``foreground`` getter returns a
    copy of the glyph's outlines, so transforming the scratch copies never
    mutates the source masters (REF-005, Spec REQ-S04).

    Returns the relative path to the PNG, or None on failure.
    """
    try:
        import fontforge as _ff

        if not os.path.isdir(overlay_dir):
            os.makedirs(overlay_dir)

        out_path = os.path.join(overlay_dir,
                                "%s_%s.png" % (weight_name, glyph_name))

        # Scratch font: one em of horizontal space between the two glyphs.
        tmp_font = _ff.font()
        tmp_font.em = 1000
        g_int = tmp_font.createChar(-1, glyph_name + "_int")
        g_ref = tmp_font.createChar(-1, glyph_name + "_ref")
        g_int.foreground = glyph.foreground
        g_ref.foreground = master_glyph.foreground
        # Shift the master one em to the right (side-by-side layout)
        g_ref.transform((1, 0, 0, 1, tmp_font.em, 0))

        # Merge both outlines into a single composite glyph
        composite = tmp_font.createChar(-1, glyph_name + "_both")
        layer = _ff.layer()
        for i in range(len(g_int.foreground)):
            layer += g_int.foreground[i]
        for i in range(len(g_ref.foreground)):
            layer += g_ref.foreground[i]
        composite.foreground = layer

        composite.export(out_path, 200)  # 200 px em-size
        return os.path.relpath(out_path, overlay_dir)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

def _validate(interpolated_path, masters_dir, threshold, overlay_dir, fail_fast):
    """Run interpolation validation and return a report dict.

    Returns ``(report, exit_code)`` where ``exit_code`` is 0 on success
    or 2 on usage error.
    """
    import fontforge

    # --- Resolve master directories ---
    regular_dir = os.path.join(masters_dir, "Regular")
    bold_dir = os.path.join(masters_dir, "Bold")

    if not os.path.isdir(regular_dir):
        _die("master Regular/ subdirectory not found in %s (expected: %s)"
             % (masters_dir, regular_dir))
    if not os.path.isdir(bold_dir):
        _die("master Bold/ subdirectory not found in %s (expected: %s)"
             % (masters_dir, bold_dir))

    # --- Open fonts ---
    try:
        font_interp = fontforge.open(interpolated_path)
    except Exception as exc:
        _die("cannot open interpolated font (%s): %s" % (interpolated_path, exc))

    try:
        font_regular = fontforge.open(regular_dir)
    except Exception as exc:
        _die("cannot open Regular master (%s): %s" % (regular_dir, exc))

    try:
        font_bold = fontforge.open(bold_dir)
    except Exception as exc:
        _die("cannot open Bold master (%s): %s" % (bold_dir, exc))

    # --- Determine weight name ---
    weight_name = os.path.basename(os.path.normpath(interpolated_path))

    # --- Iterate over interpolated glyphs ---
    glyph_names = sorted(font_interp.glyphs())
    results = []
    pass_count = 0
    warning_count = 0
    fail_count = 0
    first_fail = None

    for name in glyph_names:
        g_interp = font_interp[name]

        # --- Check self-intersection (fail) ---
        if _has_self_intersection(g_interp):
            result = {
                "name": name,
                "status": "fail",
                "issue": "self-intersection or broken contour detected",
            }
            fail_count += 1
            if first_fail is None:
                first_fail = name
            results.append(result)
            if fail_fast:
                break
            continue

        # --- Check tangent-angle discontinuity (warning) ---
        max_angle = compute_max_tangent_angle(g_interp)
        if max_angle > threshold:
            result = {
                "name": name,
                "status": "warning",
                "issue": "tangent-angle discontinuity %.1f° > threshold %.1f°"
                         % (max_angle, threshold),
            }
            warning_count += 1
        else:
            result = {
                "name": name,
                "status": "pass",
            }
            pass_count += 1

        # --- Overlay PNG (optional) ---
        if overlay_dir and result["status"] in ("warning", "fail"):
            # Use nearest master for overlay: compare against Regular
            # (typically the closer reference for Medium/SemiBold)
            ref_glyph = None
            if name in font_regular.glyphs():
                ref_glyph = font_regular[name]
            elif name in font_bold.glyphs():
                ref_glyph = font_bold[name]

            if ref_glyph is not None:
                png_path = _generate_overlay(
                    g_interp, ref_glyph, weight_name, name, overlay_dir
                )
                if png_path:
                    result["overlay_png"] = png_path

        results.append(result)

    # If we broke early on fail-fast, we still need to count remaining
    # glyphs correctly.  The report reflects the state at termination.
    total_glyphs = len(glyph_names)

    report = {
        "weight": weight_name,
        "total_glyphs": total_glyphs,
        "pass_count": pass_count,
        "warning_count": warning_count,
        "fail_count": fail_count,
        "glyphs": results,
    }

    return report


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = _parse_args(sys.argv[1:])

    if not os.path.isdir(args.interpolated):
        _die("interpolated directory not found: %s" % args.interpolated)
    if not os.path.isdir(args.masters):
        _die("masters directory not found: %s" % args.masters)

    report = _validate(
        args.interpolated,
        args.masters,
        args.threshold,
        args.overlay_dir,
        args.fail_fast,
    )

    with open(args.output, "w") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)

    print("validate_interpolation: report written to %s "
          "(weight=%s, pass=%d, warning=%d, fail=%d)"
          % (args.output, report["weight"],
             report["pass_count"], report["warning_count"],
             report["fail_count"]))

    if args.fail_fast and report["fail_count"] > 0:
        _die("fail-fast: %d glyph(s) with status 'fail'" % report["fail_count"])

    sys.exit(0)


if __name__ == "__main__":
    main()
