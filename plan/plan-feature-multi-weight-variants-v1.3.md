---
goal: Multi-Weight Font Variants for Fantasque Sans Mono
version: 1.6
date_created: 2026-07-31
last_updated: 2026-07-31
owner: Fantasque Sans Mono Core Team
status: 'Planned'
tags: [feature, architecture, interpolation, type-design]
upstream_prd: docs/prd-20260731-1000-multi-weight-variants.md
upstream_spec: spec/spec-multi-weight-variants.md
audit_reference: docs/audit/consistency-audit-plan-vs-prd-spec-2026-07-31.md
clarification_reference: docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-07-31.md
---
<!-- markdownlint-disable -->

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-lightgrey)

This plan outlines the step-by-step execution to implement Multi-Weight Font Variants (Medium, SemiBold, Light, ExtraBold) for Fantasque Sans Mono via FontForge master harmonization and linear interpolation. The execution strictly preserves legacy source files (CON-001) and integrates with the existing Custom Build Workflow. Stretch weights (Light 300, ExtraBold 800) only ship via the upstream release pipeline after core weights pass visual review (E10) — Custom Build produces core weights only.

## 1. Requirements & Constraints

- **REQ-H01 to H06**: Master Harmonization & Visual Invariants
- **REQ-I01 to I07**: Multi-Weight Interpolation, Auto-Hinting, and Metric Preservation
- **REQ-B01 to B06**: Build Pipeline Integration (Pre-processing in Stage 1)
- **REQ-D01 to D04**: Output Formats, File Naming, and Release Packaging
- **REQ-S01 to S05**: Specimen Sheet & Visual QA Validation
- **CON-001**: Legacy Code Preservation (build.py, fontbuilder.py, features.py MUST NOT be modified)
- **CON-002**: Workflow A — FontForge Interpolation Only
- **CON-005**: Vertical Metrics Freeze (Ascent, Descent, LineGap MUST NOT change)
- **CON-006**: No Italic instances generated for new weights (Faux Italic fallback)
- **GUD-003**: Progress Logging — Build log MUST display progress per stage
- **GUD-004**: Partial Success Tolerance — Stretch weight failure does NOT fail entire build

## 2. Implementation Steps

> **EXECUTION DIRECTIVE FOR AI AGENTS:**
> You MUST execute this plan phase by phase. You MUST run the specific testing/verification task at the end of each phase. After a phase is tested, you **MUST STOP AND WAIT** for the user's explicit approval before proceeding to the next phase.

### Implementation Phase 0: Tooling & PoC Preparation

- GOAL-001: Membangun fondasi *script* otomatis (deteksi, validasi, spesimen, interpolasi), menyusun standar kualitas visual, dan menyiapkan infrastruktur pengujian sebelum pekerjaan manual dimulai.

