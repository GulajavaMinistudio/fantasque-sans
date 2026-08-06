#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PoC/Phase-2 structural harmonization engine (session tooling — NOT a plan
artifact; lives under build/ which is git-ignored per FILE-024).

Shape-preserving structural compatibilization of FontForge .sfdir masters:
  - reference (Refer:) expansion with transforms
  - contour pairing (area-rank primary + centroid sanity)
  - winding alignment (exact cyclic reversal)
  - node equalization (de Casteljau cubic splits +3, on-line insertion +1,
    degenerate l->c conversion +2 — all curve-exact)

Usage:
    python build/poc/harmonize_engine.py <pair>  # pair = RB | IB
Writes harmonized masters into Sources/Harmonized/{Regular,Bold} or
{Italic,BoldItalic} (full glyph sets).
"""

from __future__ import print_function

import argparse
import math
import os
import re
import shutil
import sys
from pathlib import Path

PT_RE = re.compile(
    r"^\s*(-?[\d.]+) (-?[\d.]+)"
    r"(?:\s+(-?[\d.]+) (-?[\d.]+))?"
    r"(?:\s+(-?[\d.]+) (-?[\d.]+))?"
    r"\s+([mlc])(?: ([0-9a-fx]+))?\s*"
)

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCES = ROOT / "Sources"
HARMONIZED = SOURCES / "Harmonized"

MASTERS = {
    "RB": ("FantasqueSansMono-Regular.sfdir", "FantasqueSansMono-Bold.sfdir",
           "Regular", "Bold"),
    "IB": ("FantasqueSansMono-Italic.sfdir", "FantasqueSansMono-BoldItalic.sfdir",
           "Italic", "BoldItalic"),
}


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_glyph(path):
    """Parse a .glyph file.

    Returns (name, contours, refs) where contours is a list of contour lists
    and each entry is ("on", x, y, kind, flags) or ("off", x, y).
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    name = None
    contours = []
    refs = []
    cur = None
    in_spline = False
    for line in text.splitlines():
        if line.startswith("StartChar:"):
            name = line.split(":", 1)[1].strip()
        elif line.startswith("Refer:"):
            parts = line.split()
            refs.append((int(parts[2]), [float(x) for x in parts[4:10]]))
        elif line.startswith("SplineSet"):
            in_spline = True
        elif line.startswith("EndSplineSet"):
            in_spline = False
            cur = None
        elif in_spline:
            m = PT_RE.match(line)
            if not m:
                continue
            nums = [float(v) for v in m.groups()[:6] if v is not None]
            pairs = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
            typ = m.group(7)
            if typ == "m":
                cur = []
                contours.append(cur)
                cur.append(("on", pairs[0][0], pairs[0][1], "m", m.group(8) or ""))
            elif typ == "l":
                cur.append(("on", pairs[0][0], pairs[0][1], "l", m.group(8) or ""))
            else:
                cur.append(("off", pairs[0][0], pairs[0][1]))
                cur.append(("off", pairs[1][0], pairs[1][1]))
                cur.append(("on", pairs[2][0], pairs[2][1], "c", m.group(8) or ""))
    return name, contours, refs


def load_font(sfdir):
    """Return (fonts, enc) — fonts: name -> (contours, refs, header, footer)."""
    fonts = {}
    enc = {}
    for f in sorted(sfdir.glob("*.glyph")):
        name, contours, refs = parse_glyph(f)
        if not name:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
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
            if line.startswith("Refer:"):
                continue
            if state == "header":
                header.append(line)
            elif state == "tail":
                footer.append(line)
        fonts[name] = {"contours": contours, "refs": refs,
                       "header": header, "footer": footer, "fname": f.name}
        for line in header:
            if line.startswith("Encoding:"):
                enc[int(line.split()[1])] = name
                break
    return fonts, enc


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def lerp(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def on_positions(entries):
    return [i for i, e in enumerate(entries) if e[0] == "on"]


def winding_of(entries):
    pts = [(e[1], e[2]) for e in entries if e[0] == "on"]
    if len(pts) < 3:
        return 0
    area = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        area += x1 * y2 - x2 * y1
    return 1 if area > 0 else -1


def shoelace(entries):
    pts = [(e[1], e[2]) for e in entries if e[0] == "on"]
    if len(pts) < 3:
        return 0.0
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1]
                   - pts[i][1] * pts[(i + 1) % len(pts)][0]
                   for i in range(len(pts)))) / 2.0


