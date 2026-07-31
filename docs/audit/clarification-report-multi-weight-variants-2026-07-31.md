# Clarification Report: Multi-Weight Font Variants for Fantasque Sans Mono

**Date**: 2026-07-31
**PRD under review**: [`docs/prd-20260731-1000-multi-weight-variants.md`](../prd-20260731-1000-multi-weight-variants.md) (v1.1)
**Discovery Draft**: [`docs/discovery-draft-20260730-2110-multi-weight-variants.md`](../discovery-draft-20260730-2110-multi-weight-variants.md)
**Facilitator**: Clarification Analyst persona (`/sdlc-clarify-reqs`)
**Session language**: Indonesian (per `AGENTS.md` Communication policy)

---
<!-- markdownlint-disable  -->
## 0. ✅ Status Update — Applied to PRD v1.2 (2026-07-31)

**Verification date**: 2026-07-31
**PRD version verified**: v1.2
**Verifier**: Clarification Analyst persona (`/sdlc-clarify-reqs`)
**Summary**: 28 of 29 items applied (12/12 Resolutions, 9/10 Edge Cases, 7/7 Assumptions). 1 Edge Case (E7) applied partially — see follow-up note at the end of this section.

### Resolutions (§1) — All Applied ✅

| #   | Title                                                        | PRD Reference      |
| --- | ------------------------------------------------------------ | ------------------ |
| 1   | Target weight count (4 core + 2 stretch)                     | §1.2               |
| 2   | Selisih glyph antar master (copy as fallback)                | FR-1.1             |
| 3   | Definisi operasional "wibbly-wobbly" (Visual Quality Rubrik) | FR-2.4             |
| 4   | PoC subset diperluas (~40–50 glyph multi-kontur)             | FR-2.1             |
| 5   | Harmonisasi Italic + BoldItalic di V1                        | FR-1.1, §3.3, §9.1 |
| 6   | Invariant harmonisasi dua-tier (Hard + Soft)                 | FR-1.5             |
| 7   | Timeline 2 type designer part-time                           | §9.1, §3.3         |
| 8   | Kompatibilitas mundur output Regular/Bold (level pipeline)   | FR-7.2             |
| 9   | Build duration SM-T3 direvisi (≤ 240 menit)                  | SM-T3, FR-7.3      |
| 10  | Faux italic per platform + README section                    | §5.3               |
| 11  | CON-001 FEA wrapper (6× calls)                               | §8.1               |
| 12  | Cross-master harmonization 2 pasangan                        | FR-1.1             |

### Edge Cases (§2) — 9 Applied ✅, 1 Partial ⚠️

| #   | Title                                                 | Status    | PRD Reference                                                         |
| --- | ----------------------------------------------------- | --------- | --------------------------------------------------------------------- |
| E1  | Selisih glyph Regular↔Bold (-2)                       | ✅         | FR-1.1                                                                |
| E2  | 4 glyph italic-only di Italic.sfdir                   | ✅         | FR-1.1                                                                |
| E3  | 1 glyph bold-italic-only di BoldItalic.sfdir          | ✅         | FR-1.1                                                                |
| E4  | Ekstrapolasi Light/ExtraBold gagal visual review      | ✅         | §1.2, FR-4.1                                                          |
| E5  | Faux italic di platform berbeda                       | ✅         | §5.3                                                                  |
| E6  | Rendering di luar 8–24 pt (24–72 pt)                  | ✅         | FR-1.5                                                                |
| E7  | Konflik harmonisasi antar 2 type designer             | ⚠️ Partial | §3.3, §9.1 (tidak ada *explicit escalation* ke *upstream maintainer*) |
| E8  | Build duration > 135 menit (SM-T3)                    | ✅         | SM-T3, FR-7.3                                                         |
| E9  | User update V0 → V1 melihat *pixel rendering* berbeda | ✅         | FR-7.2                                                                |
| E10 | Fork owner memicu Custom Build tanpa *stretch weight* | ✅         | §3.3 (Fork Owner role), GH-004 acceptance                             |

### Assumptions (§3) — All Validated ✅

