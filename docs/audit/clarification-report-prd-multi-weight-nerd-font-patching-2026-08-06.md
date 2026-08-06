# Clarification Report — Review Iteration 1

> [!SUCCESS]
> **REMEDIATION STATUS: RESOLVED**
> This audit report has been remediated by the Product Manager PRD persona on 2026-08-06.
>
> - **Projected Readiness Score:** 92/100
> - **Applied:** Edits 1–7 to `docs/prd-20260806-1401-multi-weight-nerd-font-patching.md` (now v1.1), including a consistency sweep of all stale "15 PUA codepoints" references, the explicit `enable_multi_weight = true` activation conditional, and removal of the contradictory "no user-facing configuration" clause from FR-1.3. PUA counts (Regular 69, Bold 69, Italic 75, BoldItalic 72, union 75) were re-verified against master sources using the full-PUA `Encoding:` audit methodology.
> - **Applied additionally (per explicit user command):** Edit 8 — Discovery Draft revised to Rev 4 (`docs/discovery-draft-20260806-0428-multi-weight-nerd-font-patching.md`): per-master full-PUA audit table, corrected Box Drawing rationale, `PinnedIconInventory` (O-3) section, and corrected Scope Clarification record.
> - **Factual deviation from Edit 8's text:** the report's "Master Regular has 112 codepoints in U+25xx" figure was NOT reproducible — a full `Encoding:`-field audit shows **160/160 (contiguous U+2500–259F) in all four mono masters**, confirming the original Discovery Draft claim. Rev 4 states the verified figure.
> - **Remaining (Spec phase):** O-3 (PinnedIconInventory audit of the pinned Nerd Fonts v3.5.0 distribution) and O-4 (pinned patcher source citation for metric-normalization behavior).

**Document under review:** `docs/prd-20260806-1401-multi-weight-nerd-font-patching.md` (v1.0 DRAFT)
**Upstream artifact:** `docs/discovery-draft-20260806-0428-multi-weight-nerd-font-patching.md` (Rev 3, approved)
**Reviewer:** Clarification Analyst persona (`/sdlc-clarify-reqs`)
**Date:** 2026-08-06
**Iteration:** 1

---

## Readiness Score

| Score Type                     | Value      | Threshold | Status                                                                                                     |
| ------------------------------ | ---------- | --------- | ---------------------------------------------------------------------------------------------------------- |
| **Current Actual**             | **45/100** | >= 80     | **Below Threshold** — PRD/Discovery must be revised                                                        |
| **Projected Post-Remediation** | **92/100** | >= 80     | Above threshold IF the PRD Authoring Agent applies Edits 1–7 below. **Projected only — not yet realized.** |

### Score Breakdown (Current Actual)

- **Completeness (40%):** 22/40 — FRs structurally present but codepoint count materially wrong (PRD claims 15 PUA codepoints; full Encoding-based audit shows per-weight SourcePopulated of **69 / 69 / 75 / 72**, union **75** — approximately 5x the claimed count). License manifest, Nerd Font icon enumeration, naming convention, build duration, and stretch weight disclosure all underspecified.
- **Clarity (30%):** 11/30 — "Additive by contract" framing is factually wrong; "vertical metrics unchanged" is contradicted by Nerd Fonts Patcher behavior; "always-on" is conditional on `enable_multi_weight`; "pre-patch vs post-patch" terminology ambiguous; collision report conflates allowlist with effective overwrite.
- **Alignment (30%):** 12/30 — PRD's "15 PUA codepoints" claim does not match Encoding-based master source audit (full PUA: 69/69/75/72, union 75); Discovery Draft's Box Drawing rationale (160/160 coverage claim) factually wrong; per-master allowlist differences not addressed in PRD/Discovery; Discovery's "U+E100–E12C safe" claim is unverified (hypothesis only).
- **Critical Flaw Veto:** None. All findings are remediable via authoring instructions below.

### Score Breakdown (Projected Post-Remediation)

- **Completeness (40%):** 37/40 — After Edits 1–7 applied, all FRs have full-PUA allowlist per weight, Nerd Font icon set referenced (pending Spec-phase audit), license manifest scoped correctly.
- **Clarity (30%):** 27/30 — Additive framing reworded, vertical metrics re-stated as "documented in collision report for audit" (pending Spec-phase pinned-source citation), always-on conditional clarified, pre-patch/post-patch split into 9.3a/9.3b, collision report separates allowlist/expected/observed with correct gate.
- **Alignment (30%):** 28/30 — Codepoint counts align with full-PUA Encoding audit (69/69/75/72, union 75); Box Drawing rationale corrected; per-master differences explicit; icon-set claims marked as hypotheses pending pinned audit.

> **Note on 92/100:** This is a **projected** score contingent on the PRD Authoring Agent applying all 7 edits AND the Spec phase delivering the Out-of-Scope items (O-3 PinnedIconInventory audit, O-4 patcher metric documentation) on the pinned sources. If Spec phase cannot cite pinned sources for O-3 and O-4, the projected score may be lower.