def centroid(entries):
    xs = [e[1] for e in entries]
    ys = [e[2] for e in entries]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def chord_params(entries):
    idxs = on_positions(entries)
    if len(idxs) < 2:
        return [0.0] * len(idxs), 0.0
    total = 0.0
    params = [0.0] * len(idxs)
    for k in range(len(idxs) - 1):
        i, j = idxs[k], idxs[k + 1]
        d = math.hypot(entries[j][1] - entries[i][1],
                       entries[j][2] - entries[i][2])
        total += d
        params[k + 1] = total
    d = math.hypot(entries[idxs[0]][1] - entries[idxs[-1]][1],
                   entries[idxs[0]][2] - entries[idxs[-1]][2])
    total += d
    if total == 0:
        return [0.0] * len(idxs), 0.0
    return [p / total for p in params], total


def _on_real(entries):
    idxs = on_positions(entries)
    if not idxs:
        return []
    f, l = entries[idxs[0]], entries[idxs[-1]]
    if abs(l[1] - f[1]) < 0.01 and abs(l[2] - f[2]) < 0.01:
        return idxs[:-1]
    return idxs


# ---------------------------------------------------------------------------
# Reference resolution
# ---------------------------------------------------------------------------

def resolve_glyph(name, fonts, enc, memo, visiting):
    if name in memo:
        return memo[name]
    if name in visiting:
        return []
    visiting.add(name)
    g = fonts[name]
    out = [list(c) for c in g["contours"]]
    for enc2, tf in g["refs"]:
        target = enc.get(enc2)
        if target is None or target not in fonts:
            continue
        a, b, c2, d, e, f = tf
        for cont in resolve_glyph(target, fonts, enc, memo, visiting):
            out.append([(p[0], a * p[1] + c2 * p[2] + e, b * p[1] + d * p[2] + f)
                        + p[3:] for p in cont])
    visiting.remove(name)
    memo[name] = out
    return out


# ---------------------------------------------------------------------------
# Contour operations (all shape-preserving)
# ---------------------------------------------------------------------------

def split_segment(entries, i, j, u):
    """Split the segment between on-curve indices i and j at parameter u."""
    kind = entries[j][3]
    if kind == "l":
        M = lerp((entries[i][1], entries[i][2]),
                 (entries[j][1], entries[j][2]), u)
        entries.insert(j, ("on", M[0], M[1], "l", entries[j][4]))
        return True
    if entries[j][0] != "on":
        return False
    offs = [e for e in entries[i + 1:j] if e[0] == "off"]
    if len(offs) != 2:
        M = lerp((entries[i][1], entries[i][2]),
                 (entries[j][1], entries[j][2]), u)
        entries.insert(j, ("on", M[0], M[1], "l", entries[j][4]))
        return True
    P0 = (entries[i][1], entries[i][2])
    C1 = (offs[0][1], offs[0][2])
    C2 = (offs[1][1], offs[1][2])
    P3 = (entries[j][1], entries[j][2])
    p01 = lerp(P0, C1, u)
    p12 = lerp(C1, C2, u)
    p23 = lerp(C2, P3, u)
    p012 = lerp(p01, p12, u)
    p123 = lerp(p12, p23, u)
    M = lerp(p012, p123, u)
    flags = entries[j][4]
    new_block = [("off", p01[0], p01[1]), ("off", p012[0], p012[1]),
                 ("on", M[0], M[1], "c", flags),
                 ("off", p123[0], p123[1]), ("off", p23[0], p23[1]),
                 ("on", P3[0], P3[1], "c", flags)]
    entries[i + 1:j + 1] = new_block
    return True


