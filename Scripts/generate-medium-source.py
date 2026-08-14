#!/usr/bin/env python3
"""Generate a Medium (weight 500) font source from a Regular or Italic source.

This standalone script emboldens an existing ``.sfdir`` source via FontForge's
``ChangeWeight`` API and writes the result to a new output directory. It is run
manually once by the maintainer and is never executed inside the CI pipeline
(Spec v1.2 ASSUMPTION-001).

Contract (Spec v1.2 section 4):
    python generate-medium-source.py <input.sfdir> <output.sfdir>

Requirements covered: REQ-01, REQ-02, REQ-03
Constraints covered:  CON-01, CON-02, CON-03, CON-04, CON-05, CON-06
Guideline covered:    GUD-01
"""

import os
import sys

import fontforge

# Stroke expansion in em-units (GUD-01: +30 to +40; reference value 34).
STROKE_WIDTH = 34
# ChangeWeight embolden type (accepted by FontForge as "LCG" or "lcg").
EMBOLDEN_TYPE = "LCG"
# Counter handling: "retain" keeps inner counters as wide as before.
# NOTE: FontForge's Python binding is case-sensitive here and only accepts
# the lowercase spelling (see flaglist `co_types` in fontforge/python.cpp).
COUNTER_TYPE = "retain"
# Advance width of the Fantasque Sans Mono monospace grid, in em-units (CON-02).
MONOSPACE_WIDTH = 1060
# Target CSS weight for the Medium variant (CON-04).
MEDIUM_WEIGHT = 500

FAMILY_NAME = "Fantasque Sans Mono"
ITALIC_PREFIX = "FantasqueSansMono-Italic"

# SFNT name metadata per Spec v1.2 section 4.2.
UPRIGHT_NAMES = {
    "fontname": "FantasqueSansMono-Medium",
    "fullname": "Fantasque Sans Mono Medium",
    "sub_family": "Medium",
}
ITALIC_NAMES = {
    "fontname": "FantasqueSansMono-MediumItalic",
    "fullname": "Fantasque Sans Mono Medium Italic",
    "sub_family": "Medium Italic",
}

USAGE = "Usage: python generate-medium-source.py <input.sfdir> <output.sfdir>"


def generate_medium(input_sfdir, output_sfdir):
    """Generate the Medium source at ``output_sfdir`` from ``input_sfdir``.

    The input source is opened read-only by intent; all geometry changes and
    metadata updates are applied to the in-memory font and written only to the
    output path (CON-06).
    """
    font = fontforge.open(input_sfdir)

    is_italic = os.path.basename(os.path.normpath(input_sfdir)).startswith(
        ITALIC_PREFIX
    )
    names = ITALIC_NAMES if is_italic else UPRIGHT_NAMES

    # Weight and family metadata (CON-04, Spec section 4.2).
    font.os2_weight = MEDIUM_WEIGHT
    font.familyname = FAMILY_NAME
    font.fontname = names["fontname"]
    font.fullname = names["fullname"]

    # SFNT name table entries (Spec section 4.2).
    font.appendSFNTName("English (US)", "Family", FAMILY_NAME)
    font.appendSFNTName("English (US)", "SubFamily", names["sub_family"])
    font.appendSFNTName("English (US)", "Fullname", names["fullname"])
    font.appendSFNTName("English (US)", "PostScriptName", names["fontname"])

    # Embolden every glyph (CON-01, GUD-01). The italic angle and the OS/2
    # italic flag are style-specific metrics that ChangeWeight does not touch,
    # so they are preserved by non-modification (REQ-03).
    font.selection.all()
    font.changeWeight(
        STROKE_WIDTH, EMBOLDEN_TYPE, 0, 0, COUNTER_TYPE
    )

    # Geometric cleanup (CON-03): font-level removeOverlap + simplify.
    # NOTE (2026-08-13): a previously approved per-glyph `intersect()`
    # cleanup was REVERTED — `glyph.intersect()` is a Boolean intersect
    # that keeps only overlapping contour areas, which destroys the
    # non-overlapping outer/inner contours of most glyphs. The plan-exact
    # sequence below preserves all glyph geometry. Residual
    # self-intersections from the LCG stroke are documented as a known
    # limitation, deferred to Phase 4 visual QA (Spec §12).
    font.removeOverlap()
    font.simplify()

    # Enforce the monospace grid on every glyph (CON-02).
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

    generate_medium(input_sfdir, output_sfdir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
