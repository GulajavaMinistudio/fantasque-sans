> [!SUCCESS]
> **AUDIT REPORT IMPLEMENTATION STATUS: ALL FINDINGS RESOLVED**
> This Clarification Report's findings have been fully implemented across both downstream documents:
>
> - **`docs/prd-20260813-0921-medium-font-weight.md` (v1.2) — PRD remediation:**
>   - T-1 (FR-04 & GH-007 AC3): four variant permutations enumerated (`Normal`, `LargeLineHeight`, `NoLoopK`, `LargeLineHeight-NoLoopK`)
>   - T-3 (§8.1): `Variation(name)` claim corrected to align with §8.3 (the script writes SFNT metadata, not `Variation`)
> - **`spec/spec-design-medium-weight.md` (v1.2) — Spec remediation:**
>   - T-1 (AC-003): four variant permutations enumerated
>   - T-2 (§8): `counter_type="Retain"` applied (capitalized per FontForge docs) to preserve inner counters per PRD GH-006
>   - T-4 (§8): italic detection upgraded to `os.path.basename(input_sfdir).startswith("FantasqueSansMono-Italic")`; italic preservation via non-modification of `italicangle` and `fsSelection` bit now explicit
>
> **Overall:** All 4 findings (T-1, T-2, T-3, T-4) are resolved in their respective target documents. Cross-doc traceability is intact.
> **Next step:** Proceed to `/sdlc-plan-tasks` in a new chat session for implementation planning.

> [!SUCCESS]
> **PRD REMEDIATION STATUS: RESOLVED** (Review Iteration 2 — PRD scope only)
> The PRD findings from Review Iteration 2 have been remediated by Product Manager PRD.
>
> - **Projected PRD Readiness Score:** 95/100 (Completeness 36/40, Clarity 29/30, Alignment 30/30; no Critical Flaw Veto)
> - **Resolved PRD findings:** T-1 (FR-04 and GH-007 AC3 — four variant permutations enumerated), T-3 (§8.1 — corrected `Variation(name)` claim)
> - **Subsequent remediation (2026-08-13):** Spec findings T-1, T-2, and T-4 (targeting `spec/spec-design-medium-weight.md`) have since been resolved in the Specification remediation block below. This bullet is retained as a historical record of the PRD remediation scope boundary at the time of closure.

> [!SUCCESS]
> **PRD REMEDIATION STATUS: RESOLVED** (Review Iteration 1 — PRD scope)
> This audit report (Review Iteration 1) has been remediated by Product Manager PRD.
>
> - **Projected Readiness Score:** 94/100

> [!SUCCESS]
> **REMEDIATION STATUS: RESOLVED**
> This audit report's Review Iteration 2 (Technical Specification) has been remediated by Specification Architect.
>
> - **Projected Readiness Score:** 96/100
> - **Remediated Findings:** T-1 (variant permutations enumeration), T-2 (`counter_type="Retain"`), T-4 (italic detection and preservation in §8 code sample).
> - **T-3 (PRD §8.1 `Variation(name)` residual) is out of scope for Spec remediation** — was fixed by the PRD author on 2026-08-13 (see PRD REMEDIATION STATUS block above).

# 🔍 Clarification Report [Review Iteration 1]

**Readiness Score:** 90/100
**Status:** Good Enough

**Score Breakdown:**

- **Completeness (max 40):** 36 - Semua 22 section template terisi. 9 FR dan 8 user stories dengan AC SMART. FR-03 (commit sources) tidak memiliki dedicated story — minor, bersifat operational step.
- **Clarity (max 30):** 26 - 7 ambiguitas mayor ter-resolusi (advance width, weight class, stroke expansion, idempotency, Variation naming, NoCalt, visual quality). Sisa detail teknis (exact ChangeWeight params) didelegasikan ke Spec secara tepat.
- **Alignment (max 30):** 28 - Selaras dengan discovery draft setelah koreksi. Advance width error (warisan dari discovery draft) terkoreksi. Weight 500 dikonfirmasi. Scope Medium+MediumItalic sesuai. Ketiga handoff notes dari discovery draft Section 5 ter-address.
- **Critical Flaw Veto:** No - None

---

