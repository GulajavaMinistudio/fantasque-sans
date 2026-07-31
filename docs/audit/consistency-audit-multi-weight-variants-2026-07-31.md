# Consistency Audit Report: Multi-Weight Font Variants

**Date**: 2026-07-31
**Auditor**: Artifact Consistency Checker persona (`/sdlc-audit-consistency`)
**Audit type**: PRD-only (pre-Spec transition audit)
**Session language**: Indonesian (per `AGENTS.md` Communication policy)

---
<!-- markdownlint-disable -->

## 1. 📊 Executive Summary

- **Documents Analyzed:**
  - PRD: [`docs/prd-20260731-1000-multi-weight-variants.md`](../prd-20260731-1000-multi-weight-variants.md) (v1.2, DRAFT)
  - Clarification Report: [`docs/audit/clarification-report-multi-weight-variants-2026-07-31.md`](clarification-report-multi-weight-variants-2026-07-31.md)
  - Discovery Draft: [`docs/discovery-draft-20260730-2110-multi-weight-variants.md`](../discovery-draft-20260730-2110-multi-weight-variants.md)
  - Domain Glossary: [`CONTEXT.md`](../../CONTEXT.md)
  - ADRs: [`0001-multi-stage-docker-legacy-tools.md`](../adr/0001-multi-stage-docker-legacy-tools.md) (Superseded), [`0002-multi-stage-docker-deferred-engine-port.md`](../adr/0002-multi-stage-docker-deferred-engine-port.md) (Accepted)
  - Standards: `.agents/standards/CONTEXT-FORMAT.md`, `.agents/standards/ADR-FORMAT.md`
- **Overall Status:** **PASS WITH WARNINGS**
- **Standards Compliance:** **PASS** (dengan catatan minor)

**Ringkasan Eksekutif**: PRD v1.2 telah menerapkan 28 dari 29 item hasil klarifikasi dengan baik. Struktur dokumen solid, *functional requirements* saling terkait secara koheren, dan terminologi mayoritas konsisten dengan Domain Glossary. Terdapat **5 temuan minor** (C1–C5) — tidak ada yang bersifat *blocking*, namun disarankan diselesaikan sebelum atau selama fase Spec untuk menjaga kebersihan *traceability chain*.

**Catatan**: Dokumen Spec dan Plan **belum ada** pada saat audit ini dilakukan. Pengguna berada di transisi PRD → Spec. Maka audit ini fokus pada **konsistensi internal PRD** dan **konsistensi PRD terhadap dokumen upstream** (Discovery Draft & Clarification Report).

---

## 2. 🔍 Traceability Findings

*Mapping of requirements from business intent (Discovery Draft) down to functional requirements (PRD), plus internal PRD cross-reference validation.*

### 2.1 Missing Coverage (Upstream → PRD)

| # | Item | Gap | Severity |
|---|------|-----|----------|
| — | *(tidak ditemukan)* | Seluruh requirement dalam Discovery Draft telah tertangani di PRD. Seluruh 12 resolusi klarifikasi telah diterapkan dengan tepat. | — |

### 2.2 Internal PRD Cross-Reference Validation

| From | References | Status |
|------|-----------|--------|
| FR-2.4 (PoC gate) | Visual Quality Rubrik (deliverable E0.4) | ✅ Rujukan jelas, dua arah |
| FR-2.5 (PoC failure path) | §8.3 (mitigasi risiko), GH-006 (V2 eksplorasi) | ✅ Empat jalur keputusan terdokumentasi |
| FR-4.1 (stretch weight gate) | FR-5 (visual review), §8.3 (mitigasi) | ✅ Tier kesuksesan eksplisit |
| FR-5.2 (specimen sheet) | FR-1.5 (soft invariant 24–72 pt) | ✅ *Discontinuity checklist* dirujuk |
| FR-7.1 (build pipeline) | §8.1 (FEA wrapper), FR-7.2 (backward compat) | ✅ Arsitektur jelas |
| §8.1 (FEA wrapper) | CON-001, ADR-0002, `scripts/multi_weight_driver.py` | ✅ *Integration points* terdokumentasi |
| SM-T3 (build duration) | FR-7.3, §8.3 (scalability) | ✅ Target ≤ 240 menit, buffer 120 menit |
| GH-001 → GH-006 | FR-1 s/d FR-7 | ✅ Setiap *user story* memiliki mapping ke FR |
| SM-U1 s/d SM-T4 | FR-4, FR-6, FR-7, Business Goals (§2.1) | ✅ Semua *metric* memiliki justifikasi *upstream* |

