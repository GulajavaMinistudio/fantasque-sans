#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for ``Scripts/configure.py`` (Phase 1 wrapper).

Covers:
    * Schema validation (valid / invalid / empty / unknown-key / missing file)
    * Exact AC-004 error message text and exit code
    * Precedence 4-state matrix (defaults / config.json / form / form_override)
    * ``config_source`` aggregation (Spec §9.1 hierarchy)
    * Per-option log line format (AC-003 verbatim)
    * Stage 1 driver argument string (space-separated, ``UseHinted`` excluded)
    * Manifest conformance against Spec §4.6 schema
    * CLI smoke (argparse, ``--form-*`` boolean parsing, ``--help``)
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

# Make ``Scripts/`` importable as a package-less module path.
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "Scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import configure  # noqa: E402  (intentional sys.path mutation above)


FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
SCHEMA_PATH = REPO_ROOT / "config.schema.json"
MANIFEST_SCHEMA_PATH = FIXTURES_DIR / "manifest_schema.json"


# ---------------------------------------------------------------------------
# Schema fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def config_schema():
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def manifest_schema():
    with MANIFEST_SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def empty_form():
    """No form inputs — represents the ``workflow_dispatch`` default state."""
    return {
        "large_line_height": None,
        "no_loop_k": None,
        "no_calt": None,
        "use_hinted": None,
        "enable_multi_weight": None,
    }


# ===========================================================================
# Schema file sanity (Spec §10 criterion 1)
# ===========================================================================

class TestSchemaFile:
    """``config.schema.json`` MUST validate as Draft-07 (Spec §10.1)."""

    def test_schema_validates_as_draft_07(self, config_schema):
        jsonschema.Draft7Validator.check_schema(config_schema)

    def test_schema_has_five_boolean_properties(self, config_schema):
        props = config_schema["properties"]
        assert set(props.keys()) == {
            "LargeLineHeight",
            "NoLoopK",
            "NoCalt",
            "UseHinted",
            "EnableMultiWeight",
        }
        for name, spec in props.items():
            assert spec["type"] == "boolean", f"{name} must be boolean"
            assert "default" in spec, f"{name} must declare a default"

    def test_schema_allows_additional_properties(self, config_schema):
        assert config_schema.get("additionalProperties") is True


# ===========================================================================
# load_config / load_schema
# ===========================================================================

class TestLoadConfig:
    def test_missing_file_yields_empty_object(self, tmp_path):
        result = configure.load_config(tmp_path / "no-such.json")
        assert result == {}

    def test_loads_valid_json(self, tmp_path):
        p = tmp_path / "cfg.json"
        p.write_text('{"NoLoopK": true}', encoding="utf-8")
        assert configure.load_config(p) == {"NoLoopK": True}


class TestLoadSchema:
    def test_loads_and_validates_draft_07(self):
        schema = configure.load_schema(SCHEMA_PATH)
        assert schema["type"] == "object"
        assert "properties" in schema


# ===========================================================================
# validate_config (TASK-003, AC-004, GUD-001)
# ===========================================================================

