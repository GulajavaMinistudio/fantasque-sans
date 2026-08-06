# Fantasque Sans Mono — Project Context

Glosarium istilah domain untuk proyek Fantasque Sans Mono. Mendefinisikan terminologi untuk mencegah ambiguitas di seluruh codebase dan dokumentasi. Istilah dikelompokkan per klaster fitur.

## Language

### Custom Build

**Custom Build**:
Fitur yang memungkinkan pengguna GitHub menghasilkan varian font Fantasque Sans Mono yang dipersonalisasi langsung dari cloud tanpa toolchain build lokal.

**Variant**:
Kombinasi dari satu atau lebih opsi build yang menghasilkan output font dengan karakteristik visual tertentu.
_Avoid_: configuration, preset, build option

**Normal**:
Varian Fantasque Sans Mono tanpa opsi build apa pun yang diaktifkan — hasil pipeline build tanpa modifikasi.
_Avoid_: default variant, baseline, standard

**Fork Owner**:
Pengguna GitHub yang telah mem-fork repository upstream dan memiliki izin untuk memicu Custom Build di fork mereka sendiri.
_Avoid_: fork maintainer, repo owner

**Upstream**:
Repository asli `belluzj/fantasque-sans` yang menjadi sumber utama dan acuan bagi seluruh fork komunitas.
_Avoid_: main repo, original repository, source of truth

**Manifest**:
File `manifest.json` yang disertakan dalam setiap arsip build, berisi metadata build (timestamp, opsi resolved, checksum, versi toolchain) untuk keperluan audit dan verifikasi.

**Workflow**:
File GitHub Actions `.github/workflows/custom-build.yml` di repository upstream yang mendefinisikan pipeline otomatis untuk membangun varian font kustom.

### Multi-Weight Variants

**Multi-Weight Variants**:
Fitur yang memperluas jajaran weight font melalui harmonisasi kontur dan interpolasi antar master. V1 memiliki dua tier kesuksesan: 4 core weight (Regular 400, Medium 500, SemiBold 600, Bold 700) sebagai *full success*, dan 2 stretch weight (Light 300, ExtraBold 800) sebagai *partial success* yang hanya dirilis jika ekstrapolasi FontForge lolos *visual review*.
_Avoid_: multi-weight feature, weight expansion

**Weight Variant**:
Satu level ketebalan diskrit dari font (misalnya Light 300, Medium 500) yang didistribusikan sebagai file font terpisah.
_Avoid_: weight level, static instance, discrete weight

**Static Weight**:
File font terpisah untuk satu nilai weight tertentu (misalnya Regular.ttf untuk 400). Setiap weight adalah *file* independen dengan *glyph* sendiri — berbeda dengan *Variable Font* yang menyimpan seluruh rentang weight dalam satu *file*.
_Avoid_: static instance, weight file

**Variable Font**:
File font tunggal yang menyimpan seluruh rentang weight dalam satu *file* dengan sumbu `wght` yang dapat di-parameterisasi saat *render*. Tidak diproduksi di V1 — menjadi target V2 dengan migrasi ke UFO/`fontmake` (lihat GH-006).
_Avoid_: VF, variable typeface, multiple master font

**Core Weight**:
Weight yang menjadi target utama V1 dan wajib ada di *release*: Regular 400, Medium 500, SemiBold 600, Bold 700. Keempat weight ini dihasilkan melalui interpolasi murni (Medium 500 = factor 0.5, SemiBold 600 = factor 0.67 eksak antara Regular-Bold).
_Avoid_: primary weight, required weight, main weight

**Stretch Weight**:
Weight yang menjadi target opsional V1: Light 300 dan ExtraBold 800. Karena berada di luar rentang master Regular-Bold, keduanya memerlukan *extrapolation* (bukan interpolasi). Dirilis hanya jika ekstrapolasi lolos *Visual Quality Rubric*; ditunda ke V2 jika tidak.
_Avoid_: aspirational weight, optional weight, bonus weight

**Release Upstream Pipeline**:
Jalur produksi *stretch weight* (Light 300, ExtraBold 800) yang dieksekusi secara manual/terisolasi oleh *upstream maintainer* di luar Custom Build CI, aktif hanya setelah *core weight* lolos *visual review*; *stretch weight* yang gagal *visual review* dikeluarkan dari V1 ke V2 (GUD-004).
_Avoid_: upstream CI pipeline, release build, upstream release pipeline

