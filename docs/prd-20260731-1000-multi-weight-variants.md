---
title: "PRD — Multi-Weight Font Variants for Fantasque Sans Mono"
status: DRAFT (Phase 1 — post consistency audit revision v1.3)
date: 2026-07-31
version: 1.3
phase: SDLC Phase 1 (PRD)
project: Fantasque Sans Mono
author: Senior Product Manager
upstream_discovery: docs/discovery-draft-20260730-2110-multi-weight-variants.md
upstream_clarification: docs/audit/clarification-report-multi-weight-variants-2026-07-31.md
upstream_consistency_audit: docs/audit/consistency-audit-multi-weight-variants-2026-07-31.md
downstream_phase: "@SpecificationArchitect → /sdlc-define-specs"
related_docs:
  - docs/ARCHITECTURE.md
  - docs/audit/clarification-report-multi-weight-variants-2026-07-31.md
  - docs/audit/consistency-audit-multi-weight-variants-2026-07-31.md
  - docs/adr/0001-multi-stage-docker-legacy-tools.md (Superseded — see ADR-0002)
  - docs/adr/0002-multi-stage-docker-deferred-engine-port.md
  - docs/adr/0003-workflow-a-fontforge-v1-interpolation.md
  - docs/prd-20260723-1130-custom-build-workflow.md
  - docs/CUSTOM-BUILD.md
target_release_window: After V1 implementation completes, no fixed calendar date
license_impact: None — all new weight variants remain under SIL Open Font License (OFL-1.1)
---
<!-- markdownlint-disable -->

## PRD: Multi-Weight Font Variants for Fantasque Sans Mono

## 1. Product overview

### 1.1 Document title and version

- **PRD**: Multi-Weight Font Variants for Fantasque Sans Mono
- **Version**: 1.3 (DRAFT — post consistency audit revision, ready for Technical Specification)
- **SDLC Phase**: Phase 1 (PRD) — upstream: Phase 0 Discovery (approved) + Clarification Checkpoint (completed) + Consistency Audit (completed); downstream: Technical Specification (`/sdlc-define-specs`)
- **Date**: 2026-07-31
- **Author**: Product Manager PRD persona
- **Upstream artifacts**:
  - Discovery Draft: [`docs/discovery-draft-20260730-2110-multi-weight-variants.md`](/docs/discovery-draft-20260730-2110-multi-weight-variants.md)
  - Clarification Report: [`docs/audit/clarification-report-multi-weight-variants-2026-07-31.md`](/docs/audit/clarification-report-multi-weight-variants-2026-07-31.md)
  - Consistency Audit: [`docs/audit/consistency-audit-multi-weight-variants-2026-07-31.md`](/docs/audit/consistency-audit-multi-weight-variants-2026-07-31.md)
- **Target release window**: After V1 implementation completes, no fixed calendar date
- **License impact**: None — all new weight variants remain under SIL Open Font License (OFL-1.1); no relicensing or rebranding

### 1.2 Product summary

Fantasque Sans Mono saat ini hanya mendistribusikan dua varian *weight* — Regular (400) dan Bold (700) — beserta versi *italic*-nya. Keterbatasan ini tidak lagi sejalan dengan ekspektasi pengembang modern yang terbiasa dengan font pemrograman multi-weight seperti JetBrains Mono, Fira Code, dan Maple Mono yang menawarkan 5–9 varian *weight* untuk hierarki visual yang kaya di dalam editor kode.

Inisiatif ini bertujuan untuk memperluas jajaran varian *weight* Fantasque Sans Mono menjadi **enam *weight* statis dalam dua tier kesuksesan** — empat **core weight** (Regular 400, Medium 500, SemiBold 600, Bold 700) sebagai target *full success* (wajib), dan dua **stretch weight** (Light 300, ExtraBold 800) sebagai target *partial success* (opsional) — melalui proses *master harmonization* dan interpolasi antar *master* yang sudah ada. *Stretch weight* hanya dirilis jika ekstrapolasi FontForge lolos *visual review* (FR-5); jika gagal, ditunda ke V2 dengan pendekatan *additional master drawing* (mitigasi risiko §8.3). Fitur ini akan meningkatkan fleksibilitas tipografi pengguna sekaligus memperkuat posisi kompetitif font di ekosistem *open-source*.

Proyek ini bersifat *type-design-heavy*: terdapat ~1.042 *glyph* yang konturnya tidak kompatibel antara *master* Regular dan Bold saat ini. Oleh karena itu, PRD ini menetapkan pendekatan bertahap dengan *Proof of Concept* (PoC) terlebih dahulu sebelum pengerjaan penuh, serta memberlakukan standar kualitas visual yang ketat untuk mempertahankan ciri khas *"wibbly-wobbly handwriting feel"* dari Fantasque Sans Mono.

**Keputusan tooling V1**: Berdasarkan analisis pada Discovery Draft, V1 akan mengikuti **Workflow A (FontForge Interpolation)** — pendekatan jangka pendek yang menggunakan *toolchain* yang sudah ada (`.sfdir` + FontForge Python API). Migrasi ke **Workflow B (UFO Modernization dengan `fontmake`/`ufo2ft`)** yang merupakan standar industri akan dieksplorasi pada GH-006 sebagai persiapan V2, terutama jika Variable Font (VF) menjadi target V2.

## 2. Goals

### 2.1 Business goals

- **Meningkatkan adopsi dan popularitas**: Memperluas daya tarik Fantasque Sans Mono bagi pengembang modern yang mengharapkan font pemrograman dengan dukungan multi-*weight* sebagai fitur standar, sehingga mendorong peningkatan jumlah pengguna dan kontributor di ekosistem *open-source*.
- **Positioning kompetitif**: Menyetarakan kemampuan tipografi Fantasque Sans Mono dengan font pemrograman terkemuka (JetBrains Mono, Fira Code, Maple Mono, Cascadia Code) yang telah memiliki 5+ varian *weight*, menghilangkan kelemahan kompetitif yang saat ini dimiliki font.
- **Memperluas use case**: Membuka adopsi di luar editor kode — mencakup dokumentasi teknis, situs blog, UI *mockup*, dan materi presentasi — yang semuanya membutuhkan variasi *weight* untuk *typographic hierarchy* yang efektif.

### 2.2 User goals

- **Developer/Programmer**: Mendapatkan hierarki visual yang kaya di dalam IDE dan *code editor* — misalnya, *keyword* dalam Bold (700), kode reguler dalam Regular (400), komentar dalam Light (300), dan anotasi dalam Medium (500) — untuk meningkatkan keterbacaan dan produktivitas.
- **UI/UX Designer**: Memiliki palet *weight* yang memadai untuk menciptakan *typographic hierarchy* yang baik dalam *mockup*, *wireframe*, dan *design system* yang menggunakan Fantasque Sans Mono.
- **Technical Writer & Blogger**: Menggunakan variasi *weight* untuk *emphasis* dan *code highlighting* di dalam artikel teknis, dokumentasi, dan cuplikan kode di blog, sehingga konten lebih mudah dibaca dan profesional.

### 2.3 Non-goals (Out of Scope)