---

## 0. Implementation Status (planned vs. current codebase)

**All behavior described in the PRD and in this report regarding the Nerd Fonts Patcher is the PLANNED target architecture after implementation — it does NOT describe the current codebase.**

Verified against the repository (2026-08-06):

- **`Dockerfile`:** contains only two stages — `builder-fontforge` (Stage 1) and `final` (Stage 2). There is **no `builder-nerd-patcher` stage**.
- **`.github/workflows/custom-build.yml`:** the only artifact-producing workflow; its steps (checkout → unit tests → config validation → docker build → docker run packaging → upload → release) contain **no Nerd Fonts Patcher step**.
- **`Scripts/`:** no patcher-related script exists (`detect_incompatibility.py`, `validate_harmonization.py`, `validate_interpolation.py`, `multi_weight_driver.py`, `custom_build_driver.py`, `packaging.sh`, etc. — none invoke the Nerd Fonts Patcher).
- **Discovery Draft Rev 3** itself marks the patcher stage as **[PROPOSED TARGET ARCHITECTURE — NOT IMPLEMENTED]** (line 8, 83).

**Consequence:** today, **no build of any kind runs the patcher** — not single-weight, not multi-weight. The behavior "`enable_multi_weight = true` → patcher runs and produces the Nerd Font Flavor" is the PRD's target contract (FR-1.3, FR-8), which only materializes after the Spec/Code phases implement it. Any statement in this report like "the patcher overwrites at the allowlist" refers to the intended post-implementation behavior, not to anything observable in the repository today.

---

## 1. Critical Findings (Blockers)

These must be fixed by the PRD Authoring Agent to reach the 80-point threshold.

### F-1. PRD codepoint count materially wrong (FR-4 intro, FR-4.3, SM-T1)

- **Requirement (current PRD):** "The verified collision surface is exactly 15 PUA codepoints: U+E000–E007 (Fantasque stylistic alternates), U+E0A0–E0A2 and U+E0B0–E0B3 (native Powerline symbols)."
- **Issue:** Encoding-based audit of master source `.glyph` files (full PUA U+E000–U+F8FF) shows per-weight **SourcePopulated** counts of **69 / 69 / 75 / 72** (Regular / Bold / Italic / BoldItalic), with union across all masters = **75 codepoints** (composition: U+E000–E00A [11] + U+E035–E039 [5] + U+E03C–E03F [4] + U+E0A0–E0A2 [3] + U+E0B0–E0B3 [4] + U+E0E2–E0E4 [3] + U+E100–E12C [45]). The PRD's "15" count is incorrect by approximately 5x and conflates range claim with populated claim. The Discovery Draft's "U+E000–E007" claim is also wrong — `quotedbl.old` (E003), `quotesingle.old` (E004), `k.noloop` (E005), `kcommaaccent.noloop` (E006), `uni01E9.noloop` (E007) are populated in Regular, and `afii10066.serbian` through `afii10084.serbian` plus `k.noloop` family extend Italic/BoldItalic up to U+E00A.
- **Per-master composition (verified):**
  - Regular: E000–E007 (8) + E035–E039 (5) + E03C–E03F (4) + E0A0–E0A2 (3) + E0B0–E0B3 (4) + E100–E12C (45) = 69
  - Bold: E000–E002 + E005–E007 (6; E003–E004 unpopulated) + E035–E039 (5) + E03C–E03F (4) + E0A0–E0A2 (3) + E0B0–E0B3 (4) + E0E3–E0E4 (2) + E100–E12C (45) = 69
  - Italic: E000–E00A (11) + E035–E039 (5) + E03C–E03F (4) + E0A0–E0A2 (3) + E0B0–E0B3 (4) + E0E2–E0E4 (3) + E100–E12C (45) = 75
  - BoldItalic: E000–E00A (11) + E035–E039 (5) + E03C–E03F (4) + E0A0–E0A2 (3) + E0B0–E0B3 (4) + E100–E12C (45) = 72
  - Arithmetic check: 11 + 5 + 4 + 3 + 4 + 3 + 45 = 75 (union, verified). Earlier report drafts cited "union 30" (E0xx-only) and "35" — both superseded by this full-PUA audit.
- **Methodological note (preserved for future audits):** `ls | grep ^uniE` is **not** a valid PUA audit method. Glyphs at PUA codepoints can have names like `quotedbl.old`, `k.noloop`, `afii10066.serbian`, `colon_colon.liga`, `bar_bar_greater.liga`. Counts MUST be derived from the `Encoding:` field in each `.glyph` file, across the **entire** PUA range (U+E000–U+F8FF), not just U+E0xx.
- **Severity:** Critical. Foundation of the entire collision policy is based on wrong numbers.

### F-2. "Additive by contract" wording factually wrong (FR-3.1)

