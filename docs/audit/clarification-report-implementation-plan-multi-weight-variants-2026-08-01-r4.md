<!-- markdownlint-disable -->

# Clarification Report: Implementation Plan for Multi-Weight Variants (Plan v1.9 → r4)

- **Tanggal sesi:** 2026-08-01 (r4 — sesi klarifikasi keempat untuk Implementation Plan; r1: `clarification-report-implementation-plan-multi-weight-variants-2026-07-31.md`, r2: `...-2026-07-31-r2.md`, r3: `...-2026-08-01-r3.md`)
- **Persona:** Clarification Analyst (`/sdlc-clarify-reqs`)
- **Dokumen target interogasi:** `plan/plan-feature-multi-weight-variants-v1.9.md` (v1.9)
- **Referensi kontrak:** `spec/spec-multi-weight-variants.md` (v1.5), `docs/prd-20260731-1000-multi-weight-variants.md` (v1.4), `docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r3.md`, `docs/audit/consistency-audit-plan-vs-prd-spec-2026-08-01.md`, `CONTEXT.md`
- **Verifikasi codebase:** `Scripts/packaging.sh` (pre-flight wajib `manifest.json`; `USE_HINTED` via `jq` baris 70; archive tunggal `fantasque-sans-custom-build.zip`/`.tar.gz`; tanpa konsep version font), `Scripts/configure.py` (manifest berisi `manifest_version`/`workflow_version`/`source_commit` — tanpa version font; `DEFAULTS` 4 opsi), `Scripts/custom_build_driver.py` (print `"Generating {name}"`), `.github/workflows/custom-build.yml` (step packaging `docker run` tanpa env var; satu-satunya workflow di repo — tidak ada workflow push), `config.schema.json` (4 properti boolean, `additionalProperties: true`), `Dockerfile` (Stage 1 tanpa `SHELL` directive; RUN chain existing tanpa guard), `.gitignore`.

## 1. 🚨 Resolved Critical Ambiguities (Blockers)

- **Requirement:** "`packaging.sh` mode switch: `RELEASE_MODE=1` (release upstream) / `ENABLE_MULTI_WEIGHT=true` (Custom Build multi-weight) / kompatibilitas mundur" (ID: Spec §4.10; Plan TASK-4.4)
  - **Resolution (R1 → Opsi A):** **Cabang `ENABLE_MULTI_WEIGHT` dihapus sepenuhnya.** Tidak ada mekanisme yang menyetel env var ini di CI — workflow `custom-build.yml` memanggil packaging via `docker run` tanpa `-e`, sehingga cabang multi-weight tidak akan pernah aktif (fallback diam-diam ke kompatibilitas mundur). Perilaku Custom Build kembali ke "zip seluruh file di `TTF/`, `OTF/`, `Webfonts/`" (perilaku existing — otomatis menyertakan Medium/SemiBold/FantasqueSans; AC-B02 terpenuhi tanpa daftar weight eksplisit). Override hinting REQ-I04 (K9) diputuskan **murni dari pola nama file**: `NEW_WEIGHTS` = file yang basename-nya match `Medium|SemiBold|Light|ExtraBold` → selalu di-hint; weight existing tetap mengikuti `UseHinted` (dibaca dari manifest via `jq`). Satu-satunya mode eksplisit tetaplah `RELEASE_MODE=1` (K14). Konsekuensi lanjutan: `configure.py` (TASK-4.1) tetap menambahkan `EnableMultiWeight` ke `DEFAULTS`/`FORM_KEY_TO_OPTION`/`OPTION_TO_DRIVER_FLAG` (menghasilkan `--multi-weight` di `BUILD_ARGS` untuk RUN chain Stage 1) — manifest otomatis mencatat `resolved_options.EnableMultiWeight` sebagai informasi audit, tetapi **tidak dikonsumsi oleh packaging**. `config.schema.json` ditambah properti `EnableMultiWeight` (boolean, default `false`) untuk konsistensi.
  - **Catatan:** Menyelesaikan *silent mode fallback*: tanpa R1, Custom Build multi-weight menghasilkan archive 5-weight (tanpa Medium/SemiBold) tanpa error apa pun.

