<!-- markdownlint-disable -->

# Clarification Report: Implementation Plan for Multi-Weight Variants (Spec v1.6 + Plan v1.10 → r5)

- **Tanggal sesi:** 2026-08-01 (r5 — sesi klarifikasi kelima untuk Implementation Plan; r1: `clarification-report-implementation-plan-multi-weight-variants-2026-07-31.md`, r2: `...-2026-07-31-r2.md`, r3: `...-2026-08-01-r3.md`, r4: `...-2026-08-01-r4.md`)
- **Persona:** Clarification Analyst (`/sdlc-clarify-reqs`)
- **Dokumen target interogasi:** `spec/spec-multi-weight-variants.md` (v1.6) dan `plan/plan-feature-multi-weight-variants-v1.10.md` (v1.10)
- **Referensi kontrak:** `docs/prd-20260731-1000-multi-weight-variants.md` (v1.4), `docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r4.md`, `docs/audit/consistency-audit-plan-vs-prd-spec-2026-08-01.md`, `CONTEXT.md`
- **Keputusan user:** B1 dijawab eksplisit oleh user (**Opsi A**); B2–B3, E1–E8, H1–H6, dan MO dijawab berdasarkan rekomendasi Clarification Analyst (delegasi user: "jawab semua pertanyaan berdasarkan jawaban rekomendasi kamu", 2026-08-01).
- **Verifikasi codebase:** `Dockerfile` (Stage 1 apt: `ca-certificates, fontforge, python3-pip, make`; tanpa `python3-fontforge`; komentar "bindings embedded"; pip line `future`; tanpa `SHELL` directive), `Scripts/packaging.sh` (pre-flight `manifest.json`; `USE_HINTED` via `jq`; zip-all `fantasque-sans-custom-build.zip`/`.tar.gz`; tanpa env var mode), `Scripts/custom_build_driver.py` (`_die("unknown flag(s): ...")`; `find_sfdirs()` scan `.sfdir` top-level; `"Generating {name}"`; `_update_features(fnt)` in-process di `build_one_weight()`), `Scripts/configure.py` (`DEFAULTS` 4 opsi; `FORM_KEY_TO_OPTION`; `OPTION_TO_DRIVER_FLAG` tanpa `UseHinted`; `resolved_options` = dict resolved; manifest tanpa version font), `config.schema.json` (4 properti boolean, `additionalProperties: true`), `.github/workflows/custom-build.yml` (tanpa `enable_multi_weight`; `timeout-minutes: 30`; packaging via `docker run` tanpa `-e`; sudah menjalankan `pytest tests/ -v` host), `.gitignore` (tanpa `build/` & `Sources/Harmonized/Interpolated/`), `tests/` (existing: `test_configure.py`, `conftest.py`, fixture configs).

## 1. 🚨 Resolved Critical Ambiguities (Blockers)