class TestValidateConfig:
    def test_valid_config_passes(self, config_schema):
        configure.validate_config(
            {"LargeLineHeight": False, "NoLoopK": True}, config_schema
        )

    def test_empty_config_passes(self, config_schema):
        configure.validate_config({}, config_schema)

    def test_invalid_type_raises_with_ac004_message(self, config_schema):
        # AC-004: ``Invalid config.json: 'NoCalt' must be a boolean, got string``
        with pytest.raises(configure.ConfigValidationError) as exc_info:
            configure.validate_config({"NoCalt": "yes"}, config_schema)
        assert str(exc_info.value) == (
            "Invalid config.json: 'NoCalt' must be a boolean, got string"
        )

    @pytest.mark.parametrize(
        "key,bad_value,expected_got",
        [
            ("LargeLineHeight", "yes", "string"),
            ("NoLoopK", 1, "integer"),
            ("NoCalt", [True], "array"),
            ("UseHinted", {"v": 1}, "object"),
        ],
    )
    def test_invalid_type_messages_are_consistent(
        self, config_schema, key, bad_value, expected_got
    ):
        with pytest.raises(configure.ConfigValidationError) as exc_info:
            configure.validate_config({key: bad_value}, config_schema)
        assert str(exc_info.value) == (
            f"Invalid config.json: '{key}' must be a boolean, got {expected_got}"
        )

    def test_unknown_key_warns_but_does_not_fail(
        self, config_schema, caplog
    ):
        with caplog.at_level(logging.WARNING, logger="configure"):
            configure.validate_config(
                {"NoLoopK": True, "Mystery": 42}, config_schema
            )
        assert any(
            "Mystery" in record.message for record in caplog.records
        ), "Unknown key should produce a WARNING-level log line"

    def test_unknown_key_keeps_validation_passing(self, config_schema):
        # GUD-001: must not raise.
        configure.validate_config({"NoLoopK": True, "Extra": "x"}, config_schema)


# ===========================================================================
# resolve_options (TASK-004, REQ-003)
# ===========================================================================

class TestResolveOptions:
    """4-state precedence matrix."""

    def test_all_defaults(self, empty_form):
        resolved, sources = configure.resolve_options({}, empty_form)
        assert resolved == {
            "LargeLineHeight": False,
            "NoLoopK": False,
            "NoCalt": False,
            "UseHinted": True,
            "EnableMultiWeight": False,
        }
        assert all(s == "defaults" for s in sources.values())

    def test_config_json_only(self, empty_form):
        cfg = {"NoLoopK": True, "UseHinted": False}
        resolved, sources = configure.resolve_options(cfg, empty_form)
        assert resolved["NoLoopK"] is True
        assert resolved["UseHinted"] is False
        assert sources["NoLoopK"] == "config.json"
        assert sources["UseHinted"] == "config.json"
        # Other two still default.
        assert sources["LargeLineHeight"] == "defaults"
        assert sources["NoCalt"] == "defaults"

    def test_form_only_no_config(self, empty_form):
        # No config, no config.json file; form is set.
        cfg = {}
        form = {
            "large_line_height": None,
            "no_loop_k": True,
            "no_calt": None,
            "use_hinted": None,
        }
        resolved, sources = configure.resolve_options(cfg, form)
        assert resolved["NoLoopK"] is True
        assert sources["NoLoopK"] == "form"

    def test_form_override_over_config(self, empty_form):
        # AC-003 case.
        cfg = {"LargeLineHeight": False}
        form = {
            "large_line_height": True,
            "no_loop_k": None,
            "no_calt": None,
            "use_hinted": None,
        }
        resolved, sources = configure.resolve_options(cfg, form)
        assert resolved["LargeLineHeight"] is True
        assert sources["LargeLineHeight"] == "form_override"

    def test_form_equals_default_falls_through_to_config(self, empty_form):
        # ``form=false`` matches the default; per Spec §9.1 example the
        # form branch is skipped and the config.json value (if any) wins.
        cfg = {"NoLoopK": True}
        form = {
            "large_line_height": None,
            "no_loop_k": False,  # matches default
            "no_calt": None,
            "use_hinted": None,
        }
        resolved, sources = configure.resolve_options(cfg, form)
        assert resolved["NoLoopK"] is True  # config.json wins
        assert sources["NoLoopK"] == "config.json"

    def test_use_hinted_default_is_true(self, empty_form):
        # Regression guard: UseHinted default is ``True`` (not False).
        resolved, _ = configure.resolve_options({}, empty_form)
        assert resolved["UseHinted"] is True

    def test_mixed_precedence_all_four_sources(
        self, empty_form
    ):
        # Realistic mix: one default, one config.json, one form, one override.
        cfg = {"NoLoopK": True, "LargeLineHeight": False}
        form = {
            "large_line_height": True,   # form_override
            "no_loop_k": None,           # config.json
            "no_calt": True,             # form (no config)
            "use_hinted": None,          # defaults
        }
        resolved, sources = configure.resolve_options(cfg, form)
        assert resolved == {
            "LargeLineHeight": True,
            "NoLoopK": True,
            "NoCalt": True,
            "UseHinted": True,
            "EnableMultiWeight": False,
        }
        assert sources == {
            "LargeLineHeight": "form_override",
            "NoLoopK": "config.json",
            "NoCalt": "form",
            "UseHinted": "defaults",
            "EnableMultiWeight": "defaults",
        }


