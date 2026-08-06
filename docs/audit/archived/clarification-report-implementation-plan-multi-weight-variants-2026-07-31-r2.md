# Clarification Report: Implementation Plan for Multi-Weight Variants (Plan v1.6)

<!-- markdownlint-disable -->

*Status: Seluruh resolusi sesi ini **menunggu implementasi** ke `plan/plan-feature-multi-weight-variants-v1.3.md` (versi 1.7) oleh `/sdlc-plan-tasks` di sesi terpisah.*

- **Tanggal sesi:** 2026-07-31 (r2 — sesi klarifikasi kedua untuk Implementation Plan; r1: `clarification-report-implementation-plan-multi-weight-variants-2026-07-31.md`)
- **Persona:** Clarification Analyst (`/sdlc-clarify-reqs`)
- **Dokumen target interogasi:** `plan/plan-feature-multi-weight-variants-v1.3.md` (versi 1.6)
- **Referensi kontrak:** `spec/spec-multi-weight-variants.md` (v1.3), `docs/prd-20260731-1000-multi-weight-variants.md` (v1.3), `docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-07-31.md` (r1), `docs/audit/consistency-audit-multi-weight-variants-2026-07-31.md`, `CONTEXT.md`
- **Verifikasi codebase:** `Scripts/configure.py`, `Scripts/custom_build_driver.py`, `Scripts/packaging.sh`, `Dockerfile`, `.github/workflows/custom-build.yml`, `config.schema.json`, `tests/`

## 1. 🚨 Resolved Critical Ambiguities (Blockers)

- **Requirement:** "`timeout-minutes: 30` pada job build (ID: `.github/workflows/custom-build.yml` line 60) vs REQ-B04/FR-7.3/SM-T3 target ≤ 240 menit; plan TASK-4.3 tidak menyebut perubahan timeout"
  - **Resolution:** `timeout-minutes` diubah dari `30` menjadi `360` (batas maksimum GitHub Actions, konsisten dengan CON-007 dan buffer 120 menit di atas target 240 menit). Diakomodasi di TASK-4.3. Mode `false` tidak terpengaruh (build existing selesai jauh lebih cepat).
  - **Plan v1.7:** TASK-4.3 ditambah catatan perubahan `timeout-minutes: 360`.

- **Requirement:** "Unit test driver (`tests/test_multi_weight_driver.py`, TASK-0.10) memerlukan FontForge, tetapi host runner workflow menjalankan `pytest tests/ -v` tanpa FontForge (ID: workflow step "Run unit tests"; Spec §6.1; plan TASK-4.3 'tanpa step baru')"
  - **Resolution:** `tests/test_multi_weight_driver.py` menggunakan `pytest.importorskip("fontforge")` agar gate host tidak crash (`ModuleNotFoundError`). Eksekusi nyata test driver dilakukan di CI melalui RUN `pytest` tambahan di dalam Stage 1 Dockerfile (RUN chain multi-weight, fail-fast sebelum interpolasi). Interpretasi TASK-4.3 diklarifikasi menjadi "tanpa **step workflow** baru — RUN chain Dockerfile boleh diperluas".
  - **Plan v1.7:** TASK-0.10 (catatan `importorskip`), TASK-4.2 (RUN pytest di Stage 1), TASK-4.3 (klarifikasi interpretasi).

- **Requirement:** "TASK-5.4: 'Produksi stretch weights ... di **release upstream pipeline**' dengan dependensi TASK-3.Y — istilah 'release upstream pipeline' tidak pernah didefinisikan dan tampaknya membutuhkan artefak Phase 4 (ID: plan TASK-5.4 vs Spec §4.6/§4.9)"
  - **Resolution:** "Release upstream pipeline" didefinisikan sebagai **eksekusi manual/terisolasi oleh upstream maintainer** — menjalankan `multi_weight_driver.py --enable-light --enable-extrabold` di luar CI (lokal atau `docker run` ad-hoc pada image Stage 1), memanfaatkan driver yang dibangun di TASK-0.7. Dependensi TASK-5.4 → TASK-3.Y **tetap valid**. TASK-5.4 diperkaya sub-checklist "release readiness": dokumen keputusan visual review per stretch weight (lolos → V1 / gagal → V2, GUD-004), lokasi penyimpanan keputusan (mis. `docs/audit/` atau `tracking.json`), dan daftar artifact yang diproduksi. Tidak ada revisi Spec §4.9; tidak ada workflow baru.
  - **Plan v1.7:** TASK-5.4 (definisi jalur + sub-checklist release readiness), RISK-002 (referensi definisi).

