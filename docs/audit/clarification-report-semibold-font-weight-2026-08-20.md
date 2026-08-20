<!-- markdownlint-disable -->

> [!SUCCESS]
> **REMEDIATION STATUS: RESOLVED**
> This audit report has been remediated by Product Manager PRD.
>
> - **Projected Readiness Score:** 100/100

> [!NOTE]
> **IMPLEMENTATION STATUS: IMPLEMENTED**
> All findings have been implemented in the target document.
>
> - **Implemented in:** `docs/prd-20260818-1636-semibold-font-weight.md` (v1.1, 2026-08-20)
> - **Implementation coverage:** all 4 Resolved Items and 7 Auto-Resolved items applied:
>   - Calibration rule + 45 em-unit floor + escalation path → FR-01, §5.3, §8.3, §9.2, GH-006 AC3/AC4
>   - FR-02 "clearly documented invocation" removed (single script, basename detection) → FR-02
>   - Zero-touch set + `generate-css-decl` (and `zip-all-variants` auto-discovery) → §2.3, §7.3, GH-003 AC3
>   - Stroke ratio reworded to ~1.6×–2.1× (34 em-units) → §5.3, §8.3
>   - SVG added to output-format enumerations → FR-04, GH-003 AC1, GH-005 AC3, GH-007 AC2
>   - Adoption Rate removed; `Release Bundle Completeness` as sole quantitative adoption metric → §7.1, §7.2
>   - "Valid" glyph issue triage defined; editor-compat measurement method (manual QA checklist) → §7.1
>   - AC-007 PR-review trail orphan: no PRD text referenced it; covered by GH-006 (no change needed)

# 🔍 Clarification Report [Review Iteration 2]

**Target Document:** `docs/prd-20260818-1636-semibold-font-weight.md` (v1.0; remediated → v1.1)
**Upstream Document:** `docs/discovery-draft-20260818-1625-semibold-font-weight.md`

**Readiness Score:** 95/100
**Status:** Good Enough (≥ 80)

**Score Breakdown:**

- **Completeness (max 40):** 39 — Seluruh FR (9), persona (3), user story + AC (GH-001..GH-008), milestone, metrik, non-goal, dan pertimbangan teknis lengkap. Stroke kini punya band (55–70) + floor (45) + aturan kalibrasi + jalur eskalasi; metrik adopsi & triase sudah terdefinisi. Sisa omission trivial (enumerasi SVG).
- **Clarity (max 30):** 28 — "approximately double" dihilangkan, kandidat 50/60/70 vs band 55–70 direkonsiliasi, "valid" terdefinisi, floor eksplisit. Sisa: frasa "or a clearly documented invocation" (FR-02) dan metode ukur editor-compat.
- **Alignment (max 30):** 28 — Selaras dengan Discovery Draft + preseden Medium (`spec-design-medium-weight.md` v1.6). Term `SemiBold` sudah ada di `CONTEXT.md`. Sisa orphan minor (AC-007 trail, `generate-css-decl`).
- **Critical Flaw Veto:** No — None.

---

## 1. 🚨 Critical Findings (Blockers)

- None.

## 2. 🧩 Resolved Items & Agreements

- **Requirement:** FR-01 + §5.3 + §8.3 + GH-006 AC3 — fallback saat kalibrasi stroke gagal menjaga counter.
  - **Resolution:** Opsi A — aturan kalibrasi eksplisit: *pilih stroke tertinggi dalam band 55–70 yang lulus uji "discernible counters" GH-006; jika tidak ada yang lulus, turunkan sampai lulus.* Manual per-glyph fix **tidak** menjadi fallback otomatis — hanya jika maintainer meminta. Frasa "ask first boundary" di §8.3 diganti kontrak ini.
