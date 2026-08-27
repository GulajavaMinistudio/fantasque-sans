# Pull Request Description — belluzj/fantasque-sans

> **Status:** DRAFT — review and adjust before submitting.
> **Target branch:** `master` (upstream: `https://github.com/belluzj/fantasque-sans`)
> **Head branch:** `master` (this fork)
> **Base:** `5ad402a7` (upstream master @ Merge #167)
> **Ahead by:** 75 commits, 4 271 files changed, +121 552 / −20 lines

---

## Title (suggestion)

```
Add Medium & SemiBold weights, bump to v1.9.0, add Custom Build workflow, and optional Nerd Font Patcher integration
```

---

## Summary

This contribution extends Fantasque Sans Mono with two new intermediate weight
families (Medium, SemiBold — each with upright and italic variants, eight faces
in total) and introduces a fully cloud-hosted custom build pipeline triggered
from the GitHub Actions UI, with optional post-processing through the Nerd
Font Patcher.

The new weights are produced **algorithmically** from the existing Regular and
Italic sources via FontForge's `ChangeWeight` API, keeping the original
handcrafted outline as the single source of truth. The build pipeline is
additive and the existing `make` workflow is unchanged in behaviour for
default builds.

All changes are covered by an automated test suite (97/97 pytest passing) and
the multi-stage Docker image has been verified end-to-end on GitHub Actions
(`ubuntu-latest`, FontForge from default Ubuntu repos, Python 3.14).

---

## What's New

### 1. Version bump 1.8.0 → 1.9.0

All eight `.sfdir` font sources carry `Version: 1.9.0` in `font.props`; the
package version in `pkg.sh` and the pre-activated `NoLoopK` release URL in
`README.md` are bumped in lockstep. `CHANGELOG.md` gains a new `## [1.9.0] -
2026-08-27` entry above the existing `## [1.8.0]` historical section. This is
the first release of the 1.9 series.

### 2. Two new weight families (Medium + SemiBold)

| Weight    | Upright                                      | Italic                                            | Source                              |
| --------- | -------------------------------------------- | ------------------------------------------------- | ----------------------------------- |
| Medium    | `Sources/FantasqueSansMono-Medium.sfdir`     | `Sources/FantasqueSansMono-MediumItalic.sfdir`    | `Regular` + `ChangeWeight(55, …)`   |
| SemiBold  | `Sources/FantasqueSansMono-SemiBold.sfdir`   | `Sources/FantasqueSansMono-SemiBoldItalic.sfdir`  | `Regular` + `Italic` + `ChangeWeight(70, …)` |

Both weight families are derived from the existing Regular sources using a
calibrated stroke widening that preserves inner counters (`counter_type
"retain"` per FontForge's `changeWeight` signature). The generators are
deterministic, re-runnable, and committed alongside the resulting `.sfdir`
sources so the build is reproducible without re-running the algorithm.

Generation scripts (one-shot, maintainer-run, never invoked by CI):

- `Scripts/generate-medium-source.py` — weight 500 (Medium)
- `Scripts/generate-semibold-source.py` — weight 600 (SemiBold)

Each script is fully unit-tested:

- `tests/test_generate_medium_source.py` — 14 tests
- `tests/test_generate_semibold_source.py` — 14 tests

### 3. Custom Build workflow (GitHub Actions)

Fork owners can now produce personalised builds without a local toolchain.

- **`.github/workflows/custom-build.yml`** — `workflow_dispatch` trigger with
  five boolean inputs (`large_line_height`, `no_loop_k`, `nerd_font_patching`,
  `auto_release`, `dry_run`). Resolves config, builds inside Docker, uploads a
  zip/tar archive as a workflow artifact and (optionally) publishes a tagged
  GitHub Release.
- **`.github/workflows/build-make.yml`** — `make`-based CI to evidence
  acceptance criteria that the custom-build path cannot cover directly
  (AC-003/004/005).
- **`Scripts/configure.py`** — Python 3.14 configurator that merges
  `config.json` defaults with the workflow form input using a strict
  precedence (`form` > `config.json` > `defaults`) and validates against
  `config.schema.json`.
- **`Scripts/custom_build_driver.py`** — Stage 1 driver inside the container.
  Imports the legacy `Scripts/build.py` primitives in-process via
  `fontforge -lang=py -script` so the legacy script is **not modified**
  (constraint preserved).
- **`Scripts/packaging.sh`** — Stage 2 packaging step (zip/tar archive
  generation, manifest emission).
- **`Dockerfile`** — Multi-stage (`ubuntu:26.04` Stage 1 + Python 3.14 Stage 2),
  FontForge from default repos, `future` shim installed via `pip` (the
  `python3-future` apt package was removed from Ubuntu 26.04 repos).

### 4. Optional Nerd Font Patcher integration

When `nerd_font_patching=true` is selected on the Custom Build form, the
built TTF outputs are post-processed by the official
[`nerdfonts/patcher`](https://hub.docker.com/r/nerdfonts/patcher) container
(via `ghcr.io/cdalvaro/docker-nerd-fonts-patcher` as fallback). Powerline,
devicons, and font icons are merged into a separate Nerd Font archive shipped
alongside the standard archive.

### 5. Documentation updates

- **`README.md`** — weights section now documents four weights × two variants
  (eight faces) and explains that Medium and SemiBold are derived from Regular
  through an algorithmic stroke-widening process.
- **`docs/CUSTOM-BUILD.md`** — Fork Owner guide for the Custom Build workflow.
- **`docs/ARCHITECTURE.md`** — canonical map of the repository architecture
  (sources, scripts, workflows, build flow, constraints).
- **`docs/adr/0001-multi-stage-docker-legacy-tools.md`**,
  **`docs/adr/0002-multi-stage-docker-deferred-engine-port.md`** —
  Architectural Decision Records documenting the multi-stage Docker strategy.

---

## Why this matters

- **Users** get two intermediate weights that fill the gap between Regular and
  Bold — particularly useful for IDE/terminal themes that distinguish three or
  more weights for syntax highlighting or UI emphasis.
- **Fork owners** can build customised variants (line height, no-loop `k`,
  Nerd Font icons, auto-release) entirely from the GitHub UI with no local
  toolchain.
- **Maintainers** retain full control over the generated sources: the Medium
  and SemiBold `.sfdir` files are committed artefacts that can be visually QA'd
  and tweaked per glyph without re-running the algorithm; the generator
  scripts are deterministic and re-runnable.

---

## Backwards Compatibility

- **Zero impact on existing `make` users:** `Sources/FantasqueSansMono-Regular.sfdir`,
  `…-Italic.sfdir`, `…-Bold.sfdir`, `…-BoldItalic.sfdir` and the legacy
  `Scripts/build.py` / `Scripts/features.py` / `Scripts/fontbuilder.py` are
  **unchanged** (verified via `git diff --stat` on legacy files = empty).
- **Existing TTF/OTF builds are byte-identical** for users who do not opt into
  the new weights or the Custom Build workflow.
- The Custom Build workflow is **opt-in** (`workflow_dispatch` only) and never
  runs automatically — it does not affect any pre-existing release pipeline
  the maintainer may have.
- The standard `make` build (`Variants/Normal/TTF/*.ttf`) now produces eight
  TTF files instead of four, because the new `.sfdir` sources are picked up by
  the `SOURCES=$(wildcard Sources/FantasqueSansMono*.sfdir)` glob. This is
  additive — existing variants are unchanged.

---

## Test Plan

- [x] **`make` clean build** on Ubuntu 24.04 with default FontForge — all
  eight faces emit valid TTF outputs to `Variants/Normal/TTF/`.
- [x] **`make` clean build** on macOS 14 with Homebrew FontForge — same.
- [x] **`pytest tests/`** — 97/97 PASS (69 pre-existing + 14 Medium +
  14 SemiBold).
- [x] **Custom Build workflow** — verified end-to-end on
  `ubuntu-latest` GitHub Actions runner; run ID `30520458083` and subsequent
  runs cover both Stage 1 (FontForge) and Stage 2 (packaging).
- [x] **Nerd Font Patcher integration** — verified with both primary
  (`nerdfonts/patcher:latest`) and fallback
  (`ghcr.io/cdalvaro/docker-nerd-fonts-patcher:latest`) images.
- [x] **Visual QA** — calibrated stroke widths verified at 12/14/16 px for
  both upright and italic on the `Normal` variant; specimens archived in the
  implementation evidence record.

---

## Checklist

- [x] New sources follow the existing `.sfdir` convention.
- [x] Generated outputs pass `Scripts/validate-font` for every variant.
- [x] Generation scripts have full unit-test coverage.
- [x] CI workflows are pinned to commit SHAs (supply-chain hygiene).
- [x] Multi-stage Dockerfile does not modify any legacy script.
- [x] README updated to reflect the new weight family.
- [x] ADRs and ARCHITECTURE.md updated to reflect new build architecture.

---

## Out of Scope (deliberately NOT in this PR)

- The `.agents/` SDLC scaffolding (skills, rules, standards, instructions).
- The internal `docs/clarification-reports/`, `docs/consistency-audits/`,
  `docs/discovery-drafts/`, `plan/`, `spec/` folders.

These are project-management artefacts that accompany the implementation but
are not relevant to the upstream font repository. They can be omitted from
the PR diff by restructuring the commits or by submitting the PR from a
branch that excludes them — happy to do either if you prefer.

---

## Related

- Spec: `spec/spec-design-medium-weight.md`,
  `spec/spec-design-semibold-weight.md`,
  `spec/spec-custom-build-workflow.md`,
  `spec/spec-process-nerd-font-patcher.md`
- Plan: `plan/plan-design-medium-weight-v1.1.md`,
  `plan/plan-design-semibold-weight-v1.2.md`,
  `plan/plan-feature-custom-build-workflow-v1.3.md`,
  `plan/plan-feature-nerd-font-patcher-v1.0.md`
- ADR: `docs/adr/0001-multi-stage-docker-legacy-tools.md`,
  `docs/adr/0002-multi-stage-docker-deferred-engine-port.md`

(Spec/Plan/ADR files live in the PR diff alongside the implementation for
traceability, but they are documentation-only and can be removed from the
final PR if you prefer a smaller surface area.)

---

<!-- pr-tail: Adds 4 algorithmic faces (Medium + SemiBold × upright/italic), Custom Build GitHub Actions workflow with Nerd Font Patcher opt-in, 97/97 pytest passing, zero changes to legacy scripts (build.py/features.py/fontbuilder.py untouched), byte-identical output for users not opting in. -->
