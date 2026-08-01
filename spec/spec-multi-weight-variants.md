---
title: Technical Specification — Multi-Weight Font Variants for Fantasque Sans Mono
version: 1.5
date_created: 2026-07-31
last_updated: 2026-08-01
owner: Fantasque Sans Mono Core Team
tags: [spec, multi-weight, interpolation, harmonization, fontforge, type-design]
upstream_prd: docs/prd-20260731-1000-multi-weight-variants.md
related_adrs:
  - docs/adr/0002-multi-stage-docker-deferred-engine-port.md
  - docs/adr/0003-workflow-a-fontforge-v1-interpolation.md
audit_reference: docs/audit/consistency-audit-plan-vs-prd-spec-2026-08-01.md
clarification_reference: docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r3.md
---

<!-- markdownlint-disable -->

# Introduction

Dokumen ini adalah Technical Specification untuk inisiatif **Multi-Weight Font Variants** pada Fantasque Sans Mono. Spesifikasi ini mendefinisikan arsitektur pipeline harmonisasi kontur, kontrak interpolasi FontForge, integrasi dengan Custom Build Workflow existing, kontrak data untuk script validasi, spesifikasi specimen sheet, serta acceptance criteria yang terukur. Seluruh keputusan arsitektur dalam dokumen ini mengacu pada ADR-0003 (Workflow A — FontForge Interpolation) dan ADR-0002 (Multi-Stage Docker).

## 1. Purpose & Scope

### 1.1 Purpose

Mendefinisikan kontrak teknis, arsitektur pipeline, skema direktori, dan acceptance criteria yang diperlukan untuk menghasilkan 4–6 static weight instances dari master existing (Regular 400 dan Bold 700) melalui master harmonization dan FontForge linear interpolation, tanpa memodifikasi source legacy yang dilindungi CON-001.

### 1.2 Scope

- **In Scope**:
  - Pipeline deteksi inkompatibilitas kontur (FontForge Python API).
  - Pipeline validasi harmonisasi otomatis (`node-count-equal`, `contour-order-equal`, `curve-direction-equal`).
  - Arsitektur direktori harmonized sources (`Sources/Harmonized/`).
  - Script interpolasi multi-weight (`font.interpolateFonts()`).
  - Integrasi dengan Custom Build Workflow existing melalui parameter `enable_multi_weight`.
  - Strategi pemanggilan `features.py` in-process oleh `custom_build_driver.py` existing — satu kali per `.sfdir` di build source (REQ-B03, §4.7).
  - Generator specimen sheet HTML untuk visual review.
  - Pipeline auto-hinting (`ttfautohint`) untuk seluruh weight baru.
  - Strategi copy-as-fallback untuk glyph tanpa pasangan di master target.
  - Pembaruan `packaging.sh` untuk multi-weight output directory.
  - Eksperimen validasi Phase 0 (E0.1–E0.4).

- **Out of Scope (Deferred to V2)**:
  - Variable Font (VF) dengan sumbu `wght` — memerlukan migrasi ke UFO/`fontmake` (Workflow B).
  - Spike research migrasi toolchain (GH-006) — ADR perbandingan Workflow A vs B, PoC konversi satu glyph ke UFO v3, dan daftar blocker/unknowns adalah deliverable V2 Preview, bukan deliverable V1 (lihat §12).
  - Italic instances untuk weight baru (Medium Italic, SemiBold Italic, dll.) — V1 menggunakan faux italic.
  - Weight di luar rentang 300–800 (Thin 100, ExtraLight 200, Black 900).
  - Modifikasi pada `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py` (CON-001).
  - Penggunaan `font.changeWeight()` atau algoritma stroke modification otomatis.

## 2. Definitions

Seluruh istilah dalam dokumen ini mengacu pada Domain Glossary proyek ([`CONTEXT.md`](../CONTEXT.md)) klaster **Multi-Weight Variants**. Istilah tambahan yang spesifik untuk spesifikasi ini:

- **Interpolation Factor**: Nilai float antara 0.0 (Regular) dan 1.0 (Bold) yang menentukan posisi weight pada sumbu interpolasi linear. Factor untuk extrapolation (Light, ExtraBold) berada di luar rentang [0.0, 1.0].
- **Copy-as-Fallback**: Strategi penanganan glyph yang ada di satu master namun tidak ada di master target — glyph disalin langsung dari master sumber ke output weight baru tanpa interpolasi.
- **Contour Incompatibility**: Kondisi di mana dua glyph dari master berbeda tidak dapat diinterpolasi karena perbedaan jumlah node, urutan kontur, atau arah kurva.
- **Discontinuity**: Perubahan arah kurva Bézier yang tidak mulus (sudut tajam) pada titik sambungan antar node, terdeteksi oleh script validasi otomatis.
- **Specimen Sheet**: Dokumen HTML yang menampilkan waterfall teks multi-ukuran untuk seluruh weight baru, digunakan sebagai alat bantu visual review oleh type designer.
- **Hard Invariant**: Aturan visual di mana glyph hasil harmonisasi HARUS identik secara visual dengan master asli pada ukuran 8–24 pt.
- **Soft Invariant**: Aturan visual di mana glyph hasil harmonisasi BOLEH memiliki deviasi minor pada ukuran 24–72 pt, selama tidak ada discontinuity.
- **Build Source Assembly**: Direktori sementara `build/sources/` yang menyusun seluruh `.sfdir` yang akan dibuild oleh driver existing — 4 harmonized masters + 2–4 interpolated weights dengan nama `FantasqueSansMono-{Weight}.sfdir` + salinan `FantasqueSans.sfdir` (REQ-B06). Nama direktori menentukan nama file output (REQ-D02).
- **Interpolation Validation Report**: Laporan JSON dari `validate_interpolation.py` dengan status `pass`/`warning`/`fail` per glyph hasil interpolasi, mengacu pada Visual Quality Rubric (E0.4) — kontrak lengkap di §4.11.
- **Harmonization Tracking File**: File JSON `Sources/Harmonized/tracking.json` yang menandai status harmonisasi per glyph (`needs_harmonization` → `approved`), digunakan type designer untuk koordinasi dan input harmonisasi ulang (GH-005 AC#4, kontrak di §4.12).

## 3. Requirements, Constraints & Guidelines

### 3.1 Requirements

#### Master Harmonization

- **REQ-H01 (Contour Detection)**: Sistem HARUS menyediakan script yang mendeteksi inkompatibilitas kontur antara dua master (Regular↔Bold dan Italic↔BoldItalic) — membandingkan jumlah node, urutan kontur, dan arah kurva per glyph — dan menghasilkan laporan JSON yang mencantumkan setiap glyph dengan status `compatible` atau `incompatible`.
- **REQ-H02 (Validation Script)**: Sistem HARUS menyediakan script validasi otomatis yang memverifikasi tiga kondisi untuk setiap pasangan glyph: `node-count-equal`, `contour-order-equal`, dan `curve-direction-equal`. Output berupa laporan JSON dengan status `pass`/`fail` per glyph.
- **REQ-H03 (Harmonized Source Storage)**: Hasil harmonisasi HARUS disimpan dalam direktori `.sfdir` baru di `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}/`, terpisah dari source legacy. Struktur `.sfdir` mengikuti format existing — satu file `.glyph` per glyph.
- **REQ-H04 (Copy-as-Fallback)**: Untuk glyph yang ada di satu master namun tidak ada di master target, sistem HARUS menerapkan strategi copy-as-fallback: glyph disalin langsung dari master sumber ke output weight baru tanpa interpolasi. Tidak ada glyph yang hilang dari output.
- **REQ-H05 (Visual Invariant — Hard)**: Glyph hasil harmonisasi HARUS identik secara visual dengan master asli pada ukuran 8–24 pt — tidak ada perbedaan yang terlihat pada hasil render.
- **REQ-H06 (Visual Invariant — Soft)**: Glyph hasil harmonisasi BOLEH memiliki deviasi minor pada ukuran 24–72 pt, selama tidak ada discontinuity (sudut tajam atau perubahan arah mendadak) pada kurva Bézier. Discontinuity didefinisikan secara operasional sebagai perubahan tangent arah antar node **> 15.0°** (threshold awal; **protokol dua-pass (klarifikasi r3 — K7)**: (1) validasi dijalankan dengan threshold awal 15.0° via parameter eksplisit `--threshold` pada `validate_interpolation.py` (§4.11) → laporan R1; (2) selama visual diff review (FR-2.3), Designer A + maintainer menilai apakah threshold menangkap seluruh sudut tajam pada ukuran soft-invariant → nilai final `T_final`; (3) validasi dijalankan ulang dengan `--threshold T_final` → laporan R2; (4) gate PoC (AC-P03) dan gate build (§4.9) dievaluasi pada **R2**. Nilai final direkam di `docs/audit/phase0-experiments-{date}.md` dan `docs/audit/visual-quality-rubric.md`, lalu §11.2 diperbarui sesuai hasil kalibrasi).

#### Multi-Weight Interpolation

- **REQ-I01 (Core Weight Interpolation)**: Sistem HARUS menghasilkan empat core weight statis melalui interpolasi dari master yang telah diharmonisasikan:
  - **Regular (400)**: Master asli yang telah diharmonisasikan.
  - **Medium (500)**: Interpolasi dengan factor 0.5 antara Regular↔Bold.
  - **SemiBold (600)**: Interpolasi dengan factor ~0.67 antara Regular↔Bold.
  - **Bold (700)**: Master asli yang telah diharmonisasikan.
- **REQ-I02 (Stretch Weight Extrapolation)**: Sistem HARUS menghasilkan dua stretch weight statis melalui ekstrapolasi (factor eksak ditentukan **sebelum produksi stretch (Phase 5)** oleh Designer A (Lead) + upstream maintainer berdasarkan trial ekstrapolasi pada subset glyph kritis; hasil dicatat di `docs/audit/stretch-factor-decision-{date}.md` dan menjadi kontrak via amendemen §4.6 — selaras dengan FR-2.2 yang menetapkan PoC hanya Medium):
  - **Light (300)**: Ekstrapolasi ke arah lebih ringan dari Regular (factor negatif).
  - **ExtraBold (800)**: Ekstrapolasi ke arah lebih berat dari Bold (factor > 1.0).
- **REQ-I03 (Advance Width Preservation)**: Seluruh weight baru HARUS memiliki advance width yang identik dengan master Regular dan Bold. Jika interpolasi FontForge menghasilkan deviasi, script HARUS mem-post-process dengan menyalin tabel `hmtx` (horizontal metrics) dari master Regular ke weight baru.
- **REQ-I04 (Auto-Hinting)**: Setiap weight baru HARUS melewati `ttfautohint` untuk menghasilkan TrueType bytecode hinting yang konsisten. Eksekusi `ttfautohint` terjadi di **Stage 2** (packaging, per ADR-0002 — Stage 2 adalah satu-satunya stage yang boleh memanggil `ttfautohint`); `multi_weight_driver.py` TIDAK menjalankan hinting. Untuk weight baru, hinting WAJIB dilakukan **terlepas dari opsi `UseHinted`** (FR-4.3 mengalahkan `UseHinted=false` untuk weight baru; weight existing tetap mengikuti `UseHinted` — lihat §8.5). **Mekanisme override di packaging (klarifikasi r3 — K9)**: `packaging.sh` (§4.10) mengenali file weight baru (Medium, SemiBold; + Light, ExtraBold di mode release) dan menjalankan `ttfautohint` padanya **selalu**, terlepas nilai `UseHinted` yang dibaca dari manifest via `jq`; weight existing (Regular, Bold, Italic, BoldItalic, FantasqueSans) tetap mengikuti `UseHinted` (perilaku existing — hinting terkondisi di `Scripts/packaging.sh`).
- **REQ-I05 (Monospace Guarantee)**: Seluruh weight baru HARUS mempertahankan lebar karakter (advance width) yang identik — teks yang sama menempati jumlah kolom yang sama saat weight diganti di editor monospace.
- **REQ-I06 (Ligature Compatibility)**: Seluruh ligature existing (`->`, `=>`, `!=`, dll.) HARUS berfungsi identik di seluruh weight baru. Jika ligature tertentu rusak akibat interpolasi, glyph tersebut harus dikeluarkan dari output dan dikembalikan ke tahap harmonisasi.
- **REQ-I07 (Proportional Stem & Counter)**: Setiap weight baru HARUS memiliki stem width dan counter size yang proporsional terhadap posisinya pada sumbu Regular–Bold — tidak boleh ada glyph dengan counter tertutup atau stroke yang bertabrakan (FR-4.2). Verifikasi dilakukan melalui interpolation validation report (REQ-S05) dan checklist Visual Quality Rubric (E0.4).

#### Build Pipeline Integration

- **REQ-B01 (Pre-Interpolation Architecture)**: Multi-weight interpolation HARUS berjalan sebagai tahap pre-processing yang menghasilkan file `.sfdir` untuk setiap weight baru SEBELUM pipeline variant expansion existing (LargeLineHeight, NoLoopK). Weight baru menjadi source `.sfdir` tambahan yang di-feed ke pipeline existing.
- **REQ-B02 (Custom Build Parameter)**: Custom Build Workflow (`.github/workflows/custom-build.yml`) HARUS memiliki parameter boolean `enable_multi_weight` pada `workflow_dispatch`. Ketika `true`, pipeline multi-weight dijalankan; ketika `false`, hanya Regular + Bold (kompatibilitas mundur pipeline).
- **REQ-B03 (features.py Invocation)**: Pemanggilan `Scripts/features.py` dilakukan **in-process oleh `custom_build_driver.py` existing** — satu kali per weight source di direktori build source (`build/sources/`), mencakup seluruh weight baru (Regular, Medium, SemiBold, Bold, Italic, BoldItalic, + stretch jika aktif). `multi_weight_driver.py` TIDAK memanggil `features.py` langsung — cukup memastikan seluruh `.sfdir` tersedia sebelum driver existing dijalankan. `features.py` TIDAK dimodifikasi (CON-001). **Koreksi terhadap PRD §8.1**: pemanggilan 6× via subprocess tidak diperlukan karena driver existing sudah memanggil `update_features()` in-process untuk setiap `.sfdir` yang dibuild (terverifikasi di `Scripts/custom_build_driver.py`); prinsip determinisme (E0.1) tetap berlaku.
- **REQ-B04 (Build Duration)**: Total durasi build multi-weight TIDAK BOLEH melebihi 240 menit pada GitHub Actions free-tier runner (ubuntu-latest).
- **REQ-B05 (Packaging Update)**: `Scripts/packaging.sh` HARUS diperbarui untuk mengenali struktur direktori multi-weight output dan menyertakan seluruh weight dalam archive release.
- **REQ-B06 (Build Source Assembly)**: Di dalam Stage 1 (tahap pre-compilation, sebelum pemanggilan `custom_build_driver.py`), pipeline multi-weight HARUS menyusun direktori build source sementara `build/sources/` berisi: (a) 4 harmonized masters dengan nama konvensi `FantasqueSansMono-{Regular,Bold,Italic,BoldItalic}.sfdir` (disalin dari `Sources/Harmonized/`), (b) 2–4 interpolated weights dengan nama `FantasqueSansMono-{Medium,SemiBold[,Light,ExtraBold]}.sfdir` (dari `Sources/Harmonized/Interpolated/`), dan (c) salinan `FantasqueSans.sfdir` (proportional variant, tanpa harmonisasi). Driver existing kemudian dipanggil dengan `SOURCES_DIR=build/sources` — argumen posisional yang sudah didukung (`custom_build_driver.py <sources_dir> <output_dir> [options]`). Driver existing TIDAK dimodifikasi (selaras dengan CON-001). Nama direktori di `build/sources/` menentukan nama file output (`FantasqueSansMono-{Weight}.{ext}`) — memenuhi REQ-D02. Assembly dilakukan oleh `multi_weight_driver.py` saat build-time (§4.6). Pada mode single-weight (`enable_multi_weight=false`), assembly TIDAK dilakukan — driver dipanggil dengan `SOURCES_DIR=Sources` (identik dengan Custom Build existing; AC-B03).

#### Distribution & Packaging

- **REQ-D01 (Output Formats)**: Setiap weight baru DIDISTRIBUSIKAN dalam format TTF, OTF, dan WOFF2 — konsisten dengan format release saat ini. Pipeline juga memproduksi format WOFF dan SVG untuk weight baru (konsekuensi alami pipeline existing: driver menghasilkan SVG, Stage 2 menghasilkan WOFF dari seluruh TTF). **Keputusan format (mandat audit C5)**: WOFF dan SVG diproduksi tetapi tidak didistribusikan sebagai archive terpisah di release V1 (lihat REQ-D03 dan §8.5).
- **REQ-D02 (File Naming)**: Nama file mengikuti konvensi existing: `FantasqueSansMono-{Weight}.{ext}` (contoh: `FantasqueSansMono-Medium.ttf`).
- **REQ-D03 (Release Packaging)**: Release mencakup archive terpisah per format (.zip untuk TTF, .zip untuk OTF, .zip untuk WOFF2) yang masing-masing berisi 4–6 weight + varian Italic yang tersedia. File WOFF dan SVG tidak dimasukkan ke archive release V1 (archive WOFF2 hanya berisi `.woff2`); komposisi internal archive mengikuti konvensi packaging existing.
- **REQ-D04 (Documentation Update)**: `README.md` dan halaman specimen (`Specimen/`) DIPERBARUI untuk menampilkan dan mendokumentasikan seluruh varian weight baru, termasuk section "Faux Italic Limitations" dengan tabel kompatibilitas per platform.

#### Specimen & Visual QA

- **REQ-S01 (Specimen Generator)**: Sistem HARUS menyediakan script generator specimen sheet dalam format HTML yang dapat dibuka di browser secara lokal.
- **REQ-S02 (Specimen Content)**: Specimen sheet mencakup: waterfall teks (8, 10, 12, 14, 16, 20, 24, 32, 48, 72 pt), pangram bahasa Inggris dan Indonesia, set karakter pemrograman (`{}[]()<>;:.,!#$%^&*`), ligature sequences, dan discontinuity checklist untuk 48 pt dan 72 pt.
- **REQ-S03 (Specimen Metrics)**: Specimen sheet menyertakan informasi metrik untuk setiap weight: stem width, x-height, cap height, dan advance width.
- **REQ-S04 (Visual Diff)**: Script validasi HARUS menghasilkan overlay gambar PNG antara glyph interpolasi dan glyph master terdekat untuk glyph dengan status `warning` atau `fail`.
- **REQ-S05 (Interpolation Validation Report)**: Sistem HARUS menyediakan script `validate_interpolation.py` yang menghasilkan laporan JSON per glyph hasil interpolasi dengan status `pass`, `warning` (minor artifact), atau `fail` (distorsi berat — kerusakan kontur, self-intersection, counter tertutup), mengacu pada Visual Quality Rubric (E0.4) dan GH-005. Kontrak lengkap di §4.11.

### 3.2 Constraints

- **CON-001 (Legacy Code Preservation)**: `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`, dan root `Makefile` MUST NOT dimodifikasi, di-rename, atau di-refactor di V1. Semua script baru beroperasi di samping source legacy tanpa memodifikasinya.
- **CON-002 (Workflow A — FontForge Only)**: V1 HANYA menggunakan FontForge `.sfdir` + `font.interpolateFonts()`. Tidak ada migrasi ke UFO/`fontmake` di V1 (ADR-0003).
- **CON-003 (Linear Interpolation Only)**: Hanya interpolasi linear yang tersedia melalui `font.interpolateFonts()`. Tidak ada optical correction.
- **CON-004 (No Stroke Modification)**: `font.changeWeight()` atau algoritma stroke modification otomatis TIDAK BOLEH digunakan — hanya interpolasi antar master yang diharmonisasikan.
- **CON-005 (Vertical Metrics Freeze)**: Ascent, Descent, LineGap TIDAK BOLEH berubah antar weight. (Untuk *advance width*, lihat REQ-I03 dan REQ-I05).
- **CON-006 (No Italic for New Weights)**: V1 TIDAK menghasilkan Italic instances untuk weight baru (Medium, SemiBold, Light, ExtraBold). Pengguna mendapatkan faux italic dari sistem operasi.
- **CON-007 (GitHub Actions Free-Tier)**: Build pipeline HARUS berjalan pada GitHub Actions free-tier runner (`ubuntu-latest`) dengan batas waktu 360 menit.
- **CON-008 (FontForge Python Bindings)**: Semua script deteksi, validasi, dan interpolasi HARUS kompatibel dengan FontForge Python 3 bindings yang tersedia di package default Ubuntu 26.04 + `future` shim.

### 3.3 Security & Guidelines

- **SEC-001 (No User Data)**: Seluruh proses berjalan di dalam Docker container pada GitHub Actions runner. Tidak ada data pengguna yang dikumpulkan, disimpan, atau ditransmisikan.
- **SEC-002 (Scoped Token)**: Token GitHub Actions untuk Custom Build hanya memiliki izin `contents: write` yang terbatas pada fork tempat workflow dijalankan.
- **GUD-001 (Deterministic Build)**: Seluruh script multi-weight HARUS menghasilkan output deterministik — dua run dengan input identik HARUS menghasilkan file font byte-identical.
- **GUD-002 (Fail-Fast on Critical Error)**: Setiap kegagalan interpolasi yang menghasilkan distorsi kontur berat (self-intersection, counter tertutup) HARUS menghentikan pipeline dengan exit code non-zero dan pesan diagnostik.
- **GUD-003 (Progress Logging)**: Build log HARUS menampilkan pesan progres aktual pipeline (klarifikasi r2 — pesan progres yang menyebut pemanggilan `features.py` per weight mustahil dihasilkan: `multi_weight_driver.py` TIDAK memanggil `features.py` (REQ-B03) dan driver existing mencetak "Generating {name}"): "Detecting incompatibilities..." (echo RUN chain) → "Harmonizing..." (echo saat harmonized sources dimuat driver) → "Interpolating Medium (500)..." (driver baru) → "Generating {Weight}..." (driver existing) → "ttfautohint" / "packaging: ..." (Stage 2).
- **GUD-004 (Partial Success Tolerance)**: Kegagalan stretch weight (Light, ExtraBold) pada visual review TIDAK menggagalkan seluruh build. Core weight tetap dirilis — partial success tier tercapai.
- **GUD-005 (Artifact Retention)**: Build artifact (workflow run) mengikuti GitHub Actions default 90 hari. Release artifact bersifat permanen.

## 4. Interfaces & Data Contracts

### 4.1 Directory Structure — Harmonized Sources

```
Sources/
├── FantasqueSansMono-Regular.sfdir/       # Source legacy — TIDAK dimodifikasi
├── FantasqueSansMono-Bold.sfdir/          # Source legacy — TIDAK dimodifikasi
├── FantasqueSansMono-Italic.sfdir/        # Source legacy — TIDAK dimodifikasi
├── FantasqueSansMono-BoldItalic.sfdir/    # Source legacy — TIDAK dimodifikasi
├── FantasqueSans.sfdir/                   # Proportional variant — TIDAK disentuh
└── Harmonized/                            # Output harmonisasi (V1)
    ├── Regular/                           # .sfdir — harmonized Regular master
    ├── Bold/                              # .sfdir — harmonized Bold master
    ├── Italic/                            # .sfdir — harmonized Italic master (V2 foundation)
    └── BoldItalic/                        # .sfdir — harmonized BoldItalic master (V2 foundation)
```

Setiap direktori di `Sources/Harmonized/` adalah FontForge `.sfdir` directory yang berisi file `.glyph` individual. Struktur internal identik dengan source `.sfdir` existing (satu file `.glyph` per glyph, dengan nama file sesuai nama glyph).

### 4.2 Directory Structure — Interpolated Weight Output

```
Sources/Harmonized/Interpolated/
├── Medium/              # .sfdir — interpolasi factor 0.5 (Regular↔Bold)
├── SemiBold/            # .sfdir — interpolasi factor ~0.67 (Regular↔Bold)
├── Light/               # .sfdir — ekstrapolasi (factor TBD — ditetapkan Phase 5, REQ-I02)
└── ExtraBold/           # .sfdir — ekstrapolasi (factor TBD — ditetapkan Phase 5, REQ-I02)
```

Direktori `Interpolated/` berisi weight-weight baru hasil interpolasi dalam format `.sfdir`. Direktori ini berfungsi sebagai input ke pipeline variant expansion existing (LargeLineHeight, NoLoopK). **Status Git**: direktori `Interpolated/` TIDAK di-commit ke repository — dihasilkan ulang secara deterministik pada setiap build (GUD-001) dan di-cache antar build via GitHub Actions cache; hanya `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}/` (hasil kerja manual type designer) yang di-commit (PRD §8.2).

### 4.3 Multi-Weight Build Output

```
Variants/
├── Normal/
│   ├── FantasqueSansMono-Regular.ttf
│   ├── FantasqueSansMono-Medium.ttf
│   ├── FantasqueSansMono-SemiBold.ttf
│   ├── FantasqueSansMono-Bold.ttf
│   ├── FantasqueSansMono-Light.ttf          # Jika lolos visual review
│   ├── FantasqueSansMono-ExtraBold.ttf       # Jika lolos visual review
│   ├── FantasqueSansMono-Italic.ttf
│   ├── FantasqueSansMono-BoldItalic.ttf
│   └── ...
├── NoLoopK/
│   └── (struktur identik dengan Normal/)
├── LargeLineHeight/
│   └── (struktur identik dengan Normal/)
└── NoLoopK-LargeLineHeight/
    └── (struktur identik dengan Normal/)
```

**Catatan**: Struktur di atas adalah kontrak output driver existing — driver membuild **seluruh** `.sfdir` di `SOURCES_DIR` (termasuk `FantasqueSans` proportional variant) dan menamai output dari basename direktori. Di mode multi-weight, driver menerima `build/sources/` (REQ-B06) sehingga output mencakup weight baru; di mode single-weight, output identik dengan Custom Build existing (Regular, Bold, Italic, BoldItalic, FantasqueSans). **Sumber Italic/BoldItalic di `build/sources/` adalah harmonized masters** (`Sources/Harmonized/Italic/`, `Sources/Harmonized/BoldItalic/`) yang lolos `validate_harmonization.py --strict` (klarifikasi r3 — K4), bukan source legacy.

### 4.4 Incompatibility Detection Script

**File**: `Scripts/detect_incompatibility.py`

```text
Usage: fontforge -lang=py -script Scripts/detect_incompatibility.py MASTER_A.sfdir MASTER_B.sfdir [--output REPORT.json]

Arguments:
  MASTER_A.sfdir    Path ke direktori .sfdir master pertama
  MASTER_B.sfdir    Path ke direktori .sfdir master kedua
  --output PATH     Path untuk output laporan JSON (default: incompatibility_report.json)
```

**Output JSON Schema**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Incompatibility Detection Report",
  "type": "object",
  "required": ["master_a", "master_b", "total_glyphs", "compatible_count", "incompatible_count", "only_in_a_count", "only_in_b_count", "glyphs"],
  "properties": {
    "master_a": { "type": "string", "description": "Path ke master A" },
    "master_b": { "type": "string", "description": "Path ke master B" },
    "total_glyphs": { "type": "integer", "description": "Total glyph unik di union kedua master" },
    "compatible_count": { "type": "integer", "description": "Jumlah glyph yang kompatibel untuk interpolasi" },
    "incompatible_count": { "type": "integer", "description": "Jumlah glyph yang tidak kompatibel" },
    "only_in_a_count": { "type": "integer", "description": "Jumlah glyph yang hanya ada di master A" },
    "only_in_b_count": { "type": "integer", "description": "Jumlah glyph yang hanya ada di master B" },
    "glyphs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "status"],
        "properties": {
          "name": { "type": "string", "description": "Nama glyph" },
          "status": {
            "type": "string",
            "enum": ["compatible", "incompatible", "only_in_a", "only_in_b"]
          },
          "node_diff": {
            "type": "object",
            "description": "Perbedaan jumlah node per kontur (hanya untuk status incompatible)",
            "properties": {
              "contour_index": { "type": "integer" },
              "count_a": { "type": "integer" },
              "count_b": { "type": "integer" }
            }
          },
          "contour_diff": {
            "type": "object",
            "description": "Perbedaan jumlah kontur (hanya untuk status incompatible)",
            "properties": {
              "count_a": { "type": "integer" },
              "count_b": { "type": "integer" }
            }
          }
        }
      }
    }
  }
}
```

### 4.5 Harmonization Validation Script

**File**: `Scripts/validate_harmonization.py`

```text
Usage: fontforge -lang=py -script Scripts/validate_harmonization.py MASTER_A.sfdir MASTER_B.sfdir [--output REPORT.json] [--strict]