- **Requirement:** "`packaging.sh` menghasilkan archive `FantasqueSansMono-{version}-{Format}.zip` pada mode release" (ID: Spec §4.10/REQ-D03/AC-D01; Plan TASK-4.4, TASK-5.4 langkah 7)
  - **Resolution (R2 → Opsi A):** Sumber nilai `{version}` = **env var eksplisit `VERSION`** yang di-invoke maintainer bersama `RELEASE_MODE=1` (`docker run -e RELEASE_MODE=1 -e VERSION=...`). `packaging.sh` pada mode release mewajibkan `VERSION` — jika kosong, `_die` dengan pesan instruktif. Konsisten dengan pola K14 (seluruh parameter rilis eksplisit dari maintainer; version adalah keputusan rilis, bukan hasil parsing dokumen/tabel font). **Gap kedua yang ditutup:** `packaging.sh` mewajibkan `manifest.json` pada pre-flight (`[ -f "${INPUT_MANIFEST}" ]`), tetapi runbook TASK-5.4 tidak memuat langkah yang menghasilkan manifest — runbook ditambah langkah "jalankan `configure.py` (form args identik dengan build) untuk menghasilkan `manifest.json`" sebelum packaging (pre-flight, kontrak manifest di dalam archive, dan release notes terjaga).
  - **Catatan:** Workflow Custom Build tidak terpengaruh — archive tetap `fantasque-sans-custom-build.zip`/`.tar.gz` (tanpa `VERSION`).

- **Requirement:** "SemiBold (600): interpolasi dengan factor ~0.67; test `test_semibold_interpolation_factor` verifikasi 0.67 (toleransi ±0.005)" (ID: REQ-I01/FR-4.1; Spec §6.3 test case 2; Plan TASK-0.7/0.10/3.1)
  - **Resolution (R3 → Opsi A):** Nilai eksak dikunci **`0.67` (dua desimal)** sebagai kontrak spesifikasi. Toleransi test ±0.005 dimaknai sebagai **kelonggaran presisi float** (artefak perhitungan titik mengambang), bukan kebebasan memilih nilai (mencegah dua implementer memilih `0.67` vs `2/3` = 0.6666… yang menghasilkan koordinat interpolasi berbeda hingga 0.34% dari ekstrem master dan melanggar semangat determinisme GUD-001 antar-varian implementasi). Tidak ada kalibrasi visual untuk SemiBold (interpolasi di dalam rentang master — kalibrasi hanya relevan untuk ekstrapolasi stretch, REQ-I02). Kalimat "~0.67" pada dokumen upstream dimaknai "nilai eksak 0.67 (tanda `~` = pembulatan presentasi)".

## 2. 🧩 Addressed Edge Cases & Unhandled Scenarios

- **Scenario:** Spec §6.6 menetapkan "Unit test dijalankan pada setiap push ke branch `feature/multi-weight-*`", tetapi repo hanya memiliki satu workflow (`custom-build.yml`, `workflow_dispatch` manual) dan plan tidak memuat task yang memenuhi §6.6 (ID: Spec §6.6; Plan Phase 0/4)
  - **Handling Strategy (R4 → Opsi A):** Tambah **TASK-0.14** + **FILE-025**: buat `.github/workflows/test-multi-weight.yml` (trigger: push ke branch `feature/multi-weight-*`) yang menjalankan `pip install pytest jsonschema` + `pytest tests/ -v` di host runner — keempat file test FontForge-dependent di-skip otomatis via `pytest.importorskip("fontforge")` (K6); eksekusi nyata dengan FontForge tetap terjadi di container Stage 1 (RUN chain TASK-4.2 / TASK-0.X). Biaya: rendah (host runner, tanpa build Docker per push); gate cepat untuk pengembangan fitur.
  - **Catatan:** §6.4 (`test-multi-weight-build.yml`, end-to-end) tetap opsional — TASK-4.X menjalankan verifikasi e2e lokal secara manual.

