# Project Memory Log

> Active Location: `.agents/instructions/memory.instructions.md`
> This file is managed by the `memory-manager` skill.
> It persists context across AI chat sessions to prevent knowledge loss.
> Do NOT manually edit this file unless necessary.

---

## 🧠 Knowledge Base

> This section accumulates cross-session knowledge that must survive compaction.
> Compaction history:
> - 2026-07-24: Sessions 1–8 compacted; Dead-End #4 promoted. Only Session 9 (Plan v1.0) retained.
> - 2026-07-26: Session 2026-07-24 (Plan v1.0) compacted after re-audit cycle completion. Promoted: Re-audit Pattern, Single Audit Report Pattern, Delta Verification Pattern, Plan File Rename+Version Bump Protocol, User Override Priority. Retained: 2026-07-26 (Plan v1.0 Clarification), 2026-07-26 (Consistency Audit), 2026-07-26 (Re-Audit PASS Clean).
> - 2026-07-29: Session 2026-07-26 (Plan v1.0 Clarification) + 2026-07-24 (Plan v1.0 one-liner) compacted after Plan v1.2 Section 9 addition. Promoted: 4 Clarification methodology patterns (PRD anchor inclusion, targeted re-read, iterative re-analysis, literal scope adherence). Retained: 2026-07-26 (Consistency Audit), 2026-07-26 (Re-Audit PASS Clean), 2026-07-29 (Section 9 Added).
> - 2026-07-30: Direct additions to KB (no compaction this session — entries are stable, project-validated). Added: DE #6 (apt→pip fallback for shim packages), DE #7 (read-only mount vs script writeback). Added KB patterns: Cross-tool Escape Hierarchy (bash vs jq backtick handling), Defense-in-Depth vs Script Intent in Docker Mounts. Updated DE #5 "Correct Solution" to reflect `pip3 install future` pattern (replaces obsolete `python3-future` apt install). All additions are project-validated through successful end-to-end CI build.
> - 2026-07-30 (Compaction Pass): 5 old checkpoints compacted (2026-07-26 ×2, 2026-07-29 ×3). Retained 2 most recent: 2026-07-30 (First CI Run Failures) + 2026-07-30 (Build SUCCESS). Updated KB pattern "Multi-Stage Docker with Deferred Engine Port (ADR-0002)" to reflect current Stage 1 (`ubuntu:26.04` + Python 3.x) instead of outdated `ubuntu:18.04` + Python 2.7. Populated empty `Key Metrics & Baselines` section. No KB knowledge deleted (all 7 DEs + 25 patterns still project-relevant).
> - 2026-07-30 (Plan-Refactor Compaction): Checkpoint A "First CI Run Failures" compacted (subsumed by Checkpoint B). Promoted: DE #8 (no-op retry fix), 3 KB patterns (Doc Sync Scope Enumeration, Plan-as-Record after Execution, Code Review Remediation Triplet). Retained: Checkpoint B (Build SUCCESS) + new Checkpoint C (Plan-Refactor Execution — 16 tasks, 3 phases, all complete).
> - 2026-07-31 (Spec Multi-Weight Compaction): Sessions 2026-07-30 (Code Phase Debugging) + 2026-07-30 (Plan-Refactor Execution) compacted after Spec v1.3 verification (feature Custom Build fully closed in KB). Promoted: 5 KB patterns (ADR Triple-Gate Filtering, Manual Atomic Commit per Iteration, PoC Failure Path Pattern, Self-Review Diminishing Returns, Glossary-After-Doc Propagation) + DE #9 (container-only tool in host runner workflow step). Retained: 2026-07-31 (PRD v1.1), 2026-07-31 (Spec Audit v1.1), NEW 2026-07-31 (Spec v1.3).
> - 2026-07-31 (Plan v1.6 Sync Compaction): 2 checkpoints compacted (2026-07-31 PRD v1.1, 2026-07-31 Spec Audit v1.1) — keduanya usang: PRD & Spec kini v1.3, temuan audit sudah terintegrasi & tercakup di checkpoint Spec v1.3 + KB. Promoted: 2 KB patterns (Plan-Clarification Sync Pattern, markdownlint-disable Convention for Plan/Audit Docs). Retained: 2026-07-31 (Spec v1.3) + NEW 2026-07-31 (Plan v1.6).
> - 2026-08-01 (Compaction): Session 2026-07-31 (Spec v1.3 verification) compacted — knowledge inti sudah ter-promote di kompaksi 2026-07-31 (DE #9, metric spec v1.3, flag forwarding pattern). Promoted baru: 2 KB patterns (External Edit Detection via mtime, Spec Final Verification Multi-Criteria). Retained: 2026-07-31 (Plan v1.6) + 2026-08-01 (Plan v1.7).
> - 2026-08-01 (Compaction): Checkpoint "Consistency Audit (FAIL)" compacted — pengetahuan subsumed oleh Klarifikasi r4 + Plan v1.10 (15/15 cek PASS). Promoted: Tri-Directional Consistency Audit Pattern, Audit Result State Machine, DE #10 (dangling audit_reference). Retained: Klarifikasi r4 (5/5 resolusi) + Plan v1.10 (FINAL).
> - 2026-08-01 (r5 Compaction): Checkpoint "Klarifikasi r4" compacted — 5 resolusi R1–R5 sudah terserap penuh ke Plan v1.10 + Spec v1.6 (diverifikasi r5) dan terdokumentasi permanen di laporan r4. Promoted: DE #11 (pytest system python3 ≠ FontForge bindings — importorskip silent skip). Retained: Plan v1.10 (FINAL) + Klarifikasi r5 (2 most recent).
> - 2026-08-05 (Code Phase Compaction): Sessions 2026-08-01 ×3 + 2026-08-05 (TASK-1.1, Phase 2, Phase 3) compacted after Phase 4 Pipeline completion. Promoted: DE #12 (selfIntersects method vs property), DE #13 (centroid-only contour matching → area-rank), DE #14 (pathlib absolute wins), KB patterns: NOTE-row Insertion, Engine Tuple Arity. Retained: Phase 3 CLOSED + Phase 4 Pipeline.
> Updated during Compaction Mode (Workflow 4). Do NOT delete entries here.

### Architecture & Patterns

- **Agent ↔ Skill Separation of Concerns**: Agent files define persona, scope, and rules; Skill files define workflows and templates. Agents delegate execution to skills. [Source: Session 2026-06-03, still valid]
- **Ecosystem Synchronization**: `.opencode/` is the Master Source of Truth; mirrored/adapted into `.agents/` (Antigravity) and `.github/` (Copilot) for native IDE compatibility. [Source: Session 2026-06-03, still valid]
- **SDLC Phase Gates**: Strict sequential phases (Discovery → PRD → Clarification → Spec → Clarification → Consistency → Plan → Clarification → Code → Review → Docs). Each phase requires a new chat session (Strict Session Isolation). [Source: AGENTS.md institutionalized]
- **Custom Build — configure.py on Host Runner**: `configure.py` (Python 3.14) runs on GitHub Actions host runner, not inside Docker. Passes resolved build args to Stage 1 via `docker build --build-arg BUILD_ARGS`. Stage 2 (Ubuntu 26.04 + Python 3.14) handles post-build packaging tooling only. [Source: Spec v1.4 §1.2/§4.4/§4.5/§7, ADR-0002 revision]
- **Config Precedence**: `workflow_dispatch` form input > `config.json` > build defaults. `config_source` taxonomy: `defaults` | `config.json` | `form` | `form_override`. Naming: snake_case (form), PascalCase (config.json). [Source: PRD v1.3 FR-3/FR-8, Spec v1.4 §9.1]
- **Multi-Stage Docker with Deferred Engine Port (ADR-0002)** *(updated 2026-07-30)*: Stage 1 (`ubuntu:26.04` + Python 3.x + FontForge from default repos) runs legacy `build.py`/`fontbuilder`/`features` in-process via `fontforge -lang=py -script`. Stage 2 (`ubuntu:26.04` + Python 3.14) handles post-build packaging tooling only. Engine port (replacing Python 2.7 `xrange` etc. with native Py3) deferred to V2 because `build.py` imports both in-process (`from fontbuilder import *`) and CON-001 forbids modifying legacy files. The `future` Py2/3 shim package is installed via `pip3 install --break-system-packages future` (apt's `python3-future` removed from Ubuntu 26.04 repos — see DE #6). [Source: ADR-0002, Spec v1.4 §7, session 2026-07-30 CI run]
- **Bilingual Glossary Convention**: English `_Avoid_` lists in `CONTEXT.md` govern English-language documents (PRD, Spec, ADR body). Indonesian canonical terms are authoritative for Indonesian-language content. Cross-check both language surfaces during audits. [Source: Re-Audit r2, 2026-07-24]
- **Terminology Fix Propagation**: `_Avoid_` violations are contagious across SDLC artifacts. Fixing one document requires checking PRD, Spec, and CONTEXT.md together, plus updating audit reports with resolution logs. The same forbidden synonyms apply globally. [Source: Sessions 2026-07-24 Terminology Revisions]
- **Re-audit Pattern (After-Finding-Closure)**: When a finding is closed via document update (e.g., Plan v1.1 → v1.2), always perform a re-audit before approving the next SDLC phase. Re-audit focuses on: (1) deltas verification, (2) no-regression check, (3) section alignment (e.g., RISK-006 mitigation ↔ TASK-010 owner). Result: PASS bersih (tanpa "WITH WARNINGS") gives cleaner gate to next phase. [Source: Session 2026-07-26, still valid]
- **Single Audit Report Pattern**: For re-audits, update the original audit file in-place (add new section, renumber subsequent sections) rather than creating a new file. Preserves audit trail continuity; subsequent readers see both initial audit and re-audit in chronological order. [Source: Session 2026-07-26, still valid]
- **Delta Verification Pattern (Version-Increment Audit)**: For audit on Plan v1.X → v1.Y, focus on three things: (1) **Deltas** — verify every promised change is actually applied (frontmatter version, filename rename, task description expansion, Ref ID update); (2) **No-Regression** — verify sections NOT updated (e.g., §3 Alternatives, §4 Dependencies, §7 Risks) remain identical; (3) **Cross-Section Alignment** — e.g., RISK-006 mitigation text must match with the TASK that now owns the action. [Source: Session 2026-07-26, still valid]
- **Plan File Rename+Version Bump Protocol**: When user chooses "formal Plan update" option (e.g., FINDING-001 closure via v1.1 → v1.2), not enough to just edit file contents — must also: (1) rename file from `*-v1.1.md` to `*-v1.2.md`, (2) bump `version:` in frontmatter, (3) verify filename ↔ frontmatter version consistency. Failure to rename = file version mismatch that confuses next auditor. [Source: Session 2026-07-26, still valid]
- **User Override Priority (AGENTS.md Rule #1)**: Explicit user command overrides role boundaries. Example: `@ArtifactConsistencyChecker` normally cannot edit Plan documents, but user choice "Update Plan v1.1 secara formal (Opsi A1)" overrides that rule. Always confirm via ask_user_question before performing override. [Source: Session 2026-07-26, still valid]
- **PRD Anchor Inclusion in Clarification**: Always include PRD/PRD anchor in Plan/Spec clarification analysis — tanpa PRD, coverage validasi turun ~30%. Re-analysis after PRD injection may collapse many findings. [Source: Session 2026-07-26 Clarification, still valid]
- **Targeted Re-Read Before Literal Citation**: Always targeted re-read (via `grep` atau `read` selector) before literal citation — rekonstruksi dari memori audit = risiko false positive. [Source: Session 2026-07-26 Clarification, still valid]
- **Iterative Re-Analysis Pattern**: When new context (e.g., PRD injection) arrives mid-session, re-analyze prior findings — design grill untuk iteratif, bukan one-shot. Many findings may collapse on re-analysis. [Source: Session 2026-07-26 Clarification, still valid]
- **Literal Scope Adherence ("Saya tangani")**: When user says "saya tangani" or similar deferral, take it literally for the mentioned item only — jangan over-extend ke findings berikutnya saat user defer satu finding tertentu. [Source: Session 2026-07-26 Clarification, still valid]
- **Build Debug Iteration Hierarchy**: When Docker build fails, fix in order: (1) syntax coercion (YAML booleans, Dockerfile backslash+comment), (2) missing dependencies (`python-future`, etc.), (3) version mismatches (Python 2.7 vs 3.x), (4) environment changes (base image, language runtime). Iterate and verify each fix before escalating. [Source: Session 2026-07-30, first CI run]
- **YAML `on:` Boolean Coercion Gotcha**: In YAML 1.1, bareword `on` is parsed as boolean `True`. Many parsers (PyYAML) store under `True` key. GitHub Actions parser is generally lenient but quoting (`"on":`) is best practice for cross-tool compatibility. [Source: Session 2026-07-30]
- **Dockerfile Backslash Line Continuation Rules**: A backslash `\` must be IMMEDIATELY followed by a newline to be a line continuation. Any content between `\` and newline (including spaces or `# comment`) makes `\` a literal backslash, breaking the multi-line instruction and causing "Unknown instruction" errors for the next line. [Source: Session 2026-07-30]
- **CRLF in Dockerfiles on Windows**: Windows edit tools (and Git `core.autocrlf=true`) can convert LF to CRLF. CRLF in Dockerfiles is usually fine for Docker on Linux, but hadolint may warn. Always normalize to LF for cross-platform consistency. [Source: Session 2026-07-30]
- **Node.js 20 Deprecation in GitHub Actions**: As of late 2025, GitHub deprecated Node.js 20 on Actions runners. Actions `actions/checkout@v4` and `actions/setup-python@v5` (and other @v4/v5 actions) are being forced to Node.js 24 via shim, generating warnings. Upgrade: `actions/checkout@v7`, `actions/setup-python@v6+`. Always check action versions against Node.js target. [Source: Session 2026-07-30]
- **Legacy Python 2/3 Shim Package Deprecation**: The `future` package (which provides `past.builtins` for Py2/3 compat shims like `from past.builtins import xrange`) is no longer in Ubuntu 26.04 main repos (`python3-future` was removed). When migrating legacy code to modern Ubuntu, apt-installable shim packages are increasingly unavailable. **Fix pattern**: Install via `pip` instead of `apt`, using `python3-pip` (apt) as bootstrap. Use `--break-system-packages` for PEP 668 compliance (Ubuntu 24.04+) and `--no-cache-dir` to keep image small. Example: `pip3 install --break-system-packages --no-cache-dir future`. [Source: Session 2026-07-30, third Dockerfile iteration]
- **Cross-tool Escape Hierarchy (bash → jq/yq)**: When passing strings to subprocesses like `jq`, `yq`, `python -c`, etc., be aware of escape context. **In bash DOUBLE-quoted strings** (`"..."`): backtick `` ` `` triggers command substitution → escape with `` \` ``. **In bash SINGLE-quoted strings** (`'...'`): backtick is literal (no escape needed). **In jq/yq strings** (inside bash single-quotes): backtick is also literal (no escape needed). The pattern `` \`\(.field)\` `` in a single-quoted bash → jq context is a **copy-paste mistake** from bash double-quoted context. **Valid escapes inside jq double-quoted strings**: `\\`, `\"`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`, `\uXXXX`. Rule of thumb: escape sequence belongs to the tool that is **currently parsing** the string; when switching contexts (bash → jq), backslash escapes from the previous context often become invalid literals in the new context. [Source: Session 2026-07-30, release notes generation step]
- **Defense-in-Depth vs Script Intent in Docker Volume Mounts**: When a CI workflow mounts a file with `:ro` (read-only) but a script in the container is designed to write back to that path, the build fails with `Read-only file system`. The defensive `:ro` conflicts with the script's clear design intent. **Decision framework**: (1) If the script's writeback is legitimate (e.g., updating an artifact in place), **remove `:ro`** — defense-in-depth should not block trusted code. (2) If the writeback is accidental or a refactor opportunity, **change the mount path or script target**. (3) If neither is acceptable, **use a separate writable mount** for the writeback target. Generalization: when mounting volumes in CI/Docker, audit each mount against the trusted code's intent. Mismatches are a common source of "works locally, fails in CI" bugs. [Source: Session 2026-07-30, packaging step read-only filesystem error]
- **Doc Sync Scope Enumeration (CR-F2 lesson)**: When CI debugging forces environment deviation, the doc sync must enumerate ALL affected sections, not just the obvious ones. Use `grep` (e.g., `grep -in "python2.7\|ubuntu:18.04"` across all relevant docs) to enumerate the actual surface area, not relying on the original finding's stated scope. For this project, the v1.0 plan said "Spec §4.5 only" but actual env drift required syncing 7 Spec sections (`REQ-004`, §1.1, §1.2, §4.4, §4.5, §7, §8.2) + ADR-0002 + 5 PRD sections + ARCHITECTURE.md. **Lesson**: fix scope must match actual drift surface, not assumed drift surface. [Source: Session 2026-07-30, plan-refactor-code-review TASK-103..TASK-106]
- **Plan-as-Record after Execution**: After executing a refactor plan, update the plan file itself to reflect the actual state: (1) frontmatter status `Draft → Complete`, (2) version bump (e.g., 1.1 → 1.2), (3) date column on every task row, (4) revision note in Introduction footer, (5) `## 6. Execution Results` section. The plan becomes the historical record of work, not just the work instruction — future readers see both the plan and its execution outcomes in one document. [Source: Session 2026-07-30, plan-refactor-code-review closure]
- **Code Review Remediation Triplet**: When code review surfaces env drift caused by CI debugging, address all three: (1) **Env sync** (Dockerfile, `.dockerignore`, base images), (2) **Code fixes** (workflow retry, version constants, stale comments), (3) **Doc sync** (plan, spec, ADR, PRD, ARCH). Missing any one = incomplete remediation. The triplet reflects the surface area that drift can affect: runtime config, code-level constants, and human-readable documentation. [Source: Session 2026-07-30, plan-refactor-code-review scope]
- **ADR Triple-Gate Filtering**: Jangan buat ADR untuk perubahan non-arsitektural (env migration, retry strategy, version constants, `.dockerignore`). Jika keputusan tidak memenuhi triple-gate (hard to reverse / surprising / real trade-off), dokumentasikan cukup sebagai Non-ADR resolution di Spec §8.5. Superseded ADRs tidak pernah dihapus — dipertahankan untuk konteks historis. [Source: Session 2026-07-30 plan-refactor; reaffirmed 2026-07-31]
- **Manual Atomic Commit per Iteration (user preference)**: User melakukan commit manual per perbaikan/iterasi (satu commit per fix, pesan deskriptif) — memberikan traceability perbaikan ke error spesifik. Jangan batch-commit banyak fix tanpa pemisahan. [Source: Session 2026-07-30 code debugging, user workflow]
- **PoC Failure Path Pattern**: Setiap definisi kriteria LULUS untuk PoC/eksperimen WAJIB disertai jalur GAGAL eksplisit (≥3 opsi: iterasi subset, revisi cakupan, re-evaluasi tooling, penundaan). Gate check tanpa jalur gagal = proyek bisa stuck. [Source: Session 2026-07-31 PRD, FR-2.5]
- **Self-Review Diminishing Returns**: Tren temuan per ronde self-review (9→6→8→1) adalah sinyal stabilisasi. Setelah ronde ke-3/4, hentikan self-review persona yang sama dan hand off ke checkpoint khusus (`/sdlc-clarify-reqs`) — melanjutkan berisiko temuan buatan/over-editing. [Source: Session 2026-07-31 PRD, 4 ronde self-review]
- **Glossary-After-Doc Propagation**: Ketika istilah glosarium dibuat SETELAH dokumen utama selesai, jalankan scan `_Avoid_` terhadap dokumen di sesi yang sama dan perbaiki semua pelanggaran — mencegah temuan audit downstream. [Source: Session 2026-07-31 PRD, 6 fix terminologi]
- **Plan-Clarification Sync Pattern**: Setelah plan diperbarui berdasarkan laporan klarifikasi, tandai SETIAP item resolusi di laporan dengan ✅ + baris referensi lokasi implementasi ("Plan v1.x: Implemented — TASK-y.z") + header status di atas dokumen. Menutup loop traceability dua arah: laporan → task di plan, dan plan → laporan. Item yang tidak memerlukan aksi ditandai "✅ (N/A)" dengan alasan. [Source: Session 2026-07-31, plan v1.6 sync]
- **markdownlint-disable Convention for Plan/Audit Docs**: Dokumen plan (`plan/*.md`) dan laporan audit (`docs/audit/*.md`) dengan tabel task lebar / paragraf panjang memakai `<!-- markdownlint-disable -->` (setelah frontmatter/judul) — konvensi repo yang dipakai seluruh dokumen sejenis. Jangan memaksakan MD013/MD060 pada dokumen-dokumen ini; targetnya `markdownlint` exit 0 dengan directive. [Source: Session 2026-07-31, verifikasi konvensi repo]
- **External Edit Detection via mtime**: Saat bekerja pada dokumen yang mungkin diedit pihak lain (tools, maintainer, sesi paralel), cek mtime file untuk mendeteksi perubahan eksternal dan verifikasi ulang isinya sebelum mengklaim/melanjutkan — mencegah salah klaim kepemilikan konten dan melewatkan konten baru. [Source: Session 2026-07-31, Spec v1.3 verification — tambahan eksternal mtime 17:53]
- **Spec Final Verification Multi-Criteria**: Finalisasi spec diverifikasi dengan kombinasi kriteria: markdownlint 0 issues, keseimbangan code fence (62/62), cakupan traceability 100%, pemeriksaan link referensi (9/9), dan verifikasi faktual terhadap source code aktual (bukan dari memori). [Source: Session 2026-07-31, Spec v1.3 verification pass]
- **Runtime Signal Delivery Verification**: Sebelum menulis mode switch (env var / flag) pada script yang dipanggil container via `docker run` atau job CI, SELALU verifikasi mekanisme penyampaian sinyalnya di workflow aktual — env var yang tidak pernah di-`-e` dan tidak dibaca dari manifest via `jq` menghasilkan cabang yang tidak pernah aktif (silent fallback ke mode default tanpa error). Pola aman: sinyal yang berasal dari host ditulis ke manifest (`jq -r '.resolved_options.X'` — pola `UseHinted`), atau env var eksplisit di-invoke manual dengan guard `_die` jika kosong. [Source: Session 2026-08-01, klarifikasi r4 R1 — cabang `ENABLE_MULTI_WEIGHT` packaging unreachable di CI]
- **Tri-Directional Consistency Audit Pattern:** Audit konsistensi cross-document WAJIB mencakup PRD ↔ Spec ↔ Plan secara simultan (bukan satu per satu). Audit juga harus mencakup codebase reality check (verifikasi langsung ke file sumber) dan ADR triple-gate. Hasil ada 3 tingkat: PASS (→ buka gerbang /sdlc-write-code), PASS WITH WARNINGS (→ re-audit), FAIL (→ hard halt, semua amendemen upstream harus selesai dulu). Hanya PASS membuka gerbang — bukan PASS WITH WARNINGS. [Source: Session 2026-08-01, still valid]
- **Audit Result State Machine:** Hasil audit konsistensi mengikuti state machine ketat: PASS / PASS WITH WARNINGS / FAIL. "PASS" adalah satu-satunya state yang membuka gerbang ke /sdlc-write-code. "PASS WITH WARNINGS" ≠ "PASS" — sama seperti FAIL, membutuhkan re-audit penuh hingga mencapai PASS bersih. Jangan pernah lanjut ke fase berikutnya pada PASS WITH WARNINGS. [Source: Session 2026-08-01, still valid]
- **NOTE-row Insertion for Long Truncated Table Cells:** Saat menyisipkan NOTE-row ke dalam tabel task plan yang memiliki sel sangat panjang (>768 karakter), jangan mereproduksi baris panjang tersebut sebagai anchor — gunakan anchor unik pendek (misalnya `PUT >N:`) yang hanya muncul di baris target. Anchor panjang rentan gagal matching dan menyebabkan seluruh edit ditolak. [Source: Session 2026-08-01, Plan v1.11]
- **Engine Tuple Arity Preservation:** Fungsi parser internal (seperti `resolve_glyph`) yang mengembalikan tuple harus mempertahankan jumlah elemen (arity) yang konsisten di seluruh call site. Jika satu call site meng-drop elemen (misalnya dari 3-tuple menjadi 2-tuple), downstream unpacking akan menghasilkan `IndexError` atau `ValueError` yang sulit dilacak karena jauh dari sumber bug. [Source: Session 2026-08-05, Phase 2 Full Harmonization — harmonize_engine.py]

### Dead-Ends (Do NOT Repeat)

| # | Attempted | Why It Failed | Correct Solution |
|---|-----------|---------------|------------------|
| 1 | Include spacing presets in V1 | `Scripts/build.py` spacing block fully commented out — not production-ready | Defer spacing to V2 |
| 2 | Run `configure.py` inside Stage 2 Docker container | Stage 1 needs resolved args before container build (chicken-and-egg) | Run `configure.py` on host runner; pass args via `docker build --build-arg` |
| 3 | Batch `edit` with multiple hunks in one call using stale snapshot tag | A stale tag on any hunk causes partial rejection — 5 of 9 hunks silently dropped | Always re-`read` for a fresh `#TAG` before sequential multi-hunk edits; never batch hunks across stale snapshots |
| 4 | Write Spec CLI contract against a code file without verifying its actual interface | Spec v1.4 §4.4 specified `--line-height`/`--no-loop-k`/`--no-calt` flags targeting `Scripts/build.py`, which accepts only 4 positional args (`<parallel> <batch> <sfdir> <output_dir>`), declares options via `option()`/`conflicting()` in the script body, and had the `NoCalt` declaration commented out. No CLI/env option-selection mechanism existed. CON-001 forbade modifying the file — contract was unimplementable. Blocked planning; found during codebase review. | Always verify actual code interfaces (sys.argv handling, function signatures, config mechanisms) before writing contracts against them. When the target cannot be modified, create a NEW wrapper/driver script that imports the legacy module primitives and implements the contract. |
| 5 | Use Ubuntu 18.04 + python-fontforge (Py2.7) for legacy fontforge script (also: assume `ppa:fontforge/fontforge` works on newer Ubuntu) | TWO related failure modes: (a) Ubuntu 18.04: `ppa:fontforge/fontforge` is not available; default 18.04 fontforge (1:20170731) has broken Python 3 `__getitem__` for `font['name']` — `font['space']` raises `TypeError: Index must be an integer or a string`. Even with `python-future` shim, the C-level bindings reject string indices in Python 3 runtime. (b) Ubuntu 26.04 ("resolute"): `ppa:fontforge/fontforge` 404s on `resolute` suite (PPA not maintained for the latest release). CON-001 forbids modifying `features.py` to work around either issue. | Use the **default Ubuntu repos** (not PPA) for the chosen base image. Modern fontforge binaries ship Python 3 bindings embedded, so `fontforge -lang=py -script` works without a separate `python3-fontforge` package. For Ubuntu 26.04, install: `ca-certificates fontforge python3-pip make` via apt, then `pip3 install --break-system-packages --no-cache-dir future` for the Py2/3 shim (see DE #6 for why apt's `python3-future` no longer works). Update Plan v1.2 §Phase 2 base image reference accordingly (v1.3 bump recommended). Lesson: when migrating to a new Ubuntu release, NEVER assume PPA support — always test with `apt-get update` first or use default distro packages. |
| 6 | Install `python3-future` via `apt-get install` on Ubuntu 26.04 | Package removed from Ubuntu 26.04 main repos (PEP 668 / minimalism trend). `apt-get install python3-future` returns `E: Unable to locate package python3-future`. The `future` package (which provides `past.builtins` for Py2/3 compat shims like `from past.builtins import xrange`) is no longer in distro repos. | For legacy Python 2/3 shim packages, bootstrap `python3-pip` via apt then install via pip: `pip3 install --break-system-packages --no-cache-dir <package>`. The `--break-system-packages` flag is required for PEP 668 compliance (Ubuntu 24.04+); `--no-cache-dir` keeps the image small. Lesson: as Ubuntu modernizes, apt-installable shim packages are increasingly unavailable — `pip install` is the de-facto fallback for legacy compat libs. |
| 7 | Mount source manifest as `:ro` in workflow but have packaging script write updated manifest back to same path | `:ro` mount rejects all writes; script fails with `Read-only file system` error. The defensive `:ro` conflicts with script's clear design intent (update manifest in place for archive step). Even if script's writeback is "questionable" (writing back to source is unusual), the script is trusted code in the same image — blocking it with `:ro` breaks the build. | Three options: (a) **Remove `:ro` flag** (chosen for this build) — trade defense-in-depth for clean build. Container can modify source manifest, but that's the script's design intent. (b) **Refactor script to use different filename** in /app/ (e.g., `manifest.built`) — more complex, breaks canonical `manifest.json` name in archive. (c) **Copy script's writeback target to OUTPUT_DIR first**, then have script write there — adds copy step, more IO. Generalization: when mounting volumes in CI/Docker, ensure mount permissions match the trusted code's intent. Defense-in-depth is good but should not block legitimate build behavior. |
| 8 | **No-op retry fix (v1.0 → v1.1 lesson)**: Add `3) delay=25 ;;` to a `case $attempt in ... esac` loop where the loop runs only when `attempt < max_attempts` with `max_attempts=3` | The case structure has only 2 delay slots; with 3 attempts (1 initial + 2 retries), only 2 delays (1s, 5s) are needed. The new `3) delay=25 ;;` case never executes because the loop terminates at attempt 3 before reaching the new branch. Initial fix was a no-op — the case structure was unchanged in behavior. | Bump `max_attempts` to match the new delay tiers — e.g., `max_attempts=4` (1 initial + 3 retries) for 1s/5s/25s delays. **General lesson**: when adding a new branch to a loop/case structure, verify the structure actually reaches the new branch — count `attempts × delays` and ensure they match. If they don't, the fix is a no-op. |
| 9 | Write workflow step examples that invoke container-only tools (e.g., `fontforge -lang=py -script`) directly on the GitHub Actions host runner | FontForge is only available inside the Stage 1 image (`builder-fontforge`) during `docker build`; host runner (Python 3.14 + jsonschema/pytest) and the final Stage 2 image (ttfautohint/woff-tools/woff2/zip/jq) do NOT include FontForge. The §4.9 v1.1 example YAML was non-executable. | Always verify the **runtime context** of every tool before writing workflow step examples: host runner vs container stage. For container-only tools, integrate via **flag forwarding** (workflow → `configure.py` → `BUILD_ARGS` → conditional RUN in the correct stage) instead of direct host steps. [Source: Session 2026-07-31, Spec v1.2 F-5 fix] |
| 10 | Dangling `audit_reference` di Plan frontmatter | `audit_reference` mengarah ke file audit yang belum dibuat/ditulis → auditor berikutnya tidak menemukan bukti, audit gagal | Buat/simpan laporan audit TERLEBIH DAHULU, atau update `audit_reference` di plan untuk merujuk ke file yang ada (via /sdlc-plan-tasks). Verifikasi path file ada sebelum audit ditutup. [Source: Session 2026-08-01, B1 dari consistency audit] |
| 11 | Trust `pytest tests/ -v` (system python3) di Docker Stage 1 untuk benar-benar mengeksekusi test yang bergantung FontForge | Dockerfile Stage 1 apt = `ca-certificates, fontforge, python3-pip, make` — TANPA `python3-fontforge`; bindings Python FontForge embedded di interpreter binary-nya sendiri → `import fontforge` GAGAL di system python3. Semua 4 file test memakai `pytest.importorskip("fontforge")` level modul (Spec §6.3) → test SELALU SKIP, CI "pass" padahal tidak mengeksekusi apa pun (klaim K6 salah) | Instal `python3-fontforge` di Stage 1 (TASK-0.X, Phase 0) + pre-check `python3 -c "import fontforge"`; kontrak exit code `detect_incompatibility.py` (E4) jadi prasyarat. Saat test suite memakai importorskip, verifikasi skip count (jalankan dengan `-rs`/`-v`) sebelum mempercayai klaim "tests pass". [Source: Session 2026-08-01, klarifikasi r5 B1 — Spec v1.6 §6.3 vs Dockerfile] |
| 12 | Panggil `glyph.selfIntersects` sebagai properti (baca boolean) | API FontForge: `selfIntersects` adalah **method** (`glyph.selfIntersects()`), bukan properti. Bound method selalu truthy → semua glyph diklasifikasikan `fail` → gate interpolasi mustahil lolos. Bug silent (tidak crash) — hasil selalu semua-gagal tanpa peringatan. [Source: Session 2026-08-05, TASK-1.1 PoC — validate_interpolation.py] | Selalu verifikasi API FontForge: method vs property. Tambahkan `()` pada call method. Untuk regression guard: pastikan test mengeksekusi jalur sukses dan gagal secara eksplisit, bukan hanya mengandalkan hasil boolean. |
| 13 | Kontur matching by CENTROID SAJA untuk glyph multi-kontur berimpit (numbersign, Aring, Theta, dollar) | Centroid ambigu (kontur fitur berbeda dengan centroid mirip) → pasangan SILANG → equalize shape-preserving tetap jalan tapi interpolasi akan blend fitur yang salah (garbage) — tidak terdeteksi oleh cek kompatibilitas struktural. Terdeteksi via rasio luas kontur yang tidak wajar. [Source: Session 2026-08-05, Phase 2 Full Harmonization] | Gunakan **area-rank matching** sebagai validator: urutkan kontur berdasarkan luas bounding box, lalu cocokkan per-rank. Tambahkan **sanity centroid check** (centroid kontur pasangan harus dalam toleransi). Area-ratio > 4 bukan otomatis salah — glyph seperti dollar memiliki perbedaan proporsional yang sahih antar weight. |
| 14 | Bangun path pasangan glyph dengan `Path("/abs/path") / Path("/abs/other")` | `pathlib.Path` absolut sebagai divisor membuang sisi kiri: `Path("/abs/a") / Path("/abs/b")` = `/abs/b` (absolute wins). Semua glyph dibandingkan dengan dirinya sendiri → semua tampak "kompatibel" (copied=0). [Source: Session 2026-08-05, Phase 3 Core-Weight Interpolation] | Selalu gunakan `fpath.name` (nama file saja) sebelum membangun path pasangan via `pair_dir / fpath.name`. Verifikasi hitungan (blend vs copy count) sebagai sanity check — jika copied=0 untuk semua glyph, path matching kemungkinan rusak. |

### Key Metrics & Baselines

<!-- Stable metrics that serve as reference points (test counts, coverage, performance baselines). -->
- **Test Suite (configure.py)**: 62/62 pytest unit tests passing, 0.20s execution time. [Source: Session 2026-07-29 Phase 1; re-verified 2026-07-30 plan-refactor]
- **Knowledge Base Size**: 14 Dead-Ends + 42 Architecture & Patterns. [Source: Session 2026-08-05, Code Phase compaction — +3 DE (#12 selfIntersects, #13 centroid area-rank, #14 pathlib absolute) + 2 patterns (NOTE-row Insertion, Engine Tuple Arity)]
- **Plan-Refactor Execution (2026-07-30)**: 16 tasks across 3 phases, all completed in single session; 13/13 acceptance criteria met; pytest 62/62 PASS; CON-001 preserved. [Source: Session 2026-07-30, plan-refactor-code-review v1.0]
- **End-to-End Build**: 8 iteration cycles to first successful CI run (issues #1–#8). [Source: Session 2026-07-30, first end-to-end run 30520458083]
- **GitHub Actions Actions Versions**: `actions/checkout@v7` + `actions/setup-python@v6` + `actions/upload-artifact@v4` (Node.js 24 LTS). [Source: Session 2026-07-30]
- **Custom-build Release Tag Format**: `custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}` (UTC). [Source: PRD v1.3, Plan v1.2 §TASK-040]
- **CON-001 (Constraint)**: `Scripts/features.py` is FORBIDDEN to modify (legacy). All environment fixes go in `Dockerfile` or workflow YAML. Verified via `git diff --stat` on legacy files = empty. [Source: Plan v1.2 §CON-001, verified 2026-07-30 plan-refactor]
- **Spec Multi-Weight Variants (v1.3)**: 1147 lines, markdownlint 0 issues, 62 balanced code fences, traceability 100% vs PRD v1.3 (FR-1..7 / GH-001..006 / SM-T1..4 / E0.1..4 all covered). [Source: Session 2026-07-31, spec verification pass]

---



## 📝 Session Checkpoint: 2026-08-05 (Phase 3 CLOSED — user approval; briefing Phase 4)

- **Current SDLC Phase:** Phase Code — Phase 3 ditandai ✅ SELURUHNYA (TASK-3.1–3.Y) atas approval eksplisit user (2026-08-05); plan rows + todo updated. Phase 1 gate tetap blocked (GA).
- **Phase 4 (Pipeline Integration) — pembagian kerja:**
  - **AI (implementasi code, tanpa FontForge):** TASK-4.1 `configure.py` + `config.schema.json` (`--form-enable-multi-weight`, `BUILD_LEVEL_FLAGS`, properti `EnableMultiWeight`); TASK-4.2 `Dockerfile` Stage 1 RUN chain (guard Sources/Harmonized, strip `--multi-weight`, apt python3-fontforge + pre-check, pytest-cov, validate --strict kedua pasangan, driver, fail-fast loop `${T_FINAL}`); TASK-4.3 `custom-build.yml` (`enable_multi_weight`, `timeout-minutes: 360`, upload `output/reports/**`); TASK-4.4 `packaging.sh` (RELEASE_MODE + VERSION guard `_die`, NEW_WEIGHTS hinting pattern, verifikasi cabang ENABLE_MULTI_WEIGHT sudah terhapus); TASK-4.5 README + Specimen
  - **User (verifikasi di GA):** TASK-4.X docker build mode true/false + byte-identical (AC-B03) + packaging RELEASE_MODE tanpa VERSION harus `_die` (R2); TASK-4.Y approval
  - **PRASYARAT YANG SUDAH ADA:** guard `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}` — 4 master penuh ✓; `test-multi-weight.yml` push-gate ✓
  - **RISIKO YANG HARUS DISAMPAIKAN KE USER:** run `enable_multi_weight=true` penuh di GA akan FAIL-FAST (GUD-002) di interpolasi native karena 481 glyph `needs_harmonization` belum dikerjakan desainer; mode `false` dijamin byte-identical (AC-B03) — plumbing pipeline bisa diverifikasi via mode false + tahapan RUN chain sampai titik interpolasi
- **Verification Snapshot:** plan TASK-3.2/3.3/3.X/3.Y ✅ 2026-08-05 (row edit disambiguasi NOTE-3.2 via anchor `phase3-visual-review`); todo 18/24 done, 6 blocked (Phase 1 gate + pending GA)

<!-- checkpoint-tail: Phase 3 closed 2026-08-05 (user approval, semua row plan ✅). Fase 4 = pipeline integration: AI kerjakan TASK-4.1–4.5 (configure/Dockerfile/workflow/packaging/README), user verifikasi TASK-4.X di GA (mode true/false, byte-identical, RELEASE_MODE guard) + approval. Ingat: mode true akan fail-fast di interpolasi sampai 481 skip desainer beres. -->

---

## 📝 Session Checkpoint: 2026-08-05 (Phase Code — Phase 4 Pipeline Integration SELESAI; Phase 1–3 CLOSED)

- **Current SDLC Phase:** Phase Code — Phase 4 (Pipeline Integration): TASK-4.1–4.5 ✅ 2026-08-05; TASK-4.X blocked (verifikasi GA oleh user); TASK-4.Y menunggu approval. Phase 1/2/3 ditandai selesai atas approval eksplisit user (2026-08-05).
- **Active Artifacts:**
  - `Scripts/configure.py` + `config.schema.json` — EnableMultiWeight (DEFAULTS/FORM_KEY/BUILD_LEVEL_FLAGS/argparse/schema)
  - `Dockerfile` — Stage 1: python3-fontforge apt + pytest/jsonschema/pytest-cov, RUN chain kondisional multi-weight (guard→detect→validate 2 pasangan→pytest --cov→driver→fail-fast loop T_FINAL), FONTS selection + strip --multi-weight; Stage 2: COPY build-reports
  - `.github/workflows/custom-build.yml` — input enable_multi_weight, timeout 360, forward flag, upload output/reports/**
  - `Scripts/packaging.sh` — hinting override NEW_WEIGHTS (case pattern), RELEASE_MODE=1 + VERSION guard _die + 3 archive per format, reports surfacing, zip-all Custom Build (verifikasi: cabang ENABLE_MULTI_WEIGHT sudah tidak ada ✓)
  - `README.md` — section Multi-Weight Variants (prasyarat harmonized sources + pesan error guard) + Faux Italic Limitations (tabel kompatibilitas + CSS @font-face)
  - `tests/test_configure.py` — 8 test baru (TestEnableMultiWeight) + update fixture/assertion 5 opsi
- **Achieved Milestones:**
  - **TASK-4.1**: 70/70 pytest PASS (8 test baru EnableMultiWeight: default/form/config/args string/schema/manifest); `build_driver_arg_string` = driver flags + BUILD_LEVEL_FLAGS (--multi-weight terakhir)
  - **TASK-4.2**: 5 RUN fragment lolos `sh -n`; simulasi guard: dir hilang → `::error::` + exit 1 ✓; strip `--multi-weight` ✓; T_FINAL placeholder 15.0 (WAJIB diganti nilai kalibrasi saat PoC tuntas — TODO desainer/GA)
  - **TASK-4.3**: YAML valid, 5 inputs, timeout 360
  - **TASK-4.4**: bash -n OK; ENABLE_MULTI_WEIGHT branch absen (verifikasi codebase R1 ✓); RELEASE_MODE VERSION guard
  - **TASK-4.5**: README multi-weight + Faux Italic
- **Decisions Made:** user override menandai Phase 1–3 selesai (2026-08-05) meski gate GA belum dijalankan; urutan run chain mengikuti Spec §4.9 (Q-02: pytest sebelum interpolasi)
- **Next Action / Pending:**
  - **PRIORITAS #1 (user, GA):** TASK-4.X — docker build enable_multi_weight=false (byte-identical AC-B03) + true (RUN chain sampai fail-fast yang diharapkan karena 481 skip) + RELEASE_MODE tanpa VERSION harus _die
  - **PRIORITAS #2:** TASK-4.Y approval → Phase 5 (buffer/stabilisasi + runbook release TASK-5.4)
  - **PRIORITAS #3 (desainer):** 481 glyph needs_harmonization — prasyarat semua gate interpolasi lulus
  - **Git:** seluruh perubahan BELUM di-commit; branch feature/multi-weight-poc
- **Verification Snapshot:**
  - `pytest tests/ -q` → 70 passed, 4 skipped (fontforge importorskip — host)
  - `sh -n` 5 fragment Dockerfile RUN: OK; simulasi guard+strip: OK
  - `bash -n Scripts/packaging.sh`: OK; YAML workflow: valid (5 inputs, timeout 360)
  - markdownlint: README pakai directive `<!-- markdownlint-disable -->` (konvensi repo)

<!-- checkpoint-tail: Phase 4 selesai 2026-08-05 — configure.py+schema (70/70 test), Dockerfile RUN chain multi-weight, workflow enable_multi_weight+360, packaging RELEASE_MODE/NEW_WEIGHTS/reports, README; Phase 1-3 closed by user. Next: user verifikasi TASK-4.X di GA (mode true/false + RELEASE_MODE guard) → TASK-4.Y → Phase 5. -->

---

## 📝 Session Checkpoint: 2026-08-05 (Phase Code — Phase 5 Buffer SELESAI: rescue struktural +219 glyph)

- **Current SDLC Phase:** Phase Code — Phase 5 (Buffer): TASK-5.1/5.2/5.3 ✅ 2026-08-05; TASK-5.4 blocked (faktor stretch = keputusan Designer A + maintainer, butuh FontForge di luar CI); TASK-5.X/5.Y blocked (GA + desainer + approval). Phase 1–4 CLOSED (user approvals).
- **Achieved Milestones:**
  - **Engine v2 upgrade (TASK-5.1/5.3 stabilisasi)** — `build/poc/harmonize_engine.py`:
    (1) matcher `match_contours` v2: dua kandidat (area-rank + centroid-greedy) + `_pair_score` (violasi centroid > 45% diag / area-ratio > 4 + centroid jauh) — rescue refusal sambil tetap anti-crossing;
    (2) `equalize_pair`: op baru konversi **degenerate-c → line di sisi LEBIH BESAR** (−2 node, shape-exact, deteksi collinear cross ≤ 1e-3·L²) + planner eksak (d ≡ 0/1/2 mod 3; d=1 tetap butuh line di sisi kecil)
  - **+219 glyph ter-rescue**: RB harmonized 304 → 443 (skips 340 → 281); IB 400 → 480 (skips 264 → 251); union tracking 481 → **462**
  - **Verifikasi PASS**: verify_masters (0/0/0), interpolasi regenerasi (835 blend + 207 copy/weight), verify_interpolation (0 problems)
  - **Phase 4 ditandai selesai** (TASK-4.X/4.Y ✅ — user approval)
- **Dead-Ends (Do NOT Repeat):** tuple offs `("off", x, y)` di-unpack `for ox, oy in offs` → ValueError (3 elemen); pola: selalu akses `e[1]/e[2]` untuk entri tuple
- **Updated Files:**
  - `build/poc/harmonize_engine.py` — matcher v2 + equalize_pair + helpers degenerate
  - `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}/` — regenerated (443/480 harmonized)
  - `Sources/Harmonized/Interpolated/{Medium,SemiBold}/` — regenerated (835 blend)
  - `Sources/Harmonized/tracking.json` — 462 entri (regen dari skip list baru)
  - `plan/plan-feature-multi-weight-variants-v1.13.md` — TASK-5.1/5.2/5.3 ✅
- **Next Action / Pending:**
  - **TASK-5.4 (maintainer, di luar CI):** runbook 10 langkah stretch (faktor = keputusan Designer A + maintainer → `docs/audit/stretch-factor-decision-{date}.md`; driver `--enable-light/--enable-extrabold --light-factor/--extrabold-factor`; validasi per-weight terpisah + `--fail-fast`; verdict tracking.json; `RELEASE_MODE=1` + `VERSION`; stage: 2-4 = Stage 1 image, 5 = host, 6 = Stage 1 image, 7 = Stage 2 image, 8 = Stage 2 container; GUD-004 partial success)
  - **TASK-5.X/5.Y (GA + desainer):** gate ≤ 240 menit, fail_count=0 — 462 skip tersisa butuh desainer
  - **Git:** seluruh perubahan BELUM di-commit
- **Verification Snapshot:** verify_masters RESULT PASS (RB 377 files-differing harmonized, IB 431); verify_interpolation PASS; tracking 462 valid schema §4.12

<!-- checkpoint-tail: Phase 5 buffer selesai 2026-08-05 — engine v2 rescue +219 glyph (matcher 2-kandidat + degenerate-c removal), tracking 481→462, verifikasi PASS; TASK-5.4 stretch menunggu keputusan faktor maintainer (runbook 10 langkah), TASK-5.X/5.Y menunggu GA + desainer; Phase 1-4 closed. -->

---

## 📝 Session Checkpoint: 2026-08-05 (Phase 5 CLOSED — SELURUH PLAN SELESAI)

- **Current SDLC Phase:** Phase Code — **SELESAI** (user approval). Phase 5 ditandai ✅ (TASK-5.4/5.X/5.Y); plan-as-record dilengkapi: 13 baris task lama yang belum bertanda (TASK-0.11/0.12/0.X/0.Y, 1.2/1.3/1.X/1.Y, 2.4/2.X/2.Y, 4.X/4.Y) di-mark ✅ 2026-08-05 — total 47 baris task bertanda selesai, 0 tersisa. Semua fase 0–5 resmi CLOSED atas approval eksplisit user.
- **Todo:** 37/37 done.
- **Next Action / Pending (di luar implementasi):**
  - Commit seluruh perubahan (branch `feature/multi-weight-poc`) — BELUM ada yang di-commit
  - Verifikasi GA (TASK-4.X/0.X): docker build mode true/false + pytest container + RELEASE_MODE guard
  - Desainer: 462 glyph `needs_harmonization` (tracking.json)
  - Maintainer: stretch production (TASK-5.4 runbook 10 langkah, faktor = keputusan Designer A + maintainer)
  - `/sdlc-code-review` untuk review + security audit (handoff berikutnya)
- **Verification Snapshot:** plan 47/47 baris task ✅; todo 37/37; semua artefak Phase 1–5 di repo (masters, interpolated, tracking 462, tooling build/poc, Phase 4 pipeline edits)

<!-- checkpoint-tail: Phase 5 closed — seluruh plan 0-5 bertanda selesai (47 baris ✅), todo 37/37. Next: commit → verifikasi GA → desainer 462 skip → stretch maintainer → /sdlc-code-review. -->

---

## 📝 Session Checkpoint: 2026-08-05 (Engine v3 — rescue lanjutan; ceiling shape-preserving tercapai)

- **Current SDLC Phase:** Phase Code — TASK-5.1 extension (permintaan user: selesaikan 462 needs_harmonization). Hasil: **+19 glyph lagi ter-rescue (462 → 443)**, ceiling tercapai.
- **Engine v3 (`build/poc/harmonize_engine.py`):**
  - `_remove_redundant`: drop kontur degenerate (<3 on-curve / area ≈ 0) + kontur fully-contained same-winding (ray-casting + sampling konservatif 8/segmen) — shape-preserving di level render
  - `_merge_collinear_line`: −1 node (merge junction garis collinear di sisi lebih besar; toleransi cross ≤ 1e-3·L²; skip start/closure)
  - `equalize_pair` phase B: planner eksak dengan op −1 (collinear merge) / −2 (degenerate-c) / +1 / +2 / +3 — semua d ≥ 1 kecuali bila sisi besar tak punya junction collinear/degenerate-c DAN sisi kecil tak punya garis
- **Hasil:** RB 449 harmonized (skips 275), IB 501 (skips 230); tracking.json **443 entri** (RB 275, IB 230, both 62); verify_masters PASS (0/0/0); interpolasi 838 blend + 204 copy/weight, verify PASS
- **Analisis sisa 443 (mengapa tidak bisa shape-preserving):** contour-count diff-1 = 231 (mayoritas STRUKTURAL — ekstra kontur area 0.2–1.0 dari maksimum, contoh Xi/afii10020: letterform dibagi kontur berbeda antar weight; hanya ~10 kasus fitur kecil seperti ring Aring/uring/registered); diff-2+ = ~140; equalize-failed = ~90 (tidak ada op eksak yang tersedia — B tanpa junction collinear/degenerate-c, A tanpa garis); 1 degenerate-winding. **Topologi kontur yang berbeda antar master TIDAK bisa disatukan shape-preserving** — butuh keputusan desain (plan mewajibkan "Manual harmonization"; otomasi perubahan bentuk = artefak visual + melanggar semangat CON-004)
- **Next Action:** 443 glyph = kerja desainer (tracking.json berisi alasan per-glyph); GA gates; `/sdlc-code-review`. Semua perubahan BELUM di-commit.
- **Verification Snapshot:** verify_masters RESULT PASS (RB 385 files-differing / IB 458); verify_interpolation PASS; tracking 443 valid schema §4.12

<!-- checkpoint-tail: Engine v3 rescue +19 (481→443 needs_harmonization). Ceiling shape-preserving: sisa 443 butuh keputusan desain topologi (diff-1 struktural dominan). tracking.json 443 entri dengan alasan per-glyph; verifikasi PASS. -->

---

## 📝 Session Checkpoint: 2026-08-05 (Engine v3.1 — fix Phase-A gain bug; rescue 443 → 427)

- **Current SDLC Phase:** Phase Code — TASK-5.1 extension (lanjutan jawab pertanyaan "bisa selesaikan 443?"). Hasil: **+16 glyph ter-rescue (443 → 427)**, tetap shape-preserving. **Ceiling shape-preserving FINAL dikonfirmasi secara empiris.**
- **Bug Phase A yang ditemukan (`equalize_pair` di `build/poc/harmonize_engine.py`):** `gain` untuk correspondence insert dihitung dari tipe segmen di sisi **B** (`b[b_real[k]][3]`), padahal `_insert_at_param` → `split_segment` menambah **+3 (cubic)** / **+1 (line/move)** berdasarkan segmen di sisi **S**. Saat tipe segmen berbeda (B line vs S cubic), gain dihitung 1 tapi insert nyata +3 → **overshoot → rem < 0 → equalize gagal** (24 RB + 30 IB glyph). Fix: helper `_insert_gain(s, p)` menghitung gain nyata dari segmen S (sama dengan `_insert_at_param`). Bukan near-collinear fallback (yang di-rollback) — murni koreksi perhitungan.
- **Hasil:** RB skips 275→**257**, IB 230→**216**; union tracking 443→**427** (374 topology + 53 equalize — rescue 16 semuanya dari kategori equalize, 69→53). **Regresi 0** (semua skip baru ⊆ baseline 443 — diverifikasi via subset check).
- **False-positive sampling di `verify_masters.py`:** metrik lama 128-step uniform sampling melaporkan shape_violation 5.29 untuk `equal_equal_equal.liga` padahal jarak EKSAK node ke kurva Bézier = 0.001 (de Casteljau benar). Penyebab: segmen 2601 unit, spacing sample ~20 unit → jarak titik ke sample terdekat ~5+ unit. Fix: `dist_to_curve` diganti dengan subdivisi adaptif de Casteljau berbasis flatness (eps 0.25) — jarak eksak ~eps/2, **lebih akurat bukan lebih longgar**, threshold 5.0 tetap. Bonus: runtime verify 76s → **12.7s**.
- **Verifikasi FINAL semua PASS:** verify_masters (RB 403 harmonized / IB 470, compat 0, shape 0, area 0); interpolate_weights (Medium/SemiBold 856 blend + 186 copy/weight); verify_interpolation problems=0; tracking.json **427 entri** valid schema §4.12 (semua field lengkap, unique names, status needs_harmonization).
- **Kesimpulan ceiling shape-preserving (jawaban definitif untuk user):** 427 sisa = **374 topology** (contour count mismatch — perbedaan struktur kontur antar master, TIDAK bisa disatukan tanpa mengubah bentuk) + **53 equalize** (tidak ada op eksak tersedia — B tanpa junction collinear/degenerate-c DAN A tanpa garis). Semua kombinasi op shape-exact sudah dieksplorasi (v2 degenerate-c, v3 collinear-merge/remove-redundant, v3.1 -2/+3 trial → no-op, gain fix). **Yang tersisa WAJIB manual designer** (plan DEP-002; otomasi = artefak visual).
- **Next Action:** jawab user (427 tidak bisa diselesaikan algoritmik shape-preserving); opsi: (a) designer kerja dari tracking.json, (b) baseline GA gate fail_count, (c) demo subset shape-approx ≤10 glyph HANYA jika user terima deviasi bentuk. Commit belum dilakukan (branch feature/multi-weight-poc).
- **Verification Snapshot:** verify_masters RESULT PASS (RB 403/IB 470); verify_interpolation PASS (0 problems); tracking 427 valid schema §4.12.

<!-- checkpoint-tail: Engine v3.1 — fix Phase-A gain bug (gain harus dari segmen S, bukan B) rescue +16 (443→427), 0 regresi; verify_masters false-positive sampling dibenahi via subdivisi adaptif (jarak eksak, runtime -83%); sisa 427 = 374 topology + 53 equalize, ceiling shape-preserving final — butuh designer manual. -->


## 📝 Session Checkpoint: 2026-08-05 (Code Review Remediation — Phase 1 COMPLETED)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Phase Code — Code Review Remediation (Phase 1 of 3 done; Phase 2-3 pending approval)
- **Active Artifacts:**
  - `plan/plan-refactor-multi-weight-code-review-v1.0.md` — Phase 1 ✅ (5 TASKs done); Phase 2-3 pending
  - `plan/plan-feature-multi-weight-variants-v1.13.md` — Reference (implementation baseline)
  - `docs/audit/code-review-multi-weight-variants-2026-08-05.md` — Parent code review findings (2 CRITICAL, 12 REQUIRED, 5 NIT, 2 OPTIONAL, 1 FYI)
- **Achieved Milestones:**
  - **TASK-101 (REF-001):** Fixed parameter ordering bug in tests/test_multi_weight_driver.py — converted all 7 positional _interpolate_weight() invocations to keyword arguments. Positional calls silently mis-assigned 0.5→bold_path, "Medium"→factor, out_dir→weight_name, dry_run=False→output_dir. Masked by importorskip on host runner.
  - **TASK-102 (REF-002):** Removed divergent per-glyph blending fallback in Scripts/multi_weight_driver.py _interpolate_weight(). Now uses fontforge.interpolateFonts(factor, bold_path) exclusively (Spec §4.6, CON-002). Added fail-fast pre-check.
  - **TASK-103 (REF-007):** Strengthened 4 weak test assertions in tests/test_validate_interpolation.py: test_warning_status (warning_count>=1, fail_count==0), test_fail_status (fail_count>=1 + bowtie status==fail), test_overlay_png_generated (PNG file existence), test_report_json_valid (status enum consistency).
  - **TASK-104 (Q-08):** Extended test_metadata_injection to iterate all 6 weights (Light 300→ExtraBold 800) with familyname/fullname/os2_weight assertions per Spec §4.6.
  - **TASK-105 (REF-011):** Made TTF output unconditional in Scripts/poc_interpolation.py — replaced if ttf_path guard with default path; updated main() print.
- **Updated Files:**
  - Scripts/multi_weight_driver.py — removed fallback path (53 lines), added fail-fast pre-check
  - Scripts/poc_interpolation.py — TTF output conditional → unconditional
  - tests/test_multi_weight_driver.py — keyword args (7 calls) + metadata loop
  - tests/test_validate_interpolation.py — 4 strengthened assertions
- **Verification:**
  - Syntax: all 4 files OK
  - Static verification: all 5 TASKs PASSED
  - Host pytest: 70 passed, 4 skipped (FontForge importorskip) — consistent with baseline
  - CON-001: legacy files (build.py, fontbuilder.py, features.py, Makefile) untouched
  - CON-002: Workflow A (interpolateFonts only) preserved
  - Container verification (TASK-10X) NOT executed — Docker not available in this environment
- **Decisions Made:**
  - Phase 1 code review remediation completed per plan (3 phases total). Awaiting user approval to proceed to Phase 2.
- **Next Action / Pending:**
  - Await explicit user approval to proceed to Phase 2 (TASK-201–209)
  - Phase 2: tangent module, Dockerfile T_FINAL + cov-gate, overlay fix, node_diff/contour_diff, master validation, config errors, x-height, nullglob
  - Container verification (TASK-10X) requires Docker — run in GA/CI environment
  - Commit pending (branch feature/multi-weight-poc)

<!-- checkpoint-tail: Phase 1 code review remediation selesai (5/5 TASKs) — fallback removed, tests fixed, metadata loop, TTF unconditional. Container verification tertahan (no Docker). Menunggu approval Phase 2. -->

---

## 📝 Session Checkpoint: 2026-08-06 (Code Review Remediation — Phases 2 & 3 COMPLETED; plan COMPLETE v1.4)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Phase Code — Code Review Remediation **SELESAI** (Phases 1–3 ✅, user approvals 10Y/20Y/30Y). Plan refactor v1.4 status Complete (25/25 task). Handoff berikutnya: `/sdlc-code-review` (sesi baru).
- **Active Artifacts:**
  - `plan/plan-refactor-multi-weight-code-review-v1.0.md` — v1.4, status Complete, 25 `[x]` / 0 `[ ]`
  - `plan/plan-feature-multi-weight-variants-v1.13.md` — TASK-0.X/4.X doc-synced (DOC-001)
  - `spec/spec-multi-weight-variants.md` — v1.8, UNCHANGED (confirmed test #11 os2_weight 300–800; spec edits out of Dev scope)
- **Achieved Milestones:**
  - **Phase 2 (TASK-201–209, TASK-20X)** — all implemented + verified:
    - TASK-201: `Scripts/tangent_analysis.py` (stdlib-only, `compute_max_tangent_angle`/`extract_on_curve_triples`) + both validators refactored to import it; `tests/test_tangent_analysis.py` 8 tests (dummy glyphs; square 90°, equilateral triangle 120° TURNING angle = 180°−60° interior, collinear-closed → 180° reversal, degenerate segments, missing foreground)
    - TASK-202: Dockerfile `ARG T_FINAL=15.0` + `ENV T_FINAL=${T_FINAL}` (build-time override; pre-calibration default)
    - TASK-203: pytest RUN chain + `--cov-fail-under=90` (Spec §6.7)
    - TASK-204: `_generate_overlay` side-by-side REAL comparison — FontForge-native composite (interpolated left + master shifted 1 em via `g_ref.transform((1,0,0,1,em,0))`); **no Pillow** (DEP-NEW-001 resolved; `foreground` getter returns copy — verified in FontForge docs, source masters never mutated)
    - TASK-205: `node_diff`/`contour_diff` fields in validate_harmonization fail results (detect_incompatibility schema) + docstring + 4 tests extended
    - TASK-206: `_assemble_build_sources` fail-fast `_die` on missing master + new test `test_assembly_fails_fast_on_missing_master`
    - TASK-207: `validate_config` surfaces ALL errors (max 5) + `test_multiple_invalid_fields_all_reported`; 3 legacy exact-message assertions updated to multi-line format
    - TASK-208: x-height fallback `post.underlinePosition` REMOVED (wrong metric); missing sxHeight → None → "—" via `_fmt_metric`
    - TASK-209: WOFF2 zip guarded (`shopt -s nullglob` + `${#woff2_files[@]}` pre-check); simulated zero-match OK
    - TASK-20X: host pytest 81 passed/4 skipped
  - **Phase 3 (TASK-301–305, TASK-30X)** — all implemented + verified:
    - TASK-301: `Scripts/font_weights.py` (`WEIGHT_OS2_CLASS`) + refactored 3 sites (driver `WEIGHT_CLASS` removed, generate_specimen `_css_font_faces` + `_weight_number`)
    - TASK-302: `html.escape()` on ALL dynamic HTML content (8 sites: index items, waterfall text, weight names ×6 writers, checklist labels)
    - TASK-303: `_parse_bool` rejects `yes`/`no` (only true/false/1/0) + `test_parse_bool_rejects_yes_no`; parametrize updated
    - TASK-304: Dockerfile `mkdir -p build/reports` → `RUN mkdir -p build` (base, BOTH modes — Stage 2 `COPY --from=builder-fontforge /build/build` needs source path) + `mkdir -p build/reports` INSIDE multi-weight branch before pytest. **Deviation from plan text recorded in §11** (plain removal would break COPY)
    - TASK-305: plan v1.13 TASK-0.X `pip3 install` marked SUPERSEDED (Dockerfile bakes deps); TASK-4.X "Metadata Layer 2" backed by `test_metadata_injection`; Spec v1.8 test #11 CONFIRMED already documents os2_weight 300–800
    - TASK-30X: host pytest 80 passed/4 skipped; `configure.py --help` exit 0; `--form-large-line-height yes` exit 2 (rejected); `true` exit 0; WEIGHT_OS2_CLASS import OK; py_compile + bash -n + RUN chain syntax OK
- **Dead-Ends (Do NOT Repeat):**
  - **Attempted:** Unit tests assumed triangle → 60° and collinear closed contour → 0° turning angle.
  - **Reason:** `compute_max_tangent_angle` measures edge-direction TURNING angle: interior 60° triangle turns 120°; a closed all-collinear contour must reverse 180° at closure. Tests failed with 120.00000000000001 / 180.0 — fixed via `pytest.approx` + corrected expectations.
  - **Attempted:** Host-side coverage gate verification (`--cov=Scripts` + `--cov-fail-under`).
  - **Reason:** pytest-cov NOT installed on dev host (container Stage 1 only). Exit code 4 = usage error, not gate. Gate mechanism verified against pytest-cov docs instead; actual ≥90% gate run deferred to GA.
  - **Attempted (evaluated, rejected):** Pillow for `_generate_overlay` composite (advisory suggested `Pillow>=10.0` + `python3-pil`).
  - **Reason:** Research concluded FontForge-native suffices (transform + foreground-copy semantics verified in official docs); plan DEP-NEW-001 prefers native when sufficient; adding a dependency expands Docker image + requirements surface unnecessarily.
- **Updated Files (committed by user):**
  - `Scripts/tangent_analysis.py` [NEW], `Scripts/font_weights.py` [NEW], `tests/test_tangent_analysis.py` [NEW] — commits `eed9281` (Phase 2+3) + `a70dd50` (Phase 1)
  - `Scripts/multi_weight_driver.py`, `Scripts/validate_harmonization.py`, `Scripts/validate_interpolation.py`, `Scripts/configure.py`, `Scripts/generate_specimen.py`, `Scripts/poc_interpolation.py`, `Scripts/packaging.sh`, `Dockerfile`
  - `tests/test_multi_weight_driver.py`, `tests/test_validate_interpolation.py`, `tests/test_validate_harmonization.py`, `tests/test_configure.py`
  - `plan/plan-refactor-multi-weight-code-review-v1.0.md` (v1.0→v1.4), `plan/plan-feature-multi-weight-variants-v1.13.md` (TASK-0.X/4.X)
  - Working tree: CLEAN except this memory file (user committed everything)
- **Decisions Made:**
  - TASK-204 overlay: FontForge-native composite, no Pillow dependency (DEP-NEW-001 resolved as "not needed")
  - TASK-304: keep `RUN mkdir -p build` unconditional (Stage 2 COPY contract) — documented deviation
  - TASK-10X closed via user approval 2026-08-06 with deferred-to-GA note (same pattern as previous phase closures); plan status Complete
  - Remediation phases closed sequentially per plan execution directive (approval gates 10Y/20Y/30Y all granted)
- **Next Action / Pending:**
  - **Sesi baru `/sdlc-code-review`** — input: plan refactor v1.4, Spec v1.8, plan v1.13, code review report 2026-08-05 (verify closure of 22 findings). Scope: 2 commits `eed9281` + `a70dd50` (15 code/test files)
  - **Verifikasi GA (TASK-10X/20X container portion + plan v1.13 TASK-4.X)**: docker build `enable_multi_weight=false` (byte-identical AC-B03) + `true` (RUN chain, coverage ≥ 90% gate, fail-fast expected at interpolation — 427 glyphs still needs_harmonization) + `RELEASE_MODE=1` tanpa VERSION → `_die`
  - **Desainer:** 427 glyph (374 topology + 53 equalize) — manual harmonization from tracking.json
  - **Maintainer:** stretch weights TASK-5.4 runbook 10 langkah + kalibrasi `T_FINAL` (replace 15.0 placeholder via `--build-arg T_FINAL=...`)
  - Phase Docs (`/sdlc-generate-docs`) setelah review
- **Verification Snapshot:**
  - Final host pytest: 80 passed / 4 skipped (FontForge importorskip)
  - CON-001: legacy files (build.py, fontbuilder.py, features.py, Makefile) diff = 0 lines
  - Smoke: configure CLI (help=0, yes→2, true→0), WEIGHT_OS2_CLASS dict OK, RUN chain + packaging.sh syntax OK

<!-- checkpoint-tail: Remediation Phase 2+3 selesai 2026-08-06 — plan refactor v1.4 COMPLETE (25/25): tangent_analysis+font_weights modules, overlay side-by-side FontForge-native, T_FINAL ARG + cov gate 90%, node_diff/contour_diff, multi-error config, x-height honest, html.escape, nullglob, _parse_bool; 80 passed/4 skipped host; commits eed9281+a70dd50. Next: /sdlc-code-review (sesi baru) + verifikasi GA (TASK-10X/20X container, coverage gate) + desainer 427 glyph + maintainer stretch/T_FINAL. -->

---
