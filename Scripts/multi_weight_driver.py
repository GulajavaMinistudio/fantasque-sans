#!/usr/bin/env fontforge
# -*- coding: utf-8 -*-
"""
Fantasque Sans Mono — Multi-Weight Driver Script.

Entry point for the multi-weight interpolation pipeline.  Reads harmonized
Regular and Bold masters, interpolates core weights (Medium 500, SemiBold 600)
and optionally stretch weights (Light 300, ExtraBold 800), injects metadata,
copies the ``hmtx`` table unconditionally, and assembles a ``build/sources/``
directory for the existing ``custom_build_driver.py`` pipeline.

Usage::

    fontforge -lang=py -script Scripts/multi_weight_driver.py \\
        --sources SOURCES_DIR --output OUTPUT_DIR \\
        [--enable-light] [--enable-extrabold] \\
        [--light-factor F] [--extrabold-factor F] \\
        [--dry-run]

Contract: Spec §4.6
    * Interpolation factor: Medium = 0.5, SemiBold = 0.67 exact.
    * Flag ``--enable-light`` / ``--enable-extrabold`` ONLY in release
      upstream — Custom Build skips stretch weights.
    * ``--light-factor`` / ``--extrabold-factor`` are MANDATORY when the
      corresponding ``--enable-*`` flag is set; the driver exits non-zero
      with an instructive message if they are missing.
    * hmtx copy is **unconditional** (always copies advance widths).
    * Does NOT call ``features.py``, does NOT run ``ttfautohint``.
"""

from __future__ import print_function

import argparse
import os
import shutil
import sys


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Interpolation factor contract (Spec §4.6)
FACTOR_MEDIUM = 0.5
FACTOR_SEMIBOLD = 0.67  # exact — two decimals (r4 R3)

# OS/2 weight class mapping
WEIGHT_CLASS = {
    "Light": 300,
    "Regular": 400,
    "Medium": 500,
    "SemiBold": 600,
    "Bold": 700,
    "ExtraBold": 800,
}

# .sfdir naming convention for assembly
SFDIR_NAME = "FantasqueSansMono-{weight}.sfdir"


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def _die(msg):
    """Print diagnostic to stderr and exit non-zero."""
    sys.stderr.write("multi_weight_driver: " + str(msg) + "\n")
    sys.exit(1)