## 1. 🚨 Critical Findings (Blockers)

_List any remaining critical ambiguities or blocking issues that must be fixed to reach the 80-point threshold. If none, write "None"._

- None

## 2. 🧩 Resolved Items & Agreements

_List the ambiguities and edge cases that were successfully resolved during this session._

- **Requirement:** "1200 em units" for advance width
  - **Resolution:** Dikoreksi menjadi **1060 em units** di seluruh dokumen PRD (FR-01, FR-04, GH-001 AC2, GH-002 AC3, Section 5.3, Section 8.3) berdasarkan fakta aktual di codebase untuk menjaga konsistensi monospace grid.
- **Requirement:** OS/2 Weight Class "500/600"
  - **Resolution:** Diputuskan secara definitif menggunakan OS/2 weight **500** (Medium). Sesuai dengan spesifikasi OpenType dan nama SubFamily.
- **Requirement:** "stroke expansion in the range of +30 to +40 em-units"
  - **Resolution:** Dihapus sebagai constraint teknis di PRD dan diubah menjadi deskripsi behavioral: *"visually distinct weight between Regular and Bold"*, dengan catatan rentang +30 hingga +40 em-units dilampirkan sebagai *suggested starting point* untuk fase Technical Specification.
- **Requirement:** "The script SHALL be idempotent — running it multiple times with the same input produces byte-identical output."
  - **Resolution:** Diubah menjadi **"functionally idempotent"**. Geometri kontur dan metrics harus identik, namun perbedaan metadata non-fungsional (seperti timestamps) diperbolehkan.
- **Requirement:** "If it does not recognize 'Medium' as a valid subfamily, naming metadata will be incorrect." (Section 8.3)
  - **Resolution:** Kekhawatiran pada `Variation(name)` tidak akurat. Diganti menjadi peringatan bahwa script generasi harus memastikan metadata SFNT (`SubFamily = 'Medium'`) ditulis dengan benar pada `.sfdir` sumber sebelum di-commit.
- **Requirement:** Variant "NoCalt" disebutkan sejajar dengan variant directory di FR-04.
  - **Resolution:** Variant "NoCalt" dihapus dari FR-04 karena merupakan build flag boolean, bukan variant yang menghasilkan direktori output.
- **Requirement:** "visually legible" and "discernible inner counter spaces" di GH-006.
  - **Resolution:** Kriteria subjektif dipertahankan, namun ditambahkan Acceptance Criteria eksplisit untuk proses sign-off: *"Visual quality sign-off is approved when at least one maintainer confirms acceptance via PR review comment or approval."*

## 3. ⚠️ Assumed / Auto-Resolved / Out of Scope (The 20% we skip)

_List extreme edge cases, unknown details, or remaining questions that were automatically resolved by the AI's "Heavy Lifting" recommendation because the user chose to PROCEED._

- **Scenario / Question:** Apakah ada penambahan story khusus untuk proses commit (terkait FR-03) dan pengujian spesifik untuk patch Nerd Fonts (terkait FR-09)?
  - **Handling:** `[Assumed / Auto-Resolved]` - Hal ini dianggap sebagai minor tracking issue. Tindakan "commit" di-asumsikan tercakup dalam proses penyelesaian GH-001/GH-002, dan Nerd Fonts merupakan prioritas medium (P2) yang proses patching-nya sudah otomatis ditangani jika flag diaktifkan di Custom Build.

## 4. 📝 Next Steps

- The upstream document (PRD/Spec/Plan) MUST be updated with these resolutions (by the respective author agent) if the score is below 80. *(Note: Since the score is 90, you may choose to invoke `/sdlc-draft-prd` to apply these fixes for perfect alignment, or proceed directly to Spec if comfortable).*
- If new canonical business terms were agreed upon, update the Domain Glossary (`CONTEXT.md`). *(No new canonical terms needed).*
- If architectural decisions were made, document them as an ADR under `docs/adr/`. *(No ADR required for these resolutions).*

---

# 🔍 Clarification Report [Review Iteration 2] — Technical Specification

**Target Document:** `spec/spec-design-medium-weight.md` (v1.1)
**Upstream Document:** `docs/prd-20260813-0921-medium-font-weight.md` (v1.1)