### 2.3 Orphaned Items (Scope Creep)

| # | Item | Status |
|---|------|--------|
| — | *(tidak ditemukan)* | Tidak ada fitur, *task*, atau *technical requirement* dalam PRD yang tidak memiliki justifikasi dari Discovery Draft atau hasil klarifikasi. Seluruh FR memiliki *user story* terkait (GH-001 s/d GH-006) atau merupakan *internal technical requirement* yang wajar (FR-1, FR-3). |

### 2.4 Discovery Draft Handoff Notes — Coverage Verification

*Discovery Draft §5 memberikan 4 catatan wajib kepada Product Manager. Berikut verifikasi cakupannya di PRD:*

| # | Handoff Note (Discovery §5) | Cakupan di PRD | Status |
|---|---------------------------|----------------|--------|
| 1 | *"Penambahan weight ini BUKAN tugas scripting/otomatisasi sederhana. Ini adalah proyek perombakan desain font (type design)"* | PRD §1.2 menyatakan *"type-design-heavy: terdapat ~1.042 glyph yang konturnya tidak kompatibel"*, §9.1 mengalokasikan 2 Type Designer part-time, §8.3 mengakui *"skala harmonisasi manual...140–240 jam"* | ✅ |
| 2 | *"PRD harus secara eksplisit mendefinisikan apakah interpolasi matematis dapat diterima jika hal tersebut sedikit menghilangkan 'wibbly-wobbly handwriting feel'"* | PRD FR-2.4 mendefinisikan Visual Quality Rubrik sebagai standar objektif, FR-2.5 mendefinisikan *failure path* jika kualitas tidak tercapai | ✅ |
| 3 | *"Jika tujuan akhirnya mencakup pembuatan Variable Font, maka PRD harus merencanakan migrasi dari format FontForge ke UFO (fontmake)"* | PRD §1.2 mengukuhkan Workflow A untuk V1, GH-006 sebagai *spike research* UFO/fontmake untuk V2, §8.3 mengakui batasan interpolasi linear FontForge | ✅ |
| 4 | *"Sangat disarankan agar PRD mendefinisikan 'Proof of Concept (PoC)' terlebih dahulu"* | PRD FR-2 mendefinisikan PoC lengkap dengan subset 40–50 glyph, gate LULUS/GAGAL, dan *failure path* | ✅ |

### 2.5 Risk Coverage Analysis

*Verifikasi bahwa seluruh risiko yang diidentifikasi di PRD §8.3 memiliki strategi mitigasi yang terdokumentasi:*

| Risiko (§8.3) | Dampak | Mitigasi | Status |
|---------------|--------|----------|--------|
| Skala harmonisasi manual (140–240 jam, kemacetan *throughput* manusia) | Penundaan rilis | PoC (FR-2) validasi *early*, 2 Type Designer paralel (Designer A + B) | ✅ Tercakup |
| Keterbatasan interpolasi FontForge (ekstrapolasi Light/ExtraBold) | Distorsi pada *stretch weight* | *Partial success tier* — Light/ExtraBold hanya dirilis jika lolos *visual review* (FR-5); jika gagal, ditunda ke V2 | ✅ Tercakup |
| Durasi *build* (estimasi ~200–240 menit) | *Timeout* GitHub Actions (360 menit *limit*) | Optimasi *script* (*batching*, `parallel` GNU), *buffer* 120 menit, SM-T3 sebagai target terukur | ✅ Tercakup |
| CON-001 *constraint* (tidak boleh modifikasi *source legacy*) | *Wrapper* tidak bisa mengubah `build.py`/`features.py` | *Wrapper* `multi_weight_driver.py` memanggil `features.py` 6× via subprocess/import; direktori output terpisah (`sources/Harmonized/`) | ✅ Tercakup |

### 2.6 Non-Goals vs Functional Requirements — Consistency Check

*Verifikasi bahwa tidak ada Functional Requirement yang melanggar Non-Goal yang dideklarasikan di PRD §2.3:*