- **Variable Font (VF) tidak termasuk dalam V1**: Pembuatan *single file* Variable Font dengan sumbu `wght` — yang membutuhkan migrasi penuh ke *toolchain* UFO/`fontmake` — ditunda ke V2. V1 hanya menghasilkan *static weight instances*.
- **Otomatisasi penuh tanpa *human review***: Setiap *weight* hasil interpolasi WAJIB melalui *visual review* manual. Tidak ada *weight* yang dirilis tanpa pemeriksaan kualitas visual.
- **Penambahan *weight* di luar rentang 300–800**: *Weight* ekstrem seperti Thin (100), ExtraLight (200), dan Black (900) tidak termasuk dalam V1. Rentang V1 dibatasi pada apa yang dapat dihasilkan secara andal dari dua *master* yang ada (Regular 400 dan Bold 700).
- **Modifikasi pada *source* *legacy***: Invariant `CON-001` (tidak boleh memodifikasi `Scripts/features.py`) tetap berlaku. Semua pekerjaan harmonisasi dan interpolasi dilakukan melalui *wrapper script* baru atau *toolchain* terpisah.
- **Penggunaan `font.changeWeight()` atau algoritma *stroke modification* otomatis**: FontForge menyediakan `font.changeWeight()` sebagai cara cepat menambah/mengurangi *stroke weight*, namun algoritma ini akan **merusak *counter space* dan detail *handwritten*** dari kurva Bézier asimetris yang menjadi ciri khas Fantasque Sans Mono (lihat Discovery Draft §3). V1 hanya menggunakan *interpolasi* antar *master* Regular dan Bold yang sudah diharmonisasikan — bukan algoritma *stroke modification*.
- **Perubahan metrik vertikal atau lebar**: Ascent, Descent, LineGap, dan *advance width* tetap identik antar *weight* untuk mempertahankan kompatibilitas *monospace*.

## 3. User personas

### 3.1 Key user types

**External users** (*consumers* of the multi-weight fonts):

- **Alex** — *Software Engineer* / Developer (Persona Primer): Pengguna IDE dan *code editor* sehari-hari yang membutuhkan hierarki visual untuk berbagai elemen sintaks.
- **Rina** — *UI/UX Designer* (Persona Sekunder): Desainer yang menggunakan font untuk *mockup* dan prototipe antarmuka yang memerlukan variasi ketebalan.
- **Dewi** — *Technical Writer & Blogger* (Persona Tersier): Penulis konten teknis yang menggunakan font untuk cuplikan kode di blog dan dokumentasi.

**Internal stakeholders** (*producers* who enable the multi-weight fonts):

- **Bayu** — *Type Designer* (Persona Internal): Kontributor teknis yang melakukan harmonisasi manual dan *visual review* — *stakeholder* internal yang kualitas outputnya bergantung pada. Bayu tidak dihitung dalam *user goals* (§2.2) karena merupakan *producer*, bukan *consumer*.

### 3.2 Basic persona details

- **Developer/Programmer (Alex)**: Alex adalah *software engineer* yang menghabiskan 8–10 jam sehari di depan IDE. Ia sangat peduli dengan keterbacaan kode dan menginginkan font yang tidak hanya unik secara visual, tetapi juga mendukung *semantic highlighting* melalui variasi *weight*. Saat ini Alex menggunakan JetBrains Mono karena dukungan multi-*weight*-nya, namun ia menyukai karakter *handwritten* Fantasque Sans Mono. Ia akan beralih penuh jika tersedia varian Light, Medium, dan SemiBold.
- **UI/UX Designer (Rina)**: Rina adalah *product designer* yang membangun *design system* untuk timnya. Ia membutuhkan font *monospace* dengan setidaknya 4–5 *weight* untuk membuat *type scale* yang koheren di komponen UI seperti *code block*, *terminal output*, dan *data table*. Saat ini ia menggunakan Fira Code karena keterbatasan *weight* Fantasque Sans Mono.
- **Technical Writer & Blogger (Dewi)**: Dewi menulis tutorial dan dokumentasi teknis di blog pribadinya. Ia menggunakan cuplikan kode dengan *syntax highlighting* yang membutuhkan minimal 3 *weight* (regular untuk teks kode, *bold* untuk *keyword*, *light* untuk komentar). Ia ingin seluruh kontennya konsisten menggunakan Fantasque Sans Mono untuk *brand identity* personal.
- **Type Designer (Bayu) — Persona Internal**: Bayu adalah *type designer* internal (atau kontributor terpercaya) yang bertanggung jawab atas harmonisasi manual *glyph* dan *visual review* terhadap hasil interpolasi. Bayu adalah *gatekeeper* kualitas — tanpa persetujuannya (PoC LULUS per FR-2.4), pengerjaan penuh tidak dapat dilanjutkan ke Phase 2. **Catatan V1**: Bayu akan bekerja bersama satu *type designer* part-time tambahan (Designer B) untuk membagi beban harmonisasi: Bayu (Designer A, Lead) fokus pada Regular+Bold, Designer B fokus pada Italic+BoldItalic (lihat §9.1). *Success criteria* Bayu: menghasilkan *glyph* yang lolos *visual review* dengan tetap mempertahankan ciri *wibbly-wobbly* yang menjadi ciri khas font.

### 3.3 Role-based access

| Role | Permissions and surface area |
|---|---|
| **End User / Anonymous Downloader** (Alex, Rina, Dewi) | Dapat mengunduh dan menggunakan seluruh varian *weight* yang dipublikasikan di GitHub Releases. Tidak ada akun atau akses tulis yang diperlukan. Semua aset didistribusikan di bawah SIL Open Font License (OFL-1.1). |
| **Fork Owner** | Pengguna GitHub yang mem-fork repository upstream. Dapat memicu *Custom Build* dengan parameter `enable_multi_weight = true` untuk menghasilkan build personal berisi 4 *core weight* (Regular, Medium, SemiBold, Bold). *Stretch weight* (Light, ExtraBold) hanya tersedia di *release* publik upstream. Build artifact dipublikasikan hanya di *fork* mereka sendiri. |
| **Upstream Maintainer** | Memiliki kontrol administratif atas repository `belluzj/fantasque-sans`. Dapat memperbarui *source* harmonisasi, *wrapper script*, dan parameter *workflow* tanpa batasan. |
| **Type Designer Lead** (Bayu — Designer A) | Kontributor internal yang memimpin harmonisasi manual. Fokus pada pasangan Regular↔Bold (Latin/Cyrillic/Greek, ~70% *glyph*). Akses tulis ke `sources/Harmonized/Regular/` dan `sources/Harmonized/Bold/`. Bertindak sebagai *merge gate* untuk *branch* Designer B. |
| **Type Designer Support** (Designer B) | Kontributor internal part-time yang mendukung harmonisasi. Fokus pada pasangan Italic↔BoldItalic (Latin/Cyrillic/Greek, ~25% *glyph*). Akses tulis ke `sources/Harmonized/Italic/` dan `sources/Harmonized/BoldItalic/`. Bekerja di *branch* Git terisolasi, di-*merge* oleh Designer A. |
| **GitHub Actions Bot** | Peran sistem yang menjalankan *workflow* atas nama *fork owner*. Memiliki *scoped token* dengan izin `contents: write` yang terbatas pada *fork* tempat *workflow* dijalankan. |