def _insert_at_param(s, p):
    si_cur = on_positions(s)
    s_params, s_total = chord_params(s)
    if s_total == 0:
        return False
    target = p * s_total
    for kk in range(len(si_cur) - 1):
        seg_start = s_params[kk] * s_total
        seg_end = s_params[kk + 1] * s_total
        if seg_end - seg_start <= 1e-6:
            continue
        if seg_start - 1e-6 <= target <= seg_end + 1e-6:
            i, j = si_cur[kk], si_cur[kk + 1]
            u = max(0.02, min(0.98, (target - seg_start) / (seg_end - seg_start)))
            return split_segment(s, i, j, u)
    return False


def _insert_gain(s, p):
    """Node gain that _insert_at_param(s, p) will actually add.

    split_segment adds +3 on a cubic segment, +1 on a line/move fallback.
    The gain MUST be computed from the segment in *s* being split, not from
    the corresponding segment in the other contour (their kinds can differ),
    otherwise Phase A overshoots or undershoots the node budget.
    """
    si_cur = on_positions(s)
    s_params, s_total = chord_params(s)
    if s_total == 0:
        return 10**9
    target = p * s_total
    for kk in range(len(si_cur) - 1):
        seg_start = s_params[kk] * s_total
        seg_end = s_params[kk + 1] * s_total
        if seg_end - seg_start <= 1e-6:
            continue
        if seg_start - 1e-6 <= target <= seg_end + 1e-6:
            j = si_cur[kk + 1]
            return 3 if s[j][3] == "c" else 1
    return 10**9



def _line_segments(entries):
    idxs = on_positions(entries)
    return [(idxs[k], idxs[k + 1]) for k in range(len(idxs) - 1)
            if entries[idxs[k + 1]][3] == "l"]


def _convert_l_to_c(entries, i, j):
    """l -> degenerate c with collinear controls (shape-exact, +2 nodes)."""
    P0 = (entries[i][1], entries[i][2])
    P3 = (entries[j][1], entries[j][2])
    c1 = lerp(P0, P3, 1.0 / 3.0)
    c2 = lerp(P0, P3, 2.0 / 3.0)
    entries[j:j] = [("off", c1[0], c1[1]), ("off", c2[0], c2[1])]
    entries[j + 2] = ("on", P3[0], P3[1], "c", entries[j + 2][4])
    return True


def _point_in_polygon(pt, poly):
    """Ray-casting point-in-polygon over an on-curve point list."""
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xint = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xint:
                inside = not inside
    return inside


def _contour_contained(inner, outer, samples_per_seg=8):
    """True when `inner` lies fully inside `outer` (same winding, smaller
    area) — dropping it does not change the rendered shape."""
    if winding_of(inner) != winding_of(outer) or winding_of(inner) == 0:
        return False
    if shoelace(inner) >= shoelace(outer):
        return False
    outer_on = [(e[1], e[2]) for e in outer if e[0] == "on"]
    if len(outer_on) < 3:
        return False
    # every inner on-curve point inside outer
    for e in inner:
        if e[0] != "on":
            continue
        if not _point_in_polygon((e[1], e[2]), outer_on):
            return False
    # conservative: sample inner curve segments as well (cubics may bulge)
    inner_on = on_positions(inner)
    for k in range(len(inner_on) - 1):
        i, j = inner_on[k], inner_on[k + 1]
        P0 = (inner[i][1], inner[i][2])
        P3 = (inner[j][1], inner[j][2])
        offs = [e for e in inner[i + 1:j] if e[0] == "off"]
        if len(offs) == 2:
            C1 = (offs[0][1], offs[0][2])
            C2 = (offs[1][1], offs[1][2])
            for s in range(1, samples_per_seg):
                u = s / samples_per_seg
                p01 = lerp(P0, C1, u)
                p12 = lerp(C1, C2, u)
                p23 = lerp(C2, P3, u)
                q = lerp(lerp(p01, p12, u), lerp(p12, p23, u), u)
                if not _point_in_polygon(q, outer_on):
                    return False
        else:
            for s in range(1, samples_per_seg):
                q = lerp(P0, P3, s / samples_per_seg)
                if not _point_in_polygon(q, outer_on):
                    return False
    return True


def _remove_redundant(contours):
    """Drop contours that render nothing on top of the rest: fully-contained
    same-winding contours and degenerate contours (<3 on-curve points or
    zero shoelace area). Returns the cleaned contour list."""
    out = []
    for i, c in enumerate(contours):
        on = [e for e in c if e[0] == "on"]
        if len(on) < 3 or shoelace(c) < 1e-6:
            continue  # renders nothing
        if any(_contour_contained(c, other) for j, other in enumerate(contours) if j != i):
            continue  # fully inside another same-winding contour
        out.append(c)
    return out