- **Requirement:** "Factor `~0.67` (SemiBold) dan factor `TBD` (Light/ExtraBold): 'ditentukan saat PoC' (ID: Spec REQ-I02, §4.6 `--light-factor`/`--extrabold-factor`; FR-2.2 menetapkan PoC hanya Medium; tidak ada task penentu di plan)"
  - **Resolution:** Factor stretch ditetapkan saat **TASK-5.4 (Phase 5)** oleh **Designer A (Lead) + upstream maintainer** berdasarkan trial ekstrapolasi pada subset glyph kritis. Hasil dicatat di dokumen audit baru `docs/audit/stretch-factor-decision-{date}.md` dan menjadi kontrak melalui update Spec §4.6. Nilai `~0.67` **dikunci sebagai 0.67 persis** (≈2/3) dengan toleransi test ±0.005 — tidak dikalibrasi ulang (Spec §7 "Ask First": 0.67 adalah kontrak spesifikasi). Klausa REQ-I02 diamendemen: "factor eksak ditentukan **sebelum produksi stretch** (Phase 5)", selaras dengan FR-2.2 (PoC Medium-only).
  - **Plan v1.7:** TASK-0.10 (toleransi ±0.005 pada test Semibold factor), TASK-5.4 (penetapan factor + dokumen keputusan).

- **Requirement:** "Threshold discontinuity `15.0°` — 'nilai final dikalibrasi saat PoC' (ID: REQ-H06) tanpa task eksekusi kalibrasi di plan (E0.1–E0.4 tidak mencakupnya) dan tanpa script yang secara operasional menghitung tangent-angle (kontrak `validate_harmonization.py` §4.5 hanya 3 kondisi struktur)"
  - **Resolution:** Kalibrasi dilakukan **inheren dalam PoC** — perluasan TASK-1.3/1.X: selama *visual diff review* (FR-2.3), Designer A + maintainer menilai apakah threshold 15.0° menangkap seluruh sudut tajam yang terlihat pada ukuran soft-invariant. Nilai final dicatat di `docs/audit/phase0-experiments-{date}.md` (lokasi yang ditetapkan REQ-H06) **dan** direkam di `visual-quality-rubric.md` sebagai acuan konsisten. Spec REQ-H06/§11.2 di-update sesuai hasil kalibrasi. TASK-0.2 (`validate_harmonization.py`) dan TASK-0.3 (`validate_interpolation.py`) diberi catatan eksplisit bahwa deteksi tangent-angle diimplementasikan di kedua script tersebut.
  - **Plan v1.7:** TASK-0.2, TASK-0.3 (catatan implementasi tangent-angle), TASK-1.3/1.X (kalibrasi inheren PoC).

- **Requirement:** "Gate PoC: TASK-1.X 'Laporan `validate_interpolation.py` menunjukkan ≥90% lulus visual rubric' (script) vs FR-2.4 '≥90% glyph dinilai oleh type designer' (manusia); hubungan ambang dengan TASK-3.X '≤2% minor artifact + 0 distorsi berat' tidak eksplisit; definisi operasional `warning`/`fail` (§4.11) tanpa ambang kuantitatif (ID: plan TASK-1.X/3.X; PRD FR-2.4/FR-5.4; Spec §4.11)"
  - **Resolution:** Gate PoC menjadi **ganda** — LULUS jika keduanya terpenuhi: (i) script: `pass_rate ≥ 90%` dan `fail_count = 0`; (ii) manusia (FR-2.4): seluruh glyph berstatus `warning`/`fail` + sampel glyph `pass` ditinjau oleh type designer dan ≥90% disetujui "mempertahankan nuansa handwritten". Hubungan ambang dinyatakan eksplisit: **PoC (hingga ≤10% `warning`) sengaja lebih longgar dari Phase 3 (≤2% `warning`, FR-5.4)** karena PoC adalah uji kelayakan; ambang ketat berlaku untuk rilis. Definisi operasional dikunci di TASK-0.3: `warning` = artifact non-self-intersect (contoh: tangent-angle > threshold hasil kalibrasi); `fail` = self-intersection / counter tertutup / kontur rusak. Unit hitung = **per glyph** (konsisten FR-5.4: 2% ≈ 21 glyph dari 1.042).
  - **Plan v1.7:** TASK-0.3 (definisi operasional), TASK-1.X (gate ganda), TASK-3.X (klarifikasi relasi ambang).

