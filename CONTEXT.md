# Fantasque Sans Mono — Custom Build Context

Glosarium istilah domain untuk fitur Custom Build pada proyek Fantasque Sans Mono. Mendefinisikan terminologi untuk mencegah ambiguitas di seluruh codebase dan dokumentasi.

## Language

**Custom Build**:
Fitur yang memungkinkan pengguna GitHub menghasilkan varian font Fantasque Sans Mono yang dipersonalisasi langsung dari cloud tanpa toolchain build lokal.

**Variant**:
Kombinasi dari satu atau lebih opsi build yang menghasilkan output font dengan karakteristik visual tertentu.
_Avoid_: configuration, preset, build option

**Normal**:
Varian default Fantasque Sans Mono tanpa opsi build apapun yang diaktifkan — output baseline dari pipeline build.
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
