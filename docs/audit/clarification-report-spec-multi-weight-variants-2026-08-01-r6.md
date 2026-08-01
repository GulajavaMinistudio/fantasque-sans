<!-- markdownlint-disable -->

# Clarification Report: Technical Specification for Multi-Weight Variants (Spec v1.7 + Plan v1.11 → r6)

- **Tanggal sesi:** 2026-08-01 (r6 — sesi klarifikasi keenam; fokus interogasi Spec dengan acuan Plan; r1: `clarification-report-multi-weight-variants-2026-07-31.md`, r2–r5: `clarification-report-implementation-plan-multi-weight-variants-2026-07-31-r2.md` … `-2026-08-01-r5.md`)
- **Persona:** Clarification Analyst (`/sdlc-clarify-reqs`)
- **Dokumen target interogasi:** `spec/spec-multi-weight-variants.md` (v1.7) dan `plan/plan-feature-multi-weight-variants-v1.11.md` (v1.11)
- **Referensi kontrak:** `docs/prd-20260731-1000-multi-weight-variants.md` (v1.4), `docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r5.md`, `docs/audit/consistency-audit-plan-vs-prd-spec-2026-08-01.md`, `CONTEXT.md`
- **Keputusan user:** Seluruh resolusi (Q-01–Q-17) dijawab berdasarkan rekomendasi Clarification Analyst (delegasi user: "jawab semua pertanyaan klarifikasi dengan jawaban rekomendasi kamu", 2026-08-01). Laporan disimpan atas persetujuan user sebagai clarification reference (r6) — referensi ini wajib dicatat di header Spec (v1.8) dan Plan (v1.12) saat amendemen dijadwalkan.
- **Verifikasi codebase (fakta terkonfirmasi):**
  - `Scripts/custom_build_driver.py`: `parse_args()` menerima `SOURCES_DIR OUTPUT_DIR [--line-height] [--no-loop-k] [--no-calt]` dan `_die("unknown flag(s): ...")` untuk flag lain; `find_sfdirs()` memindai `.sfdir` top-level (sorted); `build_one_weight()` mencetak `"Generating {name}"`, memanggil `_update_features(fnt)` in-process, dan menulis output ke `OUTPUT_DIR/TTF|OTF|Webfonts` — **tanpa subdirektori per varian** (docstring eksplisit).
  - `Scripts/configure.py`: `DEFAULTS` 4 opsi; `FORM_KEY_TO_OPTION` 4 key; `OPTION_TO_DRIVER_FLAG` 3 flag (tanpa `UseHinted`); pola `--form-*` + `--output-args-file` + `--generate-manifest` existing.
  - `Scripts/packaging.sh`: pre-flight `[ -f "${INPUT_MANIFEST}" ]`; `USE_HINTED=$(jq -r '.resolved_options.UseHinted' ...)`; zip-all `fantasque-sans-custom-build.zip`/`.tar.gz`; WOFF/WOFF2 ditulis di `TTF_DIR`; tanpa env var mode (`RELEASE_MODE` belum ada — akan ditambah).
  - `Dockerfile`: Stage 1 `ubuntu:26.04` + apt (`ca-certificates, fontforge, python3-pip, make`), pip line `future`, tanpa `SHELL` directive; `ARG BUILD_ARGS=""`; RUN driver `Sources /build $BUILD_ARGS`; Stage 2 `ubuntu:26.04` + Python 3.14 + `ttfautohint/woff-tools/woff2/zip/tar/jq`; COPY `/build/{OTF,TTF,Webfonts}`.
  - `.github/workflows/custom-build.yml`: 4 input boolean; `timeout-minutes: 30` (akan diubah ke 360); step packaging via `docker run` **tanpa `-e`**; upload path `output/*.zip|*.tar.gz|manifest.json|LICENSE.txt|README.md`; **step auto-create GitHub Release per build** (tag `custom-build-...`, attach `fantasque-sans-custom-build.zip/.tar.gz`).
  - Jumlah glyph master terverifikasi: Regular 1042, Bold 1040, Italic 1046, BoldItalic 1041, FantasqueSans 231 — sesuai klaim Spec §8.4/§10.1.
  - `.gitignore` saat ini: `TeX, *.zip, *.tar.gz, *.deb, *.rpm, *~, Specimen/*.svg, Sources/*.sfd-*, Variants, *.pyc` — **belum** memuat `build/` & `Sources/Harmonized/Interpolated/` (FILE-024 memang diperlukan).
  - `config.schema.json`: 4 properti boolean, `additionalProperties: true`.
  - Script multi-weight (FILE-001..FILE-008) belum dibuat — status Plan `Planned` konsisten.