- **Requirement:** "Kriteria & reviewer 'visual review' tidak ditentukan: siapa yang meninjau core weights (TASK-3.3/3.Y) dan stretch (TASK-5.4); `tracking.json` (§4.12) tidak punya status/field verdict review; path rubric tidak konsisten (plan `docs/audit/visual-quality-rubric.md` vs Spec E0.4 `docs/visual-quality-rubric.md`) (ID: plan TASK-3.3/3.Y/5.4, TASK-0.5; PRD §3.2/§3.3; Spec §4.12)"
  - **Resolution:** Reviewer: **Designer A (Lead) = otoritas final** untuk seluruh glyph core (konsisten peran gatekeeper PRD §3.2/§3.3); Designer B meninjau glyph *shared pool* yang ia kerjakan, hasilnya diteruskan ke A. Untuk TASK-5.4 (stretch): **Designer A + upstream maintainer**. Checklist = `visual-quality-rubric.md` + specimen sheet (TASK-3.2). Dokumentasi keputusan per-glyph dicatat di `tracking.json` (perluasan schema §4.12: field `review_verdict` = `pass|fail` + `reviewed_by` + `date`); ringkasan keputusan gate TASK-3.Y/5.Y dilampirkan di `docs/audit/phase3-visual-review-{date}.md`. Path rubric **diseragamkan** ke satu lokasi kanonik (plan diselaraskan ke Spec atau sebaliknya — keputusan lokasi dicatat di plan v1.7).
  - **Plan v1.7:** TASK-3.3/3.Y (reviewer + dokumen review), TASK-5.4 (reviewer stretch), TASK-0.5 (path rubric + perluasan tracking.json).

- **Requirement:** "Verifikasi 'Metadata internal (os2_weight, fullname) core weight ter-inject benar dan tidak bentrok dengan master' — tanpa metode dan tanpa titik waktu eksekusi (ID: plan TASK-3.X; TASK-0.7; Spec §6.3 tidak memuat test metadata)"
  - **Resolution:** Verifikasi otomatis **dua lapis**: (1) Phase 3 (TASK-3.X) — one-liner FontForge membuka setiap interpolated `.sfdir` dan memeriksa `os2_weight` (500/600), `familyname`, `fullname`: unik per weight dan tidak identik dengan master (Regular 400/Bold 700); (2) Phase 4 (TASK-4.X) — verifikasi pada TTF final: `ttx -t name -t OS/2` dump + `fc-scan` (Linux) + font picker manual (AC-I02/I03). TASK-0.10 ditambah test case ke-11 `test_metadata_injection`.
  - **Plan v1.7:** TASK-3.X (metode lapis 1), TASK-4.X (metode lapis 2), TASK-0.10 (test case ke-11).

- **Requirement:** "Seleksi '~40–50 glyph kritis' PoC: kriteria 'worst offenders' tidak terdefinisi; daftar glyph spesifik tidak didokumentasikan sebagai artefak; sample E0.2 (`M`, `backslash`) tidak identik dengan FR-2.1 (ID: plan TASK-1.1; PRD FR-2.1; Spec §6.2 E0.2)"
  - **Resolution:** Daftar glyph PoC final (nama spesifik per kategori FR-2.1) didokumentasikan sebagai artefak audit `docs/audit/poc-glyph-list-{date}.md`, disusun oleh Designer A saat eksekusi TASK-1.1 dari laporan `detect_incompatibility.py` (TASK-0.1). Kriteria worst-offender kuantitatif: urutkan glyph `incompatible` berdasarkan (1) total `node_diff`, lalu (2) jumlah kontur mismatch, lalu (3) prioritas glyph fungsional/ligature; ambil 3–5 teratas yang belum tercakup kategori lain. E0.2 dinyatakan **eksperimen terpisah** (validasi advance width, dilaporkan di `phase0-experiments`): subset 10 glyph-nya tidak wajib identik dengan FR-2.1 — dicatat satu kalimat di plan.
  - **Plan v1.7:** TASK-1.1 (kriteria + artefak), TASK-0.11 (catatan hubungan E0.2 vs FR-2.1).