Arguments:
  MASTER_A.sfdir    Path ke direktori .sfdir master pertama (harmonized)
  MASTER_B.sfdir    Path ke direktori .sfdir master kedua (harmonized)
  --output PATH     Path untuk output laporan JSON
  --strict          Mode strict: kegagalan pada satu glyph menghasilkan exit code non-zero
```

**Validasi per pasangan glyph:**
1. `node-count-equal`: Jumlah control point per kontur identik antara master A dan B.
2. `contour-order-equal`: Jumlah dan urutan kontur identik.
3. `curve-direction-equal`: Arah kurva (clockwise/counter-clockwise) identik per kontur.

**Output JSON Schema**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Harmonization Validation Report",
  "type": "object",
  "required": ["master_a", "master_b", "total_pairs", "pass_count", "fail_count", "results"],
  "properties": {
    "master_a": { "type": "string" },
    "master_b": { "type": "string" },
    "total_pairs": { "type": "integer" },
    "pass_count": { "type": "integer" },
    "fail_count": { "type": "integer" },
    "pass_rate": { "type": "number", "description": "Persentase glyph yang lolos (0.0–100.0)" },
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["glyph_name", "status"],
        "properties": {
          "glyph_name": { "type": "string" },
          "status": { "type": "string", "enum": ["pass", "fail"] },
          "checks": {
            "type": "object",
            "properties": {
              "node_count_equal": { "type": "boolean" },
              "contour_order_equal": { "type": "boolean" },
              "curve_direction_equal": { "type": "boolean" }
            }
          },
          "details": {
            "type": "string",
            "description": "Deskripsi kegagalan (hanya untuk status fail)"
          }
        }
      }
    }
  }
}
```

### 4.6 Multi-Weight Driver Script

**File**: `Scripts/multi_weight_driver.py`

Ini adalah entry point utama untuk pipeline multi-weight. Dieksekusi oleh FontForge embedded Python 3 di Stage 1 Docker.

```text
Usage: fontforge -lang=py -script Scripts/multi_weight_driver.py --sources SOURCES_DIR --output OUTPUT_DIR [--enable-light] [--enable-extrabold] [--light-factor F] [--extrabold-factor F]

Arguments:
  --sources DIR            Path ke direktori Sources/ (mengandung Harmonized/ subdirektori)
  --output DIR             Path ke direktori output untuk weight hasil interpolasi
  --enable-light           Aktifkan ekstrapolasi Light (300)
  --enable-extrabold       Aktifkan ekstrapolasi ExtraBold (800)
  --light-factor F         Factor ekstrapolasi untuk Light (default: ditetapkan Phase 5 oleh Designer A + maintainer — REQ-I02; hasil dicatat di docs/audit/stretch-factor-decision-{date}.md)
  --extrabold-factor F     Factor ekstrapolasi untuk ExtraBold (default: ditetapkan Phase 5 oleh Designer A + maintainer — REQ-I02; hasil dicatat di docs/audit/stretch-factor-decision-{date}.md)
  --dry-run                Hanya validasi — tidak menulis file output

Catatan: flag `--enable-light` / `--enable-extrabold` HANYA digunakan oleh pipeline release upstream. Custom Build (`enable_multi_weight=true`) TIDAK membangun stretch weight (PRD GH-004, Clarification E10).
```

**Alur Eksekusi:**

```mermaid
flowchart TD
    A[Harmonized Regular + Bold .sfdir] --> B[Interpolasi Medium 500<br/>factor = 0.5]
    A --> C[Interpolasi SemiBold 600<br/>factor = ~0.67]
    A --> D{Ekstrapolasi Light?<br/>(release upstream saja)}
    D -->|--enable-light| E[Ekstrapolasi Light 300<br/>factor = TBD]
    D -->|skip| F[Skip Light]
    A --> G{Ekstrapolasi ExtraBold?<br/>(release upstream saja)}
    G -->|--enable-extrabold| H[Ekstrapolasi ExtraBold 800<br/>factor = TBD]
    G -->|skip| I[Skip ExtraBold]
    B --> J[Copy hmtx dari Regular]
    C --> J
    E --> J
    H --> J
    J --> K[Assembly build/sources/<br/>7-9 .sfdir termasuk FantasqueSans]
    K --> L[custom_build_driver.py existing<br/>features.py in-process per weight<br/>+ generate TTF/OTF/SVG]
    L --> M[Stage 2: ttfautohint weight baru<br/>+ WOFF/WOFF2 + packaging]
```

**Contract:**
- Membaca harmonized masters dari `Sources/Harmonized/Regular/` dan `Sources/Harmonized/Bold/`.
- Menghasilkan interpolated `.sfdir` di `Sources/Harmonized/Interpolated/{Medium,SemiBold,Light,ExtraBold}/` (tidak di-commit; lihat §4.2).
- Menerapkan copy-as-fallback untuk glyph tanpa pasangan.
- Mem-post-process: menyalin tabel `hmtx` dari master Regular ke seluruh weight baru untuk memastikan advance width identik.
- Meng-inject metadata internal **sebelum menyimpan** setiap `.sfdir` interpolated: `os2_weight` (Medium 500, SemiBold 600), `familyname`, `fullname` — unik per weight dan tidak identik dengan master (Regular 400, Bold 700). Verifikasi dua lapis: lapis 1 di Phase 3 pada `.sfdir` (one-liner FontForge), lapis 2 di Phase 4 pada TTF final (`ttx -t name -t OS/2` + `fc-scan`).
- Nilai factor stretch final (ditetapkan Phase 5 — REQ-I02) menjadi kontrak: dicatat di sini dan di `docs/audit/stretch-factor-decision-{date}.md`.
- Menyusun direktori build source `build/sources/` (REQ-B06): menyalin 4 harmonized masters + interpolated weights dengan nama `FantasqueSansMono-{Weight}.sfdir`, plus salinan `FantasqueSans.sfdir` legacy.
- **TIDAK memanggil `features.py` dan TIDAK menjalankan `ttfautohint`** — keduanya adalah tanggung jawab pipeline existing: `features.py` dipanggil in-process oleh `custom_build_driver.py` per weight (REQ-B03), `ttfautohint` dieksekusi di Stage 2 (REQ-I04, ADR-0002).
- Gating distorsi kontur berat BUKAN tanggung jawab driver (klarifikasi r3 — K8): driver cukup mempropagasi error FontForge (exit code non-zero + pesan diagnostik). Deteksi distorsi berat (self-intersection / counter tertutup / kontur rusak) menjadi tanggung jawab tunggal `validate_interpolation.py` — di-enforce di RUN chain build via loop `--fail-fast` per core weight (§4.9) dan di runbook release upstream (§4.10) — tanpa duplikasi logika deteksi.
- **Output PoC (klarifikasi r3 — K11)**: `poc_interpolation.py` (Phase 0) menghasilkan **dua output** — `.sfdir` interpolated subset DAN TTF untuk rendering (via `font.generate`, tanpa hinting — konsisten "TANPA ttfautohint") — TTF tersebut menjadi input `generate_specimen.py` dan visual diff review (FR-2.3 butuh font yang dapat dirender pada 8/12/16/24 pt; lihat §5.2 AC-P02).

### 4.7 features.py Invocation Contract

`Scripts/features.py` dipanggil **in-process oleh `custom_build_driver.py` existing** melalui `update_features(font)` — satu kali untuk setiap `.sfdir` di `SOURCES_DIR` (REQ-B03). Di mode multi-weight, `SOURCES_DIR=build/sources/` berisi 7–9 `.sfdir` (4 harmonized masters + 2–4 interpolated weights + `FantasqueSans.sfdir`; driver memindai seluruh `*.sfdir` top-level), sehingga `features.py` efektif dipanggil 7–9 kali per build — satu kali per `.sfdir`.

**Pola pemanggilan aktual (existing, TIDAK dimodifikasi):**

```text
fontforge --quiet -lang=py -script Scripts/custom_build_driver.py <sources_dir> <output_dir> [--line-height] [--no-loop-k] [--no-calt]
```

Di dalam `build_one_weight()`: `fontforge.open('<sources_dir>/<Weight>.sfdir')` → opsi variant (LargeLineHeight/NoLoopK/NoCalt) → `features.update_features(fnt)` → `fnt.generate(...)` (TTF/OTF/SVG).

**Invariant:**
- `features.py` TIDAK dimodifikasi (CON-001).
- Validasi determinisme (E0.1) dilakukan sebelum Phase 1: panggil pipeline 2× pada input yang sama, bandingkan output byte-by-byte. Jika output tidak identik, eskalasi ke tim engineering.
- **Koreksi terhadap PRD §8.1**: wrapper `multi_weight_driver.py` TIDAK memanggil `features.py` via subprocess — pemanggilan 6× (satu per weight master) sudah dilakukan oleh driver existing secara in-process untuk setiap `.sfdir` yang dibuild (terverifikasi di `Scripts/custom_build_driver.py`, `_update_features(fnt)` di dalam `build_one_weight()`).

### 4.8 Specimen Sheet Generator

**File**: `Scripts/generate_specimen.py`

```text
Usage: python3 Scripts/generate_specimen.py --weights WEIGHTS_DIR [--output HTML_DIR]

Arguments:
  --weights DIR    Path ke direktori yang berisi file TTF untuk seluruh weight
  --output DIR     Path ke direktori output HTML (default: Specimen/MultiWeight/)
```

**Output HTML Structure:**

```
Specimen/MultiWeight/
├── index.html              # Halaman navigasi
├── waterfall.html          # Waterfall teks multi-ukuran
├── pangrams.html           # Pangram EN + ID per weight
├── programming.html        # Set karakter pemrograman
├── metrics.html            # Tabel metrik per weight
└── discontinuity_checklist.html  # Checklist untuk 48pt dan 72pt
```

**Data Contract — Waterfall Text:**

Untuk setiap weight, specimen menampilkan teks yang sama pada ukuran: 8, 10, 12, 14, 16, 20, 24, 32, 48, dan 72 pt. Teks uji:

```text
# Pangram (English)
The quick brown fox jumps over the lazy dog. 0123456789

# Pangram (Indonesia)
Saya sedang menulis kode TypeScript dengan React dan Node.js. 0123456789

# Programming characters
{}[]()<>;:.,!#$%^&*+-=/\|~`@