- **Requirement (current PRD):** "It is additive by contract — it never replaces native glyphs."
- **Issue:** Nerd Fonts Patcher DOES overwrite existing glyphs at codepoints where its icon set collides with source font PUA. The 11 codepoints at U+E000–E00A (the range where the Pomicons icon set is believed to live — **hypothesis, pending pinned v3.5.0 audit, see O-3**) are prime collision candidates — several are populated in Fantasque masters (`quotedbl.old`, `k.noloop`, `afii10066.serbian`, etc.). Saying "never replaces" is wrong; patcher replaces **at the allowlist**, not universally. (Planned behavior post-implementation; see §0.)
- **Severity:** Critical. Type Designer reading PRD will reject on first review.

### F-3. "Vertical metrics unchanged" contradicts Patcher behavior (FR-9.1)

- **Requirement (current PRD):** "vertical metrics unchanged from the base weight"
- **Issue:** Nerd Fonts Patcher is documented (in upstream Nerd Fonts repo) to normalize vertical metrics (ascent/descent/lineGap) during patching. A literal "unchanged" gate will always fail for any successful Nerd Font Flavor build. (Note: the patcher behavior itself is not independently re-verified in this report; it is asserted based on the upstream Nerd Fonts documentation as cited in the discovery draft. **Pinned source citation pending in Spec phase, see O-4.**)
- **Severity:** Critical. Gate is impossible to satisfy under documented patcher behavior.

### F-4. Collision report conflates allowlist with effective overwrite; gate logic wrong (FR-4.3, SM-T1)

- **Requirement (current PRD):** "collision report confirms zero drift from the 15-codepoint baseline"
- **Issue:** Current framing uses a single "15-codepoint baseline" for all weights. This conflates five distinct concepts:
  1. **SourcePopulated(weight)** — full PUA inventory of codepoints populated in the source font master (69/69/75/72 per full-PUA Encoding audit; per-weight, static, derived from master source).
  2. **AuthorizedOverwriteAllowlist(weight)** — the policy-defined set of codepoints the patcher is authorized to overwrite. **Default = SourcePopulated(weight)**; MAY be narrowed in Spec phase after the pinned icon audit (e.g., if the team decides the ligature range U+E100–E12C must never be overwritten, the allowlist can exclude it). The gate binds against this set, not against a range claim.
  3. **PinnedIconInventory** — PUA codepoints where the pinned Nerd Fonts v3.5.0 distribution has icons (TBD — pending Spec-phase audit of pinned v3.5.0 distribution, O-3).
  4. **ExpectedOverwrite(weight)** = `SourcePopulated(weight) ∩ PinnedIconInventory` — the predicted set of codepoints the patcher is expected to overwrite (informational; computed at build time from the pinned inventory).
  5. **ObservedOverwrite(weight, build)** — the actual set of codepoints whose glyph changed in this build's patched font (per-build, derived from the diff between Base TTF and Patched TTF).
- **Correct drift gate:** `ObservedOverwrite(weight, build) ⊆ AuthorizedOverwriteAllowlist(weight)`. Equivalently, `ObservedOverwrite \ AuthorizedOverwriteAllowlist = ∅`. ExpectedOverwrite is reported for comparison but is NOT the gate.
- **Why the original `Effective_Overwrite = Overwritten ∩ Allowlist` formulation is wrong:** that formula computes a subset of overwrites that ARE in the allowlist; it does not detect overwrites that are OUTSIDE the allowlist. It masks drift instead of detecting it.
- **Why the allowlist must be full-PUA, not E0xx-only:** SourcePopulated includes the 45-codepoint ligature range U+E100–E12C. A gate bound to an E0xx-only inventory would flag a legitimate overwrite at U+E100 as drift — a false positive — or, worse, the implementation would trim the allowlist silently. The gate must bind against the full inventory (or an explicitly narrowed AuthorizedOverwriteAllowlist).
- **Severity:** Critical. Gate logic is wrong; the report cannot detect drift correctly as written.

### F-5. Box Drawing rationale factually wrong (Discovery Draft line 56)

- **Requirement (current Discovery):** "Box Drawing (160/160 coverage) — Patcher skips Box Drawing when the font already has full coverage"
- **Issue:** Encoding audit shows Regular master has 112 codepoints in U+25xx (not 160). The "160/160" coverage claim is wrong. More importantly, the rationale is wrong: the patcher does not overwrite Box Drawing because Nerd Fonts v3.5.0 has **zero icons in U+2500–259F** (all Nerd Font icons live in PUA at U+E0xx and above — hypothesis per upstream convention, pending O-3), regardless of source coverage. The conclusion (no overwrite in Box Drawing) is correct; the reasoning is wrong.
- **Severity:** Material. Affects reviewer's understanding of why Box Drawing is safe; should be corrected for documentation accuracy.

### F-6. "Always-on" framing ambiguous (FR-1.3, §1.1)

- **Requirement (current PRD §1.1):** "Flavor activation is always-on — the Nerd Font Flavor is produced by every build that runs the multi-weight pipeline"
- **Issue:** Read literally, "every build" could imply every Custom Build, including single-weight mode (`enable_multi_weight = false`). The actual condition is "every multi-weight build" — and the parent PRD's `enable_multi_weight` defaults to `false` in `custom-build.yml` (line 45-46) and `config.schema.json` (line 28-30). The conditional must be explicit to prevent user-expectation mismatch. (Also note: even multi-weight builds do NOT run the patcher today — see §0; this FR describes post-implementation behavior.)
- **Severity:** Material. Affects README/release notes; could lead to issue tracker noise.