- **Requirement:** "`RUN pytest tests/ -v` dijalankan di dalam RUN chain multi-weight Stage 1 — eksekusi nyata unit test FontForge" (ID: Spec §4.9; Plan TASK-4.2, TASK-0.X, TASK-0.14; klarifikasi r3 K6; §6.3 catatan `importorskip`)
  - **Resolution (B1 → Opsi A — keputusan eksplisit user):** **Instal `python3-fontforge` di Stage 1.** Bukti: `Dockerfile` Stage 1 hanya menginstal `ca-certificates, fontforge, python3-pip, make` dengan komentar eksplisit bahwa bindings Python FontForge *embedded di binary* dan `python3-fontforge` TIDAK diperlukan → system `python3` (interpreter yang menjalankan `pytest`) **tidak dapat `import fontforge`** → keempat file test FontForge-dependent (`pytest.importorskip("fontforge")` di level modul) **selalu di-skip di container**, sehingga klaim K6 "eksekusi nyata dengan FontForge tetap terjadi di container Stage 1" tidak terpenuhi dan gate fail-fast pytest §4.9 hampa untuk logika multi-weight. Dengan `python3-fontforge` di apt Stage 1 (versi identik dari repo yang sama — tanpa risiko ABI), `pytest tests/ -v` di RUN chain mengeksekusi seluruh file test dengan FontForge nyata — tanpa wrapper, tanpa perubahan kontrak §4.9.
  - **Catatan sekuensial:** TASK-0.X (Phase 0) mendahului TASK-4.2 (Phase 4) — Dockerfile resmi belum dimodifikasi saat Phase 0. Perintah ad-hoc TASK-0.X WAJIB menambah instalasi `python3-fontforge` sendiri: `apt-get install -y --no-install-recommends python3-fontforge && pip3 install --break-system-packages --no-cache-dir pytest jsonschema pytest-cov`, plus pre-check `python3 -c "import fontforge"` sebelum `pytest` (bukti mekanisme; jika gagal → eskalasi).
  - **Catatan AC-B03:** penambahan paket apt tidak mengubah output font — mode single-weight (`FONTS=Sources`) tetap byte-identical (paket tidak dieksekusi pada jalur font); `pytest` hanya dijalankan dalam cabang `--multi-weight` (§4.9).
  - **Konsekuensi:** test case §6.3 yang sebelumnya selalu di-skip kini **menjadi gate build nyata** — seluruh kontrak yang diuji (termasuk E4: exit code `detect_incompatibility.py`) harus didefinisikan secara presisi sebelum Phase 4.

- **Requirement:** "Loop fail-fast `validate_interpolation.py --threshold T_final --fail-fast` di RUN chain" (ID: GUD-002 Plan §1) vs "loop `--threshold 15.0`" (ID: Spec §4.9 RUN chain snippet; Plan TASK-4.2) — protokol dua-pass kalibrasi (klarifikasi r3 K7)
  - **Resolution (B2 → Opsi A):** **`T_final` menjadi bagian eksplisit kontrak RUN chain.** Snippet §4.9 diubah: threshold loop menggunakan variabel shell `T_FINAL` yang didefinisikan di awal cabang multi-weight dengan komentar sumber: `# T_FINAL = nilai final protokol dua-pass (r3 K7) dari docs/audit/phase0-experiments-{date}.md + visual-quality-rubric.md`; TASK-4.2 (Phase 4, eksekusi SETELAH kalibrasi Phase 1) memuat instruksi eksplisit "hardcode nilai `T_final`, bukan default 15.0". Nilai `15.0` hanya berlaku sebagai default CLI (`--threshold` default) sebelum kalibrasi. Parameterisasi via ARG/env (Opsi B) ditolak — nilai berubah sekali, menambah permukaan kontrak (configure.py, manifest) tanpa manfaat.
  - **Catatan:** `--fail-fast` hanya bereaksi pada status `fail` (self-intersection/counter tertutup/kontur rusak); threshold hanya memengaruhi klasifikasi `warning` — sehingga kesalahan nilai threshold tidak menggagalkan CI, tetapi mendistorsi laporan QA (≤2% warning, TASK-3.X) dan evidence visual.

- **Requirement:** "TASK-3.2 Hasilkan Full Specimen Sheet (HTML) untuk seluruh core weight" — input `generate_specimen.py --weights DIR` adalah file TTF (§4.8), tetapi `multi_weight_driver.py` hanya menghasilkan `.sfdir` (kontrak §4.6) dan pipeline e2e (penghasil TTF) baru ada di Phase 4 (ID: Plan TASK-3.2; Spec §4.6/§4.8; REQ-S01)
  - **Resolution (B3 → Opsi A):** **TASK-3.2 menambah langkah eksekusi lokal driver existing atas hasil assembly TASK-3.1**: `fontforge --quiet -lang=py -script Scripts/custom_build_driver.py build/sources <tmp_output>` (tanpa flag variant — varian Normal) untuk menghasilkan TTF pra-hinting; direktori `<tmp_output>/TTF` menjadi input `--weights` untuk `generate_specimen.py`. CON-001 tidak tersentuh; `features.py` tetap dipanggil in-process oleh driver (konsisten dengan rendering final). Designer sudah memiliki FontForge lokal (prasyarat kerja harmonisasi manual). Spec §4.8 diberi catatan sumber TTF specimen Phase 3.

