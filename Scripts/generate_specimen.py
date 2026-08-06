#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fantasque Sans Mono — Specimen Sheet Generator.

Generates an HTML specimen sheet for visual review of multi-weight font
variants.  Displays waterfall text (8–72 pt), pangrams (English / Indonesian),
programming character sets, ligature sequences, code samples, and per-weight
metrics tables.

Usage::

    python3 Scripts/generate_specimen.py \\
        --weights WEIGHTS_DIR [--output HTML_DIR]

Contract: Spec §4.8
    * ``--weights`` is a directory of TTF files.
    * Output is written to ``Specimen/MultiWeight/`` by default.
    * Uses ``fontTools`` for metric extraction (local dev dependency, not CI).
"""

from __future__ import print_function

import argparse
import html
import os
import re
import sys

# Shared weight → OS/2 number mapping (PRN-001 — DRY, REF-014).
from font_weights import WEIGHT_OS2_CLASS

# ---------------------------------------------------------------------------
# Optional fontTools import for metric extraction
# ---------------------------------------------------------------------------
try:
    from fontTools.ttLib import TTFont

    _HAS_FONTTOOLS = True
except ImportError:
    _HAS_FONTTOOLS = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SAMPLE_TEXTS = {
    "pangram_en": "The quick brown fox jumps over the lazy dog. 0123456789",
    "pangram_id": (
        "Saya sedang menulis kode TypeScript dengan React dan Node.js."
        " 0123456789"
    ),
    "programming": r"{}[]()<>;:.,!#$%^&*+-=/\|~`@",
    "ligatures": (
        "-> => =>> <<- <- <= >= == != === !== "
        ":: ::= |> |] [| || |= |> "
        "// /* */ /** ///"
    ),
    "code": (
        "function fibonacci(n: number): number {\n"
        "    if (n <= 1) return n;\n"
        "    return fibonacci(n - 1) + fibonacci(n - 2);\n"
        "}"
    ),
}

FONT_SIZES = [8, 10, 12, 14, 16, 20, 24, 32, 48, 72]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_args(argv):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate multi-weight specimen sheet HTML."
    )
    parser.add_argument(
        "--weights",
        required=True,
        help="Directory containing TTF font files",
    )
    parser.add_argument(
        "--output",
        default="Specimen/MultiWeight",
        help="Output directory for HTML files (default: Specimen/MultiWeight)",
    )
    return parser.parse_args(argv)


def _discover_weights(weights_dir):
    """Discover TTF files and extract weight names.

    Returns a sorted list of ``(weight_name, file_path)`` tuples.
    """
    weights = []
    pattern = re.compile(r"FantasqueSansMono-(.+)\.ttf$")
    if not os.path.isdir(weights_dir):
        return weights
    for fname in sorted(os.listdir(weights_dir)):
        match = pattern.match(fname)
        if match:
            weights.append((match.group(1), os.path.join(weights_dir, fname)))
    return weights


def _extract_metrics(ttf_path):
    """Extract font metrics from a TTF file using fontTools.

    Returns a dict with ``x_height``, ``cap_height``, ``advance_width``,
    and ``stem_width`` keys, or empty dict if fontTools is unavailable.
    """
    if not _HAS_FONTTOOLS:
        return {}

    try:
        font = TTFont(ttf_path)
        os2 = font["OS/2"]
        hmtx = font["hmtx"]

        # Advance width: use 'n' or fallback to the most common width
        advance = None
        if "n" in hmtx.metrics:
            advance = hmtx.metrics["n"][0]
        else:
            # Fallback: take the first non-zero width
            for _name, (width, _lsb) in hmtx.metrics.items():
                if width > 0:
                    advance = width
                    break

        metrics = {
            "x_height": getattr(os2, "sxHeight", None),
            "cap_height": getattr(os2, "sCapHeight", None),
            "advance_width": advance,
            "stem_width": getattr(os2, "usStemV", None),
        }

        # REF-013: no x-height fallback. ``post.underlinePosition`` is the
        # underline position, NOT the x-height — substituting it reports
        # wrong data. Missing ``os2.sxHeight`` stays None and renders as
        # "—" in the metrics table.
        font.close()
        return metrics
    except Exception:
        return {}


def _fmt_metric(value):
    """Render a metrics-table cell; missing values show an em dash."""
    return "—" if value is None else str(value)


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def _css_font_faces(weights):
    """Generate @font-face CSS rules."""
    rules = []
    for weight_name, ttf_path in weights:
        num = WEIGHT_OS2_CLASS.get(weight_name, 400)
        rules.append(
            '@font-face {\n'
            '    font-family: "Fantasque Sans Mono";\n'
            '    src: url("../%s") format("truetype");\n'
            '    font-weight: %d;\n'
            '    font-style: normal;\n'
            '}\n' % (ttf_path, num)
        )
    return "\n".join(rules)


def _write_stylesheet(output_dir, weights):
    """Write specimen.css."""
    css = (
        "body {\n"
        "    font-family: \"Fantasque Sans Mono\", monospace;\n"
        "    background: #1a1a2e;\n"
        "    color: #e0e0e0;\n"
        "    margin: 0;\n"
        "    padding: 20px;\n"
        "}\n"
        "h1, h2, h3 {\n"
        "    color: #f0c040;\n"
        "}\n"
        "h1 { font-size: 32px; border-bottom: 2px solid #f0c040; padding-bottom: 8px; }\n"
        "h2 { font-size: 24px; margin-top: 32px; }\n"
        "h3 { font-size: 18px; color: #c0c0c0; }\n"
        "table {\n"
        "    border-collapse: collapse;\n"
        "    margin: 16px 0;\n"
        "    width: 100%;\n"
        "}\n"
        "th, td {\n"
        "    border: 1px solid #444;\n"
        "    padding: 8px 12px;\n"
        "    text-align: left;\n"
        "}\n"
        "th {\n"
        "    background: #2a2a3e;\n"
        "    color: #f0c040;\n"
        "}\n"
        ".weight-section {\n"
        "    margin-bottom: 40px;\n"
        "    border-left: 3px solid #f0c040;\n"
        "    padding-left: 16px;\n"
        "}\n"
        ".waterfall-line {\n"
        "    margin: 4px 0;\n"
        "    line-height: 1.2;\n"
        "}\n"
        ".size-label {\n"
        "    display: inline-block;\n"
        "    width: 36px;\n"
        "    color: #888;\n"
        "    font-size: 11px;\n"
        "    vertical-align: middle;\n"
        "}\n"
        ".checklist-pass { color: #4caf50; }\n"
        ".checklist-fail { color: #f44336; }\n"
        ".back-link { margin-bottom: 20px; }\n"
        ".back-link a { color: #f0c040; }\n"
        "nav { margin-bottom: 24px; }\n"
        "nav a { color: #f0c040; margin-right: 16px; }\n"
    )

    css += "\n" + _css_font_faces(weights)

    os.makedirs(output_dir, exist_ok=True)
    css_path = os.path.join(output_dir, "specimen.css")
    with open(css_path, "w") as fh:
        fh.write(css)
    return css_path


def _waterfall_line(text, size, label=True):
    """Generate a single waterfall line of HTML.

    If ``label`` is True, the line includes a size label.
    """
    label_html = '<span class="size-label">%d</span> ' % size if label else ""
    # REF-016: escape dynamic text — sample content may contain HTML
    # metacharacters (e.g. "<", ">", "&") in the future.
    return (
        '<div class="waterfall-line" style="font-size:%dpx">'
        "%s%s</div>" % (size, label_html, html.escape(text))
    )


def _write_index(output_dir, weights):
    """Write index.html — navigation page."""
    weight_items = ""
    for weight_name, _ in weights:
        weight_items += "<li>%s</li>\n" % html.escape(weight_name)

    html = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<title>Fantasque Sans Mono — Multi-Weight Specimen</title>\n'
        '<link rel="stylesheet" href="specimen.css">\n'
        '</head>\n'
        '<body>\n'
        '<h1>Fantasque Sans Mono — Multi-Weight Specimen</h1>\n'
        '<nav>\n'
        '<a href="waterfall.html">Waterfall</a>\n'
        '<a href="pangrams.html">Pangrams</a>\n'
        '<a href="programming.html">Programming</a>\n'
        '<a href="metrics.html">Metrics</a>\n'
        '<a href="discontinuity_checklist.html">Discontinuity Checklist</a>\n'
        '</nav>\n'
        '<h2>Available Weights</h2>\n'
        '<ul>\n%s</ul>\n'
        '</body>\n'
        '</html>\n'
    ) % weight_items

    path = os.path.join(output_dir, "index.html")
    with open(path, "w") as fh:
        fh.write(html)
    return path


def _write_waterfall(output_dir, weights):
    """Write waterfall.html — multi-size text display."""
    sections = ""
    for weight_name, _ in weights:
        lines = ""
        for size in FONT_SIZES:
            lines += _waterfall_line(SAMPLE_TEXTS["pangram_en"], size)
            lines += _waterfall_line(SAMPLE_TEXTS["code"].replace("\n", " "), size)

        sections += (
            '<div class="weight-section">\n'
            '<h2>%s (%s)</h2>\n'
            '%s\n'
            '</div>\n'
        ) % (html.escape(weight_name), _weight_number(weight_name), lines)

    html = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<title>Waterfall — Fantasque Sans Mono</title>\n'
        '<link rel="stylesheet" href="specimen.css">\n'
        '</head>\n'
        '<body>\n'
        '<div class="back-link"><a href="index.html">← Index</a></div>\n'
        '<h1>Waterfall (8–72 pt)</h1>\n'
        '%s\n'
        '</body>\n'
        '</html>\n'
    ) % sections

    path = os.path.join(output_dir, "waterfall.html")
    with open(path, "w") as fh:
        fh.write(html)
    return path


def _write_pangrams(output_dir, weights):
    """Write pangrams.html."""
    sections = ""
    for weight_name, _ in weights:
        lines = (
            _waterfall_line(SAMPLE_TEXTS["pangram_en"], 16) +
            _waterfall_line(SAMPLE_TEXTS["pangram_id"], 16)
        )
        sections += (
            '<div class="weight-section">\n'
            '<h2>%s (%s)</h2>\n'
            '%s\n'
            '</div>\n'
        ) % (html.escape(weight_name), _weight_number(weight_name), lines)

    html = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<title>Pangrams — Fantasque Sans Mono</title>\n'
        '<link rel="stylesheet" href="specimen.css">\n'
        '</head>\n'
        '<body>\n'
        '<div class="back-link"><a href="index.html">← Index</a></div>\n'
        '<h1>Pangrams (English &amp; Indonesian)</h1>\n'
        '%s\n'
        '</body>\n'
        '</html>\n'
    ) % sections

    path = os.path.join(output_dir, "pangrams.html")
    with open(path, "w") as fh:
        fh.write(html)
    return path


def _write_programming(output_dir, weights):
    """Write programming.html."""
    sections = ""
    for weight_name, _ in weights:
        lines = (
            _waterfall_line(SAMPLE_TEXTS["programming"], 16) +
            _waterfall_line(SAMPLE_TEXTS["ligatures"], 16) +
            _waterfall_line(SAMPLE_TEXTS["code"].replace("\n", " "), 14)
        )
        sections += (
            '<div class="weight-section">\n'
            '<h2>%s (%s)</h2>\n'
            '%s\n'
            '</div>\n'
        ) % (html.escape(weight_name), _weight_number(weight_name), lines)

    html = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<title>Programming — Fantasque Sans Mono</title>\n'
        '<link rel="stylesheet" href="specimen.css">\n'
        '</head>\n'
        '<body>\n'
        '<div class="back-link"><a href="index.html">← Index</a></div>\n'
        '<h1>Programming Characters &amp; Ligatures</h1>\n'
        '%s\n'
        '</body>\n'
        '</html>\n'
    ) % sections

    path = os.path.join(output_dir, "programming.html")
    with open(path, "w") as fh:
        fh.write(html)
    return path


def _write_metrics(output_dir, weights):
    """Write metrics.html with per-weight font metrics."""
    rows = ""
    for weight_name, ttf_path in weights:
        m = _extract_metrics(ttf_path)
        rows += (
            '<tr>'
            '<td>%s</td>'
            '<td>%s</td>'
            '<td>%s</td>'
            '<td>%s</td>'
            '<td>%s</td>'
            '</tr>\n'
        ) % (
            html.escape(weight_name),
            _fmt_metric(m.get("x_height")),
            _fmt_metric(m.get("cap_height")),
            _fmt_metric(m.get("advance_width")),
            _fmt_metric(m.get("stem_width")),
        )

    html = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<title>Metrics — Fantasque Sans Mono</title>\n'
        '<link rel="stylesheet" href="specimen.css">\n'
        '</head>\n'
        '<body>\n'
        '<div class="back-link"><a href="index.html">← Index</a></div>\n'
        '<h1>Font Metrics per Weight</h1>\n'
        '<table>\n'
        '<tr>'
        '<th>Weight</th>'
        '<th>x-height</th>'
        '<th>Cap Height</th>'
        '<th>Advance Width</th>'
        '<th>Stem Width</th>'
        '</tr>\n'
        '%s\n'
        '</table>\n'
        '</body>\n'
        '</html>\n'
    ) % rows

    path = os.path.join(output_dir, "metrics.html")
    with open(path, "w") as fh:
        fh.write(html)
    return path


def _write_discontinuity_checklist(output_dir, weights):
    """Write discontinuity_checklist.html for 48pt and 72pt review."""
    sections = ""
    for weight_name, _ in weights:
        checklist = ""
        checks = [
            "Counter shape preserved?",
            "Bézier asymmetry maintained?",
            "Terminal style consistent?",
            "No sharp angle discontinuity?",
            "Stem width proportional?",
        ]
        for chk in checks:
            checklist += (
                '<tr><td>%s</td><td class="checklist-fail">☐</td></tr>\n'
                % html.escape(chk)
            )

        sections += (
            '<div class="weight-section">\n'
            '<h2>%s (%s)</h2>\n'
            '<table>\n%s</table>\n'
            '</div>\n'
        ) % (html.escape(weight_name), _weight_number(weight_name), checklist)

    html = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<title>Discontinuity Checklist — Fantasque Sans Mono</title>\n'
        '<link rel="stylesheet" href="specimen.css">\n'
        '</head>\n'
        '<body>\n'
        '<div class="back-link"><a href="index.html">← Index</a></div>\n'
        '<h1>Discontinuity Checklist (48 pt &amp; 72 pt)</h1>\n'
        '<p>Review each weight at both 48pt and 72pt for the following.</p>\n'
        '%s\n'
        '</body>\n'
        '</html>\n'
    ) % sections

    path = os.path.join(output_dir, "discontinuity_checklist.html")
    with open(path, "w") as fh:
        fh.write(html)
    return path


def _weight_number(weight_name):
    """Map weight name to CSS font-weight number (string form)."""
    return str(WEIGHT_OS2_CLASS.get(weight_name, 400))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = _parse_args(sys.argv[1:])
    weights = _discover_weights(args.weights)

    if not weights:
        print("generate_specimen: no TTF files found in %s" % args.weights,
              file=sys.stderr)
        sys.exit(1)

    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    print("generate_specimen: found %d weight(s) in %s"
          % (len(weights), args.weights))

    _write_stylesheet(output_dir, weights)
    _write_index(output_dir, weights)
    _write_waterfall(output_dir, weights)
    _write_pangrams(output_dir, weights)
    _write_programming(output_dir, weights)
    _write_metrics(output_dir, weights)
    _write_discontinuity_checklist(output_dir, weights)

    print("generate_specimen: HTML specimen written to %s" % output_dir)


if __name__ == "__main__":
    main()
