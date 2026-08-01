# Clarification Report: Implementation Plan for Multi-Weight Variants (Plan v1.8 → r3)

<!-- markdownlint-disable -->

*Status (diperbarui 2026-08-01): **Sebagian terimplementasi.** Amendemen `spec/spec-multi-weight-variants.md` (v1.4 → **v1.5**) oleh `/sdlc-define-specs` **SELESAI** — seluruh poin amendemen spec pada §4 (Next Steps) telah diterapkan: §4.9 (RUN chain — grep portabel, `DRIVER_ARGS` strip, validasi kedua pasangan master, loop `validate_interpolation.py --fail-fast`, instalasi pytest/jsonschema Stage 1), §4.6 (gating distorsi berat via `validate_interpolation.py` + kontrak output TTF `poc_interpolation.py`), §4.10 (definisi `RELEASE_MODE` + komposisi budget WOFF2 6 weight), §6.3 (catatan `importorskip` seluruh file test FontForge-dependent + kontrak `--threshold`), §6.5 (mekanisme test assembly — pohon sintetis temp), §7 (item Ask First Dockerfile/pip ditandai disetujui untuk konteks r3), §9.2 (SVC-005 diperluas menjadi future + pytest + jsonschema), §11.1 (VAL-017 — 7/9 `.sfdir`), AC-H02 (gate dua-tingkat), REQ-H06/§4.11 (parameter `--threshold` + protokol dua-pass kalibrasi), REQ-I04 (mekanisme override hinting weight baru), §4.3 (sumber Italic/BoldItalic dari harmonized masters), §5.2 AC-P02 (kontrak output `poc_interpolation.py`), §11.2 (protokol dua-pass), §12 (link laporan r3) — ringkasan lengkap di Spec §8.5 "Resolusi sesi klarifikasi r3 (Spec v1.5)". Implementasi ke `plan/plan-feature-multi-weight-variants-v1.8.md` (versi 1.9) oleh `/sdlc-plan-tasks` **masih MENUNGGU** di sesi terpisah.*

- **Tanggal sesi:** 2026-08-01 (r3 — sesi klarifikasi ketiga untuk Implementation Plan; r1: `clarification-report-implementation-plan-multi-weight-variants-2026-07-31.md`, r2: `clarification-report-implementation-plan-multi-weight-variants-2026-07-31-r2.md`)
- **Persona:** Clarification Analyst (`/sdlc-clarify-reqs`)
- **Dokumen target interogasi:** `plan/plan-feature-multi-weight-variants-v1.8.md` (v1.8)
- **Referensi kontrak:** `spec/spec-multi-weight-variants.md` (v1.4), `docs/prd-20260731-1000-multi-weight-variants.md` (v1.4), `docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-07-31-r2.md`, `docs/audit/consistency-audit-plan-vs-prd-spec-2026-08-01.md`, `CONTEXT.md`
- **Verifikasi codebase:** `Scripts/custom_build_driver.py` (parser argumen ketat, baris 93–113), `Scripts/configure.py` (`FORM_KEY_TO_OPTION`/`OPTION_TO_DRIVER_FLAG`, baris 42–62), `Scripts/packaging.sh` (hinting terkondisi `UseHinted`, baris 70–89), `Dockerfile` (paket Stage 1 & RUN chain existing, tanpa `SHELL` directive), `.github/workflows/custom-build.yml` (4 input existing, forwarding `--build-arg BUILD_ARGS`), `tests/` (`conftest.py`, `test_configure.py` impor jsonschema), `.gitignore`, jumlah glyph per master (Regular 1042, Bold 1040, Italic 1046, BoldItalic 1041, FantasqueSans 231).

## 1. 🚨 Resolved Critical Ambiguities (Blockers)