## 2. 🧩 Addressed Edge Cases & Unhandled Scenarios

- **Scenario:** `tracking.json` (satu file JSON, §4.12) di-update oleh dua type designer yang bekerja paralel di branch Git terisolasi (TASK-2.1/2.2/2.3) — konflik merge pada file yang sama dijamin terjadi, strategi resolusi tidak didefinisikan (ID: §4.12; Plan TASK-2.1/2.2/2.3)
  - **Handling Strategy (E1):** Aturan kolaborasi eksplisit: (1) masing-masing designer TIDAK memformat ulang atau merombak urutan array `glyphs` di luar glyph yang mereka kerjakan (minimalkan permukaan konflik); (2) konflik merge `tracking.json` diresolusi dengan **union + sort** (seluruh field dipertahankan; tidak ada field yang di-drop; urutan akhir di-sort berdasarkan nama glyph); (3) aturan dicatat di §4.12 dan TASK-2.1/2.2/2.3.

- **Scenario:** Runbook release langkah 3 menjalankan `validate_interpolation.py --threshold T_final --fail-fast` untuk Light & ExtraBold — jika satu stretch gagal, exit non-zero menghentikan runbook, bertentangan dengan GUD-004 "kegagalan stretch tidak menggagalkan seluruh build" (ID: Plan TASK-5.4 langkah 3; GUD-004; Spec §4.10 filter runtime)
  - **Handling Strategy (E2):** Validasi stretch dijalankan **per weight terpisah** (dua pemanggilan, bukan satu): exit non-zero pada satu stretch → verdict `fail` dicatat di `tracking.json` → weight dieksklusi dari daftar `WEIGHTS` → lanjut ke weight lain (partial success, GUD-004); filter runtime §4.10 (cek keberadaan file per weight) menjadi lapisan kedua. Jalur eksklusi ini ditulis eksplisit di runbook TASK-5.4.

- **Scenario:** Glyph `only_in_b` — copy-as-fallback menyalin glyph **dan advance width** dari Bold, sedangkan post-process hmtx menyalin dari Regular; konsistensi AC-I04 (advance width identik antar weight) bergantung asumsi monospace yang tidak dinyatakan (ID: REQ-I03; Spec §4.6; §10.1; AC-I04)
  - **Handling Strategy (E3):** Kontrak hmtx diperjelas: glyph yang ada di Regular → advance width dari Regular; glyph `only_in_b` → advance width dari Bold (master sumber fallback). Asumsi monospace (seluruh glyph berbagi advance width yang sama) dinyatakan eksplisit di REQ-I03 dan diverifikasi oleh E0.2/AC-I04; jika deviasi advance width antar master ditemukan → eskalasi via failure path E0.2, bukan koreksi diam-diam.

- **Scenario:** Test case 8 `test_empty_master` menuntut "Master kosong → exit code non-zero + pesan error", tetapi §4.4 `detect_incompatibility.py` tidak memiliki kontrak exit code — kini test tersebut benar-benar dieksekusi di CI (B1) dan dapat memblokir build tanpa dasar kontrak (ID: Spec §4.4 vs §6.3 test 8)
  - **Handling Strategy (E4):** §4.4 ditambah kontrak exit code: input tidak valid (direktori tidak ada/tidak terbaca/master tidak dapat dibuka/0 glyph) → exit non-zero + pesan error ke stderr; laporan berhasil dihasilkan (termasuk seluruh glyph `compatible`) → exit 0.

- **Scenario:** REQ-I03 menulis hmtx copy *kondisional* ("Jika interpolasi FontForge menghasilkan deviasi, script HARUS mem-post-process...") vs §4.6 *unconditional* ("Mem-post-process: menyalin tabel hmtx...") — hasil implementasi bisa berbeda antar implementer (ID: REQ-I03 vs §4.6)
  - **Handling Strategy (E5):** Disatukan ke **unconditional**: REQ-I03 diubah menghapus klausa kondisional — post-process hmtx dari Regular SELALU dilakukan (copy saat nilai identik adalah no-op semantik; deterministik GUD-001). §4.6 tidak berubah.

