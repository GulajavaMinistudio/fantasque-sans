# Clarification Report: Implementation Plan for Multi-Weight Variants

<!-- markdownlint-disable -->

*Status: Seluruh resolusi di bawah telah diimplementasikan ke `plan/plan-feature-multi-weight-variants-v1.3.md` versi 1.6 (2026-07-31).*

## 1. 🚨 Resolved Critical Ambiguities (Blockers)

- ✅ **Requirement:** "Eksekusi `multi_weight_driver.py` untuk Core & Stretch Weights" + "Menghasilkan *core* & *stretch weights*" (ID: PLAN TASK-3.1 / GOAL-004 / TASK-3.3 / TASK-3.5 / TASK-3.X — Phase 3)
  - **Resolution:** Spec §4.6, §4.10, dan AC-B02 secara eksplisit menetapkan bahwa *stretch weights* (Light 300, ExtraBold 800) **hanya** dihasilkan di *pipeline release upstream*, bukan di Custom Build. Phase 3 (TASK-3.1) dan verifikasinya (TASK-3.3, TASK-3.4, TASK-3.5, TASK-3.X) **hanya mencakup Core Weights**: Medium 500 (factor 0.5) dan SemiBold 600 (factor ~0.67). *Stretch weights* ditangguhkan ke Phase 5 / *release upstream pipeline*. GOAL-004 diupdate dari "Menghasilkan core & stretch weights" menjadi "Menghasilkan core weights". Flag CLI untuk stretch weight menggunakan nama yang didefinisikan di Spec §4.6 — `--enable-light` / `--enable-extrabold` (bukan `--include-stretch`).
  - **Plan v1.6:** Implemented — GOAL-004, TASK-3.1, TASK-3.2–3.4, TASK-3.X (core weights only), TASK-5.4 (stretch → release upstream)
- ✅ **Requirement:** "Eksekusi `ttfautohint` secara manual/lokal untuk QA visual (validasi sebelum integrasi pipeline)" (ID: PLAN TASK-3.2 — Phase 3)
  - **Resolution:** Spec §3.1 REQ-I04, §4.6, dan §8.5 secara tegas menetapkan bahwa `ttfautohint` **hanya** boleh dieksekusi di **Stage 2 Docker container**. Host runner tidak memiliki `ttfautohint` terpasang. TASK-3.2 **dihapus** dari Phase 3. QA visual pra-*hinting* menggunakan *specimen sheet HTML* dan *FontForge rendering preview* (TTX/text-mode) — cukup untuk mendeteksi distorsi kontur dan *discontinuity* sebelum *hinting* diterapkan. Verifikasi *hinting* konsisten penuh dialihkan ke akhir Phase 4 (setelah TASK-4.X) sesuai dengan Spec §8.5.
  - **Plan v1.6:** Implemented — TASK-3.2 (`ttfautohint` manual) dihapus; QA pra-hinting di TASK-3.2 baru; verifikasi hinting Stage 2 di TASK-4.X
- ✅ **Requirement:** "Disepakati: Langkah eksekusi `ttfautohint` lokal wajib ditambahkan pada subset PoC (Task 1.2.b)" (dokumen klarifikasi sebelumnya)
  - **Resolution:** **DIBATALKAN.** Keputusan ini kini bertentangan dengan keputusan klarifikasi terbaru. Spec §8.5 menetapkan `ttfautohint` hanya di Stage 2. PoC tidak membutuhkan *hinting* untuk *visual review* — *glyph* asli dan hasil interpolasi dapat dibandingkan dengan adil pada level rendering yang sama (kedua belum di-*hint*).
  - **Plan v1.6:** Implemented — TASK-1.2 eksplisit TANPA `ttfautohint` (PoC, Spec §8.5)
- ✅ **Requirement:** "`multi_weight_driver.py` dirancang menggunakan parameter/argumen flag khusus (`--include-stretch`)" (dokumen klarifikasi sebelumnya)
  - **Resolution:** Nama flag **diperbarui** menjadi `--enable-light` / `--enable-extrabold` agar konsisten dengan Spec §4.6. Argumen ini **hanya** diteruskan oleh **release upstream pipeline**, bukan oleh Docker RUN kondisional Custom Build. Custom Build (flag `--multi-weight`) **selalu** hanya menghasilkan **core weights** (Medium 500 + SemiBold 600). Release upstream pipeline memanggil `--enable-light` / `--enable-extrabold` secara terpisah pada *release build* untuk menghasilkan Light 300 dan ExtraBold 800 setelah core weights lulus *visual review*. Ini konsisten dengan Spec §4.6 (flowchart: "release upstream saja"), §4.9 (kontrak Dockerfile hanya meneruskan `--multi-weight`), dan AC-B02.
  - **Plan v1.6:** Implemented — TASK-0.7 (flag `--enable-light`/`--enable-extrabold` hanya release upstream)
