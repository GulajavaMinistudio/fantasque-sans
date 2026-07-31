# 0003 - Workflow A (FontForge Interpolation) for V1, Deferred UFO/fontmake Migration

**Date:** 2026-07-31
**Status:** Accepted

## Context
The Multi-Weight Variants initiative requires generating 4–6 static weight instances from two existing masters (Regular 400 and Bold 700). Two toolchain options exist: **Workflow A** — FontForge `.sfdir` + `font.interpolateFonts()` using the existing familiar toolchain — and **Workflow B** — UFO v3 + `fontmake`/`ufo2ft`, the industry standard for multi-weight and Variable Font generation. The decision must balance tactical speed (immediate harmonization without format conversion) against long-term maintainability (native Variable Font support, richer `fontTools` ecosystem).

## Decision
V1 will use **Workflow A** (FontForge `.sfdir` + linear interpolation via `font.interpolateFonts()`). Migration to **Workflow B** (UFO v3 + `fontmake`) is deferred to V2 and will be explored via GH-006 as a spike research task. The existing FontForge Python API and `.sfdir` sources remain the authoritative format for V1.

## Consequences
- **Speed**: Type designers can begin harmonization immediately without learning a new toolchain or performing `.sfdir` → `.ufo` conversion, which risks introducing format-translation errors.
- **Accepted limitation**: FontForge's `font.interpolateFonts()` only supports linear interpolation — no optical correction. Extrapolation for stretch weights (Light 300, ExtraBold 800) may produce unacceptable distortion; these weights follow a *partial success* tier and will be deferred to V2 if visual review fails.
- **Technical debt**: A future dual-toolchain scenario (FontForge for legacy `.sfdir` maintenance, UFO/`fontmake` for V2+ multi-axis generation) is explicitly accepted. The `.sfdir` → UFO conversion pathway remains unvalidated and is scoped to GH-006.
- **Variable Font readiness**: V1 cannot produce Variable Font (`gvar` table) output; this is a non-goal (PRD §2.3). V2 migration to UFO/`fontmake` unlocks native VF support.

## Considered Options
- **Workflow B (UFO/fontmake) for V1**: Rejected. Would require converting all four `.sfdir` masters (Regular, Bold, Italic, BoldItalic) to UFO v3 before harmonization could begin, adding unknown format-conversion risk and delaying the critical path. The team has no operational experience with `fontmake`/`ufo2ft` in this repository. GH-006 will de-risk this path for V2.
- **Hybrid approach (FontForge for interpolation, UFO for output)**: Rejected. Adds complexity without clear benefit — the interpolation engine and output format would diverge, creating two debugging surfaces instead of one.