- **Scenario:** `enable_multi_weight=true` dijalankan tanpa direktori `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}` (fork owner belum sync hasil harmonisasi upstream, atau upstream belum meng-commit hasil Phase 2) — `validate_harmonization.py --strict` gagal dengan error mentah FontForge ("unable to open") tanpa pesan instruktif (ID: Spec §4.9 RUN chain; Plan TASK-4.2)
  - **Handling Strategy (R5 → Opsi A):** Tambah **guard eksplisit** di awal RUN chain Stage 1 (sebelum `detect_incompatibility.py`/`validate_harmonization.py`): periksa keberadaan keempat direktori `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}`; jika salah satu hilang → `echo "::error::multi-weight build requires harmonized sources (Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}); sync upstream or run harmonization first" >&2; exit 1`. Prasyarat harmonized sources dicatat di `README.md` section multi-weight (TASK-4.5). Fail-fast tetap terjaga (GUD-002), pesan menjadi actionable bagi fork owner.

## 3. 🔍 Validated Implicit Assumptions

- **Assumption (R1):** Cabang `ENABLE_MULTI_WEIGHT` di Spec §4.10 dapat diaktifkan di CI tanpa mekanisme penyampaian sinyal.
  - **Validation:** **DITOLAK.** Workflow memanggil `packaging.sh` tanpa env var; `packaging.sh` hanya membaca manifest via `jq` (pola `UseHinted`). Tanpa R1, cabang multi-weight tidak pernah aktif di CI (silent fallback). Resolusi: hapus cabang; perilaku berbasis file (zip-all + pola nama untuk override hinting) — lihat R1.
- **Assumption (R2):** Nilai `{version}` pada penamaan archive release tersedia secara implisit di lingkungan packaging.
  - **Validation:** **DITOLAK.** Tidak ada version font di manifest (`configure.py` hanya menulis `manifest_version`, `workflow_version`, `source_commit`), di env container, maupun di runbook. Resolusi: env var eksplisit `VERSION` + langkah generate manifest di runbook — lihat R2.
- **Assumption (R3):** "~0.67" + toleransi test ±0.005 cukup mengunci nilai factor SemiBold.
  - **Validation:** **DITOLAK.** Dua nilai berbeda (`0.67` vs `2/3`) lolos toleransi dan menghasilkan output berbeda. Resolusi: kunci `0.67` eksak — lihat R3.
- **Assumption (R4):** Kewajiban Spec §6.6 terpenuhi oleh gate pytest host runner pada `custom-build.yml` (manual dispatch).
  - **Validation:** **DITOLAK.** §6.6 mensyaratkan eksekusi *pada setiap push* ke branch fitur — workflow manual tidak memenuhi trigger push. Resolusi: TASK-0.14 + FILE-025 (workflow push) — lihat R4.
- **Assumption (R5):** Kegagalan `validate_harmonization.py --strict` tanpa harmonized sources sudah cukup informatif.
  - **Validation:** **DITOLAK.** Error mentah FontForge tidak menuntun pengguna. Resolusi: guard eksplisit dengan pesan instruktif — lihat R5.

## 4. 📝 Next Steps

