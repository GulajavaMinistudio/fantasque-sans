#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fantasque Sans Mono — Shared Tangent-Angle Analysis Module.

Single source of truth for the tangent-angle discontinuity computation used
by the harmonization validator (``validate_harmonization.py``, Spec §4.5)
and the interpolation validator (``validate_interpolation.py``, Spec §4.11).

Contract: Spec §4.5 / §4.11
    * ``compute_max_tangent_angle(glyph)`` — maximum discontinuity across
      all contours of a glyph, in degrees (0.0 for degenerate inputs).
    * ``extract_on_curve_triples(contour)`` — consecutive point triples
      with wraparound, one per point in the contour.

This module is intentionally dependency-free (stdlib only): it must be
importable from host-side unit tests without a FontForge installation.
"""

from __future__ import print_function

import math


def extract_on_curve_triples(contour):
    """Extract consecutive point triples from a contour, wrapping at the ends.

    Returns a list of ``(prev_pt, this_pt, next_pt)`` triples — one per
    point in the contour (points are iterated in contour order).  Returns
    an empty list if the contour has fewer than 3 points.
    """
    points = [contour[i] for i in range(len(contour))]
    n = len(points)
    if n < 3:
        return []
    return [
        (points[(i - 1) % n], points[i], points[(i + 1) % n])
        for i in range(n)
    ]


def compute_max_tangent_angle(glyph):
    """Return the maximum tangent-angle discontinuity across all contours.

    The angle is measured in degrees between the incoming edge direction
    (prev → this) and the outgoing edge direction (this → next) at every
    point of every contour.  Returns 0.0 if the glyph has no usable point
    triples (fewer than 3 points per contour, degenerate zero-length
    segments, or an unreadable foreground layer).
    """
    try:
        layer = glyph.foreground
    except Exception:
        return 0.0

    overall_max = 0.0
    for i in range(len(layer)):
        triples = extract_on_curve_triples(layer[i])
        for prev_pt, this_pt, next_pt in triples:
            # Incoming vector: prev → this
            dx_in = this_pt.x - prev_pt.x
            dy_in = this_pt.y - prev_pt.y
            mag_in = math.sqrt(dx_in * dx_in + dy_in * dy_in)

            # Outgoing vector: this → next
            dx_out = next_pt.x - this_pt.x
            dy_out = next_pt.y - this_pt.y
            mag_out = math.sqrt(dx_out * dx_out + dy_out * dy_out)

            if mag_in < 1e-9 or mag_out < 1e-9:
                # Degenerate segment — skip angle check
                continue

            # Dot product → angle
            dot = dx_in * dx_out + dy_in * dy_out
            cos_angle = dot / (mag_in * mag_out)
            # Clamp for floating-point safety
            cos_angle = max(-1.0, min(1.0, cos_angle))
            angle = math.degrees(math.acos(cos_angle))

            if angle > overall_max:
                overall_max = angle

    return overall_max
