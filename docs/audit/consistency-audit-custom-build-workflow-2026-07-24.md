# Consistency Audit Report: Custom Build via GitHub Workflow

## 1. 📊 Executive Summary

- **Documents Analyzed:**
  - PRD v1.3 ([prd-20260723-1130-custom-build-workflow.md](file:///d:/WebstormProject/fantasque-sans/docs/prd-20260723-1130-custom-build-workflow.md))
  - Spec v1.3 ([spec-custom-build-workflow.md](file:///d:/WebstormProject/fantasque-sans/spec/spec-custom-build-workflow.md))
  - Plan (N/A — belum dibuat)
  - ADR-0001 ([0001-multi-stage-docker-legacy-tools.md](file:///d:/WebstormProject/fantasque-sans/docs/adr/0001-multi-stage-docker-legacy-tools.md)) — Status: Superseded
  - ADR-0002 ([0002-multi-stage-docker-deferred-engine-port.md](file:///d:/WebstormProject/fantasque-sans/docs/adr/0002-multi-stage-docker-deferred-engine-port.md)) — Status: Accepted
  - Domain Glossary ([CONTEXT.md](file:///d:/WebstormProject/fantasque-sans/CONTEXT.md))
- **Audit Date:** 2026-07-24
- **Overall Status:** **PASS WITH WARNINGS**
- **Standards Compliance:** **FAIL** (Pelanggaran Glosarium Domain di PRD, Spec, dan CONTEXT.md itu sendiri)

---

## 2. 🔍 Traceability Findings

_Mapping of requirements from business intent down to technical implementation._

### 2.1 Traceability Matrix: Functional Requirements (FR-1 s/d FR-11)

| PRD FR | Deskripsi | Spec Coverage | Status |
| ------ | --------- | ------------- | ------ |
| FR-1 (P0) | Configuration File (`config.json`) | REQ-001, §4.1, §4.2 | ✅ PASS |
| FR-2 (P0) | Interactive Form (`workflow_dispatch`) | §4.3 | ✅ PASS |
| FR-3 (P0) | Configuration Precedence | REQ-003, §4.4, §9.1 | ✅ PASS |
| FR-4 (P0) | Build Execution (Multi-Stage Docker) | REQ-004, REQ-005, §4.5 | ✅ PASS |
| FR-5 (P0) | Artifact Publishing (`.zip` + `.tar.gz`) | REQ-006, §4.6 | ✅ PASS |
| FR-6 (P0) | GitHub Releases Publishing | REQ-007, §4.7, §9.2 | ✅ PASS |
| FR-7 (P1) | Configuration Schema Validation | REQ-002, §4.2, AC-004 | ✅ PASS |
| FR-8 (P1) | Build Manifest (`manifest.json`) | §4.6, AC-001–AC-005 | ✅ PASS |
| FR-9 (P1) | Documentation (`docs/CUSTOM-BUILD.md` + `README.md` update) | §1.2 *In Scope* (line 27): *User documentation* bullet | ✅ PASS (post-fix, Spec v1.3) |
| FR-10 (P1) | Error Handling & User Feedback | GUD-003, §3.3 | ✅ PASS |
| FR-11 (P2) | Backward Compatibility | CON-001 | ✅ PASS |

### 2.2 Traceability Matrix: User Stories (US-001 s/d US-015)

| PRD US | Deskripsi | Spec Coverage | Status |
| ------ | --------- | ------------- | ------ |
| US-001 (P0) | Trigger Build via Form (defaults) | AC-001 | ✅ PASS |
| US-002 (P0) | Configure via `config.json` | AC-002 | ✅ PASS |
| US-003 (P0) | Form Override `config.json` | AC-003 | ✅ PASS |
| US-004 (P0) | Default Fallback (no config) | AC-001 | ✅ PASS |
| US-005 (P1) | Schema Validation Error | AC-004 | ✅ PASS |
| US-006 (P0) | Download from GitHub Releases | AC-005, §4.7 | ✅ PASS |
| US-007 (P0) | Download from Workflow Artifacts | REQ-006 | ✅ PASS |
| US-008 (P1) | Manifest with Build Metadata | §4.6 | ✅ PASS |
| US-009 (P2) | Local `make` Build Still Works | CON-001 | ✅ PASS |
| US-010 (P0) | Isolated Build Environment | REQ-004, §4.5 | ✅ PASS |
| US-011 (P1) | Documentation for Casual Users | §1.2 *In Scope* (line 27) | ✅ PASS (post-fix, Spec v1.3) |
| US-012 (P1) | Documentation for Power Users | §1.2 *In Scope* (line 27) | ✅ PASS (post-fix, Spec v1.3) |
| US-013 (P1) | README Updated with Prominent Link | §1.2 *In Scope* (line 27) | ✅ PASS (post-fix, Spec v1.3) |
| US-014 (P1) | Build Error Produces Visible Failure | GUD-003, §3.3 | ✅ PASS |
| US-015 (P2) | Build Reproducibility & Audit Trail | §4.6 (`source_commit`, `toolchain_versions`) | ✅ PASS |

### 2.3 Missing Coverage (PRD → Spec)

- **Item 1:** FR-9 (Documentation) + US-011, US-012, US-013
  - **Gap:** PRD secara eksplisit mengamanatkan: (1) pembuatan `docs/CUSTOM-BUILD.md` dengan dua seksi terpisah untuk Casper dan Penny, (2) pembaruan `README.md` dengan seksi "Custom Build" yang prominent, dan (3) screenshot beranotasi untuk alur GitHub Actions. Spec §1.2 *In Scope* tidak menyebutkan *deliverables* dokumentasi ini sama sekali, sehingga tidak ada kontrak teknis yang dapat dipetakan oleh `@PlannerArchitect` ke dalam tugas implementasi.
  - **Severity:** ⚠️ MEDIUM — Dokumentasi adalah P1 dan tiga User Stories (US-011, US-012, US-013) bergantung padanya.

### 2.4 Orphaned Items (Scope Creep)

- **Item:** Tidak Ditemukan.
- **Issue:** Seluruh elemen dalam Spec dapat dilacak kembali ke PRD. Ekstensi skema pada `manifest.json` (seperti `toolchain_versions`, `manifest_version`, dan `spdx_license`) merupakan penjabaran teknis wajar dari FR-8 dan bukan *scope creep*. Penambahan `config_source` sebagai field terpisah di manifest selaras dengan FR-8 PRD.

### 2.5 Contradictions (Cross-Document Conflicts)

- **Issue:** Tidak Ditemukan.
  - Presedensi konfigurasi: PRD FR-3 (`form` > `config.json` > `defaults`) = Spec REQ-003. ✅
  - Format tag release: PRD FR-6 (`custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}`) = Spec REQ-007. ✅
  - Retry semantics: PRD FR-10 (3 attempts, exponential backoff) = Spec GUD-003 (1s, 5s, 25s). ✅
  - `config_source` enum: PRD FR-8 (`defaults|config.json|form|form_override`) = Spec §4.6 manifest schema. ✅
  - `UseHinted` default: PRD FR-1/FR-2 (`true`) = Spec §4.1/§4.2/§4.3. ✅
  - Build duration target: PRD SM-T2 (≤15 min p95) = Spec tanpa kontradiksi (tidak mendefinisikan batas waktu sendiri). ✅

---

## 3. 🛡️ Standards Compliance (Documentation Audit)

### 3.1 ADR Format Compliance: **PASS**

**ADR-0001** (`Superseded by ADR-0002`):

- Mengikuti template mandatory dari [ADR-FORMAT.md](file:///d:/WebstormProject/fantasque-sans/.agents/standards/ADR-FORMAT.md): memiliki `Context`, `Decision`, `Consequences`, dan `Considered Options`.
- Status `Superseded` sudah tepat karena ADR-0002 menggantikannya.
- Triple Gate: Keputusan asli (multi-stage Docker untuk Python 2.7 legacy) memenuhi ketiga kriteria sebelum di-*supersede*. ✅

**ADR-0002** (`Accepted`):

- Triple Gate Validation:
  1. **Hard to reverse:** ✅ — Arsitektur multi-stage Docker dengan Stage 1 (ubuntu:18.04 + Python 2.7) dan Stage 2 (Ubuntu 26.04 + Python 3.14) adalah keputusan infrastruktur fundamental yang mahal untuk diubah.
  2. **Surprising without context:** ✅ — Menggunakan image EOL (ubuntu:18.04) di Stage 1 sambil *sengaja* tidak mem-port engine ke Python 3 akan mengejutkan pembaca tanpa konteks NG-9.
  3. **Real trade-off:** ✅ — Trade-off nyata antara stabilitas kode warisan (menghormati NG-9) vs risiko dependensi glibc lintas versi dan ketergantungan pada image EOL.
- Memiliki seksi `Considered Options` yang menjelaskan alternatif yang ditolak. ✅
- Terminology: Tidak menggunakan istilah *_Avoid_*. ✅
- **Catatan minor:** ADR-0002 memiliki seksi tambahan `Revision Note` yang bukan bagian dari template mandatory, namun ini merupakan ekstensi informatif dan bukan pelanggaran.

### 3.2 Context/Glossary Alignment: ~~FAIL~~ → **RESOLVED** (post-fix, Spec v1.3 + PRD v1.3 + CONTEXT.md)

Audit `_Avoid_` synonym terhadap seluruh dokumen:

| Istilah Terlarang (`_Avoid_`) | Ditemukan Di | Lokasi | Tingkat Keparahan |
| ----------------------------- | ------------ | ------ | ----------------- |
| **"presets"** (Avoid untuk **Variant**) | PRD | §2.3 NG-11: *"Custom spacing presets"* | ⚠️ MEDIUM |
| **"presets"** (Avoid untuk **Variant**) | PRD | §7.2 SM-B5: *"new config presets"* | ⚠️ MEDIUM |
| **"presets"** (Avoid untuk **Variant**) | Spec | §1.2: *"Spacing presets"* | ⚠️ MEDIUM |
| **"baseline"** (Avoid untuk **Normal**) | PRD | §5.3: *"pipeline's baseline"* | ⚠️ MEDIUM |
| **"baseline"** (Avoid untuk **Normal**) | PRD | US-001: *"get a baseline Fantasque Sans Mono build"* | ⚠️ MEDIUM |
| **"baseline"** (Avoid untuk **Normal**) | Spec | §2: *"Baseline Fantasque Sans Mono variant"* | ⚠️ MEDIUM |
| **"baseline"** (Avoid untuk **Normal**) | **CONTEXT.md** | Definisi Normal: *"output baseline dari pipeline build"* | 🔴 HIGH |
| **"build options"** (Avoid untuk **Variant**) | PRD | FR-1 §4.1: *"preferred build options"* | ⚠️ MEDIUM |
| **"build options"** (Avoid untuk **Variant**) | Spec | §2 definisi Variant: *"build options producing"* | ⚠️ MEDIUM |
| **"build options"** (Avoid untuk **Variant**) | Spec | §2 definisi Normal: *"no build options enabled"* | ⚠️ MEDIUM |
| **"Fork Maintainer"** (Avoid untuk **Fork Owner**) | PRD | §3.1: *"Penny — Power User / Fork Maintainer"* | ⚠️ MEDIUM |
| **"Fork Maintainer"** (Avoid untuk **Fork Owner**) | PRD | §3.2: *"Penny (Power User / Fork Maintainer)"* | ⚠️ MEDIUM |
| **"default variant"** (Avoid untuk **Normal**) | PRD | US-004: *"default variant: `Custom Build: Normal (default)`"* | ⚠️ LOW |

> [!NOTE]
> **Resolusi inkonsistensi internal CONTEXT.md (2026-07-24):** Definisi **Normal** di `CONTEXT.md` baris 15 telah direvisi oleh `@ClarificationAnalyst` menjadi *"Varian Fantasque Sans Mono tanpa opsi build apa pun yang diaktifkan — hasil pipeline build tanpa modifikasi."* — kata `baseline`, `default`, dan `standar`/`standard` semuanya dihapus dari definisi. Pelanggaran ini **tidak lagi berlaku**.

### 3.3 ADR Compliance — Kepatuhan Spec terhadap ADR-0002: **PASS**

| Aspek ADR-0002 | Spec Coverage | Status |
| -------------- | ------------- | ------ |
| Stage 1: `ubuntu:18.04` + Python 2.7 + FontForge | §4.5 Dockerfile Stage 1 | ✅ PASS |
| Stage 1: Executes `build.py` + `fontbuilder` + `features` in-process (Python 2.7) | §4.5 `RUN python2.7 Scripts/build.py $BUILD_ARGS` | ✅ PASS |
| Stage 2: `Ubuntu 26.04 LTS` + Python 3.14 (deadsnakes PPA) | §4.5 Dockerfile Stage 2 | ✅ PASS |
| Stage 2: Post-build packaging only (`ttfautohint`, `woff-tools`, `woff2`) | §4.5 Stage 2 packages | ✅ PASS |
| `configure.py` runs on **host runner** (not in container) | §4.4 *"executes on the GitHub Actions runner host"* | ✅ PASS |
| Build args passed via `docker build --build-arg` | §4.5 `ARG BUILD_ARGS` | ✅ PASS |
| Engine port deferred to V2 | §1.2 Out of Scope, §7 Rationale | ✅ PASS |
| NG-9 preserved (no modification to legacy scripts) | CON-001 | ✅ PASS |

### 3.4 Codebase Reality Check: **PASS**

- Arsitektur yang diusulkan selaras dengan batasan struktur repositori yang ada (file `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`, dan `Makefile` tidak dimodifikasi).
- Spec mendefinisikan file-file baru (`Scripts/configure.py`, `config.json`, `config.schema.json`, `.github/workflows/custom-build.yml`, `Dockerfile`) yang tidak berkonflik dengan file yang sudah ada.

---

## 4. 📝 Action Plan (Corrective Actions)

_Clear checklist for the user to fix before invoking `@PlannerArchitect`._

### Updates Required

- [x] **CONTEXT.md** (🔴 PRIORITAS TINGGI): ~~Perbaiki inkonsistensi internal~~ — **SELESAI** (`@ClarificationAnalyst`, 2026-07-24). Definisi **Normal** direvisi; kata `baseline`/`default`/`standar` dihapus.
- [x] **PRD** (⚠️ MEDIUM): ~~8 lokasi~~ — **SELESAI** (`@ProductManagerPRD`, 2026-07-24). PRD sekarang **v1.3**. Verifikasi via grep: nol `_Avoid_` term tersisa di PRD.
  - §2.3 NG-11: Ubah *"Custom spacing presets"* → *"Custom spacing variants"*
  - §7.2 SM-B5: Ubah *"new config presets"* → *"new config variants"* atau *"new variant configurations"*
  - §5.3 edge case: Ubah *"pipeline's baseline"* → *"Normal variant"*
  - US-001 §10.1: Ubah *"a baseline Fantasque Sans Mono build"* → *"a Normal Fantasque Sans Mono build"*
  - §4.1 FR-1: Ubah *"preferred build options"* → *"preferred variant flags"* atau *"preferred variant settings"*
  - §3.1 dan §3.2: Ubah *"Fork Maintainer"* → *"Fork Owner"* untuk persona Penny (atau tambahkan catatan bahwa ini merujuk ke peran persona, bukan istilah domain)
  - US-004 §10.4: Ubah *"default variant"* → *"Normal variant"*
  - (**Agen:** `@ProductManagerPRD`)
- [x] **Spec** (⚠️ MEDIUM): ~~4 lokasi (3 terminologi + 1 coverage)~~ — **SELESAI** (`@SpecificationArchitect`, 2026-07-24). Spec sekarang **v1.3**. Verifikasi via grep: nol `_Avoid_` term tersisa di Spec (di luar entri `_Avoid_:` glossary yang merupakan format wajib).
  - §1.2 Out of Scope: Ubah *"Spacing presets"* → *"Spacing variants"*
  - §1.2 In Scope: Tambahkan *deliverable* dokumentasi: pembuatan `docs/CUSTOM-BUILD.md` dan pembaruan `README.md` sebagai bagian dari scope teknis (untuk menjamin *traceability* FR-9, US-011, US-012, US-013)
  - §2 definisi Variant: Ubah *"one or more build options producing"* → *"one or more variant flags producing"*
  - §2 definisi Normal: Ubah *"Baseline Fantasque Sans Mono variant with no build options enabled"* → *"Fantasque Sans Mono variant with no variant flags enabled"*
  - (**Agen:** `@SpecificationArchitect`)
- [x] **Plan:** Siap dibuat. `@PlannerArchitect` dapat mulai menyusun `/plan/` setelah re-audit traceability oleh `@ArtifactConsistencyChecker` (lihat §6 Resolution Log).
- [x] **Standards (ADR/Context):** ADR-0001 dan ADR-0002 sudah sesuai standar (tidak berubah). `CONTEXT.md` telah direvisi (lihat poin pertama) — inkonsistensi internal teratasi.

### Approval Status

~~**REQUIRED**~~ — **SATISFIED** (post-fix, 2026-07-24). Dokumen PRD v1.3, Spec v1.3, dan `CONTEXT.md` telah diperbaiki sesuai checklist di atas. Spec siap diteruskan ke `@ArtifactConsistencyChecker` untuk re-audit traceability, kemudian ke `@PlannerArchitect` untuk penyusunan Implementation Plan.

---

## 5. 📋 Ringkasan Kelayakan Handoff

| Kriteria | Status | Catatan |
| -------- | ------ | ------- |
| Cakupan FR lengkap (FR-1 s/d FR-11) | ✅ 11/11 (post-fix) | FR-9 tercakup di §1.2 *In Scope* Spec v1.3 (line 27) |
| Cakupan US lengkap (US-001 s/d US-015) | ✅ 15/15 (post-fix) | US-011, US-012, US-013 tercakup di §1.2 *In Scope* Spec v1.3 (line 27) |
| Kepatuhan ADR-0002 | ✅ PASS | Spec sepenuhnya mematuhi keputusan ADR-0002 |
| Kepatuhan Glosarium Domain | ✅ PASS (post-fix) | Nol pelanggaran `_Avoid_` tersisa; verifikasi via grep |
| Bebas scope creep | ✅ PASS | Tidak ada orphaned items |
| Bebas kontradiksi lintas dokumen | ✅ PASS | Semua parameter numerik konsisten |
| Siap untuk handoff ke `@ArtifactConsistencyChecker` (re-audit) | ✅ **SIAP** | PRD v1.3 + Spec v1.3 + CONTEXT.md sudah bersih |
| Siap untuk handoff ke `@PlannerArchitect` (setelah re-audit) | ⏳ **Menunggu re-audit** | Tergantung hasil re-audit traceability oleh `@ArtifactConsistencyChecker` |

---

## 6. ✅ Resolution Log (2026-07-24)

> **Diperbarui oleh:** `@SpecificationArchitect` (out-of-scope, atas perintah eksplisit user) — pembaruan ini **tidak menggantikan** peran `@ArtifactConsistencyChecker` untuk re-audit traceability independen.

Dokumen ini merupakan *snapshot* audit pada 2026-07-24. Seluruh *findings* di §2-§4 bersifat **historis** dan tetap dibiarkan untuk *audit trail*. Bagian ini merangkum status resolusi:

### 6.1 Ringkasan Resolusi

| # | Finding | Severity | Status Resolusi (2026-07-24) |
|---|---------|----------|------------------------------|
| 1 | CONTEXT.md self-contradiction (definisi Normal pakai `baseline`) | 🔴 HIGH | ✅ **Resolved** oleh `@ClarificationAnalyst` — kata `baseline`/`default`/`standar` dihapus dari definisi Normal |
| 2 | 13 pelanggaran `_Avoid_` di PRD (8) + Spec (3) + CONTEXT.md (1, lihat #1) | ⚠️ MEDIUM | ✅ **Resolved** — PRD v1.3 oleh `@ProductManagerPRD`; Spec v1.3 oleh `@SpecificationArchitect` |
| 3 | FR-9 (Documentation) tidak tercakup di Spec | ⚠️ MEDIUM | ✅ **Resolved** — bullet *User documentation* ditambahkan di §1.2 *In Scope* (line 27) |
| 4 | US-011, US-012, US-013 tidak tercakup di Spec | ⚠️ MEDIUM | ✅ **Resolved** — tercakup oleh bullet yang sama (line 27) |

### 6.2 Verifikasi Pasca-Perbaikan

Verifikasi yang dilakukan oleh `@SpecificationArchitect` (sama dengan yang akan dilakukan oleh `@ArtifactConsistencyChecker` di re-audit):

- ✅ `docs/prd-20260723-1130-custom-build-workflow.md` sekarang **v1.3** (bump dari v1.2)
- ✅ `spec/spec-custom-build-workflow.md` sekarang **v1.3** (bump dari v1.2)
- ✅ `CONTEXT.md` definisi **Normal** direvisi (`@ClarificationAnalyst`)
- ✅ Grep `_Avoid_` terms di Spec: nol kemunculan di luar entri `_Avoid_:` glossary (line 39, 41, 43, 45 — format wajib `CONTEXT-FORMAT.md`)
- ✅ FR-9 tercakup di §1.2 *In Scope* Spec (line 27)
- ✅ US-011, US-012, US-013 tercakup di §1.2 *In Scope* Spec (line 27)

### 6.3 Tindak Lanjut

Audit ulang **independen** oleh `@ArtifactConsistencyChecker` tetap **diperlukan** sebelum `@PlannerArchitect` dapat menyusun Implementation Plan. Re-audit diharapkan:

1. Memverifikasi kebenaran pembaruan versi PRD/Spec (v1.2 → v1.3)
2. Memverifikasi kebenaran terminologi pasca-revisi (zero `_Avoid_` violations)
3. Memverifikasi cakupan FR-9 + US-011/012/013 di §1.2 *In Scope* Spec v1.3
4. Memverifikasi bahwa ADR-0002 masih dipenuhi oleh Spec v1.3
5. Memverifikasi tidak ada scope creep baru yang diperkenalkan oleh perubahan

Hanya setelah re-audit PASS, `@PlannerArchitect` dapat mulai menyusun `/plan/`.
