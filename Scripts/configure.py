#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fantasque Sans Mono Custom Build Configuration Wrapper.

Validates ``config.json`` against ``config.schema.json`` (JSON Schema
Draft-07), resolves the five boolean build options with strict precedence
(``workflow_dispatch`` form input > ``config.json`` > defaults), emits a
Stage 1 driver argument string, and (optionally) writes a build manifest
conforming to the contract in Technical Specification v1.5 section 4.6.

Runs on the GitHub Actions host runner (Python 3.14). Per ADR-0002 and
Spec section 1.2, this wrapper MUST NOT be executed inside the Docker
container — it lives on the host and feeds ``docker build --build-arg``.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft7Validator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Build defaults (Spec REQ-003, AC-001).
DEFAULTS = {
    "LargeLineHeight": False,
    "NoLoopK": False,
    "NoCalt": False,
    "UseHinted": True,
    "EnableMultiWeight": False,
}

# Maps CLI form flag key (snake_case, matches workflow_dispatch input) to
# config option name (PascalCase, matches config.json / manifest key).
FORM_KEY_TO_OPTION = {
    "large_line_height": "LargeLineHeight",
    "no_loop_k": "NoLoopK",
    "no_calt": "NoCalt",
    "use_hinted": "UseHinted",
    "enable_multi_weight": "EnableMultiWeight",
}

# Maps option name (PascalCase) to Stage 1 driver CLI flag.
# ``UseHinted`` is intentionally absent — it controls Stage 2 hinting
# (Spec section 4.4: "The UseHinted option does not map to a driver
# argument"). The wrapper writes the resolved value into the manifest
# instead so Stage 2 can read it via ``jq``.
OPTION_TO_DRIVER_FLAG = {
    "LargeLineHeight": "--line-height",
    "NoLoopK": "--no-loop-k",
    "NoCalt": "--no-calt",
}

# Build-level flags forwarded into the Stage 1 RUN chain (Spec §4.9,
# plan resolution D / v1.13). These are NOT driver flags: the Dockerfile
# RUN chain strips ``--multi-weight`` from ``$BUILD_ARGS`` before invoking
# ``custom_build_driver.py`` (which ``_die``s on unknown flags). Kept in a
# separate constant so ``OPTION_TO_DRIVER_FLAG`` remains the single source
# of truth for flags the legacy driver understands.
BUILD_LEVEL_FLAGS = {
    "EnableMultiWeight": "--multi-weight",
}

# Manifest top-level constants (Spec section 4.6).
MANIFEST_VERSION = "1.0"
WORKFLOW_VERSION = "1.3"
SPDX_LICENSE = "OFL-1.1"

# Python type name to JSON Schema primitive name (for the validation
# diagnostic mandated by AC-004: ``got string``, not ``got str``).
_PY_TYPE_TO_JSON_TYPE = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "list": "array",
    "dict": "object",
    "NoneType": "null",
}


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

log = logging.getLogger("configure")


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ConfigValidationError(Exception):
    """Raised when ``config.json`` fails schema validation (AC-004)."""


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def load_config(config_path):
    """Load ``config.json``. Missing file yields an empty object (Spec §4.4)."""
    if not config_path.is_file():
        log.info("No config.json at %s; treating as empty object.", config_path)
        return {}
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_schema(schema_path):
    """Load ``config.schema.json`` and ensure it is a valid Draft-07 schema."""
    with schema_path.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    Draft7Validator.check_schema(schema)
    return schema


# ---------------------------------------------------------------------------
# Validation (TASK-003)
# ---------------------------------------------------------------------------

def validate_config(config, schema):
    """Validate ``config`` against ``schema``; raise on failure.

    Unknown keys are warned but do not fail (GUD-001).
    """
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(config), key=lambda e: list(e.path))
    if errors:
        # AC-004 mandates an exact, human-readable diagnostic. Surface the
        # first error (deterministic order) in the spec-required form.
        err = errors[0]
        if err.validator == "type" and err.path:
            key = err.path[0]
            got_type = _PY_TYPE_TO_JSON_TYPE.get(
                type(config[key]).__name__, type(config[key]).__name__
            )
            raise ConfigValidationError(
                f"Invalid config.json: '{key}' must be a boolean, got {got_type}"
            )
        # Fallback: use jsonschema's own message (preserves all validator
        # kinds for future-proofing, even though the current schema only
        # declares type constraints).
        raise ConfigValidationError(
            f"Invalid config.json: {err.message}"
        )

    # GUD-001: unknown keys warn but never fail.
    allowed = set(schema.get("properties", {}).keys())
    for key in config.keys():
        if key not in allowed:
            log.warning("Unknown key in config.json: '%s' (ignored)", key)