- **Requirement:** "Kontrak RUN chain Spec §4.9 meneruskan `$BUILD_ARGS` verbatim ke `custom_build_driver.py "$FONTS" /build $BUILD_ARGS`; `configure.py` akan memasukkan `--multi-weight` ke `BUILD_ARGS` (pola `OPTION_TO_DRIVER_FLAG`)" (ID: Spec §4.9; Plan TASK-4.1/4.2)
  - **Resolution (K1 → Opsi A):** Mekanisme satu-kanal flag dipertahankan (`--multi-weight` tetap hidup di `BUILD_ARGS`). RUN chain TASK-4.2 diperbaiki: (i) menambah `SHELL ["/bin/bash", "-c"]` pada Stage 1 ATAU mengganti bashism `<<<` dengan bentuk portabel `echo "$BUILD_ARGS" | grep -q -- "--multi-weight"`; (ii) men-strip `--multi-weight` sebelum pemanggilan driver, mis. `DRIVER_ARGS=$(printf '%s' "$BUILD_ARGS" | sed 's/--multi-weight//g')` → `custom_build_driver.py "$FONTS" /build $DRIVER_ARGS`. Verifikasi codebase: `parse_args()` melakukan `_die("unknown flag(s): ...")` untuk flag di luar `--line-height/--no-loop-k/--no-calt`; Dockerfile tanpa `SHELL` directive → `/bin/sh` (dash) tidak mendukung here-string `<<<`. CON-001 tidak tersentuh. Spec §4.9 diamendemen (baris akhir RUN chain + bentuk grep portabel).
  - **Catatan:** Keputusan ini menyelesaikan potensi *build-breaker* ganda: (1) flag tak dikenal → exit non-zero; (2) bashism → syntax error.

- **Requirement:** "`RUN pytest tests/ -v` dijalankan di dalam RUN chain multi-weight Stage 1 (Spec §4.9, Plan TASK-4.2)" (ID: Spec §4.9; Plan TASK-4.2)
  - **Resolution (K2 → Opsi A):** pytest + jsonschema diinstal **tidak kondisional** di Stage 1 — perpanjang baris `pip3 install --break-system-packages --no-cache-dir future` menjadi `... future pytest jsonschema` (pola existing, satu layer; image single-weight tidak terpengaruh pada output font — AC-B03 tetap berlaku). Verifikasi codebase: paket Stage 1 aktual hanya `ca-certificates, fontforge, python3-pip, make` + pip `future`; `tests/test_configure.py` mengimpor `jsonschema` dan `pytest`. Spec §9.2 SVC-005 diperluas menjadi daftar pip packages (future, pytest, jsonschema); item *Ask First* Spec §7 ("Memodifikasi Dockerfile untuk menambah/mengganti package sistem") ditandai **disetujui** pada sesi ini untuk perubahan ini saja.

- **Requirement:** "TASK-2.X/AC-H02: `pass_rate ≥ 98%` sebagai gate Phase 2 vs RUN chain build `validate_harmonization.py --strict` (satu `fail` → exit non-zero) dan Spec §7 *Never Do*: seluruh glyph `fail` HARUS diperbaiki sebelum interpolasi" (ID: Plan TASK-2.X/2.Y/3.1; Spec AC-H02, §4.9, §7)
  - **Resolution (K3 → Opsi A):** Gate **dua-tingkat**: `pass_rate ≥ 98%` = *checkpoint kemajuan* (melanjutkan review/iterasi), `fail_count = 0` (100%) = **syarat masuk Phase 3** (interpolasi). Tidak ada task baru — pengerjaan sisa ≤2% adalah kelanjutan alami TASK-2.1/2.2. AC-H02 tetap bermakna sebagai metrik checkpoint (SM-T1). Konsisten dengan *Never Do*, GUD-002, dan `--strict` di RUN chain. Plan TASK-2.X/2.Y diamendemen dengan formulasi gate dua-tingkat.

## 2. 🧩 Addressed Edge Cases & Unhandled Scenarios

