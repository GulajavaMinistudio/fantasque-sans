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
import math
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

def _get_on_curve_triples(contour):
    """Extract consecutive on-curve point triples from a FontForge contour."""
    on_curve = [contour[i] for i in range(len(contour))]
    n = len(on_curve)
    if n < 3:
        return []
    triples = []
    for i in range(n):
        prev_pt = on_curve[(i - 1) % n]
        this_pt = on_curve[i]
        next_pt = on_curve[(i + 1) % n]
        triples.append((prev_pt, this_pt, next_pt))
    return triples


def _compute_max_tangent_angle(glyph):
    """Return the maximum tangent-angle discontinuity across all contours.

    Returns 0.0 if the glyph has fewer than 3 points in every contour.
    """
    try:
        layer = glyph.foreground
    except Exception:
        return 0.0

    overall_max = 0.0
    for i in range(len(layer)):
        triples = _get_on_curve_triples(layer[i])
        for prev_pt, this_pt, next_pt in triples:
            dx_in = this_pt.x - prev_pt.x
            dy_in = this_pt.y - prev_pt.y
            mag_in = math.sqrt(dx_in * dx_in + dy_in * dy_in)

            dx_out = next_pt.x - this_pt.x
            dy_out = next_pt.y - this_pt.y
            mag_out = math.sqrt(dx_out * dx_out + dy_out * dy_out)

            if mag_in < 1e-9 or mag_out < 1e-9:
                continue

            dot = dx_in * dx_out + dy_in * dy_out
            cos_angle = dot / (mag_in * mag_out)
            cos_angle = max(-1.0, min(1.0, cos_angle))
            angle = math.degrees(math.acos(cos_angle))

            if angle > overall_max:
                overall_max = angle

    return overall_max


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
    """Generate a side-by-side overlay PNG comparing interpolated vs master.

    Returns the relative path to the PNG, or None on failure.
    """
    try:
        import fontforge as _ff
        import tempfile as _tempfile

        # Build a temporary font containing both glyphs for visual comparison
        tmp_font = _ff.font()
        # Create a simple temp font with the two glyphs
        g_int = tmp_font.createChar(-1, glyph_name + "_int")
        g_ref = tmp_font.createChar(-1, glyph_name + "_ref")

        # Copy contours from source glyphs
        try:
            g_int.foreground = glyph.foreground
            g_ref.foreground = master_glyph.foreground
        except Exception:
            return None

        if not os.path.isdir(overlay_dir):
            os.makedirs(overlay_dir)

        out_path = os.path.join(overlay_dir,
                                "%s_%s.png" % (weight_name, glyph_name))

        # Export the glyph pair as a bitmap
        g_int.export(out_path, 200)  # 200 px em-size
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
        max_angle = _compute_max_tangent_angle(g_interp)
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