| Task      | Description                                                                  | Ref ID  | AC Ref | Dep   | Files | Completed | Date |
| --------- | ---------------------------------------------------------------------------- | ------- | ------ | ----- | ----- | --------- | ---- |
| TASK-0.0  | Buat *branch* Git terisolasi `feature/multi-weight-poc`                      | -       | -      | -     | -     |           |      |
| TASK-0.1  | Buat `Scripts/detect_incompatibility.py` (Deteksi kontur)                    | REQ-H01 | AC-H01 | -     | 1     |           |      |
| TASK-0.2  | Buat `Scripts/validate_harmonization.py` (Validasi node & kontur)            | REQ-H02 | -      | -     | 1     |           |      |
| TASK-0.3  | Buat `Scripts/validate_interpolation.py` (Validasi hasil interpolasi)        | REQ-S05 | AC-I08 | -     | 1     |           |      |
| TASK-0.4  | Buat `Scripts/generate_specimen.py` (Generator HTML *waterfall*)             | REQ-S01 | AC-S01 | -     | 1     |           |      |
| TASK-0.5  | Buat `docs/audit/visual-quality-rubric.md` & `Sources/Harmonized/tracking.json` | -       | AC-P03 | -     | 2     |           |      |
| TASK-0.6  | Buat `Scripts/poc_interpolation.py` (Script interpolasi subset)              | REQ-I01 | AC-P02 | -     | 1     |           |      |
| TASK-0.7  | Buat `Scripts/multi_weight_driver.py` (Interpolasi & Assembly): flag `--enable-light`/`--enable-extrabold` (HANYA dipakai release upstream, E10 — bukan `--include-stretch`), TIDAK memanggil `features.py` & TIDAK menjalankan `ttfautohint` (Spec §4.6), injeksi metadata internal (os2_weight, fullname) sebelum menyimpan `.sfdir`, copy-as-fallback + hmtx copy, assembly `build/sources/` (REQ-B06) | REQ-B06 | AC-B02 | -     | 1     |           |      |
| TASK-0.8  | Buat `tests/test_detect_incompatibility.py` (Unit test deteksi kontur)       | Spec §6.3 | -   | TASK-0.1 | 1  |           |      |
| TASK-0.9  | Buat `tests/test_validate_harmonization.py` (Unit test validasi harmonisasi) | Spec §6.3 | -   | TASK-0.2 | 1  |           |      |
| TASK-0.10 | Buat `tests/test_multi_weight_driver.py` — 10 test case Spec §6.3 (factor 0.5 & ~0.67, copy-as-fallback, hmtx copy, no-ttfautohint, dry-run, missing-master, assembly naming, FantasqueSans copy) | Spec §6.3 | -   | TASK-0.7 | 1  |           |      |
| TASK-0.11 | Jalankan eksperimen E0.1 (Idempotensi) & E0.2 (Advance Width)                | REQ-I03 | AC-P05 | -     | -     |           |      |
| TASK-0.12 | Jalankan eksperimen E0.3 (Simulasi paralel 2-designer)                       | -       | AC-P01 | -     | -     |           |      |
| TASK-0.X  | **VERIFY**: Jalankan semua script validasi dengan dummy input + seluruh unit test (`pytest`) memastikan tidak ada *syntax error* dan test *passing*. | - | - | - | - |        |      |
| TASK-0.Y  | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 1      | -       | -      | -     | -     |           |      |

### Implementation Phase 1: Proof of Concept (MVP)

- GOAL-002: Memvalidasi kelayakan harmonisasi dan interpolasi pada subset terbatas (~40-50 *glyph* kritis) sebelum eksekusi massal.

| Task     | Description                                                     | Ref ID  | AC Ref | Dep      | Files | Completed | Date |
| -------- | --------------------------------------------------------------- | ------- | ------ | -------- | ----- | --------- | ---- |
| TASK-1.1 | Harmonisasi manual ~40-50 *glyph* untuk pasangan Regular ↔ Bold | REQ-H03 | AC-P01 | TASK-0.2 | 1-2   |           |      |
| TASK-1.2 | Interpolasi subset ke Medium (500) menggunakan `poc_interpolation.py` — TANPA `ttfautohint` (hinting hanya di Stage 2, Spec §8.5; perbandingan visual adil pada level rendering yang sama: kedua font belum di-*hint*) | REQ-I01 | AC-P02 | TASK-1.1 | -     |           |      |
| TASK-1.3 | Hasilkan Specimen Sheet HTML untuk hasil interpolasi Medium     | REQ-S02 | AC-P06 | TASK-1.2 | 1     |           |      |
| TASK-1.X | **VERIFY**: Laporan `validate_interpolation.py` menunjukkan >=90% lulus *visual rubric*. | -       | AC-P03 | -        | -     |           |      |
| TASK-1.Y | **APPROVAL**: Wait for explicit user confirmation (PoC Lulus) to proceed to Phase 2. Jika GAGAL, ikuti salah satu dari 4 jalur keputusan FR-2.5: (1) Iterasi harmonisasi ulang pada subset PoC — maksimal 2 siklus tambahan, (2) Revisi cakupan V1 — batasi hanya Medium+SemiBold tanpa *stretch weight*, (3) Re-evaluasi keputusan tooling — pertimbangkan percepatan migrasi ke Workflow B (UFO/`fontmake`), (4) Penundaan/penghentian fitur — jika ketiga opsi di atas tidak layak. Keputusan akhir WAJIB didokumentasikan sebagai catatan pada PRD (revisi minor) atau ADR baru. | - | AC-P07 | - | - | | |