- **Scenario:** Gate PoC (TASK-1.X) dievaluasi dengan laporan `validate_interpolation.py` yang dihitung dengan threshold 15.0° awal, sementara kalibrasi threshold terjadi "inheren" saat visual diff review (TASK-1.3) — perubahan threshold mengubah jumlah `warning` sehingga mengubah `pass_rate` (ID: Plan TASK-1.3/1.X; Spec REQ-H06/§4.11)
  - **Handling Strategy (K7 → Opsi A):** Protokol **dua-pass**: (1) jalankan `validate_interpolation.py` dengan threshold awal 15.0° → laporan R1; (2) visual diff review (FR-2.3) mengkalibrasi threshold → nilai final `T_final` dicatat di `docs/audit/phase0-experiments-{date}.md` + `visual-quality-rubric.md`; (3) jalankan ulang script dengan `T_final` → laporan R2; (4) gate TASK-1.X dievaluasi pada **R2**. Script `validate_interpolation.py` (TASK-0.3) diberi parameter eksplisit `--threshold DEG` (default 15.0), dipisahkan dari rubric markdown (rubric mendokumentasikan nilai final, bukan sumber parsing script). Guard: perubahan threshold wajib didasari temuan visual dan didokumentasikan — tidak boleh disetel hanya agar gate lolos.

- **Scenario:** Deteksi distorsi berat (GUD-002) tidak ter-enforce pada build-time: RUN chain (Spec §4.9) tidak memanggil `validate_interpolation.py`; kontrak driver §4.6 "Exit code non-zero pada kegagalan kritis" berisiko menduplikasi logika deteksi (ID: Spec GUD-002, §4.6, §4.9; Plan TASK-0.3/0.7/4.2)
  - **Handling Strategy (K8 → Opsi A):** RUN chain diperluas: setelah `multi_weight_driver.py` dan sebelum `custom_build_driver.py`, tambahkan loop fail-fast `validate_interpolation.py --threshold T --fail-fast` untuk setiap core weight interpolated (Medium, SemiBold) — status `fail` (self-intersection / counter tertutup / kontur rusak) → exit non-zero (GUD-002 ter-enforce di CI); `warning` ≤2% tidak memblokir build (metrik QA Phase 3). Kontrak driver §4.6 diamendemen: driver cukup mempropagasi error FontForge; gating distorsi berat menjadi tanggung jawab `validate_interpolation.py` (satu sumber deteksi, tanpa duplikasi). Untuk jalur release upstream, runbook TASK-5.4 menyertakan langkah validasi yang sama (lihat K14).

- **Scenario:** Eksekusi `pytest` Phase 0 (TASK-0.X) di host runner tanpa FontForge: hanya `test_multi_weight_driver.py` yang memakai `pytest.importorskip("fontforge")`; dua/empat file test lain tidak disebutkan; script validasi (detect/validate) butuh FontForge untuk membaca fixture `.sfdir` (ID: Plan TASK-0.X; Spec §6.1/§6.3)
  - **Handling Strategy (K6 → Opsi A):** (1) **Seluruh** file test baru yang menyentuh FontForge (`test_detect_incompatibility.py`, `test_validate_harmonization.py`, `test_validate_interpolation.py`, `test_multi_weight_driver.py`) memakai `pytest.importorskip("fontforge")` di level modul agar gate pytest host tidak crash; (2) eksekusi nyata Phase 0 dilakukan di dalam image `builder-fontforge` via `docker run` ad-hoc dengan pip install sementara (`pip3 install --break-system-packages pytest jsonschema` + bind-mount repo), sebelum TASK-4.2 membakukan instalasi di Dockerfile resmi; (3) TASK-0.X diamendemen: "jalankan di container Stage 1 (FontForge nyata), bukan host runner".

- **Scenario:** Fixture terkunci (TASK-0.10/Spec §6.5) tidak memuat `FantasqueSans.sfdir` maupun master Italic/BoldItalic, sementara test case #9/#10 (assembly naming + includes FantasqueSans) dan kontrak assembly driver (7–9 `.sfdir`, REQ-B06) membutuhkan struktur lengkap (ID: Plan TASK-0.10; Spec §6.3 test #9/#10, §6.5, REQ-B06)
  - **Handling Strategy (K12 → Opsi A):** Fixture terkunci tetap menjadi kanon minimal (2 master + edge-case glyphs + `font.props`); test #9/#10 membangun pohon sintetis lengkap **di direktori temp**: menyalin fixture ke `Harmonized/{Regular,Bold}`, menambah stub `Harmonized/{Italic,BoldItalic}` (salinan minimal master) dan stub `FantasqueSans.sfdir` (minimal) — helper test, bukan fixture yang di-commit. Konten fixture yang di-commit tidak berubah.