## 4. Functional requirements

### FR-1: Master Harmonization (Priority: CRITICAL)

Kondisi saat ini: *Glyph* antara *master* Regular (400) dan Bold (700) **tidak memiliki jumlah titik (node) dan struktur kontur yang kompatibel** untuk interpolasi. Contoh konkret: huruf `g` memiliki 21 *node* pada kontur ke-3 di Regular, tetapi 22 *node* di Bold.

- **FR-1.1**: *Glyph* pada **dua pasangan *master*** HARUS diselaraskan (*harmonized*) sehingga setiap *glyph* memiliki jumlah *node* yang identik, urutan kontur yang sama, dan arah kurva (`clockwise`/`counter-clockwise`) yang konsisten dalam setiap pasangan:
  - **Regular ↔ Bold** — untuk interpolasi Medium (500) dan SemiBold (600) *upright*.
  - **Italic ↔ BoldItalic** — untuk fondasi V2 (*Italic Medium* dan *Italic SemiBold*), meskipun tidak digunakan di V1.
  Pasangan Regular↔Italic atau Bold↔BoldItalic **tidak** diselaraskan karena tidak ada *use case* V1 maupun V2 langsung.
  **Catatan**: Jumlah *glyph* antar *master* **tidak identik** (Regular: 1.042, Bold: 1.040, Italic: 1.046, BoldItalic: 1.041). Untuk *glyph* tanpa pasangan di *master* target, diterapkan strategi ***copy as fallback***: *glyph* disalin langsung dari *master* sumber ke *output weight* baru tanpa interpolasi. Tidak ada *glyph* yang hilang dari *output*.
- **FR-1.2**: Harmonisasi dilakukan melalui *script* Python yang berjalan di atas FontForge (`fontforge -lang=py -script`), menggunakan API FontForge untuk membandingkan struktur kontur dan menandai *glyph* yang tidak kompatibel.
- **FR-1.3**: Untuk setiap *glyph* yang tidak kompatibel, harmonisasi HARUS dilakukan secara manual oleh *type designer* — bukan melalui otomatisasi. *Script* hanya berfungsi sebagai alat deteksi dan validasi, bukan alat perbaikan.
- **FR-1.4**: Hasil harmonisasi HARUS divalidasi oleh *script* verifikasi yang memastikan jumlah *node*, urutan kontur, dan arah kurva identik antara kedua *master* untuk setiap *glyph*.
- **FR-1.5**: Harmonisasi TIDAK BOLEH mengubah tampilan visual *glyph* pada *master* asli (Regular, Bold, Italic, dan BoldItalic). Invariant visual bersifat **dua-tier**:
  - **Hard invariant** (8–24 pt): *Glyph* **HARUS** identik secara visual dengan *master* asli — tidak ada perbedaan yang terlihat pada hasil *render* di ukuran teks normal.
  - **Soft invariant** (24–72 pt): *Glyph* **BOLEH** memiliki deviasi minor, **selama** tidak ada *discontinuity* (sudut tajam atau perubahan arah mendadak) pada kurva Bézier. Perubahan *tangent* arah antar *node* >N° akan dideteksi oleh *script* validasi otomatis.
  *Specimen sheet* diperluas ke 48 pt dan 72 pt dengan *checklist discontinuity* eksplisit.

### FR-2: Proof of Concept (PoC) — Subset Glyph Interpolation (Priority: CRITICAL)

Sebelum pengerjaan penuh pada seluruh ~1.042 *glyph*, PoC dengan subset terbatas WAJIB dilakukan untuk memvalidasi kelayakan pendekatan harmonisasi dan interpolasi.

- **FR-2.1**: PoC mencakup subset **~40–50 *glyph*** prioritas tinggi yang dipilih secara strategis untuk memvalidasi berbagai tingkat kompleksitas kontur:
  - Huruf kecil `a`–`z` (26 *glyph*) — *baseline single-contour glyphs*.
  - *Glyph* multi-kontur yang rawan distorsi: `g` (eksplisit — *node count mismatch* 21 vs 22 di kontur ke-3), `@`, `&`, `Q`, `?`, `!`.
  - *Glyph* dengan *counter* kompleks: `ß`, `fi`, `fl`.
  - *Glyph* kritis fungsional: `space`, `period`, `comma`, `zero`.
  - 3–5 *glyph* tambahan dari output *script* deteksi inkompatibilitas (*worst offenders*).
  **Catatan**: Pasangan Italic↔BoldItalic tidak memerlukan PoC terpisah karena prinsip harmonisasi identik dengan pasangan Regular↔Bold. Risiko spesifik *italic* (misalnya *slant angle* tidak konsisten antar *master*) diterima dan akan ditangani di Phase 2.
- **FR-2.2**: Subset PoC WAJIB diharmonisasikan (FR-1) dan diinterpolasi untuk menghasilkan *weight* Medium (500) sebagai satu-satunya *target weight* PoC.
- **FR-2.3**: Hasil interpolasi PoC HARUS menjalani *visual diff review*: perbandingan *side-by-side* antara *glyph* asli Regular/Bold dengan *glyph* hasil interpolasi Medium, pada berbagai ukuran teks (8 pt, 12 pt, 16 pt, 24 pt).
- **FR-2.4**: PoC dinyatakan **LULUS** jika ≥ 90% *glyph* hasil interpolasi dinilai "mempertahankan nuansa *handwritten*" oleh *type designer* berdasarkan **Visual Quality Rubric** (dokumen acuan yang disusun di Phase 0 sebagai *deliverable* E0.4), dan tidak ada *glyph* yang mengalami distorsi berat (kerusakan kontur, *self-intersection*, *counter* tertutup). Rubric berisi: (a) 5–10 *glyph* referensi dari Regular existing sebagai *gold standard* "wibbly-wobbly", (b) 5 contoh distorsi yang tidak dapat diterima (*counter* tertutup, kurva terlalu kaku, *self-intersection*), dan (c) *checklist* terstruktur per *glyph*: *counter shape preserved*?, *Bézier asymmetry maintained*?, *terminal style consistent*?.
- **FR-2.5 — PoC Failure Path**: Jika PoC dinyatakan **GAGAL** (tidak memenuhi FR-2.4), proyek TIDAK BOLEH melanjutkan ke Phase 2 (Full Harmonization). Jalur keputusan yang tersedia:
  1. **Iterasi harmonisasi ulang pada subset PoC** (maksimal 2 siklus tambahan) — jika kegagalan disebabkan oleh teknik harmonisasi yang belum tepat.
  2. **Revisi cakupan V1** — misalnya, membatasi V1 hanya pada Medium (500) dan SemiBold (600) tanpa *extrapolated weights* (Light/ExtraBold), jika kegagalan terkonsentrasi pada *weight* ekstrem.
  3. **Re-evaluasi keputusan tooling** — mempertimbangkan percepatan migrasi ke Workflow B (UFO/`fontmake`) jika kegagalan disebabkan oleh keterbatasan fundamental interpolasi linear FontForge (lihat §8.3 dan GH-006).
  4. **Penundaan/penghentian fitur** — jika ketiga opsi di atas tidak layak, fitur ditunda dan PRD dikembalikan ke fase Discovery untuk evaluasi ulang.
  Keputusan akhir atas jalur yang dipilih WAJIB didokumentasikan sebagai catatan pada PRD ini (revisi minor) atau ADR baru (jika melibatkan perubahan arsitektur signifikan).