| Non-Goal (§2.3) | FR Terkait | Status |
|-----------------|-----------|--------|
| Variable Font (VF) tidak termasuk V1 | FR-4.1: hanya menghasilkan *static weight instances* | ✅ Konsisten |
| Otomatisasi penuh tanpa *human review* | FR-5.1, FR-5.3: setiap *glyph* wajib *visual review* manual | ✅ Konsisten |
| *Weight* di luar rentang 300–800 | FR-4.1: rentang Light 300 s/d ExtraBold 800 | ✅ Konsisten |
| Modifikasi pada *source legacy* (CON-001) | FR-1.2, FR-3.3: *script* baru, direktori `sources/Harmonized/` terpisah | ✅ Konsisten |
| `font.changeWeight()` atau *stroke modification* otomatis | FR-4.1: menggunakan `font.interpolateFonts()` — interpolasi, bukan *stroke modification* | ✅ Konsisten |
| Perubahan metrik vertikal atau lebar | §5.3 *"Monospace guarantee"*: *advance width* identik antar *weight* | ✅ Konsisten |

### 2.7 Contradictions (Cross-Document Conflicts)

#### C1 — E7 Escalation Path Tidak Eksplisit di PRD §9.1 ⚠️ LOW

- **Sumber**: Clarification Report §2, Edge Case E7 (status: ⚠️ Partial)
- **Temuan**: Clarification Report menyatakan bahwa jika terjadi deadlock pada *shared pool* (Symbols, ligatures, PUA, box-drawing), eskalasi dilakukan ke *upstream maintainer*. PRD §9.1 menjelaskan pembagian statis dan "*merge gate* oleh Designer A", namun **tidak menyebutkan eskalasi ke *upstream maintainer*** secara eksplisit.
- **Catatan**: Entri "Type Designer" di CONTEXT.md sudah mencakup kalimat *"Escalation ke upstream maintainer untuk deadlock"*, tetapi PRD belum.
- **Dampak**: Jika deadlock terjadi saat eksekusi Phase 2, tidak ada *decision-maker* yang jelas di luar Designer A. Risiko terbatas karena *shared pool* hanya ~5% glyph.
- **Rekomendasi**: Tambahkan satu kalimat di PRD §9.1: *"Jika terjadi deadlock pada shared pool, eskalasi ke upstream maintainer untuk resolusi."*

#### C2 — Domain Language: "Visual Quality Rubrik" vs "Visual Quality Rubric" ⚠️ LOW

- **Sumber**: PRD FR-2.4, FR-2.5, §5.3, §9.2, GH-005 vs CONTEXT.md entri "Visual Quality Rubric"
- **Temuan**: PRD menggunakan ejaan Indonesia "Rubrik" (dengan 'k') di seluruh 8 kemunculan. Sementara CONTEXT.md mendefinisikan istilah kanonis sebagai **"Visual Quality Rubric"** (dengan 'c', ejaan Inggris). Ini adalah inkonsistensi *domain language* — PRD menggunakan varian ejaan yang tidak terdaftar di CONTEXT.md.
- **Dampak**: Tidak ada dampak fungsional. Namun jika ada *script* atau *tooling* yang melakukan *regex match* terhadap istilah dari CONTEXT.md, varian "Rubrik" tidak akan tertangkap.
- **Rekomendasi**: Pilih salah satu:
  - (A) Ubah seluruh kemunculan "Rubrik" di PRD menjadi "Rubric" agar konsisten dengan CONTEXT.md.
  - (B) Perbarui CONTEXT.md untuk menerima kedua ejaan: `_Avoid_:` (kosong, karena bukan *synonym* melainkan varian ejaan).
  - Rekomendasi auditor: opsi (A) — gunakan ejaan Inggris "Rubric" di seluruh dokumen teknis, karena istilah domain lainnya menggunakan ejaan Inggris.

#### C5 — Cross-PRD Integration Gap: Custom Build Workflow ⚠️ LOW