## 3. 🔍 Validated Implicit Assumptions

- **Assumption (K4):** Pembagian kerja 70/25/5 (TASK-2.1/2.2/2.3) adalah batas cakupan harmonisasi per designer — bertentangan dengan AC-H02 ("kedua pasangan ≥98%") dan PRD §8.3 (~1.042 × 2 pasangan).
  - **Validation (Opsi A):** **DITOLAK sebagai batas cakupan.** Setiap designer mengharmonisasi **100% pasangan yang ditugaskan** (Designer A: Regular↔Bold; Designer B: Italic↔BoldItalic); 70/25/5 adalah label informal porsi beban/prioritas. AC-H02 tetap berlaku untuk kedua pasangan. RUN chain build ditambah `validate_harmonization.py --strict` untuk pasangan Italic↔BoldItalic (hasil harmonisasinya ikut di-assembly ke `build/sources/`). Plan TASK-2.1/2.2/2.3 dan TASK-4.2 diamendemen; Spec §4.9 diamendemen (validasi kedua pasangan) + §4.3 catatan sumber Italic/BoldItalic dari harmonized masters yang lolos validasi.

- **Assumption (K5):** Seluruh kontrak unit test Spec §6.3 tercakup di Plan.
  - **Validation:** **SALAH — kesenjangan.** Spec §6.3 mendefinisikan `tests/test_validate_interpolation.py` (5 test case: pass, warning, fail, overlay PNG, JSON valid), tetapi Plan tidak memiliki TASK maupun FILE untuknya (FILE-014/015/016; TEST-003 hanya 3 file). **Resolusi:** tambah TASK-0.13 (Dep: TASK-0.3; Files: 1) + FILE-023 `tests/test_validate_interpolation.py` [NEW] + TEST-003 diperluas (4 file test) + catatan `importorskip` (K6).

- **Assumption (K9):** Override REQ-I04 ("weight baru WAJIB di-hint terlepas `UseHinted`") terimplementasi tanpa task eksplisit.
  - **Validation:** **SALAH — gap implementasi.** `packaging.sh` aktual hanya menjalankan ttfautohint saat `UseHinted=true` (dibaca dari manifest via jq). **Resolusi (Opsi A):** TASK-4.4 diperluas: packaging mengenali file weight baru (Medium, SemiBold; + Light/ExtraBold di mode release) dan menghintnya **selalu**, terlepas `UseHinted`; weight existing (Regular, Bold, Italic, BoldItalic, FantasqueSans) tetap mengikuti `UseHinted`. TEST-006 tetap sebagai verifikasi.

- **Assumption (K10):** Komposisi "6 weight" pada AC-D03/SM-T4 ("WOFF2 ≤ 500 KB") sudah jelas.
  - **Validation:** **SALAH — ambigu.** REQ-D03 menyatakan archive WOFF2 berisi "4–6 weight + varian Italic"; §4.10 `WEIGHTS_RELEASE` bahkan mencantumkan FantasqueSans; AC-D02 menyebut descriptor 300–800 (6 nilai = 4 core + 2 stretch). **Resolusi (Opsi A):** Definisi eksplisit — budget 500 KB dihitung atas **6 weight baru** pada set release: Regular, Medium, SemiBold, Bold + Light, ExtraBold (jika diproduksi). Italic, BoldItalic, dan FantasqueSans **tidak** dihitung (weight existing yang sudah dirilis). Jika stretch gagal review, jumlah file otomatis berkurang (budget melonggar — tetap kap). Spec AC-D03/§4.10 diamendemen dengan definisi ini; catatan interpretasi SM-T4 di PRD (opsional).