def _merge_collinear_line(entries):
    """Remove one on-curve 'l' point whose two adjacent segments are
    collinear lines (shape-exact, -1 node). Returns True on success.

    The start point (kind 'm') and the closure duplicate are never removed.
    """
    idxs = on_positions(entries)
    if len(idxs) < 4:
        return False
    for k in range(1, len(idxs) - 1):  # skip start; skip closure
        i = idxs[k]
        nxt = idxs[k + 1]
        if entries[i][3] != "l" or entries[nxt][3] != "l":
            continue
        if i == idxs[0] or i == idxs[-1]:
            continue
        P0 = (entries[idxs[k - 1]][1], entries[idxs[k - 1]][2])
        P1 = (entries[i][1], entries[i][2])
        P2 = (entries[nxt][1], entries[nxt][2])
        vx, vy = P2[0] - P0[0], P2[1] - P0[1]
        L2 = vx * vx + vy * vy
        if L2 == 0:
            continue
        cross = (P1[0] - P0[0]) * vy - (P1[1] - P0[1]) * vx
        if abs(cross) > 1e-3 * L2:
            continue
        # P1 must lie BETWEEN P0 and P2
        dot = (P1[0] - P0[0]) * (P1[0] - P2[0]) + (P1[1] - P0[1]) * (P1[1] - P2[1])
        if dot > 0:
            continue
        del entries[i]
        return True
    return False


def _merge_collinear_pass(entries, count):
    """Apply _merge_collinear_line up to `count` times."""
    n = 0
    while n < count and _merge_collinear_line(entries):
        n += 1
    return n


def _is_degenerate_c(entries, i, j):
    """True if segment (i,j) is a cubic whose off-curve controls are
    collinear with the chord P0->P3 (shape-exactly a straight line)."""
    if entries[j][3] != "c":
        return False
    offs = [e for e in entries[i + 1:j] if e[0] == "off"]
    if len(offs) != 2:
        return False
    P0 = (entries[i][1], entries[i][2])
    P3 = (entries[j][1], entries[j][2])
    vx, vy = P3[0] - P0[0], P3[1] - P0[1]
    L2 = vx * vx + vy * vy
    if L2 == 0:
        return False
    for e in offs:
        cross = (e[1] - P0[0]) * vy - (e[2] - P0[1]) * vx
        if abs(cross) > 1e-3 * L2:
            return False
    return True


def _convert_c_to_line(entries, i, j):
    """Remove the collinear off-curve controls of a degenerate cubic segment
    (shape-exact, -2 nodes). Returns True on success."""
    if not _is_degenerate_c(entries, i, j):
        return False
    offs = [k for k in range(i + 1, j) if entries[k][0] == "off"]
    del entries[offs[1]]
    del entries[offs[0]]
    idx = j - 2
    entries[idx] = ("on", entries[idx][1], entries[idx][2], "l", entries[idx][4])
    return True