- **Requirement:** FR-01 — batas bawah (floor) stroke.
  - **Resolution:** Opsi A — floor eksplisit **45 em-unit**. Jika counter tidak lulus pada/atau di atas floor, pendekatan single-pass dinyatakan gagal dan **eskalasi ke keputusan maintainer** (re-scope / abandon / manual fix), bukan diam-diam ship clone-Medium.
- **Requirement:** §7.1 — metrik "Adoption Rate ≥ 10% of font downloads include SemiBold".
  - **Resolution:** Opsi A — metrik dihapus; `Release Bundle Completeness` (100%) menjadi satu-satunya metrik kuantitatif adopsi.
- **Requirement:** §7.1 — definisi "valid" pada metrik "Community Feedback: No more than 2 valid glyph quality issues".
  - **Resolution:** Opsi A — triase eksplisit: *valid = glyph-quality defect yang dikonfirmasi maintainer, dedup per akar-masalah, mengecualikan artefak yang sudah dicatat `accepted-deviation`.* Target ≤2 dihitung terhadap isu valid menurut definisi ini.

## 3. ⚠️ Assumed / Auto-Resolved / Out of Scope

- **Scenario / Question:** FR-01 "~55–70 em-units" vs §8.3/§9.2 "candidate 50/60/70".
  - **Handling:** `[Assumed / Auto-Resolved]` — grid kandidat 50/60/70, band target 55–70, 50 = step-down pertama di bawah band, floor 45 (konsisten dengan Resolusi floor).
- **Scenario / Question:** Discovery §5 menyebut carry-over "AC-007 external PR-review trail" (artefak Medium) yang tidak punya padanan di PRD SemiBold.
  - **Handling:** `[Assumed / Auto-Resolved]` — orphan; hapus/abaikan. GH-006 (visual QA via PR review) sudah menutupi jejak review PR.
- **Scenario / Question:** §2.3 non-goal hanya mencantumkan 8 file CON-07, tapi `generate-css-decl` juga zero-touch (Medium spec §1).
  - **Handling:** `[Assumed / Auto-Resolved]` — tambah `generate-css-decl` (dan catat `zip-all-variants` auto-discover) ke enumerasi zero-touch. Terverifikasi kedua skrip membaca `os2_weight`/direktori secara dinamis.
- **Scenario / Question:** §5.3 "approximately double the Medium stroke".
  - **Handling:** `[Assumed / Auto-Resolved]` — reword ke "~1.6×–2.1× stroke Medium (34 em-unit)" agar presisi.
- **Scenario / Question:** FR-04/GH-005/GH-007 tidak mencantumkan SVG, padahal build juga memproduksi SVG (`generate-css-decl` merujuk `.svg`).
  - **Handling:** `[Assumed / Auto-Resolved]` — tambah SVG ke enumerasi format output.
- **Scenario / Question:** FR-02 "The same script (or a clearly documented invocation)".
  - **Handling:** `[Assumed / Auto-Resolved]` — satu skrip (preseden Medium, deteksi input italic via basename).
- **Scenario / Question:** §7.1 "Editor Compatibility: renders correctly in the top 5 editors" — metode ukur tidak terdefinisi.
  - **Handling:** `[Assumed / Auto-Resolved]` — metode ukur = checklist QA manual (kualitatif), bukan gate CI.

## 4. 📝 Next Steps

- `CONTEXT.md`: tidak ada term domain baru yang di-resolve → tidak berubah.
- ADR: keputusan kalibrasi/floor adalah kebijakan per-fitur, bukan keputusan arsitektur hard-to-reverse → tidak dibuat.
- `/sdlc-define-specs` mengkodekan keempat resolusi ke `spec-design-semibold-weight.md`; author PRD menerapkan 7 auto-resolusi di atas.

---

> **User Decision Prompt:** Dokumen telah mencapai Readiness Score **95/100**. Siap lanjut ke fase berikutnya. Apakah Anda ingin **PROCEED** ke `/sdlc-define-specs`, atau **REFINE** untuk memperjelas lebih lanjut?