# ---------------------------------------------------------------------------
# Resolution (TASK-004)
# ---------------------------------------------------------------------------

def resolve_options(config, form_inputs):
    """Resolve the four options with strict precedence.

    Per Spec REQ-003, hierarchy is:
        form input > config.json > defaults

    Per-option source taxonomy:
        "form_override"  — form input provided, differs from default, AND
                           config.json also declares the key (form wins)
        "form"           — form input provided, differs from default, but
                           config.json does NOT declare the key
        "config.json"    — form input not provided (or matches default) but
                           config.json declares the key
        "defaults"       — neither form nor config.json contributed; the
                           DEFAULTS value is used

    Returns ``(resolved, sources)`` — both dicts keyed by PascalCase option
    name. ``sources`` values are always one of the four strings above.
    """
    resolved = {}
    sources = {}

    for option_name, default_val in DEFAULTS.items():
        # Find the form key for this option.
        form_key = next(
            fk for fk, on in FORM_KEY_TO_OPTION.items() if on == option_name
        )
        form_val = form_inputs.get(form_key)
        config_val = config.get(option_name)

        if form_val is not None and form_val != default_val:
            if config_val is not None:
                sources[option_name] = "form_override"
            else:
                sources[option_name] = "form"
            resolved[option_name] = form_val
        elif config_val is not None:
            sources[option_name] = "config.json"
            resolved[option_name] = config_val
        else:
            sources[option_name] = "defaults"
            resolved[option_name] = default_val

    return resolved, sources


# ---------------------------------------------------------------------------
# config_source aggregator (TASK-005, Spec §9.1)
# ---------------------------------------------------------------------------

def compute_config_source(sources, has_config_file):
    """Reduce per-option sources to a single build-level ``config_source``.

    Hierarchy (Spec §9.1):
        1. If any per-option source is "form_override" → "form_override"
        2. elif ``has_config_file`` and at least one source is "config.json"
           and no source is "form" → "config.json"
        3. elif any source is "form" → "form"
        4. else → "defaults"
    """
    values = list(sources.values())

    if "form_override" in values:
        return "form_override"

    if has_config_file and "form" not in values and "config.json" in values:
        return "config.json"

    if "form" in values:
        return "form"

    return "defaults"


# ---------------------------------------------------------------------------
# Logging per option (TASK-004)
# ---------------------------------------------------------------------------

def log_option_sources(sources):
    """Emit one log line per option naming its source (Spec AC-003)."""
    for form_key, option_name in FORM_KEY_TO_OPTION.items():
        source = sources.get(option_name, "defaults")
        if source == "defaults":
            log.info("Using default value for %s", form_key)
        elif source == "config.json":
            log.info("Using config.json value for %s", form_key)
        elif source == "form":
            log.info("Using form value for %s", form_key)
        elif source == "form_override":
            log.info("Using form value (overrides config.json) for %s", form_key)


# ---------------------------------------------------------------------------
# Driver args file (TASK-005)
# ---------------------------------------------------------------------------

def build_driver_arg_string(resolved):
    """Build the Stage 1 driver CLI argument string (space-separated).

    Empty string is a valid result — the Docker ``BUILD_ARGS`` ARG defaults
    to ``""`` and the driver handles the no-flags case.

    Build-level flags (BUILD_LEVEL_FLAGS, e.g. ``--multi-weight``) are
    appended AFTER the driver flags: they are consumed by the Stage 1 RUN
    chain (and stripped before the legacy driver invocation), not by the
    driver itself.
    """
    flags = [
        flag
        for option_name, flag in OPTION_TO_DRIVER_FLAG.items()
        if resolved.get(option_name)
    ]
    flags += [
        flag
        for option_name, flag in BUILD_LEVEL_FLAGS.items()
        if resolved.get(option_name)
    ]
    return " ".join(flags)