# Ligature sequences
-> => =>> <<- <- <= >= == != === !==
:: ::= |> |] [| || |= |>
// /* */ /** ///

# Code sample
function fibonacci(n: number): number {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}
```

### 4.9 Custom Build Workflow Extension

**File**: `.github/workflows/custom-build.yml`

**Parameter Baru:**

| Input Key | Type | Default | Description |
|---|---|---|---|
| `enable_multi_weight` | boolean | `false` | Enable multi-weight interpolation (Medium, SemiBold). Stretch weight (Light, ExtraBold) TIDAK dibangun di Custom Build — hanya di release upstream (E10) |

**Konteks eksekusi (koreksi v1.2)**: Script multi-weight HANYA dapat dieksekusi di **Stage 1 Docker** (`builder-fontforge`) — FontForge tidak tersedia di host runner (hanya Python 3.14 + jsonschema/pytest) maupun di image final Stage 2 (ttfautohint, woff-tools, woff2, zip/tar/jq) — lihat ADR-0002. Oleh karena itu integrasi dilakukan melalui **flag forwarding**: workflow → `configure.py` → `BUILD_ARGS` → RUN kondisional di Dockerfile. Tidak ada step tambahan yang memanggil `fontforge` langsung di runner.

**Alur forwarding flag:**

```text
custom-build.yml (workflow_dispatch input: enable_multi_weight)
  └─ configure.py --form-enable-multi-weight <true|false>   # pola --form-* existing
       └─ build_driver_arg_string() → flag "--multi-weight" (jika true) → build-args.txt
            └─ Docker ARG BUILD_ARGS (dari build-args.txt)
                 └─ Stage 1 RUN kondisional: echo "$BUILD_ARGS" | grep -q -- "--multi-weight"   # bentuk portabel (tanpa bashism <<< — Dockerfile tanpa SHELL directive; klarifikasi r3 K1)
```

**Kontrak configure.py**: Tambahkan argumen `--form-enable-multi-weight` (boolean, default `false`) pada parser existing dan mapping ke flag driver `--multi-weight` (mengikuti pola `FORM_KEY_TO_OPTION` / `OPTION_TO_DRIVER_FLAG` yang sudah ada). Modifikasi `Scripts/configure.py` diperbolehkan — file ini TIDAK dilindungi CON-001; namun dikelola oleh Custom Build Spec, sehingga minor update cross-spec diperlukan (PRD §8.1, audit C5).

**Dockerfile Stage 1 — RUN chain kontrak:**

```dockerfile
# Mode multi-weight: flag diteruskan via BUILD_ARGS
ARG BUILD_ARGS=""
RUN if echo "$BUILD_ARGS" | grep -q -- "--multi-weight"; then \
        echo "::group::Multi-Weight Pipeline"; \
        echo "Detecting incompatibilities..."; \
        fontforge --quiet -lang=py -script Scripts/detect_incompatibility.py \
            Sources/FantasqueSansMono-Regular.sfdir \
            Sources/FantasqueSansMono-Bold.sfdir \
            --output build/incompatibility_report.json; \
        echo "Validating harmonized sources (Regular<->Bold)..."; \
        fontforge --quiet -lang=py -script Scripts/validate_harmonization.py \
            Sources/Harmonized/Regular \
            Sources/Harmonized/Bold \
            --output build/harmonization_report_regular_bold.json \
            --strict; \
        echo "Validating harmonized sources (Italic<->BoldItalic)..."; \
        fontforge --quiet -lang=py -script Scripts/validate_harmonization.py \
            Sources/Harmonized/Italic \
            Sources/Harmonized/BoldItalic \
            --output build/harmonization_report_italic_bolditalic.json \
            --strict; \
        echo "Running unit tests (fail-fast)..."; \
        pytest tests/ -v; \
        echo "Running multi-weight driver..."; \
        fontforge -lang=py -script Scripts/multi_weight_driver.py \
            --sources Sources \
            --output Sources/Harmonized/Interpolated; \
        echo "Validating interpolated weights (fail-fast)..."; \
        for w in Medium SemiBold; do \
            fontforge --quiet -lang=py -script Scripts/validate_interpolation.py \
                --interpolated "Sources/Harmonized/Interpolated/$w" \
                --masters Sources/Harmonized \
                --threshold 15.0 \
                --output "build/interpolation_report_${w}.json" \
                --fail-fast; \
        done; \
        echo "::endgroup::"; \
        DRIVER_ARGS=$(printf '%s' "$BUILD_ARGS" | sed 's/--multi-weight//g'); \
        FONTS=build/sources; \
    else \
        DRIVER_ARGS="$BUILD_ARGS"; \
        FONTS=Sources; \
    fi \
    && fontforge --quiet -lang=py -script \
        Scripts/custom_build_driver.py "$FONTS" /build $DRIVER_ARGS
```

Catatan kontrak:
- `build/`, `Sources/Harmonized/Interpolated/` dan `build/sources/` adalah direktori runtime di dalam container — tidak di-commit (GUD-001, §4.2).
- Mode `false` → `FONTS=Sources` + `DRIVER_ARGS="$BUILD_ARGS"` → RUN identik dengan Custom Build existing → output byte-identical (AC-B03).
- Stripping `--multi-weight` dari `$BUILD_ARGS` via `DRIVER_ARGS=$(printf '%s' "$BUILD_ARGS" | sed 's/--multi-weight//g')` WAJIB dilakukan sebelum pemanggilan driver — `parse_args()` driver existing melakukan `_die("unknown flag(s): ...")` untuk flag di luar `--line-height`/`--no-loop-k`/`--no-calt` (klarifikasi r3 — K1; terverifikasi di `Scripts/custom_build_driver.py`).
- Bentuk grep portabel `echo "$BUILD_ARGS" | grep -q -- "--multi-weight"` menggantikan bashism here-string `<<<` — Dockerfile Stage 1 tanpa `SHELL` directive → `/bin/sh` (dash) tidak mendukung `<<<` (klarifikasi r3 — K1).
- `validate_harmonization.py --strict` dijalankan untuk **kedua pasangan master** — Regular↔Bold DAN Italic↔BoldItalic (hasil harmonisasi Italic/BoldItalic ikut di-assembly ke `build/sources/`; klarifikasi r3 — K4). Fail-fast jika masih ada glyph `fail` yang belum diperbaiki (Never Do — seluruh glyph fail HARUS diperbaiki sebelum interpolasi).
- Loop fail-fast `validate_interpolation.py --threshold 15.0 --fail-fast` per core weight interpolated (Medium, SemiBold) dijalankan SETELAH `multi_weight_driver.py` dan SEBELUM `custom_build_driver.py` — status `fail` (self-intersection / counter tertutup / kontur rusak) → exit non-zero (GUD-002 ter-enforce di CI; klarifikasi r3 — K8); `warning` ≤ 2% tidak memblokir build (metrik QA Phase 3). Nilai `--threshold` mengikuti REQ-H06/§11.2 — diperbarui ke `T_final` setelah kalibrasi (klarifikasi r3 — K7).
- `multi_weight_driver.py` menghasilkan interpolated `.sfdir` DAN menyusun `build/sources/` (assembly — §4.6, REQ-B06).
- Stretch weight (Light, ExtraBold) TIDAK dibangun di Custom Build — flag `--enable-light`/`--enable-extrabold` hanya dipakai pipeline release upstream (E10).
- `pytest` + `jsonschema` diinstal **tidak kondisional** di Stage 1 — baris `pip3 install --break-system-packages --no-cache-dir future` diperpanjang menjadi `... future pytest jsonschema` (pola existing, satu layer; image single-weight tidak terpengaruh pada output font — AC-B03 tetap berlaku; klarifikasi r3 — K2).
- `pytest tests/ -v` dijalankan di dalam RUN chain multi-weight (fail-fast **sebelum interpolasi**): keempat file test FontForge-dependent (`test_detect_incompatibility.py`, `test_validate_harmonization.py`, `test_validate_interpolation.py`, `test_multi_weight_driver.py`) dieksekusi dengan FontForge nyata dari Stage 1. Di host runner, keempat file tersebut memakai `pytest.importorskip("fontforge")` di level modul sehingga gate pytest host tidak crash (TASK-4.2, TASK-0.10; klarifikasi r3 — K6).
- Pesan log tahap mengikuti GUD-003 / GH-004 AC#5 — termasuk `Harmonizing...` (ditampilkan saat harmonized sources dimuat oleh driver; harmonisasi itu sendiri adalah kerja manual type designer — FR-1.3).

**Workflow custom-build.yml — kontrak step (step EXISTING yang diperluas, tanpa step baru):**

```yaml
- name: Configure build options
  run: |
    python3 Scripts/configure.py \
      --form-large-line-height "${{ inputs.large_line_height }}" \
      --form-no-loop-k "${{ inputs.no_loop_k }}" \
      --form-no-calt "${{ inputs.no_calt }}" \
      --form-use-hinted "${{ inputs.use_hinted }}" \
      --form-enable-multi-weight "${{ inputs.enable_multi_weight }}" \
      --output-args-file build-args.txt
    echo "BUILD_ARGS=$(cat build-args.txt)" >> "$GITHUB_ENV"
```

Build tetap satu kali `docker build` — multi-weight pipeline berjalan di dalam Stage 1 tanpa step workflow tambahan.

### 4.10 Packaging.sh Extension

**File**: `Scripts/packaging.sh`

Fungsi packaging diperluas untuk mengenali struktur direktori multi-weight:

```bash
# Pseudo-code — kontrak, bukan implementasi
# RELEASE_MODE=1 → pipeline release upstream (dipicu maintainer secara eksplisit
# via env var; CI Custom Build TIDAK pernah menyetelnya — E10, klarifikasi r3 K14).
if [ "$RELEASE_MODE" = "1" ]; then
    # Release upstream (publik): 4–6 weight sesuai kelolosan stretch (FR-6.3)
    WEIGHTS=("Regular" "Medium" "SemiBold" "Bold" "Italic" "BoldItalic"
             ["Light"] ["ExtraBold"]  # hanya jika lolos visual review
             "FantasqueSans")
elif [ "$ENABLE_MULTI_WEIGHT" = "true" ]; then
    # Mode Custom Build (fork owner, Stage 2): stretch weight TIDAK pernah disertakan (E10)
    WEIGHTS=("Regular" "Medium" "SemiBold" "Bold" "Italic" "BoldItalic")
else
    # Kompatibilitas mundur penuh — identik dengan Custom Build existing:
    # driver membuild seluruh .sfdir di Sources/ (termasuk FantasqueSans)
    WEIGHTS=("Regular" "Bold" "Italic" "BoldItalic" "FantasqueSans")
fi

# Override hinting REQ-I04 (klarifikasi r3 — K9): weight baru (Medium, SemiBold;
# + Light, ExtraBold di mode release) WAJIB di-hint SELALU, terlepas nilai
# UseHinted yang dibaca dari manifest via jq. Weight existing (Regular, Bold,
# Italic, BoldItalic, FantasqueSans) tetap mengikuti UseHinted (perilaku
# packaging.sh existing — hinting terkondisi).
NEW_WEIGHTS=("Medium" "SemiBold" "Light" "ExtraBold")  # subset aktif sesuai mode

for weight in "${WEIGHTS[@]}"; do
    # Cek apakah file TTF/OTF/WOFF2 untuk weight ini ada
    # Sertakan dalam archive .zip per format
done

# Komposisi budget WOFF2 ≤ 500 KB (AC-D03, klarifikasi r3 — K10):
#   dihitung atas 6 weight baru pada set release — Regular, Medium, SemiBold,
#   Bold + Light, ExtraBold (jika diproduksi). Italic, BoldItalic, dan
#   FantasqueSans TIDAK dihitung (weight existing yang sudah dirilis).
#   Jika stretch gagal review, jumlah file otomatis berkurang (budget melonggar — tetap kap).
```

### 4.11 Interpolation Validation Script

**File**: `Scripts/validate_interpolation.py`

```text
Usage: fontforge -lang=py -script Scripts/validate_interpolation.py --interpolated INTERPOLATED_DIR --masters MASTER_DIR [--rubric RUBRIC.json] [--threshold DEG] [--output REPORT.json] [--overlay-dir PNG_DIR] [--fail-fast]

Arguments:
  --interpolated DIR   Path ke .sfdir hasil interpolasi
  --masters DIR        Path ke direktori harmonized masters (Regular & Bold)
  --rubric FILE        Visual Quality Rubric (E0.4) sebagai acuan klasifikasi warning/fail
  --threshold DEG      Threshold discontinuity dalam derajat (default: 15.0) — REQ-H06; dipisahkan dari rubric markdown (rubric mendokumentasikan nilai final, bukan sumber parsing script) — klarifikasi r3 K7
  --output FILE        Path output laporan JSON (default: interpolation_report.json)
  --overlay-dir DIR    Direktori output overlay PNG (REQ-S04); di-skip jika tidak diberikan
  --fail-fast          Exit code non-zero jika ada glyph berstatus `fail` (gating GUD-002 — dipakai RUN chain §4.9 dan runbook release upstream §4.10) — klarifikasi r3 K8
```

**Output JSON Schema** (per GH-005):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Interpolation Validation Report",
  "type": "object",
  "required": ["weight", "total_glyphs", "pass_count", "warning_count", "fail_count", "glyphs"],
  "properties": {
    "weight": { "type": "string", "description": "Nama weight yang divalidasi (misal Medium)" },
    "total_glyphs": { "type": "integer" },
    "pass_count": { "type": "integer" },
    "warning_count": { "type": "integer" },
    "fail_count": { "type": "integer" },
    "glyphs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "status"],
        "properties": {
          "name": { "type": "string" },
          "status": { "type": "string", "enum": ["pass", "warning", "fail"] },
          "issue": { "type": "string", "description": "Deskripsi masalah (hanya untuk warning/fail)" },
          "overlay_png": { "type": "string", "description": "Path relatif overlay PNG (hanya untuk warning/fail, jika --overlay-dir diberikan)" }
        }
      }
    }
  }
}
```

**Semantik status** (sesuai FR-5.4, SM-T2, dan klarifikasi r2 — definisi operasional dikunci di TASK-0.3):
- `pass`: glyph tidak memiliki artifact.
- `warning`: artifact **non-self-intersect** (contoh: tangent-angle > threshold discontinuity hasil kalibrasi REQ-H06) yang tidak mengganggu keterbacaan 8–16 pt (masuk toleransi ≤ 2%).
- `fail`: distorsi berat — **self-intersection / counter tertutup / kontur rusak** — glyph HARUS dikembalikan ke harmonisasi (FR-5.3), tidak boleh diperbaiki pada hasil interpolasi.
- Unit hitung klasifikasi = **per glyph** (konsisten FR-5.4: ≤ 2% ≈ 21 glyph dari 1.042).
**Protokol dua-pass kalibrasi threshold (klarifikasi r3 — K7)**: (1) jalankan `validate_interpolation.py` dengan threshold awal 15.0° (default `--threshold`) → laporan R1; (2) visual diff review (FR-2.3) mengkalibrasi threshold → nilai final `T_final` dicatat di `docs/audit/phase0-experiments-{date}.md` dan `docs/audit/visual-quality-rubric.md`; (3) jalankan ulang script dengan `--threshold T_final` → laporan R2; (4) gate PoC (AC-P03) dan gate build (§4.9) dievaluasi pada **R2**. Guard: perubahan threshold wajib didasari temuan visual dan didokumentasikan — tidak boleh disetel hanya agar gate lolos.

### 4.12 Harmonization Tracking File Contract

**File**: `Sources/Harmonized/tracking.json`

Format file JSON yang digunakan oleh type designer untuk menandai glyph yang memerlukan harmonisasi ulang atau yang telah di-review (memenuhi PRD GH-005 AC#4). Keputusan visual review per-glyph dicatat melalui field `review_verdict`/`reviewed_by`/`date` (Phase 3 — core weight: Designer A (Lead) = otoritas final, Designer B untuk glyph shared pool yang ia kerjakan; Phase 5 — stretch weight: Designer A + upstream maintainer). File ini dikomit ke dalam repository.

**Output JSON Schema**:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Harmonization Tracking File",
  "type": "object",
  "required": ["last_updated", "glyphs"],
  "properties": {
    "last_updated": { "type": "string", "format": "date-time" },
    "glyphs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "status", "assigned_to"],
        "properties": {
          "name": { "type": "string" },
          "status": {
            "type": "string",
            "enum": ["needs_harmonization", "in_progress", "ready_for_review", "approved"]
          },
          "assigned_to": { "type": "string", "description": "Type designer yang bertanggung jawab" },
          "notes": { "type": "string" },
          "date_flagged": { "type": "string", "format": "date-time" },
          "review_verdict": { "type": "string", "enum": ["pass", "fail"], "description": "Hasil review visual type designer (hanya untuk glyph yang sudah direview)" },
          "reviewed_by": { "type": "string", "description": "Nama type designer reviewer (Designer A = otoritas final; Designer B untuk shared pool)" },
          "date": { "type": "string", "format": "date-time", "description": "Tanggal verdict review" }
        }
      }
    }
  }
}
```

## 5. Acceptance Criteria

### 5.1 Master Harmonization

- **AC-H01**: Script `detect_incompatibility.py` menghasilkan laporan JSON yang valid dengan field `total_glyphs`, `compatible_count`, `incompatible_count`, dan array `glyphs` dengan status per glyph.
- **AC-H02**: Script `validate_harmonization.py` melaporkan `pass_rate ≥ 98%` untuk pasangan Regular↔Bold dan Italic↔BoldItalic (SM-T1). **Gate dua-tingkat (klarifikasi r3 — K3)**: `pass_rate ≥ 98%` = checkpoint kemajuan (melanjutkan review/iterasi); `fail_count = 0` (100%) = syarat masuk Phase 3 (interpolasi) — konsisten dengan Never Do §7, GUD-002, dan `--strict` di RUN chain §4.9.
- **AC-H03**: Semua hasil harmonisasi tersimpan di `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}/` dalam format `.sfdir`.
- **AC-H04**: Glyph hasil harmonisasi lolos hard invariant: tidak ada perbedaan visual yang terlihat pada ukuran 8–24 pt saat dibandingkan side-by-side dengan master asli.
- **AC-H05**: Glyph hasil harmonisasi lolos soft invariant: tidak ada discontinuity (sudut tajam) pada ukuran 24–72 pt berdasarkan checklist specimen sheet.

### 5.2 Proof of Concept (PoC)

- **AC-P01**: PoC mencakup subset ~40–50 glyph sesuai FR-2.1 (huruf `a`–`z`, glyph multi-kontur `g`/`@`/`&`/`Q`/`?`/`!`, glyph counter kompleks `ß`/`fi`/`fl`, glyph kritis fungsional `space`/`period`/`comma`/`zero`, dan 3–5 worst offenders).
- **AC-P02**: Script interpolasi menghasilkan Medium (500) dari subset yang telah diharmonisasikan. **Kontrak output (klarifikasi r3 — K11)**: `poc_interpolation.py` menghasilkan dua output — `.sfdir` interpolated subset DAN TTF untuk rendering via `font.generate` (tanpa hinting — konsisten "TANPA ttfautohint"); TTF menjadi input `generate_specimen.py` dan visual diff review FR-2.3 (render 8/12/16/24 pt; lihat §4.6).
- **AC-P03**: ≥ 90% glyph hasil interpolasi PoC dinilai "mempertahankan nuansa handwritten" oleh type designer berdasarkan Visual Quality Rubric (E0.4).
- **AC-P04**: Tidak ada glyph yang mengalami distorsi berat (kerusakan kontur, self-intersection, counter tertutup).
- **AC-P05**: Advance width Medium (500) identik dengan Regular (400) — divalidasi dengan E0.2.
- **AC-P06**: Visual diff review PoC (FR-2.3) selesai: perbandingan side-by-side antara glyph asli Regular/Bold dan hasil interpolasi Medium pada 8 pt, 12 pt, 16 pt, dan 24 pt, dengan hasil terdokumentasi.
- **AC-P07**: Jika PoC GAGAL (FR-2.4 tidak terpenuhi), pipeline TIDAK melanjutkan ke Phase 2 dan salah satu dari 4 jalur keputusan FR-2.5 dipilih serta didokumentasikan (iterasi harmonisasi ulang maks. 2 siklus / revisi cakupan V1 / re-evaluasi tooling / penundaan fitur).

### 5.3 Multi-Weight Interpolation

- **AC-I01**: Keempat core weight (Regular 400, Medium 500, SemiBold 600, Bold 700) tersedia sebagai file TTF, OTF, dan WOFF2 terpisah.
- **AC-I02**: File font dapat diinstal dengan benar di Windows (Font Settings), macOS (Font Book), dan Linux (`fontconfig`).
- **AC-I03**: Setiap weight muncul dengan nama yang benar di font picker aplikasi (contoh: "Fantasque Sans Mono Medium").
- **AC-I04**: Advance width seluruh 4–6 weight identik — teks yang sama menempati jumlah kolom yang sama saat weight diganti di editor monospace.
- **AC-I05**: Ligature (`->`, `=>`, `!=`, dll.) berfungsi dengan benar di semua weight.
- **AC-I06**: Interpolasi menghasilkan ≤ 2% glyph dengan minor visual artifact (FR-5.4).
- **AC-I07**: Tidak ada glyph dengan counter tertutup atau stroke bertabrakan pada seluruh weight baru; stem width dan counter size proporsional terhadap posisi weight (FR-4.2) — diverifikasi melalui laporan `validate_interpolation.py` (REQ-S05) dan checklist rubrik.
- **AC-I08**: `validate_interpolation.py` menghasilkan laporan JSON dengan status `pass`/`warning`/`fail` per glyph (REQ-S05), dan overlay PNG dihasilkan untuk glyph berstatus `warning`/`fail` (REQ-S04).

### 5.4 Build Pipeline

- **AC-B01**: Custom Build Workflow memiliki parameter boolean `enable_multi_weight` di halaman "Run workflow".
- **AC-B02**: Ketika `enable_multi_weight = true`, build menghasilkan 4 core weight (Regular, Medium, SemiBold, Bold) dalam 3 format distribusi (TTF, OTF, WOFF2) + output existing (Italic, BoldItalic, FantasqueSans) — Regular/Bold dibangun dari harmonized masters (TIDAK byte-identical dengan V0). Stretch weight TIDAK dihasilkan di Custom Build (E10).
- **AC-B03**: Ketika `enable_multi_weight = false`, build berjalan tanpa pemanggilan script multi-weight dan outputnya **byte-identical dengan Custom Build existing** (Regular, Bold, Italic, BoldItalic, FantasqueSans) — kompatibilitas mundur penuh pada level pipeline DAN level output.
- **AC-B04**: Total durasi build multi-weight ≤ 240 menit pada GitHub Actions free-tier runner (SM-T3).
- **AC-B05**: Build log menampilkan pesan progres aktual: "Detecting incompatibilities...", "Harmonizing...", "Interpolating Medium (500)...", "Generating {Weight}...", "ttfautohint", "packaging: ..." (GUD-003).
- **AC-B06**: Artifact ZIP multi-weight memiliki ukuran ≤ 5 MB dan dapat diunduh dari halaman Actions.

### 5.5 Specimen & Visual QA

- **AC-S01**: Specimen sheet HTML menampilkan waterfall teks untuk seluruh weight pada 10 ukuran (8–72 pt).
- **AC-S02**: Specimen menampilkan pangram bahasa Inggris dan Indonesia, serta set karakter pemrograman.
- **AC-S03**: Specimen menyertakan discontinuity checklist untuk 48 pt dan 72 pt.
- **AC-S04**: Specimen menyertakan informasi metrik: stem width, x-height, cap height, advance width per weight.

### 5.6 Distribution

- **AC-D01**: Release GitHub mencakup 3 archive terpisah (TTF .zip, OTF .zip, WOFF2 .zip).
- **AC-D02**: File WOFF2 dapat digunakan dengan standard `@font-face` CSS declaration dan descriptor `font-weight` yang sesuai (300, 400, 500, 600, 700, 800).
- **AC-D03**: Total ukuran WOFF2 untuk 6 weight ≤ 500 KB. **Komposisi "6 weight" (klarifikasi r3 — K10)**: budget dihitung atas 6 weight baru pada set release — Regular, Medium, SemiBold, Bold + Light, ExtraBold (jika diproduksi); Italic, BoldItalic, dan FantasqueSans TIDAK dihitung (weight existing yang sudah dirilis; lihat §4.10).
- **AC-D04**: `README.md` menyertakan section "Faux Italic Limitations" dengan workaround spesifik per platform (tabel kompatibilitas macOS/Windows/Linux/Browser).
- **AC-D05**: `README.md` menyertakan contoh kode CSS untuk embedding web multi-weight.

## 6. Test Automation Strategy

### 6.1 Test Levels

| Level | Scope | Framework | Executor |
|---|---|---|---|
| **Eksperimen Validasi (Phase 0)** | Validasi asumsi kritis sebelum harmonisasi dimulai | Script Python + bash | Manual / docker |
| **Unit Test — Detection Script** | Verifikasi output JSON `detect_incompatibility.py` untuk berbagai skenario glyph | `pytest` | GitHub Actions / local |
| **Unit Test — Validation Script** | Verifikasi `validate_harmonization.py` mendeteksi ketiga kondisi (node count, contour order, curve direction) | `pytest` | GitHub Actions / local |
| **Unit Test — Interpolation Driver** | Verifikasi `multi_weight_driver.py` menghasilkan file `.sfdir` yang valid untuk setiap weight | `pytest` + FontForge | GitHub Actions / local |
| **Integration Test — End-to-End Build** | Workflow dispatch → build → artifact → verifikasi konten artifact | GitHub Actions | `workflow_dispatch` manual |
| **Visual QA** | Manual type designer review menggunakan specimen sheet dan Visual Quality Rubric | Manual | Lokal type designer |

### 6.2 Eksperimen Validasi Phase 0 (Wajib)

Eksperimen berikut HARUS diselesaikan dan didokumentasikan sebelum Phase 1 (PoC) dimulai. Hasil eksperimen disimpan di `docs/audit/phase0-experiments-{date}.md`.

#### E0.1 — `features.py` Idempotency Test

- **Tujuan**: Memvalidasi bahwa `features.py` bersifat deterministik dan idempotent ketika dipanggil 6 kali dengan glyph set yang sama.
- **Metode**: Panggil pipeline (`custom_build_driver.py` → `features.update_features`) pada satu font source (misal Regular) sebanyak 6 kali berturut-turut, simpan output font untuk setiap pemanggilan, dan bandingkan byte-by-byte (`sha256sum`). **Penyempurnaan metode vs PRD §9.2 (E0.1)**: PRD membandingkan output antar weight master yang berbeda; versi ini membandingkan 6 pemanggilan pada source yang SAMA — test idempotency sejati yang tidak terkontaminasi perbedaan antar master. Uji determinisme untuk input berbeda didelegasikan ke GUD-001 (input identik → output byte-identical).
- **Acceptance**: Seluruh 6 output memiliki SHA-256 checksum identik.
- **Failure path**: Jika output tidak identik, identifikasi source non-determinisme (timestamp, random seed, urutan iterasi dictionary) dan laporkan ke tim engineering untuk mitigasi.

#### E0.2 — FontForge Interpolation Advance Width Test

- **Tujuan**: Memvalidasi bahwa `font.interpolateFonts()` mempertahankan advance width yang identik antara master dan hasil interpolasi.
- **Metode**: Harmonisasi 10 glyph sample (`a`, `g`, `&`, `@`, `M`, `space`, `zero`, `period`, `backslash`, `fi`), interpolasi Medium (factor 0.5), bandingkan advance width Regular original vs Medium hasil interpolasi.
- **Acceptance**: Advance width Medium identik dengan Regular untuk seluruh 10 glyph.
- **Failure path**: Jika advance width berbeda, script `multi_weight_driver.py` HARUS menyalin tabel `hmtx` dari Regular ke seluruh weight baru sebagai post-processing step.
- **Catatan (klarifikasi r2)**: E0.2 adalah eksperimen terpisah dari pemilihan subset PoC (FR-2.1) — subset 10 glyph-nya TIDAK wajib identik dengan daftar FR-2.1.

#### E0.3 — 2-Designer Parallel Work Simulation

- **Tujuan**: Mengkalibrasi throughput aktual harmonisasi dan mengidentifikasi potensi konflik pada shared pool.
- **Metode**: Designer A (Regular↔Bold) dan Designer B (Italic↔BoldItalic) masing-masing mengharmonisasikan 10 glyph bersama (termasuk 2 glyph dari shared pool: Symbols dan ligatures).
- **Acceptance**: Kedua designer menyelesaikan harmonisasi dalam waktu yang sebanding; konflik shared pool teridentifikasi dan strategi resolusi terdokumentasi.
- **Output**: Dokumen `docs/audit/parallel-harmonization-simulation-{date}.md` berisi throughput aktual (glyph/jam per designer) dan aturan first-come-first-served untuk shared pool.

#### E0.4 — Visual Quality Rubric Documentation

- **Tujuan**: Menyusun dokumen acuan kualitas visual yang terukur.
- **Output**: Dokumen `docs/audit/visual-quality-rubric.md` (PATH KANONIK — keputusan Plan v1.7 TASK-0.5) berisi:
  - 5–10 glyph referensi dari Regular existing sebagai gold standard "wibbly-wobbly".
  - 5 contoh distorsi yang tidak dapat diterima (counter tertutup, kurva terlalu kaku, self-intersection).
  - Checklist terstruktur per glyph: *counter shape preserved?*, *Bézier asymmetry maintained?*, *terminal style consistent?*, *no sharp angle discontinuity?*, *stem width proportional?*.

### 6.3 Unit Test Contracts

#### Test: `detect_incompatibility.py`

```
File: tests/test_detect_incompatibility.py