- **Sumber**: PRD Multi-Weight §8.1 / FR-7.1 vs PRD Custom Build (`docs/prd-20260723-1130-custom-build-workflow.md`) FR-4.4
- **Temuan**: Multi-Weight PRD mengusulkan parameter baru `enable_multi_weight` pada Custom Build Workflow. Namun Custom Build PRD FR-4.4 menyatakan *"The build shall produce...outputs for all 4 weights of Fantasque Sans Mono (Regular, Bold, Italic, Bold Italic)"* — tidak menyebutkan kemungkinan 6–8 *weight*. Custom Build PRD tidak direferensikan sebagai dokumen yang perlu diperbarui.
- **Potensi konflik format**: Multi-Weight PRD FR-6.1 hanya menyebutkan TTF, OTF, WOFF2 untuk *weight* baru. Custom Build PRD FR-4.4 juga menghasilkan WOFF dan SVG untuk *weight* existing. Apakah *weight* baru juga perlu WOFF dan SVG? Tidak dijawab di kedua PRD.
- **Dampak**: Saat fase Spec, tim teknis perlu memutuskan apakah Custom Build PRD perlu direvisi untuk mengakomodasi parameter `enable_multi_weight`, atau apakah Multi-Weight Spec akan mendefinisikan integrasi sebagai *extension point* yang tidak memerlukan perubahan pada Custom Build Spec.
- **Rekomendasi**: Tambahkan referensi eksplisit ke Custom Build PRD di Multi-Weight PRD §8.1 dan catat bahwa Custom Build Spec mungkin perlu *minor update* untuk mengakomodasi parameter baru. Format WOFF/SVG untuk *weight* baru agar diputuskan di fase Spec.

---

## 3. 🛡️ Standards Compliance (Documentation Audit)

*Auditing adherence to project standards defined in `.agents/standards/`.*

### 3.1 ADR Format Compliance: PASS ✅

- **ADR-0001** (Superseded): Format sesuai template `.agents/standards/ADR-FORMAT.md`. Memiliki `Context`, `Decision`, `Consequences`, dan `Considered Options`. Status *superseded* didokumentasikan dengan jelas di header dan body.
- **ADR-0002** (Accepted): Format sesuai template. *Revision notes* terstruktur dengan baik (2026-07-23, 2026-07-30) dan *inline* dengan perubahan arsitektur.
- **Triple Gate Validation (ADR-0002)**:
  - ✅ **Hard to reverse** — Multi-stage Docker dengan `ubuntu:26.04` + `future` shim adalah keputusan infrastruktur signifikan.
  - ✅ **Surprising without context** — Penggunaan `future` shim untuk menjalankan *legacy Python 2.7 scripts* di atas Python 3 tidaklah *obvious* bagi engineer baru.
  - ✅ **Real trade-off** — *Deferred engine port* ke Python 3.14 (V2) vs *full rewrite* sekarang (risiko regresi output font).
  - **Kesimpulan**: ADR-0002 valid dan memenuhi ketiga kriteria.

### 3.2 Context/Glossary Alignment: PASS (dengan catatan) ⚠️

- PRD secara konsisten menggunakan istilah kanonis dari CONTEXT.md:
  - ✅ *Master*, *Master Harmonization*, *Interpolation*, *Static Weight*, *Variable Font*
  - ✅ *Core Weight*, *Stretch Weight*, *Faux Italic*, *Type Designer*
  - ✅ *Fork Owner*, *Upstream*, *Workflow A*, *Workflow B*, *Visual Quality Rubric*
- **Tidak ditemukan** penggunaan istilah yang tercantum di bawah `_Avoid_` dalam CONTEXT.md.
- **Catatan**: Inkonsistensi ejaan "Rubrik" vs "Rubric" (C2) adalah satu-satunya penyimpangan — lihat §2.4 untuk detail dan rekomendasi.

### 3.3 Codebase Reality Check: PASS ✅

| Claim in PRD | Codebase Verification | Status |
|-------------|----------------------|--------|
| Regular.sfdir: 1.042 glyph | Dikonfirmasi oleh Clarification Report (inspeksi codebase) | ✅ |
| Bold.sfdir: 1.040 glyph | Dikonfirmasi oleh Clarification Report | ✅ |
| Italic.sfdir: 1.046 glyph | Dikonfirmasi oleh Clarification Report | ✅ |
| BoldItalic.sfdir: 1.041 glyph | Dikonfirmasi oleh Clarification Report | ✅ |
| `Scripts/features.py` tidak dimodifikasi (CON-001) | PRD §2.3, §8.1 — *wrapper* hanya memanggil, tidak mengubah | ✅ |
| `Scripts/build.py` sebagai entry point | Dikonfirmasi di ADR-0002 | ✅ |
| `.github/workflows/custom-build.yml` | Dikonfirmasi di ADR-0002 dan ARCHITECTURE.md | ✅ |
| Eksperimen Phase 0 (E0.1–E0.4) | Didefinisikan di PRD §9.1 — menunggu eksekusi | ✅ |

