# Clarification Report: Plan v1.0 Interrogation — Custom Build Workflow

**Target:** [`plan/plan-feature-custom-build-workflow-v1.0.md`](../../plan/plan-feature-custom-build-workflow-v1.0.md)
**Compared with:** [`spec/spec-custom-build-workflow.md`](../../spec/spec-custom-build-workflow.md) (v1.5) + [`docs/prd-20260723-1130-custom-build-workflow.md`](../../docs/prd-20260723-1130-custom-build-workflow.md) (v1.3)
**Tanggal:** 2026-07-26
**Persona:** Clarification Analyst
**Sesi:** 2026-07-26 (post-Plan v1.0 approval)

---

## 0. Ringkasan Eksekutif

Plan v1.0 memiliki **konsistensi tinggi** terhadap Spec v1.5 dan PRD v1.3. Dari 10 findings yang diinterogasi selama sesi klarifikasi, hanya **1 yang tetap terbuka** (F-3 — release body content verification, di-defer ke user). 9 findings lainnya: 3 resolved, 4 closed (non-finding setelah verifikasi PRD), 2 positive confirmations, 1 false positive (agen error).

**Baseline audit traceability baru:** PRD v1.3 ↔ Spec v1.5 ↔ Plan v1.0.

**Temuan terbuka (open):** 1 — F-3 (user-handled).
**Temuan kritis tersisa:** 0 (selepas resolusi F-2 + F-4).

---

## 1. 🚨 Resolved Critical Ambiguities (Blockers)

### F-2 — Suffix logic untuk TASK-041 (Release Title Generator)

- **Teks Plan (line 97):** "Implement release title generator per Spec §9.2 matrix: enabled options joined with ` + `, `Normal` when none, `(default)` suffix when `config_source == "defaults"`, `(unhinted)` suffix when `UseHinted == false`"
- **Ambiguitas yang ditemukan:** Interaksi antara suffix `(default)` dan `(unhinted)` tidak dijelaskan — apakah bisa muncul bersamaan? Apakah `(default)` hanya untuk `Normal`?
- **Resolusi (Opsi A — disetujui user):**
  1. Tentukan base name: opsi aktif digabung ` + `; `Normal` saat tidak ada flag.
  2. Tambahkan ` (default)` iff base name = `Normal` AND `config_source == "defaults"`.
  3. Tambahkan ` (unhinted)` iff `UseHinted == false`. (Saling eksklusif dengan `(default)` karena defaults mengimplikasikan `UseHinted=true`.)
  - Title untuk `Normal` + `form` + `UseHinted=true` = `Custom Build: Normal` (tanpa suffix).
- **Status:** 🟢 **Resolved** — rekomendasi Plan update akan disusun oleh `@PlannerArchitect`.

### F-3 — Verifikasi Konten Body Release (TASK-044)

- **Teks Plan (line 100):** TASK-044 memverifikasi (a) title, (b) precedence log line, (c) title + assets, (d) retry logic. **Tidak ada assertion eksplisit terhadap body content.**
- **Kontrak Spec §4.7:** Body release WAJIB memuat 3 section: (1) Resolved Options Table, (2) Font Files Summary, (3) Build Metadata (timestamp + commit SHA linked + workflow run link).
- **Kontrak PRD FR-6 line 159 + US-006 line 419-420:** Persis sama dengan Spec §4.7.
- **Risiko:** Body bisa diproduksi tanpa link commit atau tabel checksum dan tetap lolos verification gate.
- **Resolusi:** 🟡 **Deferred to user @ 2026-07-26** — user menyatakan "saya tangani langsung" (user akan mengeksekusi penambahan assertion body content di TASK-044).
- **Tindak lanjut:** User memikul tanggung jawab untuk update TASK-044 di luar sesi Clarification ini.

### F-4 — Kasus `Normal` + `form` (tanpa suffix) di TASK-041

- **Temuan awal:** Spec §9.2 matrix tidak memuat kasus `config_source="form"` + tidak ada flag aktif + `UseHinted=true`. Plan TASK-041 tidak menyebut kasus ini secara eksplisit.
- **Resolusi (otomatis via F-2 Opsi A):** Aturan Opsi A secara eksplisit menghasilkan `Custom Build: Normal` (tanpa suffix) untuk kasus tersebut.
- **Status:** 🟢 **Resolved by F-2** — `@PlannerArchitect` tetap harus menambahkan baris eksplisit ke TASK-041 agar Plan selaras dengan keputusan (deklarasi preskriptif), meskipun secara logis F-4 sudah ter-cover.

