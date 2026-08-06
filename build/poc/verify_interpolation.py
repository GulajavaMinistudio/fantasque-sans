#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification for the text-level interpolated core weights
(build/poc/interpolate_weights.py output).

Checks per weight (Medium, SemiBold):
  1. Structural: interpolated contour/node structure == harmonized Regular.
  2. Blend exactness: every coordinate == A + factor*(B-A) (1e-6 tolerance)
     for blended glyphs; fallback glyphs are byte-identical to Regular.
  3. hmtx copy: advance width == harmonized Regular (unconditional, r5 E5).
  4. Metadata Layer 1 (r6 Q-08 / TASK-3.X): familyname identical across all
     weights (incl. masters), fullname "Fantasque Sans Mono {Weight}",
     os2_weight 500/600 — not identical to the masters' fullname/os2_weight.

Usage: python build/poc/verify_interpolation.py
Exit 0 when all checks pass, non-zero otherwise.
"""

from __future__ import print_function

import filecmp
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harmonize_engine import parse_glyph  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
HARMONIZED = ROOT / "Sources" / "Harmonized"

FACTORS = {"Medium": 0.5, "SemiBold": 0.67}
WEIGHT_CLASS = {"Medium": 500, "SemiBold": 600}
FAMILY_NAME = "Fantasque Sans Mono"


def props_of(sfdir_dir):
    out = {}
    for line in (sfdir_dir / "font.props").read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            out[key.strip()] = val.strip()
    return out


def glyph_widths(sfdir_dir):
    widths = {}
    for f in sfdir_dir.glob("*.glyph"):
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("StartChar:"):
                name = line.split(":", 1)[1].strip()
            elif line.startswith("Width:"):
                widths[name] = int(line.split(":", 1)[1].split()[0])
    return widths


def verify_weight(weight_name):
    factor = FACTORS[weight_name]
    reg = HARMONIZED / "Regular"
    bold = HARMONIZED / "Bold"
    out = HARMONIZED / "Interpolated" / weight_name
    problems = []

    n_blend = n_copy = 0
    for f in sorted(out.glob("*.glyph")):
        src_reg = reg / f.name
        src_bold = bold / f.name
        _, ca, _ = parse_glyph(f)
        _, ra, _ = parse_glyph(src_reg)
        # 1) structure must match harmonized Regular
        if len(ca) != len(ra) or any(len(x) != len(y) for x, y in zip(ca, ra)):
            problems.append((f.name, "structure mismatch vs Regular"))
            continue
        if not src_bold.exists():
            n_copy += 1
            continue
        _, rb, _ = parse_glyph(src_bold)
        compatible = (len(ra) == len(rb)
                      and all(len(x) == len(y) for x, y in zip(ra, rb)))
        if not compatible:
            # fallback copy — must be byte-identical to Regular
            n_copy += 1
            if not filecmp.cmp(src_reg, f, shallow=False):
                problems.append((f.name, "fallback copy not byte-identical"))
            continue
        n_blend += 1
        # 2) blend exactness
        _, cb, _ = parse_glyph(src_bold)
        for c_out, c_a, c_b in zip(ca, ra, rb):
            for eo, ea, eb in zip(c_out, c_a, c_b):
                ex = ea[1] + factor * (eb[1] - ea[1])
                ey = ea[2] + factor * (eb[2] - ea[2])
                if abs(eo[1] - ex) > 1e-6 or abs(eo[2] - ey) > 1e-6:
                    problems.append((f.name, "blend inexact: %.4f %.4f vs %.4f %.4f"
                                     % (eo[1], eo[2], ex, ey)))
                    break
    # 3) hmtx copy
    w_reg = glyph_widths(reg)
    w_out = glyph_widths(out)
    for name, w in w_out.items():
        if name in w_reg and w != w_reg[name]:
            problems.append((name, "advance width %d != Regular %d" % (w, w_reg[name])))

    # 4) metadata Layer 1
    p_out = props_of(out)
    p_reg = props_of(reg)
    p_bold = props_of(bold)
    if p_out.get("FamilyName") != FAMILY_NAME:
        problems.append(("font.props", "FamilyName=%s" % p_out.get("FamilyName")))
    if p_out.get("FullName") != "%s %s" % (FAMILY_NAME, weight_name):
        problems.append(("font.props", "FullName=%s" % p_out.get("FullName")))
    if p_out.get("Weight") != weight_name:
        problems.append(("font.props", "Weight=%s" % p_out.get("Weight")))
    if p_out.get("TTFWeight") != str(WEIGHT_CLASS[weight_name]):
        problems.append(("font.props", "TTFWeight=%s" % p_out.get("TTFWeight")))
    # familyname identical across masters (r6 Q-08)
    if p_reg.get("FamilyName") != FAMILY_NAME or p_bold.get("FamilyName") != FAMILY_NAME:
        problems.append(("font.props", "master FamilyName mismatch"))
    # fullname + os2_weight not identical to masters
    for p_m in (p_reg, p_bold):
        if p_m.get("FullName") == p_out.get("FullName"):
            problems.append(("font.props", "fullname identical to master"))
        if p_m.get("TTFWeight") == str(WEIGHT_CLASS[weight_name]):
            problems.append(("font.props", "os2_weight identical to master"))

    print("%s: blended=%d copied=%d | problems=%d" % (weight_name, n_blend, n_copy, len(problems)))
    for p in problems[:10]:
        print("   ", p)
    return len(problems)


def main():
    total = 0
    for w in ("Medium", "SemiBold"):
        total += verify_weight(w)
    print("RESULT:", "FAIL" if total else "PASS")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
