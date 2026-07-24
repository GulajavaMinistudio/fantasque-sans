# Clarification Report: Terminology & Coverage Fix (Audit Follow-up)

**Sumber Audit:** [`consistency-audit-custom-build-workflow-2026-07-24.md`](./consistency-audit-custom-build-workflow-2026-07-24.md)
**Tanggal:** 2026-07-24
**Persona:** Clarification Analyst

---

## 1. 🚨 Resolved Critical Ambiguities (Blockers)

### CONTEXT.md Self-Contradiction (🔴 HIGH)

- **Masalah:** Definisi **Normal** menggunakan kata `baseline` — yang merupakan istilah dalam daftar `_Avoid_` miliknya sendiri. Selain itu, definisi lama juga menggunakan `default` dan `standar` (padanan `standard`), dua kata lain dari daftar `_Avoid_` yang sama.
- **Definisi lama:** *"Varian default Fantasque Sans Mono tanpa opsi build apapun yang diaktifkan — output baseline dari pipeline build."*
- **Definisi baru:** *"Varian Fantasque Sans Mono tanpa opsi build apa pun yang diaktifkan — hasil pipeline build tanpa modifikasi."*
- **Status:** ✅ **Selesai** — CONTEXT.md baris 15 telah diperbaiki langsung oleh `@ClarificationAnalyst`.

---

## 2. 📋 Daftar Perbaikan Presisi (Find-and-Replace)

> **Instruksi:** Semua perbaikan di bawah bersifat mekanis — setiap kata dari `_Avoid_` sudah memiliki canonical term yang jelas di CONTEXT.md. Tidak ada ambiguitas yang perlu diinterogasi lebih lanjut.

### 2.1 PRD (`docs/prd-20260723-1130-custom-build-workflow.md`)

**Agen pelaksana:** `@ProductManagerPRD`

| # | Baris | Teks Lama | Teks Baru | `_Avoid_` |
|---|-------|-----------|-----------|-----------|
| 1 | 67 | `Custom spacing presets` | `Custom spacing variants` | `presets` → **Variant** |
| 2 | 74 | `Power User / Fork Maintainer` | `Power User / Fork Owner` | `Fork Maintainer` → **Fork Owner** |
| 3 | 85 | `Penny (Power User / Fork Maintainer)` | `Penny (Power User / Fork Owner)` | `Fork Maintainer` → **Fork Owner** |
| 4 | 110 | `preferred build options` | `preferred variant settings` | `build options` → **Variant** |
| 5 | 242 | `pipeline's baseline` | `Normal variant` | `baseline` → **Normal** |
| 6 | 273 | `new config presets` | `new variant configurations` | `presets` → **Variant** |
| 7 | 345 | `a baseline Fantasque Sans Mono build` | `a Normal Fantasque Sans Mono build` | `baseline` → **Normal** |
| 8 | 394 | `the default variant` | `the Normal variant` | `default variant` → **Normal** |

### 2.2 Spec (`spec/spec-custom-build-workflow.md`)

**Agen pelaksana:** `@SpecificationArchitect`

**A. Perbaikan Terminologi:**

| # | Baris | Teks Lama | Teks Baru | `_Avoid_` |
|---|-------|-----------|-----------|-----------|
| 9 | 29 | `Spacing presets` | `Spacing variants` | `presets` → **Variant** |
| 10 | 37 | `one or more build options producing` | `satu atau lebih flag varian yang menghasilkan` | `build options` → **Variant** |
| 11 | 39 | `Baseline Fantasque Sans Mono variant with no build options enabled` | `Fantasque Sans Mono variant with no variant flags enabled` | `baseline` → **Normal**, `build options` → **Variant** |

> **Catatan khusus baris 37 & 39:** Spec §2 *Definitions* memiliki pola kontradiksi-diri yang sama seperti CONTEXT.md sebelumnya — definisi **Variant** dan **Normal** menggunakan kata dari daftar `_Avoid_` miliknya sendiri. Perbaiki kedua baris ini sekaligus.

