#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text-level interpolation of core weights (Medium 500, SemiBold 600) from the
harmonized Regular/Bold masters — session tooling (NOT a plan artifact; lives
under build/ which is git-ignored per FILE-024).

Replicates Scripts/multi_weight_driver.py semantics (Spec §4.6):
  * factors: Medium = 0.5, SemiBold = 0.67 exact (r4 R3)
  * per-point linear blend: P = A + factor*(B-A), point kind/flags from Regular
  * hmtx copy: advance width (Width:) taken from Regular — unconditional (r5 E5)
  * metadata injection: familyname "Fantasque Sans Mono" (identical across all
    weights), fullname "Fantasque Sans Mono {Weight}", os2_weight 500/600,
    fontname "FantasqueSansMono-{Weight}" (r6 Q-08)

Divergence from the driver (documented): glyphs whose contour/node structure
still differs between masters (the harmonization-skip list) are copied from
Regular wholesale (copy-as-fallback), instead of the driver's per-contour
drop behavior — the copy keeps the glyph renderable.

Output: Sources/Harmonized/Interpolated/{Medium,SemiBold}/ (git-ignored).
The authoritative artifacts are produced by multi_weight_driver.py under
FontForge (GitHub Actions); this tooling produces equivalent previews so the
validation chain can run before FontForge is available.

Usage: python build/poc/interpolate_weights.py
"""

from __future__ import print_function

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harmonize_engine import (  # noqa: E402
    parse_glyph, load_font, on_positions, fmt_num,
)

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCES = ROOT / "Sources"
HARMONIZED = SOURCES / "Harmonized"

FACTORS = {"Medium": 0.5, "SemiBold": 0.67}
WEIGHT_CLASS = {"Medium": 500, "SemiBold": 600}
FAMILY_NAME = "Fantasque Sans Mono"


def blend_entries(entries_a, entries_b, factor):
    """Linear blend of two entry lists (same structure)."""
    out = []
    for ea, eb in zip(entries_a, entries_b):
        x = ea[1] + factor * (eb[1] - ea[1])
        y = ea[2] + factor * (eb[2] - ea[2])
        out.append((ea[0], x, y) + ea[3:])
    return out


def write_font_props(src_props, weight_name, out_path):
    """Copy Regular font.props with injected metadata overrides."""
    weight_num = WEIGHT_CLASS[weight_name]
    overrides = {
        "FontName": "FantasqueSansMono-%s" % weight_name,
        "FamilyName": FAMILY_NAME,
        "FullName": "%s %s" % (FAMILY_NAME, weight_name),
        "Weight": weight_name,
        "TTFWeight": str(weight_num),
    }
    lines = []
    for line in src_props.read_text(encoding="utf-8", errors="replace").splitlines():
        key = line.split(":", 1)[0].strip()
        if key in overrides:
            lines.append("%s: %s" % (key, overrides[key]))
        else:
            lines.append(line)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def interpolate_weight(weight_name, fonts_reg, fonts_bold, harm_reg, harm_bold,
                       out_dir):
    factor = FACTORS[weight_name]
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in list(out_dir.glob("*.glyph")) + list(out_dir.glob("font.props")):
        f.unlink()

    n_blend = n_copy = 0
    for fpath in sorted(harm_reg.glob("*.glyph")):
        fname = fpath.name
        src_reg = harm_reg / fname
        src_bold = harm_bold / fname
        name_a, contours_a, _ = parse_glyph(src_reg)
        if not src_bold.exists():
            # glyph only in Regular — copy as-is
            shutil.copy2(src_reg, out_dir / fname)
            n_copy += 1
            continue
        name_b, contours_b, _ = parse_glyph(src_bold)

        # structure-compatible → blend; otherwise copy Regular (fallback)
        compatible = (len(contours_a) == len(contours_b)
                      and all(len(x) == len(y) for x, y in zip(contours_a, contours_b)))
        if compatible:
            blended = [blend_entries(a, b, factor) for a, b in zip(contours_a, contours_b)]
            g = fonts_reg.get(name_a)
            if g is None:
                shutil.copy2(src_reg, out_dir / fname)
                n_copy += 1
                continue
            write_blended_glyph(src_reg, blended, out_dir / fname)
            n_blend += 1
        else:
            shutil.copy2(src_reg, out_dir / fname)
            n_copy += 1

    write_font_props(harm_reg / "font.props", weight_name, out_dir / "font.props")
    print("  %s: blended=%d copied(fallback)=%d" % (weight_name, n_blend, n_copy))


def write_blended_glyph(src_path, contours, out_path):
    """Write a glyph file with blended contours (header/footer from source)."""
    text = src_path.read_text(encoding="utf-8", errors="replace")
    header = []
    footer = []
    state = "header"
    for line in text.splitlines():
        if line.startswith("Fore"):
            state = "tail"
            header.append(line)
            continue
        if line.startswith("SplineSet"):
            state = "spline"
            continue
        if line.startswith("EndSplineSet"):
            state = "tail"
            continue
        if state == "header":
            header.append(line)
        elif state == "tail":
            footer.append(line)
    lines = list(header)
    lines.append("SplineSet")
    for contour in contours:
        for idx, e in enumerate(contour):
            if e[0] == "off":
                continue
            offs = []
            k = idx - 1
            while k >= 0 and contour[k][0] == "off":
                offs.insert(0, (contour[k][1], contour[k][2]))
                k -= 1
            if e[3] == "m":
                lines.append("%s %s m %s" % (fmt_num(e[1]), fmt_num(e[2]), e[4] or "0"))
            else:
                parts = [fmt_num(x) for off in offs for x in off]
                parts += [fmt_num(e[1]), fmt_num(e[2]), e[3], e[4] or "0"]
                lines.append(" ".join(parts))
    lines.append("EndSplineSet")
    lines.extend(footer)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    harm_reg = HARMONIZED / "Regular"
    harm_bold = HARMONIZED / "Bold"
    fonts_reg, _ = load_font(harm_reg)
    fonts_bold, _ = load_font(harm_bold)
    interp_dir = HARMONIZED / "Interpolated"
    for weight_name in ("Medium", "SemiBold"):
        print("Interpolating %s (factor=%.4f)..." % (weight_name, FACTORS[weight_name]))
        interpolate_weight(weight_name, fonts_reg, fonts_bold, harm_reg, harm_bold,
                           interp_dir / weight_name)
    print("Interpolated → %s" % interp_dir)


if __name__ == "__main__":
    main()