## 1. 🚨 Resolved Critical Ambiguities (Blockers)

- **Requirement:** "Struktur di atas adalah kontrak output driver existing — driver membuild seluruh `.sfdir` di `SOURCES_DIR` ... dan menamai output dari basename direktori" (ID: Spec §4.3 pohon direktori `Variants/Normal/...`) vs implementasi aktual driver.
  - **Resolution (Q-01 → Opsi A):** **§4.3 diamendemen ke layout aktual** `<output_dir>/TTF|OTF|Webfonts/FantasqueSansMono-{Weight}.{ext}` — `build_one_weight()` menulis langsung ke `OUTPUT_DIR/TTF|OTF|Webfonts` tanpa subdirektori per varian (terverifikasi; docstring eksplisit "no per-variant subdirectory"), konsisten dengan `Dockerfile` Stage 2 (`COPY /build/{OTF,TTF,Webfonts}`) dan `packaging.sh` (`/app/TTF|OTF|Webfonts`). Pohon `Variants/` adalah layout legacy Makefile (bahkan sudah di-ignore di `.gitignore`) — dihapus atau ditandai eksplisit sebagai non-workflow. Plan tidak bergantung pada pohon ini — perubahan Spec-only.

- **Requirement:** Urutan RUN chain — Spec §4.9: `pytest tests/ -v` **sebelum** `multi_weight_driver.py` ("fail-fast sebelum interpolasi"); Plan TASK-4.2(iii): `RUN pytest tests/` **setelah** loop `validate_interpolation --fail-fast`. (ID: Spec §4.9 vs Plan TASK-4.2)
  - **Resolution (Q-02 → Opsi A):** **Posisi Spec dipertahankan** — pytest (dengan `--cov`) dieksekusi **sebelum interpolasi** (validasi tooling lebih dulu, error muncul paling awal); Plan TASK-4.2(iii) dikoreksi agar urutannya: guard → detect → validate kedua pasangan → **pytest --cov** → multi_weight_driver → loop `validate_interpolation --fail-fast` → custom_build_driver.
  - **Catatan coverage path (bagian dari Q-02):** Plan TEST-007 menulis `--cov-report=xml:output/reports/coverage.xml` — path `output/` tidak ada di Stage 1 (direktori host/Stage 2). **Rekomendasi:** laporan ditulis ke `build/reports/coverage.xml` (selaras alur H3: `mkdir -p build` → `COPY /build/build /app/build-reports` → packaging → `output/reports/`); baris `pytest` di §4.9 menjadi varian `--cov` agar klaim §6.7 benar-benar terukur di RUN chain.

- **Requirement:** "Eksplisit jalur eksklusi: `--exclude WEIGHT` flag pada `custom_build_driver.py` untuk meng-skip weight yang gagal validasi" (ID: Plan NOTE-5.4 E2) vs REQ-B06/§4.9 "Driver existing TIDAK dimodifikasi" + `parse_args()` `_die` pada flag tak dikenal.
  - **Resolution (Q-03 → Opsi A):** **Mekanisme `--exclude` dihapus.** Eksklusi stretch yang gagal cukup via tiga jalur existing: (a) tidak meneruskan `--enable-light`/`--enable-extrabold` saat faktor/trial gagal; (b) filter runtime per-file di packaging release (§4.10 — file tidak diproduksi → otomatis tidak masuk archive); (c) verdict `fail` di `tracking.json`. Validasi per-weight terpisah (E2) tetap dipertahankan. Tidak ada modifikasi `custom_build_driver.py` (freeze kontrak).

- **Requirement:** "duplicate `glyph_name + check_type` → overwrite dengan verdict terbaru" (ID: Plan NOTE-2.3 aturan 3) vs schema `tracking.json` §4.12 yang **tidak memiliki field `check_type`**.
  - **Resolution (Q-04 → Opsi A):** **`check_type` dihapus dari NOTE-2.3** — aturan duplikat = per `glyph_name` (sesuai Spec §4.12 aturan 3 yang sudah benar: "entry duplikat untuk glyph yang sama → overwrite dengan verdict terbaru"). `[INFERENCE]` `check_type` adalah sisa schema lama yang memiliki entri per-check.