### FR-3: Full Master Harmonization (Priority: HIGH)

Setelah PoC dinyatakan LULUS, harmonisasi diperluas ke seluruh *glyph set*.

- **FR-3.1**: Seluruh *glyph* pada **empat *master*** (Regular, Bold, Italic, dan BoldItalic) HARUS diharmonisasikan dalam dua pasangan independen (Regular↔Bold dan Italic↔BoldItalic) dan lolos validasi `node-count-equal`, `contour-order-equal`, dan `curve-direction-equal` untuk setiap pasangan. Untuk *glyph* tanpa pasangan di *master* target, diterapkan *copy as fallback* (lihat FR-1.1).
- **FR-3.2**: Setiap *glyph* yang tidak kompatibel HARUS ditangani secara manual. Estimasi awal: dari 1.042 *glyph*, diperkirakan 60–80% membutuhkan penyesuaian manual berdasarkan tingkat ketidakcocokan yang terdeteksi.
- **FR-3.3**: *Glyph* harmonisasi HARUS disimpan dalam direktori `.sfdir` baru yang terpisah dari *source legacy*:
  - `sources/Harmonized/Regular/` dan `sources/Harmonized/Bold/` — untuk interpolasi *upright weight* baru.
  - `sources/Harmonized/Italic/` dan `sources/Harmonized/BoldItalic/` — untuk fondasi V2.
  Struktur ini mematuhi `CON-001` dan menjaga *source* asli tetap utuh.

### FR-4: Multi-Weight Interpolation (Priority: HIGH)

Setelah seluruh *glyph* terharmonisasi, interpolasi dilakukan untuk menghasilkan empat *weight* statis baru.

- **FR-4.1**: Menggunakan FontForge Python API (`font.interpolateFonts(factor, target)`), hasilkan *weight variant* baru berikut. *Factor* menentukan posisi *weight* pada sumbu antara Regular (=0.0) dan Bold (=1.0):
  - **Core weight** (*full success* — wajib dirilis):
    - **Medium (500)**: *Interpolation* tepat di tengah Regular-Bold (*factor* 0.5)
    - **SemiBold (600)**: *Interpolation* antara Regular-Bold (*factor* ~0.67)
  - **Stretch weight** (*partial success* — opsional, hanya dirilis jika lolos *visual review*):
    - **Light (300)**: *Extrapolation* ke arah lebih ringan dari Regular (*factor* negatif; *nilai eksak* ditentukan saat PoC berdasarkan kualitas visual)
    - **ExtraBold (800)**: *Extrapolation* ke arah lebih berat dari Bold (*factor* >1.0; *nilai eksak* ditentukan saat PoC berdasarkan kualitas visual)
  Jika *stretch weight* gagal *visual review* (FR-5), *weight* tersebut dikeluarkan dari V1 dan masuk V2 dengan pendekatan *additional master drawing*. Proyek **tidak dianggap gagal** — *partial success* tier tercapai.
- **FR-4.2**: Setiap *weight variant* baru HARUS memiliki *stem width* dan *counter size* yang proporsional — tidak boleh ada *glyph* dengan *counter* tertutup atau *stroke* yang bertabrakan.
- **FR-4.3**: Setelah interpolasi, setiap *weight* baru HARUS melewati *auto-hinting* (`ttfautohint`) untuk mempertahankan kualitas *hinting* yang konsisten dengan *weight* existing.

### FR-5: Visual Quality Assurance (Priority: HIGH)

- **FR-5.1**: Setiap *glyph* pada setiap *weight* baru (Light, Medium, SemiBold, ExtraBold) HARUS menjalani *visual review* oleh *type designer* menggunakan *specimen sheet* yang dihasilkan otomatis.
- **FR-5.2**: *Specimen sheet* mencakup: *waterfall* teks (ukuran 8, 10, 12, 14, 16, 20, 24, 32, 48, dan 72 pt), *pangram* bahasa Inggris dan Indonesia, set karakter pemrograman (`{}[]()<>;:.,`), *ligature sequences*, dan *checklist discontinuity* eksplisit untuk ukuran 48 pt dan 72 pt (sesuai *soft invariant* FR-1.5).
- **FR-5.3**: *Glyph* yang gagal *visual review* HARUS dikembalikan ke tahap harmonisasi untuk penyesuaian ulang, bukan diperbaiki langsung pada hasil interpolasi (mencegah *drift* antar *weight*).
- **FR-5.4**: Toleransi cacat visual: maksimal **2%** dari total *glyph* (≈21 *glyph* dari 1.042) boleh memiliki *minor visual artifact* yang tidak mengganggu keterbacaan di ukuran 8–16 pt.

### FR-6: Distribution & Packaging (Priority: MEDIUM)

- **FR-6.1**: Setiap *weight* baru DIDISTRIBUSIKAN dalam format TTF, OTF, dan WOFF2 (konsisten dengan format *release* saat ini).
- **FR-6.2**: Nama file mengikuti konvensi existing: `FantasqueSansMono-{Weight}.{ext}` (contoh: `FantasqueSansMono-Medium.ttf`).
- **FR-6.3**: *Release* mencakup *archive* terpisah per format (`.zip` untuk TTF, `.zip` untuk OTF, `.zip` untuk WOFF2) yang masing-masing berisi 4–6 *weight* (tergantung kelolosan *stretch weight*) + varian *Italic* yang tersedia.
- **FR-6.4**: `README.md` dan halaman *specimen* (`Specimen/`) DIPERBARUI untuk menampilkan dan mendokumentasikan seluruh varian *weight* baru, termasuk *visual comparison* antar *weight*.

### FR-7: Build Pipeline Integration (Priority: MEDIUM)

- **FR-7.1**: *Script* harmonisasi dan interpolasi DIINTEGRASIKAN ke dalam *Custom Build Workflow* (`.github/workflows/custom-build.yml`) sebagai tahap opsional yang dapat dipicu melalui `workflow_dispatch` dengan parameter boolean `enable_multi_weight`.
- **FR-7.2**: *Build pipeline* HARUS tetap berfungsi dalam mode *single-weight* (hanya Regular + Bold) ketika `enable_multi_weight = false`, mempertahankan kompatibilitas mundur pada **level pipeline** — mode *single-weight* masih dapat di-*trigger*. Namun, output TTF/OTF Regular dan Bold di V1 **tidak *byte-identical*** dengan V0 karena harmonisasi kontur (FR-1.1) mengubah struktur *node*, sehingga `ttfautohint` akan menghasilkan *hinting* yang berbeda. *Release notes* V1 menyatakan secara eksplisit bahwa *rendering* mungkin berbeda halus (<1px di beberapa ukuran) dibanding V0. Semua fitur yang ada tetap identik.
- **FR-7.3**: Durasi *build* multi-*weight* TIDAK BOLEH melebihi **≤ 240 menit** pada *GitHub Actions free-tier runner*. Estimasi kasar: harmonisasi 15 menit, interpolasi 140 menit, *auto-hinting* 80 menit, *packaging* 10 menit. Optimasi *script* menjadi target eksplisit: *batching* interpolasi per *glyph*, `parallel` GNU untuk operasi independen (lihat SM-T3).