def equalize_pair(small, big):
    """Equalize node counts between two contours (curve-exact).

    Returns ``(new_small, new_big)`` or ``(None, None)`` when the exact
    count cannot be reached with shape-preserving operations.

    Operations (all shape-exact):
      on the SMALLER side (A): +1 line split, +2 l->degenerate-c,
      +3 cubic split (de Casteljau)
      on the LARGER side (B): -2 degenerate-c -> line
    Reachable diffs: any d != 1; d == 1 additionally requires a line
    segment in A.
    """
    s = [list(e) for e in small]
    b = [list(e) for e in big]
    d = len(b) - len(s)
    if d == 0:
        return s, b
    if d < 0:
        return None, None

    # Phase A: correspondence inserts at big's missing on-curve points
    b_params, b_total = chord_params(b)
    if b_total == 0:
        return None, None
    b_real = _on_real(b)
    for k in range(1, len(b_real)):
        remaining = len(b) - len(s)
        if remaining <= 0:
            break
        p = b_params[k]
        s_params, _ = chord_params(s)
        s_real = _on_real(s)
        pos = {eidx: kk for kk, eidx in enumerate(on_positions(s))}
        if any(abs(s_params[pos[idx]] - p) < 0.035 for idx in s_real):
            continue
        gain = _insert_gain(s, p)
        if gain > remaining:
            continue
        if not _insert_at_param(s, p):
            return None, None

    # Phase B: exact-gain planning (splits + line ops on s, -1 collinear
    # merge / -2 degenerate-c removal on b)
    guard = 0
    while True:
        rem = len(b) - len(s)
        if rem == 0:
            break
        if rem < 0 or guard > 300:
            return None, None
        guard += 1
        lines = _line_segments(s)
        b_idxs = on_positions(b)
        b_degen = [(b_idxs[k], b_idxs[k + 1]) for k in range(len(b_idxs) - 1)
                   if _is_degenerate_c(b, b_idxs[k], b_idxs[k + 1])]
        if rem % 3 == 1:
            # prefer -1 on b (collinear line merge); fall back to +1 on a
            if _merge_collinear_line(b):
                continue
            if lines:
                split_segment(s, *lines[-1], 0.5)
                continue
            return None, None
        if rem % 3 == 2:
            if _merge_collinear_line(b):
                continue
            if b_degen:
                _convert_c_to_line(b, *b_degen[-1])
                continue
            if lines:
                _convert_l_to_c(s, *lines[-1])
                continue
            if len(lines) >= 2:
                split_segment(s, *lines[-1], 0.5)
                split_segment(s, *lines[-2], 0.5)
                continue
            return None, None
        # rem % 3 == 0 and rem >= 3: cubic split on a
        idxs = on_positions(s)
        if len(idxs) < 2:
            return None, None
        split_segment(s, idxs[-2], idxs[-1], 0.5)
    if len(s) != len(b):
        return None, None
    return s, b


def reverse_contour(entries):
    """Reverse winding (cyclic reorder, segment kinds remapped)."""
    idxs = on_positions(entries)
    if len(idxs) < 3:
        return entries
    first = entries[idxs[0]]
    last = entries[idxs[-1]]
    is_closure = abs(last[1] - first[1]) < 0.01 and abs(last[2] - first[2]) < 0.01
    if not is_closure:
        return entries
    real = idxs[:-1]
    n = len(real)
    last_idx = idxs[-1]
    segs = []
    for k in range(n):
        if k == 0:
            kind = entries[last_idx][3]
            offs = [(e[1], e[2]) for e in entries[real[-1] + 1:last_idx]
                    if e[0] == "off"]
        else:
            prev = real[k - 1]
            i = real[k]
            kind = entries[i][3]
            offs = [(e[1], e[2]) for e in entries[prev + 1:i] if e[0] == "off"]
        segs.append((kind, offs))
    out = [("on", first[1], first[2], "m", first[4])]
    for k in range(1, n):
        pt = entries[real[n - k]]
        kind, offs = segs[(n - k + 1) % n]
        for ox, oy in reversed(offs):
            out.append(("off", ox, oy))
        out.append(("on", pt[1], pt[2], kind, pt[4]))
    kind1, offs1 = segs[1]
    for ox, oy in reversed(offs1):
        out.append(("off", ox, oy))
    out.append(("on", first[1], first[2], kind1, first[4]))
    return out


# ---------------------------------------------------------------------------
# Contour matching
# ---------------------------------------------------------------------------

def _pair_score(a_list, b_list, pairs):
    """Count pairing violations: far centroids, or far centroids + gross
    area mismatch (both indicate a crossed pairing)."""
    violations = 0
    for ia, ib in pairs:
        ca = centroid(a_list[ia])
        cb = centroid(b_list[ib])
        d = math.hypot(ca[0] - cb[0], ca[1] - cb[1])
        xs = [e[1] for e in a_list[ia]] + [e[1] for e in b_list[ib]]
        ys = [e[2] for e in a_list[ia]] + [e[2] for e in b_list[ib]]
        diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
        ar = shoelace(a_list[ia])
        ao = shoelace(b_list[ib])
        area_ratio = max(ar, ao) / min(ar, ao) if min(ar, ao) > 0 else 1.0
        if diag > 0 and d > 0.45 * diag:
            violations += 1
        elif diag > 0 and area_ratio > 4.0 and d > 0.3 * diag:
            violations += 1
    return violations


