# Consistency Audit Report: Multi-Weight Font Variants (Plan vs PRD vs Spec)

**Date**: 2026-08-01
**Auditor**: Artifact Consistency Checker persona (`/sdlc-audit-consistency`)
**Audit type**: Tri-directional audit (PRD → Spec → Plan) + ADR/Glossary/Codebase compliance
**Session language**: Indonesian (per `AGENTS.md` Communication policy)

---
<!-- markdownlint-disable -->

## 1. 📊 Executive Summary

- **Documents Analyzed:**
  - PRD: [`docs/prd-20260731-1000-multi-weight-variants.md`](../prd-20260731-1000-multi-weight-variants.md) (v1.3, DRAFT)
  - Spec: [`spec/spec-multi-weight-variants.md`](../../spec/spec-multi-weight-variants.md) (v1.3, `last_updated` 2026-07-31)
  - Plan: [`plan/plan-feature-multi-weight-variants-v1.3.md`](../../plan/plan-feature-multi-weight-variants-v1.3.md) (konten internal **v1.7**, `last_updated` 2026-08-01)
  - Domain Glossary: [`CONTEXT.md`](../../CONTEXT.md)
  - ADRs: `docs/adr/0001-multi-stage-docker-legacy-tools.md` (Superseded), `0002-multi-stage-docker-deferred-engine-port.md` (Accepted), `0003-workflow-a-fontforge-v1-interpolation.md` (Accepted)
  - Kontekstual: `docs/audit/consistency-audit-multi-weight-variants-2026-07-31.md` (audit PRD sebelumnya), `docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-07-31-r2.md` (klarifikasi r2), `docs/audit/clarification-report-multi-weight-variants-2026-07-31.md`, `docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-07-31.md` (r1)
  - Standards: `.agents/standards/CONTEXT-FORMAT.md`, `.agents/standards/ADR-FORMAT.md`, `.agents/skills/sdlc-audit-consistency/references/AUDIT-REPORT-TEMPLATE.md`
  - Codebase: `Scripts/` (custom_build_driver.py, configure.py, features.py, packaging.sh), `Sources/` (5 .sfdir), `Dockerfile`, `.github/workflows/custom-build.yml`, `tests/`, root `Makefile`
- **Overall Status:** **FAIL** — dengan catatan: mayoritas temuan sudah diketahui dan terjadwal sebagai amendemen upstream (klarifikasi r2 §4), namun **belum dieksekusi** ke Spec v1.3 / PRD v1.3.
- **Standards Compliance:** **PASS** (format ADR & CONTEXT.md sudah sesuai; terdapat 2 pelanggaran domain-language minor di Plan)

**Ringkasan Eksekutif**: Plan v1.7 adalah artefak paling matang — seluruh 12 resolusi klarifikasi r2 terimplementasi dengan akurat, dan 5 rekomendasi audit sebelumnya (C1–C5) telah ditutup semua. Namun Spec v1.3 dan PRD v1.3 belum diamendemen sesuai r2, sehingga kondisi dokumen saat ini mengandung kontradiksi langsung (path rubric, daftar pesan log, model pemanggilan `features.py`, klaim byte-identical, timing factor stretch, dll.). Plan juga mereferensikan file audit yang tidak ada di `docs/audit/` (temuan B1). **Konsekuensi**: proses menuju `/sdlc-write-code` ditahan sampai amendemen upstream diterapkan dan re-audit lulus.

## 2. 🔍 Traceability Findings

_Mapping of requirements from business intent down to technical implementation._

### 2.1 Missing Coverage (PRD → Spec → Plan): ✅ NONE

Seluruh Functional Requirement (FR-1.1 s/d FR-7.3), 6 user story (GH-001 s/d GH-006), eksperimen E0.1–E0.4, dan acceptance criteria PRD memiliki desain di Spec (REQ-*) dan task eksplisit di Plan (TASK-*). Contoh verifikasi:

| PRD | Spec | Plan | Status |
|---|---|---|---|
| FR-2.4 (PoC gate ≥90%, rubric) | AC-P03, §6.2 E0.4 | TASK-1.X (gate ganda), TASK-0.5 | ✅ (path rubric: lihat A1) |
| FR-2.5 (4 jalur kegagalan PoC) | AC-P07 | TASK-1.Y | ✅ |
| FR-4.1 (factor 0.5 / ~0.67) | REQ-I01, §4.6 | TASK-0.7, TASK-3.1 | ✅ (timing stretch: lihat A2) |
| FR-5.4 (≤2% ≈ 21 glyph) | AC-I06, §11.2 | TASK-3.X | ✅ |
| FR-6.3 (3 archive per format) | REQ-D03, AC-D01 | TASK-4.4 | ✅ |
| FR-7.3 / SM-T3 (≤240 menit) | REQ-B04, AC-B04 | TASK-5.3, TASK-4.X | ✅ |
| GH-003 (WOFF2 ≤ 500 KB) | AC-D03 | TASK-4.X | ✅ |
| GH-005 AC#4 (tracking file) | §4.12 | TASK-0.5 | ✅ (schema: lihat A5) |
| GH-006 (V2 Preview, non-V1) | §1.2 Out of Scope, §12 | (tidak ada task V1) | ✅ |

### 2.2 Orphaned Items (Scope Creep): ✅ NONE

Seluruh item Plan dapat ditelusuri ke Spec/PRD/klarifikasi r2. Item yang tampak baru seluruhnya berakar pada kontrak existing atau resolusi terdokumentasi:

| Item Plan | Justifikasi Upstream |
|---|---|
| Penanganan `FantasqueSans.sfdir` (REQ-B06, §4.3) | Kontrak driver existing — `find_sfdirs()` memindai seluruh `*.sfdir` di SOURCES_DIR; bukan fitur baru |
| `Scripts/poc_interpolation.py` (FILE-005) | PRD §9.2 Phase 0: "Tulis script interpolasi proof-of-concept" |
| Fixture sintetis `tests/fixtures/multi_weight/` (FILE-022) | Spec §6.5, resolusi r2 (konten dikunci) |
| Injeksi metadata os2_weight/fullname (TASK-0.7/3.1) | GH-001 AC (font picker name), AC-I03 |
| 3 artefak audit baru (`poc-glyph-list`, `stretch-factor-decision`, `phase3-visual-review`) | Resolusi r2 §1/§4 |
| `timeout-minutes: 360` (TASK-4.3) | CON-007, PRD §8.3, resolusi r2 |
| Tangent-angle detection (TASK-0.2/0.3) | REQ-H06 (discontinuity threshold 15.0°) |

### 2.3 Contradictions (Cross-Document Conflicts): ❌ MAJOR

#### Grup A — Amendemen r2 yang belum diterapkan (kontradiksi kondisi saat ini)