## 5. User experience

### 5.1 Entry points & first-time user flow

- **Pengguna existing**: Saat mengunduh *release* terbaru, pengguna akan menemukan 6 varian *weight* (sebelumnya hanya 2) di dalam folder TTF/OTF/Webfonts. Mereka dapat langsung menginstal *weight* yang diinginkan tanpa perubahan konfigurasi.
- **Pengguna baru**: Melalui halaman GitHub Releases atau website spesimen, pengguna baru akan melihat *visual waterfall* yang menampilkan seluruh *weight* secara *side-by-side*, membantu mereka memilih *weight* yang sesuai sebelum mengunduh.
- **Pengguna Custom Build**: Pada halaman *Actions* → *Custom Build* → *Run workflow*, tersedia *checkbox* baru **"Enable Multi-Weight Variants"** yang jika dicentang akan menghasilkan 4 *core weight* (Regular, Medium, SemiBold, Bold) sekaligus dalam satu *build artifact*. *Stretch weight* (Light, ExtraBold) hanya tersedia di *release* publik upstream.

### 5.2 Core experience

- **Instalasi**: Pengguna mengunduh dan menginstal *weight* yang diinginkan melalui mekanisme standar sistem operasi (Windows: *right-click → Install*, macOS: *Font Book*, Linux: `~/.local/share/fonts/`).
- **Konfigurasi IDE**: Pengguna memilih varian di *font settings* editor — misalnya `'Fantasque Sans Mono'` sebagai font utama, `'Fantasque Sans Mono Bold'` untuk *bold text*, `'Fantasque Sans Mono Light'` untuk *line numbers*, dan `'Fantasque Sans Mono Medium'` untuk *active tab*.
- **Web embedding**: Pengguna *web developer* menggunakan `@font-face` dengan *descriptor* `font-weight` yang sesuai — `font-weight: 300` memuat *Light*, `font-weight: 500` memuat *Medium*, dan seterusnya — identik dengan cara font multi-*weight* lainnya digunakan di web.

### 5.3 UI/UX highlights & Edge cases

- **Fallback behavior**: Jika aplikasi tidak mendukung pemilihan *weight* spesifik (misal terminal sederhana), *Regular* (400) tetap menjadi *default* — tidak ada perubahan perilaku bagi pengguna yang tidak mengonfigurasi apa pun.
- **Italic consistency**: Varian *Italic* saat ini hanya tersedia untuk Regular dan Bold. Pada V1, *Italic* untuk *weight* baru TIDAK dihasilkan — pengguna yang memilih Medium (500) atau SemiBold (600) dan mengaktifkan *italic* akan mendapatkan *faux italic* (sintesis miring oleh sistem operasi). *Release notes* V1 mencantumkan **tabel kompatibilitas per platform**:

  | Platform | Faux Italic Behavior | Workaround |
  |---|---|---|
  | **macOS** (Font Book) | *Faux italic* otomatis via *synthesis* | Tidak diperlukan |
  | **Windows** (GDI/DirectWrite) | *Faux italic* otomatis jika tidak ada *italic master* | Tidak diperlukan |
  | **Linux** (`fontconfig`) | Tergantung konfigurasi | `synthetic-slant = true` di `fonts.conf` |
  | **Browser CSS** | Bergantung `font-synthesis` *property* | `font-synthesis: style` di CSS; Firefox membolehkan, Chrome dengan set tertentu melarang |

  *README* ditambahkan *section* "Faux Italic Limitations" dengan *workaround* spesifik per platform. *Italic* sejati untuk *weight* baru ditunda ke V2.

- **Monospace guarantee**: Seluruh *weight* baru HARUS mempertahankan *advance width* yang identik dengan Regular dan Bold — pengguna tidak akan mengalami pergeseran kolom saat mengganti *weight* di editor.
- **Ligature compatibility**: *Ligature* yang sudah ada (misal `->`, `=>`, `!=`) HARUS berfungsi identik di seluruh *weight* baru. Jika *ligature* tertentu rusak akibat interpolasi, *glyph* tersebut harus dikeluarkan dari *output* dan dikembalikan ke tahap harmonisasi.

## 6. Narrative

Alex, seorang *software engineer*, telah lama mengagumi karakter unik Fantasque Sans Mono — aksen *handwritten*-nya membuat kode terasa lebih personal dan hangat. Namun, ia selalu kembali ke JetBrains Mono karena kebutuhannya akan *semantic highlighting*: *keyword* harus tebal (Bold), komentar harus ringan (Light), dan anotasi harus medium. Dengan dirilisnya varian multi-*weight*, Alex akhirnya bisa sepenuhnya beralih. Ia menginstal enam *weight* Fantasque Sans Mono, mengonfigurasi IDE-nya dalam hitungan menit, dan kini kodenya tidak hanya fungsional — tetapi juga indah. Timnya yang melihat *screenshot* pun ikut mengadopsi font yang sama.

Rina, seorang *product designer*, mengalami hal serupa. Ia ingin menggunakan satu font *monospace* yang konsisten di seluruh *design system*-nya — dari *code block* di dokumentasi hingga *data table* di aplikasi. Dengan 6 *weight* yang tersedia, ia akhirnya bisa membuat *type scale* yang koheren tanpa harus mencampur font yang berbeda. Semua elemen kini bernafas dalam "wibbly-wobbly" yang sama.

Bagi Dewi, *technical writer*, konsistensi adalah segalanya. Artikel teknisnya kini menampilkan cuplikan kode dalam satu *typeface* — dari komentar Light hingga *keyword* SemiBold — menciptakan identitas visual yang kuat dan profesional di setiap publikasi.

Di balik layar, **Bayu** (Designer A, Lead) dan satu *type designer* pendukung (Designer B) telah menghabiskan berminggu-minggu secara paralel menyelaraskan ratusan kontur Bézier — Bayu pada *glyph* Regular dan Bold, Designer B pada Italic dan BoldItalic — pekerjaan monoton yang nyaris tak terlihat oleh pengguna akhir, namun menentukan apakah setiap *weight* baru akan mempertahankan "jiwa *handwritten*" Fantasque Sans Mono. Bagi mereka, multi-weight bukan sekadar fitur teknis — melainkan komitmen terhadap kualitas yang hanya bisa dijaga oleh tangan manusia, bukan algoritma.

## 7. Success metrics

### 7.1 User-centric metrics

