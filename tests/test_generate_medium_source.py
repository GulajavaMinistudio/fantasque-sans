#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for ``Scripts/generate-medium-source.py`` (Medium Font Weight).

Covers:
    * CLI argument contract (zero / one / three arguments -> non-zero exit)
    * Input == output path guard (CON-06)
    * Metadata mapping for upright and italic inputs (Spec v1.2 section 4.2)
    * ``changeWeight(34, "LCG", 0, 0, "retain")`` invocation (CON-01, GUD-01)
    * ``removeOverlap`` / ``simplify`` invocation and runtime order (CON-03)
    * Advance-width enforcement to 1060 on every glyph (CON-02)
    * ``save`` target is the output path, never the input path (CON-06)

The CI host runner has no ``fontforge`` module, so a fake module is injected
into ``sys.modules`` before the script module is loaded (Plan TASK-002 /
ASSUMPTION-003). The script file name contains a hyphen and is therefore
loaded explicitly by path via ``importlib.util`` instead of a plain import.
"""

import importlib.util
import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(REPO_ROOT, "Scripts", "generate-medium-source.py")


def _load_script():
    """Load ``Scripts/generate-medium-source.py`` as a fresh module instance."""
    spec = importlib.util.spec_from_file_location(
        "generate_medium_source", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Inject a placeholder module so the script can be loaded for the CLI tests
# that never touch ``fontforge`` (the real module is absent on the CI runner).
_placeholder = type("placeholder", (), {})()
sys.modules.setdefault("fontforge", _placeholder)

# Loaded once for the argument-count tests that never touch ``fontforge``.
generate_medium_source = _load_script()


class FakeGlyph:
    """Minimal stand-in for a ``fontforge.glyph``."""

    def __init__(self, width=1000):
        self.width = width
        self.remove_overlap_calls = 0
        self.intersect_calls = 0
        self.round_calls = 0

    def removeOverlap(self):
        self.remove_overlap_calls += 1

    def intersect(self):
        self.intersect_calls += 1

    def round(self):
        self.round_calls += 1


class _FakeSelection:
    """``font.selection`` is an attribute object in real FontForge."""

    def __init__(self, font):
        self._font = font

    def all(self):
        self._font._selection_called = True


class FakeFont:
    """Minimal stand-in for a ``fontforge.font`` recording all mutations."""

    def __init__(self):
        self.os2_weight = None
        self.familyname = None
        self.fontname = None
        self.fullname = None
        self.sfnt_names = []
        self.saved_paths = []
        self.closed = False
        # A stable glyph list: the script must mutate these exact instances.
        self._glyphs = [FakeGlyph() for _ in range(3)]
        self.selection = _FakeSelection(self)
        self._selection_called = False
        self._change_weight_calls = []
        self._remove_overlap_calls = 0
        self._simplify_calls = 0
        # Chronological log of geometry operations for order assertions.
        self._operation_log = []

    def changeWeight(self, *args):
        self._change_weight_calls.append(args)
        self._operation_log.append(("changeWeight", args))

    def removeOverlap(self):
        self._remove_overlap_calls += 1
        self._operation_log.append(("removeOverlap",))

    def simplify(self):
        self._simplify_calls += 1
        self._operation_log.append(("simplify",))

    def glyphs(self):
        return self._glyphs

    def appendSFNTName(self, language, name_id, value):
        self.sfnt_names.append((language, name_id, value))

    def save(self, path):
        self.saved_paths.append(path)

    def close(self):
        self.closed = True


class FakeFontForgeModule:
    """Fake ``fontforge`` module injected into ``sys.modules``."""

    def __init__(self):
        self.fonts = []
        self.last_opened = []

    def open(self, path):
        self.last_opened.append(path)
        font = FakeFont()
        self.fonts.append(font)
        return font


@pytest.fixture
def fake_fontforge(monkeypatch):
    """Inject the fake module and load a fresh script instance against it."""
    fake = FakeFontForgeModule()
    monkeypatch.setitem(sys.modules, "fontforge", fake)
    script = _load_script()
    yield fake, script


def _run_main(argv, script_module=generate_medium_source):
    return script_module.main(["prog"] + argv)


class TestCliArguments:
    """REQ-02: exactly two positional arguments are required."""

    @pytest.mark.parametrize("argv", [[], ["input.sfdir"]])
    def test_wrong_argument_count_exits_nonzero(self, capsys, argv):
        assert _run_main(argv) == 1
        assert "Usage:" in capsys.readouterr().err

    def test_three_arguments_rejected_before_any_font_work(self, fake_fontforge):
        fake, script = fake_fontforge
        assert _run_main(["in.sfdir", "out.sfdir", "extra.sfdir"], script) == 1
        assert fake.last_opened == []

    def test_input_equals_output_rejected(self, capsys):
        assert _run_main(["same.sfdir", "same.sfdir"]) == 1
        assert "must differ" in capsys.readouterr().err


class TestUprightGeneration:
    """CON-04 + Spec section 4.2 metadata for the Medium upright variant."""

    def test_metadata_and_names_for_upright_input(self, fake_fontforge):
        fake, script = fake_fontforge
        assert (
            _run_main(
                [
                    "Sources/FantasqueSansMono-Regular.sfdir",
                    "Sources/FantasqueSansMono-Medium.sfdir",
                ],
                script,
            )
            == 0
        )

        font = fake.fonts[0]
        assert font.os2_weight == 500
        assert font.familyname == "Fantasque Sans Mono"
        assert font.fontname == "FantasqueSansMono-Medium"
        assert font.fullname == "Fantasque Sans Mono Medium"
        assert ("English (US)", "Family", "Fantasque Sans Mono") in font.sfnt_names
        assert ("English (US)", "SubFamily", "Medium") in font.sfnt_names
        assert (
            "English (US)",
            "Fullname",
            "Fantasque Sans Mono Medium",
        ) in font.sfnt_names
        assert (
            "English (US)",
            "PostScriptName",
            "FantasqueSansMono-Medium",
        ) in font.sfnt_names


class TestItalicDetection:
    """REQ-03: italic input is detected by basename prefix."""

    def test_metadata_and_names_for_italic_input(self, fake_fontforge):
        fake, script = fake_fontforge
        assert (
            _run_main(
                [
                    "Sources/FantasqueSansMono-Italic.sfdir",
                    "Sources/FantasqueSansMono-MediumItalic.sfdir",
                ],
                script,
            )
            == 0
        )

        font = fake.fonts[0]
        assert font.os2_weight == 500
        assert font.fontname == "FantasqueSansMono-MediumItalic"
        assert font.fullname == "Fantasque Sans Mono Medium Italic"
        assert ("English (US)", "SubFamily", "Medium Italic") in font.sfnt_names
        assert (
            "English (US)",
            "PostScriptName",
            "FantasqueSansMono-MediumItalic",
        ) in font.sfnt_names

    def test_italic_detection_uses_normpath_basename(self, fake_fontforge):
        fake, script = fake_fontforge
        assert (
            _run_main(
                [
                    "Sources/FantasqueSansMono-Italic.sfdir/",
                    "out/MediumItalic.sfdir",
                ],
                script,
            )
            == 0
        )

        font = fake.fonts[0]
        assert font.fontname == "FantasqueSansMono-MediumItalic"


class TestGeometryPipeline:
    """CON-01, CON-02, CON-03, GUD-01 operation sequence."""

    def test_embolden_and_cleanup_calls(self, fake_fontforge):
        fake, script = fake_fontforge
        _run_main(["in.sfdir", "out.sfdir"], script)

        font = fake.fonts[0]
        assert font._change_weight_calls == [(34, "LCG", 0, 0, "retain")]
        assert font._selection_called is True
        assert font._remove_overlap_calls == 1
        assert font._simplify_calls == 1

    def test_geometry_operations_run_in_plan_order(self, fake_fontforge):
        """CON-03: embolden must precede font-level cleanup at runtime."""
        fake, script = fake_fontforge
        _run_main(["in.sfdir", "out.sfdir"], script)

        font = fake.fonts[0]
        ops = [op for op, *_ in font._operation_log]
        assert ops == ["changeWeight", "removeOverlap", "simplify"]

    def test_every_glyph_width_set_to_1060(self, fake_fontforge):
        fake, script = fake_fontforge
        _run_main(["in.sfdir", "out.sfdir"], script)

        font = fake.fonts[0]
        widths = [glyph.width for glyph in font.glyphs()]
        assert widths == [1060, 1060, 1060]


class TestSaveTarget:
    """CON-06: never write to the input path."""

    def test_save_called_only_with_output_path(self, fake_fontforge):
        fake, script = fake_fontforge
        _run_main(["in.sfdir", "out.sfdir"], script)

        font = fake.fonts[0]
        assert font.saved_paths == ["out.sfdir"]
        assert "in.sfdir" not in font.saved_paths
        assert font.closed is True

    def test_open_called_with_input_path(self, fake_fontforge):
        fake, script = fake_fontforge
        _run_main(["in.sfdir", "out.sfdir"], script)
        assert fake.last_opened == ["in.sfdir"]