### Implementation Phase 2: Full Master Harmonization (Core Experience)

- GOAL-003: Melakukan harmonisasi manual pada seluruh *glyph* Regular ↔ Bold dan Italic ↔ BoldItalic (pekerjaan utama *type designer*).

| Task      | Description                                                                                          | Ref ID  | AC Ref | Dep      | Files | Completed | Date |
| --------- | ---------------------------------------------------------------------------------------------------- | ------- | ------ | -------- | ----- | --------- | ---- |
| TASK-2.1  | Harmonisasi manual Regular ↔ Bold — Designer A (Lead): Latin/Cyrillic/Greek (~70% *glyph*)           | REQ-H03 | AC-H04 | TASK-1.Y | 2     |           |      |
| TASK-2.2  | Harmonisasi manual Italic ↔ BoldItalic — Designer B (Support): Latin/Cyrillic/Greek (~25% *glyph*)   | REQ-H03 | AC-H05 | TASK-1.Y | 2     |           |      |
| TASK-2.3  | **Shared pool** (Symbols, ligatures, PUA, box-drawing — ~5%): *first-come-first-served* via Git branch terisolasi, dikerjakan bersamaan dengan TASK-2.1 & 2.2. Jika *deadlock*, eskalasi ke *upstream maintainer*. | PRD §9.1 | - | TASK-1.Y | - | | |
| TASK-2.4  | *Visual spot-check* per *glyph family* (misal: semua *arrow glyphs*, *bracket glyphs*, *currency glyphs*) secara berkala selama harmonisasi berlangsung | PRD §9.2 | - | TASK-1.Y | - | | |
| TASK-2.X  | **VERIFY**: `validate_harmonization.py` menunjukkan `pass_rate >= 98%` untuk kedua pasangan master.  | -       | AC-H02 | -        | -     |           |      |
| TASK-2.Y  | **APPROVAL**: Wait for explicit user confirmation to proceed to Phase 3                              | -       | -      | -        | -     |           |      |

### Implementation Phase 3: Multi-Weight Interpolation & QA (Resilience)

- GOAL-004: Menghasilkan **core weights** (Medium 500, SemiBold 600), melakukan pasca-pemrosesan (hmtx & assembly), QA visual menyeluruh, dan *iterative fix loop*. *Stretch weights* (Light, ExtraBold) ditangguhkan ke *release upstream pipeline* (Spec §4.6/§8.5, E10).

