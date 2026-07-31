---
title: Project Discovery & Architecture Summary
status: DRAFT (Phase 0)
date_analyzed: 2026-07-30
---
<!-- markdownlint-disable -->

# Project Discovery Summary: Multi-Weight Variants

## 1. Project Overview
Fantasque Sans Mono adalah font pemrograman (monospace) bergaya *handwritten*. Saat ini font didistribusikan dalam format statis TTF/OTF/Webfonts dengan jumlah varian weight yang sangat terbatas (hanya 2: Regular 400 dan Bold 700, ditambah versi italic-nya). Inisiatif eksplorasi ini bertujuan untuk menginvestigasi kelayakan teknis penambahan varian weight multi-level (misal 100-800 seperti pada Maple Mono) untuk meningkatkan fleksibilitas tipografi bagi pengguna modern.

## 2. Technology Stack & Infrastructure

*(Detail arsitektur utama telah didefinisikan secara komprehensif dalam `docs/ARCHITECTURE.md`.)*

Fokus infrastruktur yang relevan untuk penambahan varian weight:
- **Core Font Format:** FontForge Spline Font Directory (`.sfdir`)
- **Key Dependencies (Build):** `fontforge` (dengan Python 3 bindings + `future` shim), `ttfautohint`
- **Missing Infrastructure (Gap Analisis vs Maple Mono):** Tidak adanya dukungan untuk Variable Fonts (`gvar` tables) dan tidak adanya *build toolchain* modern (seperti `fontmake`, `ufo2ft`, dan `fontTools`) yang digunakan standar industri saat ini untuk mengelola multi-weight interpolations.

## 3. Current Architecture Assessment

Dari perspektif *Senior Staff Engineer*, arsitektur font source saat ini menimbulkan tantangan signifikan untuk penambahan weight baru secara otomatis:

- **Strengths:** 
  - Struktur `.sfdir` sudah sangat modular (terpisah per glyph).
  - Metrik dasar (Ascent, Descent, LineGap, Width) antara master Regular dan Bold sudah tersinkronisasi dan identik secara presisi.
- **Tech Debt & Risks (KRITIS):** 
  - **Inkompatibilitas Kontur (Outline Incompatibility):** Data spline antara master `Regular` dan `Bold` **tidak memiliki jumlah titik (node) yang setara**. Contoh: Huruf `g` memiliki 21 titik pada kontur ke-3 di Regular, namun memiliki 22 titik di Bold. Ketidaksesuaian ini akan menyebabkan proses interpolasi otomatis (untuk menghasilkan weight menengah seperti Medium/500) gagal total atau mengalami distorsi bentuk.
  - **Progresi Linear vs Geometris:** Algoritma perubahan stroke dasar (seperti `font.changeWeight()`) akan merusak *counter space* dan detail *handwritten* dari kurva Bézier yang asimetris.

## 4. ⚙️ Operational Workflow (Weight Generation Paths)

Terdapat dua alur utama yang dianalisis untuk menghasilkan weight baru:

1. **Workflow A (FontForge Interpolation - Jangka Pendek):**
   - *Master Harmonization:* Menyeragamkan jumlah titik (`nodes`) dan arah kurva pada seluruh ~1,042 glyph antara Regular dan Bold.
   - *Scripting Interpolation:* Menggunakan `font.interpolateFonts(factor, target)` melalui Python API FontForge untuk menghasilkan varian statis seperti Medium (500) atau SemiBold (600).
   - *Kelemahan:* Keterbatasan interpolasi linear dan harus dieksekusi secara terpisah dari *Custom Build Workflow* yang dilindungi invariant `CON-001`.

2. **Workflow B (UFO Modernization - Standar Industri/Maple Mono):**
   - *Data Conversion:* Mengubah source `.sfdir` menjadi ekosistem UFO v3.
   - *Designspace Definition:* Membuat `.designspace` XML untuk memetakan master pada sumbu koordinat `wght`.
   - *Variable Font Compilation:* Memanfaatkan `fontmake` untuk melakukan *instantiation* yang menghasilkan static instances (Thin 100 - Black 900) dan 1 file Variable Font (VF).

## 5. Handoff Notes for Product Manager (/sdlc-draft-prd)

Product Manager **HARUS** memperhatikan poin-poin berikut sebelum menyusun PRD:

1. **Skala Usaha (Effort Scale):** Penambahan weight ini BUKAN tugas scripting/otomatisasi sederhana. Ini adalah proyek perombakan desain font (type design) karena outline Regular dan Bold saat ini inkompatibel. Ada ~1,042 glyph yang perlu ditinjau/diperbaiki kompatibilitasnya.
2. **Karakter Visual:** PRD harus secara eksplisit mendefinisikan apakah interpolasi matematis dapat diterima jika hal tersebut sedikit menghilangkan "wibbly-wobbly handwriting feel" dari desain aslinya.
3. **Keputusan Tooling:** Jika tujuan akhirnya mencakup pembuatan **Variable Font**, maka PRD harus merencanakan migrasi dari format FontForge ke UFO (`fontmake`), yang akan berdampak langsung pada pipeline CI/CD saat ini.
4. **Strategi Bertahap:** Sangat disarankan agar PRD mendefinisikan "Proof of Concept (PoC)" terlebih dahulu: Menyelaraskan subset 20-30 glyph (a-z) dan mengujinya sebelum merombak ribuan glyph lainnya.

*(Silakan jadikan draf ini sebagai basis untuk memulai fase `/sdlc-draft-prd`)*