- **Implementation Plan** (`plan/plan-feature-multi-weight-variants-v1.9.md` → v1.10) **HARUS** diperbarui oleh `/sdlc-plan-tasks` di sesi terpisah:
  - TASK-4.4: hapus cabang `ENABLE_MULTI_WEIGHT`; perilaku Custom Build = zip-all existing; override hinting via pola nama file `NEW_WEIGHTS` (`Medium|SemiBold|Light|ExtraBold`); mode eksplisit hanya `RELEASE_MODE=1`; env var `VERSION` wajib (guard `_die` jika kosong) untuk penamaan `FantasqueSansMono-{VERSION}-{Format}.zip` — R1/R2.
  - TASK-5.4: runbook 9 langkah diperluas → tambah langkah generate `manifest.json` via `configure.py` sebelum packaging (pre-flight `packaging.sh`); perjelas langkah 5 menjadi `custom_build_driver.py build/sources /build` (SOURCES_DIR + OUTPUT_DIR, kontrak driver) — R2 + MO-1.
  - TASK-0.7/3.1: nilai factor SemiBold dikunci `0.67` eksak (bukan "~0.67") — R3.
  - TASK-0.10: catatan test case 2 — verifikasi `0.67`; toleransi ±0.005 = kelonggaran presisi float — R3.
  - TASK-4.2: tambah guard `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}` di awal RUN chain (pesan `::error::` + `exit 1`) — R5.
  - TASK-4.1: perjelas `EnableMultiWeight` masuk `DEFAULTS`/`FORM_KEY_TO_OPTION`/`OPTION_TO_DRIVER_FLAG` + properti `config.schema.json` (boolean, default `false`); manifest mencatatnya sebagai informasi audit (tidak dikonsumsi packaging) — R1.
  - TASK-4.5: catat prasyarat harmonized sources di README section multi-weight — R5.
  - TASK-0.14 (**BARU**): `.github/workflows/test-multi-weight.yml` (push `feature/multi-weight-*`, pytest host runner) + FILE-025 — R4.
  - TEST-003/§6.6: catatan eksekusi push-gate (host) vs eksekusi nyata (Stage 1) — R4.
  - Changelog v1.10 + `clarification_reference` rujuk laporan r4 ini.

- **Technical Specification** (`spec/spec-multi-weight-variants.md` → v1.6) **HARUS** diamendemen:
  - §4.10: pseudo-code packaging disederhanakan — hapus cabang `ENABLE_MULTI_WEIGHT`; perilaku berbasis file (zip-all + pola nama `NEW_WEIGHTS`); definisi `VERSION` (env var eksplisit, wajib pada `RELEASE_MODE=1`, guard `_die`); penamaan archive `FantasqueSansMono-${VERSION}-${Format}.zip` — R1/R2.
  - §4.9: RUN chain ditambah guard eksistensi `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}` (pesan `::error::` + exit 1) — R5.
  - REQ-I01/§6.3 test case 2: nilai eksak `0.67` dikunci; toleransi ±0.005 = kelonggaran presisi float — R3.
  - §4.6/§6.6: catatan implementasi push-gate (workflow `test-multi-weight.yml`, host runner, `importorskip`) — R4.

- **PRD** (`docs/prd-20260731-1000-multi-weight-variants.md`): tidak ada amendemen wajib; catatan interpretasi FR-4.1 ("~0.67" → eksak `0.67`) bersifat opsional (R3).

- **Domain Glossary (CONTEXT.md):** Tidak ada istilah kanonis baru yang disepakati pada sesi ini — `VERSION` dan `RELEASE_MODE` adalah variabel teknis, bukan istilah domain. Tidak ada pembaruan glossary.

- **ADR:** Tidak ada keputusan yang memenuhi triple-gate (hard to reverse / surprising / real trade-off) — seluruh resolusi (R1–R5) bersifat mudah dibalik dan masuk kategori *spec-level resolutions* (Spec §8.5). Tidak ada ADR baru yang dibuat.

- **Minor Observations (MO) untuk plan implementer:**
  - MO-1: Runbook TASK-5.4 langkah 5 menyebut `custom_build_driver.py build/sources` tanpa argumen output — perjelas `custom_build_driver.py build/sources /build` (kontrak `SOURCES_DIR OUTPUT_DIR`).
  - MO-2: `validate_interpolation.py --fail-fast` di RUN chain tidak meneruskan `--overlay-dir` — overlay PNG (AC-I08) dipenuhi pada review manual Phase 3 (TASK-3.X); tidak perlu perubahan.
  - MO-3: Pseudocode §4.10 mode release mencantumkan `FantasqueSans` — dikonfirmasi konsisten dengan K16 (9 `.sfdir` assembly) dan perilaku zip-all; archive release menyertakan `FantasqueSans` (tidak ada regresi vs release existing).