- **SM-U1 — Adoption of new weight variants**: ≥ 30% of *download link* clicks on the release page are for archives that include the new weight variants (archives labelled "Multi-Weight" or "Full") — measured via the *GitHub Release API* (`releases/{id}/downloads` *event count* per asset) within 3 months post-release.
- **SM-U2 — GitHub star growth**: ≥ 20% increase in *GitHub stars* within 6 months after the multi-weight release, as a proxy for improved *visibility* and community interest.
- **SM-U3 — Positive sentiment**: ≥ 80% positive comments or reactions on *social media* (Twitter/X, Reddit r/typography, Hacker News) and on *GitHub issues* within the first month post-release.
- **SM-U4 — Self-reported feature usage** *(proxy, optional)*: ≥ 5 *GitHub issues* or *discussions* opened by users reporting successful use of Light, Medium, SemiBold, or ExtraBold variants in production within 3 months post-release. (Note: per-fork Custom Build metrics are not visible to upstream, so a self-reporting proxy is used instead.)

### 7.2 Business metrics

- **SM-B1 — Download increase**: ≥ 50% increase in total *release* downloads compared to the 3-month average before the multi-weight release.
- **SM-B2 — Contributor growth**: ≥ 3 new contributors involved in *issues* or *pull requests* related to *glyph* or new *weight* improvements within 6 months.
- **SM-B3 — User churn reduction**: ≥ 25% decrease in *issues* requesting additional *weight* support (indicating the need has been met).

### 7.3 Technical metrics

- **SM-T1 — Harmonization success rate**: ≥ 98% of *glyphs* pass harmonization validation (`node-count-equal`, `contour-order-equal`, `curve-direction-equal`).
- **SM-T2 — Interpolation success rate**: ≥ 98% of interpolated *glyphs* produce no fatal error or distortion (contour damage, *self-intersection*) — beyond the 2% *minor artifact* tolerance defined in FR-5.4.
- **SM-T3 — Build duration**: The multi-weight *build pipeline* completes in **≤ 240 menit** pada *GitHub Actions free-tier runner*. Estimasi kasar: harmonisasi 15 menit, interpolasi 140 menit, *auto-hinting* 80 menit, *packaging* 10 menit. Optimasi *script* menjadi target eksplisit: *batching* interpolasi per *glyph*, `parallel` GNU untuk operasi independen.
- **SM-T4 — Release size**: Total *archive release* size (6 *weights* × 3 formats) does not exceed 5× the current *release* size (2 *weights*); total WOFF2 for 6 *weights* ≤ 500 KB (related to GH-003).

## 8. Technical considerations (Input for Engineering Team)

### 8.1 Integration points

- **FontForge Python API**: Seluruh proses harmonisasi dan interpolasi bertumpu pada FontForge CLI dengan Python 3 *bindings* (via `fontforge -lang=py -script`). Spesifikasi *stack* runtime yang tepat, *base image* Docker, dan *dependency* instalasi akan ditentukan oleh tim teknis pada fase *Spec* dengan mengacu pada `docs/ARCHITECTURE.md` dan ADR-0002.
- **Custom Build Workflow** (`.github/workflows/custom-build.yml`): *Wrapper script* baru (`scripts/multi_weight_driver.py`) akan dipanggil dari *workflow* yang sudah ada sebagai langkah *pre-build* opsional. *Wrapper* **memanggil** `features.py` (via subprocess atau `import`) **6 kali** — satu kali per *weight master* (Regular, Medium, SemiBold, Bold, Italic, BoldItalic) — menghasilkan file `.fea` terpisah dengan *output path* unik per *weight*. `features.py` **tidak dimodifikasi** — hanya dipanggil lebih sering (mematuhi invariant `CON-001` yang melindungi `Scripts/build.py`, `Scripts/fontbuilder.py`, `Scripts/features.py`). **Asumsi**: `features.py` deterministik & *idempotent* — wajib divalidasi di Phase 0 (eksperimen E0.1).
- **Release Pipeline**: *Script* `Scripts/packaging.sh` yang sudah ada akan DIPERBARUI untuk mengenali *multi-weight output directory* dan menyertakan seluruh *weight* dalam *archive release*. Format arsip (zip/tar.gz) dan struktur direktori internal akan mengikuti konvensi *Custom Build* existing.
- **Cross-PRD Integration — Custom Build Workflow**: Parameter `enable_multi_weight` yang diusulkan di PRD ini (§5.1, FR-7.1) merupakan *extension point* terhadap Custom Build Workflow yang didefinisikan di [`docs/prd-20260723-1130-custom-build-workflow.md`](../prd-20260723-1130-custom-build-workflow.md). Custom Build Spec mungkin memerlukan *minor update* untuk mengakomodasi parameter baru ini. Format WOFF dan SVG untuk *weight* baru akan diputuskan di fase Spec Multi-Weight — tidak dibahas di PRD ini.
- **Dokumen Terkait**: Spesifikasi teknis detail tentang *integration points* akan didokumentasikan di *Technical Specification* (`spec/spec-multi-weight-variants.md`) setelah PRD ini disetujui.

### 8.2 Data storage & privacy

- **Tidak ada data pengguna**: Seluruh proses berjalan di dalam Docker container pada GitHub Actions runner. Tidak ada data pengguna yang dikumpulkan, disimpan, atau ditransmisikan.
- **Artifact Retention**: GitHub Actions *artifact retention* (default 90 hari) berlaku untuk *build artifact* multi-*weight*. *Release artifact* bersifat permanen.
- **Source .sfdir**: Direktori `.sfdir` baru (`sources/Harmonized/`) disimpan di repository Git yang sama. Ukuran tambahan diperkirakan 4–8 MB (setara dengan duplikasi `Regular.sfdir` + `Bold.sfdir` + `Italic.sfdir` + `BoldItalic.sfdir` untuk 4 *master harmonisasi*).

### 8.3 Scalability & potential technical challenges

- **Skala harmonisasi manual**: Dengan ~1.042 *glyph* × 2 pasangan *master* (Regular↔Bold + Italic↔BoldItalic) dan estimasi 60–80% membutuhkan harmonisasi manual, ini adalah upaya *type design* yang signifikan — diperkirakan **140–240 jam** kerja *type designer* (termasuk +30% *effort* tambahan untuk Italic↔BoldItalic). Risiko: kemacetan pada *throughput* manusia. Mitigasi: PoC (FR-2) memberikan validasi *early* sebelum investasi waktu besar, dan 2 *type designer* part-time bekerja paralel (Designer A: Regular+Bold, Designer B: Italic+BoldItalic).
- **Keterbatasan interpolasi FontForge**: `font.interpolateFonts()` hanya mendukung interpolasi linear — tidak ada *optical correction*. Untuk *weight* ekstrem (Light 300 dan ExtraBold 800), *extrapolation* dapat menghasilkan distorsi yang tidak dapat diperbaiki tanpa *manual touch-up*. Risiko: hasil Light dan ExtraBold tidak memenuhi standar kualitas. Mitigasi: jika *extrapolation* gagal pada *visual review* (FR-5), *weight* tersebut dikeluarkan dari V1 dan ditunda ke V2 dengan pendekatan *additional master drawing*.
- **Durasi *build***: Interpolasi hingga 4 *weight* × ~1.042 *glyph* = hingga ~4.168 operasi interpolasi. Ditambah *auto-hinting* dan *packaging*, total waktu bisa mencapai 200–240 menit. Risiko: *timeout* pada *GitHub Actions* (360 menit *limit*, cukup aman dengan *buffer* 120 menit). Mitigasi: optimasi *script* (*batching*, *parallel processing* via GNU `parallel`), dan *monitoring* progres (lihat SM-T3).
- **CON-001 Constraint**: Semua *script* baru harus beroperasi di samping *source legacy* tanpa memodifikasinya. Ini berarti *wrapper script* harus mengimpor modul yang diperlukan dan menghasilkan *output* di direktori terpisah, dengan *symlink* atau *copy* untuk *glyph* yang tidak berubah.

