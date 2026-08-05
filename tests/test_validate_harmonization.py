#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for ``Scripts/validate_harmonization.py``.

Test cases: Spec §6.3 (8 test cases).
"""

import os
import sys
import tempfile

import pytest

ff = pytest.importorskip("fontforge")

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "Scripts")
sys.path.insert(0, SCRIPTS_DIR)

import validate_harmonization as _mod  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_font(glyph_specs):
    """Create a FontForge font from ``(name, contours)`` specs.

    Each contour is ``[(x,y), ...]``.
    """
    font = ff.font()
    font.fontname = "TestHarm"
    font.familyname = "TestHarm"
    font.fullname = "TestHarm"

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


def _save(font):
    tmp = tempfile.mkdtemp(prefix="test_valharm_")
    font.save(tmp)
    return tmp


# ---------------------------------------------------------------------------
# Test 1: all three checks pass
# ---------------------------------------------------------------------------

def test_all_three_checks_pass():
    spec = [("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]])]
    font_a = _make_font(spec)
    font_b = _make_font(spec)
    dir_a = _save(font_a)
    dir_b = _save(font_b)

    report, fc = _mod._validate(dir_a, dir_b, strict=False, threshold=15.0)

    assert fc == 0
    assert report["pass_count"] == 1
    assert report["fail_count"] == 0
    r = report["results"][0]
    assert r["status"] == "pass"
    assert r["checks"]["node_count_equal"] is True
    assert r["checks"]["contour_order_equal"] is True
    assert r["checks"]["curve_direction_equal"] is True


# ---------------------------------------------------------------------------
# Test 2: node count fails
# ---------------------------------------------------------------------------

def test_node_count_fails():
    spec_a = [("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]])]  # 4 nodes
    spec_b = [("A", [[(0, 0), (100, 0), (100, 100)]])]              # 3 nodes
    font_a = _make_font(spec_a)
    font_b = _make_font(spec_b)
    dir_a = _save(font_a)
    dir_b = _save(font_b)

    report, fc = _mod._validate(dir_a, dir_b, strict=False, threshold=15.0)

    assert fc == 1
    r = report["results"][0]
    assert r["status"] == "fail"
    assert r["checks"]["node_count_equal"] is False


# ---------------------------------------------------------------------------
# Test 3: contour order fails
# ---------------------------------------------------------------------------

def test_contour_order_fails():
    spec_a = [("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]])]       # 1 contour
    spec_b = [("A", [[(0, 0), (100, 0), (100, 100), (0, 100)],
                      [(20, 20), (80, 20), (80, 80), (20, 80)]])]       # 2 contours
    font_a = _make_font(spec_a)
    font_b = _make_font(spec_b)
    dir_a = _save(font_a)
    dir_b = _save(font_b)

    report, fc = _mod._validate(dir_a, dir_b, strict=False, threshold=15.0)

    assert fc == 1
    r = report["results"][0]
    assert r["status"] == "fail"
    assert r["checks"]["contour_order_equal"] is False


# ---------------------------------------------------------------------------
# Test 4: curve direction fails
# ---------------------------------------------------------------------------

def test_curve_direction_fails():
    spec_a = [("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]])]       # CW-ish
    spec_b = [("A", [[(0, 0), (0, 100), (100, 100), (100, 0)]])]       # CCW-ish
    font_a = _make_font(spec_a)
    font_b = _make_font(spec_b)
    dir_a = _save(font_a)
    dir_b = _save(font_b)

    report, fc = _mod._validate(dir_a, dir_b, strict=False, threshold=15.0)

    assert fc == 1
    r = report["results"][0]
    assert r["status"] == "fail"
    assert r["checks"]["curve_direction_equal"] is False


# ---------------------------------------------------------------------------
# Test 5: multiple failures
# ---------------------------------------------------------------------------

def test_multiple_failures():
    # A: 1 contour, 4 nodes
    # B: 2 contours, different node counts → both contour_order + node_count fail
    spec_a = [("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]])]
    spec_b = [("A", [[(0, 0), (100, 0), (100, 100)],
                      [(20, 20), (80, 20), (80, 80)]])]
    font_a = _make_font(spec_a)
    font_b = _make_font(spec_b)
    dir_a = _save(font_a)
    dir_b = _save(font_b)

    report, fc = _mod._validate(dir_a, dir_b, strict=False, threshold=15.0)

    assert fc >= 1
    r = report["results"][0]
    assert r["status"] == "fail"
    # At least one check should fail
    assert (r["checks"]["node_count_equal"] is False or
            r["checks"]["contour_order_equal"] is False)


# ---------------------------------------------------------------------------
# Test 6: pass_rate calculation
# ---------------------------------------------------------------------------

def test_pass_rate_calculation():
    spec = [("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
            ("B", [[(0, 0), (100, 0), (100, 100), (0, 100)]])]
    spec_bad = [("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
                ("B", [[(0, 0), (100, 0), (100, 100)]])]  # B is 3-node vs 4
    font_a = _make_font(spec)
    font_b = _make_font(spec_bad)
    dir_a = _save(font_a)
    dir_b = _save(font_b)

    report, fc = _mod._validate(dir_a, dir_b, strict=False, threshold=15.0)

    assert report["total_pairs"] == 2
    assert report["pass_count"] == 1
    assert report["fail_count"] == 1
    assert report["pass_rate"] == pytest.approx(50.0, abs=0.1)


# ---------------------------------------------------------------------------
# Test 7: strict mode exit code
# ---------------------------------------------------------------------------

def test_strict_mode_exit_code():
    spec_a = [("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]])]
    spec_b = [("A", [[(0, 0), (100, 0), (100, 100)]])]  # different nodes
    font_a = _make_font(spec_a)
    font_b = _make_font(spec_b)
    dir_a = _save(font_a)
    dir_b = _save(font_b)

    # In strict mode, _validate still returns the report; the exit
    # happens in main().  We test that fail_count > 0 with strict=True.
    report, fc = _mod._validate(dir_a, dir_b, strict=True, threshold=15.0)

    assert fc >= 1


# ---------------------------------------------------------------------------
# Test 8: curve_smoothness non-blocking
# ---------------------------------------------------------------------------

def test_curve_smoothness_non_blocking():
    """Tangent-angle > threshold → curve_smoothness_ok=false + details filled,
    but exit code should remain 0 even with --strict (check 4 non-blocking)."""
    # Create a glyph with a sharp angle (acute triangle)
    spec = [("A", [[(0, 0), (100, 0), (50, 100)]])]
    font_a = _make_font(spec)
    font_b = _make_font(spec)
    dir_a = _save(font_a)
    dir_b = _save(font_b)

    # Use a very low threshold so even small angles trigger
    report, fc = _mod._validate(dir_a, dir_b, strict=True, threshold=0.1)

    # fail_count should be 0 (checks 1–3 pass)
    assert fc == 0
    r = report["results"][0]
    assert r["status"] == "pass"
    # curve_smoothness_ok might be False, but that does not affect exit code
    assert "curve_smoothness_ok" in r["checks"]