| # | Konflik | Lokasi | Severity |
|---|---|---|---|
| A1 | **Path rubric**: `docs/visual-quality-rubric.md` (Spec) vs `docs/audit/visual-quality-rubric.md` (kanonik, Plan TASK-0.5) | Spec §6.2 E0.4 vs Plan TASK-0.5 | HIGH |
| A2 | **Timing factor stretch**: "factor eksak ditentukan **saat PoC**" (Spec) vs ditentukan **Phase 5** oleh Designer A + maintainer (Plan TASK-5.4); FR-2.2 menetapkan PoC hanya Medium | Spec REQ-I02 vs Plan TASK-5.4 | HIGH |
| A3 | **Pesan log mustahil**: `"Calling features.py for Regular..."` tidak mungkin dihasilkan (CON-001; driver existing mencetak `"Generating {name}"`; `multi_weight_driver.py` TIDAK memanggil `features.py` — REQ-B03) | Spec GUD-003/AC-B05 & PRD GH-004 AC#5 vs Plan TASK-4.X | HIGH |
| A4 | **Injeksi metadata** (os2_weight/fullname) belum ada di kontrak driver | Spec §4.6 vs Plan TASK-0.7/3.1 | MEDIUM |
| A5 | **Schema `tracking.json`** belum memuat field `review_verdict`/`reviewed_by`/`date` | Spec §4.12 vs Plan TASK-0.5 | MEDIUM |
| A6 | **Jumlah test case driver**: 10 (Spec) vs 11 (Plan, +`test_metadata_injection`, toleransi ±0.005) | Spec §6.3 vs Plan TASK-0.10 | MEDIUM |
| A7 | **Konten fixture** belum dikunci (2 master, ≥6 glyph, advance width beda, node_count_mismatch, only_in_a/b, font.props) | Spec §6.5 vs Plan TASK-0.10 | MEDIUM |
| A8 | **Definisi operasional `warning`/`fail`** (warning = artifact non-self-intersect / tangent-angle > threshold; fail = self-intersection / counter tertutup / kontur rusak) belum ada | Spec §4.11 vs Plan TASK-0.3 | MEDIUM |
| A9 | **Definisi "Release Upstream Pipeline"** (eksekusi manual/terisolasi maintainer di luar CI) belum dicatat | Spec §8.5 vs Plan TASK-5.4/RISK-002 | LOW |
| A10 | **Gate ganda PoC** (script ≥90% + fail_count=0 + manusia ≥90%) belum tercatat di PRD | PRD FR-2.4 vs Plan TASK-1.X | MEDIUM |
| A11 | **Model pemanggilan `features.py`**: PRD menyebut subprocess 6× + perbandingan antar master; Spec mengoreksi menjadi in-process oleh driver existing + source sama (terverifikasi: `Scripts/custom_build_driver.py:230` `_update_features(fnt)` di `build_one_weight()`) | PRD §8.1, §9.2 E0.1 vs Spec REQ-B03/§4.7/E0.1 | HIGH |

#### Grup B — Temuan baru (BELUM masuk daftar amendemen terjadwal Plan v1.7)