def _warn(msg):
    """Print warning to stderr."""
    sys.stderr.write("multi_weight_driver: WARNING: " + str(msg) + "\n")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _parse_args(argv):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Multi-weight interpolation driver for Fantasque Sans Mono."
    )
    parser.add_argument(
        "--sources",
        required=True,
        help="Path to the Sources/ directory (containing Harmonized/ subdirectory)",
    )
    parser.add_argument(
        "--output",
        default="Sources/Harmonized/Interpolated",
        help="Output directory for interpolated .sfdir files",
    )
    parser.add_argument(
        "--enable-light",
        action="store_true",
        help="Enable Light (300) extrapolation (release upstream only)",
    )
    parser.add_argument(
        "--enable-extrabold",
        action="store_true",
        help="Enable ExtraBold (800) extrapolation (release upstream only)",
    )
    parser.add_argument(
        "--light-factor",
        type=float,
        default=None,
        help="Extrapolation factor for Light (MANDATORY with --enable-light)",
    )
    parser.add_argument(
        "--extrabold-factor",
        type=float,
        default=None,
        help="Extrapolation factor for ExtraBold (MANDATORY with --enable-extrabold)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate only — do not write any output files",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Metadata injection
# ---------------------------------------------------------------------------

def _inject_metadata(font, weight_name):
    """Inject internal metadata into a FontForge font before saving.

    Sets ``familyname``, ``fullname``, ``fontname``, ``weight``, and
    OS/2 weight class according to the Spec §4.6 contract.
    """
    weight_num = WEIGHT_CLASS.get(weight_name, 400)

    try:
        font.familyname = "Fantasque Sans Mono"
    except Exception:
        pass
    try:
        font.fullname = "Fantasque Sans Mono %s" % weight_name
    except Exception:
        pass
    try:
        font.fontname = "FantasqueSansMono-%s" % weight_name
    except Exception:
        pass
    try:
        font.weight = weight_name
    except Exception:
        pass
    try:
        font.os2_weight = weight_num
    except Exception:
        pass


# ---------------------------------------------------------------------------
# hmtx copy (unconditional)
# ---------------------------------------------------------------------------

def _copy_hmtx(target_font, source_font):
    """Copy advance width from source glyphs to target font.

    Unconditional per Spec §4.6 (r5 E5).  Glyphs not found in the source
    are left unchanged.
    """
    for glyph_name in source_font.glyphs():
        try:
            target_font[glyph_name].width = source_font[glyph_name].width
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Core interpolation
# ---------------------------------------------------------------------------

def _interpolate_weight(regular_font, bold_font, factor, weight_name, output_dir, dry_run):
    """Interpolate a single weight between Regular and Bold masters.

    Uses FontForge's built-in ``interpolateFonts()`` when available,
    falling back to per-glyph coordinate blending.

    Returns the interpolated font, or None on failure.
    """
    import fontforge

    print("  Interpolating %s (factor=%.4f)..." % (weight_name, factor))

    # Try FontForge built-in interpolation first
    try:
        if hasattr(regular_font, "interpolateFonts"):
            result = regular_font.interpolateFonts(factor, bold_font)
        else:
            # Fallback: copy Regular and blend per-glyph
            result = fontforge.font()
            for attr in ("fontname", "familyname", "fullname",
                          "ascent", "descent", "em"):
                try:
                    setattr(result, attr, getattr(regular_font, attr))
                except Exception:
                    pass

            for name in regular_font.glyphs():
                try:
                    ga = regular_font[name]
                    gb = bold_font[name] if name in bold_font.glyphs() else None

                    g_out = result.createChar(-1, name)
                    g_out.width = ga.width

                    if gb is None:
                        g_out.foreground = ga.foreground
                        continue

                    layer_a = ga.foreground
                    layer_b = gb.foreground
                    if len(layer_a) != len(layer_b):
                        g_out.foreground = ga.foreground
                        continue

                    new_layer = fontforge.layer()
                    for ca, cb in zip(layer_a, layer_b):
                        if len(ca) != len(cb):
                            continue
                        new_contour = fontforge.contour()
                        for pa, pb in zip(ca, cb):
                            new_x = pa.x + factor * (pb.x - pa.x)
                            new_y = pa.y + factor * (pb.y - pa.y)
                            new_pt = fontforge.point(new_x, new_y)
                            if hasattr(pa, "point_type"):
                                new_pt.type = pa.point_type
                            elif hasattr(pa, "type"):
                                new_pt.type = pa.type
                            new_contour += new_pt
                        new_contour.closed = getattr(ca, "closed", True)
                        new_layer += new_contour
                    g_out.foreground = new_layer
                except Exception as exc:
                    _warn("skipping glyph '%s' during interpolation: %s" % (name, exc))
                    continue
    except Exception as exc:
        _die("interpolation failed for %s: %s" % (weight_name, exc))

    # Inject metadata
    _inject_metadata(result, weight_name)

    # hmtx copy (unconditional)
    _copy_hmtx(result, regular_font)

    if not dry_run:
        weight_dir = os.path.join(output_dir, weight_name)
        os.makedirs(weight_dir, exist_ok=True)
        try:
            result.save(weight_dir)
        except Exception as exc:
            _die("cannot save %s to %s: %s" % (weight_name, weight_dir, exc))
        print("    .sfdir → %s" % weight_dir)

    return result


# ---------------------------------------------------------------------------
# Build source assembly
# ---------------------------------------------------------------------------

def _assemble_build_sources(sources_dir, output_dir, weights, dry_run):
    """Assemble ``build/sources/`` with all .sfdir files.

    Copies harmonized masters + interpolated weights (renamed to
    ``FantasqueSansMono-{Weight}.sfdir``) + legacy ``FantasqueSans.sfdir``.
    """
    build_dir = os.path.join(sources_dir, "..", "build", "sources")
    build_dir = os.path.normpath(build_dir)

    if dry_run:
        print("  [dry-run] would assemble %s" % build_dir)
        return build_dir

    os.makedirs(build_dir, exist_ok=True)

    # Copy 4 harmonized masters
    harmonized = os.path.join(sources_dir, "Harmonized")
    for master in ("Regular", "Bold", "Italic", "BoldItalic"):
        src = os.path.join(harmonized, master)
        dst = os.path.join(build_dir, SFDIR_NAME.format(weight=master))
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print("  [assembly] %s → %s" % (master, dst))

    # Copy interpolated weights
    interpolated = os.path.join(harmonized, "Interpolated")
    for weight in weights:
        src = os.path.join(interpolated, weight)
        dst = os.path.join(build_dir, SFDIR_NAME.format(weight=weight))
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print("  [assembly] %s → %s" % (weight, dst))

    # Copy legacy FantasqueSans.sfdir
    fantasque_src = os.path.join(sources_dir, "FantasqueSans.sfdir")
    fantasque_dst = os.path.join(build_dir, "FantasqueSans.sfdir")
    if os.path.isdir(fantasque_src):
        if os.path.exists(fantasque_dst):
            shutil.rmtree(fantasque_dst)
        shutil.copytree(fantasque_src, fantasque_dst)
        print("  [assembly] FantasqueSans → %s" % fantasque_dst)
    else:
        _warn("FantasqueSans.sfdir not found at %s — assembly will be incomplete"
              % fantasque_src)

    return build_dir


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = _parse_args(sys.argv[1:])
    import fontforge  # noqa: E402

    sources = args.sources
    harmonized_dir = os.path.join(sources, "Harmonized")
    regular_dir = os.path.join(harmonized_dir, "Regular")
    bold_dir = os.path.join(harmonized_dir, "Bold")

    # --- Validation ---
    if not os.path.isdir(regular_dir):
        _die("harmonized Regular not found: %s" % regular_dir)
    if not os.path.isdir(bold_dir):
        _die("harmonized Bold not found: %s" % bold_dir)

    if args.enable_light and args.light_factor is None:
        _die("--light-factor is required when --enable-light is set "
             "(factor stretch ditetapkan Phase 5 — lihat "
             "docs/audit/stretch-factor-decision-{date}.md)")
    if args.enable_extrabold and args.extrabold_factor is None:
        _die("--extrabold-factor is required when --enable-extrabold is set "
             "(factor stretch ditetapkan Phase 5 — lihat "
             "docs/audit/stretch-factor-decision-{date}.md)")

    # --- Open masters ---
    print("multi_weight_driver: loading harmonized masters...")
    try:
        font_reg = fontforge.open(regular_dir)
    except Exception as exc:
        _die("cannot open Regular: %s" % exc)
    try:
        font_bold = fontforge.open(bold_dir)
    except Exception as exc:
        _die("cannot open Bold: %s" % exc)

    output_dir = args.output
    weights_produced = []

    # --- Core weights ---
    print("multi_weight_driver: producing core weights...")
    _interpolate_weight(font_reg, font_bold, FACTOR_MEDIUM,
                        "Medium", output_dir, args.dry_run)
    weights_produced.append("Medium")

    _interpolate_weight(font_reg, font_bold, FACTOR_SEMIBOLD,
                        "SemiBold", output_dir, args.dry_run)
    weights_produced.append("SemiBold")

    # --- Stretch weights (release upstream only) ---
    if args.enable_light:
        _interpolate_weight(font_reg, font_bold, args.light_factor,
                            "Light", output_dir, args.dry_run)
        weights_produced.append("Light")

    if args.enable_extrabold:
        _interpolate_weight(font_reg, font_bold, args.extrabold_factor,
                            "ExtraBold", output_dir, args.dry_run)
        weights_produced.append("ExtraBold")

    # --- Assembly ---
    print("multi_weight_driver: assembling build/sources/...")
    build_dir = _assemble_build_sources(sources, output_dir,
                                         weights_produced, args.dry_run)

    font_reg.close()
    font_bold.close()

    print("multi_weight_driver: done — %d weight(s) produced: %s"
          % (len(weights_produced), ", ".join(weights_produced)))
    print("multi_weight_driver: build sources → %s" % build_dir)


if __name__ == "__main__":
    main()