# ===========================================================================
# compute_config_source (TASK-005, Spec §9.1)
# ===========================================================================

class TestComputeConfigSource:
    """Every Spec §9.1 rule case must be exercised."""

    def test_all_defaults(self):
        sources = {
            "LargeLineHeight": "defaults",
            "NoLoopK": "defaults",
            "NoCalt": "defaults",
            "UseHinted": "defaults",
        }
        assert configure.compute_config_source(sources, False) == "defaults"
        assert configure.compute_config_source(sources, True) == "defaults"

    def test_config_json_only_with_file(self):
        sources = {
            "LargeLineHeight": "config.json",
            "NoLoopK": "defaults",
            "NoCalt": "defaults",
            "UseHinted": "defaults",
        }
        assert configure.compute_config_source(sources, True) == "config.json"

    def test_config_json_present_but_empty_object(self):
        # File exists, but per-option sources are all defaults → "defaults".
        sources = {
            "LargeLineHeight": "defaults",
            "NoLoopK": "defaults",
            "NoCalt": "defaults",
            "UseHinted": "defaults",
        }
        assert configure.compute_config_source(sources, True) == "defaults"

    def test_form_only_without_file(self):
        sources = {
            "LargeLineHeight": "form",
            "NoLoopK": "defaults",
            "NoCalt": "defaults",
            "UseHinted": "defaults",
        }
        assert configure.compute_config_source(sources, False) == "form"

    def test_form_override_wins_over_anything(self):
        sources = {
            "LargeLineHeight": "form_override",
            "NoLoopK": "config.json",
            "NoCalt": "defaults",
            "UseHinted": "defaults",
        }
        assert (
            configure.compute_config_source(sources, True) == "form_override"
        )

    def test_form_mixed_with_config_json(self):
        # Spec §9.1 rule 2 requires NO "form" entries; here we have one
        # "form" entry so rule 3 fires → "form".
        sources = {
            "LargeLineHeight": "form",
            "NoLoopK": "config.json",
            "NoCalt": "defaults",
            "UseHinted": "defaults",
        }
        assert configure.compute_config_source(sources, True) == "form"


# ===========================================================================
# log_option_sources (AC-003 verbatim)
# ===========================================================================

class TestLogOptionSources:
    @pytest.mark.parametrize(
        "source,expected_substring",
        [
            ("defaults", "Using default value for large_line_height"),
            ("config.json", "Using config.json value for large_line_height"),
            ("form", "Using form value for large_line_height"),
            (
                "form_override",
                "Using form value (overrides config.json) for large_line_height",
            ),
        ],
    )
    def test_exact_log_format(
        self, caplog, source, expected_substring
    ):
        sources = {
            "LargeLineHeight": source,
            "NoLoopK": "defaults",
            "NoCalt": "defaults",
            "UseHinted": "defaults",
        }
        with caplog.at_level(logging.INFO, logger="configure"):
            configure.log_option_sources(sources)
        joined = "\n".join(record.getMessage() for record in caplog.records)
        assert expected_substring in joined

    def test_emits_one_line_per_option(self, caplog):
        sources = {
            "LargeLineHeight": "form",
            "NoLoopK": "config.json",
            "NoCalt": "defaults",
            "UseHinted": "form_override",
            "EnableMultiWeight": "defaults",
        }
        with caplog.at_level(logging.INFO, logger="configure"):
            configure.log_option_sources(sources)
        info_lines = [
            r.getMessage() for r in caplog.records if r.levelno == logging.INFO
        ]
        # One log line per option (5 total).
        assert len(info_lines) == 5