- **Requirement:** Snippet YAML "Configure build options" §4.9 hanya memuat `--form-*` + `--output-args-file` (ID: Spec §4.9) vs step existing yang juga memuat `--config-file`, `--schema-file`, `--generate-manifest` (terverifikasi di `custom-build.yml` step 5).
  - **Resolution (Q-05 → Opsi A):** **Snippet diganti perluasan step existing** — tambah satu argumen `--form-enable-multi-weight "${{ inputs.enable_multi_weight }}"` pada perintah existing, pertahankan seluruh flag lain. Implementasi literal snippet saat ini akan memutus validasi config dan membuat pre-flight manifest `packaging.sh` gagal. Plan TASK-4.1/4.3 sudah benar — koreksi Spec-only.

- **Requirement:** "Anotasi stage per langkah runbook: ... (6) Stage 2 image (packaging.sh); (7) Stage 2 container" (ID: Plan NOTE-5.4) vs langkah runbook TASK-5.4 yang sebenarnya.
  - **Resolution (Q-06 → Opsi A):** **Anotasi dikoreksi** (off-by-one): langkah (6) `custom_build_driver.py build/sources /build` = **Stage 1 image** (FontForge); (7) ttfautohint + WOFF/WOFF2 = Stage 2 image; (8) `packaging.sh` = Stage 2 container; (5) `configure.py`/manifest = host runner.

- **Requirement:** "`Scripts/validate_harmonization.py` (Validasi node & kontur, termasuk implementasi deteksi *tangent-angle*)" (ID: Plan TASK-0.2) — Spec §4.5 hanya mendefinisikan 3 check (node-count, contour-order, curve-direction); tidak ada kontrak tangent-angle (field output, threshold, semantik `--strict`, test case), dan TASK-0.2 tidak memiliki AC Ref.
  - **Resolution (Q-07 → Opsi A):** **Kontrak ditambahkan ke Spec §4.5**: check ke-4 `curve_smoothness_ok` — deteksi discontinuity antar-node pada glyph harmonisasi, default threshold 15.0° via flag `--threshold`, bersifat **non-blocking terhadap `--strict`** (hanya dilaporkan + field `details`) — konsisten dengan sifat Soft Invariant (REQ-H06: deviasi minor 24–72 pt diizinkan). Tambah 1 test case unit. Menutup celah AC-H05 yang saat ini hanya manual checklist. **Catatan scope: ini PENAMBAHAN beban kerja ke TASK-0.2** (flag baru `--threshold`, field output baru `curve_smoothness_ok`/`details`, +1 test case unit, pembaruan Files/AC Ref) — bukan sekadar koreksi teks; dijadwalkan sebagai beban baru di §4. (Opsi B ditolak: hapus tangent-angle dari TASK-0.2 dan serahkan deteksi otomatis hanya ke `validate_interpolation.py`.)

