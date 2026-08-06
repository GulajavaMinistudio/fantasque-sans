#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for ``Scripts/tangent_analysis.py`` (REF-006 / PRN-001).

The shared module is deliberately dependency-free (no FontForge import), so
these tests run on the host runner with plain point/contour/layer dummies.
Test cases per TEST-REF-006: square (90° corners), equilateral triangle
(60° corners), and degenerate inputs (collinear points, < 3 points,
missing foreground).
"""

import os
import sys

import pytest

# Make ``Scripts/`` importable as a package-less module path.
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "Scripts")
sys.path.insert(0, SCRIPTS_DIR)

import tangent_analysis as _mod  # noqa: E402


# ---------------------------------------------------------------------------
# Minimal FontForge-shape dummies (index-based access, .x/.y points)
# ---------------------------------------------------------------------------

class _Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


class _Contour:
    def __init__(self, points):
        self._points = points

    def __len__(self):
        return len(self._points)

    def __getitem__(self, i):
        return self._points[i]


class _Layer:
    def __init__(self, contours):
        self._contours = contours

    def __len__(self):
        return len(self._contours)

    def __getitem__(self, i):
        return self._contours[i]


class _Glyph:
    def __init__(self, contours=None, has_foreground=True):
        self._contours = contours or []
        self._has_foreground = has_foreground

    @property
    def foreground(self):
        if not self._has_foreground:
            raise AttributeError("glyph has no foreground layer")
        return _Layer(self._contours)


def _contour(*xy_pairs):
    return _Contour([_Point(x, y) for x, y in xy_pairs])


# ---------------------------------------------------------------------------
# extract_on_curve_triples
# ---------------------------------------------------------------------------

def test_extract_on_curve_triples_wraps_around():
    c = _contour((0, 0), (10, 0), (10, 10), (0, 10))
    triples = _mod.extract_on_curve_triples(c)

    assert len(triples) == 4
    # i=0: (last, first, second)
    assert triples[0][0] is c[3]
    assert triples[0][1] is c[0]
    assert triples[0][2] is c[1]
    # i=1: (first, second, third)
    assert triples[1] == (c[0], c[1], c[2])
    # Last triple wraps: (c[2], c[3], c[0])
    assert triples[3] == (c[2], c[3], c[0])


def test_extract_on_curve_triples_fewer_than_3_points():
    c = _contour((0, 0), (10, 0))
    assert _mod.extract_on_curve_triples(c) == []


def test_extract_on_curve_triples_empty_contour():
    assert _mod.extract_on_curve_triples(_Contour([])) == []


# ---------------------------------------------------------------------------
# compute_max_tangent_angle
# ---------------------------------------------------------------------------

def test_compute_max_tangent_angle_square_returns_90():
    """A square has 90° corners."""
    glyph = _Glyph([_contour((0, 0), (100, 0), (100, 100), (0, 100))])
    assert _mod.compute_max_tangent_angle(glyph) == pytest.approx(90.0)


def test_compute_max_tangent_angle_equilateral_triangle_returns_120():
    """An equilateral triangle has interior angles of 60°, so the edge
    direction TURNS by 180° − 60° = 120° at each vertex."""
    # height = 100 * sin(60°) ≈ 86.6025
    glyph = _Glyph([_contour((0, 0), (100, 0), (50, 86.60254037844386))])
    assert _mod.compute_max_tangent_angle(glyph) == pytest.approx(120.0)


def test_compute_max_tangent_angle_collinear_closed_contour_returns_180():
    """A closed contour whose points are all collinear must reverse course
    at the closure point — an unavoidable 180° turning angle."""
    glyph = _Glyph([_contour((0, 0), (50, 0), (100, 0))])
    assert _mod.compute_max_tangent_angle(glyph) == pytest.approx(180.0)


def test_compute_max_tangent_angle_takes_max_across_contours():
    """Mixed contours: worst angle wins (triangle 120° > square 90°)."""
    glyph = _Glyph([
        _contour((0, 0), (100, 0), (50, 86.60254037844386)),
        _contour((0, 0), (100, 0), (100, 100), (0, 100)),
    ])
    assert _mod.compute_max_tangent_angle(glyph) == pytest.approx(120.0)


def test_compute_max_tangent_angle_empty_glyph_returns_zero():
    assert _mod.compute_max_tangent_angle(_Glyph([])) == 0.0


def test_compute_max_tangent_angle_missing_foreground_returns_zero():
    glyph = _Glyph(has_foreground=False)
    assert _mod.compute_max_tangent_angle(glyph) == 0.0


def test_compute_max_tangent_angle_skips_degenerate_segments():
    """Zero-length segments are skipped without raising; the angle from the
    remaining valid corners is still reported (square → 90°)."""
    glyph = _Glyph([_contour((0, 0), (0, 0), (100, 0), (100, 100), (0, 100))])
    assert _mod.compute_max_tangent_angle(glyph) == 90.0