# ===========================================================================
# build_driver_arg_string (TASK-005)
# ===========================================================================

class TestBuildDriverArgString:
    def test_empty_string_when_all_defaults(self):
        resolved = {
            "LargeLineHeight": False,
            "NoLoopK": False,
            "NoCalt": False,
            "UseHinted": True,
        }
        assert configure.build_driver_arg_string(resolved) == ""

    def test_use_hinted_is_not_a_driver_flag(self):
        # Per Spec §4.4: UseHinted does NOT map to a driver argument.
        resolved = {
            "LargeLineHeight": False,
            "NoLoopK": False,
            "NoCalt": False,
            "UseHinted": False,
        }
        assert configure.build_driver_arg_string(resolved) == ""

    def test_single_flag(self):
        resolved = {
            "LargeLineHeight": True,
            "NoLoopK": False,
            "NoCalt": False,
            "UseHinted": True,
        }
        assert configure.build_driver_arg_string(resolved) == "--line-height"

    def test_multiple_flags_space_separated(self):
        resolved = {
            "LargeLineHeight": True,
            "NoLoopK": True,
            "NoCalt": False,
            "UseHinted": True,
        }
        out = configure.build_driver_arg_string(resolved)
        # Order is determined by OPTION_TO_DRIVER_FLAG insertion order.
        assert out == "--line-height --no-loop-k"


# ===========================================================================
# EnableMultiWeight (TASK-4.1, Spec §4.9 / plan v1.13 resolution D)
# ===========================================================================

class TestEnableMultiWeight:
    def test_default_is_false(self, empty_form):
        resolved, sources = configure.resolve_options({}, empty_form)
        assert resolved["EnableMultiWeight"] is False
        assert sources["EnableMultiWeight"] == "defaults"

    def test_form_true_resolves(self, empty_form):
        form = dict(empty_form)
        form["enable_multi_weight"] = True
        resolved, sources = configure.resolve_options({}, form)
        assert resolved["EnableMultiWeight"] is True
        assert sources["EnableMultiWeight"] == "form"

    def test_config_json_true_resolves(self, empty_form):
        resolved, sources = configure.resolve_options(
            {"EnableMultiWeight": True}, empty_form
        )
        assert resolved["EnableMultiWeight"] is True
        assert sources["EnableMultiWeight"] == "config.json"

    def test_flag_appears_in_driver_arg_string(self):
        resolved = {
            "LargeLineHeight": False,
            "NoLoopK": False,
            "NoCalt": False,
            "UseHinted": True,
            "EnableMultiWeight": True,
        }
        out = configure.build_driver_arg_string(resolved)
        assert "--multi-weight" in out

    def test_flag_absent_when_disabled(self):
        resolved = {
            "LargeLineHeight": False,
            "NoLoopK": False,
            "NoCalt": False,
            "UseHinted": True,
            "EnableMultiWeight": False,
        }
        assert configure.build_driver_arg_string(resolved) == ""

    def test_driver_flags_and_build_level_flag_combined(self):
        resolved = {
            "LargeLineHeight": True,
            "NoLoopK": False,
            "NoCalt": False,
            "UseHinted": True,
            "EnableMultiWeight": True,
        }
        out = configure.build_driver_arg_string(resolved)
        # Driver flags first (OPTION_TO_DRIVER_FLAG), build-level flag last.
        assert out == "--line-height --multi-weight"

    def test_schema_declares_boolean_property(self, config_schema):
        prop = config_schema["properties"]["EnableMultiWeight"]
        assert prop["type"] == "boolean"
        assert prop["default"] is False

    def test_manifest_records_resolved_option(
        self, tmp_path, manifest_schema
    ):
        resolved = {
            "LargeLineHeight": False,
            "NoLoopK": False,
            "NoCalt": False,
            "UseHinted": True,
            "EnableMultiWeight": True,
        }
        sources = {k: "defaults" for k in resolved}
        out = tmp_path / "manifest.json"
        configure.generate_manifest(resolved, sources, "defaults", out)
        with out.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["resolved_options"]["EnableMultiWeight"] is True
        # Manifest must still validate against the §4.6 schema.
        jsonschema.validate(data, manifest_schema)