**B. Missing Coverage — Dokumentasi (FR-9, US-011, US-012, US-013):**

| # | Lokasi | Tindakan |
|---|--------|----------|
| 12 | §1.2 *In Scope* (setelah baris 26) | Tambahkan bullet: `- User documentation: creation of docs/CUSTOM-BUILD.md (Getting Started + Advanced Configuration sections) and README.md update with prominent Custom Build section linking to the guide.` |

---

## 3. 🔍 Validated Implicit Assumptions

- **Asumsi:** `_Avoid_` berlaku untuk bentuk plural dari kata yang sama (misal: `presets` = plural dari `preset`, `build options` = plural dari `build option`).
  - **Validasi:** ✅ Dikonfirmasi. Audit dan standar CONTEXT-FORMAT.md tidak membedakan singular/plural — seluruh variasi morfologis dari istilah `_Avoid_` harus dihindari.

- **Asumsi:** Perbaikan terminologi di Spec §2 harus konsisten dua arah: definisi tidak boleh menggunakan kata dari `_Avoid_` miliknya sendiri.
  - **Validasi:** ✅ Dikonfirmasi. Pola kontradiksi-diri yang sama seperti CONTEXT.md ditemukan di Spec baris 37 dan 39.

---

## 4. 📝 Next Steps

| Urutan | Tindakan | Agen | Status |
|--------|----------|------|--------|
| 1 | Perbaiki CONTEXT.md baris 15 | `@ClarificationAnalyst` | ✅ **Selesai** |
| 2 | Perbaiki PRD (8 lokasi, lihat §2.1) | `@ProductManagerPRD` | ✅ **Selesai (PRD v1.3)** |
| 3 | Perbaiki Spec (3 terminologi + 1 coverage, lihat §2.2) | `@SpecificationArchitect` | ✅ **Selesai (Spec v1.3)** |
| 4 | Audit ulang pasca-perbaikan | `@ArtifactConsistencyChecker` | ⬜ Menunggu |
| 5 | Susun Implementation Plan | `@PlannerArchitect` | ⬜ Menunggu (bergantung pada #2, #3, #4) |

> ⚠️ **Peringatan Handoff:** PRD dan Spec **harus** diperbaiki sesuai daftar di atas sebelum `@PlannerArchitect` dapat menyusun Implementation Plan. Tanpa perbaikan ini, audit konsistensi akan tetap **FAIL** pada kepatuhan Glosarium Domain dan cakupan FR-9.

## 5. ✅ Resolution Confirmation (2026-07-24)

> **Diperbarui oleh:** `@SpecificationArchitect` (out-of-scope, atas perintah eksplisit user) — pembaruan ini **tidak menggantikan** peran `@ArtifactConsistencyChecker` untuk audit ulang independen.

Status item #1, #2, dan #3 dari §4 telah selesai:

- **#1 CONTEXT.md** — selesai sebelumnya oleh `@ClarificationAnalyst` (definisi Normal direvisi, kata `baseline`/`default`/`standar` dihapus).
- **#2 PRD** — selesai oleh `@ProductManagerPRD`. Delapan lokasi diperbaiki per §2.1. PRD sekarang pada **v1.3**.
- **#3 Spec** — selesai oleh `@SpecificationArchitect` (sesi ini). Empat lokasi diperbaiki per §2.2:
  - §1.2 *Out of Scope* (line 30): `Spacing presets` → `Spacing variants`
  - §2 definisi **Variant** (line 38): `build options` → `variant flags`
  - §2 definisi **Normal** (line 40): `Baseline...build options` → `Fantasque Sans Mono variant with no variant flags`
  - §1.2 *In Scope* (line 27, baru): bullet *User documentation* ditambahkan untuk menutup FR-9 + US-011/US-012/US-013
  - Metadata Spec di-bump: `version: 1.2` → `1.3`, `last_updated: 2026-07-23` → `2026-07-24`.

**Item #4 dan #5 tetap menunggu** sesi berikutnya (`@ArtifactConsistencyChecker` untuk re-audit traceability, kemudian `@PlannerArchitect` untuk `/plan/`).