| Task     | Description                                                                                          | Ref ID  | AC Ref | Dep      | Files | Completed | Date |
| -------- | ---------------------------------------------------------------------------------------------------- | ------- | ------ | -------- | ----- | --------- | ---- |
| TASK-3.1 | Eksekusi `multi_weight_driver.py` untuk **Core Weights only** (Medium 500 + SemiBold 600) — tanpa flag `--enable-light`/`--enable-extrabold` (stretch HANYA di release upstream, E10); driver meng-inject metadata internal (os2_weight, fullname) sebelum menyimpan `.sfdir` | REQ-I01 | AC-I01 | TASK-2.Y | -     |           |      |
| TASK-3.2 | Hasilkan Full Specimen Sheet (HTML) untuk seluruh **core weight** — termasuk informasi metrik: *stem width*, *x-height*, *cap height*, *advance width* per weight. QA visual pra-*hinting* via specimen sheet HTML + FontForge rendering preview (TTX/text-mode) — cukup untuk mendeteksi distorsi kontur & *discontinuity* sebelum hinting (Spec §8.5) | REQ-S02 | AC-S02, AC-S04 | TASK-3.1 | - | | |
| TASK-3.3 | **Iterative fix loop** (core weights): *Glyph* gagal *visual review* → harmonisasi ulang (FR-5.3) → interpolasi ulang → validasi ulang. Ulangi hingga <=2% *minor artifact* dan 0 distorsi berat. | FR-5.3 | AC-I06 | TASK-3.2 | - | | |
| TASK-3.4 | *Gate Check* cakupan V1: *Stretch weight* (Light, ExtraBold) **TIDAK diproduksi di fase ini** — Custom Build hanya membangun 4 core weight + output existing (Spec §4.6/§8.5, E10). Keputusan kelolosan *stretch weight* (*partial success*, GUD-004) dialihkan ke *release upstream pipeline*. Proyek **tidak dianggap gagal** jika stretch weight tidak rilis di V1. | REQ-I02 | - | TASK-3.3 | - | | |
| TASK-3.X | **VERIFY**: `validate_interpolation.py` melaporkan <= 2% *minor artifact* (`warning`) dan 0 distorsi berat (`fail`) pada **core weights**. *Advance width* seluruh core weight identik (REQ-I03/I05). *Counter* tidak tertutup, *stem width* proporsional (REQ-I07/AC-I07). *Ligature* (`->`, `=>`, `!=`, dll.) berfungsi benar di semua core weight (AC-I05). Metadata internal (os2_weight, fullname) core weight ter-inject benar dan tidak bentrok dengan master. | - | AC-I05, AC-I06, AC-I07 | - | - | | |
| TASK-3.Y | **APPROVAL**: Wait for explicit user confirmation (Final QA) to proceed to Phase 4                   | -       | -      | -        | -     |           |      |

### Implementation Phase 4: Pipeline Integration & Release (Polish)

- GOAL-005: Integrasi pipeline interpolasi ke Custom Build Workflow di GitHub Actions dan perilisan resmi.

