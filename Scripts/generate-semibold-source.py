#!/usr/bin/env python3
"""Generate a SemiBold (weight 600) font source from a Regular or Italic source.

This standalone script emboldens an existing ``.sfdir`` source via FontForge's
``ChangeWeight`` API and writes the result to a new output directory. It is run
manually once by the maintainer and is never executed inside the CI pipeline
(Spec v1.1 ASSUMPTION-001).

Contract (Spec v1.1 section 4.1):
    python generate-semibold-source.py <input.sfdir> <output.sfdir>

Requirements covered: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06,
                      REQ-07, REQ-08, REQ-09
Constraints covered:  CON-01, CON-02, CON-03, CON-04, CON-05
Guidelines covered:   GUD-01, GUD-02, GUD-03
"""

import os
import sys

import fontforge

# Reference stroke in em-units, selected per the calibration contract
# (Spec v1.1 section 4.3): highest grid candidate in the 55-70 band
# passing the COMPOSITE AND gate (upright counters AND italic counters
# AND clearly heavier than Medium AND clearly lighter than Bold); else
# descend 50, then the 45 em-unit floor. Failing at or above the floor
# escalates to a maintainer decision.
# Reference value 60 (mid candidate grid) — final value locked during
# Phase 1 calibration BEFORE sources are committed.
STROKE_WIDTH = 70
# ChangeWeight embolden type (accepted by FontForge as "LCG" or "lcg").
EMBOLDEN_TYPE = "LCG"
# Counter handling: "retain" keeps inner counters as wide as before.
# NOTE: FontForge's Python binding is case-sensitive here and only accepts
# the lowercase spelling (see flaglist `co_types` in fontforge/python.cpp).
COUNTER_TYPE = "retain"
# Advance width of the Fantasque Sans Mono monospace grid, in em-units (REQ-05).
MONOSPACE_WIDTH = 1060
# Target CSS weight for the SemiBold variant (REQ-07).
SEMIBOLD_WEIGHT = 600
# FontForge weight name for the SemiBold variant (Spec v1.1 section 4.2).
# FontForge derives SFNT name IDs 3/16/17 from this string when the
# explicit name records are absent; the upright source would otherwise
# keep inheriting "Weight: Regular" from its input (GUD-02).
SEMIBOLD_WEIGHT_NAME = "SemiBold"

FAMILY_NAME = "Fantasque Sans Mono"
ITALIC_PREFIX = "FantasqueSansMono-Italic"

# SFNT name metadata per Spec v1.1 section 4.2.
UPRIGHT_NAMES = {
    "fontname": "FantasqueSansMono-SemiBold",
    "fullname": "Fantasque Sans Mono SemiBold",
    "sub_family": "SemiBold",
}
ITALIC_NAMES = {
    "fontname": "FantasqueSansMono-SemiBoldItalic",
    "fullname": "Fantasque Sans Mono SemiBold Italic",
    "sub_family": "SemiBold Italic",
}

USAGE = "Usage: python generate-semibold-source.py <input.sfdir> <output.sfdir>"


def generate_semibold(input_sfdir, output_sfdir):
    """Generate the SemiBold source at ``output_sfdir`` from ``input_sfdir``.

    The input source is opened read-only by intent; all geometry changes and
    metadata updates are applied to the in-memory font and written only to the
    output path (REQ-09).
    """
    font = fontforge.open(input_sfdir)

    is_italic = os.path.basename(os.path.normpath(input_sfdir)).startswith(
        ITALIC_PREFIX
    )
    names = ITALIC_NAMES if is_italic else UPRIGHT_NAMES

    # Weight and family metadata (REQ-07, Spec v1.1 section 4.2).
    # WHY: os2_weight must be set before weight — the inherited
    # OS2_WeightWidthSlopeOnly flag keeps the numeric class authoritative;
    # the Medium TASK-104 dump proved no ID 16/17 side effects (GUD-03).
    font.os2_weight = SEMIBOLD_WEIGHT
    font.weight = SEMIBOLD_WEIGHT_NAME
    font.familyname = FAMILY_NAME
    font.fontname = names["fontname"]
    font.fullname = names["fullname"]

    # SFNT name table entries (Spec v1.1 section 4.2).
    font.appendSFNTName("English (US)", "Family", FAMILY_NAME)
    font.appendSFNTName("English (US)", "SubFamily", names["sub_family"])
    font.appendSFNTName("English (US)", "Fullname", names["fullname"])
    font.appendSFNTName("English (US)", "PostScriptName", names["fontname"])

    # Embolden every glyph (REQ-04, GUD-01). The italic angle and the OS/2
    # italic flag are style-specific metrics that ChangeWeight does not touch,
    # so they are preserved by non-modification (REQ-03).
    font.selection.all()
    font.changeWeight(
        STROKE_WIDTH, EMBOLDEN_TYPE, 0, 0, COUNTER_TYPE
    )

    # Geometric cleanup (REQ-06): font-level removeOverlap + simplify.
    # NOTE (2026-08-13): a previously approved per-glyph `intersect()`
    # cleanup was REVERTED in the Medium round — `glyph.intersect()` is a
    # Boolean intersect that keeps only overlapping contour areas, which
    # destroys the non-overlapping outer/inner contours of most glyphs
    # (Medium plan Dead-End #11). The plan-exact sequence below preserves
    # all glyph geometry. Residual self-intersections from the LCG stroke
    # are documented as a known limitation, deferred to Phase 4 visual QA
    # (Spec v1.1 section 12).
    font.removeOverlap()
    font.simplify()

    # Enforce the monospace grid on every glyph (REQ-05).
    for glyph in font.glyphs():
        glyph.width = MONOSPACE_WIDTH

    font.save(output_sfdir)
    font.close()


def main(argv):
    """CLI entry point. Returns the process exit code."""
    if len(argv) != 3:
        print(USAGE, file=sys.stderr)
        return 1

    input_sfdir = argv[1]
    output_sfdir = argv[2]

    if os.path.abspath(input_sfdir) == os.path.abspath(output_sfdir):
        print("Error: input and output paths must differ", file=sys.stderr)
        return 1

    generate_semibold(input_sfdir, output_sfdir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