| #   | Title                                                          | PRD Reference               |
| --- | -------------------------------------------------------------- | --------------------------- |
| A1  | `features.py` deterministik & idempotent                       | §8.1, §9.1 (E0.1)           |
| A2  | FontForge interpolation tidak mengubah *advance width*         | §9.1 (E0.2)                 |
| A3  | TTF rebuild dari kontur harmonisasi memiliki *hinting* berbeda | FR-7.2                      |
| A4  | 2 *type designer* part-time parallel                           | §9.1 (E0.3)                 |
| A5  | 5 *glyph* italic-only tidak diperlukan di Regular/Bold         | FR-1.1 (*copy as fallback*) |
| A6  | `scripts/multi_weight_driver.py` tidak SPOF                    | §8.1, FR-7.1                |
| A7  | `sources/Harmonized/` direktori size                           | §8.2                        |

### ⚠️ Follow-up: Edge Case E7 (Escalation Path)

The clarification report's E7 stated: "Jika terjadi konflik pada glyph yang sama, escalation ke upstream maintainer." The PRD §3.3 and §9.1 describe the static division and "merge gate by Designer A" but **do not explicitly mention escalation to the upstream maintainer for deadlocks**. Designer A is a type designer lead, distinct from the upstream maintainer role per §3.3.

**Recommendation**: add one sentence to PRD §9.1 explicitly stating: "If a deadlock occurs in the shared pool, escalate to the upstream maintainer for resolution." This is a minor addition that does not change the architecture or scope.

---


## 1. 🚨 Resolved Critical Ambiguities (Blockers)

### ✅ Resolution #1 — Target weight count (4 core + 2 stretch)

- **Requirement:** "Inisiatif ini bertujuan untuk memperluas jajaran varian weight Fantasque Sans Mono menjadi **enam weight statis** — Light (300), Regular (400), Medium (500), SemiBold (600), Bold (700), dan ExtraBold (800)" (PRD §1.2, FR-4.1)
  - **Resolution:** V1 memiliki **2 tier kesuksesan** eksplisit:
    - *Full success* (wajib): 4 *core weight* — Regular 400, Medium 500, SemiBold 600, Bold 700.
    - *Partial success* (stretch, opsional): Light 300 + ExtraBold 800 — dirilis hanya jika ekstrapolasi FontForge lolos *visual review* (FR-5). Jika gagal, ditunda ke V2 dengan pendekatan *additional master drawing* (mitigasi risiko §8.3).

### ✅ Resolution #2 — Selisih glyph antar master (copy as fallback)

- **Requirement:** "Glyph pada master Regular dan Bold HARUS diselaraskan (harmonized) sehingga setiap glyph memiliki jumlah node yang identik, urutan kontur yang sama, dan arah kurva (clockwise/counter-clockwise) yang konsisten antara kedua master" (FR-1.1) — diasumsikan kedua *master* memiliki *glyph* *set* identik.
  - **Resolution:** Faktanya jumlah *glyph* **tidak identik** (lihat §2 Edge Cases). Untuk *glyph* tanpa pasangan, **disalin langsung** (*copy as fallback*) dari *master* yang memiliki *glyph* tersebut ke *output weight* baru tanpa interpolasi. Tidak ada *glyph* yang hilang dari *output*.

### ✅ Resolution #3 — Definisi operasional "wibbly-wobbly handwriting feel"

- **Requirement:** "PoC dinyatakan **LULUS** jika ≥ 90% glyph hasil interpolasi dinilai 'mempertahankan nuansa handwritten' oleh type designer, dan tidak ada glyph yang mengalami distorsi berat" (FR-2.4)
  - **Resolution:** Dibuat **Visual Quality Rubrik** di Phase 0 — dokumen berisi:
    - 5–10 *glyph* referensi dari Regular existing sebagai *gold standard* "wibbly-wobbly".
    - 5 contoh distorsi yang **tidak** dapat diterima (counter tertutup, kurva terlalu kaku, *self-intersection*).
    - *Checklist* terstruktur per *glyph*: (1) *counter shape preserved*? (2) *Bézier asymmetry maintained*? (3) *terminal style consistent*?
  - Rubrik menjadi acuan bagi *type designer* dan penerusnya, memungkinkan validasi lebih konsisten antar sesi *review*.