- **Requirement:** "TASK-4.4 'Archive release 3 format terpisah: TTF .zip, OTF .zip, WOFF2 .zip (REQ-D03, AC-D01)' vs `packaging.sh` existing (1 archive zip + tar.gz, Custom Build Spec REQ-006) dan step 'Create GitHub Release' yang me-attach nama file hardcoded; AC-B06 menyebut 'Artifact ZIP' tunggal (ID: plan TASK-4.4; Spec REQ-D03/AC-D01/AC-B06; workflow step 11)"
  - **Resolution:** Perilaku berbeda per mode: **Custom Build tetap 1 archive** (zip + tar.gz — REQ-006/AC-B06; step release workflow dan Custom Build Spec **tidak berubah**); **3 archive per format hanya untuk release upstream** (FR-6.3/REQ-D03/AC-D01) — packaging.sh dikontrak dengan *mode switch* (mis. parameter `RELEASE_MODE` atau script packaging release terpisah; penamaan `FantasqueSansMono-{version}-{TTF,OTF,WOFF2}.zip`). TASK-4.4 diarahkan ulang menjadi packaging release upstream.
  - **Plan v1.7:** TASK-4.4 (mode switch + penamaan), TASK-4.3 (klarifikasi step release tidak berubah).

- **Requirement:** "AC-B05/GUD-003 menuntut string literal 'Calling features.py for Regular...' di build log, tetapi `custom_build_driver.py` existing (CON-001, tidak boleh dimodifikasi) mencetak 'Generating {name}'; `multi_weight_driver.py` tidak memanggil `features.py` (REQ-B03) sehingga string tersebut mustahil dihasilkan (ID: Spec GUD-003/AC-B05; PRD GH-004 AC#5; plan TASK-4.X)"
  - **Resolution:** AC-B05/GUD-003 **diamendemen ke daftar pesan progres aktual**: `"Detecting incompatibilities..."` (echo RUN chain) → `"Harmonizing..."` (echo saat harmonized sources dimuat driver) → `"Interpolating Medium (500)..."` (driver baru) → `"Generating {Weight}..."` (driver existing — menggantikan string "Calling features.py for X...") → `"ttfautohint"` / `"packaging: ..."` (Stage 2). Spec GUD-003/AC-B05 dan PRD GH-004 AC#5 diamendemen; verifikasi TASK-4.X (AC-B05) mengacu daftar pesan baru. CON-001 tidak dilanggar.
  - **Plan v1.7:** TASK-4.X (daftar pesan verifikasi baru).

- **Requirement:** "TASK-0.X 'Jalankan semua script validasi dengan dummy input' — konten minimal dummy input tidak didefinisikan agar unit test driver benar-benar menguji interpolasi (ID: plan TASK-0.X; Spec §6.5)"
  - **Resolution:** "Dummy input" = fixture `.sfdir` sintetis yang merupakan **deliverable TASK-0.10** dan di-commit ke `tests/fixtures/multi_weight/`: 2 master `.sfdir` (Regular/Bold) berisi ≥6 glyph — (a) 3–4 glyph kompatibel dengan **koordinat berbeda** antar master (segitiga/persegi berukuran berbeda — memungkinkan verifikasi numerik factor 0.5/0.67) termasuk **advance width berbeda** (untuk test hmtx-copy), (b) 1 glyph `node_count_mismatch` (menguji detect/validate), (c) 1 glyph `only_in_a` + 1 `only_in_b` (copy-as-fallback & assembly), plus `font.props` minimal.
  - **Plan v1.7:** TASK-0.X (definisi dummy input → fixture), TASK-0.10 (deliverable fixture).

## 2. 🧩 Addressed Edge Cases & Unhandled Scenarios

- **Scenario:** Build multi-weight di-terminate CI pada menit ke-30 sebelum interpolasi selesai (estimasi 200–240 menit).
  - **Handling Strategy:** `timeout-minutes` 30 → 360 (batas platform, CON-007); buffer 120 menit di atas target REQ-B04.

- **Scenario:** `pytest tests/ -v` di host runner crash dengan `ModuleNotFoundError: fontforge` setelah test driver ditambahkan.
  - **Handling Strategy:** `pytest.importorskip("fontforge")` di test driver; eksekusi nyata dipindah ke Stage 1 Docker (RUN pytest dalam RUN chain multi-weight).

- **Scenario:** Regresi interpolasi (factor salah, hmtx copy rusak) lolos gate CI karena test driver tidak pernah dieksekusi.
  - **Handling Strategy:** RUN pytest di Stage 1 — test driver dieksekusi di setiap build multi-weight dengan FontForge nyata, fail-fast sebelum interpolasi.