**Master**:
Font sumber yang menjadi titik ujung interpolasi — Regular (400), Bold (700), Italic, dan BoldItalic — yang struktur konturnya menjadi acuan harmonisasi.
_Avoid_: source font, base font, interpolation endpoint

**Master Harmonization**:
Proses penyelarasan jumlah node, urutan kontur, dan arah kurva antara dua master (Regular↔Bold untuk weight upright, Italic↔BoldItalic untuk weight italic) agar kompatibel untuk interpolasi.
_Avoid_: outline harmonization, contour alignment, glyph harmonization

**Interpolation**:
Pembangkitan weight variant perantara dari dua master yang sudah diharmonisasikan; weight di luar rentang master dihasilkan melalui extrapolation.
_Avoid_: weight generation, font blending

**Workflow A**:
Jalur pembangkitan weight pada V1 yang berbasis interpolasi FontForge terhadap sumber `.sfdir` yang sudah diharmonisasikan. Berbeda dengan istilah **Workflow** pada klaster Custom Build yang merujuk ke file pipeline GitHub Actions.
_Avoid_: FontForge path, short-term workflow

**Workflow B**:
Jalur pembangkitan weight berbasis ekosistem UFO v3 dan `fontmake` (standar industri) yang menjadi kandidat pendekatan V2 dan Variable Font.
_Avoid_: UFO path, modernization path

**Faux Italic**:
Sintesis miring algoritmis yang dihasilkan oleh sistem operasi atau *browser* ketika *glyph italic* tidak tersedia untuk suatu weight. Pada V1, weight baru (Medium, SemiBold) menggunakan *faux italic* — bukan *italic master* — karena V1 tidak menghasilkan *italic* untuk *weight* baru. Perilaku bervariasi per platform (macOS/Windows otomatis, Linux butuh `synthetic-slant`, browser bergantung pada `font-synthesis`).
_Avoid_: synthesized italic, fake italic, oblique, slanted

**Type Designer**:
Kontributor internal yang bertanggung jawab atas harmonisasi manual *glyph* dan *visual review* terhadap hasil interpolasi. Pada V1, terdapat **2 type designer part-time** dengan pembagian statis: Designer A fokus Regular+Bold, Designer B fokus Italic+BoldItalic. *Escalation* ke *upstream maintainer* untuk deadlock.
_Avoid_: font designer, glyph artist, type engineer

**Visual Quality Rubric**:
Dokumen acuan yang mendefinisikan kualitas visual "wibbly-wobbly handwriting feel" Fantasque Sans Mono secara terukur. Berisi 5–10 *glyph* referensi (gold standard), 5 contoh distorsi yang ditolak, dan *checklist* terstruktur per *glyph* (counter shape, Bézier asymmetry, terminal style). Menjadi acuan bagi *type designer* dan *validation script* otomatis.
_Avoid_: quality checklist, visual standards doc, style guide

### Nerd Font Flavor

**Nerd Font Flavor**:
Flavor rilis Fantasque Sans Mono yang diperkaya dengan set icon lengkap Nerd Fonts v3.5.0 pada setiap *weight* monospace yang dirilis. Icon ditambahkan oleh *patcher* (aditif) di codepoint Private Use Area dan tidak pernah menggantikan *glyph* native.
_Avoid_: patched font, icon font, Nerd Font variant

**Base Flavor**:
Flavor rilis Fantasque Sans Mono tanpa augmentasi icon — artefak yang sama dengan output pipeline saat ini. Base Flavor tidak pernah dimutasi oleh *patcher*; dalam mode *single-weight* set artefak dan perilaku outputnya tetap sama dengan baseline (byte-identity tidak dijamin karena manifest berisi *build_timestamp* dinamis).
_Avoid_: vanilla font, original font, regular flavor

**Native Glyph Fallback**:
Kebijakan substitusi outline Regular untuk *glyph* native yang tidak dapat diharmonisasi (427 *glyph*: 374 topology + 53 equalize) pada *weight* hasil interpolasi, sehingga output tetap *renderable* dan deterministik. Merupakan batasan visual yang didisklosur, bukan perbaikan.
_Avoid_: fallback font, glyph substitution, outline copying

**Collision Report**:
Laporan per-*weight* yang mendaftar setiap codepoint yang *glyph*-nya berubah akibat *patching*, dibandingkan terhadap baseline 15 codepoint PUA yang terverifikasi. Laporan ini menjadi *gate* rilis untuk mendeteksi drift icon set baru.
_Avoid_: conflict report, overwrite report