def write_args_file(args_string, output_path):
    """Write the driver arg string to ``output_path``."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(args_string, encoding="utf-8")


# ---------------------------------------------------------------------------
# Manifest (TASK-006)
# ---------------------------------------------------------------------------

def generate_manifest(resolved, sources, config_source, manifest_path):
    """Write a build manifest conforming to Spec §4.6 ``required`` array.

    Fields populated by Phase 1 (other than resolved_options):
        - manifest_version
        - build_timestamp (UTC ISO 8601, ``Z`` suffix)
        - source_commit (env GITHUB_SHA, "unknown" fallback for local)
        - workflow_version
        - toolchain_versions.python (fontforge/ttfautohint filled in Phase 3)

    Fields intentionally left for downstream stages:
        - toolchain_versions.fontforge
        - toolchain_versions.ttfautohint
        - font_files (empty array in Phase 1; populated in Phase 3)
    """
    toolchain_versions = {
        "python": "%d.%d.%d" % sys.version_info[:3],
    }

    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "build_timestamp": (
            datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
        ),
        "source_commit": os.environ.get("GITHUB_SHA", "unknown"),
        "workflow_version": WORKFLOW_VERSION,
        "config_source": config_source,
        "resolved_options": dict(resolved),
        "toolchain_versions": toolchain_versions,
        "font_files": [],
        "spdx_license": SPDX_LICENSE,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_bool(value):
    """argparse ``type=`` for boolean form inputs.

    Accepts ``true|false`` (case-insensitive), ``1|0``, ``yes|no``. Already
    decoded booleans pass through unchanged so test code can pass ``True``
    / ``False`` directly.
    """
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in ("true", "1", "yes"):
        return True
    if s in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError(
        f"expected true|false (got {value!r})"
    )


def build_arg_parser():
    """Construct the argparse parser (separated for testability)."""
    parser = argparse.ArgumentParser(
        prog="configure.py",
        description=(
            "Fantasque Sans Mono Custom Build configuration resolver. "
            "Validates config.json, applies form/config/default precedence, "
            "and writes the Stage 1 driver args + manifest."
        ),
    )
    parser.add_argument(
        "--config-file",
        type=Path,
        default=Path("config.json"),
        help="Path to config.json (default: ./config.json)",
    )
    parser.add_argument(
        "--schema-file",
        type=Path,
        default=Path("config.schema.json"),
        help="Path to config.schema.json (default: ./config.schema.json)",
    )
    parser.add_argument(
        "--form-large-line-height",
        type=_parse_bool,
        default=None,
        help="workflow_dispatch form input: large_line_height (true|false)",
    )
    parser.add_argument(
        "--form-no-loop-k",
        type=_parse_bool,
        default=None,
        help="workflow_dispatch form input: no_loop_k (true|false)",
    )
    parser.add_argument(
        "--form-no-calt",
        type=_parse_bool,
        default=None,
        help="workflow_dispatch form input: no_calt (true|false)",
    )
    parser.add_argument(
        "--form-use-hinted",
        type=_parse_bool,
        default=None,
        help="workflow_dispatch form input: use_hinted (true|false)",
    )
    parser.add_argument(
        "--form-enable-multi-weight",
        type=_parse_bool,
        default=None,
        help="workflow_dispatch form input: enable_multi_weight (true|false)",
    )
    parser.add_argument(
        "--output-args-file",
        type=Path,
        default=None,
        help="Path to write the Stage 1 driver CLI argument string",
    )
    parser.add_argument(
        "--generate-manifest",
        type=Path,
        default=None,
        help="Path to write the output manifest.json",
    )
    return parser


def parse_args(argv=None):
    return build_arg_parser().parse_args(argv)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(argv=None):
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        stream=sys.stdout,
    )

    args = parse_args(argv)

    # 1. Load and validate.
    config = load_config(args.config_file)
    schema = load_schema(args.schema_file)
    try:
        validate_config(config, schema)
    except ConfigValidationError as exc:
        log.error("%s", exc)
        return 1

    # 2. Collect form inputs in the shape resolve_options() expects.
    form_inputs = {
        "large_line_height": args.form_large_line_height,
        "no_loop_k": args.form_no_loop_k,
        "no_calt": args.form_no_calt,
        "use_hinted": args.form_use_hinted,
        "enable_multi_weight": args.form_enable_multi_weight,
    }

    # 3. Resolve and aggregate.
    resolved, sources = resolve_options(config, form_inputs)
    has_config_file = args.config_file.is_file()
    config_source = compute_config_source(sources, has_config_file)

    # 4. Emit log lines (TASK-004: one per option + final config_source).
    log_option_sources(sources)
    log.info("config_source: %s", config_source)

    # 5. Optional outputs.
    if args.output_args_file is not None:
        args_string = build_driver_arg_string(resolved)
        write_args_file(args_string, args.output_args_file)
        log.info(
            "Wrote driver args (%d chars) to %s",
            len(args_string),
            args.output_args_file,
        )

    if args.generate_manifest is not None:
        generate_manifest(resolved, sources, config_source, args.generate_manifest)
        log.info("Wrote manifest to %s", args.generate_manifest)

    return 0


if __name__ == "__main__":
    sys.exit(main())
