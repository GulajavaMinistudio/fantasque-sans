#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for ``Scripts/detect_incompatibility.py``.

All FontForge-dependent tests are guarded by
``pytest.importorskip("fontforge")`` so the suite passes cleanly on
host runners without FontForge installed.  Real execution occurs inside
the ``builder-fontforge`` Docker image (Stage 1, RUN chain).

Test cases: Spec §6.3 (8 test cases).
"""

import json
import os
import sys
import tempfile
import textwrap

import pytest


# ---------------------------------------------------------------------------
# FontForge guard
# ---------------------------------------------------------------------------
ff = pytest.importorskip("fontforge")

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "Scripts")
sys.path.insert(0, SCRIPTS_DIR)

import detect_incompatibility as _mod  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_test_font(glyph_specs):
    """Create an in-memory FontForge font from a list of glyph specs.

    Each spec is a ``(name, contours)`` tuple where ``contours`` is a list of
    ``[(x, y), ...]`` point lists.
    """
    font = ff.font()
    font.fontname = "TestFont"
    font.familyname = "Test"
    font.fullname = "Test"

    for name, contours in glyph_specs:
        glyph = font.createChar(-1, name)
        glyph.width = 600
        layer = ff.layer()
        for pts in contours:
            cont = ff.contour()
            for x, y in pts:
                cont += ff.point(x, y)
            cont.closed = True
            layer += cont
        glyph.foreground = layer

    return font


def _save_to_temp(font):
    """Save a font to a temporary .sfdir and return the path."""
    tmp = tempfile.mkdtemp(prefix="test_detect_")
    font.save(tmp)
    return tmp


# ---------------------------------------------------------------------------
# Test 1: Identical glyphs → "compatible"
# ---------------------------------------------------------------------------

def test_identical_glyphs_pass():
    """Two identical glyphs should be reported as compatible."""
    spec = [
        ("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
    ]
    font_a = _make_test_font(spec)
    font_b = _make_test_font(spec)

    dir_a = _save_to_temp(font_a)
    dir_b = _save_to_temp(font_b)

    report = _mod._detect(dir_a, dir_b)

    assert report["compatible_count"] == 1
    assert report["incompatible_count"] == 0
    assert report["glyphs"][0]["status"] == "compatible"


# ---------------------------------------------------------------------------
# Test 2: Node count mismatch → "incompatible", node_diff filled
# ---------------------------------------------------------------------------

def test_node_count_mismatch():
    """Glyphs with different node counts should be incompatible with node_diff."""
    spec_a = [
        ("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),  # 4 nodes
    ]
    spec_b = [
        ("A", [[(0, 0), (100, 0), (100, 100)]],),  # 3 nodes
    ]
    font_a = _make_test_font(spec_a)
    font_b = _make_test_font(spec_b)

    dir_a = _save_to_temp(font_a)
    dir_b = _save_to_temp(font_b)

    report = _mod._detect(dir_a, dir_b)

    assert report["incompatible_count"] == 1
    glyph = report["glyphs"][0]
    assert glyph["status"] == "incompatible"
    assert "node_diff" in glyph


# ---------------------------------------------------------------------------
# Test 3: Contour count mismatch → "incompatible", contour_diff filled
# ---------------------------------------------------------------------------

def test_contour_count_mismatch():
    """Glyphs with different contour counts should be incompatible."""
    spec_a = [
        ("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),  # 1 contour
    ]
    spec_b = [
        ("A", [[(0, 0), (100, 0), (100, 100), (0, 100)],
                [(20, 20), (80, 20), (80, 80), (20, 80)]]),  # 2 contours
    ]
    font_a = _make_test_font(spec_a)
    font_b = _make_test_font(spec_b)

    dir_a = _save_to_temp(font_a)
    dir_b = _save_to_temp(font_b)

    report = _mod._detect(dir_a, dir_b)

    assert report["incompatible_count"] == 1
    glyph = report["glyphs"][0]
    assert glyph["status"] == "incompatible"
    assert "contour_diff" in glyph


# ---------------------------------------------------------------------------
# Test 4: Curve direction mismatch → "incompatible"
# ---------------------------------------------------------------------------

def test_curve_direction_mismatch():
    """Glyphs with opposite curve directions should be incompatible."""
    # Clockwise: points in clockwise order
    spec_a = [
        ("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
    ]
    # Counter-clockwise
    spec_b = [
        ("A", [[(0, 0), (0, 100), (100, 100), (100, 0)]]),
    ]
    font_a = _make_test_font(spec_a)
    font_b = _make_test_font(spec_b)

    dir_a = _save_to_temp(font_a)
    dir_b = _save_to_temp(font_b)

    report = _mod._detect(dir_a, dir_b)

    assert report["incompatible_count"] == 1
    glyph = report["glyphs"][0]
    assert glyph["status"] == "incompatible"


# ---------------------------------------------------------------------------
# Test 5: Glyph only in master A → "only_in_a"
# ---------------------------------------------------------------------------

def test_glyph_only_in_a():
    """Glyphs present only in master A should be reported."""
    spec_a = [
        ("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
        ("B", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
    ]
    spec_b = [
        ("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
    ]
    font_a = _make_test_font(spec_a)
    font_b = _make_test_font(spec_b)

    dir_a = _save_to_temp(font_a)
    dir_b = _save_to_temp(font_b)

    report = _mod._detect(dir_a, dir_b)

    assert report["only_in_a_count"] == 1
    only_a = [g for g in report["glyphs"] if g["name"] == "B"]
    assert len(only_a) == 1
    assert only_a[0]["status"] == "only_in_a"


# ---------------------------------------------------------------------------
# Test 6: Glyph only in master B → "only_in_b"
# ---------------------------------------------------------------------------

def test_glyph_only_in_b():
    """Glyphs present only in master B should be reported."""
    spec_a = [
        ("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
    ]
    spec_b = [
        ("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
        ("C", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
    ]
    font_a = _make_test_font(spec_a)
    font_b = _make_test_font(spec_b)

    dir_a = _save_to_temp(font_a)
    dir_b = _save_to_temp(font_b)

    report = _mod._detect(dir_a, dir_b)

    assert report["only_in_b_count"] == 1
    only_b = [g for g in report["glyphs"] if g["name"] == "C"]
    assert len(only_b) == 1
    assert only_b[0]["status"] == "only_in_b"


# ---------------------------------------------------------------------------
# Test 7: Output JSON valid against schema
# ---------------------------------------------------------------------------

def test_report_json_valid():
    """Output JSON should contain all required fields."""
    spec_a = [
        ("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
    ]
    spec_b = [
        ("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
    ]
    font_a = _make_test_font(spec_a)
    font_b = _make_test_font(spec_b)

    dir_a = _save_to_temp(font_a)
    dir_b = _save_to_temp(font_b)

    report = _mod._detect(dir_a, dir_b)

    required_keys = [
        "master_a", "master_b", "total_glyphs",
        "compatible_count", "incompatible_count",
        "only_in_a_count", "only_in_b_count", "glyphs",
    ]
    for key in required_keys:
        assert key in report, "missing required key: %s" % key

    assert isinstance(report["glyphs"], list)
    for g in report["glyphs"]:
        assert "name" in g
        assert "status" in g


# ---------------------------------------------------------------------------
# Test 8: Empty master → exit code non-zero
# ---------------------------------------------------------------------------

def test_empty_master():
    """Empty master should cause a SystemExit with non-zero code."""
    spec_empty = []
    spec_ok = [
        ("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
    ]
    font_empty = _make_test_font(spec_empty)
    font_ok = _make_test_font(spec_ok)

    dir_empty = _save_to_temp(font_empty)
    dir_ok = _save_to_temp(font_ok)

    with pytest.raises(SystemExit) as exc_info:
        _mod._detect(dir_empty, dir_ok)

    assert exc_info.value.code != 0