| Task     | Description                                                                                          | Ref ID  | AC Ref | Dep      | Files | Completed | Date |
| -------- | ---------------------------------------------------------------------------------------------------- | ------- | ------ | -------- | ----- | --------- | ---- |
| TASK-4.1 | Modifikasi `Scripts/configure.py` tambah `--form-enable-multi-weight` (boolean, default `false`) — mapping ke flag driver `--multi-weight` via pola `FORM_KEY_TO_OPTION`/`OPTION_TO_DRIVER_FLAG` (Spec §4.9). Catatan: `configure.py` TIDAK dilindungi CON-001 (dikelola Custom Build Spec; minor update cross-spec — PRD §8.1, audit C5) | REQ-B02 | AC-B01 | TASK-3.Y | 1     |           |      |
| TASK-4.2 | Modifikasi `Dockerfile` (Stage 1 RUN conditional block) — kontrak RUN chain Spec §4.9: `detect_incompatibility.py` → `validate_harmonization.py --strict` → `multi_weight_driver.py` (TANPA flag stretch) → `custom_build_driver.py` dengan `FONTS=build/sources`; mode `false` → `FONTS=Sources` → output byte-identical (AC-B03) | REQ-B02 | AC-B02 | TASK-4.1 | 1     |           |      |
| TASK-4.3 | Update `.github/workflows/custom-build.yml` — parameter boolean `enable_multi_weight` (default `false`); stretch weight TIDAK dibangun di Custom Build (E10); tanpa step baru — murni *flag forwarding* ke `configure.py` | REQ-B02 | AC-B01 | TASK-4.1 | 1     |           |      |
| TASK-4.4 | Modifikasi `Scripts/packaging.sh` — daftar weight per mode: Custom Build → `Regular, Medium, SemiBold, Bold, Italic, BoldItalic` (stretch TIDAK pernah disertakan, E10); mode `false` → `Regular, Bold, Italic, BoldItalic, FantasqueSans` (kompatibilitas mundur penuh); release upstream → + `Light`/`ExtraBold` hanya jika lolos visual review (FR-6.3). Archive release 3 format terpisah: TTF .zip, OTF .zip, WOFF2 .zip (REQ-D03, AC-D01) | REQ-B05, REQ-D03 | AC-B06, AC-D01 | TASK-4.2 | 1 | | |
| TASK-4.5 | Update dokumentasi (`README.md` — termasuk *section* "Faux Italic Limitations" dengan tabel kompatibilitas platform + contoh CSS `@font-face`, `Specimen/`) | REQ-D04 | AC-S03, AC-D04, AC-D05 | TASK-4.4 | 2 | | |
| TASK-4.X | **VERIFY**: Eksekusi lokal *Custom Build pipeline* menggunakan mode docker (`enable_multi_weight=true` dan `false`) sukses dan deterministik (AC-B03). Build log menampilkan progres per tahap sesuai GUD-003 (AC-B05). Total durasi build ≤ 240 menit (SM-T3/REQ-B04). WOFF2 ≤ 500 KB (AC-D03). WOFF2 kompatibel dengan `@font-face` CSS (AC-D02). Font terinstal dengan benar di Windows/macOS/Linux (AC-I02) dan muncul dengan nama benar di *font picker* (AC-I03). **Hinting**: weight baru di-`ttfautohint` di Stage 2 dengan hasil konsisten untuk semua core weight — terlepas dari opsi `UseHinted` (REQ-I04, FR-4.3, Spec §8.5). | - | AC-B03, AC-B05, AC-I02, AC-I03, AC-D02, AC-D03 | - | - | | |
| TASK-4.Y | **APPROVAL**: Wait for explicit user confirmation to finalize implementation                         | -       | -      | -        | -     |           |      |

### Implementation Phase 5: Buffer — Iteration & Stabilization (Optional)

- GOAL-006: Menyediakan *slack time* untuk iterasi harmonisasi ulang, perbaikan *visual review* lanjutan, dan stabilisasi build. Fase ini hanya aktif jika diperlukan berdasarkan hasil Phase 3 atau 4.
- **Durasi**: 4 minggu (Minggu 15–18, sesuai PRD §9.2 "Buffer Phase")
- **Trigger**: Diaktifkan jika Phase 3 menemukan >2% *glyph* dengan *minor artifact*, jika harmonisasi ulang tambahan diperlukan (termasuk persiapan *stretch weight* untuk *release upstream*), atau jika pipeline build memerlukan stabilisasi pasca-integrasi.

| Task     | Description                                                                  | Ref ID | AC Ref | Dep      | Files | Completed | Date |
| -------- | ---------------------------------------------------------------------------- | ------ | ------ | -------- | ----- | --------- | ---- |
| TASK-5.1 | Harmonisasi ulang *glyph* bermasalah (dari backlog TASK-3.3)                 | FR-5.3 | AC-I06 | TASK-3.4 | 1-2   |           |      |
| TASK-5.2 | Interpolasi ulang + validasi ulang untuk *glyph* yang direvisi               | REQ-I01 | AC-I06 | TASK-5.1 | -     |           |      |
| TASK-5.3 | Stabilisasi dan optimasi build pipeline (jika diperlukan)                    | REQ-B04 | AC-B04 | TASK-4.X | 1-2   |           |      |
| TASK-5.4 | Produksi *stretch weights* (Light 300, ExtraBold 800) di **release upstream pipeline** via `multi_weight_driver.py --enable-light --enable-extrabold` — hanya setelah core weights lolos *visual review* (Spec §4.6, E10). *Gate check* kelolosan: *stretch weight* gagal *visual review* dikeluarkan dari V1 → V2; proyek tidak dianggap gagal (GUD-004). | REQ-I02 | - | TASK-3.Y | - | | |
| TASK-5.X | **VERIFY**: Seluruh *glyph* lolos validasi akhir; pipeline stabil dan ≤ 240 menit; *stretch weight* yang lolos memenuhi *visual rubric* dan yang gagal dikeluarkan dari V1 (GUD-004). | -       | -      | -        | -     |           |      |
| TASK-5.Y | **FINAL APPROVAL**: Konfirmasi eksplisit bahwa implementasi selesai dan siap rilis. | -       | -      | -        | -     |           |      |

