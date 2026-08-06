#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification for the harmonized masters produced by harmonize_engine.py.

Checks per pair:
  1. Structural compatibility of harmonized glyphs (contour/node/winding).
  2. Shape preservation (min-dev of every written on-curve point against the
     resolved original curves — sampling-exact metric).
  3. Pairing sanity: no gross area mismatch between paired contours.

Usage: python build/poc/verify_masters.py
Exit 0 when all checks pass, non-zero otherwise.
"""

from __future__ import print_function

import filecmp
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harmonize_engine import (  # noqa: E402
    PT_RE, parse_glyph, load_font, resolve_glyph, on_positions, winding_of,
    shoelace, centroid, lerp,
)

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCES = ROOT / "Sources"
HARMONIZED = SOURCES / "Harmonized"

PAIRS = [
    ("FantasqueSansMono-Regular.sfdir", "FantasqueSansMono-Bold.sfdir",
     "Regular", "Bold", "RB"),
    ("FantasqueSansMono-Italic.sfdir", "FantasqueSansMono-BoldItalic.sfdir",
     "Italic", "BoldItalic", "IB"),
]


def dist_pt_line(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def _dist_to_cubic(p, P0, C1, C2, P3, eps=0.25):
    """Distance from point p to a cubic Bezier via adaptive subdivision.

    Uniform 128-step sampling overstates the distance for very long nearly
    flat segments (a 2600-unit segment samples every ~20 units, so a point
    lying exactly on the curve can measure ~5-10 units away from the
    nearest sample). Adaptive flatness subdivision keeps the measured
    distance exact to ~eps/2 while staying fast on short segments.
    """
    if (dist_pt_line(C1, P0, P3) <= eps and dist_pt_line(C2, P0, P3) <= eps):
        return dist_pt_line(p, P0, P3)
    p01 = lerp(P0, C1, 0.5)
    p12 = lerp(C1, C2, 0.5)
    p23 = lerp(C2, P3, 0.5)
    p012 = lerp(p01, p12, 0.5)
    p123 = lerp(p12, p23, 0.5)
    M = lerp(p012, p123, 0.5)
    return min(_dist_to_cubic(p, P0, p01, p012, M, eps),
               _dist_to_cubic(p, M, p123, p23, P3, eps))


def dist_to_curve(p, o_c):
    idxs = on_positions(o_c)
    best = 1e18
    for k in range(len(idxs) - 1):
        i, j = idxs[k], idxs[k + 1]
        P0 = (o_c[i][1], o_c[i][2])
        P3 = (o_c[j][1], o_c[j][2])
        offs = [e for e in o_c[i + 1:j] if e[0] == "off"]
        if len(offs) != 2:
            best = min(best, dist_pt_line(p, P0, P3))
        else:
            C1 = (offs[0][1], offs[0][2])
            C2 = (offs[1][1], offs[1][2])
            best = min(best, _dist_to_cubic(p, P0, C1, C2, P3))
    return best


def harm_fnames(src_dir, harm_dir):
    return [f.name for f in harm_dir.glob("*.glyph")
            if (src_dir / f.name).exists()
            and not filecmp.cmp(src_dir / f.name, f, shallow=False)]


def main():
    failures = 0
    for src_a_name, src_b_name, out_a, out_b, label in PAIRS:
        src_a = SOURCES / src_a_name
        src_b = SOURCES / src_b_name
        fonts_a, enc_a = load_font(src_a)
        fonts_b, enc_b = load_font(src_b)
        harm_a = HARMONIZED / out_a
        harm_b = HARMONIZED / out_b
        parsed_a = {f.name: parse_glyph(f) for f in harm_a.glob("*.glyph")}
        parsed_b = {f.name: parse_glyph(f) for f in harm_b.glob("*.glyph")}

        hf = harm_fnames(src_a, harm_a)
        n_compat_issues = 0
        n_shape = 0
        worst_shape = 0.0
        worst_shape_fn = None
        n_area_flags = 0

        for fn in hf:
            name = parsed_a[fn][0]
            ca = parsed_a[fn][1]
            cb = parsed_b[fn][1]
            # 1) structural compatibility of harmonized glyphs
            if len(ca) != len(cb):
                n_compat_issues += 1
                continue
            for x, y in zip(ca, cb):
                if len(x) != len(y) or winding_of(x) != winding_of(y):
                    n_compat_issues += 1
            # 2) shape preservation (min-dev vs resolved original)
            memo = {}
            orig_a = resolve_glyph(name, fonts_a, enc_a, memo, set())
            for n_c in ca:
                best = 1e18
                for o_c in orig_a:
                    w = 0.0
                    for e in n_c:
                        if e[0] == "on":
                            d = dist_to_curve((e[1], e[2]), o_c)
                            if d > w:
                                w = d
                    if w < best:
                        best = w
                if best > 5.0:  # 128-step sampling artifact bound is ~4.9; real write bugs are far larger
                    n_shape += 1
                    if best > worst_shape:
                        worst_shape = best
                        worst_shape_fn = fn
            # 3) pairing sanity via area ratio of original masters
            memo_b = {}
            orig_b = resolve_glyph(name, fonts_b, enc_b, memo_b, set())
            if len(orig_a) == len(orig_b):
                a_order = sorted(range(len(orig_a)), key=lambda i: -shoelace(orig_a[i]))
                b_order = sorted(range(len(orig_b)), key=lambda i: -shoelace(orig_b[i]))
                for ia, ib in zip(a_order, b_order):
                    ar = shoelace(orig_a[ia])
                    ao = shoelace(orig_b[ib])
                    if min(ar, ao) <= 0 or max(ar, ao) / min(ar, ao) <= 4.0:
                        continue
                    # Only flag when the paired centroids are also far apart —
                    # small contours may legitimately differ in relative area
                    # across weights (e.g. dollar end strokes).
                    ca = centroid(orig_a[ia])
                    cb = centroid(orig_b[ib])
                    cd = math.hypot(ca[0] - cb[0], ca[1] - cb[1])
                    xs = [e[1] for e in orig_a[ia]] + [e[1] for e in orig_b[ib]]
                    ys = [e[2] for e in orig_a[ia]] + [e[2] for e in orig_b[ib]]
                    diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
                    if diag > 0 and cd > 0.3 * diag:
                        n_area_flags += 1

        print("%s: harmonized=%d compat_issues=%d shape_violations=%d "
              "worst_shape=%.3f (%s) area_flags=%d"
              % (label, len(hf), n_compat_issues, n_shape, worst_shape,
                 worst_shape_fn, n_area_flags))
        if n_compat_issues or n_shape or n_area_flags:
            failures += 1

    print("RESULT:", "FAIL" if failures else "PASS")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