Test Cases:
1. test_identical_glyphs_pass — Dua glyph identik → status "compatible"
2. test_node_count_mismatch — Glyph dengan jumlah node berbeda → status "incompatible", node_diff terisi
3. test_contour_count_mismatch — Glyph dengan jumlah kontur berbeda → status "incompatible", contour_diff terisi
4. test_curve_direction_mismatch — Glyph dengan arah kurva berbeda → status "incompatible"
5. test_glyph_only_in_a — Glyph hanya ada di master A → status "only_in_a"
6. test_glyph_only_in_b — Glyph hanya ada di master B → status "only_in_b"
7. test_report_json_valid — Output JSON valid terhadap schema
8. test_empty_master — Master kosong → exit code non-zero + pesan error

Catatan: file test memakai `pytest.importorskip("fontforge")` di level modul — eksekusi nyata dilakukan di Stage 1 Docker via `pytest tests/ -v` dalam RUN chain multi-weight (§4.9); gate pytest host runner tidak crash tanpa FontForge (klarifikasi r3 — K6).
```

#### Test: `validate_harmonization.py`

```
File: tests/test_validate_harmonization.py

Test Cases:
1. test_all_three_checks_pass — node-count-equal, contour-order-equal, curve-direction-equal → status "pass"
2. test_node_count_fails — Jumlah node berbeda → status "fail", node_count_equal=false
3. test_contour_order_fails — Urutan kontur berbeda → status "fail", contour_order_equal=false
4. test_curve_direction_fails — Arah kurva berbeda → status "fail", curve_direction_equal=false
5. test_multiple_failures — Dua atau lebih kondisi gagal → status "fail", semua flag sesuai
6. test_pass_rate_calculation — Verifikasi kalkulasi pass_rate = pass_count / total_pairs * 100
7. test_strict_mode_exit_code — Mode strict: satu glyph gagal → exit code non-zero