**Readiness Score:** 89/100
**Status:** Good Enough (≥ 80)

**Score Breakdown:**

- **Completeness (max 40):** 36 — All 9 PRD FRs are covered by the spec's REQ/CON/GUD/AC (FR-01→REQ-01/02 + CON-01..06 + GUD-01; FR-02→REQ-03; FR-03→§7; FR-04→AC-003; FR-05→AC-004; FR-06→AC-005/006; FR-07→§4.2; FR-08→§6/§13; FR-09→§13). Gaps: FR-03, FR-07, FR-08, and FR-09 have no dedicated numbered AC; the SVG output format is omitted from AC-003/AC-005.
- **Clarity (max 30):** 26 — Mostly implementable. The `counter_type="squish"` choice is unexplained (potentially conflicts with the counter-legibility AC); the "variant permutations (Normal, NoLoopK, LargeLineHeight)" enumeration is incomplete versus actual build output; the §8 italic-detection heuristic is not fully specified.
- **Alignment (max 30):** 27 — Strong traceability to the PRD. Advance width 1060, weight 500, functional idempotency, italic preservation, and zero-touch are all verified consistent. Residual: the PRD §8.1 `Variation(name)` claim is stale (the spec correctly follows §8.3); the variant-permutation enumeration diverges from actual code (inherited from the PRD).
- **Critical Flaw Veto:** No — None.

---

## 1. 🚨 Critical Findings (Blockers)

- None. No blocking ambiguity; the Medium variants build correctly regardless of the findings below.

## 2. 🧩 Resolved Items & Agreements (Traceability Verified Against Codebase)

- **Advance width 1060:** PRD FR-01/GH-001 ↔ Spec CON-02 — consistent. (Codebase: 1042 Regular glyphs at width 1060, verified in a prior session.)
- **OS/2 weight 500:** PRD FR-01/GH-001 ↔ Spec CON-04 — consistent.
- **`removeOverlap()` + `simplify()`:** PRD FR-01 ↔ Spec CON-03 — consistent.
- **Functional idempotency:** PRD FR-01 ↔ Spec CON-05 — consistent (contour geometry + metrics identical; non-functional metadata may differ).
- **Italic preservation:** PRD FR-02/GH-002 ↔ Spec REQ-03/§4.2 — consistent. (Codebase: `Sources/FantasqueSansMono-Italic.sfdir` has `ItalicAngle: -11` and `StyleMap: 0x0001` = italic flag set; Regular has `ItalicAngle: 0`.)
- **SFNT naming:** PRD FR-07/GH-004 ↔ Spec §4.2 — consistent (`Family`, `SubFamily`, `Fullname`, `PostScriptName`).
- **CSS declaration:** PRD FR-05/GH-005 ↔ Spec AC-004 — consistent. (Codebase: `generate-css-decl` reads `font.os2_weight` and `font.italicangle`; `italicangle != 0.0` → `font-style: italic`.)
- **Packaging:** PRD FR-06/GH-007 ↔ Spec AC-005 — consistent. (`zip-all-variants` iterates each variant directory.)
- **CI/CD zero-touch:** PRD FR-06/GH-008 ↔ Spec AC-006 — consistent.
- **validate-font:** PRD FR-08 ↔ Spec §6/§13 — consistent. (Codebase: `validate-font` has `exit 0` before `exit $error`; inspecting output for `Error in ...` is the effective signal — the §6 note is accurate.)
- **Nerd Font patching:** PRD FR-09 ↔ Spec §13 — consistent.
- **Zero-touch list:** PRD §7.3 ↔ Spec §1.1/§9 — consistent (Makefile, config.schema.json, configure.py, custom_build_driver.py must not be modified).
- **Stroke expansion +30..+40 (ref 34):** PRD FR-01 ↔ Spec GUD-01/§1.2 — consistent; 34 is within the PRD range.
- **`ChangeWeight` over `interpolateFonts()`:** PRD §8.3 ↔ Spec §10 — consistent (non-matching master topology).
- **`ChangeWeight` signature:** Spec §8 `font.changeWeight(34, "LCG", 0, 0, "squish")` matches the official signature `font.changeWeight(stroke_width, type, serif_height, serif_fuzz, counter_type)` — arity and values are valid (`type="LCG"` and `counter_type="squish"` are valid FontForge values).
- **`counter_type` selection (T-2):** Spec §8 used `counter_type="squish"` (counters shrink, no retention). **Resolved 2026-08-13:** user chose **`Retain`** — preserves inner counters, aligned with PRD GH-006 counter-legibility AC. The spec author must update §8 from `font.changeWeight(34, "LCG", 0, 0, "squish")` to `font.changeWeight(34, "LCG", 0, 0, "Retain")` (verify exact casing at implementation).