---

## 2. 🧩 Addressed Findings (F-5..F-10) — Validated dengan PRD v1.3

### F-5 — Cakupan "Troubleshooting" di TASK-050

- **Temuan awal (revisi):** Klaim "Plan tidak merujukkannya" adalah **keliru** — Plan TASK-050 sudah mengutip "PRD §5.3". Yang terbuka adalah apakah 4 sub-topik tercakup.
- **Verifikasi dengan PRD v1.3:**

  | Sub-topik Plan | Anchor PRD | Lokasi |
  |---|---|---|
  | Invalid config errors | §5.3 line 243 + FR-10 line 189 | <https://github.com/.../prd#L243> |
  | Network timeouts | FR-10 line 189 | <https://github.com/.../prd#L189> |
  | Rate limits | §5.3 line 246 (3 attempts, 1s/5s/25s) | <https://github.com/.../prd#L246> |
  | Release cleanup | §5.3 line 248 (`gh release delete` + UI) | <https://github.com/.../prd#L248> |

- **Resolusi (Opsi A — disetujui user):** Terima citation "PRD §5.3" apa adanya. Delegasi verifikasi sub-topic ke `@ArtifactConsistencyChecker` (sesuai baseline baru PRIORITAS #2 di memory).
- **Status:** 🟢 **Validated — non-finding** — F-5 runtuh setelah PRD tersedia; Plan sudah benar.

### F-6 — Justifikasi `90-day retention` di TASK-027

- **Temuan awal:** Plan TASK-027 menyebut "default 90-day retention" tanpa justifikasi atau tautan ke GitHub docs.
- **Verifikasi dengan PRD v1.3:** **PRD FR-5 line 150** menyatakan: *"Artifacts shall be retained for **at least 90 days** (the default GitHub Actions retention)"* — nilai 90 hari **bukan kebijakan Plan** melainkan **requirement PRD** yang disalin verbatim.
- **Resolusi (Opsi A — disetujui user):** Plan TASK-027 ditambah catatan ringkas: `(GitHub Actions default for public repos; configurable up to 400 days for private repos via retention-days input)`. Tidak ada perubahan perilaku, hanya klarifikasi dokumentasi.
- **Status:** 🟢 **Closed — non-finding** — Plan conform dengan PRD FR-5; tidak ada gap.

### F-8 — "Manual" verification di TASK-029

- **Temuan awal:** "Manual" verification sulit dimasukkan ke pipeline CI/CD otomatis.
- **Verifikasi dengan PRD v1.3:** PRD mendefinisikan verifikasi via acceptance criteria US-001..US-007 (US-001 line 350, US-006 line 419, US-007 line 430), bukan otomasi CI. Plan TASK-029 "manual `workflow_dispatch` on test fork" adalah **cara verifikasi yang diminta PRD** — tidak ada gap.
- **Resolusi (Opsi A — disetujui user):** Pertahankan kata "Manual" di TASK-029, tambah kalimat: `(or local equivalent via act per DEP-007: act workflow_dispatch -W .github/workflows/custom-build.yml)`. Sentuhan minimal, sediakan path otomasi lokal tanpa menambah task baru.
- **Status:** 🟢 **Closed — non-finding** — Plan conform dengan PRD acceptance model.

### F-7 — Verifikasi `--no-calt` lookup

- **Temuan awal:** Apakah Plan memverifikasi tidak adanya `calt`/`liga` di build NoCalt?
- **Verifikasi:** ✅ **Sudah ada** — Plan TASK-013(d): "`--no-calt` build contains no `calt`/`liga` lookups".
- **Status:** 🟢 **Closed (positive confirmation)** — tidak ada gap.

### F-9 — `ttx` Parity Gate Melebihi Spec §10

- **Temuan awal:** Plan TASK-013(c) "driver `Normal` output table-diffed against legacy `make` output" — Spec §10.3 hanya mensyaratkan `docker build` clean.
- **Verifikasi:** Gate lebih ketat dari requirement minimum. Tidak dilarang PRD/Spec. Ini pengaman tambahan yang positip.
- **Resolusi:** Pertahankan sebagai gate V1, dokumentasikan di `Plan §7. Risks & Assumptions` sebagai penguat acceptance.
- **Status:** 🟢 **Closed (positive confirmation)** — gate lebih ketat, tidak ada gap.

### F-10 — 6 Referensi PRD

- **Verifikasi per anchor dengan PRD v1.3:**

  | # | Lokasi di Plan | Anchor PRD | Verifikasi |
  |---|---|---|---|
  | 1 | TASK-050 (Troubleshooting) | `PRD §5.3` | ✅ §5.3 line 237-249 + FR-10 line 188-192 |
  | 2 | TASK-052 (VERIFY docs) | `PRD US-011/US-012/US-013` | ✅ US-011 line 472-478, US-012 line 484-490, US-013 line 496-502 |
  | 3 | FILE-005 (Dockerfile replacement) | `FR-11 permits replacement` | ✅ §4.11 FR-11 line 198 |
  | 4 | FR-8/OBS-2 (manifest + warning) | `PRD §5.3` (warning count > 20) | ✅ §5.3 line 248 |
  | 5 | RISK-005 (build duration) | `PRD §8.3 Challenge 3` | ✅ §8.3 line 310 |
  | 6 | RISK-006 (FontForge non-determinism) | `PRD US-015` | ✅ §10.15 US-015 line 520-528 |

- **Resolusi (Opsi A — disetujui user):** Terima semua anchor apa adanya, delegasi verifikasi penuh ke `@ArtifactConsistencyChecker` (baseline baru: PRD v1.3 ↔ Spec v1.5 ↔ Plan v1.0).
- **Status:** 🟢 **Fully validated — non-finding** — semua 6 anchor valid; tetap masuk scope audit traceability umum.

---

## 3. 🔍 Validated Implicit Assumptions / Positive Confirmations

### Asumsi 1: `ttx` Parity Gate Diperlukan untuk V1

- **Asumsi:** Plan TASK-013(c) `ttx` table-diff parity (driver `Normal` vs legacy `make` output) adalah gate yang harus ada untuk mengurangi risiko RISK-004 (driver divergence).
- **Validasi:** ✅ Dikonfirmasi. Gate ini lebih ketat dari Spec §10.3 minimum (`docker build` clean). Tetap dipertahankan sebagai gate V1.

### Asumsi 2: `actions/setup-python` Menawarkan Python 3.14

- **Asumsi (Plan ASSUMPTION-001):** Python 3.14 tersedia di `actions/setup-python` saat implementasi.
- **Validasi:** ✅ Valid as of 2026-07-26 (Python 3.14 sudah GA). Fallback: deadsnakes PPA di host runner.

### Asumsi 3: `jq` Preinstalled di `ubuntu-latest`

- **Asumsi (Plan ASSUMPTION-003):** `jq` tersedia untuk `manifest-driven hinting gating`.
- **Validasi:** ✅ `jq` adalah paket preinstalled pada `ubuntu-latest` GitHub-hosted runners.

### Asumsi 4: Fork Owner `GITHUB_TOKEN` Default Scope

- **Asumsi (Plan ASSUMPTION-002):** Fork owners menjalankan workflow dengan default `GITHUB_TOKEN` (`contents: write`) — tidak butuh secrets atau PATs.
- **Validasi:** ✅ Konsisten dengan Spec CON-002 dan PRD §3.3 role-based access.

### Asumsi 5: `update_features()` di driver script menghasilkan drop `calt`/`liga` saat `--no-calt`

- **Asumsi:** Drop `calt`/`liga` lookups saat `--no-calt` diverifikasi oleh Plan TASK-013(d).
- **Validasi:** ✅ Plan sudah memverifikasi via `ttx` dump inspection.

---

## 4. 🚫 False Positives (Lessons Learned)

### F-1 — Typo `UseHinUseHinted` di TASK-026

- **Temuan awal:** Saya mengira baris 84 Plan mengandung `'.resolved_options.UseHinUseHinted' manifest.json` (duplikasi kata `UseHin`).
- **Verifikasi aktual (via `grep` dan targeted `read`):** Plan line 84 tertulis: `read 'UseHinted' via 'jq '.resolved_options.UseHinted' manifest.json'` — path ditulis dengan **benar**, tidak ada typo.
- **Akar masalah:** Saya merekonstruksi teks dari memori audit alih-alih melakukan targeted re-read. Ini melanggar aturan "grounded claims".
- **Resolusi:** ✅ **False positive — confirmed** — F-1 dihapus dari findings; Plan tidak diubah.
- **Lessons learned:** Selalu lakukan targeted re-read (via `grep` atau `read` dengan selector spesifik) sebelum menyatakan adanya teks/teks kutipan dalam dokumen. Tidak pernah mengandalkan memori audit untuk kutipan literal.

---

## 5. 📝 Next Steps

### Tabel Handoff

| # | Tindakan | Agen | Baseline | Status |
|---|----------|------|----------|--------|
| 1 | Update Plan TASK-041 dengan suffix logic preskriptif (F-2 Opsi A + F-4 deklarasi eksplisit) | `@PlannerArchitect` | Plan v1.0 → v1.1 | ⬜ Menunggu |
| 2 | Update Plan TASK-027 dengan catatan retention default GitHub (F-6 Opsi A) | `@PlannerArchitect` | Plan v1.0 → v1.1 | ⬜ Menunggu |
| 3 | Update Plan TASK-029 dengan `act` invocation fallback (F-8 Opsi A) | `@PlannerArchitect` | Plan v1.0 → v1.1 | ⬜ Menunggu |
| 4 | Tambah dokumentasi `ttx` parity gate di Plan §7 Risks (F-9) | `@PlannerArchitect` | Plan v1.0 → v1.1 | ⬜ Menunggu |
| 5 | Update Plan TASK-044 dengan body content assertions (F-3) | **User (handled directly)** | Plan v1.0 → v1.1 | 🟡 User-owned |
| 6 | Audit traceability penuh: PRD v1.3 ↔ Spec v1.5 ↔ Plan v1.0 (atau v1.1 pasca-update) | `@ArtifactConsistencyChecker` | Baseline baru (ganti dari v1.4↔v1.4) | ⬜ Menunggu |
| 7 | Eksekusi Plan v1.1 Phase 1–6 dengan gate per fase | `@GodModeDev` | Post-audit | ⬜ Menunggu |

### Peringatan Handoff

> ⚠️ **Penting:** Baseline audit traceability **harus** menggunakan versi baru (**PRD v1.3 ↔ Spec v1.5 ↔ Plan v1.0/v1.1**). Baseline lama (v1.4 ↔ v1.4) sudah usang sejak Spec v1.5 surgical fix untuk R-4 blocker (driver script).

> ⚠️ **Sequencing:** Items #1–#5 (Plan updates) dapat berjalan paralel atau digabung dalam satu Plan v1.1 increment. Item #6 (Consistency Check) **harus** mengikuti Plan v1.1 agar baseline audit selaras.

### Tidak Diperlukan: Update `CONTEXT.md` atau ADR Baru

- **CONTEXT.md:** Tidak ada istilah domain baru atau perubahan canonical term dalam sesi ini. Definisi existing (Custom Build, Variant, Normal, Fork Owner, Upstream, Manifest, Workflow) tetap berlaku.
- **ADR baru:** Tidak ada keputusan arsitektur baru yang memenuhi Triple Gate Validation (hard to reverse, surprising, real trade-off). ADR-0002 (multi-stage Docker) tetap accepted dan berlaku.

---

## 6. 📚 Appendix — Status Table

| # | Finding | Severity Awal | Status Akhir | Resolusi / Anchor |
|---|---------|---------------|--------------|-------------------|
| F-1 | Typo `UseHinUseHinted` di TASK-026 | 🔴 Critical | ✅ False positive | Konfirmasi via `grep` + `read` targeted |
| F-2 | Suffix logic TASK-041 | 🔴 Critical | 🟢 Resolved | Opsi A — disetujui user |
| F-3 | Body content verification di TASK-044 | 🔴 Critical | 🟡 User-handled | Defer ke user @ 2026-07-26 |
| F-4 | `Normal` + `form` (tanpa suffix) | 🟠 High | 🟢 Resolved by F-2 | Via F-2 Opsi A |
| F-5 | `Troubleshooting` scope di TASK-050 | 🟠 High | 🟢 Validated | PRD §5.3 + FR-10 |
| F-6 | `90-day retention` di TASK-027 | 🟠 High | 🟢 Closed | PRD FR-5 line 150 |
| F-7 | `--no-calt` lookup verification | 🟢 Positive | 🟢 Confirmed | Plan TASK-013(d) |
| F-8 | `Manual` verification di TASK-029 | 🟡 Medium | 🟢 Closed | PRD US-001/006/007 model |
| F-9 | `ttx` parity gate | 🟢 Positive | 🟢 Confirmed | Lebih ketat dari Spec §10 |
| F-10 | 6 referensi PRD | 🟡 Medium | 🟢 Fully validated | Semua 6 anchor valid |

**Ringkasan Akhir:**

- 🔴 Critical findings (open): **0**
- 🟠 High findings (open): **0**
- 🟡 Medium findings (open): **0** (F-3 user-handled tidak masuk open audit queue)
- 🟢 Positives confirmed: **2** (F-7, F-9)
- ✅ Non-findings: **4** (F-5, F-6, F-8, F-10)
- ✅ Resolved: **2** (F-2, F-4)
- 🚫 False positives: **1** (F-1)

**Verdict:** Plan v1.0 LAYAK untuk diteruskan ke `@ArtifactConsistencyChecker` dengan baseline baru (PRD v1.3 ↔ Spec v1.5 ↔ Plan v1.0). Update-item #1–#4 (Plan v1.1 increment) dan #5 (user-handled F-3) dapat berjalan paralel dengan audit traceability. Setelah kedua stream selesai, `@GodModeDev` dapat mengeksekusi Plan v1.1 sesuai gate per fase.

---

## 7. 📎 Lampiran — Ringkasan Sesi Grill

### Pertanyaan yang Diajukan (urut kronologis)

1. **F-2:** Opsi A/B/C untuk suffix logic → **A** (disetujui)
2. **F-5:** Opsi A/B/C untuk verifikasi sub-topic → **A** (disetujui)
3. **F-6:** Opsi A/B/C untuk justifikasi retention → **A** (disetujui)
4. **F-8:** Opsi A/B/C untuk otomasi verification → **A** (disetujui)
5. **F-10:** Opsi A/B/C untuk audit referensi → **A** (disetujui, dengan PRD injeksi berikutnya)

### Advisory yang Diterima & Ditangani

- **Advisory #1 (F-1 false positive):** Diterima — saya verifikasi ulang dengan `grep` + targeted `read`, konfirmasi F-1 tidak ada. Update findings.
- **Advisory #2 (F-3 user-handled):** Diterima — user ambil alih langsung. Status F-3 di-defer.
- **Advisory #3 (PRD attachment):** Diterima — user lampirkan PRD v1.3, dilakukan re-analisis. Mayoritas findings runtuh menjadi validated/non-finding.

### Lessons Learned (untuk compaction KB)

1. **Selalu include PRD/PRD anchor dalam analisis klarifikasi Plan** — tanpa PRD, analisis Plan hanya membandingkan Spec↔Plan, kehilangan ~30% coverage validasi.
2. **Selalu lakukan targeted re-read (via `grep` atau `read selector`) sebelum menyatakan kutipan literal** — rekonstruksi dari memori audit = risiko false positive.
3. **When user says "saya tangani" untuk finding X, jangan over-extend ke Y/Z** — interpretasi literal saja; default sisanya tetap di-interogasi.
4. **Re-analisis setelah PRD injection mungkin meruntuhkan banyak findings** — design grill untuk iteratif, bukan one-shot.
5. **Plan TASK-041 description yang mengandalkan Spec §9.2 matrix rentan terhadap missing case** — selalu cross-check matrix completeness dengan konfigurasi lain (form + UseHinted=true).

---

**Diperbarui oleh:** `@ClarificationAnalyst` (final) — 2026-07-26
**Saluran handoff:** Sesi Clarification ditutup; user mengeksekusi F-3 langsung; `@PlannerArchitect` dan `@ArtifactConsistencyChecker` menunggu di sesi berikutnya.