- **Scenario:** Kontrak CLI `--light-factor F` / `--extrabold-factor F` menyebut "default: ditetapkan Phase 5" — tidak implementable sebagai default kode; perilaku saat `--enable-light` tanpa factor tidak didefinisikan (ID: Spec §4.6 usage)
  - **Handling Strategy (E6):** Kontrak diubah: `--light-factor` WAJIB diberikan bersama `--enable-light` (dan `--extrabold-factor` bersama `--enable-extrabold`); tanpa nilai → exit non-zero + pesan instruktif ("factor stretch ditetapkan Phase 5 — lihat `docs/audit/stretch-factor-decision-{date}.md`"). Tidak ada default di kode.

- **Scenario:** REQ-I06 "glyph tersebut harus dikeluarkan dari output dan dikembalikan ke tahap harmonisasi" vs REQ-H04 "Tidak ada glyph yang hilang dari output" — interpretasi permanen melanggar AC-I05 (ID: REQ-I06 vs REQ-H04)
  - **Handling Strategy (E7):** Wording REQ-I06 diamendemen: "dikeluarkan dari output **SEMENTARA** (durasi iterasi fix loop FR-5.3) dan dikembalikan ke tahap harmonisasi"; dilarang hilang permanen dari output final (REQ-H04). Jika fix loop tidak menyelesaikan dalam batas iterasi → jalur keputusan FR-2.5 (revisi cakupan V1).

- **Scenario:** AC-B02 menyatakan "Regular/Bold dibangun dari harmonized masters (TIDAK byte-identical dengan V0)" — padahal Italic/BoldItalic di mode multi-weight juga dibangun dari harmonized masters (§4.3) sehingga juga tidak byte-identical (ID: AC-B02 vs §4.3)
  - **Handling Strategy (E8):** AC-B02 parenthetical diperluas: "(Regular, Bold, Italic, BoldItalic dibangun dari harmonized masters — tidak byte-identical dengan V0; `FantasqueSans` tetap salinan legacy — byte-identical)".

## 3. 🔍 Validated Implicit Assumptions

- **Assumption (H1):** `T_final` yang dikalibrasi pada subset PoC (~40–50 glyph, FR-2.1) berlaku generik untuk seluruh 1.042 glyph tanpa verifikasi generalisasi distribusi tangent-angle.
  - **Validation:** **DITERIMA DENGAN VERIFIKASI.** TASK-3.X menambah langkah: jalankan `validate_interpolation.py --threshold T_final` pada Medium full (laporan R-full) dan bandingkan distribusi warning vs PoC; jika warning rate > 2% atau muncul pola artifact yang tidak terwakili subset → kalibrasi ulang threshold (terdokumentasi — guard anti "disetel agar lolos", konsisten K7). Tidak menambah gate CI baru.

- **Assumption (H2):** Status "tidak di-commit" untuk `build/` dan `Sources/Harmonized/Interpolated/` (§4.2) ter-enforce — tetapi FILE-024 (`.gitignore` [MODIFY]) tidak memiliki owning task.
  - **Validation:** **DITOLAK (gap).** FILE-024 di-resolve ke **TASK-0.7** (Files 1 → 2: `Scripts/multi_weight_driver.py` + `.gitignore` — tambah `build/` & `Sources/Harmonized/Interpolated/`) — task yang memperkenalkan direktori runtime tersebut.

- **Assumption (H3):** "Sertakan laporan validasi JSON sebagai artifact build" (Spec §7 Always Do) terpenuhi — padahal laporan ditulis ke `build/` di dalam container (RUN chain §4.9) dan workflow hanya meng-upload `output/*.zip|*.tar.gz|manifest.json|LICENSE.txt|README.md`; laporan hilang setelah `docker build`.
  - **Validation:** **DITOLAK (gap).** Mekanisme surfacing tiga bagian: (a) Dockerfile TASK-4.2 — `mkdir -p build` di base Stage 1 (unconditional; tidak mengubah output font) + Stage 2 `COPY --from=builder-fontforge /build/build /app/build-reports`; (b) TASK-4.4 — `packaging.sh` menyalin `/app/build-reports/*.json` ke `output/reports/` jika ada (guard); (c) TASK-4.3 — upload path workflow ditambah `output/reports/**`.