### ✅ Resolution #4 — PoC subset diperluas dengan glyph multi-kontur

- **Requirement:** "PoC mencakup subset 20–30 glyph prioritas tinggi: huruf kecil a-z (26 glyph), ditambah glyph kritis seperti space, period, comma, dan zero" (FR-2.1)
  - **Resolution:** Subset PoC diperluas menjadi **~40–50 *glyph*** dengan menambahkan *glyph* multi-kontur & bermasalah:
    - `g` (eksplisit — Discovery Draft §3 menunjukkan *node count mismatch* 21 vs 22 di kontur ke-3).
    - `@`, `&`, `Q`, `?`, `!` — *glyph* multi-kontur yang rawan distorsi.
    - `ß`, `fi`, `fl` — *glyph* dengan *counter* kompleks.
    - 3–5 *glyph* tambahan dari output *script* deteksi inkompatibilitas (*worst offenders*).
  - Harmonisasi manual dilakukan sekali per *glyph* (tidak per bobot), sehingga effort tambahan minimal.

### ✅ Resolution #5 — Harmonisasi Italic + BoldItalic di V1

- **Requirement:** "Varian italic saat ini hanya tersedia untuk Regular dan Bold. Pada V1, italic untuk weight baru TIDAK dihasilkan" (§5.3) — ambigu apakah Italic/BoldItalic *master* juga harus diharmonisasi.
  - **Resolution:** **YA** — *master* Italic dan BoldItalic diharmonisasi mengikuti FR-1.1–FR-1.5 yang sama. Disimpan di `sources/Harmonized/Italic/` dan `sources/Harmonized/BoldItalic/`. Tidak digunakan di V1 (karena *italic* untuk *weight* baru = *faux italic*), tapi fondasi siap untuk V2 tanpa *rework*. Estimasi tambahan: **+30%** *effort* harmonisasi (total 140–240 jam *type designer*).

### ✅ Resolution #6 — Invariant harmonisasi dua-tier (Hard + Soft)

- **Requirement:** "Harmonisasi TIDAK BOLEH mengubah tampilan visual glyph pada master asli... bersifat invisible — tidak terlihat pada hasil render di ukuran teks normal (8–24 pt)" (FR-1.5)
  - **Resolution:** Invariant **dua-tier**:
    - **Hard invariant** (8–24 pt): *glyph* **HARUS** identik secara visual dengan *master* asli.
    - **Soft invariant** (24–72 pt): *glyph* **BOLEH** memiliki *deviation* minor, **selama** tidak ada *discontinuity* (sudut tajam atau perubahan arah mendadak) pada kurva Bézier.
  - *Specimen sheet* diperluas ke 48 pt dan 72 pt dengan *checklist* *discontinuity* eksplisit. *Script* validasi mendeteksi perubahan *tangent* arah >N° antar *node*.

### ✅ Resolution #7 — Timeline dengan 2 *type designer* part-time

- **Requirement:** "Estimate: 14–18 minggu (1 type designer part-time untuk harmonisasi, engineer full-time untuk tooling)" (§9.1)
  - **Resolution:** Timeline tetap **14–18 minggu** dengan tambahan **1 *type designer* part-time kedua** (~20 jam/minggu). Pembagian statis:
    - **Designer A (Lead)**: Regular + Bold Latin/Cyrillic/Greek (~70% *glyph*).
    - **Designer B (Support)**: Italic + BoldItalic Latin/Cyrillic/Greek (~25% *glyph*).
    - **Shared pool**: Symbols, ligatures, PUA, box-drawing (~5%) — *first-come-first-served* dengan *Git branch* terisolasi.
  - Escalation ke *upstream maintainer* untuk deadlock. *Effort* total paralel: 2 × 20 jam × 6 minggu = 240 jam — cukup untuk 140–240 jam harmonisasi.

### ✅ Resolution #8 — Kompatibilitas mundur output Regular/Bold