- **Scenario:** Stretch weight diproduksi sebelum jalur rilis siap, atau dependensi TASK-5.4 yang salah membuat Phase 5 berjalan di atas pipeline yang belum terintegrasi.
  - **Handling Strategy:** Definisi "release upstream pipeline" = eksekusi manual maintainer (di luar CI); dependensi TASK-5.4 → TASK-3.Y dinyatakan valid; sub-checklist "release readiness" mengunci kesiapan sebelum rilis.

- **Scenario:** Konflik metadata (os2_weight/fullname bentrok dengan master) baru terdeteksi setelah build penuh oleh pengguna akhir.
  - **Handling Strategy:** Verifikasi dua lapis (`.sfdir` di Phase 3 + TTF final di Phase 4) + unit test `test_metadata_injection`.

- **Scenario:** Ambiguitas interpretasi ambang kelulusan PoC (script vs manusia) dan perbedaan toleransi dengan Phase 3 menimbulkan dispute saat gate.
  - **Handling Strategy:** Gate ganda eksplisit (script ≥90% + manusia ≥90%) dan relasi ambang dikontrak (PoC ≤10% warning = kelayakan; Phase 3 ≤2% = rilis).

- **Scenario:** Path rubric tidak konsisten antara plan (`docs/audit/`) dan Spec (`docs/`) — script/verifikator tidak menemukan dokumen.
  - **Handling Strategy:** Path rubric diseragamkan ke satu lokasi kanonik (diputuskan di plan v1.7).

- **Scenario:** Daftar glyph PoC tidak dapat diverifikasi ulang (AC-P01) karena tidak ada artefak spesifik.
  - **Handling Strategy:** Artefak `docs/audit/poc-glyph-list-{date}.md` dengan kriteria worst-offender kuantitatif.

- **Scenario:** Perubahan packaging ke 3 archive mengubah UX fork owner (breaking change) dan memutus step release workflow yang me-attach nama file hardcoded.
  - **Handling Strategy:** Custom Build tetap 1 archive; 3 archive per format hanya release upstream via mode switch.

- **Scenario:** Pesan log yang menuntut string mustahil ("Calling features.py for X...") memicu modifikasi ilegal `custom_build_driver.py` (CON-001) atau log menyesatkan.
  - **Handling Strategy:** Daftar pesan aktual diamendemen ke Spec/PRD; verifikasi mengacu daftar baru.

- **Scenario:** Test interpolasi hanya smoke test (master tanpa perbedaan koordinat) sehingga factor 0.5/0.67 tidak pernah terverifikasi secara numerik.
  - **Handling Strategy:** Fixture dengan koordinat & advance width berbeda antar master (konten dikunci di TASK-0.10).

## 3. 🔍 Validated Implicit Assumptions

- **Assumption:** FR-2.2 (PoC hanya Medium) harus diamendemen agar PoC mencakup penentuan factor stretch.
  - **Validation:** **DITOLAK** — FR-2.2 dipertahankan; penentuan factor stretch dipindah ke TASK-5.4 (Phase 5); REQ-I02 diamendemen ("sebelum produksi stretch").

- **Assumption:** String log AC-B05 menuntut modifikasi `custom_build_driver.py`.
  - **Validation:** **DITOLAK** — CON-001 dihormati; daftar pesan log diamendemen ke output aktual pipeline ("Generating {Weight}..." dari driver existing).

- **Assumption:** Boundary E10 (stretch tidak pernah diproduksi via jalur Custom Build CI) dapat dilonggarkan untuk memudahkan otomasi.
  - **Validation:** **DITOLAK** — boundary dipertahankan penuh; stretch diproduksi via eksekusi manual maintainer di luar CI.

- **Assumption:** Nilai `0.67` dan `15.0°` bersifat tentatif dan dapat diubah sepihak saat eksekusi.
  - **Validation:** **DITOLAK** — keduanya kontrak spesifikasi (Spec §7 "Ask First"); perubahan hanya melalui amendemen Spec yang terdokumentasi; 0.67 dikunci persis (toleransi test ±0.005), 15.0° dikalibrasi dengan protokol PoC dan dicatat.

- **Assumption:** Packaging release 3-archive (REQ-D03) mengubah perilaku packaging Custom Build existing.
  - **Validation:** **DITOLAK** — Custom Build Spec REQ-006 (1 archive) dan workflow step release tidak berubah; 3-archive hanya mode release upstream.

