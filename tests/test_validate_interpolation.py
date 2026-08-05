#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for ``Scripts/validate_interpolation.py``.

Test cases: Spec §6.3 (6 test cases).
"""

import os
import sys
import tempfile

import pytest

ff = pytest.importorskip("fontforge")

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "Scripts")
sys.path.insert(0, SCRIPTS_DIR)

import validate_interpolation as _mod  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_font(glyph_specs):
    """Create a FontForge font from glyph specs.

    Each spec: ``(name, contours)`` where ``contours`` is ``[[(x,y),...], ...]``.
    """
    font = ff.font()
    font.fontname = "TestInterp"
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


def _save(font):
    tmp = tempfile.mkdtemp(prefix="test_valinterp_")
    font.save(tmp)
    return tmp


def _build_masters_tree(base_dir):
    """Build a minimal masters tree under ``base_dir``.

    Creates:
        masters/Regular/  — 4-node square glyph "A"
        masters/Bold/     — same glyph
        masters/interp/   — identical glyph for testing

    Returns ``(base_dir, masters_dir, interp_dir)``.
    """
    spec = [("A", [[(0, 0), (100, 0), (100, 100), (0, 100)]])]
    font_reg = _make_font(spec)
    font_bold = _make_font(spec)
    font_interp = _make_font(spec)

    masters_dir = os.path.join(base_dir, "masters")
    reg_dir = os.path.join(masters_dir, "Regular")
    bold_dir = os.path.join(masters_dir, "Bold")
    interp_dir = os.path.join(base_dir, "interp")

    os.makedirs(reg_dir, exist_ok=True)
    os.makedirs(bold_dir, exist_ok=True)
    font_reg.save(reg_dir)
    font_bold.save(bold_dir)
    font_interp.save(interp_dir)

    return base_dir, masters_dir, interp_dir


# ---------------------------------------------------------------------------
# Test 1: pass status
# ---------------------------------------------------------------------------

def test_pass_status():
    """Glyph without artifact should be classified as 'pass'."""
    base = tempfile.mkdtemp(prefix="test_vi_")
    _, masters_dir, interp_dir = _build_masters_tree(base)

    # The fixture square has 90° corners, which exceeds the default 15.0°
    # threshold and would be classified as a minor warning — not a fail.
    # Use a threshold above 90° so the clean glyph is classified 'pass'.
    report = _mod._validate(interp_dir, masters_dir, 100.0, None, False)

    assert report["fail_count"] == 0
    assert report["warning_count"] == 0
    assert report["pass_count"] >= 1


# ---------------------------------------------------------------------------
# Test 2: warning status
# ---------------------------------------------------------------------------

def test_warning_status():
    """Minor artifact (tangent-angle > threshold) should be 'warning'."""
    base = tempfile.mkdtemp(prefix="test_vi_")
    _, masters_dir, interp_dir = _build_masters_tree(base)

    # Use a very low threshold to trigger warnings on any angle
    report = _mod._validate(interp_dir, masters_dir, 0.01, None, False)

    assert report["warning_count"] >= 1
    assert report["fail_count"] == 0


# ---------------------------------------------------------------------------
# Test 3: fail status
# ---------------------------------------------------------------------------

def test_fail_status():
    """Severe distortion (self-intersection) should be 'fail'."""
    base = tempfile.mkdtemp(prefix="test_vi_")
    _, masters_dir, interp_dir = _build_masters_tree(base)

    # Add a self-intersecting glyph to the interpolated font
    font_interp = ff.open(interp_dir)
    g = font_interp["A"]
    # Create a self-intersecting contour (bowtie shape)
    bowtie = ff.contour()
    bowtie += ff.point(0, 0)
    bowtie += ff.point(100, 100)
    bowtie += ff.point(100, 0)
    bowtie += ff.point(0, 100)
    bowtie.closed = True
    layer = ff.layer()
    layer += bowtie
    g.foreground = layer
    font_interp.save(interp_dir)

    report = _mod._validate(interp_dir, masters_dir, 15.0, None, False)

    assert report["fail_count"] >= 1
    for g in report["glyphs"]:
        if g["name"] == "A":
            assert g["status"] == "fail"


# ---------------------------------------------------------------------------
# Test 4: overlay PNG generated
# ---------------------------------------------------------------------------

def test_overlay_png_generated():
    """--overlay-dir should produce PNG for warning/fail glyphs."""
    base = tempfile.mkdtemp(prefix="test_vi_")
    _, masters_dir, interp_dir = _build_masters_tree(base)
    overlay_dir = os.path.join(base, "overlays")

    report = _mod._validate(interp_dir, masters_dir, 0.01, overlay_dir, False)

    assert report["total_glyphs"] > 0
    assert report["warning_count"] >= 1
    png_files = [f for f in os.listdir(overlay_dir) if f.endswith(".png")]
    assert len(png_files) >= 1, "expected at least one PNG in overlay dir"


# ---------------------------------------------------------------------------
# Test 5: report JSON valid
# ---------------------------------------------------------------------------

def test_report_json_valid():
    """Output JSON should contain all required fields."""
    base = tempfile.mkdtemp(prefix="test_vi_")
    _, masters_dir, interp_dir = _build_masters_tree(base)

    report = _mod._validate(interp_dir, masters_dir, 15.0, None, False)

    required_keys = [
        "weight", "total_glyphs", "pass_count",
        "warning_count", "fail_count", "glyphs",
    ]
    for key in required_keys:
        assert key in report, "missing required key: %s" % key

    for g in report["glyphs"]:
        assert "name" in g
        assert "status" in g
        assert g["status"] in ("pass", "warning", "fail")

    # Spec §4.11: status enum must be consistent with aggregate counts
    total = report["pass_count"] + report["warning_count"] + report["fail_count"]
    assert total == report["total_glyphs"]


# ---------------------------------------------------------------------------
# Test 6: masters parent dir resolution
# ---------------------------------------------------------------------------

def test_masters_parent_dir_resolution():
    """--masters should accept a parent dir with Regular/ and Bold/ subdirs."""
    base = tempfile.mkdtemp(prefix="test_vi_")
    _, masters_dir, interp_dir = _build_masters_tree(base)

    # This should resolve successfully
    report = _mod._validate(interp_dir, masters_dir, 15.0, None, False)
    assert report is not None

    # Test with missing subdirectory
    bad_masters = os.path.join(base, "bad_masters")
    os.makedirs(os.path.join(bad_masters, "Regular"), exist_ok=True)
    # Missing Bold/ subdirectory
    with pytest.raises(SystemExit) as exc_info:
        _mod._validate(interp_dir, bad_masters, 15.0, None, False)
    assert exc_info.value.code != 0