- **Assumption (K11):** Output `poc_interpolation.py` (TASK-1.2) kompatibel dengan `generate_specimen.py` (TASK-1.3) yang membaca file TTF.
  - **Validation:** **SALAH — format tidak ditentukan.** **Resolusi (Opsi A):** `poc_interpolation.py` (TASK-0.6) menghasilkan **dua output**: `.sfdir` interpolated subset DAN TTF untuk rendering (via `font.generate`, tanpa hinting — konsisten "TANPA ttfautohint"); TASK-1.3 memakai TTF tersebut untuk specimen HTML & visual diff review (FR-2.3 butuh font yang dapat dirender pada 8/12/16/24 pt).

- **Assumption (K13):} "Sampel pass" pada gate manusia PoC (TASK-1.X) cukup representatif tanpa ukuran didefinisikan.
  - **Validation:** **DITOLAK — dapat dimanipulasi.** **Resolusi (Opsi A):** Review manusia mencakup **100% glyph PoC** (~40–50 glyph; biaya trivial) — selaras AC-P03 ("≥90% glyph hasil interpolasi PoC dinilai"); gate: ≥90% dari seluruh glyph yang direview mempertahankan nuansa handwritten + `fail_count = 0` (script). TASK-1.X diamendemen (hapus kata "sampel pass").

- **Assumption (K14):** Urutan eksekusi release upstream dan pemicu `RELEASE_MODE` cukup jelas dari definisi kontrak.
  - **Validation:** **SALAH — runbook tidak lengkap.** **Resolusi (Opsi A):** TASK-5.4 dilengkapi runbook checklist 9 langkah: (1) tetapkan factor stretch (Designer A + maintainer) → `stretch-factor-decision-{date}.md`; (2) `multi_weight_driver.py --sources Sources --output Sources/Harmonized/Interpolated --enable-light --enable-extrabold --light-factor F --extrabold-factor F` (lokal/docker run image Stage 1); (3) `validate_interpolation.py` fail-fast untuk Light & ExtraBold; (4) visual review per stretch (rubric + specimen) → verdict di `tracking.json`; (5) `custom_build_driver.py build/sources`; (6) Stage 2: ttfautohint (override REQ-I04) + WOFF/WOFF2; (7) `packaging.sh` dengan `RELEASE_MODE=1` → 3 archive `FantasqueSansMono-{version}-{TTF|OTF|WOFF2}.zip`; (8) `gh release create` + attach; (9) update README/Specimen. **Trigger:** env var eksplisit `RELEASE_MODE=1` diinvoke maintainer; CI Custom Build tidak pernah menyetelnya (E10). TASK-4.4 & Spec §4.10 diamendemen (definisi RELEASE_MODE).

- **Assumption (K15):** Direktori runtime kontrak "tidak di-commit" terlindungi oleh `.gitignore`.
  - **Validation:** **SALAH — celah.** `.gitignore` aktual tidak memuat `build/` maupun `Sources/Harmonized/Interpolated/`. **Resolusi (Opsi A):** TASK-0.0 atau TASK-0.7 menambahkan kedua entri ke `.gitignore` (selaras §4.2/§4.9).

- **Assumption (K16):** Jumlah `.sfdir` hasil assembly konsisten di seluruh dokumen.
  - **Validation:** **SALAH — inkonsistensi numerik.** VAL-017 menyebut "6–8 `.sfdir`"; §4.7/REQ-B06 menyebut "7–9". **Resolusi:** VAL-017 diamendemen: assembly memuat **7 `.sfdir`** pada mode Custom Build (4 harmonized masters + Medium + SemiBold + `FantasqueSans.sfdir`) dan **9 `.sfdir`** pada release upstream dengan stretch (8 weight + FantasqueSans); diselaraskan dengan §4.7 (7–9).

## 4. 📝 Next Steps

