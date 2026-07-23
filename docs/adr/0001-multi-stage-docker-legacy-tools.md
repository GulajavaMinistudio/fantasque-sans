# 0001 - Multi-Stage Docker Build untuk Legacy Toolchain

**Date:** 2026-07-23  
**Status:** Accepted  

## Context
Pipeline build Fantasque Sans Mono (`Scripts/build.py`, `Scripts/fontbuilder.py`) ditulis dalam Python 2.7 dan memerlukan FontForge yang dikompilasi dengan dukungan Python 2.7. Kedua dependensi ini tidak tersedia di Ubuntu 24.04 LTS: DeadSnakes PPA tidak lagi membuild Python 2.7 untuk Ubuntu 22.04+ (memerlukan `libssl<3`), dan `ppa:fontforge/fontforge` tidak mendukung rilis setelah Eoan 19.10. Di sisi lain, V1 Custom Build memerlukan container berbasis Ubuntu 24.04 (atau 22.04) untuk keamanan dan dukungan jangka panjang — `ubuntu:18.04` sudah EOL sejak April 2023. Prinsip "Wrap, Don't Rewrite" melarang modifikasi atau rewrite pipeline build yang sudah ada.

## Decision
Menggunakan strategi **multi-stage Docker build**: Stage 1 (`ubuntu:18.04` + `ppa:fontforge/fontforge`) menyediakan binary Python 2.7 dan FontForge (dengan dukungan Python 2.7). Stage 2 (`ubuntu:24.04`) menyalin binary tersebut beserta library dependencies-nya, dan berfungsi sebagai container final tempat build berjalan. Tool modern lainnya (`ttfautohint`, `sfnt2woff`, `woff2_compress`) diinstal langsung dari repository Ubuntu 24.04 universe.

## Consequences
- **Positif**: Pipeline build existing tidak disentuh sama sekali — mematuhi "Wrap, Don't Rewrite" sepenuhnya. Container final berjalan di Ubuntu 24.04 yang masih menerima security patch hingga 2029.
- **Negatif**: Dockerfile menjadi lebih kompleks (dua stage, penyalinan binary manual). Binary compatibility Python 2.7 dan FontForge lintas versi glibc (2.27 → 2.39) perlu diverifikasi dan berpotensi menimbulkan masalah runtime yang sulit didebug. Jika GitHub Actions suatu saat men-drop dukungan untuk container `ubuntu:18.04`, Stage 1 harus diganti dengan mekanisme alternatif.
- **Risiko jangka panjang**: Ini adalah solusi taktis, bukan strategis. Pipeline build suatu saat harus dimigrasikan ke Python 3 — ketika itu terjadi, ADR ini menjadi usang dan multi-stage build bisa dihilangkan.

## Considered Options
- **Rewrite build scripts ke Python 3**: Ditolak karena melanggar "Wrap, Don't Rewrite" secara fundamental dan memerlukan verifikasi penuh terhadap output font (reproduksibilitas, kompatibilitas FontForge Python 3 API).
- **Turun ke Ubuntu 22.04 + repo focal**: Ditolak karena mixing repository Ubuntu berbeda versi berisiko menimbulkan konflik dependensi yang sulit di-maintain, dan tidak menyelesaikan masalah Python 2.7 (tetap tidak tersedia di 22.04).
- **Gunakan base image `python:2.7-slim` (Debian Buster)**: Ditolak karena mencampur ekosistem Debian dan Ubuntu dalam satu container meningkatkan risiko inkompatibilitas library, dan Debian Buster juga sudah EOL.