## 3. Alternatives

- **ALT-001 (Workflow B - UFO/fontmake)**: Menggunakan ekosistem modern UFO v3 dan `fontmake`. Ditolak untuk V1 karena mengubah struktur repository terlalu radikal; akan dieksplorasi di V2.
- **ALT-002 (Single-file Variable Font)**: Membuat font variabel dengan sumbu `wght`. Ditolak untuk V1 karena memerlukan migrasi penuh ke UFO; V1 hanya berfokus pada varian bobot statis (static instances).
- **ALT-003 (Stroke modification algorithms)**: Menggunakan algoritma tebal/tipis otomatis seperti `font.changeWeight()`. Ditolak karena merusak asimetri "wibbly-wobbly" (counter space dan handwritten detail).

## 4. Dependencies

- **DEP-001**: FontForge Python 3 API (`fontforge` python module) di ubuntu:26.04.
- **DEP-002**: Tim Type Designer (Designer A & Designer B) untuk melakukan harmonisasi manual yang akan memakan waktu substansial (~140-240 jam).

## 5. Files

- **FILE-001**: `Scripts/detect_incompatibility.py` [NEW]
- **FILE-002**: `Scripts/validate_harmonization.py` [NEW]
- **FILE-003**: `Scripts/validate_interpolation.py` [NEW]
- **FILE-004**: `Scripts/generate_specimen.py` [NEW]
- **FILE-005**: `Scripts/poc_interpolation.py` [NEW]
- **FILE-006**: `Scripts/multi_weight_driver.py` [NEW]
- **FILE-007**: `docs/audit/visual-quality-rubric.md` [NEW]
- **FILE-008**: `Sources/Harmonized/tracking.json` [NEW]
- **FILE-009**: `Scripts/configure.py` [MODIFY]
- **FILE-010**: `Dockerfile` [MODIFY]
- **FILE-011**: `.github/workflows/custom-build.yml` [MODIFY]
- **FILE-012**: `Scripts/packaging.sh` [MODIFY]
- **FILE-013**: `README.md` [MODIFY]
- **FILE-014**: `tests/test_detect_incompatibility.py` [NEW]
- **FILE-015**: `tests/test_validate_harmonization.py` [NEW]
- **FILE-016**: `tests/test_multi_weight_driver.py` [NEW]
- **FILE-017**: `docs/audit/phase0-experiments-{date}.md` [NEW]
- **FILE-018**: `docs/audit/parallel-harmonization-simulation-{date}.md` [NEW]

## 6. Testing

- **TEST-001**: Idempotency & Determinism Test — Memastikan pipeline menghasilkan byte-identical output pada mode non-multi-weight (`enable_multi_weight=false`).
- **TEST-002**: Automated Validation Scripts — `validate_harmonization.py`, `validate_interpolation.py` dengan laporan JSON terstruktur.
- **TEST-003**: Unit Tests (Spec §6.1, §6.3) — `pytest` untuk `test_detect_incompatibility.py`, `test_validate_harmonization.py`, `test_multi_weight_driver.py`.
- **TEST-004**: Visual Quality Review — Menggunakan Specimen Sheet HTML dan Visual Quality Rubric (E0.4).
- **TEST-005**: Integration Test — End-to-End Custom Build workflow (`enable_multi_weight=true` dan `false`) via Docker lokal.
- **TEST-006**: Hinting Verification — Seluruh weight baru di-*hint* di Stage 2 (`ttfautohint`) terlepas dari opsi `UseHinted` (REQ-I04, FR-4.3) dan hasil hinting konsisten antar weight.