def match_contours(a_list, b_list):
    """Pair contours, preferring the candidate with zero violations.

    Candidate 1: area-rank (largest<->largest) — robust for glyphs with
    overlapping features (e.g. Aring, numbersign).
    Candidate 2: centroid-greedy — rescues glyphs where the area-rank
    pairing is ambiguous but centroids disambiguate cleanly.

    Returns a list of (ia, ib) pairs, or None when counts differ or both
    candidates violate (crossing risk — the caller skips the glyph).
    """
    if len(a_list) != len(b_list):
        return None
    n = len(a_list)
    a_order = sorted(range(n), key=lambda i: -shoelace(a_list[i]))
    b_order = sorted(range(n), key=lambda i: -shoelace(b_list[i]))
    ar_pairs = list(zip(a_order, b_order))
    used = set()
    cg_pairs = []
    for ia in sorted(range(n), key=lambda i: centroid(a_list[i])):
        best, bd = None, None
        for ib in range(n):
            if ib in used:
                continue
            ca = centroid(a_list[ia])
            cb = centroid(b_list[ib])
            d = (ca[0] - cb[0]) ** 2 + (ca[1] - cb[1]) ** 2
            if bd is None or d < bd:
                best, bd = ib, d
        used.add(best)
        cg_pairs.append((ia, best))
    s_ar = _pair_score(a_list, b_list, ar_pairs)
    s_cg = _pair_score(a_list, b_list, cg_pairs)
    if s_ar == 0:
        return ar_pairs
    if s_cg == 0:
        return cg_pairs
    if s_cg < s_ar:
        return cg_pairs
    return ar_pairs if s_ar < s_cg else None


# ---------------------------------------------------------------------------
# Glyph harmonization
# ---------------------------------------------------------------------------

def harmonize_glyph(name, fonts_a, fonts_b, enc_a, enc_b):
    ga = fonts_a[name]
    gb = fonts_b[name]
    memo_a, memo_b = {}, {}
    ca = resolve_glyph(name, fonts_a, enc_a, memo_a, set())
    cb = resolve_glyph(name, fonts_b, enc_b, memo_b, set())
    # Drop contours that render nothing (fully-contained same-winding or
    # degenerate) — shape-preserving at render level (engine v3).
    ca = _remove_redundant(ca)
    cb = _remove_redundant(cb)
    pairs = match_contours(ca, cb)
    if pairs is None:
        return None, "contour count mismatch (%d vs %d)" % (len(ca), len(cb))
    new_a, new_b = [], []
    for ia, ib in pairs:
        a, b = ca[ia], cb[ib]
        wa, wb = winding_of(a), winding_of(b)
        if wa != wb:
            if wb == 0 or wa == 0:
                return None, "degenerate winding"
            b = reverse_contour(b)
        if len(a) == len(b):
            eq_a, eq_b = a, b
        elif len(a) < len(b):
            eq_a, eq_b = equalize_pair(a, b)
            if eq_a is None:
                return None, "equalize failed (A%d < B%d)" % (len(a), len(b))
        else:
            eq_b, eq_a = equalize_pair(b, a)
            if eq_b is None:
                return None, "equalize failed (B%d < A%d)" % (len(b), len(a))
        if len(eq_a) != len(eq_b):
            return None, "post-equalize mismatch %d vs %d" % (len(eq_a), len(eq_b))
        new_a.append(eq_a)
        new_b.append(eq_b)
    return (new_a, new_b), None


# ---------------------------------------------------------------------------
# Write-back
# ---------------------------------------------------------------------------