- **Assumption:** Penilaian kualitas PoC sepenuhnya dapat diotomatisasi (menggantikan type designer).
  - **Validation:** **DITOLAK** — PRD Non-Goal "Otomatisasi penuh tanpa human review" dihormati; gate ganda (script + manusia).

- **Assumption:** GitHub Actions `timeout-minutes` dapat melebihi 360 menit.
  - **Validation:** **DITOLAK** — 360 menit adalah batas platform (CON-007); nilai timeout baru = 360.

- **Assumption:** Test suite driver dapat dieksekusi di host runner (tanpa FontForge).
  - **Validation:** **DITOLAK** — FontForge hanya tersedia di Stage 1 (ADR-0002); eksekusi nyata dipindah ke Stage 1 Docker, host runner memakai `importorskip`.

## 4. 📝 Next Steps

- **Implementation Plan** (`plan/plan-feature-multi-weight-variants-v1.3.md` → v1.7) **HARUS** diperbarui oleh `/sdlc-plan-tasks` di sesi terpisah:
  - TASK-0.2/0.3: catatan implementasi tangent-angle + definisi operasional `warning`/`fail`.
  - TASK-0.5: path rubric diseragamkan; `tracking.json` diperluas (`review_verdict`/`reviewed_by`/`date`).
  - TASK-0.10: `importorskip`, toleransi test ±0.005, test case ke-11 `test_metadata_injection`, deliverable fixture (konten dikunci).
  - TASK-0.11: catatan hubungan E0.2 vs FR-2.1.
  - TASK-0.X: definisi "dummy input" = fixture `tests/fixtures/multi_weight/`.
  - TASK-1.1: kriteria worst-offender + artefak `poc-glyph-list-{date}.md`.
  - TASK-1.3/1.X: kalibrasi inheren threshold 15.0°; gate ganda PoC (script + manusia).
  - TASK-3.X: verifikasi metadata lapis 1 (.sfdir) + klarifikasi relasi ambang ≤2%.
  - TASK-4.2: RUN pytest di Stage 1.
  - TASK-4.3: `timeout-minutes: 360`; klarifikasi "tanpa step workflow baru".
  - TASK-4.4: mode switch packaging release upstream (3 archive per format); Custom Build tetap 1 archive.
  - TASK-4.X: verifikasi metadata lapis 2 (TTX/fc-scan) + daftar pesan log baru.
  - TASK-5.4: definisi release upstream manual + penetapan factor stretch + sub-checklist "release readiness".
  - Artefak audit baru: `poc-glyph-list-{date}.md`, `stretch-factor-decision-{date}.md`, `phase3-visual-review-{date}.md`.

- **Technical Specification** (`spec/spec-multi-weight-variants.md`) **HARUS** diamendemen:
  - REQ-I02: "factor eksak ditentukan sebelum produksi stretch (Phase 5)".
  - REQ-H06/§11.2: hasil kalibrasi threshold 15.0° (diperbarui pasca-PoC).
  - §4.6: nilai factor stretch final dicatat sebagai kontrak.
  - §4.11: definisi operasional `warning`/`fail` (ambang kuantitatif).
  - §4.12: schema `tracking.json` + field `review_verdict`/`reviewed_by`/`date`.
  - §6.2: path E0.4 diseragamkan; catatan E0.2 (eksperimen terpisah dari FR-2.1).
  - §6.3: test case tambahan (metadata injection, toleransi factor).
  - §6.5: konten fixture `.sfdir` minimal (konten dikunci).
  - GUD-003/AC-B05: daftar pesan progres aktual.
  - §8.5: catatan keputusan "release upstream = eksekusi manual maintainer".

- **PRD** (`docs/prd-20260731-1000-multi-weight-variants.md`) **HARUS** diamendemen:
  - GH-004 AC#5: daftar pesan build log baru ("Generating {Weight}..." menggantikan "Calling features.py for X...").
  - Catatan interpretasi FR-2.4: gate ganda (script + manusia).

- **Domain Glossary (CONTEXT.md):** ditambahkan istilah kanonis **"Release Upstream Pipeline"** (lihat file CONTEXT.md yang diperbarui di sesi ini).

- **ADR:** Tidak ada keputusan yang memenuhi triple-gate (hard to reverse / surprising / real trade-off) — seluruh resolusi bersifat mudah dibalik dan masuk kategori *spec-level resolutions* (Spec §8.5). Tidak ada ADR baru yang dibuat.
