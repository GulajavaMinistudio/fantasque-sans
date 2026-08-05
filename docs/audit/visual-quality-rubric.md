# Visual Quality Rubric — Fantasque Sans Mono Multi-Weight

![Status: Draft](https://img.shields.io/badge/status-Draft-orange)
![Version: 1.0](https://img.shields.io/badge/version-1.0-blue)

## Purpose

This document defines the measurable visual quality standards for judging
interpolated weight glyphs.  It serves as the reference for:

- **Phase 1 PoC gate** (AC-P03): ≥ 90% of glyphs judged "maintain handwritten feel"
- **Phase 3 QA** (AC-I06): ≤ 2% minor artifacts
- **`validate_interpolation.py`** classification: `pass` / `warning` / `fail`

## Gold Standard Reference Glyphs

The following glyphs from the existing **Regular (400)** master exemplify the
"wibbly-wobbly" handwritten aesthetic that MUST be preserved in all derived
weights.  Reviewers should use these as visual anchors.

| Glyph | Key Characteristics |
|---|---|
| `a` | Asymmetric bowl, slightly tilted terminal |
| `g` | Double-storey with organic ear curve, open tail |
| `&` | Multi-contour complexity, graceful loops |
| `@` | Concentric circles with subtle irregularity |
| `Q` | Tail extends past baseline with slight rightward lean |
| `?` | Dot detached, curve not perfectly circular |
| `S` | Upper counter slightly smaller than lower |

## Unacceptable Distortions

The following artifacts are classified as **fail** and the glyph MUST be
returned to harmonization (FR-5.3):

1. **Closed Counter** — An interior counter shape has collapsed, turning a
   "hole" glyph into a solid silhouette (e.g., `a`, `e`, `g`, `8`, `&`, `@`).

2. **Self-Intersection** — A contour crosses over itself, creating a figure-8
   loop or tangled path that would render with inverted fill.

3. **Broken Contour** — A contour has fewer than 2 points or an open path flag
   where closed is expected, producing a rendering artifact.

4. **Overly Stiff Curve** — The handwriting fuzziness has been smoothed away
   entirely; the glyph looks mechanically perfect (like Consolas or Fira Code)
   rather than retaining the organic "wibbly-wobbly" quality.

## Minor Artifacts (Warning)

The following artifacts are classified as **warning** and accepted up to ≤ 2%
of total glyphs.  They do not block the build:

1. **Tangent-Angle Discontinuity** — A sharp angle between consecutive curve
   segments where the original master had a smooth transition.  Threshold
   calibrated during Phase 1 PoC (two-pass protocol, Spec §4.11).

2. **Stem Width Asymmetry** — Slight variation (≤ 3%) in stem thickness
   between corresponding stems (e.g., left vs right of `H`), detectable only
   at 24+ pt.

3. **Terminal Drift** — A finial or terminal has shifted position by ≤ 2% of
   the em-square relative to the master, not noticeable at text sizes.

## Per-Glyph Review Checklist

For each glyph being reviewed at 48 pt and 72 pt, evaluate:

- [ ] **Counter shape preserved?** — Interior counters retain their organic
  asymmetry (Hard Invariant: REQ-H05).
- [ ] **Bézier asymmetry maintained?** — Curve extrema are slightly off the
  geometric ideal; no mechanical perfection.
- [ ] **Terminal style consistent?** — Ball terminals, finials, and serif
  hints match the master's style across weights.
- [ ] **No sharp angle discontinuity?** — Smooth curve transitions; no
  unexpected "corner points" (Soft Invariant: REQ-H06).
- [ ] **Stem width proportional?** — Stems scale smoothly between Regular and
  Bold without sudden jumps at intermediate weights.

## Throughput Benchmarks

Derived from Phase 0 experiment E0.3 (2-designer parallel simulation):

| Metric | Value |
|---|---|
| Harmonization throughput (glyph/hour, single designer) | TBD — calibrated in E0.3 |
| Review throughput (glyph/hour) | TBD — calibrated in Phase 1 |
| Shared pool conflict rate | TBD — calibrated in E0.3 |

## Threshold Calibration Log

| Date | Threshold | Calibration Pass | Source |
|---|---|---|---|
| 2026-08-XX | 15.0° (initial) | R1 | Default (`--threshold 15.0`) |
| TBD | T_final | R2 | Two-pass protocol (Spec §4.11) |