# ===========================================================================
# generate_manifest (TASK-006, Spec §4.6)
# ===========================================================================

class TestGenerateManifest:
    @pytest.fixture
    def sample_manifest_kwargs(self):
        resolved = {
            "LargeLineHeight": False,
            "NoLoopK": True,
            "NoCalt": False,
            "UseHinted": True,
        }
        sources = {
            "LargeLineHeight": "defaults",
            "NoLoopK": "config.json",
            "NoCalt": "defaults",
            "UseHinted": "defaults",
        }
        return resolved, sources, "config.json"

    def test_writes_valid_json(self, tmp_path, sample_manifest_kwargs):
        resolved, sources, cs = sample_manifest_kwargs
        out = tmp_path / "manifest.json"
        configure.generate_manifest(resolved, sources, cs, out)
        with out.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_required_fields_present(
        self, tmp_path, sample_manifest_kwargs, manifest_schema
    ):
        resolved, sources, cs = sample_manifest_kwargs
        out = tmp_path / "manifest.json"
        configure.generate_manifest(resolved, sources, cs, out)
        with out.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for required_key in manifest_schema["required"]:
            assert required_key in data, (
                f"manifest missing required field: {required_key}"
            )

    def test_conforms_to_spec_4_6_schema(
        self, tmp_path, sample_manifest_kwargs, manifest_schema
    ):
        """The manifest written by configure.py MUST validate against
        Spec §4.6 (PLAN-001 mandatory acceptance gate for Phase 1)."""
        resolved, sources, cs = sample_manifest_kwargs
        out = tmp_path / "manifest.json"
        configure.generate_manifest(resolved, sources, cs, out)
        with out.open("r", encoding="utf-8") as f:
            data = json.load(f)
        jsonschema.Draft7Validator(manifest_schema).validate(data)

    def test_spdx_license_is_ofl_1_1(
        self, tmp_path, sample_manifest_kwargs
    ):
        resolved, sources, cs = sample_manifest_kwargs
        out = tmp_path / "manifest.json"
        configure.generate_manifest(resolved, sources, cs, out)
        with out.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["spdx_license"] == "OFL-1.1"

    def test_python_version_in_toolchain(
        self, tmp_path, sample_manifest_kwargs
    ):
        resolved, sources, cs = sample_manifest_kwargs
        out = tmp_path / "manifest.json"
        configure.generate_manifest(resolved, sources, cs, out)
        with out.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert "python" in data["toolchain_versions"]
        assert isinstance(data["toolchain_versions"]["python"], str)
        # Looks like X.Y.Z
        parts = data["toolchain_versions"]["python"].split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_source_commit_from_env(
        self, tmp_path, sample_manifest_kwargs, monkeypatch
    ):
        monkeypatch.setenv("GITHUB_SHA", "deadbeef1234")
        resolved, sources, cs = sample_manifest_kwargs
        out = tmp_path / "manifest.json"
        configure.generate_manifest(resolved, sources, cs, out)
        with out.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["source_commit"] == "deadbeef1234"

    def test_source_commit_fallback_when_no_env(
        self, tmp_path, sample_manifest_kwargs, monkeypatch
    ):
        monkeypatch.delenv("GITHUB_SHA", raising=False)
        resolved, sources, cs = sample_manifest_kwargs
        out = tmp_path / "manifest.json"
        configure.generate_manifest(resolved, sources, cs, out)
        with out.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["source_commit"] == "unknown"

    def test_build_timestamp_utc_iso8601(
        self, tmp_path, sample_manifest_kwargs
    ):
        resolved, sources, cs = sample_manifest_kwargs
        out = tmp_path / "manifest.json"
        configure.generate_manifest(resolved, sources, cs, out)
        with out.open("r", encoding="utf-8") as f:
            data = json.load(f)
        ts = data["build_timestamp"]
        # ``Z`` suffix for UTC.
        assert ts.endswith("Z"), f"expected UTC Z-suffix, got {ts!r}"
        # Validate as date-time per JSON Schema.
        jsonschema.Draft7Validator(
            {"type": "string", "format": "date-time"}
        ).validate(ts)

    def test_font_files_is_empty_array_in_phase1(
        self, tmp_path, sample_manifest_kwargs
    ):
        resolved, sources, cs = sample_manifest_kwargs
        out = tmp_path / "manifest.json"
        configure.generate_manifest(resolved, sources, cs, out)
        with out.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["font_files"] == []