- **Requirement:** "Build pipeline HARUS tetap berfungsi dalam mode single-weight (hanya Regular + Bold) ketika enable_multi_weight = false, mempertahankan kompatibilitas mundur penuh" (FR-7.2)
  - **Resolution:** *Backward compatibility* dijamin pada level *pipeline* (mode *single-weight* masih bisa di-*trigger*), **bukan** pada level output biner. Harmonisasi kontur (FR-1.1) akan mengubah struktur *node* Regular dan Bold, sehingga `ttfautohint` akan menghasilkan *hinting* yang **berbeda** dari V0. *Release notes* V1 menyatakan secara eksplisit:
    > "Regular dan Bold TTF/OTF di-*rebuild* dari kontur harmonisasi. *Rendering* mungkin berbeda halus (<1px di beberapa ukuran) dibanding V0. Semua fitur yang ada tetap identik."
  - Perbedaan *rendering* seharusnya minimal karena FR-1.5 sudah menjamin *invisible* pada 8–24 pt.

### ✅ Resolution #9 — Build duration SM-T3 direvisi

- **Requirement:** "The multi-weight build pipeline completes in ≤ 135 minutes on a GitHub Actions free-tier runner" (SM-T3)
  - **Resolution:** SM-T3 direvisi menjadi **≤ 240 menit** pada *free-tier runner*. Optimasi *script* menjadi target eksplisit: *batching* interpolasi per *glyph*, `parallel` GNU untuk operasi independen. Estimasi kasar: harmonisasi 15 min, interpolasi 140 min, *auto-hinting* 80 min, *packaging* 10 min.

### ✅ Resolution #10 — Faux italic untuk weight baru

- **Requirement:** "Varian italic saat ini hanya tersedia untuk Regular dan Bold. Pada V1, italic untuk weight baru TIDAK dihasilkan — pengguna yang memilih Medium (500) dan mengaktifkan italic akan mendapatkan faux italic (sintesis miring oleh sistem operasi)" (§5.3)
  - **Resolution:** *Faux italic* **diterima** untuk Medium dan SemiBold (V1). *Release notes* V1 mencantumkan **tabel kompatibilitas per platform**:
    - **macOS** (Font Book): *faux italic* otomatis via *synthesis*.
    - **Windows** (GDI/DirectWrite): *faux italic* otomatis jika tidak ada *italic master*.
    - **Linux** (`fontconfig`): tergantung konfigurasi — *workaround*: `synthetic-slant = true` di `fonts.conf`.
    - **Browser CSS**: bergantung pada `font-synthesis` *property* — Firefox membolehkan, Chrome dengan set tertentu melarang.
  - *README* menambahkan *section* "Faux Italic Limitations" dengan *workaround* spesifik per platform. *Italic* sejati untuk *weight* baru ditunda ke V2.

### ✅ Resolution #11 — CON-001 vs aturan OpenType (FEA)

- **Requirement:** "Invariant CON-001 (tidak boleh memmodifikasi Scripts/features.py) tetap berlaku. Semua pekerjaan harmonisasi dan interpolasi dilakukan melalui wrapper script baru atau toolchain terpisah" (§2.3, §8.1)
  - **Resolution:** *Wrapper* baru (`scripts/multi_weight_driver.py`) **memanggil** `features.py` (subprocess atau `import`) **6 kali** — satu kali per *weight* master (Regular, Medium, SemiBold, Bold, Italic, BoldItalic). Setiap *call* menghasilkan file `.fea` terpisah dengan *output path* unik per *weight*. `features.py` **tidak dimodifikasi** — hanya dipanggil lebih sering. Asumsi: `features.py` deterministik & *idempotent* (divalidasi di Phase 0).

### ✅ Resolution #12 — Cross-master harmonization (2 pasangan)

- **Requirement:** "Glyph pada master Regular dan Bold HARUS diselaraskan" (FR-1.1) — hanya menyebutkan 1 pasangan *master*.
  - **Resolution:** Harmonisasi V1 mencakup **2 pasangan independen**:
    - **Regular ↔ Bold** — untuk interpolasi Medium 500 dan SemiBold 600 *upright*.
    - **Italic ↔ BoldItalic** — untuk fondasi V2 (Italic Medium dan Italic SemiBold), meskipun tidak digunakan di V1.
  - Pasangan Regular↔Italic atau Bold↔BoldItalic **tidak** diselaraskan (tidak ada *use case* V1 maupun V2 langsung).