## 9. Milestones & sequencing

### 9.1 Project estimate & Team composition

- **Size**: Large | **Estimate**: 14–18 minggu | **Team**: 2 Type Designer part-time (~20 jam/minggu masing-masing: Designer A (Lead) untuk Regular+Bold Latin/Cyrillic/Greek, Designer B (Support) untuk Italic+BoldItalic Latin/Cyrillic/Greek), 1 DevOps Engineer (pipeline & *scripting*), 1 PM/QA (*acceptance testing* & *specimen review*). Pembagian *shared pool* (Symbols, ligatures, PUA, box-drawing): *first-come-first-served* dengan Git *branch* terisolasi. Jika terjadi deadlock pada *shared pool*, eskalasi ke *upstream maintainer* untuk resolusi. Total *effort* paralel: 2 × 20 jam × 6 minggu = 240 jam — cukup untuk estimasi 140–240 jam harmonisasi.

### 9.2 Suggested phases

- **Phase 0 — Tooling & PoC Preparation (Minggu 1–2)**:
  - Tulis *script* deteksi inkompatibilitas kontur (FontForge Python API).
  - Tulis *script* interpolasi *proof-of-concept*.
  - Siapkan *specimen sheet generator* untuk *visual review*.
  - Siapkan *branch* Git terisolasi (`feature/multi-weight-poc`).
  - **Eksperimen validasi awal (wajib sebelum Phase 1)**:
    - **E0.1 — `features.py` idempotency test**: Panggil `features.py` 6 kali (satu per *weight master*), bandingkan output *byte-by-byte*. Jika identik, deterministik *confirmed*.
    - **E0.2 — FontForge interpolation *advance width* test**: Harmonisasi 10 *glyph* sample (`a`, `g`, `&`, `@`, `M`, dll.), interpolasi Medium, bandingkan *advance width* Regular original vs Medium hasil interpolasi. Jika berbeda, *script* harus *post-process*: salin *hmtx* table dari Regular ke Medium.
    - **E0.3 — 2-*designer* parallel work simulation**: Kedua *designer* berlatih satu siklus harmonisasi pada 10 *glyph* bersama untuk mengkalibrasi *throughput* aktual dan mengidentifikasi potensi konflik pada *shared pool*.
    - **E0.4 — Visual Quality Rubric dokumentasi**: Susun dokumen berisi 5–10 *glyph* referensi dari Regular existing sebagai *gold standard* "wibbly-wobbly", 5 contoh distorsi yang tidak dapat diterima, dan *checklist* terstruktur per *glyph*. Rubric menjadi acuan bagi *type designer* untuk validasi konsisten (lihat FR-2.4).

- **Phase 1 — Proof of Concept (Minggu 3–4)**:
  - Harmonisasi subset ~40–50 *glyph* (sesuai FR-2.1: huruf `a`–`z`, multi-kontur `g`/`@`/`&`/`Q`/`?`/`!`, *counter* kompleks `ß`/`fi`/`fl`, dan 3–5 *worst offenders* dari *script* deteksi).
  - Interpolasi Medium (500) dari subset yang terharmonisasi.
  - *Visual review* + *acceptance testing* PoC menggunakan Visual Quality Rubric (E0.4).
  - *Gate Check*: PoC HARUS LULUS (FR-2.4) sebelum lanjut ke Phase 2. Jika GAGAL, ikuti jalur keputusan pada FR-2.5.

- **Phase 2 — Full Harmonization (Minggu 5–10)**:
  - Harmonisasi seluruh *glyph* pada **empat *master*** (Regular, Bold, Italic, BoldItalic) dalam 2 pasangan independen:
    - Designer A (Lead): Regular + Bold Latin/Cyrillic/Greek (~70% *glyph*).
    - Designer B (Support): Italic + BoldItalic Latin/Cyrillic/Greek (~25% *glyph*).
    - *Shared pool* (Symbols, ligatures, PUA, box-drawing): ~5% — *first-come-first-served* dengan Git *branch* terisolasi.
  - Validasi otomatis: `node-count-equal`, `contour-order-equal`, `curve-direction-equal`.
  - *Visual spot-check* per *glyph family* (misal: semua *arrow glyphs*, semua *bracket glyphs*).

- **Phase 3 — Multi-Weight Interpolation & QA (Minggu 11–12)**:
  - Interpolasi *core weight* (Medium 500, SemiBold 600) — wajib.
  - Interpolasi *stretch weight* (Light 300, ExtraBold 800) — opsional, hanya jika ekstrapolasi memungkinkan.
  - *Auto-hinting* untuk semua *weight* baru.
  - *Full visual review* dengan *specimen sheet* (8–72 pt, termasuk *discontinuity checklist* untuk 48 pt dan 72 pt).
  - *Iterative fix*: *glyph* gagal → harmonisasi ulang → interpolasi ulang.
  - *Gate Check*: *Stretch weight* yang gagal *visual review* dikeluarkan dari V1 (masuk V2). Proyek **tidak dianggap gagal** — *partial success* tier tercapai.

- **Phase 4 — Pipeline Integration & Release (Minggu 13–14)**:
  - Integrasi ke *Custom Build Workflow* (`enable_multi_weight` parameter) — *wrapper* `multi_weight_driver.py` memanggil `features.py` 6×.
  - *End-to-end CI test*: *workflow_dispatch* → *build* → *artifact* → *release*.
  - Pembaruan dokumentasi (`README.md` termasuk *section* "Faux Italic Limitations", `Specimen/`, *release notes* dengan tabel kompatibilitas platform).
  - Publikasi *release* publik dengan *core weight* (4–6 *weight* tergantung hasil *stretch weight*) × 3 format.

- **Buffer Phase — Iteration & Stabilization (Minggu 15–18, *optional based on PoC outcome*):**
  - *Reserved* untuk iterasi harmonisasi ulang, perbaikan *visual review* yang ditemukan di Phase 3, dan stabilisasi build.
  - Aktif hanya jika PoC (Phase 1) atau Phase 3 memerlukan harmonisasi ulang yang signifikan.

## 10. User stories & Acceptance Criteria

### 10.1. Developer menginstal dan mengonfigurasi varian multi-weight di IDE