- ✅ **Requirement:** "Modifikasi `Scripts/packaging.sh` untuk memproses weight baru" (ID: REQ-D03 / TASK-4.4 di Implementation Plan)
  - **Resolution:** `packaging.sh` perlu diperluas untuk menghasilkan **3 archive terpisah per format** (TTF .zip, OTF .zip, WOFF2 .zip) sesuai Spec REQ-D01/REQ-D03 dan §4.10. Custom Build hanya mencakup *core weights*; *stretch weights* hanya dimasukkan pada *release upstream*.
  - **Plan v1.6:** Implemented — TASK-4.4 (3 archive per format; daftar weight per mode, E10/FR-6.3)

## 2. 🧩 Addressed Edge Cases & Unhandled Scenarios

- ✅ **Scenario:** *Font* hasil interpolasi (misalnya direktori `Medium.sfdir`) memiliki *internal metadata* bawaan (seperti `os2_weight` dan `fontname`) yang diturunkan/identik dengan *master* aslinya. Hal ini berisiko membuat font baru saling bertumpuk (*conflict*) dengan *weight* aslinya saat dipasang di sistem operasi pengguna.
  - **Handling Strategy:** Pembaruan *internal font metadata* (injeksi `os2_weight=500`, *fullname*, dsb.) sepenuhnya ditangani dan dienkapsulasi oleh `multi_weight_driver.py`. Metadata akan di-inject langsung ke objek internal FontForge sebelum *driver* menyimpan file menjadi struktur `Medium.sfdir`.
  - **Plan v1.6:** Implemented — TASK-0.7 (injeksi metadata driver), TASK-3.1, TASK-3.X (verifikasi metadata)
- ✅ **Scenario:** *Stretch weight* (Light, ExtraBold) dapat gagal *visual review* meskipun berhasil secara teknis (interpolasi berhasil, advance width identik, tidak ada *discontinuity*).
  - **Handling Strategy:** FontForge *extrapolation* ke luar rentang master dapat menghasilkan distorsi visual yang tidak terdeteksi oleh *validation script* otomatis. Spec §10.6 (TASK-3.5) dan §8.5 menetapkan *gate check*: *stretch weight* yang gagal *visual review* **dikeluarkan dari V1** dan masuk ke V2. Jika kedua *stretch weight* gagal, rilis V1 tetap dilakukan dengan 4 core weight saja — proyek tidak dianggap gagal (GUD-004). Keputusan ini **hanya** memengaruhi *release upstream pipeline*, bukan Custom Build.
  - **Plan v1.6:** Implemented — TASK-3.4 (gate check cakupan), TASK-5.4 (gate check kelolosan), RISK-002
- ✅ **Scenario:** *Specimen sheet* untuk QA visual tidak tersedia dalam format yang sama seperti *hinted* font, sehingga type designer mungkin melihat *rendering* yang berbeda dengan yang akan dilihat pengguna akhir.
  - **Handling Strategy:** Spec §4.3 REQ-S05 dan §8.5 menetapkan bahwa *hinting* dilakukan di Stage 2, setelah interpolasi. QA visual pra-*hinting* (Phase 3) menggunakan *specimen sheet HTML* untuk mendeteksi distorsi kontur dan *discontinuity* — ini cukup karena *hinting* tidak mengubah bentuk kontur, hanya menambahkan *bytecode* untuk *rasterization*. Verifikasi akhir *hinting* dilakukan di Phase 4 setelah pipeline terintegrasi.
  - **Plan v1.6:** Implemented — TASK-3.2 (QA pra-hinting), TASK-4.X & TEST-006 (verifikasi hinting akhir Phase 4)

## 3. 🔍 Validated Implicit Assumptions

- ✅ **Assumption:** *Legacy script* proyek (yaitu `build.py`, `fontbuilder.py`, atau `configure.py`) harus dimodifikasi sebagian agar mengetahui adanya penambahan varian *weight* baru saat melakukan kompilasi dari SFDIR ke TTF/OTF.
  - **Validation:** Asumsi ini **DITOLAK**. Aturan preservasi `CON-001` menegaskan bahwa `build.py`, `fontbuilder.py`, `features.py`, dan `Makefile` **TIDAK** boleh dimodifikasi. Direktori sumber baru (`Medium.sfdir`) yang dirakit oleh `multi_weight_driver.py` bersifat sepenuhnya *self-contained* dan sudah memiliki metadata final. *Legacy driver* (`custom_build_driver.py` yang ada — bukan yang baru) hanya akan memproses direktori *input* yang diberikan kepadanya seolah-olah itu adalah *master* reguler (mode *agnostic*). `configure.py` **diperluasi** (bukan dilindungi CON-001) untuk menambahkan `--form-enable-multi-weight` flag forwarding (Spec §4.9).
  - **Plan v1.6:** Implemented — TASK-4.1 (catatan `configure.py` TIDAK dilindungi CON-001)