Catatan: file test memakai `pytest.importorskip("fontforge")` di level modul — eksekusi nyata dilakukan di Stage 1 Docker via `pytest tests/ -v` dalam RUN chain multi-weight (§4.9); gate pytest host runner tidak crash tanpa FontForge (klarifikasi r3 — K6).
```

#### Test: `multi_weight_driver.py`

```
File: tests/test_multi_weight_driver.py

Test Cases:
1. test_medium_interpolation_factor — Verifikasi factor 0.5 menghasilkan interpolasi tepat di tengah
2. test_semibold_interpolation_factor — Verifikasi factor 0.67 (toleransi ±0.005)
3. test_copy_as_fallback — Glyph only_in_a disalin ke output tanpa interpolasi
4. test_hmtx_copy — Advance width output identik dengan master Regular
5. test_output_sfdir_structure — Direktori output memiliki struktur .sfdir yang valid
6. test_no_ttfautohint_in_driver — Driver TIDAK memanggil ttfautohint (tanggung jawab Stage 2, REQ-I04)
7. test_dry_run_no_output — Flag --dry-run tidak menulis file apapun
8. test_missing_master_error — Master tidak ditemukan → exit code non-zero
9. test_source_assembly_naming — Direktori build/sources/ berisi nama `FantasqueSansMono-{Weight}.sfdir` sesuai REQ-D02/REQ-B06
10. test_assembly_includes_fantasque_sans — Salinan `FantasqueSans.sfdir` ada di build/sources/ (REQ-B06)
11. test_metadata_injection — Verifikasi injeksi metadata os2_weight/fullname pada `.sfdir` interpolated: unik per weight (500/600) dan tidak identik dengan master (400/700)

Catatan: file test memakai `pytest.importorskip("fontforge")` — eksekusi nyata dilakukan di Stage 1 Docker via `pytest tests/ -v` dalam RUN chain multi-weight (§4.9); gate pytest host runner tidak crash tanpa FontForge.
```

#### Test: `validate_interpolation.py`

```
File: tests/test_validate_interpolation.py

Test Cases:
1. test_pass_status — Glyph tanpa artifact → status "pass"
2. test_warning_status — Minor artifact (toleransi FR-5.4) → status "warning"
3. test_fail_status — Distorsi berat (self-intersection, counter tertutup) → status "fail"
4. test_overlay_png_generated — Flag --overlay-dir menghasilkan PNG untuk status warning/fail
5. test_report_json_valid — Output JSON valid terhadap schema §4.11

Catatan: file test memakai `pytest.importorskip("fontforge")` di level modul — eksekusi nyata dilakukan di Stage 1 Docker via `pytest tests/ -v` dalam RUN chain multi-weight (§4.9); gate pytest host runner tidak crash tanpa FontForge (klarifikasi r3 — K6). Script menerima `--threshold DEG` (default 15.0) dan `--fail-fast` — kontrak §4.11 (klarifikasi r3 — K7/K8); perubahan nilai threshold hanya via parameter eksplisit, bukan parsing rubric markdown.
```

### 6.4 Integration Test — End-to-End Custom Build

```
File: .github/workflows/test-multi-weight-build.yml (opsional, untuk CI)