- **Assumption (H4):** Push-gate `test-multi-weight.yml` (r4 R4) berfungsi sebagai gate pengembangan fitur — padahal keempat file test FontForge-dependent selalu di-skip di host runner; hanya `test_configure.py` existing yang benar-benar dieksekusi.
  - **Validation:** **Peran diklarifikasi.** Push-gate = **smoke gate** (sintaks/import + test non-FontForge), didokumentasikan demikian di TASK-0.14/§6.6; eksekusi nyata logika multi-weight = RUN chain Stage 1 (terpenuhi setelah B1) + e2e manual TASK-4.X. Tidak ada perubahan fungsional.

- **Assumption (H5):** `grep -q -- "--multi-weight"` (substring matching) dan `sed 's/--multi-weight//g'` (tanpa word boundary) aman terhadap flag lain.
  - **Validation:** **DITERIMA (non-issue terdokumentasi).** Vocabulary flag dikontrol tunggal oleh `configure.py` (`OPTION_TO_DRIVER_FLAG`) — tidak ada flag lain yang mengandung substring `--multi-weight`; catatan ditambahkan di §4.9. Tidak ada perubahan kode.

- **Assumption (H6):** Runbook release upstream TASK-5.4 (10 langkah) dapat dieksekusi — tanpa pemetaan stage per langkah (FontForge hanya di Stage 1; ttfautohint/woff/packaging hanya di Stage 2; configure.py/manifest di host runner).
  - **Validation:** **DITOLAK (gap).** Runbook di-annotasi stage per langkah: (1) keputusan factor — tidak butuh runtime; (2) driver + (3) validasi per stretch + (4) persiapan visual review — **Stage 1 image** (`docker run --rm -v <repo>:/build builder-fontforge ...`) atau lokal dengan FontForge; (5) generate `manifest.json` via `configure.py` — **host runner** (python 3.14, pola existing, argumen form identik build); (6) verifikasi metadata lapis 2 (`ttx`/`fc-scan`) — host; (7) packaging — **Stage 2 image** (`docker run --rm -e RELEASE_MODE=1 -e VERSION=${VERSION} -v <manifest>:/app/manifest.json -v <output>:/app/output fantasque-custom bash /app/Scripts/packaging.sh`).

## 4. 📝 Next Steps

- **Implementation Plan** (`plan/plan-feature-multi-weight-variants-v1.10.md` → v1.11) **HARUS** diperbarui oleh `/sdlc-plan-tasks` di sesi terpisah:
  - TASK-0.7: Files 1 → 2 (+ `.gitignore` — `build/` & `Sources/Harmonized/Interpolated/`) — H2.
  - TASK-0.X: perintah ad-hoc ditambah `apt-get install -y --no-install-recommends python3-fontforge` + pre-check `python3 -c "import fontforge"` sebelum pytest + `pytest-cov` — B1/MO-1.
  - TASK-3.2: langkah eksekusi lokal `custom_build_driver.py build/sources <tmp_output>` sebagai sumber TTF specimen pra-hinting — B3.
  - TASK-3.X: verifikasi generalisasi `T_final` (laporan R-full vs PoC; kalibrasi ulang bila perlu) — H1.
  - TASK-4.2: (i) apt Stage 1 + `python3-fontforge` + koreksi komentar Dockerfile "embedded bindings"; (ii) `mkdir -p build` di base Stage 1 + Stage 2 `COPY --from=builder-fontforge /build/build /app/build-reports`; (iii) threshold loop validasi = `T_FINAL` (dari `phase0-experiments-{date}.md` + rubric), bukan 15.0 — B1/B2/H3.
  - TASK-4.3: upload path tambah `output/reports/**` — H3.
  - TASK-4.4: `packaging.sh` — salin `/app/build-reports/*.json` ke `output/reports/` (guard) — H3.
  - TASK-5.4: runbook di-annotasi stage per langkah (Stage 1 / host / Stage 2); validasi stretch per weight terpisah + jalur eksklusi eksplisit (GUD-004) — E2/H6.
  - TASK-2.1/2.2/2.3: aturan kolaborasi `tracking.json` (no-reformat, union + sort saat konflik) — E1.
  - Changelog v1.11 + `clarification_reference` rujuk laporan r5 ini.