## 7. Risks & Assumptions

- **RISK-001**: Harmonization memakan waktu sangat lama (bottle-neck) akibat proses manual yang masif.
- **RISK-002**: Stretch weights (Light, ExtraBold) mungkin tidak memenuhi standar *Visual Quality* karena ekstrapolasi FontForge. Risiko hanya relevan untuk *release upstream pipeline* (Custom Build tidak memproduksi stretch weight — E10); dimitigasi via *gate check* kelolosan: gagal → keluar dari V1 → V2 (*partial success*, GUD-004).
- **ASSUMPTION-001**: `Scripts/features.py` dipastikan deterministik dan idempotent, sehingga dapat dipanggil multiple times tanpa mengubah hasil (divalidasi oleh E0.1).

## 8. Related Specifications / Further Reading

- [PRD - Multi-Weight Variants](../docs/prd-20260731-1000-multi-weight-variants.md)
- [Technical Specification - Multi-Weight Variants](../spec/spec-multi-weight-variants.md)
- [ADR-0003: Workflow A - FontForge v1 Interpolation](../docs/adr/0003-workflow-a-fontforge-v1-interpolation.md)
- [Clarification Report: Implementation Plan - Multi-Weight Variants](../docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-07-31.md)

## 9. Rollback / Recovery Plan

- Jika fase PoC gagal total, seluruh file baru (`Scripts/detect*.py`, dsb.) akan di-*revert* dengan `git revert`, dan parameter build tidak akan di-*merge* ke `master`.
- Jika Custom Build Workflow memunculkan isu regresi pada environment produksi, parameter `enable_multi_weight` pada `.github/workflows/custom-build.yml` akan dinonaktifkan (`hidden`/`false`) sementara *fix* diimplementasikan, karena fallback `false` akan selalu menjalankan *pipeline* legacy yang byte-identical.

## 10. Changelog

| Version | Date       | Changes                                                                                          |
| ------- | ---------- | ------------------------------------------------------------------------------------------------ |
| 1.6     | 2026-07-31 | Sinkronisasi laporan klarifikasi: Phase 3 hanya core weights (stretch → release upstream, E10), hapus TASK-3.2 `ttfautohint` manual (hinting hanya Stage 2, Spec §8.5), renumber TASK-3.x, gate check TASK-3.4 disesuaikan, flag `--enable-light`/`--enable-extrabold`, injeksi metadata driver (TASK-0.7/3.1), kontrak RUN chain Dockerfile & daftar weight packaging per mode (TASK-4.2/4.4), verifikasi hinting Stage 2 di TASK-4.X, tambah TASK-5.4 produksi stretch release upstream, RISK-002 & TEST-006 diperbarui. |
| 1.5     | 2026-07-31 | Observasi minor: tambah verifikasi ligature (AC-I05) ke TASK-3.X, metrik specimen (AC-S04) ke TASK-3.3, archive 3 format (AC-D01) ke TASK-4.4, instalasi font + nama (AC-I02/I03) ke TASK-4.X, perbaiki dependency TASK-2.3 & 2.4 agar konkuren dengan harmonisasi. |
| 1.4     | 2026-07-31 | Konsistensi audit: tambah Buffer Phase 5, unit test tasks, shared pool strategy, visual spot-check, iterative fix loop, perbaikan traceability REQ-ID, pindahkan multi_weight_driver.py ke Phase 0, perkaya TASK-4.X verification, tambah git branch TASK-0.0, perbarui TASK-1.Y dengan 4 jalur keputusan FR-2.5, tambah file unit test & experiment docs, perbarui Testing section. |
| 1.3     | 2026-07-31 | Initial plan draft berdasarkan PRD v1.3 dan Spec v1.3.                                           |