Test Cases:
1. test_single_weight_backward_compat — enable_multi_weight=false → output identik dengan Custom Build existing (Regular, Bold, Italic, BoldItalic, FantasqueSans) — byte-identical (AC-B03)
2. test_multi_weight_core_only — enable_multi_weight=true → output 4 core weight × 3 format
3. test_build_duration — Total workflow duration ≤ 240 menit
4. test_artifact_structure — ZIP artifact mengandung file dengan nama yang benar
5. test_woff2_size — Total ukuran WOFF2 untuk 6 weight ≤ 500 KB
6. test_flag_forwarding — configure.py --form-enable-multi-weight=true → build-args.txt mengandung flag --multi-weight; false → tanpa flag (§4.9)
```

### 6.5 Test Data Management

- **Fixture glyph**: Glyph sintetis sederhana (segitiga, persegi) digunakan untuk unit test — tidak bergantung pada source font aktual.
- **Fixture `.sfdir`** (`tests/fixtures/multi_weight/` — konten dikunci, deliverable TASK-0.10): 2 master `.sfdir` sintetis (Regular/Bold) berisi ≥ 6 glyph: (a) 3–4 glyph kompatibel dengan koordinat **berbeda antar master** (segitiga/persegi berukuran berbeda — memungkinkan verifikasi numerik factor 0.5/0.67) termasuk **advance width berbeda** (untuk test hmtx-copy), (b) 1 glyph `node_count_mismatch` (menguji detect/validate), (c) 1 glyph `only_in_a` + 1 glyph `only_in_b` (copy-as-fallback & assembly), plus file `font.props` minimal.
- **Cleanup**: Test tidak meninggalkan file output di luar direktori temporary.
- **Mekanisme test assembly (klarifikasi r3 — K12)**: Fixture terkunci tetap kanon minimal (2 master + edge-case glyphs + `font.props`). Test assembly `build/sources/` (test case #9/#10 §6.3) membangun pohon sintetis lengkap **di direktori temp**: menyalin fixture ke `Harmonized/{Regular,Bold}`, menambah stub `Harmonized/{Italic,BoldItalic}` (salinan minimal master) dan stub `FantasqueSans.sfdir` (minimal) — helper test, bukan fixture yang di-commit. Konten fixture yang di-commit tidak berubah.

### 6.6 CI/CD Integration

- Unit test dijalankan pada setiap push ke branch `feature/multi-weight-*`.
- Eksperimen Phase 0 didokumentasikan secara manual (tidak diotomatisasi).
- End-to-end build test dipicu secara manual melalui `workflow_dispatch` pada branch feature.

### 6.7 Coverage Requirements

- Unit test untuk script deteksi dan validasi: ≥ 90% code coverage.
- Integration test: mencakup happy path (core weight build sukses) dan failure path (incompatible glyph, build timeout).

## 7. Implementation Boundaries

### Always Do

- Jalankan `detect_incompatibility.py` dan `validate_harmonization.py` sebelum setiap sesi harmonisasi.
- Commit hasil harmonisasi per batch glyph (bukan per glyph) dengan pesan commit deskriptif: `harmonize: Latin lowercase a-z (26 glyphs) — Regular↔Bold`.
- Sertakan laporan validasi JSON sebagai artifact build.
- Laporkan progres per tahap di build log (GUD-003).
- Validasi advance width setiap weight baru sebelum release (REQ-I03).
- Gunakan Visual Quality Rubric (E0.4) sebagai acuan konsisten untuk seluruh visual review.
- Tandai glyph yang memerlukan perbaikan dalam file tracking JSON `Sources/Harmonized/tracking.json` (schema §4.12) untuk digunakan oleh script harmonisasi ulang.

### Ask First

- Menambah dependency Python baru di luar `future` shim yang sudah ada. **DISETUJUI untuk konteks klarifikasi r3 (K2)**: penambahan `pytest` + `jsonschema` pada instalasi pip Stage 1 (baris `pip3 install --break-system-packages --no-cache-dir future` → `... future pytest jsonschema`) telah disetujui pada sesi r3 — perubahan ini saja; penambahan dependency lain tetap Ask First.
- Mengubah struktur direktori `Sources/Harmonized/` yang telah disepakati.
- Mengubah factor interpolasi untuk core weight (0.5 dan 0.67) — nilai ini adalah kontrak spesifikasi.
- Mengubah nama font family atau nama file output.
- Menambah weight baru di luar daftar yang telah disepakati (Light 300, Medium 500, SemiBold 600, ExtraBold 800).
- Mengubah format output specimen sheet (HTML → format lain).
- Mengubah strategi copy-as-fallback menjadi strategi lain.
- Memodifikasi `Dockerfile` untuk menambah/mengganti package sistem. **DISETUJUI untuk konteks klarifikasi r3 (K2)**: perubahan baris instalasi pip Stage 1 sebagaimana disebut di atas; perubahan Dockerfile lain tetap Ask First.
- Mengubah batas toleransi cacat visual (2%) — nilai ini adalah kontrak spesifikasi (FR-5.4).
- Mengubah threshold discontinuity (15.0°) — nilai ini adalah kontrak spesifikasi (REQ-H06).

### Never Do

- Memodifikasi `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`, atau root `Makefile` (CON-001).
- Menggunakan `font.changeWeight()` atau algoritma stroke modification otomatis (CON-004).
- Merilis weight yang belum melalui visual review type designer.
- Mengabaikan kegagalan validasi harmonisasi — semua glyph dengan status `fail` HARUS diperbaiki sebelum interpolasi.
- Mengubah metrik vertikal (Ascent, Descent, LineGap) antar weight (CON-005).
- Menghapus atau me-rename source `.sfdir` legacy.
- Meng-overwrite source master asli (Regular, Bold, Italic, BoldItalic) dengan versi harmonisasi — harmonisasi selalu ditulis ke `Sources/Harmonized/`.
- Commit file font biner hasil build ke repository.
- Menggunakan format UFO/`fontmake` di V1 (CON-002, ADR-0003).
- Menjalankan `ttfautohint` di Stage 1 / dalam `multi_weight_driver.py` — hinting hanya di Stage 2 (REQ-I04, ADR-0002).

## 8. Rationale, Context & Architecture Decisions (ADRs)

### 8.1 ADR-0003 — Workflow A (FontForge Interpolation) for V1

Keputusan untuk menggunakan Workflow A (FontForge `.sfdir` + `font.interpolateFonts()`) didasarkan pada analisis trade-off antara kecepatan taktis dan kesiapan Variable Font jangka panjang.

**Alasan**: Type designer dapat segera memulai harmonisasi tanpa mempelajari toolchain baru atau melakukan konversi `.sfdir` → `.ufo` yang berisiko. Workflow B (UFO/`fontmake`) tetap menjadi target V2 melalui GH-006.

**Konsekuensi yang diterima**:
- Hanya interpolasi linear yang tersedia — tidak ada optical correction.
- Ekstrapolasi untuk stretch weight (Light, ExtraBold) dapat menghasilkan distorsi; weight ini mengikuti tier partial success.
- V1 tidak dapat menghasilkan Variable Font (`gvar` table).

Referensi lengkap: [`docs/adr/0003-workflow-a-fontforge-v1-interpolation.md`](../docs/adr/0003-workflow-a-fontforge-v1-interpolation.md)

### 8.2 ADR-0002 — Multi-Stage Docker Build

Pipeline multi-weight menggunakan arsitektur Docker multi-stage yang sama dengan Custom Build Workflow. Stage 1 (ubuntu:26.04 + FontForge + Python 3) menjalankan seluruh kompilasi font termasuk harmonisasi dan interpolasi. Stage 2 (ubuntu:26.04 + Python 3.14) menangani auto-hinting, webfont compression, dan packaging.

Referensi lengkap: [`docs/adr/0002-multi-stage-docker-deferred-engine-port.md`](../docs/adr/0002-multi-stage-docker-deferred-engine-port.md)

### 8.3 Pre-Interpolation Architecture Decision

Keputusan untuk menjalankan interpolasi SEBELUM variant expansion (LargeLineHeight, NoLoopK) — bukan sesudahnya — didasarkan pada pertimbangan:

- **Separation of concerns**: Harmonisasi/interpolasi adalah type design step, variant expansion adalah build step.
- **CON-001 compliance**: Pipeline variant expansion tidak disentuh sama sekali — hanya menerima lebih banyak source `.sfdir`.
- **Menghindari ledakan kombinatorial**: Tanpa pre-interpolation, setiap kombinasi varian harus diinterpolasi terpisah (4 kombinasi × 2 weight baru = 8 operasi interpolasi vs 2 operasi dengan pre-interpolation).
- **Cacheability**: File `.sfdir` intermediate dapat di-cache antar build (via GitHub Actions cache; `Sources/Harmonized/Interpolated/` tidak di-commit — lihat §4.2).

### 8.4 Copy-as-Fallback Rationale

Strategi copy-as-fallback dipilih karena jumlah glyph antar master tidak identik (Regular: 1042, Bold: 1040, Italic: 1046, BoldItalic: 1041). Tanpa strategi ini, glyph yang tidak memiliki pasangan di master target akan hilang dari output — tidak dapat diterima untuk font pemrograman yang mengandalkan cakupan karakter lengkap.

### 8.5 Non-ADR Decisions & Spec-Level Resolutions

Keputusan berikut bersifat mudah dibalik atau merupakan resolusi spesifik (tidak memenuhi triple-gate ADR — lihat `.agents/standards/ADR-FORMAT.md`) namun WAJIB didokumentasikan karena dibuat pada Spec v1.1, v1.2, dan v1.5 (sesi klarifikasi r3):

- **Nama file output**: Mengikuti konvensi existing — `FantasqueSansMono-{Weight}.{ext}`. Keputusan obvious, konsisten dengan semua file existing.
- **Format specimen sheet HTML**: Dipilih karena dapat dibuka tanpa server, kompatibel dengan semua OS, dan mudah di-generate secara programatis. **Resolusi konflik PRD internal**: GH-002 dan FR-5.2 menetapkan HTML; GH-005 menyebut "specimen sheet PDF" — disepakati **HTML** sebagai format resmi V1 (PDF tidak diproduksi; dapat ditinjau di V2). **Koreksi GH-005 AC#2**: Specimen dihasilkan sebagai satu set halaman HTML gabungan untuk seluruh weight (memudahkan review side-by-side), bukan satu dokumen terpisah per weight.
- **JSON sebagai format laporan**: Dipilih karena machine-readable, mudah divalidasi dengan schema, dan dapat di-parse oleh downstream tooling.
- **Format WOFF & SVG untuk weight baru (mandat audit C5)**: Diproduksi oleh pipeline (SVG oleh driver, WOFF oleh Stage 2) tetapi **tidak didistribusikan sebagai archive terpisah di release V1** — release tetap 3 archive per FR-6.3 (REQ-D01/REQ-D03). Alasan: FR-6.3 menetapkan 3 archive; WOFF legacy dan SVG tidak dikonsumsi oleh release audience utama. Mudah dibalik: menambahkan archive WOFF/SVG di release berikutnya tidak mengubah pipeline.
- **Stretch weight eksklusif untuk release upstream**: Custom Build (`enable_multi_weight=true`) hanya menghasilkan 4 core weight + output existing; Light/ExtraBold hanya dibangun pada pipeline release upstream (`--enable-light`/`--enable-extrabold`). Konsisten dengan PRD GH-004 dan Clarification E10 — mencegah fork owner mendapat partial build yang tidak konsisten dengan upstream release.
- **`ttfautohint` hanya di Stage 2**: `multi_weight_driver.py` TIDAK melakukan hinting (koreksi konsistensi vs ADR-0002 yang menetapkan Stage 2 sebagai satu-satunya stage hinting). Untuk weight baru, hinting WAJIB dilakukan terlepas dari `UseHinted` — FR-4.3 (kualitas hinting konsisten) mengalahkan opsi build unhinted untuk weight baru; weight existing tetap mengikuti `UseHinted` (REQ-I04).
- **Feeding pipeline via `build/sources/` assembly**: Hasil harmonisasi + interpolasi disatukan di direktori build sementara (REQ-B06) dan driver existing dipanggil dengan `SOURCES_DIR=build/sources` — tanpa modifikasi driver. Alasan: `custom_build_driver.py` men-scan hanya `.sfdir` top-level dan menamai output dari basename direktori; nama direktori assembly menjamin REQ-D02 terpenuhi.
- **`Sources/Harmonized/Interpolated/` tidak di-commit**: Interpolasi bersifat deterministik (GUD-001) sehingga output dapat diregenerasi; menghindari ~4–8 MB bloat repo dan konflik merge. Di-cache via GitHub Actions cache.
- **Koreksi klaim byte-identical FR-7.2**: Mode single-weight (`enable_multi_weight=false`) tidak menyentuh harmonized sources → output **byte-identical dengan V0**. Mode multi-weight membangun Regular/Bold dari harmonized masters → tidak byte-identical (klaim FR-7.2 hanya berlaku untuk mode ini). Spec v1.0 menempatkan catatan ini pada contoh mode single-weight (§10.5) — dikoreksi di v1.1.
- **Threshold discontinuity 15.0°**: Nilai awal; kalibrasi bersifat inheren dalam PoC (visual diff review, FR-2.3) oleh Designer A + maintainer — nilai final direkam di `docs/audit/phase0-experiments-{date}.md` dan `docs/audit/visual-quality-rubric.md`, kemudian dimasukkan ke REQ-H06/§11.2. PRD FR-1.5 menyebut ">N°" tanpa nilai.
- **`features.py` dipanggil in-process oleh driver existing (koreksi PRD §8.1)**: Pemanggilan 6× via subprocess tidak diperlukan — driver existing memanggil `update_features()` untuk setiap `.sfdir` yang dibuild (REQ-B03, §4.7).
- **Konteks eksekusi integrasi multi-weight (koreksi v1.2)**: Script multi-weight (detect, validate, interpolate, assembly) dieksekusi di dalam Stage 1 Docker melalui RUN kondisional pada flag `--multi-weight` di `BUILD_ARGS` — BUKAN step workflow host runner (§4.9). Alasan: FontForge hanya tersedia di image `builder-fontforge` (ADR-0002); host runner dan image Stage 2 tidak memuat FontForge. Konsekuensi: `Scripts/configure.py` diperluas dengan `--form-enable-multi-weight` (tidak dilindungi CON-001) dan Custom Build Spec memerlukan minor update (PRD §8.1, audit C5).
- **Definisi Release Upstream Pipeline (klarifikasi r2)**: Eksekusi **manual/terisolasi oleh upstream maintainer di luar CI** — menjalankan `multi_weight_driver.py --enable-light --enable-extrabold` (lokal atau `docker run` ad-hoc pada image Stage 1), memanfaatkan driver yang sama dengan Custom Build. Stretch weight yang lolos visual review masuk V1; yang gagal dikeluarkan ke V2 (GUD-004). Custom Build (`enable_multi_weight=true`) TIDAK pernah memproduksi stretch weight (E10).
- **Resolusi sesi klarifikasi r3 (Spec v1.5)**: Seluruh keputusan dari `docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r3.md` (K1–K16) diklasifikasikan sebagai spec-level resolutions — mudah dibalik, tidak memenuhi triple-gate ADR. Ringkasan implementasi: (K1) grep portabel tanpa bashism `<<<` + stripping `--multi-weight` → `$DRIVER_ARGS` di RUN chain (§4.9); (K2) instalasi `pytest`/`jsonschema` tidak kondisional di Stage 1 + item Ask First ditandai disetujui (§4.9, §7, §9.2); (K3) gate harmonisasi dua-tingkat — ≥98% checkpoint / `fail_count = 0` pra-interpolasi (AC-H02, §5.1); (K4) validasi harmonisasi kedua pasangan master + sumber Italic/BoldItalic dari harmonized masters (§4.3, §4.9); (K5) kontrak `test_validate_interpolation.py` 5 test case (§6.3); (K6) `pytest.importorskip("fontforge")` di seluruh file test FontForge-dependent (§6.3); (K7) parameter `--threshold` + protokol dua-pass kalibrasi (§4.11, REQ-H06, §11.2); (K8) gating distorsi berat via `validate_interpolation.py --fail-fast` di RUN chain — satu sumber deteksi tanpa duplikasi (§4.6, §4.9); (K9) override hinting weight baru di packaging terlepas `UseHinted` (§4.10, REQ-I04); (K10) komposisi budget WOFF2 dihitung atas 6 weight baru (AC-D03, §4.10); (K11) output ganda `poc_interpolation.py` — `.sfdir` + TTF tanpa hinting (§4.6, §5.2); (K12) pohon sintetis temp untuk test assembly (§6.5); (K13) review manusia 100% glyph PoC (implementasi plan-side); (K14) definisi `RELEASE_MODE=1` + runbook release upstream (§4.10); (K15) entri `.gitignore` untuk `build/` dan `Sources/Harmonized/Interpolated/` (implementasi plan-side, §4.2/§4.9); (K16) jumlah `.sfdir` assembly — 7 (Custom Build) / 9 (release upstream) (VAL-017, §11.1).

## 9. Dependencies & External Integrations

### 9.1 External Systems

| ID | System | Purpose | Interface |
|---|---|---|---|
| **EXT-001** | GitHub Actions | CI/CD orchestration untuk Custom Build multi-weight | `.github/workflows/custom-build.yml` → `workflow_dispatch` |
| **EXT-002** | GitHub Releases | Distribusi release artifact publik | `gh release create` via GitHub Actions |

### 9.2 Third-Party Services & Tools

| ID | Tool | Version Constraint | Purpose | Runtime |
|---|---|---|---|---|
| **SVC-001** | FontForge | Default package ubuntu:26.04 | Font compilation, interpolasi, validasi kontur | Stage 1 Docker |
| **SVC-002** | `ttfautohint` | Default package ubuntu:26.04 | TrueType auto-hinting untuk weight baru | Stage 2 Docker |
| **SVC-003** | `sfnt2woff` (woff-tools) | Default package ubuntu:26.04 | Konversi TTF → WOFF | Stage 2 Docker |
| **SVC-004** | `woff2_compress` (Google WOFF2) | Default package ubuntu:26.04 | Konversi TTF → WOFF2 | Stage 2 Docker |
| **SVC-005** | `future`, `pytest`, `jsonschema` (PyPI) | Latest via pip3 | `future` = compatibility shim (`past.builtins`) untuk engine script Python 2.7 di FontForge Python 3; `pytest` + `jsonschema` = runner & validator unit test yang dieksekusi di RUN chain Stage 1 (klarifikasi r3 — K2) | Stage 1 Docker |

### 9.3 Infrastructure Dependencies

| ID | Component | Requirement | Constraint |
|---|---|---|---|
| **INF-001** | Docker | ≥ 18.x | Multi-stage build: Stage 1 (ubuntu:26.04 + FontForge), Stage 2 (ubuntu:26.04 + Python 3.14) |
| **INF-002** | GitHub Actions Runner | `ubuntu-latest` | Free-tier; batas waktu 360 menit; disk space mencukupi untuk ~6-8 `.sfdir` tambahan (≈2 MB per direktori; total ≈8 MB untuk 4 harmonized masters — terukur dari source existing) |
| **INF-003** | Git Repository | Standard Git LFS tidak diperlukan | File `.glyph` dalam `.sfdir` adalah teks biasa — total tambahan ~4-8 MB untuk 4 harmonized masters |

### 9.4 Data Dependencies

| ID | Data Source | Format | Access Pattern |
|---|---|---|---|
| **DAT-001** | `Sources/FantasqueSansMono-Regular.sfdir/` | FontForge Spline Font Directory | Read-only (source legacy — tidak dimodifikasi) |
| **DAT-002** | `Sources/FantasqueSansMono-Bold.sfdir/` | FontForge Spline Font Directory | Read-only |
| **DAT-003** | `Sources/FantasqueSansMono-Italic.sfdir/` | FontForge Spline Font Directory | Read-only |
| **DAT-004** | `Sources/FantasqueSansMono-BoldItalic.sfdir/` | FontForge Spline Font Directory | Read-only |
| **DAT-005** | `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}/` | FontForge Spline Font Directory | Write-once (output harmonisasi), Read-many (input interpolasi) |
| **DAT-006** | `Sources/Harmonized/Interpolated/{Medium,SemiBold,Light,ExtraBold}/` | FontForge Spline Font Directory | Write-once (output interpolasi), Read-many (input variant expansion) |
| **DAT-007** | Visual Quality Rubric | Markdown document | Read-only (acuan type designer) |

## 10. Examples & Edge Cases

### 10.1 Copy-as-Fallback Scenario

Glyph `uniE0A2` (Powerline symbol) ada di Regular (1042 glyph) tetapi tidak ada di Bold (1040 glyph).

```
Input:
  Regular/uniE0A2.glyph → 5 contours, 23 nodes
  Bold/uniE0A2.glyph → MISSING