- **Technical Specification** (`spec/spec-multi-weight-variants.md` → v1.7) **HARUS** diamendemen:
  - §4.9: (i) catatan konteks eksekusi pytest — `python3-fontforge` di Stage 1 → keempat file test benar-benar dieksekusi di container (klaim K6 terpenuhi); (ii) snippet RUN chain — threshold loop `--threshold "${T_FINAL}"` + definisi `T_FINAL` dengan sumber; (iii) catatan H5 (vocabulary flag dikontrol configure.py) — B1/B2/H5.
  - §4.4: kontrak exit code `detect_incompatibility.py` (input tidak valid → non-zero + pesan; sukses → 0) — E4.
  - §4.6: kontrak `--light-factor`/`--extrabold-factor` = wajib bersama `--enable-*` (tanpa default; error instruktif) — E6.
  - §4.8: catatan sumber TTF specimen Phase 3 (output lokal driver existing atas `build/sources`, pra-hinting) — B3.
  - §4.12: aturan kolaborasi `tracking.json` (no-reformat; union + sort) — E1.
  - REQ-I03: hmtx copy unconditional + penanganan `only_in_b` (advance width dari Bold) + asumsi monospace eksplisit + eskalasi deviasi — E3/E5.
  - REQ-I06: "dikeluarkan dari output SEMENTARA" (durasi fix loop; dilarang hilang permanen) — E7.
  - AC-B02: parenthetical diperluas (Italic/BoldItalic juga non-byte-identical; FantasqueSans tetap legacy) — E8.
  - §7 Ask First: DISETUJUI untuk konteks r5 — penambahan `python3-fontforge` (apt Stage 1) dan `pytest-cov` (pip Stage 1); perubahan lain tetap Ask First — B1/MO-1.
  - §9.2 SVC-001: catatan `python3-fontforge`; SVC-005: + `pytest-cov` — B1/MO-1.
  - §6.7: mekanisme ukur coverage (pytest-cov di eksekusi container Stage 1; host gate tidak mengukur) — MO-1.

- **PRD** (`docs/prd-20260731-1000-multi-weight-variants.md`): tidak ada amendemen wajib — seluruh resolusi r5 bersifat teknis (execution/CI-level), tidak mengubah kebutuhan produk.

- **Domain Glossary (CONTEXT.md):** Tidak ada istilah kanonis baru yang disepakati pada sesi ini — `python3-fontforge`, `T_FINAL`, dan `pytest-cov` adalah entitas teknis, bukan istilah domain. Tidak ada pembaruan glossary.

- **ADR:** Tidak ada keputusan yang memenuhi triple-gate (hard to reverse / surprising / real trade-off) — seluruh resolusi (B1–B3, E1–E8, H1–H6) bersifat mudah dibalik (penambahan paket/instruksi/dokumentasi) dan masuk kategori *spec-level resolutions* (Spec §8.5). Tidak ada ADR baru yang dibuat.

- **Minor Observations (MO) untuk plan implementer:**
  - MO-1: §6.7 menuntut coverage ≥ 90% tanpa tool ukur — `pytest-cov` ditambahkan ke pip line Stage 1 (perluasan persetujuan K2 untuk konteks r5; host gate tetap tanpa ukuran coverage).
  - MO-2: `custom-build.yml` existing sudah menjalankan `pytest tests/ -v` di host (Phase 1 gate Custom Build) — push-gate baru (TASK-0.14) tumpang tindih fungsional untuk `test_configure.py`; diterima (biaya rendah, trigger berbeda: push vs workflow_dispatch) — peran smoke gate tetap seperti H4.
  - MO-3: `--threshold` di RUN chain bernilai `15.0` pada §4.9 v1.6 sedangkan GUD-002 Plan menyebut `T_final` — diselesaikan oleh B2; verifikasi lintas dokumen dilakukan pada re-audit.