## 3. 🔎 Non-Blocking Findings (Recommended Before Plan)

- **T-1 — Incomplete "variant permutations" enumeration (PRD + Spec):** PRD FR-04, Spec AC-003, AC-007, and GH-007 AC3 state "(Normal, NoLoopK, LargeLineHeight)" = 3 permutations. In fact `build.py` registers 2 active options (`LargeLineHeight` via `conflicting(...)`, `NoLoopK`; `NoCalt` is commented out), producing **4** variant directories: `Normal`, `LargeLineHeight`, `NoLoopK`, and `LargeLineHeight-NoLoopK`. The Medium variants still build in all four (wildcard + automatic permutations), so this is not a functional blocker — but the AC enumeration is inaccurate. **Recommendation:** enumerate all four permutations (or "all 2^2 permutations of the active options") in FR-04/AC-003/AC-007.
- **T-2 — `counter_type` selection (RESOLVED):** Originally `squish` (counters shrink). Resolved to **`Retain`** — see §2.
- **T-3 — PRD §8.1 residual (PRD document, not a spec defect):** PRD §8.1 still states "`Variation(name)` in `fontbuilder.py` must correctly derive SFNT naming from the source directory basename". In fact `Variation(name)` appends a name to `familyname` (it does not derive SubFamily from the basename), and `build.py` does not call `Variation` at all. Spec §4.2 is correct (assigns metadata writing to the generation script), consistent with PRD §8.3 (already corrected). **Recommendation:** the PRD author corrects §8.1 to align with §8.3.
- **T-4 — §8 code sample vs REQ-03 (minor):** §8 detects italic via `is_italic = "Italic" in input_sfdir` (substring heuristic — would misclassify `BoldItalic` if ever passed) and does not demonstrate the `italicangle`/`StyleMap` preservation required by REQ-03/§4.2. Preservation-by-non-modification is valid (the script does not touch `StyleMap`), but the sample does not illustrate that step. **Recommendation:** clarify the italic handling in the sample.

## 4. ⚠️ Assumed / Auto-Resolved / Out of Scope

- **SVG output omission:** Spec AC-003/AC-005 do not mention SVG, whereas PRD FR-04 lists it and `build.py` `_build` emits `.svg`. `[Assumed / Auto-Resolved]` — SVG is still produced by the existing pipeline; the AC format enumeration can be aligned with the PRD wording.
- **`counter_type` casing:** FontForge docs write `Squish`/`Retain`/`Auto` (capitalized); Spec uses lowercase `squish`. `[Assumed / Auto-Resolved]` — verify during implementation; if case-sensitive, use the exact documented value.

## 5. 📝 Next Steps

- **Subsequent remediation (2026-08-13):** All 4 findings (T-1, T-2, T-3, T-4) have been remediated in their respective target documents — T-1, T-2, T-4 in `spec/spec-design-medium-weight.md` v1.2; T-3 in `docs/prd-20260813-0921-medium-font-weight.md` v1.2. See REMEDIATION STATUS blocks at the top of this file for details. The next SDLC phase is `/sdlc-plan-tasks` (implementation planning).
- No new canonical terms resolved → no `CONTEXT.md` update required.
- No new ADR required (the `ChangeWeight` vs `interpolateFonts` decision already exists in PRD §8.3/Spec §10; it is not a new hard-to-reverse decision).

---

> **Clarification Complete (Review Iteration 2):**
> Readiness Score 89/100 (at audit time, prior to remediation). All 4 findings (T-1, T-2, T-3, T-4) have since been remediated in PRD v1.2 and Spec v1.2 — see REMEDIATION STATUS blocks above for the final implementation state.