Expected output:
  Medium/uniE0A2.glyph → Copy dari Regular (identik)
  SemiBold/uniE0A2.glyph → Copy dari Regular (identik)
  Light/uniE0A2.glyph → Copy dari Regular (identik)
  ExtraBold/uniE0A2.glyph → Copy dari Regular (identik)

Validation:
  - Tidak ada glyph yang hilang dari output
  - Warning dicatat di build log: "uniE0A2: copy-as-fallback dari Regular"
```

### 10.2 Node Count Mismatch — Glyph `g`

Contoh konkret inkompatibilitas kontur yang didokumentasikan di PRD:

```
Input:
  Regular/g.glyph → Kontur ke-3: 21 nodes
  Bold/g.glyph → Kontur ke-3: 22 nodes

Detection output (detect_incompatibility.py):
  {
    "name": "g",
    "status": "incompatible",
    "node_diff": {
      "contour_index": 3,
      "count_a": 21,
      "count_b": 22
    }
  }

Required action:
  Type designer menyelaraskan jumlah node pada kontur ke-3.
  Opsi harmonisasi: (a) tambah 1 node di Regular, atau (b) kurangi 1 node di Bold.
  Keputusan: ditentukan oleh type designer berdasarkan mana yang
  mempertahankan "wibbly-wobbly feel" lebih baik.
```

### 10.3 Discontinuity Detection

Glyph hasil harmonisasi menunjukkan sudut tajam pada ukuran 48 pt:

```
Validation output (soft invariant — 48pt specimen):
  Glyph: "at" (@ sign)
  Status: warning
  Issue: "Tangent angle change 15.3° detected at node 7 on contour 2.
          Threshold: 15.0°."
  Recommended: "Review node 7 placement. Consider adding an intermediate
                control point to smooth the curve transition."
```

### 10.4 Ligature Corruption — Glyph `fi` setelah Interpolasi

```
Scenario:
  Ligature "fi" (f+i) mengalami self-intersection setelah interpolasi Medium.

Detection:
  validate_interpolation.py → status "fail"
  Reason: "Self-intersection detected at contour intersection (x=342, y=518)"

Required action (FR-5.3):
  1. Glyph DIKEMBALIKAN ke tahap harmonisasi (BUKAN diperbaiki langsung
     pada hasil interpolasi).
  2. Type designer memeriksa struktur kontur "fi" di master Regular dan Bold.
  3. Harmonisasi ulang pada glyph "fi".
  4. Interpolasi ulang.
  5. Validasi ulang.

Rationale: Memperbaiki hasil interpolasi tanpa memperbaiki source master
  akan menyebabkan drift antar weight — masalah yang sama akan muncul lagi
  pada interpolasi SemiBold.
```

### 10.5 Custom Build — Fork Owner Tanpa Multi-Weight

```
Scenario:
  Fork owner memicu Custom Build dengan enable_multi_weight = false.

Expected:
  - Build berjalan dalam mode single-weight — pipeline IDENTIK dengan
    Custom Build existing (tanpa pemanggilan detect_incompatibility.py
    dan multi_weight_driver.py).
  - Artifact ZIP berisi output yang sama dengan Custom Build existing:
    Regular, Bold, Italic, BoldItalic, dan FantasqueSans (proportional),
    dalam TTF/OTF/SVG + WOFF/WOFF2 (Stage 2).
  - CATATAN: Output byte-identical dengan V0 — mode ini tidak menyentuh
    harmonized sources. Klaim "TIDAK byte-identical" pada FR-7.2 hanya
    berlaku untuk mode multi-weight (lihat §8.5).
```

### 10.6 Custom Build — Fork Owner dengan Multi-Weight

```
Scenario:
  Fork owner memicu Custom Build dengan enable_multi_weight = true.

Expected:
  - Build menghasilkan 4 core weight (Regular, Medium, SemiBold, Bold)
    + output existing (Italic, BoldItalic, FantasqueSans) — Regular/Bold
    dibangun dari harmonized masters (TIDAK byte-identical dengan V0).
  - Stretch weight (Light, ExtraBold) TIDAK tersedia — hanya di
    release publik upstream (E10).
  - TTF/OTF/WOFF2 dihasilkan; WOFF dan SVG ikut diproduksi pipeline
    namun tidak didistribusikan sebagai archive terpisah (REQ-D01/D03).
  - Build log menampilkan progres per tahap.
  - Artifact ZIP memiliki ukuran ≤ 5 MB.
```

## 11. Validation Criteria

### 11.1 Compliance Checklist

Sebelum spesifikasi ini dianggap terpenuhi, seluruh kriteria berikut HARUS diverifikasi:

- [ ] **VAL-001**: Script `detect_incompatibility.py` menghasilkan laporan JSON yang valid untuk pasangan Regular↔Bold dan Italic↔BoldItalic.
- [ ] **VAL-002**: Script `validate_harmonization.py` melaporkan pass_rate ≥ 98% untuk kedua pasangan master (gate dua-tingkat: ≥98% = checkpoint kemajuan; `fail_count = 0` = syarat masuk Phase 3 — lihat AC-H02, klarifikasi r3 K3).
- [ ] **VAL-003**: Eksperimen E0.1 mengonfirmasi `features.py` bersifat deterministik (6 output identik).
- [ ] **VAL-004**: Eksperimen E0.2 mengonfirmasi advance width identik antara master dan hasil interpolasi.
- [ ] **VAL-005**: Eksperimen E0.3 mendokumentasikan throughput aktual harmonisasi (glyph/jam).
- [ ] **VAL-006**: Eksperimen E0.4 menghasilkan Visual Quality Rubric yang disetujui type designer lead.
- [ ] **VAL-007**: PoC (FR-2.4) LULUS: ≥ 90% glyph dinilai mempertahankan nuansa handwritten; tidak ada distorsi berat.
- [ ] **VAL-008**: 4 core weight (Regular 400, Medium 500, SemiBold 600, Bold 700) tersedia dalam format TTF, OTF, WOFF2.
- [ ] **VAL-008b**: Verifikasi manual cross-platform sukses (install + cek font picker name + verifikasi monospace + ligatures) pada Windows, macOS, dan Linux.
- [ ] **VAL-009**: Advance width identik untuk seluruh weight — terverifikasi dengan teks yang sama di editor monospace.
- [ ] **VAL-010**: Ligature berfungsi di seluruh weight baru.
- [ ] **VAL-011**: Build pipeline `enable_multi_weight = true` selesai dalam ≤ 240 menit.
- [ ] **VAL-012**: Build pipeline `enable_multi_weight = false` tetap berfungsi (kompatibilitas mundur pipeline).
- [ ] **VAL-013**: Specimen sheet HTML menampilkan waterfall, pangram, karakter pemrograman, dan metrik untuk seluruh weight.
- [ ] **VAL-014**: `README.md` diperbarui dengan section Multi-Weight, Faux Italic Limitations, dan contoh CSS.
- [ ] **VAL-015**: Release GitHub berisi archive terpisah per format dengan penamaan file yang benar.
- [ ] **VAL-016**: `validate_interpolation.py` menghasilkan laporan JSON berstatus `pass`/`warning`/`fail` untuk seluruh glyph weight baru (REQ-S05).
- [ ] **VAL-017**: Direktori `build/sources/` hasil assembly memuat **7 `.sfdir`** pada mode Custom Build (4 harmonized masters + Medium + SemiBold + `FantasqueSans.sfdir`) dan **9 `.sfdir`** pada release upstream dengan stretch (8 weight + `FantasqueSans.sfdir`) — selaras §4.7 (7–9) dan klarifikasi r3 (K16).
- [ ] **VAL-018**: Custom Build multi-weight TIDAK memuat stretch weight (E10) — terverifikasi pada artifact test build.

### 11.2 Quantitative Thresholds

| Metric | Threshold | Reference |
|---|---|---|
| Harmonization pass rate | ≥ 98% | SM-T1 |
| Interpolation success rate | ≥ 98% (tanpa distorsi berat) | SM-T2 |
| PoC visual approval rate | ≥ 90% | FR-2.4 |
| Build duration | ≤ 240 menit | SM-T3 |
| WOFF2 total size (6 weights) | ≤ 500 KB | SM-T4 |
| Release archive size | ≤ 5× current release size | SM-T4 |
| Visual artifact tolerance | ≤ 2% (~21 glyph) | FR-5.4 |
| Discontinuity threshold | 15.0° awal → `T_final` via protokol dua-pass (R1 threshold awal → kalibrasi visual diff review → R2 `--threshold T_final`; gate dievaluasi pada R2 — klarifikasi r3 K7). Nilai final direkam di `phase0-experiments-{date}.md` & `visual-quality-rubric.md` | REQ-H06 |
| Unit test coverage | ≥ 90% | §6.7 |

## 12. Related Specifications / Further Reading

### Internal Documents

- [`docs/prd-20260731-1000-multi-weight-variants.md`](../docs/prd-20260731-1000-multi-weight-variants.md) — Product Requirements Document (v1.3)
- [`docs/discovery-draft-20260730-2110-multi-weight-variants.md`](../docs/discovery-draft-20260730-2110-multi-weight-variants.md) — Phase 0 Discovery Draft
- [`docs/audit/clarification-report-multi-weight-variants-2026-07-31.md`](../docs/audit/clarification-report-multi-weight-variants-2026-07-31.md) — Clarification Report
- [`docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-07-31-r2.md`](../docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-07-31-r2.md) — Clarification Report r2 (Implementation Plan)
- [`docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r3.md`](../docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r3.md) — Clarification Report r3 (Implementation Plan)
- [`docs/audit/consistency-audit-multi-weight-variants-2026-07-31.md`](../docs/audit/consistency-audit-multi-weight-variants-2026-07-31.md) — Consistency Audit Report
- [`docs/audit/consistency-audit-plan-vs-prd-spec-2026-08-01.md`](../docs/audit/consistency-audit-plan-vs-prd-spec-2026-08-01.md) — Consistency Audit (Plan vs PRD vs Spec)
- [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) — Project Architecture Documentation
- [`docs/CUSTOM-BUILD.md`](../docs/CUSTOM-BUILD.md) — Custom Build User Guide
- [`spec/spec-custom-build-workflow.md`](./spec-custom-build-workflow.md) — Custom Build Workflow Specification (v1.6)
- [`CONTEXT.md`](../CONTEXT.md) — Domain Glossary

### V2 Preview (GH-006)

- **GH-006** (spike research migrasi Workflow B) — deliverable: ADR perbandingan Workflow A vs B, PoC konversi satu glyph `.sfdir` → UFO v3, dan daftar blocker/unknowns migrasi. **Bukan deliverable V1** — dijadwalkan sebagai pekerjaan paralel/pasca-V1 (PRD GH-006).

### Architecture Decision Records

- [`docs/adr/0002-multi-stage-docker-deferred-engine-port.md`](../docs/adr/0002-multi-stage-docker-deferred-engine-port.md) — Multi-Stage Docker Build
- [`docs/adr/0003-workflow-a-fontforge-v1-interpolation.md`](../docs/adr/0003-workflow-a-fontforge-v1-interpolation.md) — Workflow A (FontForge Interpolation)

### External References

- [FontForge Python API Documentation](https://fontforge.org/docs/scripting/python/fontforge.html) — `font.interpolateFonts()` reference
- [SIL Open Font License (OFL-1.1)](https://openfontlicense.org/) — License terms for all distributed fonts
- [ttfautohint Documentation](https://freetype.org/ttfautohint/) — TrueType auto-hinting parameters
- [WOFF2 Specification (W3C)](https://www.w3.org/TR/WOFF2/) — Web Open Font Format 2.0
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions) — `workflow_dispatch` inputs reference