- **ID**: GH-001
- **Story**: Sebagai seorang *software engineer*, saya ingin menginstal varian Light, Medium, dan SemiBold dari Fantasque Sans Mono, sehingga saya dapat mengonfigurasi *semantic highlighting* yang kaya di IDE saya (misal: *keyword* Bold, kode Regular, komentar Light, anotasi Medium).
- **Acceptance criteria**:
  - [ ] Seluruh 4 *core weight* (Regular 400, Medium 500, SemiBold 600, Bold 700) **wajib** tersedia sebagai file TTF terpisah dalam *release* GitHub.
  - [ ] *Stretch weight* (Light 300, ExtraBold 800) tersedia sebagai file TTF terpisah **jika lolos *visual review*** (FR-5); jika tidak, ditunda ke V2.
  - [ ] Setiap *weight* terinstal dengan benar di Windows, macOS, dan Linux (terverifikasi dengan `fontconfig`/Font Book/Font Settings).
  - [ ] Setiap *weight* muncul dengan nama yang benar di *font picker* aplikasi (misal: "Fantasque Sans Mono Medium").
  - [ ] *Advance width* seluruh *weight* identik — teks yang sama menempati jumlah kolom yang sama saat *weight* diganti di editor monospace.
  - [ ] *Ligature* (`->`, `=>`, `!=`, dll.) berfungsi dengan benar di semua *weight*.

### 10.2. Desainer menggunakan multi-weight untuk design system

- **ID**: GH-002
- **Story**: Sebagai seorang *UI/UX designer*, saya ingin melihat *specimen* visual seluruh varian *weight* secara *side-by-side*, sehingga saya dapat memilih kombinasi *weight* yang tepat untuk *type scale* di *design system* saya.
- **Acceptance criteria**:
  - [ ] Halaman *specimen* (`Specimen/`) menampilkan *waterfall* teks untuk seluruh *weight* pada ukuran 8, 10, 12, 14, 16, 20, 24, 32, 48, dan 72 pt.
  - [ ] *Specimen* menampilkan *pangram* ("The quick brown fox jumps over the lazy dog") dan karakter pemrograman (`{}[]()<>;:.,!#$%^&*`) untuk setiap *weight*.
  - [ ] *Specimen* menyertakan *discontinuity checklist* untuk ukuran 48 pt dan 72 pt (sesuai *soft invariant* FR-1.5).
  - [ ] *Specimen* tersedia dalam format HTML yang dapat dibuka di browser secara lokal.
  - [ ] *Specimen* menyertakan informasi metrik untuk setiap *weight*: *stem width*, *x-height*, *cap height*, dan *advance width*.

### 10.3. Technical writer mendapatkan konsistensi tipografi

- **ID**: GH-003
- **Story**: Sebagai seorang *technical writer*, saya ingin menggunakan *web fonts* (WOFF2) multi-*weight* Fantasque Sans Mono di blog saya, sehingga cuplikan kode memiliki variasi *weight* yang konsisten dengan identitas visual saya.
- **Acceptance criteria**:
  - [ ] Seluruh *core weight* (4 *weight*) **wajib** tersedia dalam format WOFF2 di *release* GitHub; *stretch weight* jika lolos *visual review*.
  - [ ] File WOFF2 dapat digunakan dengan *standard* `@font-face` CSS *declaration* dan *descriptor* `font-weight` yang sesuai (300, 400, 500, 600, 700, 800).
  - [ ] *Font loading* di browser tidak menghasilkan *flash of unstyled text* (FOUT) yang signifikan — total ukuran WOFF2 untuk hingga 6 *weight* ≤ 500 KB.
  - [ ] *Documentation* `README.md` menyertakan contoh kode CSS untuk *embedding* web multi-*weight*.

### 10.4. Pemilik fork memicu Custom Build multi-weight

- **ID**: GH-004
- **Story**: Sebagai seorang *fork owner*, saya ingin memicu *custom build* yang menghasilkan varian *core weight* (Regular, Medium, SemiBold, Bold) melalui satu klik di *GitHub Actions*, sehingga saya bisa mendapatkan *customized* font dengan variasi *weight* lengkap tanpa *toolchain* lokal.
- **Acceptance criteria**:
  - [ ] *Custom Build Workflow* memiliki parameter *boolean* `enable_multi_weight` di halaman *Run workflow*.
  - [ ] Ketika `enable_multi_weight = true`, *build* menghasilkan 4 *core weight* (Regular, Medium, SemiBold, Bold) × 3 format (TTF, OTF, WOFF2) dalam satu *artifact*. *Stretch weight* (Light, ExtraBold) **tidak** tersedia di Custom Build — hanya di *release* publik upstream (lihat Edge Case E10 di *clarification report*).
  - [ ] Ketika `enable_multi_weight = false`, *build* hanya menghasilkan Regular + Bold (kompatibilitas mundur penuh pada level pipeline).
  - [ ] *Artifact* ZIP multi-*weight* memiliki ukuran yang wajar (≤ 5 MB) dan dapat diunduh dari halaman *Actions*.
  - [ ] *Build log* menampilkan progres per *weight*: "Harmonizing...", "Calling features.py for Regular...", "Interpolating Medium (500)...", "Hinting...", "Packaging...".

### 10.5. Type designer memvalidasi kualitas visual hasil interpolasi

- **ID**: GH-005
- **Story**: Sebagai seorang *type designer*, saya ingin memiliki *tool* validasi otomatis yang membandingkan *glyph* hasil interpolasi dengan *master* asli, sehingga saya dapat dengan cepat mengidentifikasi *glyph* mana yang memerlukan harmonisasi ulang.
- **Acceptance criteria**:
  - [ ] *Script* validasi menghasilkan laporan JSON yang mencantumkan setiap *glyph* hasil interpolasi dengan status: `pass`, `warning` (*minor artifact*), atau `fail` (distorsi berat), mengacu pada **Visual Quality Rubric** (E0.4).
  - [ ] *Specimen sheet* PDF dihasilkan secara otomatis untuk setiap *weight*, menampilkan seluruh *glyph* dalam format grid, termasuk ukuran 48 pt dan 72 pt dengan *discontinuity checklist*.
  - [ ] *Script* `diff` visual menghasilkan *overlay* gambar PNG antara *glyph* interpolasi dan *glyph master* terdekat untuk *glyph* dengan status `warning` atau `fail`.
  - [ ] *Type designer* dapat menandai *glyph* yang memerlukan perbaikan dalam file *tracking* (CSV atau JSON) yang akan digunakan oleh *script* harmonisasi ulang.

### 10.6. Eksplorasi migrasi toolchain ke UFO/fontmake (V2 Preview)

- **ID**: GH-006
- **Story**: Sebagai seorang *build engineer*, saya ingin mengeksplorasi migrasi dari FontForge `.sfdir` ke ekosistem UFO v3 + `fontmake` sebagai persiapan V2 (Variable Font), sehingga kami memahami *gap* dan *effort* yang diperlukan sebelum berkomitmen penuh.
- **Acceptance criteria**:
  - [ ] *Spike research* didokumentasikan dalam ADR baru yang membandingkan *pros/cons* FontForge interpolation vs. UFO/`fontmake` pipeline.
  - [ ] *Proof-of-concept* konversi satu *glyph* (misal: `A`) dari `.sfdir` ke UFO v3 berhasil — `fontmake` dapat membangun `.ttf` dari `.ufo` hasil konversi.
  - [ ] Daftar *blocker* dan *unknowns* untuk migrasi penuh didokumentasikan (estimasi *effort*, kompatibilitas *feature file*, dukungan *ligature*).