---

## 2. 🧩 Addressed Edge Cases & Unhandled Scenarios

### ✅ Edge Case E1 — Selisih glyph Regular↔Bold (-2)

- **Scenario:** Codebase menunjukkan Regular.sfdir berisi **1.042** *glyph*, Bold.sfdir berisi **1.040** *glyph* — selisih 2 *glyph* yang tidak ada di Bold. Jika ada *glyph* `X` di Regular tapi tidak di Bold, maka *glyph* `X` tidak bisa diinterpolasi karena tidak memiliki pasangan di *master* satunya.
  - **Handling Strategy:** *Glyph* tanpa pasangan di *master* target disalin langsung (*copy as fallback*) dari *master* yang memiliki *glyph* tersebut ke *output weight* baru. Untuk Medium dan SemiBold, *glyph* `X` dari Regular (tanpa padanan Bold) disalin apa adanya ke *output*. Tidak ada upaya interpolasi untuk *glyph* ini.

### ✅ Edge Case E2 — 4 *glyph* italic-only di Italic.sfdir

- **Scenario:** Italic.sfdir berisi **1.046** *glyph* — selisih **+4** dari Regular (1.042). Keempat *glyph* ini kemungkinan adalah *glyph* Unicode yang hanya ada di *master* Italic (misal: karakter historis, PUA yang hanya relevan untuk *italic rendering*).
  - **Handling Strategy:** Diterapkan *copy as fallback* (diperluas dari E1): *glyph* italic-only disalin langsung dari Italic ke *output* Italic (Medium, SemiBold, Bold yang sudah ada). Tidak ada interpolasi karena tidak ada pasangan di *master* *upright*.

### ✅ Edge Case E3 — 1 *glyph* bold-italic-only di BoldItalic.sfdir

- **Scenario:** BoldItalic.sfdir berisi **1.041** *glyph* — selisih **-1** dari Bold (1.040). Satu *glyph* ini hanya ada di BoldItalic.
  - **Handling Strategy:** Sama seperti E2 — *copy as fallback* ke *output* BoldItalic (Bold existing, tidak ada *weight* baru untuk *italic* di V1).

### ✅ Edge Case E4 — Ekstrapolasi Light/ExtraBold gagal visual review

