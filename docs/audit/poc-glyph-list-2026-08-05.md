<!-- markdownlint-disable -->

# PoC Glyph List — Multi-Weight Variants (Regular ↔ Bold)

![Status: Draft](https://img.shields.io/badge/status-Draft-orange)
![Date: 2026-08-05](https://img.shields.io/badge/date-2026-08-05-blue)

> **Update 2026-08-05 (Phase 2):** the harmonized masters at
> `Sources/Harmonized/{Regular,Bold}` have been superseded by the **full**
> harmonized masters (all glyphs — see Phase 2 execution). The PoC subset
> composition below remains the documented selection record; the runbook in
> §4 still applies verbatim (paths unchanged).

## Purpose

Deliverable of **TASK-1.1** (Implementation Phase 1 — Proof of Concept, GOAL-002).
Documents the ~40–50 glyph PoC subset for the Regular ↔ Bold pair, selected per
PRD **FR-2.1** (quantitative *worst offenders* criteria: node_diff, contour
mismatch, functional priority) and **AC-P01**, together with the harmonization
status of every glyph.

Companion artifacts:

- Harmonized subset masters: `Sources/Harmonized/Regular/` and
  `Sources/Harmonized/Bold/` (36 glyphs each + `font.props`)
- Visual Quality Rubric: `docs/audit/visual-quality-rubric.md`
- Harmonization analysis tooling: ad-hoc session scripts (not committed — see
  *Methodology* below)

## 1. Quantitative Baseline (Worst-Offender Analysis)

Run with a structural parser replicating `Scripts/detect_incompatibility.py`
semantics (node count per contour, contour count, winding direction) over the
actual `.sfdir` sources — **no FontForge required** (plain-text `.glyph` files):

| Metric | Value |
|---|---|
| Regular glyphs | 1,042 |
| Bold glyphs | 1,040 |
| Common glyphs analyzed | 1,037 |
| Compatible (structural) | 633 (61.0%) |
| Incompatible | 394 (39.0%) |
| Only in Regular | 5 (`quotedbl.old`, `quotesingle.old`, `uni0527`, `uni2A7D`, `uni2A7E`) |
| Only in Bold | 3 (`ring`, `uniE0E3`, `uniE0E4`) |

Top worst offenders (non-ligature, non-PUA) used to fill the "3–5 worst
offenders" slot of FR-2.1:

| Rank | Glyph | Issue (Regular vs Bold) |
|---|---|---|
| 1 | `percent` | node_diff contour 0: 61 vs 87; **contour count 5 vs 3** |
| 2 | `hyphen` | node_diff contour 0: 5 vs 27 |
| 3 | `plus` | node_diff contour 0: 13 vs 32 |
| 4 | `numbersign` | node_diff contour 0: 84 vs 66 |
| 5 | `greaterequal` | node_diff contour 0: 24 vs 46 |

## 2. PoC Subset (40 Glyphs) — Harmonization Status

Selection per FR-2.1: lowercase `a`–`z`, multi-contour glyphs, complex-counter
glyphs, functionally critical glyphs, plus worst offenders.

> **Deviation from FR-2.1 (documented):** the font contains **no `fi`/`fl`
> ligature glyphs** (verified against the full glyph set of both masters — the
> font's ligatures are of the `*.liga` family, e.g. `equal_equal.liga`, which
> belong to the Phase 2 shared pool). `germandbls` (ß) serves as the
> complex-counter representative; no replacement glyph was added beyond the
> worst-offender slot.

### 2.1 Lowercase `a`–`z` (26)

| Glyph | Status | Note |
|---|---|---|
| `a`, `b`, `e`, `f`, `g`, `h`, `i`, `j`, `k`, `l`, `n`, `o`, `p`, `q`, `r`, `s`, `t`, `u`, `v`, `w`, `x`, `y`, `z` | ✅ harmonized | Structural compatibilization applied |
| `c`, `n`*, `s`, `y`* | ✅ already compatible | Copied as-is |

\* `n`, `y`, `s`, `c`, `e`, `o` were already structurally compatible; they are
included in the harmonized masters unmodified.

| Glyph | Status | Reason |
|---|---|---|
| `d` | ⛔ skipped | Contour count mismatch 4 vs 2 — Regular carries a **doubled/overlapping outline** (two stacked drawings, centroid pairs ~73 units apart). Requires a design decision (remove overlap or restructure) — designer harmonization, Phase 2 |
| `m` | ⛔ skipped | Contour count mismatch 1 vs 2 — Regular draws `m` as a single connected outline, Bold splits it into two contours. Requires design-level harmonization |

### 2.2 Multi-Contour & Complex Counter (6)

| Glyph | Status | Note |
|---|---|---|
| `g` | ✅ harmonized | 6-contour structure in both masters; equalized |
| `at` | ⛔ skipped | One contour pair needs +1 node with no line segment available (all-curve contour). Requires designer decision (Bold `@` is a much simpler 15-node design vs Regular's 77-node) |
| `ampersand` | ✅ harmonized | |
| `Q` | ✅ harmonized | |
| `question` | ✅ harmonized | Contour order differed between masters (dot/body) — reordered consistently |
| `exclam` | ✅ harmonized | Contour order reordered consistently |
| `germandbls` | ✅ harmonized | Replaces absent `fi`/`fl` (see deviation note) |

### 2.3 Functionally Critical (4)

| Glyph | Status |
|---|---|
| `space` | ✅ compatible (empty glyph) |
| `period` | ✅ compatible |
| `comma` | ✅ compatible |
| `zero` | ✅ compatible |

### 2.4 Worst Offenders (4, from §1)

| Glyph | Status | Note |
|---|---|---|
| `percent` | ⛔ skipped | Contour count mismatch 5 vs 3 — design-level harmonization required |
| `hyphen` | ✅ harmonized | 5 → 27 nodes (22 insertions) |
| `plus` | ✅ harmonized | 13 → 32 nodes |
| `numbersign` | ✅ harmonized | |

**Summary: 36/40 glyphs available in the harmonized subset masters; 4 skipped
(design-level harmonization required — `d`, `m`, `at`, `percent`).**

## 3. Harmonization Methodology (TASK-1.1)

The PoC harmonization was performed as **structural, shape-preserving
compatibilization** at the `.sfdir` text level:

1. **Reference expansion** — `Refer:` components (e.g., `i`/`j` stem via
   `dotlessi`, dot via `dotabove`) resolved recursively into concrete contours
   with transform application, so both masters share pure-outline structure.
2. **Contour matching** — per-glyph contour pairing by centroid (handles
   differing contour order, e.g. `question`, `exclam`).
3. **Winding alignment** — contours reversed (cyclic point reorder with
   segment-kind remapping) where masters differ.
4. **Node equalization** — the smaller contour gains nodes via exact
   curve-preserving operations:
   - cubic split (de Casteljau, +3 nodes),
   - on-curve insertion on a line segment (+1 node),
   - `l`→degenerate-`c` conversion with collinear controls (+2 nodes, shape
     identical).

**Verification performed:**

- Re-parse of both harmonized masters: **0 compatibility issues** (contour
  count, node count, winding identical per glyph).
- Shape preservation: every inserted on-curve point lies on the original
  curve; sampled curves coincide (residual ≤ 0.7 em-units — sampling
  discretization of the verification metric, converging quadratically with
  sampling density; true deviation ≈ 0).
- Closure entries and point flags preserved per original conventions.

**Assumption (explicit):** this is PoC-level *structural* harmonization, NOT
the final *design* harmonization of Phase 2. The type designer must still
review the interpolated results (human gate FR-2.4/AC-P03) and refine glyph
structure during Phase 2. The 4 skipped glyphs require genuine design work.

**Tooling note:** the analysis/harmonization engine is session tooling (not a
committed plan artifact — the plan's file list for TASK-1.1 is the glyph list
document). Methodology is fully described here for reproducibility.

## 4. Remaining PoC Steps (TASK-1.2 / 1.3 / 1.X)

The following run under FontForge (GitHub Actions / Docker `builder-fontforge`
image — local execution deferred by user decision 2026-08-05):

```bash
# TASK-1.2 — interpolate subset to Medium (500), no hinting
fontforge -lang=py -script Scripts/poc_interpolation.py \
  --regular Sources/Harmonized/Regular --bold Sources/Harmonized/Bold \
  --output build/poc/Medium.sfdir --ttf build/poc/Medium.ttf

# TASK-1.3 — specimen + two-pass threshold calibration (15.0° → T_final)
python3 Scripts/generate_specimen.py --weights build/poc --output build/poc/specimen
fontforge -lang=py -script Scripts/validate_interpolation.py \
  --interpolated build/poc/Medium.sfdir --masters Sources/Harmonized \
  --threshold 15.0 --output build/poc/report-R1.json \
  --overlay-dir build/poc/overlays

# TASK-1.X — final gate on R2 with calibrated T_final
fontforge -lang=py -script Scripts/validate_interpolation.py \
  --interpolated build/poc/Medium.sfdir --masters Sources/Harmonized \
  --threshold T_final --output build/poc/report-R2.json --fail-fast
```

PoC gate (FR-2.4): script — `pass_rate ≥ 90%` and `fail_count = 0` on R2;
human — visual diff review (8/12/16/24 pt) with ≥ 90% "handwritten feel"
per the Visual Quality Rubric.

**Phase 3 (TASK-3.2/3.X — GA):** interpolated core weights are available at
`Sources/Harmonized/Interpolated/{Medium,SemiBold}/` (text-level previews —
authoritative run is `multi_weight_driver.py` under FontForge):

```bash
# TASK-3.X — validation per core weight (Phase 3 gate: ≤ 2% warning, 0 fail)
fontforge -lang=py -script Scripts/validate_interpolation.py \
  --interpolated Sources/Harmonized/Interpolated/Medium \
  --masters Sources/Harmonized --threshold T_final \
  --output build/reports/interp-medium-R2.json --fail-fast
fontforge -lang=py -script Scripts/validate_interpolation.py \
  --interpolated Sources/Harmonized/Interpolated/SemiBold \
  --masters Sources/Harmonized --threshold T_final \
  --output build/reports/interp-semibold-R2.json --fail-fast

# TASK-3.2 — specimen sheet (needs TTF: generate from the .sfdir under FontForge)
fontforge -lang=py -script Scripts/multi_weight_driver.py \
  --sources Sources --output Sources/Harmonized/Interpolated
python3 Scripts/generate_specimen.py --weights build/pre_hint/TTF --output build/specimen

# Metadata verification Layer 1 (one-liner FontForge equivalents)
# familyname == "Fantasque Sans Mono" across all weights incl. masters;
# fullname == "Fantasque Sans Mono {Weight}"; os2_weight 400/500/600/700
```

> **Driver fix (2026-08-05):** `Scripts/multi_weight_driver.py` passed a font
> *object* to `font.interpolateFonts(factor, bold)` — the FontForge API
> requires the other font's *filename* (`interpolateFonts(fraction, filename)`).
> Fixed surgically (bold path threaded through); call sites updated. The
> harmonization-skip list (tracking.json) means a FontForge run currently
> FAILS at the native interpolation step (GUD-002 fail-fast) until the 481
> `needs_harmonization` glyphs are harmonized by the designer — the text-level
> previews use copy-as-fallback for those glyphs instead.

> **Risk flagged during review:** `Scripts/validate_interpolation.py` called
> `glyph.selfIntersects` as a property; the FontForge API exposes it as a
> method (`glyph.selfIntersects()`). A bound method is always truthy, so every
> glyph would be classified `fail` — the PoC gate could never pass. **Fixed**
> (surgical) in this session; `tests/test_validate_interpolation.py` covers
> the regression (`test_pass_status`). Verify in the container run.

## 5. References

- PRD FR-2.1–FR-2.5, AC-P01–AC-P07 — `docs/prd-20260731-1000-multi-weight-variants.md`
- Spec §5.1, §6.2 — `spec/spec-multi-weight-variants.md`
- Plan TASK-1.1–1.Y — `plan/plan-feature-multi-weight-variants-v1.13.md`
- Visual Quality Rubric — `docs/audit/visual-quality-rubric.md`
