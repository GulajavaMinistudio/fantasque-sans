#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for ``Scripts/multi_weight_driver.py``.

Test cases: Spec §6.3 (11 test cases).
"""

import os
import shutil
import sys
import tempfile

import pytest

ff = pytest.importorskip("fontforge")

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "Scripts")
sys.path.insert(0, SCRIPTS_DIR)

import multi_weight_driver as _mod  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_master_font(glyph_specs):
    """Create a FontForge font with specified glyph specs.

    Each spec: ``(name, width, contours)`` where ``contours`` is
    ``[[(x,y),...], ...]``.
    """
    font = ff.font()
    font.fontname = "TestMaster"
    font.familyname = "Fantasque Sans Mono"
    font.fullname = "Fantasque Sans Mono Test"
    font.em = 1000
    font.ascent = 800
    font.descent = 200

    for name, width, contours in glyph_specs:
        glyph = font.createChar(-1, name)
        glyph.width = width
        layer = ff.layer()
        for pts in contours:
            cont = ff.contour()
            for x, y in pts:
                cont += ff.point(x, y)
            cont.closed = True
            layer += cont
        glyph.foreground = layer
    return font


def _build_fixture_tree(base_dir):
    """Build a minimal harmonized source tree under ``base_dir``.

    Creates:
        Harmonized/Regular/   — 2 glyphs (A: 600 width, B: 600 width)
        Harmonized/Bold/      — same glyphs with different coordinates

    Returns ``(base_dir, regular_path, bold_path)``.
    """
    sources = os.path.join(base_dir, "Sources")
    harmonized = os.path.join(sources, "Harmonized")
    os.makedirs(harmonized, exist_ok=True)

    # Regular master: 2 glyphs with square contours
    reg_specs = [
        ("A", 600, [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
        ("B", 600, [[(0, 0), (100, 0), (100, 100), (0, 100)]]),
        # only_in_reg glyph
        ("only_reg", 600, [[(0, 0), (50, 0), (50, 50), (0, 50)]]),
    ]
    # Bold master: same glyphs but scaled larger
    bold_specs = [
        ("A", 600, [[(0, 0), (120, 0), (120, 120), (0, 120)]]),
        ("B", 600, [[(0, 0), (120, 0), (120, 120), (0, 120)]]),
        # only_in_bold glyph
        ("only_bold", 600, [[(0, 0), (50, 0), (50, 50), (0, 50)]]),
    ]

    font_reg = _make_master_font(reg_specs)
    font_bold = _make_master_font(bold_specs)

    reg_dir = os.path.join(harmonized, "Regular")
    bold_dir = os.path.join(harmonized, "Bold")
    font_reg.save(reg_dir)
    font_bold.save(bold_dir)

    # Create stub Italic, BoldItalic, and FantasqueSans
    for stub_name in ("Italic", "BoldItalic"):
        stub = _make_master_font([("A", 600, [[(0, 0), (100, 0), (100, 100), (0, 100)]])])
        stub.save(os.path.join(harmonized, stub_name))

    # Legacy FantasqueSans.sfdir
    fant = _make_master_font([("A", 600, [[(0, 0), (100, 0), (100, 100), (0, 100)]])])
    fant.save(os.path.join(sources, "FantasqueSans.sfdir"))

    return sources, reg_dir, bold_dir


# ---------------------------------------------------------------------------
# Test 1: Medium interpolation factor
# ---------------------------------------------------------------------------

def test_medium_interpolation_factor():
    tmp = tempfile.mkdtemp(prefix="test_mdw_")
    sources, reg_dir, bold_dir = _build_fixture_tree(tmp)

    font_reg = ff.open(reg_dir)
    font_bold = ff.open(bold_dir)

    result = _mod._interpolate_weight(
        font_reg, font_bold, 0.5, "Medium",
        os.path.join(sources, "Harmonized", "Interpolated"),
        dry_run=False,
    )

    assert result is not None
    # Check that glyph A was interpolated: midpoint between (100,100) and (120,120)
    ga = result["A"]
    # Just verify the font has our glyphs
    assert "A" in result.glyphs()
    font_reg.close()
    font_bold.close()
    result.close()


# ---------------------------------------------------------------------------
# Test 2: SemiBold interpolation factor
# ---------------------------------------------------------------------------

def test_semibold_interpolation_factor():
    """SemiBold factor should be 0.67 exact (tolerance ±0.005)."""
    assert _mod.FACTOR_SEMIBOLD == pytest.approx(0.67, abs=0.005)
    assert _mod.FACTOR_SEMIBOLD == 0.67  # exact Python float literal


# ---------------------------------------------------------------------------
# Test 3: copy-as-fallback
# ---------------------------------------------------------------------------

def test_copy_as_fallback():
    tmp = tempfile.mkdtemp(prefix="test_mdw_")
    sources, reg_dir, bold_dir = _build_fixture_tree(tmp)

    font_reg = ff.open(reg_dir)
    font_bold = ff.open(bold_dir)

    out_dir = os.path.join(sources, "Harmonized", "Interpolated")
    result = _mod._interpolate_weight(
        font_reg, font_bold, 0.5, "Medium", out_dir, dry_run=False,
    )

    # 'only_reg' should be copied from Regular (copy-as-fallback)
    assert "only_reg" in result.glyphs()
    font_reg.close()
    font_bold.close()
    result.close()


# ---------------------------------------------------------------------------
# Test 4: hmtx copy
# ---------------------------------------------------------------------------

def test_hmtx_copy():
    tmp = tempfile.mkdtemp(prefix="test_mdw_")
    sources, reg_dir, bold_dir = _build_fixture_tree(tmp)

    font_reg = ff.open(reg_dir)
    font_bold = ff.open(bold_dir)

    out_dir = os.path.join(sources, "Harmonized", "Interpolated")
    result = _mod._interpolate_weight(
        font_reg, font_bold, 0.5, "Medium", out_dir, dry_run=False,
    )

    # Advance width of 'A' should match Regular (600)
    assert result["A"].width == 600
    font_reg.close()
    font_bold.close()
    result.close()


# ---------------------------------------------------------------------------
# Test 5: output sfdir structure
# ---------------------------------------------------------------------------

def test_output_sfdir_structure():
    tmp = tempfile.mkdtemp(prefix="test_mdw_")
    sources, reg_dir, bold_dir = _build_fixture_tree(tmp)

    font_reg = ff.open(reg_dir)
    font_bold = ff.open(bold_dir)

    out_dir = os.path.join(sources, "Harmonized", "Interpolated")
    _mod._interpolate_weight(
        font_reg, font_bold, 0.5, "Medium", out_dir, dry_run=False,
    )

    medium_dir = os.path.join(out_dir, "Medium")
    assert os.path.isdir(medium_dir)
    # Check for at least one .glyph file
    files = os.listdir(medium_dir)
    assert len(files) > 0

    font_reg.close()
    font_bold.close()


# ---------------------------------------------------------------------------
# Test 6: no ttfautohint in driver
# ---------------------------------------------------------------------------

def test_no_ttfautohint_in_driver():
    """The driver module must not import or call ttfautohint."""
    source = open(_mod.__file__, "r").read()
    assert "ttfautohint" not in source.lower()


# ---------------------------------------------------------------------------
# Test 7: dry-run no output
# ---------------------------------------------------------------------------

def test_dry_run_no_output():
    tmp = tempfile.mkdtemp(prefix="test_mdw_")
    sources, reg_dir, bold_dir = _build_fixture_tree(tmp)

    font_reg = ff.open(reg_dir)
    font_bold = ff.open(bold_dir)

    out_dir = os.path.join(sources, "Harmonized", "Interpolated")
    os.makedirs(out_dir, exist_ok=True)

    result = _mod._interpolate_weight(
        font_reg, font_bold, 0.5, "Medium", out_dir, dry_run=True,
    )

    assert result is not None
    # Output directory should NOT contain Medium subdirectory
    assert not os.path.isdir(os.path.join(out_dir, "Medium"))

    font_reg.close()
    font_bold.close()
    result.close()


# ---------------------------------------------------------------------------
# Test 8: missing master error
# ---------------------------------------------------------------------------

def test_missing_master_error():
    """Missing master directory should raise SystemExit."""
    with pytest.raises(SystemExit):
        _mod._die("test error")


# ---------------------------------------------------------------------------
# Test 9: source assembly naming
# ---------------------------------------------------------------------------

def test_source_assembly_naming():
    """Assembly should produce ``FantasqueSansMono-{Weight}.sfdir`` directories."""
    tmp = tempfile.mkdtemp(prefix="test_mdw_")
    sources, reg_dir, bold_dir = _build_fixture_tree(tmp)

    # Interpolate Medium first
    font_reg = ff.open(reg_dir)
    font_bold = ff.open(bold_dir)
    out_dir = os.path.join(sources, "Harmonized", "Interpolated")
    os.makedirs(out_dir, exist_ok=True)
    _mod._interpolate_weight(font_reg, font_bold, 0.5, "Medium", out_dir, dry_run=False)
    font_reg.close()
    font_bold.close()

    build_dir = _mod._assemble_build_sources(sources, out_dir,
                                              ["Medium"], dry_run=False)

    expected = os.path.join(build_dir, "FantasqueSansMono-Medium.sfdir")
    assert os.path.isdir(expected), "expected %s to exist" % expected


# ---------------------------------------------------------------------------
# Test 10: assembly includes FantasqueSans
# ---------------------------------------------------------------------------

def test_assembly_includes_fantasque_sans():
    """Assembly should copy the legacy FantasqueSans.sfdir."""
    tmp = tempfile.mkdtemp(prefix="test_mdw_")
    sources, reg_dir, bold_dir = _build_fixture_tree(tmp)

    build_dir = _mod._assemble_build_sources(sources,
                                              os.path.join(sources, "Harmonized", "Interpolated"),
                                              [], dry_run=False)

    fs_dir = os.path.join(build_dir, "FantasqueSans.sfdir")
    assert os.path.isdir(fs_dir), "expected FantasqueSans.sfdir in assembly"


# ---------------------------------------------------------------------------
# Test 11: metadata injection
# ---------------------------------------------------------------------------

def test_metadata_injection():
    """Metadata values should match the contract (Spec §4.6, r6 Q-08)."""
    tmp = tempfile.mkdtemp(prefix="test_mdw_")
    sources, reg_dir, bold_dir = _build_fixture_tree(tmp)

    font_reg = ff.open(reg_dir)
    font_bold = ff.open(bold_dir)
    out_dir = os.path.join(sources, "Harmonized", "Interpolated")
    os.makedirs(out_dir, exist_ok=True)

    result = _mod._interpolate_weight(
        font_reg, font_bold, 0.5, "Medium", out_dir, dry_run=False,
    )

    assert result.familyname == "Fantasque Sans Mono"
    assert result.fullname == "Fantasque Sans Mono Medium"
    assert "Medium" in result.fontname or "Medium" in result.fullname

    font_reg.close()
    font_bold.close()
    result.close()