- **Scenario:** Setelah PoC, *type designer* menilai hasil ekstrapolasi Light 300 atau ExtraBold 800 memiliki distorsi yang tidak memenuhi *Visual Quality Rubrik* (Resolution #3).
  - **Handling Strategy:** *Weight* tersebut **dikeluarkan dari V1** dan masuk V2 dengan pendekatan *additional master drawing* (mitigasi risiko §8.3). V1 *release* mencakup 4 *core weight* (Regular, Medium, SemiBold, Bold). Proyek **tidak dianggap gagal** — *partial success* tier tercapai.

### ✅ Edge Case E5 — Faux italic di platform berbeda

- **Scenario:** Pengguna mengaktifkan `font-style: italic` untuk Medium (500) di IDE/browser, namun tidak ada Italic Medium *master* di V1. Hasil *faux italic* bervariasi per platform.
  - **Handling Strategy:** Tabel kompatibilitas per platform di *release notes* V1 (lihat Resolution #10). *User* yang butuh *italic* sejati untuk *weight* baru menunggu V2. *Workaround* Linux: `synthetic-slant = true` di `fonts.conf`. *Workaround* browser: `font-synthesis: style` di CSS.

### ✅ Edge Case E6 — *Rendering* di luar 8–24 pt (presentasi, poster)

- **Scenario:** Pengguna menggunakan font di ukuran 48 pt (judul presentasi), 72 pt (poster), atau 100+ pt (banner). *Node* tambahan dari harmonisasi bisa terlihat sebagai *discontinuity* pada kurva di ukuran besar.
  - **Handling Strategy:** Invariant dua-tier (Resolution #6) — *hard* (8–24 pt identik) + *soft* (24–72 pt tanpa *discontinuity*). *Script* validasi otomatis mendeteksi perubahan *tangent* arah >N° antar *node*. *Specimen sheet* mencakup 48 pt dan 72 pt dengan *checklist* *discontinuity*.

### ⚠️ Edge Case E7 — Konflik harmonisasi antar 2 *type designer* (partial — *escalation path* ke *upstream maintainer* belum eksplisit di PRD)

- **Scenario:** Designer A dan Designer B mengerjakan *glyph* yang sama (misal: *glyph* `g` di shared pool Symbols) dan menghasilkan harmonisasi berbeda — siapa yang memutuskan?
  - **Handling Strategy:** Pembagian statis (Resolution #7) — Designer A fokus Regular+Bold Latin/Cyrillic/Greek, Designer B fokus Italic+BoldItalic Latin/Cyrillic/Greek. *Shared pool* (Symbols, ligatures, PUA, box-drawing) menggunakan *Git branch* terisolasi per *glyph family* dengan *first-come-first-served*. Jika terjadi konflik pada *glyph* yang sama, *escalation* ke *upstream maintainer*.

### ✅ Edge Case E8 — Build duration > 135 menit (SM-T3 original)

- **Scenario:** Dengan 4 *master* × 4 *weight* × ~1.042 *glyph* per *weight*, total operasi interpolasi ~16.672 — estimasi ~140 menit untuk interpolasi saja, ditambah *auto-hinting* ~80 menit. Total ~245 menit, melebihi SM-T3 original 135 menit.
  - **Handling Strategy:** SM-T3 direvisi menjadi ≤ 240 menit (Resolution #9). Optimasi *script* menjadi target: *batching* per *glyph*, `parallel` GNU untuk operasi independen. Estimasi setelah optimasi: ~200 menit.

### ✅ Edge Case E9 — User update dari V0 ke V1 melihat *pixel rendering* berbeda

- **Scenario:** Pengguna yang sudah menginstal `FantasqueSansMono-Regular.ttf` dari V0 melakukan *update* ke V1. *Auto-hinting* yang di-*regenerate* dari kontur harmonisasi menghasilkan *rendering* sedikit berbeda (FR-1.5 menjamin *invisible* pada 8–24 pt, tapi bisa terlihat pada ukuran besar atau *anti-aliasing* tertentu).
  - **Handling Strategy:** *Minor visual drift* **diterima** (Resolution #8). *Release notes* V1 menyatakan eksplisit. Tidak ada upaya mempertahankan *byte-identical* output. *User* paranoid didorong untuk *test* di *staging* sebelum *deploy* ke *production*.

### ✅ Edge Case E10 — Fork owner memicu Custom Build tanpa stretch weight

- **Scenario:** Setelah V1 *release*, *fork owner* memicu Custom Build dengan `enable_multi_weight = true`, namun Light/ExtraBold sudah dikeluarkan dari V1 karena PoC gagal.
  - **Handling Strategy:** Custom Build hanya menghasilkan **4 *core weight***. *Stretch weight* (jika berhasil di PoC) hanya tersedia di *release* publik upstream, **tidak** di Custom Build *artifact*. Hal ini mencegah *fork owner* mendapat *partial build* yang tidak konsisten dengan *upstream release*.

---

## 3. 🔍 Validated Implicit Assumptions

### ✅ Assumption A1 — `features.py` deterministik & idempotent

- **Assumption:** Memanggil `features.py` 6× (satu per *weight* master) dengan parameter berbeda akan menghasilkan output FEA yang konsisten untuk *glyph* yang identik. Jika `features.py` menghasilkan output non-deterministik (misal: timestamp, random ID, atau state global), 6 *call* akan menghasilkan output yang tidak reproducible.
  - **Validation:** Asumsi ini **wajib divalidasi** di Phase 0 dengan eksperimen:
    1. Panggil `features.py` dua kali untuk Regular master, bandingkan output byte-by-byte.
    2. Jika identik, deterministik confirmed.
    3. Ulangi untuk Bold, Italic, BoldItalic.
  - Kegagalan determinism akan dideteksi dini dan *wrapper* dapat ditambahkan *caching layer* (misal: `functools.lru_cache` pada level *glyph*).

### ✅ Assumption A2 — FontForge interpolation tidak mengubah *advance width*

- **Assumption:** `font.interpolateFonts()` mempertahankan *advance width* *glyph* (tidak melakukan interpolasi metrik). Jika asumsi ini salah, *monospace guarantee* (§2.3, §5.3) akan terlanggar — Medium dan SemiBold akan memiliki *advance width* yang sedikit berbeda dari Regular/Bold, menyebabkan pergeseran kolom di editor.
  - **Validation:** Asumsi ini **KRITIS** dan **wajib divalidasi empiris** di Phase 0:
    1. Harmonisasi 10 *glyph* sample (a, g, &, @, M, dll.).
    2. Interpolasi Medium dari Regular+Bold harmonis.
    3. Bandingkan *advance width* Regular original vs Medium hasil interpolasi.
    4. Jika berbeda, *script* harus *post-process*: salin *hmtx* table dari Regular ke Medium, atau *override* *advance width* per *glyph* sebelum *save*.

### ✅ Assumption A3 — TTF rebuild dari kontur harmonisasi memiliki hinting berbeda

- **Assumption:** `ttfautohint` membaca struktur *node* kontur. Jika kontur Regular diubah (penambahan *node* untuk harmonisasi), output *hinting* akan **berbeda** dari V0. Pengguna yang *update* dari V0 ke V1 akan melihat *pixel rendering* berbeda halus.
  - **Validation:** *Confirmed* via Resolution #8. *Spec phase* harus menambahkan *validation script* yang membandingkan *hinting output* V0 vs V1 untuk deteksi regresi. *Release notes* V1 mendokumentasikan eksplisit.

### ✅ Assumption A4 — 2 *type designer* part-time dapat bekerja paralel tanpa konflik

- **Assumption:** Designer A (~20 jam/minggu) dan Designer B (~20 jam/minggu) dapat bekerja paralel pada *master* berbeda (Regular+Bold vs Italic+BoldItalic) tanpa *resource contention* atau konflik. Total *throughput* 40 jam/minggu.
  - **Validation:** Asumsi ini memerlukan validasi di Phase 0 — kedua *designer* harus latihan satu siklus harmonisasi pada 10 *glyph* bersama untuk:
    1. Mengkalibrasi *throughput* aktual vs estimasi 20 jam/minggu.
    2. Mengidentifikasi potensi konflik pada *shared pool* (Symbols, ligatures).
    3. Menetapkan *escalation path* yang jelas jika deadlock terjadi.
  - *Branch isolation* via Git adalah mekanisme teknis utama — setiap *designer* bekerja di *branch* pribadi, di-*merge* oleh *lead designer* (Designer A).

### ✅ Assumption A5 — 5 *glyph* italic-only tidak diperlukan di Regular/Bold

- **Assumption:** 4 *glyph* di Italic.sfdir yang tidak ada di Regular, dan 1 *glyph* di BoldItalic.sfdir yang tidak ada di Bold, adalah *glyph* italic-specific (tidak pernah digunakan dalam *context upright*). Asumsi ini aman berdasarkan inspeksi codebase — tidak ada *cross-reference* dari *glyph* italic-only ke Regular/Bold usage.
  - **Validation:** *Confirmed* via codebase inspection. *Copy-as-fallback* (E2, E3) aman.

### ✅ Assumption A6 — `scripts/multi_weight_driver.py` baru tidak akan menjadi *single point of failure*

- **Assumption:** *Wrapper* baru yang memanggil `features.py` 6× akan stabil setelah initial *debugging*. Kegagalan di *wrapper* (misal: *path* salah, *permission* issue) tidak akan mempengaruhi *build* single-weight existing.
  - **Validation:** *Confirmed* via Resolution #11 — *wrapper* dipanggil sebagai *pre-build step* opsional (FR-7.1: `enable_multi_weight` parameter). Mode *single-weight* tidak melewati *wrapper*, sehingga *failure mode* terisolasi.

### ✅ Assumption A7 — `sources/Harmonized/` direktori baru cukup besar

- **Assumption:** Penyimpanan 4 *master* harmonisasi (Regular, Bold, Italic, BoldItalic) di `sources/Harmonized/` menambah 2–5 MB (estimasi §8.2). Ini diterima oleh *repository* Fantasque Sans Mono yang sudah berisi *source legacy* ~50+ MB.
  - **Validation:** *Confirmed* via §8.2. Tidak ada *repository size concern* yang material.

---

## 4. 📝 Next Steps

1. **Update PRD** — `docs/prd-20260731-1000-multi-weight-variants.md` harus direvisi untuk mencerminkan semua 12 resolusi di atas sebelum diserahkan ke **SpecificationArchitect** (Phase Spec). Perubahan minimum yang diperlukan:
   - §1.2: Ganti "enam weight statis" menjadi "4 core + 2 stretch weight (partial success tier)".
   - FR-1.1: Eksplisitkan 2 pasangan harmonisasi (Regular↔Bold + Italic↔BoldItalic).
   - FR-1.5: Tambah *soft invariant* tier (24–72 pt) + *discontinuity check*.
   - FR-2.1: Perluas subset PoC ke ~40–50 *glyph* multi-kontur.
   - FR-2.4: Rujuk ke *Visual Quality Rubrik* baru.
   - FR-7.2: Klarifikasi "kompatibilitas mundur" = level *pipeline*, bukan *byte-identical output*.
   - SM-T3: Direvisi menjadi ≤ 240 menit.
   - §9.1: Tambah 1 *type designer* part-time kedua.

2. **Update CONTEXT.md** — Tambahkan istilah domain baru hasil klarifikasi:
   - **Master** (Regular, Bold, Italic, BoldItalic, base FantasqueSans)
   - **Harmonization** (proses penyeragaman struktur *node* kontur)
   - **Static Weight** vs **Variable Font** (VF)
   - **Core Weight** vs **Stretch Weight**
   - **Faux Italic** vs **Real Italic**
   - **Type Designer** (peran internal, V1 = 2 *part-time*)

3. **ADR baru** — **TIDAK diperlukan** untuk keputusan FEA wrapper (Resolution #11). *Triple gate* ADR tidak sepenuhnya terpenuhi:
   - **Hard to reverse**: Lemah — memanggil `features.py` 6× dengan *output path* unik adalah pattern yang mudah direfactor di kemudian hari.
   - **Surprising**: Lemah — memanggil *script* build per-*weight* adalah pattern natural di build pipeline.
   - **Real trade-off**: Ya, tapi *trade-off* (CON-001 compliance vs *architectural risk*) sudah cukup didokumentasikan di PRD §2.3 dan §8.1.
   - Keputusan: **skip ADR** untuk Resolution #11. Keputusan ini sendiri dapat menjadi *ADR* jika di kemudian hari ada *engineer* yang mempertanyakan kenapa *wrapper* memanggil `features.py` 6× — *rationale* ada di *clarification report* ini.

4. **Eksperimen validasi awal (Phase 0)** — *Deliverable* wajib sebelum Phase 1 (PoC):
   - **E0.1**: `features.py` idempotency test (6 *calls*, *output diff*).
   - **E0.2**: FontForge interpolation *advance width* test (10 *glyph*, sebelum-sesudah banding).
   - **E0.3**: 2-*designer* parallel work simulation (10 *glyph* harmonisasi bersama, *throughput* calibration).
   - **E0.4**: Visual Quality Rubrik dokumentasi (5–10 *glyph* referensi + 5 contoh distorsi).

5. **Spec phase handoff** — Setelah PRD direvisi dan eksperimen Phase 0 selesai, proyek siap masuk ke **/sdlc-define-specs** dengan SpecificationArchitect. *Spec* harus mendokumentasikan:
   - API dan *interface* `scripts/multi_weight_driver.py`.
   - *Schema* file `.fea` per *weight*.
   - *Algorithm* `ttfautohint` *post-processing* untuk *discontinuity check*.
   - *Git workflow* untuk 2 *designer* parallel.
