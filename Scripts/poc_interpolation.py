#!/usr/bin/env fontforge
# -*- coding: utf-8 -*-
"""
Fantasque Sans Mono — PoC Interpolation Script.

Produces a proof-of-concept Medium (500) weight by linearly interpolating a
subset of harmonized glyphs between Regular and Bold masters.  Outputs both
an ``.sfdir`` directory AND a TTF file (without hinting) for use with the
specimen sheet generator and visual diff review.

Usage::

    fontforge -lang=py -script Scripts/poc_interpolation.py \\
        --regular REGULAR_DIR --bold BOLD_DIR \\
        --output OUTPUT_DIR [--ttf TTF_PATH]

Contract: Spec §4.6
    * Dual output: ``.sfdir`` interpolated subset + TTF (no hinting).
    * TTF is required for ``generate_specimen.py`` input and visual diff
      review at 8/12/16/24 pt (FR-2.3).
    * Interpolation factor: 0.5 (Medium).
"""

from __future__ import print_function

import argparse
import os
import sys


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def _die(msg):
    """Print diagnostic to stderr and exit non-zero."""
    sys.stderr.write("poc_interpolation: " + str(msg) + "\n")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _parse_args(argv):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="PoC: interpolate a subset of glyphs to Medium (500)."
    )
    parser.add_argument(
        "--regular",
        required=True,
        help="Path to harmonized Regular .sfdir",
    )
    parser.add_argument(
        "--bold",
        required=True,
        help="Path to harmonized Bold .sfdir",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Directory to write the interpolated .sfdir",
    )
    parser.add_argument(
        "--ttf",
        default=None,
        help="Path to write the TTF output (no hinting)",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _interpolate_subset(regular_dir, bold_dir, output_dir, ttf_path):
    """Interpolate common glyphs from Regular→Bold to Medium (factor 0.5).

    Returns a tuple ``(total_glyphs, interpolated_count)``.
    """
    import fontforge

    # --- Open masters ---
    try:
        font_reg = fontforge.open(regular_dir)
    except Exception as exc:
        _die("cannot open Regular master (%s): %s" % (regular_dir, exc))

    try:
        font_bold = fontforge.open(bold_dir)
    except Exception as exc:
        _die("cannot open Bold master (%s): %s" % (bold_dir, exc))

    # --- Identify common glyphs ---
    glyphs_reg = set(g.glyphname for g in font_reg.glyphs())
    glyphs_bold = set(g.glyphname for g in font_bold.glyphs())
    common = sorted(glyphs_reg & glyphs_bold)
    only_in_reg = sorted(glyphs_reg - glyphs_bold)

    if not common:
        _die("no common glyphs found between Regular and Bold masters")

    # --- Create output font ---
    font_out = fontforge.font()

    # Copy font-level properties from Regular
    for prop in ("fontname", "familyname", "fullname", "weight",
                 "copyright", "version", "ascent", "descent"):
        try:
            setattr(font_out, prop, getattr(font_reg, prop))
        except Exception:
            pass

    font_out.fontname = "FantasqueSansMono-Medium-PoC"
    font_out.fullname = "Fantasque Sans Mono Medium PoC"
    font_out.weight = "Medium"

    # Copy em-size
    try:
        font_out.em = font_reg.em
    except Exception:
        pass

    interpolated_count = 0

    # --- Interpolate common glyphs ---
    for name in common:
        try:
            ga = font_reg[name]
            gb = font_bold[name]

            # Create glyph in output font
            g_out = font_out.createChar(-1, name)
            g_out.width = ga.width  # maintain advance width

            # FontForge interpolation: create an intermediate via
            # ``font.interpolateFonts()`` at the font level, or
            # interpolate per-glyph by blending contour coordinates.
            #
            # Per-glyph linear interpolation at factor 0.5:
            #   result = master_a + factor * (master_b - master_a)
            #
            # We copy the Regular contours and blend Bold contours.
            try:
                g_out.foreground = ga.foreground
            except Exception:
                pass

            # Apply per-contour interpolation manually by reading
            # coordinates and blending.
            layer_a = ga.foreground
            layer_b = gb.foreground

            if len(layer_a) != len(layer_b):
                # Mismatched contour count — skip interpolation,
                # fall back to Regular copy
                continue

            # Build interpolated foreground
            new_layer = fontforge.layer()
            for ca, cb in zip(layer_a, layer_b):
                if len(ca) != len(cb):
                    # Mismatched node count — skip this contour
                    continue
                new_contour = fontforge.contour()
                for pa, pb in zip(ca, cb):
                    # Linear blend: (1 - 0.5) * a + 0.5 * b
                    new_x = pa.x + 0.5 * (pb.x - pa.x)
                    new_y = pa.y + 0.5 * (pb.y - pa.y)
                    new_pt = fontforge.point(new_x, new_y)
                    # Copy point type from Regular
                    if hasattr(pa, "point_type"):
                        new_pt.type = pa.point_type
                    elif hasattr(pa, "type"):
                        new_pt.type = pa.type
                    # Copy on-curve flag
                    if hasattr(pa, "on_curve"):
                        new_pt.on_curve = pa.on_curve
                    new_contour += new_pt
                new_contour.closed = ca.closed if hasattr(ca, "closed") else True
                new_layer += new_contour

            g_out.foreground = new_layer

            # Copy references (components/overlays)
            if hasattr(g_out, "addReference"):
                try:
                    for ref in ga.references:
                        g_out.addReference(ref[0], ref[1])
                except Exception:
                    pass

            interpolated_count += 1

        except Exception as exc:
            sys.stderr.write(
                "poc_interpolation: WARNING: skipping glyph '%s': %s\n" % (name, exc)
            )
            continue

    # --- Copy-as-fallback for glyphs only in Regular ---
    for name in only_in_reg:
        try:
            ga = font_reg[name]
            g_out = font_out.createChar(-1, name)
            g_out.width = ga.width
            g_out.foreground = ga.foreground
        except Exception:
            pass

    total_glyphs = len(common) + len(only_in_reg)

    # --- Save .sfdir ---
    try:
        font_out.save(output_dir)
    except Exception as exc:
        _die("cannot save output .sfdir (%s): %s" % (output_dir, exc))

    # --- Generate TTF (no hinting) — unconditional per Spec r3 K11 + AC-P02 ---
    ttf_path = ttf_path or os.path.join(os.path.dirname(output_dir), "Medium.ttf")
    try:
        font_out.generate(ttf_path)
    except Exception as exc:
        _die("cannot generate TTF (%s): %s" % (ttf_path, exc))

    font_reg.close()
    font_bold.close()
    font_out.close()

    return total_glyphs, interpolated_count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = _parse_args(sys.argv[1:])

    if not os.path.isdir(args.regular):
        _die("Regular directory not found: %s" % args.regular)
    if not os.path.isdir(args.bold):
        _die("Bold directory not found: %s" % args.bold)

    total, interpolated = _interpolate_subset(
        args.regular, args.bold, args.output, args.ttf
    )

    print("poc_interpolation: %d/%d glyphs interpolated to Medium (factor=0.5)"
          % (interpolated, total))
    resolved_ttf = args.ttf or os.path.join(os.path.dirname(args.output), "Medium.ttf")
    print("poc_interpolation: .sfdir → %s" % args.output)
    print("poc_interpolation: TTF   → %s" % resolved_ttf)


if __name__ == "__main__":
    main()