- **Implementation Plan** (`plan/plan-feature-multi-weight-variants-v1.8.md` → v1.9) **HARUS** diperbarui oleh `/sdlc-plan-tasks` di sesi terpisah:
  - TASK-2.1/2.2/2.3: klarifikasi 70/25/5 sebagai label porsi beban (bukan batas cakupan) — K4.
  - TASK-2.X/2.Y: gate dua-tingkat harmonisasi (≥98% checkpoint; `fail_count = 0` syarat Phase 3) — K3.
  - TASK-0.3: parameter `--threshold` pada `validate_interpolation.py` — K7.
  - TASK-0.6: `poc_interpolation.py` menghasilkan `.sfdir` + TTF (tanpa hinting) — K11.
  - TASK-0.7: `.gitignore` + `build/` & `Sources/Harmonized/Interpolated/`; kontrak driver §4.6 (propagasi error, gating via validate) — K15/K8.
  - TASK-0.10: mekanisme test assembly (pohon sintetis temp + stub) — K12.
  - TASK-0.13 (BARU): `tests/test_validate_interpolation.py` (5 test case Spec §6.3) + FILE-023 — K5.
  - TASK-0.X: eksekusi pytest Phase 0 di container Stage 1 (FontForge nyata); `importorskip` di keempat file test — K6.
  - TASK-1.3/1.X: protokol dua-pass kalibrasi threshold; gate pada laporan threshold final; review manusia 100% glyph PoC — K7/K13.
  - TASK-4.2: RUN chain final (SHELL bash / grep portabel + strip `--multi-weight` via `DRIVER_ARGS`; validasi `--strict` kedua pasangan master; `validate_interpolation.py --fail-fast` per core weight; instalasi pytest/jsonschema Stage 1) — K1/K2/K3/K4/K8.
  - TASK-4.4: override hinting REQ-I04 untuk weight baru (terlepas `UseHinted`) + definisi `RELEASE_MODE` — K9/K14.
  - TASK-5.4: runbook release upstream 9 langkah — K14.
  - TEST-003: diperluas ke 4 file test — K5.
  - Changelog v1.9 + `clarification_reference` rujuk laporan r3 ini.

- **Technical Specification** (`spec/spec-multi-weight-variants.md` → v1.5) **HARUS** diamendemen:
  - §4.9: koreksi RUN chain (grep portabel tanpa `<<<`, stripping `--multi-weight` → `$DRIVER_ARGS`, validasi harmonisasi kedua pasangan, loop `validate_interpolation.py --fail-fast` per core weight, instalasi pytest/jsonschema Stage 1).
  - §4.6: kontrak driver — gating distorsi berat via `validate_interpolation.py` (bukan deteksi internal driver); output TTF `poc_interpolation.py`.
  - §4.10: definisi `RELEASE_MODE`; AC-D03/§4.10 definisi komposisi "6 weight" budget WOFF2 (K10).
  - §6.3: catatan `importorskip` untuk seluruh file test FontForge-dependent; kontrak `--threshold`.
  - §6.5: mekanisme test assembly (pohon sintetis temp).
  - §7: item *Ask First* "Dockerfile package" ditandai disetujui (pytest, jsonschema) untuk konteks r3.
  - §9.2: SVC-005 diperluas (future, pytest, jsonschema).
  - §11.1 VAL-017: koreksi jumlah `.sfdir` (7 Custom Build / 9 release upstream) — K16.
  - AC-H02/§5.1: catatan gate dua-tingkat (98% checkpoint / 100% pra-interpolasi).
  - REQ-H06/§4.11: parameter `--threshold` + protokol dua-pass kalibrasi.
  - REQ-I04: mekanisme override UseHinted di packaging (weight baru selalu di-hint).

- **PRD** (`docs/prd-20260731-1000-multi-weight-variants.md`): tidak ada amendemen wajib; catatan interpretasi SM-T4 (komposisi 6 weight budget WOFF2) bersifat opsional (K10).

- **Domain Glossary (CONTEXT.md):** Tidak ada istilah kanonis baru yang disepakati pada sesi ini — "Release Upstream Pipeline" sudah terdefinisi; `RELEASE_MODE` adalah variabel teknis, bukan istilah domain. Tidak ada pembaruan glossary.

- **ADR:** Tidak ada keputusan yang memenuhi triple-gate (hard to reverse / surprising / real trade-off) — seluruh resolusi bersifat mudah dibalik dan masuk kategori *spec-level resolutions* (Spec §8.5). Tidak ada ADR baru yang dibuat.