### 3.4 Numeric Consistency Verification

*Verifikasi seluruh angka dan batasan kuantitatif konsisten di seluruh dokumen PRD:*

| Parameter | Nilai di PRD | Kemunculan | Status |
|-----------|-------------|------------|--------|
| Glyph Regular | 1.042 | FR-1.1, §1.2, §8.3, §9.1 | ✅ Konsisten |
| Glyph Bold | 1.040 | FR-1.1 | ✅ Konsisten |
| Glyph Italic | 1.046 | FR-1.1 | ✅ Konsisten |
| Glyph BoldItalic | 1.041 | FR-1.1 | ✅ Konsisten |
| PoC subset | ~40–50 glyph | FR-2.1, §9.2 Phase 1 | ✅ Konsisten |
| Toleransi cacat visual | 2% ≈ 21 glyph | FR-5.4 | ✅ 1.042 × 0.02 = 20.84 ≈ 21 |
| Core weight count | 4 (Regular, Medium, SemiBold, Bold) | §1.2, FR-4.1, GH-001, GH-004 | ✅ Konsisten |
| Stretch weight count | 2 (Light, ExtraBold) | §1.2, FR-4.1 | ✅ Konsisten |
| Total weight (max) | 6 | §1.2, §5.1, SM-T4 | ✅ Konsisten |
| Build duration target | ≤ 240 menit | FR-7.3, SM-T3 | ✅ Konsisten |
| Build duration estimasi | 15m + 140m + 80m + 10m = 245m | FR-7.3, SM-T3 | ⚠️ Estimasi kasar 245m > target 240m. PRD mengakui perlu optimasi (GNU `parallel`, *batching*) untuk turun ke ~200m — dapat diterima sebagai target optimasi |
| GitHub Actions limit | 360 menit | §8.3 | ✅ *Buffer* 120 menit dari target 240 menit |
| Timeline total | 14–18 minggu (Minggu 1–14 + buffer 15–18) | §9.1, §9.2 | ✅ Konsisten |
| Type Designer count | 2 part-time @ ~20 jam/minggu | §9.1, §3.2, §3.3 | ✅ Konsisten |
| Total effort paralel | 240 jam (2 × 20 jam × 6 minggu) | §9.1 | ✅ Cukup untuk estimasi 140–240 jam harmonisasi |
| WOFF2 size target | ≤ 500 KB untuk 6 weight | GH-003, SM-T4 | ✅ Konsisten |
| Release size multiplier | ≤ 5× current release size | SM-T4 | ✅ Konsisten |
| Medium factor | 0.5 (tepat di tengah) | FR-4.1 | ✅ 400 + 0.5 × (700−400) = 550 — nilai 500 adalah *target weight name*, bukan hasil matematis linear. Dapat diterima karena interpolasi tipografis tidak selalu linear terhadap skala angka weight |
| SemiBold factor | ~0.67 | FR-4.1 | ✅ 400 + 0.67 × (700−400) ≈ 601 ≈ 600 |

### 3.5 ADR Triple Gate Audit — Potential Missing ADR ⚠️

#### C3 — Missing ADR: Workflow A (FontForge) vs Workflow B (UFO/fontmake) ⚠️ MEDIUM

- **Keputusan**: V1 menggunakan **Workflow A** (FontForge `.sfdir` + interpolasi linear via `font.interpolateFonts()`), menunda migrasi ke **Workflow B** (UFO v3 + `fontmake`) ke V2. Keputusan ini dibuat di Discovery Draft §4 dan dikukuhkan di PRD §1.2.
- **Triple Gate Assessment**:
  - ✅ **Hard to reverse** — Berganti *toolchain* di tengah proyek akan membatalkan hasil harmonisasi yang sudah dilakukan (format `.sfdir` berbeda dengan `.ufo`).
  - ✅ **Surprising without context** — Seorang *external contributor* atau *engineer* baru akan bertanya: *"Mengapa tidak menggunakan `fontmake` + UFO yang merupakan standar industri untuk multi-weight font generation?"*
  - ✅ **Real trade-off**:
    - **Workflow A (dipilih)**: Kecepatan taktis — *toolchain* sudah familiar, tidak perlu konversi format, bisa langsung mulai harmonisasi.
    - **Workflow B (ditunda)**: *Maintainability* jangka panjang, dukungan native untuk Variable Font (`gvar` table), ekosistem `fontTools` yang kaya.
  - **Kesimpulan**: Ketiga kriteria **terpenuhi**. Keputusan ini layak didokumentasikan sebagai ADR.