### F-7. "Pre-patch" terminology ambiguous (FR-9.3)

- **Requirement (current PRD FR-9.3):** "A validation gate MUST compare the patched flavor with its pre-patch inputs"
- **Issue:** "Pre-patch inputs" is ambiguous — could mean (a) Base TTF (input to patcher), (b) Patched TTF before hinting, (c) Patched TTF before webfont conversion. Two distinct comparisons are actually needed: (a) collision report (Patched TTF vs Base TTF) and (b) webfont integrity (Patched TTF vs hinted TTF vs WOFF/WOFF2). Conflating them prevents independent gate debug.
- **Severity:** Material. Implementation ambiguity in Spec phase.

---

## 2. Resolved Items & Agreements

### R-1. Per-weight PUA allowlist: SourcePopulated counts (full-PUA, Encoding-verified)

- **Agreement (from user BLOCKER advisories + this review's full-PUA Encoding audit):** Per-weight SourcePopulated PUA counts (U+E000–U+F8FF) are **Regular 69, Bold 69, Italic 75, BoldItalic 72**, with union **75 codepoints** across all masters.
- **Composition of union 75 (verified by full-PUA Encoding audit):**
  - U+E000–E00A: 11 codepoints (range where the Pomicons icon set is *believed* to live — **hypothesis, pending pinned v3.5.0 audit, see O-3**; per-master populated: Regular 8 [E000–E007], Bold 6 [E000–E002, E005–E007], Italic 11, BoldItalic 11)
  - U+E035–E039: 5 codepoints (ligature prefixes; note E03A–E03B are unpopulated gaps)
  - U+E03C–E03F: 4 codepoints (ligature suffixes)
  - U+E0A0–E0A2: 3 codepoints (native Powerline symbols — left/right separator family)
  - U+E0B0–E0B3: 4 codepoints (native Powerline symbols — branch/flame family)
  - U+E0E2–E0E4: 3 codepoints (per-master extensions: Bold has E0E3+E0E4, Italic has E0E2+E0E3+E0E4, Regular/BoldItalic have none)
  - U+E100–E12C: 45 codepoints (programming ligatures, e.g., `bar_bar_greater.liga`, `less_tilde.liga`; populated in ALL four masters; Discovery Draft's "safe, no icon set in this range" is **hypothesis, pending O-3**)
- **Arithmetic check:** 11 + 5 + 4 + 3 + 4 + 3 + 45 = 75 (verified via Python set-union). Earlier chat drafts of "30" (E0xx-only) and "35" (arithmetic error) are superseded by this full-PUA audit.
- **Methodology note:** Counts derived from `Encoding:` field inspection in each `.glyph` file, NOT from filename glob. Glyphs at PUA codepoints can have names like `quotedbl.old`, `k.noloop`, `afii10066.serbian`, `colon_colon.liga`, `bar_bar_greater.liga`, etc. The audit MUST cover the entire PUA range (U+E000–U+F8FF).

### R-2. Nerd Font naming convention validated

- **Agreement:** Nerd Fonts ecosystem convention applies `Mono` / `Propo` suffix only when source font has BOTH variants. Fantasque Sans Mono is monospace-only, so the family name `Fantasque Sans Mono Nerd Font` (no `Mono` suffix) and file naming `FantasqueSansMonoNerdFont-{Weight}.{ext}` are **correct** per upstream Nerd Fonts convention. No change required to FR-5.3.
- **Rationale:** Matches JetBrains Mono Nerd Font, Fira Code Nerd Font, and other monospace-only sources in the Nerd Fonts repository.

### R-3. Patcher default policy (no `--careful`)

- **Agreement:** Nerd Fonts Patcher default behavior (overwrite on collision) is correct. The `--careful` flag would skip overwrites entirely, contradicting the PRD's documented overwrite intent. Drift detection relies on default policy plus the collision report gate.
- **Implementation note:** Patcher's collision policy is the **default**; `--careful` is NOT used. (Patcher CLI flag behavior per upstream Nerd Fonts Patcher documentation — pinned source citation pending, see O-4. Planned behavior post-implementation; see §0.)

---

## 3. Assumed / Auto-Resolved / Out of Scope

### Auto-Resolved (Heavy Lifting by Clarification Analyst — verified against available source)

| #    | Scenario                      | Handling                                                                                                                                                                                                          | Rationale                                                                                                                                                                                                             |
| ---- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A-3  | FR-3.1 additive wording       | `[Assumed / Auto-Resolved]` — reframe to "additive on native, overwrite on allowlist"                                                                                                                             | Factual correctness; eliminates reviewer rejection. Source: master source Encoding audit + Discovery Draft collision-surface claim.                                                                                   |
| A-4  | FR-9.3 pre-patch ambiguity    | `[Assumed / Auto-Resolved]` — split into FR-9.3a (collision report) and FR-9.3b (webfont integrity)                                                                                                               | Separates concerns; enables independent gate debug. Source: existing FR structure in parent PRD.                                                                                                                      |
| A-5  | FR-4 collision policy framing | `[Assumed / Auto-Resolved]` — define SourcePopulated (full PUA), AuthorizedOverwriteAllowlist, PinnedIconInventory, ExpectedOverwrite, ObservedOverwrite; gate `ObservedOverwrite ⊆ AuthorizedOverwriteAllowlist` | Logically correct drift detection; separates source state from patcher intent and from policy. Source: logical derivation from gate semantics.                                                                        |
| A-6  | Box Drawing rationale         | `[Assumed / Auto-Resolved]` — correct to "Nerd Fonts v3.5.0 has no icons in U+2500–259F (hypothesis pending O-3)"                                                                                                 | Factual correction of the coverage claim (112/160, not 160/160); conclusion unchanged. Source: master source Encoding audit + Nerd Fonts icon-set convention.                                                         |
| A-7  | Always-on conditional         | `[Assumed / Auto-Resolved]` — explicit `enable_multi_weight = true` conditional in FR-1.3 and §1.1                                                                                                                | Eliminates user-expectation ambiguity. Source: `custom-build.yml` line 45-46 and `config.schema.json` line 28-30.                                                                                                     |
| A-8  | Nerd Font naming              | `[Assumed / Auto-Resolved]` — no change (validated as correct)                                                                                                                                                    | Matches upstream Nerd Fonts convention. Source: Nerd Fonts repo naming convention for monospace-only sources.                                                                                                         |
| A-9  | Patcher policy                | `[Assumed / Auto-Resolved]` — default policy, no `--careful`                                                                                                                                                      | Aligns with documented overwrite intent. Source: Nerd Fonts Patcher CLI documentation (default vs `--careful`; pinned source citation pending, see O-4).                                                              |
| A-10 | ADR-0004 candidate            | `[Assumed / Auto-Resolved]` — create ADR-0004 in Spec phase                                                                                                                                                       | Triple Gate: hard to reverse (Docker stage structural), surprising without context (type designer wouldn't expect Patcher stage), real trade-off (Docker vs host-runner). Source: ADR-FORMAT.md triple-gate criteria. |
| A-11 | VQR scope                     | `[Assumed / Auto-Resolved]` — extend VQR with "Fallback Disclosure" section                                                                                                                                       | Single source of truth; avoids document fragmentation. Source: existing `docs/audit/visual-quality-rubric.md` structure.                                                                                              |

### Out of Scope (defer to Spec phase — pinned source required)

| #   | Scenario                                                                                                                                                                                                             | Handling                                                      | Rationale                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| O-1 | 427 split (374 + 53) verification                                                                                                                                                                                    | `[Assumed / Out of Scope]` — defer to Spec phase              | `tracking.json` has no per-type breakdown; re-running `detect_incompatibility.py` with type classifier is Spec-phase work. Pinned source: `Sources/Harmonized/tracking.json` (current state, 427 entries, all `needs_harmonization`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| O-2 | 300-minute build duration feasibility                                                                                                                                                                                | `[Assumed / Out of Scope]` — defer benchmark to Spec phase    | 60-min headroom is realistic but requires real-runner benchmark; FR-8.4 300-min cap is the gate.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| O-3 | **Nerd Fonts v3.5.0 icon inventory audit**                                                                                                                                                                           | `[Assumed / Out of Scope]` — defer to Spec phase              | **PinnedIconInventory** is a pinned build input. Spec phase must: (a) download official v3.5.0 distribution from upstream Nerd Fonts repo; (b) verify SHA-256 checksum; (c) enumerate PUA codepoints in the distribution's icon `.glyph` files; (d) compute `ExpectedOverwrite(weight) = SourcePopulated(weight) ∩ PinnedIconInventory` per weight. **Until this audit is performed with a pinned source, no specific icon-set enumeration is asserted in this report.** The 12-icon-set list cited in the chat discussion (Pomicons, Powerline Symbols, Seti-UI, Devicons, Font Awesome Free, Material Design Icons, Weather Icons, Octicons, Font Logos, Codicons, IEC Power Symbols, Nerd Fonts custom additions) is **not asserted as verified** in this report; it must be re-derived from the pinned v3.5.0 distribution. Likewise, the Discovery Draft's "U+E100–E12C is safe (no icon set in this range)" claim is **hypothesis, not verified** — the audit must confirm whether any pinned v3.5.0 icon lands in U+E100–E12C. |
| O-4 | Patcher metric-normalization behavior citation                                                                                                                                                                       | `[Assumed / Out of Scope]` — defer to Spec phase              | The claim "Nerd Fonts Patcher normalizes vertical metrics (ascent/descent/lineGap)" is asserted based on the discovery draft's reference to the upstream Nerd Fonts Patcher behavior. **The pinned source citation (upstream Nerd Fonts Patcher v3.5.0 source code or documentation) is not included in this report.** Spec phase must: (a) checkout pinned v3.5.0 patcher source; (b) verify the metric normalization claim against the source; (c) cite the specific code path. Until then, FR-9.1 should be re-stated as "vertical metrics MUST be documented in the collision report for audit" without asserting normalization as the reason.                                                                                                                                                                                                                                                                                                                                                                                    |
| O-5 | Manifest schema for Nerd Font Flavor                                                                                                                                                                                 | `[Assumed / Out of Scope]` — defer to Spec phase              | PRD only requires `flavor` field, per-file checksum, toolchain_versions; detailed schema is Spec decision.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| O-6 | Glossary entries (PUA codepoint, Powerline symbols native, Stylistic alternates, Per-master allowlist, SourcePopulated / AuthorizedOverwriteAllowlist / PinnedIconInventory / ExpectedOverwrite / ObservedOverwrite) | `[Assumed / Out of Scope]` — lazy creation per CONTEXT-FORMAT | Per `CONTEXT-FORMAT.md`, glossary entries created when first canonical term is resolved, not pre-populated.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |

---

## 4. Authoring Instructions for PRD Authoring Agent

These are the specific edits required to bring the PRD from current 45/100 to projected 92/100. The PRD Authoring Agent (`/sdlc-draft-prd`) should apply these as targeted, surgical edits — NOT as full file replacement.

### Edit 1 — FR-4 intro (PRD line 130)

**Replace:**

> "The verified collision surface is exactly **15 PUA codepoints**: U+E000–E007 (Fantasque stylistic alternates), U+E0A0–E0A2 and U+E0B0–E0B3 (native Powerline symbols). No native letter is ever touched."

**With:**

> "The **per-weight PUA SourcePopulated inventory** (populated codepoints in master source, verified by Encoding inspection of `.glyph` files across the full PUA range U+E000–U+F8FF) is: Regular 69, Bold 69, Italic 75, BoldItalic 72 codepoints; union across all masters = 75 codepoints (composition: U+E000–E00A [11] + U+E035–E039 [5] + U+E03C–E03F [4] + U+E0A0–E0A2 [3] + U+E0B0–E0B3 [4] + U+E0E2–E0E4 [3] + U+E100–E12C [45]). The inventory comprises: (a) U+E000–E00A (stylistic alternates, `k.noloop` family, Serbian alternate ligatures — content varies per master; the icon set believed to collide here is Pomicons — **hypothesis pending the pinned v3.5.0 audit**), (b) U+E035–E039 + U+E03C–E03F programming ligature prefixes/suffixes, (c) U+E0A0–E0A2 + U+E0B0–E0B3 native Powerline symbols, (d) U+E0E2–E0E4 per-master extensions (Bold +E0E3,E0E4; Italic +E0E2,E0E3,E0E4; Regular/BoldItalic none), (e) U+E100–E12C programming ligatures (45 codepoints, all masters; Discovery's 'no icon set here' is **hypothesis pending the pinned audit**).
>
> The **AuthorizedOverwriteAllowlist(weight)** is the policy set the patcher is authorized to overwrite; **default = SourcePopulated(weight)**, and MAY be narrowed in Spec phase (e.g., excluding U+E100–E12C if the team so decides). The **drift gate** is `ObservedOverwrite(weight, build) ⊆ AuthorizedOverwriteAllowlist(weight)`. **ExpectedOverwrite(weight) = SourcePopulated(weight) ∩ PinnedIconInventory** is the predicted set, reported for comparison (informational; PinnedIconInventory is the pinned Nerd Fonts v3.5.0 icon codepoint set, audited in Spec phase per O-3). Codepoints outside the allowlist MUST NOT be overwritten; any such overwrite is drift and fails the build gate."

### Edit 2 — FR-3.1 (PRD line 121)

**Replace:**

> "It is additive by contract — it never replaces native glyphs."

**With:**

> "Patcher is **additive on all native Latin, Greek, Cyrillic, digit, and punctuation glyphs** (never removes, alters, or replaces) and **overwrites only at the per-weight PUA allowlist** (Regular 69, Bold 69, Italic 75, BoldItalic 72 codepoints, union 75; allowlist default = full SourcePopulated, see FR-4) in the Nerd Font Flavor only. Overwrites outside the allowlist constitute drift and fail the build gate (FR-4.3). Added codepoints (PinnedIconInventory codepoints where SourcePopulated is empty) are informational, not a gate. Icon-set attribution for the collision ranges is pending the pinned v3.5.0 audit (Spec phase, O-3); no icon-set-to-range mapping in this PRD is asserted as verified."

### Edit 3 — FR-4.3 (PRD line 134)

**Replace:**

> "A collision report MUST be generated per weight, comparing the patched flavor against its pre-patch input and listing every codepoint whose glyph changed. The report MUST confirm zero drift from the 15-codepoint baseline; any drift MUST block the release (gate)."

**With:**

> "A collision report MUST be generated per weight, comparing Patched TTF (output of Nerd Fonts Patcher) against Base TTF (input to patcher). The report MUST record, per weight:
>
> 1. **ObservedOverwrite** — the actual set of codepoints whose glyph changed in this build (derived from the diff between Base TTF and Patched TTF).
> 2. **ExpectedOverwrite** — `SourcePopulated(weight) ∩ PinnedIconInventory`, computed at build time from the pinned Nerd Fonts v3.5.0 icon inventory (informational, for comparison).
> 3. **Added** — codepoints where PinnedIconInventory has an icon but SourcePopulated is empty (patcher added new glyph; informational only).
> 4. **Drift gate** — `ObservedOverwrite(weight, build) ⊆ AuthorizedOverwriteAllowlist(weight)` MUST hold (equivalently, `ObservedOverwrite \ AuthorizedOverwriteAllowlist = ∅`). Any drift blocks the release."

### Edit 4 — FR-9.1 (PRD line 170)

**Replace:**

> "vertical metrics unchanged from the base weight"

**With:**

> "vertical metrics (ascent, descent, lineGap) MUST be documented in the collision report for audit. The gate does not assert equivalence with the base weight; it asserts that the actual values are recorded for post-build inspection. (Pinned source citation for the patcher's metric behavior is pending in Spec phase per O-4; until cited, this gate is an audit gate, not a drift gate.)"

### Edit 5 — SM-T1 (PRD line 219)

**Replace:**

> "Zero drift across every released weight — each collision report lists exactly the verified 15 PUA codepoints (U+E000–E007, U+E0A0–E0A2, U+E0B0–E0B3) and no others (FR-4.3)."

**With:**

> "Zero drift across every released weight — every collision report verifies that `ObservedOverwrite(weight, build) ⊆ AuthorizedOverwriteAllowlist(weight)` (equivalently, `ObservedOverwrite \ AuthorizedOverwriteAllowlist = ∅`). Per-weight SourcePopulated inventories (full PUA U+E000–U+F8FF): Regular 69, Bold 69, Italic 75, BoldItalic 72 (union 75 across all masters); AuthorizedOverwriteAllowlist defaults to SourcePopulated and MAY be narrowed in Spec phase (FR-4). ExpectedOverwrite (= `SourcePopulated ∩ PinnedIconInventory`) is reported for comparison but is NOT the gate (FR-4.3)."

### Edit 6 — FR-1.3 (PRD §1.3) and §1.1 product summary

**Add explicit conditional language:**

In §1.1 (product summary), add:

> "**Activation scope:** The Nerd Font Flavor is produced automatically **only when `enable_multi_weight = true`** (default `false` per `custom-build.yml` line 45-46 and `config.schema.json` line 28-30). Builds with multi-weight disabled produce only the Base Flavor; no Nerd Font artifacts, no patcher execution (FR-7.1)."

In FR-1.3, replace "always-on within the multi-weight pipeline" with:

> "Flavor activation is **automatic within the multi-weight pipeline** (conditional on `enable_multi_weight = true`): every multi-weight-enabled build MUST produce both flavors, with no new `workflow_dispatch` input. Builds with `enable_multi_weight = false` MUST NOT produce Nerd Font artifacts and MUST retain today's exact behavior (FR-7.1, SM-T4)."

### Edit 7 — FR-9.3 split (PRD line 172)

**Replace:**

> "A validation gate MUST compare the patched flavor with its pre-patch inputs and record codepoint collisions, changes to native glyphs, vertical metrics, advance widths, family naming, and output completeness — this record accompanies the release (see FR-4.3)."

**With:**

> "**FR-9.3a (Collision report):** Validation gate MUST compare Patched TTF (output of Nerd Fonts Patcher) against Base TTF (input to patcher) per weight, and record: (i) ObservedOverwrite (codepoint collisions), (ii) changes to native glyphs (must be zero), (iii) family naming (must match FR-5.3), (iv) output completeness (every released weight in every format). Record accompanies the release. Drift gate per FR-4.3.
>
> **FR-9.3b (Webfont integrity):** Validation gate MUST compare Hinted TTF (output of ttfautohint) against Patched TTF pre-hinting and against WOFF/WOFF2 outputs, to verify hinting fidelity and compression losslessness. Record accompanies the release."

### Edit 8 — Discovery Draft (Rev 4)

**Collision Surface Audit table (Discovery line 65-79):** Expand with per-master column and full-PUA rows. Add:
- Per-master SourcePopulated rows: Regular 69, Bold 69, Italic 75, BoldItalic 72; union 75.
- Per-master extension rows: Bold +E0E3 (57571), +E0E4 (57572); Italic +E0E2 (57570), +E0E3 (57571), +E0E4 (57572); BoldItalic no extensions beyond the common set.
- U+E100–E12C row: 45 codepoints populated in ALL masters; Discovery's "No icon set in this range ✅ Safe" must be re-labeled **"hypothesis — pending pinned v3.5.0 audit (O-3)"**.
- Methodology note: audit spans the full PUA (U+E000–U+F8FF) via the `Encoding:` field, not filename glob.

**Box Drawing rationale (Discovery line 56):** Replace the 160/160 coverage claim with:

> "Box Drawing — Nerd Fonts v3.5.0 is believed to have no icons in U+2500–259F (all Nerd Font icons live in PUA at U+E0xx and above — hypothesis pending the pinned v3.5.0 audit, O-3), so the patcher is expected to add nothing in Box Drawing regardless of source coverage. Master Regular currently has 112 codepoints in U+25xx (not 160/160), but coverage is irrelevant because the patcher has no Box Drawing icons to add. Collision report still verifies zero overwrite in U+2500–259F as a safety check for future icon-set drift."

**PinnedIconInventory reference:** Add a section noting that the pinned Nerd Fonts v3.5.0 icon inventory is to be audited in Spec phase (O-3) and forms the `PinnedIconInventory` set used to compute `ExpectedOverwrite`; no icon-set-to-range mapping is asserted as verified until then.

---

## 5. Next Steps

1. **PRD Authoring Agent** (`/sdlc-draft-prd`) must apply Edits 1–7 above to `docs/prd-20260806-1401-multi-weight-nerd-font-patching.md` as targeted surgical edits (NOT full file replacement).
2. **Discovery Draft** must be revised to Rev 4 per Edit 8.
3. **Spec phase** (`/sdlc-define-specs`) must:
   - **O-3 (CRITICAL):** Audit pinned Nerd Fonts v3.5.0 distribution. Download the official v3.5.0 release, verify SHA-256 checksum against the pinned value, enumerate PUA codepoints in the distribution's icon `.glyph` files, and produce the `PinnedIconInventory` set. Compute `ExpectedOverwrite(weight) = SourcePopulated(weight) ∩ PinnedIconInventory` per weight. Confirm or refute whether any pinned icon lands in U+E100–E12C and in U+2500–259F.
   - **O-4 (CRITICAL):** Cite pinned Nerd Fonts Patcher v3.5.0 source for metric normalization behavior. Checkout pinned v3.5.0 patcher source, identify the specific code path that modifies vertical metrics, and document the exact transformation.
   - Finalize `AuthorizedOverwriteAllowlist(weight)` policy per weight (default = SourcePopulated; decide explicitly whether U+E100–E12C ligatures may ever be overwritten).
   - Implement collision report gate per FR-9.3a (with `ObservedOverwrite ⊆ AuthorizedOverwriteAllowlist` as the gate).
   - Implement webfont integrity gate per FR-9.3b.
   - Create ADR-0004 documenting Patcher Docker stage placement (Triple Gate validated).
   - Extend VQR with "Fallback Disclosure" section.
4. **Domain Glossary** (`CONTEXT.md`): Lazy update for new terms (PUA codepoint, Powerline symbols native, Stylistic alternates, Per-master allowlist, SourcePopulated / AuthorizedOverwriteAllowlist / PinnedIconInventory / ExpectedOverwrite / ObservedOverwrite) when first used in implementation, per CONTEXT-FORMAT.md.
5. **Re-audit**: After PRD Authoring Agent applies Edits 1–7, re-run `/sdlc-clarify-reqs` for Review Iteration 2. Final readiness after re-audit (with O-3 and O-4 resolved by pinned source) should be 80+ to proceed to Spec implementation.

---

## 6. Verification Methodology Note (for future audits)

A critical methodological lesson from this review: **font PUA codepoint counts must be derived from the `Encoding:` field in `.glyph` files — across the ENTIRE PUA range (U+E000–U+F8FF) — not from filename glob patterns and not from a single PUA sub-range.** Glyphs at PUA codepoints can have arbitrary names (`quotedbl.old`, `k.noloop`, `afii10066.serbian`, `colon_colon.liga`, `bar_bar_greater.liga`, etc.). A `ls | grep ^uniE` audit undercounts by 5x or more (this review: E0xx-only audit found 24/24/30/27; full-PUA audit found 69/69/75/72). Correct audit pattern:

```python
import re
from pathlib import Path

ENCODING_RE = re.compile(r"^Encoding:\s+(\d+)")
PUA = (0xE000, 0xF8FF)  # entire Private Use Area

for f in Path(master_dir).glob("*.glyph"):
    with open(f, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = ENCODING_RE.match(line)
            if m:
                enc = int(m.group(1))
                if PUA[0] <= enc <= PUA[1]:
                    # populated PUA codepoint
                break
```

This lesson applies equally to the Nerd Fonts v3.5.0 icon distribution audit (O-3) in Spec phase: its `PinnedIconInventory` must also be derived from `Encoding:` fields of the pinned distribution's glyph files, across the full PUA.

---

*End of Clarification Report — Review Iteration 1 (corrected) — 2026-08-06*

*Note: Section "User Decision Prompt" intentionally omitted — per the Clarification Report template, the prompt is only permitted at Readiness Score >= 80 or review iteration >= 3; this report is at 45/100 on iteration 1, and the user has already commanded the report be saved.*