# ===========================================================================
# argparse / boolean parsing
# ===========================================================================

class TestFormBoolParser:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("true", True), ("false", False),
            ("True", True), ("FALSE", False),
            ("1", True), ("0", False),
            ("yes", True), ("no", False),
            (True, True), (False, False),
        ],
    )
    def test_parse_bool_accepts_canonical_forms(self, raw, expected):
        assert configure._parse_bool(raw) is expected

    def test_parse_bool_rejects_garbage(self):
        with pytest.raises(SystemExit):
            configure.build_arg_parser().parse_args(
                ["--form-no-calt", "maybe"]
            )


class TestArgParser:
    def test_defaults_match_cli_surface(self):
        ns = configure.build_arg_parser().parse_args([])
        assert ns.config_file == Path("config.json")
        assert ns.schema_file == Path("config.schema.json")
        assert ns.form_large_line_height is None
        assert ns.form_no_loop_k is None
        assert ns.form_no_calt is None
        assert ns.form_use_hinted is None
        assert ns.output_args_file is None
        assert ns.generate_manifest is None

    def test_help_exits_zero(self):
        with pytest.raises(SystemExit) as exc_info:
            configure.build_arg_parser().parse_args(["--help"])
        assert exc_info.value.code == 0


# ===========================================================================
# End-to-end: main() entry point
# ===========================================================================

class TestMainEntryPoint:
    def test_main_returns_1_on_invalid_config(self, tmp_path, caplog):
        bad = tmp_path / "bad.json"
        bad.write_text('{"NoCalt": "yes"}', encoding="utf-8")
        rc = configure.main(
            [
                "--config-file", str(bad),
                "--schema-file", str(SCHEMA_PATH),
            ]
        )
        assert rc == 1
        joined = "\n".join(r.getMessage() for r in caplog.records)
        assert "Invalid config.json: 'NoCalt' must be a boolean, got string" in joined

    def test_main_writes_args_and_manifest(self, tmp_path, caplog):
        args_file = tmp_path / "args.txt"
        manifest_file = tmp_path / "manifest.json"
        rc = configure.main(
            [
                "--schema-file", str(SCHEMA_PATH),
                "--form-no-loop-k", "true",
                "--output-args-file", str(args_file),
                "--generate-manifest", str(manifest_file),
            ]
        )
        assert rc == 0
        assert args_file.read_text(encoding="utf-8") == "--no-loop-k"
        with manifest_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["resolved_options"]["NoLoopK"] is True
        assert data["config_source"] == "form"

    def test_main_emits_ac003_log_line(self, tmp_path, caplog):
        cfg = tmp_path / "cfg.json"
        cfg.write_text(
            '{"LargeLineHeight": false}', encoding="utf-8"
        )
        with caplog.at_level(logging.INFO, logger="configure"):
            rc = configure.main(
                [
                    "--config-file", str(cfg),
                    "--schema-file", str(SCHEMA_PATH),
                    "--form-large-line-height", "true",
                ]
            )
        assert rc == 0
        joined = "\n".join(r.getMessage() for r in caplog.records)
        assert (
            "Using form value (overrides config.json) for large_line_height"
            in joined
        )