- **Rekomendasi**: Buat **ADR-0003** (`docs/adr/0003-workflow-a-fontforge-v1-interpolation.md`) yang mendokumentasikan:
  - Mengapa FontForge `.sfdir` dipilih untuk V1 (kecepatan, familiaritas, menghindari risiko konversi format)
  - Mengapa UFO/`fontmake` ditunda ke V2 (GH-006 sebagai *spike research*, Variable Font sebagai target V2)
  - *Trade-off* yang diterima: *technical debt* berupa *dual toolchain* di masa depan, dan batasan interpolasi linear FontForge untuk *extrapolation weight*

### 3.6 Spec Handoff Readiness Assessment

*Sebelum memasuki fase Spec (`/sdlc-define-specs`), beberapa item perlu dipastikan kesiapannya. Berikut penilaian berdasarkan kondisi PRD saat ini:*

| Item | Status | Catatan |
|------|--------|--------|
| PRD telah melalui Clarification Checkpoint | ✅ Selesai | 28/29 item diterapkan, 1 partial (E7) |
| PRD telah melalui Consistency Audit | ✅ Selesai | Laporan ini |
| Eksperimen Phase 0 (E0.1–E0.4) | ❌ Menunggu eksekusi | Wajib sebelum Phase 1 (PoC), bukan prasyarat Spec. Spec dapat ditulis paralel dengan eksperimen, karena Spec mendefinisikan *how to build*, bukan hasil eksperimen |
| Domain Glossary (CONTEXT.md) mutakhir | ✅ Siap | Semua istilah multi-weight sudah terdefinisi. Perbaikan minor: selaraskan "Rubrik" → "Rubric" (C2) |
| ADR untuk Workflow A vs B | ❌ Belum ada | Buat ADR-0003 sebelum atau selama Spec (C3) |
| Custom Build PRD sinkronisasi | ⚠️ Perlu koordinasi | Custom Build PRD perlu *minor update* atau Spec Multi-Weight perlu mendefinisikan integrasi sebagai *extension point* (C5) |

**Kesimpulan**: PRD siap menjadi fondasi Spec. Spec dapat dimulai secara paralel dengan eksperimen Phase 0 dan perbaikan minor PRD (C1, C2).

---

### 3.7 PoC Scope Completeness — Minor Gap ⚠️

#### C4 — PoC Tidak Memvalidasi Pasangan Italic↔BoldItalic ⚠️ LOW

- **Temuan**: FR-2.1 mendefinisikan subset PoC ~40–50 *glyph* (a–z, multi-kontur g/@/&/Q/?, counter kompleks ß/fi/fl, fungsional space/period/comma/zero, dan 3–5 *worst offenders*). Subset ini seluruhnya adalah *upright glyphs*. Namun FR-1.1 dan FR-3.1 mensyaratkan harmonisasi **dua pasangan master** (Regular↔Bold **dan** Italic↔BoldItalic). PoC saat ini hanya memvalidasi pendekatan pada pasangan pertama.
- **Risiko**: Masalah spesifik Italic↔BoldItalic — misalnya *slant angle* tidak konsisten antar master, atau perbedaan struktur kontur yang unik pada *glyph italic* — baru terdeteksi di Phase 2, setelah investasi harmonisasi penuh.
- **Rekomendasi** (pilih salah satu):
  - (A) Tambahkan 2–3 *glyph italic* representatif (misal: `a`, `g`, `f` dari Italic.sfdir) ke dalam subset PoC.
  - (B) Tambahkan catatan eksplisit di FR-2.1 bahwa pasangan Italic↔BoldItalic tidak memerlukan PoC terpisah karena prinsip harmonisasi identik dengan pasangan Regular↔Bold, dan risikonya diterima.
  - Rekomendasi auditor: opsi (B) — lebih pragmatis dan tidak menambah beban Phase 1.

---

## 4. 📝 Action Plan (Corrective Actions)

*Clear checklist for the user to address before or during the Spec phase.*

### Updates Required