def fmt_num(x):
    s = ("%.6f" % x).rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def write_glyph(g, contours, out_path):
    lines = [l for l in g["header"]]
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
    lines.extend(g["footer"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def entries_equal(cont_a, cont_b):
    if len(cont_a) != len(cont_b):
        return False
    for ca, cb in zip(cont_a, cont_b):
        if len(ca) != len(cb):
            return False
        for x, y in zip(ca, cb):
            if x[0] != y[0]:
                return False
            if abs(x[1] - y[1]) > 1e-6 or abs(x[2] - y[2]) > 1e-6:
                return False
            if x[0] == "on" and x[3] != y[3]:
                return False
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Structural harmonization engine")
    parser.add_argument("pair", choices=["RB", "IB"])
    args = parser.parse_args()

    src_a_name, src_b_name, out_a, out_b = MASTERS[args.pair]
    src_a = SOURCES / src_a_name
    src_b = SOURCES / src_b_name
    fonts_a, enc_a = load_font(src_a)
    fonts_b, enc_b = load_font(src_b)
    harm_a = HARMONIZED / out_a
    harm_b = HARMONIZED / out_b
    harm_a.mkdir(parents=True, exist_ok=True)
    harm_b.mkdir(parents=True, exist_ok=True)
    for d in (harm_a, harm_b):
        for f in list(d.glob("*.glyph")) + list(d.glob("font.props")):
            f.unlink()

    common = sorted(set(fonts_a) & set(fonts_b))
    only_a = sorted(set(fonts_a) - set(fonts_b))
    only_b = sorted(set(fonts_b) - set(fonts_a))

    n_harm = n_copy = n_ref = n_skip = 0
    skipped = []
    for name in common:
        refs_a = [(e[0], tuple(round(x, 3) for x in e[1])) for e in fonts_a[name]["refs"]]
        refs_b = [(e[0], tuple(round(x, 3) for x in e[1])) for e in fonts_b[name]["refs"]]
        if refs_a == refs_b and refs_a:
            n_ref += 1
            shutil.copy2(src_a / fonts_a[name]["fname"], harm_a / fonts_a[name]["fname"])
            shutil.copy2(src_b / fonts_b[name]["fname"], harm_b / fonts_b[name]["fname"])
            continue
        ca, cb = fonts_a[name]["contours"], fonts_b[name]["contours"]
        if (not refs_a and not refs_b and len(ca) == len(cb)
                and all(len(x) == len(y) and winding_of(x) == winding_of(y)
                        for x, y in zip(ca, cb))):
            n_copy += 1
            shutil.copy2(src_a / fonts_a[name]["fname"], harm_a / fonts_a[name]["fname"])
            shutil.copy2(src_b / fonts_b[name]["fname"], harm_b / fonts_b[name]["fname"])
            continue
        res, err = harmonize_glyph(name, fonts_a, fonts_b, enc_a, enc_b)
        if res is None:
            n_skip += 1
            skipped.append((name, err))
            shutil.copy2(src_a / fonts_a[name]["fname"], harm_a / fonts_a[name]["fname"])
            shutil.copy2(src_b / fonts_b[name]["fname"], harm_b / fonts_b[name]["fname"])
            continue
        new_a, new_b = res
        if entries_equal([list(c) for c in ca], new_a) and not refs_a:
            shutil.copy2(src_a / fonts_a[name]["fname"], harm_a / fonts_a[name]["fname"])
        else:
            write_glyph(fonts_a[name], new_a, harm_a / fonts_a[name]["fname"])
        if entries_equal([list(c) for c in cb], new_b) and not refs_b:
            shutil.copy2(src_b / fonts_b[name]["fname"], harm_b / fonts_b[name]["fname"])
        else:
            write_glyph(fonts_b[name], new_b, harm_b / fonts_b[name]["fname"])
        n_harm += 1

    for name in only_a:
        shutil.copy2(src_a / fonts_a[name]["fname"], harm_a / fonts_a[name]["fname"])
    for name in only_b:
        shutil.copy2(src_b / fonts_b[name]["fname"], harm_b / fonts_b[name]["fname"])
    shutil.copy2(src_a / "font.props", harm_a / "font.props")
    shutil.copy2(src_b / "font.props", harm_b / "font.props")

    print("pair=%s common=%d ref-copied=%d copied=%d harmonized=%d skipped=%d"
          % (args.pair, len(common), n_ref, n_copy, n_harm, n_skip))
    print("only_in_A=%d only_in_B=%d" % (len(only_a), len(only_b)))
    for name, err in skipped:
        print("SKIP %s: %s" % (name, err))


if __name__ == "__main__":
    main()