| # | Konflik | Lokasi | Severity |
|---|---|---|---|
| B1 | **Referensi audit rusak**: `audit_reference: docs/audit/consistency-audit-plan-vs-prd-spec-2026-07-31.md` — file **tidak ada** di repository (diverifikasi via `find`); hanya Plan yang mereferensikannya | Plan frontmatter (baris 11) | MEDIUM |
| B2 | **Klaim byte-identical**: PRD menyatakan output "tidak byte-identical dengan V0" dalam konteks mode single-weight; Spec mengoreksi: mode `false` = **byte-identical**, hanya mode multi-weight yang berbeda (Regular/Bold dibangun dari harmonized masters) | PRD FR-7.2 vs Spec §8.5/AC-B03/§10.5 | HIGH |
| B3 | **Output mode single-weight**: "build hanya menghasilkan Regular + Bold" vs output aktual 5 file (Regular, Bold, Italic, BoldItalic, FantasqueSans) | PRD GH-004 AC#3 vs Spec AC-B03/§4.3 | MEDIUM |
| B4 | **Specimen PDF**: "Specimen sheet PDF dihasilkan otomatis untuk setiap weight" vs keputusan resmi **HTML** (PDF ditunda V2; koreksi GH-005 AC#2 — satu set halaman HTML gabungan) | PRD GH-005 AC#2 vs Spec §8.5/REQ-S01 | MEDIUM |
| B5 | **Bentuk integrasi workflow**: "diintegrasikan ke dalam Custom Build Workflow sebagai tahap opsional" vs RUN kondisional Dockerfile Stage 1 (bukan step workflow; flag forwarding via `configure.py`) | PRD FR-7.1 vs Spec §4.9 | MEDIUM |
| B6 | **Penjadwalan stretch**: PRD Phase 3 (Minggu 11–12) masih menginstruksikan "Interpolasi stretch weight — opsional"; Plan menangguhkan seluruh produksi stretch ke release upstream pipeline (Phase 5) | PRD §9.2 Phase 3 vs Plan Phase 3/5 | LOW |
| B7 | **Daftar amendemen Plan tidak lengkap**: tidak mencakup Spec §4.9 (RUN chain + `RUN pytest tests/` di Stage 1 — diubah oleh TASK-4.2) serta B2–B6 di PRD | Plan Introduction vs r2 §4 | LOW |

#### Grup C — Inkonsistensi numerik/lateral minor

| # | Temuan | Detail |
|---|---|---|
| C1 | **Jumlah pemanggilan `features.py`**: PRD "6×", Spec §4.7 "6–8×" — aktual **7–9×** (build/sources = 4 harmonized master + 2–4 interpolated + `FantasqueSans.sfdir`; driver memindai seluruh `*.sfdir`) | Penyelarasan kalimat menjadi "per `.sfdir` di build/sources" disarankan |
| C2 | **`timeout-minutes`**: saat ini `30` (`.github/workflows/custom-build.yml:60`) → Plan TASK-4.3 mengubah ke `360` (batas platform, CON-007) | ✅ Konsisten — perubahan terjadwal, bukan konflik |

### 2.4 Verifikasi audit sebelumnya (consistency-audit-multi-weight-variants-2026-07-31.md): ✅ SEMUA DITUTUP

| Temuan audit sebelumnya | Status di dokumen saat ini |
|---|---|
| C1 — eskalasi deadlock ke upstream maintainer di PRD §9.1 | ✅ Ditambahkan: "Jika terjadi deadlock pada shared pool, eskalasi ke upstream maintainer untuk resolusi" |
| C2 — ejaan "Rubrik" vs "Rubric" | ✅ 0 kemunculan "Rubrik" di PRD v1.3; seluruhnya "Rubric" |
| C3 — Missing ADR Workflow A vs B | ✅ ADR-0003 dibuat (Accepted) |
| C4 — PoC tidak memvalidasi pasangan Italic↔BoldItalic | ✅ Catatan eksplisit ditambahkan di FR-2.1 |
| C5 — Cross-PRD Custom Build gap | ✅ PRD §8.1 mereferensikan Custom Build PRD + catatan minor update; format WOFF/SVG diputuskan di Spec REQ-D01/D03 |

## 3. 🛡️ Standards Compliance (Documentation Audit)

_Auditing adherence to project standards defined in `.agents/standards/`._

### 3.1 ADR Format Compliance: PASS ✅

- **ADR-0001** (Superseded by ADR-0002): format sesuai template (Context, Decision, Consequences, Considered Options); status supersession terdokumentasi.
- **ADR-0002** (Accepted): format sesuai; revision notes terstruktur (2026-07-23, 2026-07-30) selaras dengan implementasi aktual Dockerfile.
- **ADR-0003** (Accepted): format sesuai; **Triple Gate valid** — (1) Hard to reverse: hasil harmonisasi `.sfdir` akan dibatalkan jika berganti toolchain; (2) Surprising without context: mengapa tidak `fontmake`/UFO yang merupakan standar industri; (3) Real trade-off: kecepatan taktis vs maintainability jangka panjang (VF).
- **Missing ADR**: ✅ NONE. Keputusan Stage-1 execution context (§4.9) dan boundary stretch eksklusif upstream (§8.5) terdokumentasi sebagai spec-level resolutions dan mudah dibalik; kesimpulan klarifikasi r2 ("tidak ada keputusan yang memenuhi triple-gate; tidak ada ADR baru") **dikonfirmasi disetujui**.

### 3.2 Context/Glossary Alignment: FAIL ⚠️ (2 pelanggaran minor di Plan)

- **D1**: Plan baris 20 menggunakan sinonim **_Avoid_**: *"upstream release pipeline"* — terdaftar di `_Avoid_` untuk istilah kanonis **Release Upstream Pipeline** (CONTEXT.md). Sekaligus inkonsisten internal: TASK-3.4/5.4/RISK-002 memakai "release upstream pipeline" (kanonis).
- **D2**: Plan ALT-002 — *"varian bobot statis (static instances)"* — "static instance(s)" terdaftar di `_Avoid_` (Static Weight & Weight Variant); "bobot" bukan istilah glossary.
- **Lainnya**: PASS — syntax `_Avoid_:` sesuai CONTEXT-FORMAT.md; istilah kanonis (Master, Master Harmonization, Interpolation, Core Weight, Stretch Weight, Faux Italic, Visual Quality Rubric, Type Designer, Workflow A/B) digunakan konsisten di PRD/Spec/Plan. Tidak ditemukan penggunaan sinonim _Avoid_ lain (termasuk "VF" hanya muncul sebagai penjelasan dalam tanda kurung setelah istilah kanonis).

### 3.3 Codebase Reality Check: PASS ✅

| Klaim Dokumen | Verifikasi Codebase | Status |
|---|---|---|
| Glyph counts: Regular 1.042, Bold 1.040, Italic 1.046, BoldItalic 1.041 | `ls Sources/*.sfdir/*.glyph` → Regular 1042, Bold 1040, Italic 1046, BoldItalic 1041 (FantasqueSans: 231) | ✅ |
| `custom_build_driver.py <sources_dir> <output_dir> [options]` | Argumen posisional dikonfirmasi; `find_sfdirs()` memindai `*.sfdir` top-level | ✅ |
| `features.py` dipanggil in-process oleh driver (REQ-B03) | `_update_features(fnt)` di `build_one_weight()` (baris 230) | ✅ |
| Dockerfile Stage 1: `ubuntu:26.04` + `builder-fontforge` + `ARG BUILD_ARGS` | Dikonfirmasi (baris 21, 55); RUN chain multi-weight belum ada — sesuai TASK-4.2 | ✅ |
| Dockerfile Stage 2: `ubuntu:26.04` + Python 3.14 + ttfautohint/woff-tools/woff2/zip/tar/jq | Dikonfirmasi (baris 68+); sesuai ADR-0002 & Spec §9.2 | ✅ |
| Custom Build inputs existing (`large_line_height`, `no_loop_k`, `no_calt`, `use_hinted`) | Dikonfirmasi di custom-build.yml; `enable_multi_weight` belum ada — sesuai TASK-4.3 | ✅ |
| CON-001 (build.py, fontbuilder.py, features.py, root Makefile) | Seluruh file ada dan tidak dimodifikasi | ✅ |

### 3.4 Konsistensi Numerik (Lateral)

| Parameter | Nilai | Verifikasi |
|---|---|---|
| Toleransi cacat visual | ≤ 2% ≈ 21 glyph (1042 × 0.02 = 20.84) | ✅ Konsisten di PRD FR-5.4, Spec AC-I06/§11.2, Plan TASK-3.X |
| Harmonization pass rate | ≥ 98% (SM-T1) | ✅ AC-H02, TASK-2.X |
| Interpolation success / Phase 3 gate | ≥ 98% / ≤2% warning + 0 fail | ✅ SM-T2, TASK-3.X |
| PoC gate | ≥ 90% + 0 distorsi berat | ✅ FR-2.4, AC-P03, TASK-1.X (gate ganda) |
| Build duration | ≤ 240 menit (est. 15+140+80+10 = 245 → target optimasi) | ✅ FR-7.3/SM-T3/REQ-B04/AC-B04 — catatan optimasi konsisten di ketiga dokumen |
| Platform limit | 360 menit | ✅ CON-007, PRD §8.3, TASK-4.3 |
| WOFF2 total | ≤ 500 KB (6 weight) | ✅ GH-003, AC-D03, TASK-4.X |
| SemiBold factor | 0.67 (±0.005 test tolerance) | ✅ FR-4.1/REQ-I01/Plan TASK-0.10 |
| Discontinuity threshold | 15.0° (kalibrasi PoC) | ✅ REQ-H06, §11.2, Plan TASK-1.3 |
| Timeline | 14–18 minggu (6 fase) | ✅ PRD §9.2 ↔ Plan Phase 0–5 (mapping 1:1) |
| Effort harmonisasi | 140–240 jam | ✅ PRD §8.3/§9.1, Plan DEP-002 |
| Ukuran Sources/Harmonized | 4–8 MB | ✅ PRD §8.2, Spec INF-002/003 |
| Subset PoC | ~40–50 glyph (26+6+3+4+3–5 = 39–44) | ✅ FR-2.1, AC-P01 |

## 4. 📝 Action Plan (Corrective Actions)

_Clear checklist for the user to fix before invoking `/sdlc-write-code`._

### Updates Required

- [ ] **Spec** (`spec/spec-multi-weight-variants.md` → v1.4, via `/sdlc-define-specs`):
  - Terapkan amendemen r2 §4 yang belum masuk: **REQ-I02** (A2), **REQ-H06/§11.2** (hasil kalibrasi), **§4.6** (A4 + nilai factor stretch final), **§4.11** (A8), **§4.12** (A5), **§6.2** (A1 + catatan E0.2), **§6.3** (A6), **§6.5** (A7), **GUD-003/AC-B05** (A3), **§8.5** (A9).
  - Tambahan baru: **§4.9** — RUN chain harus memuat `RUN pytest tests/` (fail-fast sebelum interpolasi, TASK-4.2) (B7); **§4.7** — penyelarasan jumlah pemanggilan `features.py` per `.sfdir` (C1).
- [ ] **PRD** (`docs/prd-20260731-1000-multi-weight-variants.md` → v1.4, via `/sdlc-draft-prd`):
  - Terapkan amendemen r2: **GH-004 AC#5** (A3), **catatan interpretasi FR-2.4** (A10), **§8.1 + E0.1** (A11).
  - Tambahan baru: **FR-7.2** (B2), **GH-004 AC#3** (B3), **GH-005 AC#2** (B4), **FR-7.1** (B5), **§9.2 Phase 3** (B6), **path `scripts/` → `Scripts/`** (D3).
- [ ] **Plan** (`plan/plan-feature-multi-weight-variants-v1.3.md` — pertimbangkan rename ke `-v1.7`):
  - Perbaiki **`audit_reference`** yang menggantung (B1) — rujuk laporan ini (`docs/audit/consistency-audit-plan-vs-prd-spec-2026-08-01.md`).
  - Perbaiki domain language: **D1** ("upstream release pipeline" → "release upstream pipeline"), **D2** ("varian bobot statis (static instances)" → "static weight").
  - Perluas §1 dengan GUD-001/GUD-002 (dan sebutkan CON-003/004/007/008, SEC-001/002 sebagai konstrain yang dihormati).
  - Perluas §8 Related Specifications: tambahkan laporan r2 dan laporan audit ini.
- [ ] **Standards (ADR/Context):** Tidak ada perubahan — `CONTEXT.md` & format ADR sudah compliant; **tidak ada ADR baru** yang diperlukan (kesimpulan r2 dikonfirmasi).

### Approval Status: **REQUIRED**

Overall status **FAIL** → proses menuju `/sdlc-write-code` **diblokir** sampai amendemen Spec & PRD diterapkan dan re-audit lulus. Tidak ada temuan *scope creep* atau *missing coverage* — seluruh perbaikan bersifat mekanis dan sebagian besar sudah terjadwal di Plan v1.7.

## 5. 📎 References

- PRD under audit: `docs/prd-20260731-1000-multi-weight-variants.md` (v1.3)
- Spec under audit: `spec/spec-multi-weight-variants.md` (v1.3)
- Plan under audit: `plan/plan-feature-multi-weight-variants-v1.3.md` (v1.7)
- Domain Glossary: `CONTEXT.md`
- ADRs: `docs/adr/0001`, `0002`, `0003`
- Audit PRD sebelumnya: `docs/audit/consistency-audit-multi-weight-variants-2026-07-31.md`
- Klarifikasi: `docs/audit/clarification-report-multi-weight-variants-2026-07-31.md`, `clarification-report-implementation-plan-multi-weight-variants-2026-07-31.md` (r1), `...-r2.md`
- Standards: `.agents/standards/CONTEXT-FORMAT.md`, `.agents/standards/ADR-FORMAT.md`
- Audit Template: `.agents/skills/sdlc-audit-consistency/references/AUDIT-REPORT-TEMPLATE.md`