- ✅ **Assumption:** `custom_build_driver.py` perlu diperluas untuk memanggil `features.py` 6× via *subprocess*.
  - **Validation:** Asumsi ini **DITOLAK** oleh Spec §4.7. `custom_build_driver.py` yang ada sudah memanggil `update_features()` **in-process** untuk setiap `.sfdir` yang dibuild — satu kali per weight source. `multi_weight_driver.py` **TIDAK** memanggil `features.py` — cukup memastikan seluruh `.sfdir` tersedia sebelum driver existing dijalankan. Ini konsisten dengan PRD §8.1 koreksi (Spec §4.7).
  - **Plan v1.6:** Implemented — TASK-0.7 (driver TIDAK memanggil `features.py`)
- ✅ **Assumption:** *Build source assembly* (`build/sources/`) dapat di-generate oleh `multi_weight_driver.py` di Stage 1 sebelum `custom_build_driver.py` existing dijalankan.
  - **Validation:** **TERKONFIRMASI** oleh Spec §4.6 (REQ-B06) dan §4.9 (Dockerfile RUN kondisional). Driver menyusun 4 harmonized masters + 2 core weights dengan nama `FantasqueSansMono-{Weight}.sfdir` + salinan `FantasqueSans.sfdir`, kemudian driver existing dipanggil dengan `SOURCES_DIR=build/sources`.
  - **Plan v1.6:** Implemented — TASK-0.7 (assembly `build/sources/`), TASK-4.2 (RUN chain `FONTS=build/sources`)

## 4. 📝 Next Steps

- ✅ **Implementation Plan** (`plan/plan-feature-multi-weight-variants-v1.3.md`) **HARUS** diperbarui untuk mencerminkan resolusi berikut:
  - ✅ TASK-3.1: Hanya menghasilkan **Core Weights** (Medium 500 + SemiBold 600); *stretch weights* ditangguhkan ke Phase 5 / *release upstream pipeline*.
  - ✅ TASK-3.2: **Dihapus** — `ttfautohint` manual tidak dilakukan; QA visual pra-*hinting* menggunakan *specimen sheet HTML*.
  - ✅ TASK-3.3, TASK-3.4, TASK-3.5, TASK-3.X: Diupdate untuk **hanya mencakup Core Weights** di fase ini.
  - ✅ GOAL-004: Diupdate dari "core & stretch weights" menjadi "core weights".
  - Dokumen ini **telah disesuaikan dan dipastikan** memenuhi seluruh resolusi di atas.
  - **Plan v1.6:** Implemented — seluruh sub-bullet diterapkan: TASK-3.1 (core-only), TASK-3.2 dihapus, TASK-3.3–3.4 & TASK-3.X (core-only), GOAL-004
- ✅ **Technical Specification** (`spec/spec-multi-weight-variants.md`) sudah konsisten — tidak perlu perubahan. Namun, plan perlu diselaraskan dengan Spec §4.6, §4.9, §4.10, §8.5, dan AC-B02.
  - **Plan v1.6:** Implemented — plan diselaraskan dengan Spec §4.6 (TASK-0.7/3.1/3.4), §4.9 (TASK-4.1–4.3), §4.10 (TASK-4.4), §8.5 (TASK-1.2/3.2/4.X), AC-B02 (TASK-4.2/4.4)
- ✅ **(N/A)** Jika istilah domain baru disepakati selama sesi ini, Agent harus menawarkan untuk membuat atau memperbarui Domain Glossary (melalui root `CONTEXT.md` atau `CONTEXT-MAP.md`).
  - *(Catatan Internal: Tidak ada definisi domain baru — semua istilah sudah didefinisikan di `CONTEXT.md` klaster Multi-Weight Variants.)*
- ✅ **(N/A)** Jika keputusan arsitektur baru yang (1) hard to reverse, (2) surprising, dan (3) real trade-off, Agent harus menawarkan untuk mendokumentasikan dalam ADR di `docs/adr/`.
  - *(Catatan Internal: Tidak ada keputusan arsitektur baru. Semua keputusan selaras dengan ADR-0002 dan ADR-0003 yang sudah ada.)*