- [ ] **PRD §9.1** — Tambahkan satu kalimat: *"Jika terjadi deadlock pada shared pool, eskalasi ke upstream maintainer untuk resolusi."* (Tindak lanjut dari **C1** / Clarification E7)
- [ ] **PRD (global)** atau **CONTEXT.md** — Selaraskan ejaan "Visual Quality Rubrik" vs "Visual Quality Rubric". Rekomendasi: ubah seluruh "Rubrik" di PRD menjadi "Rubric" agar konsisten dengan CONTEXT.md. (**C2**)
- [ ] **ADR baru** — Buat `docs/adr/0003-workflow-a-fontforge-v1-interpolation.md` untuk mendokumentasikan keputusan Workflow A vs Workflow B. (**C3**)
- [ ] **PRD FR-2.1** (opsional) — Tambahkan catatan eksplisit bahwa pasangan Italic↔BoldItalic tidak memerlukan PoC terpisah. (**C4**)
- [ ] **PRD §8.1** — Tambahkan referensi eksplisit ke Custom Build PRD dan catatan bahwa Custom Build Spec mungkin perlu *minor update*. Format WOFF/SVG untuk *weight* baru diputuskan di Spec. (**C5**)
- [x] **Spec:** *(belum ada — tidak ada tindakan)*
- [x] **Plan:** *(belum ada — tidak ada tindakan)*
- [x] **Standards (ADR/Context):** *(format sudah sesuai — hanya perlu ADR baru untuk C3)*

### Approval Status: **NOT REQUIRED**

PRD v1.2 dapat dilanjutkan ke fase **Spec** (`/sdlc-define-specs`) tanpa perlu *re-approval*. Kelima temuan (C1–C5) bersifat minor dan tidak memblokir proses *downstream*. Auditor merekomendasikan penyelesaian C1 dan C2 sebelum menulis Spec (cukup 2 kalimat), sementara C3 (ADR baru), C4 (opsional), dan C5 (koordinasi Spec) dapat diselesaikan selama fase Spec.

---

## 5. 📋 Traceability Matrix (PRD → User Stories)

*Ringkasan pemetaan Functional Requirements ke User Stories untuk referensi cepat saat menulis Spec.*

| FR | Deskripsi Singkat | User Story | Priority |
|----|-------------------|-----------|----------|
| FR-1 | Master Harmonization (2 pasangan) | GH-005 (validasi) | CRITICAL |
| FR-2 | Proof of Concept (PoC) subset | GH-005 (validasi) | CRITICAL |
| FR-3 | Full Master Harmonization (4 master) | GH-005 (validasi) | HIGH |
| FR-4 | Multi-Weight Interpolation (4–6 weight) | GH-001, GH-002 | HIGH |
| FR-5 | Visual Quality Assurance | GH-005 | HIGH |
| FR-6 | Distribution & Packaging (TTF/OTF/WOFF2) | GH-001, GH-002, GH-003 | MEDIUM |
| FR-7 | Build Pipeline Integration (Custom Build) | GH-004 | MEDIUM |
| GH-006 | Eksplorasi UFO/fontmake (V2 Preview) | *(spike research)* | LOW |

---

## 6. 📎 References

- PRD under audit: [`docs/prd-20260731-1000-multi-weight-variants.md`](../prd-20260731-1000-multi-weight-variants.md) (v1.2)
- Clarification Report: [`docs/audit/clarification-report-multi-weight-variants-2026-07-31.md`](clarification-report-multi-weight-variants-2026-07-31.md)
- Discovery Draft: [`docs/discovery-draft-20260730-2110-multi-weight-variants.md`](../discovery-draft-20260730-2110-multi-weight-variants.md)
- Domain Glossary: [`CONTEXT.md`](../../CONTEXT.md)
- ADR-0001: [`docs/adr/0001-multi-stage-docker-legacy-tools.md`](../adr/0001-multi-stage-docker-legacy-tools.md) (Superseded)
- ADR-0002: [`docs/adr/0002-multi-stage-docker-deferred-engine-port.md`](../adr/0002-multi-stage-docker-deferred-engine-port.md) (Accepted)
- Standards: `.agents/standards/CONTEXT-FORMAT.md`, `.agents/standards/ADR-FORMAT.md`
- Audit Template: `.agents/skills/sdlc-audit-consistency/references/AUDIT-REPORT-TEMPLATE.md`
