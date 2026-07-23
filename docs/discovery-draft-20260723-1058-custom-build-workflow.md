---
title: Project Discovery & Architecture Summary — Custom Build Workflow
status: DRAFT (Phase 0)
date_analyzed: 2026-07-23
---
<!-- markdownlint-disable -->
# Project Discovery Summary: Custom Build via GitHub Workflow

## 1. Project Overview

Fitur yang diusulkan adalah sistem **Custom Build berbasis GitHub Workflow** untuk font **Fantasque Sans Mono**, yang terinspirasi langsung oleh arsitektur build [Maple Mono](https://github.com/subframe7536/maple-font). 

Fitur ini memungkinkan pengguna untuk mem-fork repositori Fantasque Sans Mono, menyesuaikan konfigurasi gaya/opsi font (melalui file `config.json` atau form interaktif di GitHub Actions UI `workflow_dispatch`), lalu menjalankan kompilasi font secara otomatis di cloud tanpa perlu menginstal FontForge atau tools kompilasi font di komputer lokal mereka. Hasil kompilasi akhir (`.zip` & `.tar.gz`) dipublikasikan secara otomatis ke **GitHub Releases** dan **Workflow Artifacts**.

---

## 2. Technology Stack & Infrastructure

*(Mereferensikan basis teknologi yang didokumentasikan di `docs/ARCHITECTURE.md` dengan penambahan infrastruktur CI/CD baru)*

- **Core Font Compiler:** FontForge Python API (`import fontforge`) + GNU Make
- **Font Post-Processing:** `ttfautohint` (TrueType hinting), `sfnt2woff` (WOFF), `woff2_compress` (WOFF2)
- **Legacy Engine Language:** Python 2.7 (`past.builtins.xrange`, legacy print syntax)
- **New CI/CD Engine:** GitHub Actions (`workflow_dispatch`, `ubuntu-latest`)
- **New Container Infrastructure:** Docker (Upgrade dari `ubuntu:18.04` ke `ubuntu:24.04` / `ubuntu:22.04` LTS)
- **Configuration Layer (Baru):** `config.json` + `config.schema.json` (JSON Schema draft-07) + Python 3 CLI wrapper

---

## 3. Current Architecture Assessment

### Strengths (Kelebihan Pipeline Saat Ini)
- Engine permutasi biner $2^N$ pada `Scripts/fontbuilder.py` sudah teruji dan mampu menghasilkan kombinasi opsi variasi font secara otomatis.
- Generasi fitur OpenType ligatur (`calt`) pada `Scripts/features.py` fleksibel dan dapat memindai glyph `.liga` secara dinamis.
- Sudah memiliki `Dockerfile` bawaan yang mengemas seluruh pustakaFontForge dan build tools.

### Tech Debt & Risks (Hasil Evaluasi & Grilling Session)
1. **Python 2.7 Dependency:** Pipeline asli ditulis dalam Python 2.7 yang sudah EOL. Strategi yang disepakati adalah **"Wrap, Don't Rewrite"** — menggunakan wrapper layer modern di Python 3 untuk mengontrol pipeline legacy tanpa merusak stabilitas script build asli.
2. **Container EOL:** `Dockerfile` eksisting menginduk pada `ubuntu:18.04` (EOL April 2023). **Keputusan Grilling #2:** Di-upgrade ke Ubuntu LTS terbaru (24.04/22.04) dengan versi tools yang kompatibel.
3. **Hardcoded Options:** Opsi variasi font saat ini terisolasi di dalam `Scripts/build.py`. **Keputusan Grilling #1:** Scope dibatasi pada 3 opsi stabil (`LargeLineHeight`, `NoLoopK`, `NoCalt`) + preset spacing. Opsi alternate glyphs yang file `.glyph`-nya belum ada di `.sfdir` dikeluarkannya dari scope V1.

---

## 4. Operational Workflow (Keputusan Hasil Grilling Session)

### 4.1 Hierarki Konfigurasi (Keputusan Grilling #3)
Sistem akan memproses preferensi build dengan urutan prioritas override sebagai berikut:
```text
Parameter Form GHA (workflow_dispatch) > File config.json di repo fork > Default Fallback
```

### 4.2 Alur Eksekusi End-to-End
1. **Pengguna** mem-fork repositori Fantasque Sans Mono.
2. **Pengguna** mengedit `config.json` (opsional) atau membuka tab **Actions** → pilih **Custom Build** → isi form inputs:
   - `large_line_height` (boolean, default: false)
   - `no_loop_k` (boolean, default: false)
   - `no_calt` (boolean, default: false)
   - `use_hinted` (boolean, default: true)
   - `spacing` (choice: normal, loose, half-loose, half-tight, tight)
3. **GitHub Actions Runner** mengeksekusi workflow:
   - Menyiapkan environment (Docker / Ubuntu LTS runner dengan FontForge, ttfautohint, woff-tools, woff2).
   - Menjalankan `configure.py` (wrapper) untuk menerjemahkan input form/config ke argumen pipeline build.
   - Menjalankan kompilasi font via `make` / Docker container.
4. **Publishing (Keputusan Grilling #4):**
   - Hasil kompilasi terkompresi (`.zip` dan `.tar.gz`) dipublikasikan secara otomatis ke **GitHub Releases** repositori fork dengan tag timestamp & release notes komprehensif.
   - Hasil build juga diunggah sebagai **Workflow Artifacts**.

---

## 5. Handoff Notes for Product Manager (@ProductManagerPRD)

Dokumen ini menandai selesainya **Fase 0 (Discovery & Brainstorming)**. Catatan penting bagi Product Manager sebelum menyusun PRD:

1. **Scope V1 Terisolasi:** PRD harus secara eksplisit membatasi opsi varian pada `LargeLineHeight`, `NoLoopK`, `NoCalt` (disable ligatures), dan `spacing presets`. Jangan memasukkan alternate glyphs (`$` dan `0`) sampai berkas `.glyph` terkait dibuat oleh desainer font.
2. **Zero Breaking Changes pada Engine Existing:** PRD harus menegaskan bahwa pipeline kompilasi asli di `Scripts/` tidak boleh di-rewrite total, melainkan dibungkus (*wrapped*) oleh konfigurasi layer baru.
3. **Distribusi Output:** Acceptance criteria PRD harus mencakup pengujian sukses pada repositori fork (ketersediaan form `workflow_dispatch`, pembuatan file rilis di tab Releases, dan integritas file zip).

---

## 6. Selesai Fase 0 & Instruksi Handoff

Discovery Draft telah disetujui. Untuk melanjutkan ke pembuatan **Product Requirements Document (PRD)** pada SDLC Fase PRD, jalankan perintah berikut di sesi baru:

```text
@ProductManagerPRD Buatkan PRD berdasarkan hasil Discovery Draft di @docs/discovery-draft-20260723-1058-custom-build-workflow.md
```