- **Requirement:** "Meng-inject metadata internal ... `os2_weight` (Medium 500, SemiBold 600), `familyname`, `fullname` — unik per weight dan tidak identik dengan master" (ID: Spec §4.6) vs AC-I03 (font picker menampilkan "Fantasque Sans Mono Medium") dan praktik family grouping.
  - **Resolution (Q-08 → Opsi A):** **Nilai eksak dikunci**: `familyname` = `"Fantasque Sans Mono"` **identik di seluruh weight** (family grouping di font picker); `fullname` = `"Fantasque Sans Mono {Weight}"`; `os2_weight` = 300/400/500/600/700/800 sesuai weight (diperluas ke Light 300 & ExtraBold 800, tidak hanya Medium/SemiBold). Klausul "tidak identik dengan master" hanya berlaku untuk `os2_weight` & `fullname`. `test_metadata_injection` (test #11) disinkronkan dengan nilai eksak ini. **Terverifikasi konsisten dengan master existing** (`Sources/*.sfdir/font.props`): `FamilyName: Fantasque Sans Mono` identik di Regular/Italic/Bold, `FullName` unik per style (`Fantasque Sans Mono Regular|Italic|Bold`), `TTFWeight` 400/400/700 — rekomendasi tidak menimbulkan risiko inkonsistensi naming dengan font existing. [Catatan: Italic memakai `Weight: Book` + `TTFWeight: 400`; pola `fullname = Family + Weight` tetap berlaku.]

- **Requirement:** "`--masters DIR` — Path ke direktori harmonized masters (Regular & Bold)" (ID: Spec §4.11) vs pemanggilan RUN chain `--masters Sources/Harmonized` (direktori induk berisi subdirektori `Regular/`, `Bold/`, ...).
  - **Resolution (Q-09 → Opsi A):** **Kontrak dikunci**: `--masters` = direktori induk yang memuat subdirektori `Regular/` dan `Bold/`; script me-resolve kedua subdirektori tersebut, error non-zero + pesan instruktif jika salah satu hilang. Usage text §4.11 + test case diperbarui.

- **Requirement:** "PoC `configure.py` menggunakan fallback `15.0` hanya jika env var `T_FINAL` tidak diset (di-container Stage 1)" (ID: Plan NOTE-3.X H1) vs r3 K7 (parameterisasi ARG/env **ditolak**) dan r5 B2 (`T_FINAL` = variabel shell RUN chain).
  - **Resolution (Q-13 → Opsi A):** **NOTE-3.X dikoreksi**: `configure.py` tidak memiliki konsep threshold (host-side resolver opsi boolean); `T_FINAL` di-hardcode oleh TASK-4.2 di RUN chain dari `docs/audit/phase0-experiments-{date}.md` (laporan R-full) + `visual-quality-rubric.md`; CLI default `--threshold 15.0` hanya untuk penggunaan manual; **tidak ada fallback env**; runbook mencatat `T_final_source` (path file) untuk reproducibility.

- **Requirement:** "Jika advance width berbeda, script `multi_weight_driver.py` HARUS menyalin tabel `hmtx` ... sebagai post-processing step" (ID: Spec §6.2 E0.2 failure path) vs REQ-I03 (r5 E5: hmtx copy **unconditional**).
  - **Resolution (Q-12 → Opsi A):** **Failure path E0.2 diubah**: hmtx copy adalah post-process unconditional (E5) — bukan keputusan reaktif hasil E0.2; E0.2 tetap dijalankan sebagai eksperimen validasi asumsi (menginformasikan AC-P05), bukan penentu implementasi.

- **Requirement:** "Output: `build/pre_hint/{weight}.ttf`" (ID: Plan NOTE-3.2) vs "direktori `<tmp_output>/TTF` menjadi input `--weights`" (ID: Spec §4.8, klarifikasi r5 B3) — driver menulis ke `<output>/TTF/{name}.ttf`.
  - **Resolution (Q-14 → Opsi A):** **Satu konvensi path**: `build/pre_hint/TTF/` (struktur driver); NOTE-3.2 dikoreksi; frasa "FontForge post-processing (TASK-3.Y → TASK-4.2)" diganti menjadi penjelasan yang akurat (tidak ada task post-processing FontForge — hinting/metadata adalah Stage 2 / `multi_weight_driver.py`; usulan: "sebelum eksekusi Stage 2").

## 2. 🧩 Addressed Edge Cases & Unhandled Scenarios

- **Scenario:** AC-B06 "Artifact ZIP multi-weight ≤ 5 MB" tanpa baseline terukur — zip existing memuat 5 font × 5 format (TTF+OTF+SVG+WOFF+WOFF2) + manifest; multi-weight menambah Medium/SemiBold (+2 font × 5 format, estimasi +40–50%). (ID: AC-B06 vs Plan TASK-4.X)
  - **Handling Strategy (Q-15):** Pengukuran empiris dijadwalkan di TASK-4.X (zip single-weight vs multi-weight); jika > 5 MB → amendemen AC-B06 ke threshold realistik (usulan ≤ 8 MB) via `/sdlc-define-specs`. Nilai ini kontrak yang harus diverifikasi, bukan dipertahankan tanpa bukti.

- **Scenario:** Step `detect_incompatibility.py` di RUN chain hanya untuk pasangan Regular↔Bold (source **legacy**, bukan harmonized), exit code selalu 0 selama laporan dihasilkan (r5 E4), dan pasangan Italic↔BoldItalic tidak melewati detect di CI. (ID: Spec §4.9 vs REQ-H01)
  - **Handling Strategy (Q-16):** Didokumentasikan di §4.9 bahwa laporan detect di CI bersifat **informatif/audit baseline** (artifact via H3); gate kualitas aktual = `validate_harmonization.py --strict` kedua pasangan + `validate_interpolation.py --fail-fast`. Penambahan detect I↔BI opsional (biaya kecil, tidak menambah gate) — bukan rekomendasi utama.

- **Scenario:** Laporan RUN chain ditulis ke `build/*.json` tetapi `build/` tidak di-commit dan tidak dijamin ada di container (tidak ada `mkdir` di Spec §4.9). (ID: Spec §4.9 vs Plan NOTE-4.2(ii))
  - **Handling Strategy (Q-17):** `mkdir -p build` ditambahkan ke catatan kontrak §4.9 (atau kontrak script: `--output` membuat parent dir) — sinkron dengan NOTE-4.2(ii) yang sudah mengagendakan `mkdir -p build` di base Stage 1.

- **Scenario:** REQ-S03/AC-S04 meminta metrik stem width, x-height, cap height, advance width per weight tanpa metode ekstraksi, dan `generate_specimen.py` berjalan via `python3` host (tanpa FontForge) dengan dependency parsing TTF yang tidak didefinisikan. (ID: REQ-S03/AC-S04, Spec §4.8, FILE-004)
  - **Handling Strategy (Q-10):** Metode dikunci: `x_height`/`cap_height` dari tabel OS/2 (sxHeight/sCapHeight) atau `font.x_height`/`font.cap_height` (FontForge); advance width dari `hmtx`; stem width dari `OS/2.usStemV` atau pengukuran glyph referensi (`n`). Dependency: **`fontTools` sebagai dev dependency lokal type designer** (bukan CI) — dicatat di FILE-004; alternatif: jalankan generator di Stage 1 (FontForge) — tidak direkomendasikan (kompleksitas eksekusi lokal).

- **Scenario:** Set karakter pemrograman berbeda antara REQ-S02 (`{}[]()<>;:.,!#$%^&*`) dan §4.8 data contract (`{}[]()<>;:.,!#$%^&*+-=/\|~`@` — lebih lengkap 9 karakter). (ID: REQ-S02 vs Spec §4.8)
  - **Handling Strategy (Q-11):** §4.8 ditetapkan sebagai kontrak operatif; teks REQ-S02 disamakan agar merujuk §4.8. `[INFERENCE]` perbedaan murni ringkasan vs kontrak detail.

## 3. 🔍 Validated Implicit Assumptions

- **Assumption:** Layout output driver existing tidak memiliki subdirektori per varian (`Variants/Normal/...`).
  - **Validation:** **DITERIMA — layout aktual adalah `OUTPUT_DIR/TTF|OTF|Webfonts`** (terverifikasi di `build_one_weight()` docstring dan `Dockerfile` Stage 2 COPY); §4.3 diamendemen (Q-01). Pohon `Variants/` di `.gitignore` adalah artefak legacy Makefile.

- **Assumption:** Workflow `custom-build.yml` memanggil packaging tanpa env var mode sehingga cabang `ENABLE_MULTI_WEIGHT` tidak akan pernah aktif (dasar r4 R1).
  - **Validation:** **DITERIMA** — terverifikasi step 7 workflow: `docker run --rm -v manifest -v output fantasque-custom bash /app/Scripts/packaging.sh` (tanpa `-e`). `RELEASE_MODE=1` + `VERSION` hanya di-invoke manual oleh maintainer (TASK-5.4).

- **Assumption:** Jumlah glyph master yang dikutip Spec §8.4/§10.1 (Regular 1042, Bold 1040, Italic 1046, BoldItalic 1041) akurat.
  - **Validation:** **DITERIMA** — terverifikasi dengan penghitungan file `*.glyph` di `Sources/` (FantasqueSans 231; total file per direktori = glyph + `font.props`).

- **Assumption:** Integrasi `EnableMultiWeight` ke `configure.py` mengikuti pola existing dan aman.
  - **Validation:** **DITERIMA dengan catatan** — `resolve_options()` mengiterasi `DEFAULTS` dan mencocokkan via `FORM_KEY_TO_OPTION`; `EnableMultiWeight` WAJIB ditambahkan ke **kedua** dict + `config.schema.json` + parser + manifest (bila hanya di `DEFAULTS` → `StopIteration`/`KeyError`). Manifest `resolved_options.EnableMultiWeight` tetap info audit (tidak dikonsumsi packaging — r4 R1).

- **Assumption:** Hinting override REQ-I04 (weight baru selalu di-hint) tidak mengubah label output.
  - **Validation:** **DITERIMA DENGAN CATATAN KOSMETIK** — saat `UseHinted=false`, judul release workflow ("(unhinted)") tetap tercetak padahal weight baru di-hint (REQ-I04 override). Disarankan catatan kecil di release notes/TASK-4.3 bahwa weight baru selalu di-hint; tidak mengubah fungsionalitas.

- **Assumption:** Step auto-create GitHub Release pada `custom-build.yml` (existing, per build: tag `custom-build-...`, attach zip/tar.gz) tidak bertabrakan dengan release upstream pipeline.
  - **Validation:** **DITERIMA** — release upstream (3 archive per format, `FantasqueSansMono-{VERSION}-{Format}.zip`) hanya diproduksi runbook manual TASK-5.4; archive custom build otomatis menyertakan Medium/SemiBold via zip-all (AC-B02). Tidak ada konflik penamaan tag/artefak.

## 4. 📝 Next Steps

- **Technical Specification** (`spec/spec-multi-weight-variants.md` v1.7 → v1.8) **HARUS** diperbarui oleh `/sdlc-define-specs` di sesi terpisah:
  - §4.3: layout output aktual `TTF|OTF|Webfonts` (hapus/tandai pohon `Variants/`) — Q-01.
  - §4.5: check ke-4 `curve_smoothness_ok` (non-blocking, `--threshold`) + test case — Q-07.
  - §4.6: nilai eksak metadata (familyname identik, fullname per weight, os2_weight 300–800) — Q-08.
  - §4.8: kontrak `--masters` (direktori induk + subdirektori) — Q-09; sumber metrik specimen + dependency `fontTools` lokal — Q-10; set karakter disamakan dengan REQ-S02 — Q-11.
  - §4.9: snippet YAML = perluasan step existing (Q-05); posisi pytest --cov sebelum interpolasi + path `build/reports/coverage.xml` (Q-02); catatan `mkdir -p build` (Q-17); catatan detect informatif (Q-16).
  - §4.11: usage `--masters` diperjelas — Q-09.
  - §6.2: failure path E0.2 = unconditional hmtx (E5) — Q-12.
  - Header: `clarification_reference` ditambah laporan r6 ini.
- **Implementation Plan** (`plan/plan-feature-multi-weight-variants-v1.11.md` → v1.12) **HARUS** diperbarui oleh `/sdlc-plan-tasks` di sesi terpisah:
  - TASK-0.2: **penambahan scope (beban baru)** — implementasi check ke-4 `curve_smoothness_ok` pada `validate_harmonization.py` sesuai §4.5: flag baru `--threshold` (default 15.0°), field output baru (`curve_smoothness_ok`, `details`), non-blocking terhadap `--strict`; perbarui Files & AC Ref TASK-0.2; **+1 test case unit di TASK-0.9** (`test_validate_harmonization.py`) — Q-07.
  - TASK-0.7/test #11: nilai eksak metadata — Q-08.
  - TASK-2.3 NOTE-2.3: hapus `check_type` — Q-04.
  - TASK-3.2 NOTE-3.2: path `build/pre_hint/TTF/` — Q-14.
  - TASK-3.X NOTE-3.X: koreksi sumber `T_FINAL` (hapus "configure.py fallback env") — Q-13.
  - TASK-4.2: urutan RUN chain (pytest sebelum interpolasi) + path coverage — Q-02.
  - TASK-4.X: pengukuran empiris ukuran zip (AC-B06) — Q-15.
  - TASK-5.4 NOTE-5.4: hapus `--exclude` pada `custom_build_driver.py`; koreksi anotasi stage — Q-03/Q-06.
  - Header: `clarification_reference` ditambah laporan r6 ini.
- **PRD:** tidak ada amendemen wajib (resolusi r6 bersifat spec/plan-level; tidak ada perubahan cakupan produk).
- **CONTEXT.md:** tidak ada istilah kanonis baru yang disepakati sesi ini — tidak ada pembaruan glossary.
- **ADR:** tidak ada keputusan yang memenuhi triple-gate (hard to reverse / surprising / real trade-off) — seluruh resolusi Q-01–Q-17 bersifat mudah dibalik, masuk kategori spec-level resolutions (Spec §8.5).
- **Verifikasi lanjutan:** re-audit konsistensi (`.agents` audit) disarankan setelah Spec v1.8 & Plan v1.12 diterapkan, sebelum fase Code dimulai.
