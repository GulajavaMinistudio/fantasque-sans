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

### Key Metrics & Baselines

<!-- Stable metrics that serve as reference points (test counts, coverage, performance baselines). -->
- **Test Suite (configure.py)**: 62/62 pytest unit tests passing, 0.20s execution time. [Source: Session 2026-07-29 Phase 1; re-verified 2026-07-30 plan-refactor]
- **Knowledge Base Size**: 11 Dead-Ends + 40 Architecture & Patterns. [Source: Session 2026-07-31, post plan v1.6 compaction; +2 promoted 2026-08-01 compaction; +1 promoted 2026-08-01 klarifikasi r4 + 2 patterns, + 1 DE; +1 DE 2026-08-01 klarifikasi r5 (DE #11); kompresi 2026-08-01] |
- **Plan-Refactor Execution (2026-07-30)**: 16 tasks across 3 phases, all completed in single session; 13/13 acceptance criteria met; pytest 62/62 PASS; CON-001 preserved. [Source: Session 2026-07-30, plan-refactor-code-review v1.0]
- **End-to-End Build**: 8 iteration cycles to first successful CI run (issues #1–#8). [Source: Session 2026-07-30, first end-to-end run 30520458083]
- **GitHub Actions Actions Versions**: `actions/checkout@v7` + `actions/setup-python@v6` + `actions/upload-artifact@v4` (Node.js 24 LTS). [Source: Session 2026-07-30]
- **Custom-build Release Tag Format**: `custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}` (UTC). [Source: PRD v1.3, Plan v1.2 §TASK-040]
- **CON-001 (Constraint)**: `Scripts/features.py` is FORBIDDEN to modify (legacy). All environment fixes go in `Dockerfile` or workflow YAML. Verified via `git diff --stat` on legacy files = empty. [Source: Plan v1.2 §CON-001, verified 2026-07-30 plan-refactor]
- **Spec Multi-Weight Variants (v1.3)**: 1147 lines, markdownlint 0 issues, 62 balanced code fences, traceability 100% vs PRD v1.3 (FR-1..7 / GH-001..006 / SM-T1..4 / E0.1..4 all covered). [Source: Session 2026-07-31, spec verification pass]

---


## 📝 Session Checkpoint: 2026-08-01 (Plan Multi-Weight v1.10 — Sync Klarifikasi r4 R1–R5 + MO-1)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Previous Phase:** Recurring Checkpoint — Clarification r4 (5/5 resolusi, laporan r4 tersimpan); plan v1.9 = target interogasi
- **Current SDLC Phase:** Phase Plan (Implementation Planning) — plan v1.10 FINAL (10/10 Next Steps r4 terimplementasi), menunggu commit + amendemen Spec v1.6
- **Active Artifacts:**
  - `plan/plan-feature-multi-weight-variants-v1.10.md` — Status: ✅ v1.10 (rename dari v1.9 via `git mv`; **belum di-commit**)
  - `docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r4.md` — Status: ✅ Finalized (rujukan `clarification_reference` plan v1.10)
  - `spec/spec-multi-weight-variants.md` — Status: ⏳ v1.5 BUTUH amendemen → v1.6 via `/sdlc-define-specs` (R1/R2 §4.10, R5 §4.9 guard, R3 REQ-I01/§6.3, R4 §4.6/§6.6 — DIJADWALKAN, belum diterapkan)
  - `docs/prd-20260731-1000-multi-weight-variants.md` — Status: ✅ v1.4 — tanpa amendemen wajib (catatan interpretasi FR-4.1 opsional, R3)
  - `CONTEXT.md` — Status: ✅ tidak berubah (`VERSION`/`RELEASE_MODE` = variabel teknis, bukan istilah domain)
- **Achieved Milestones:**
  - **Plan v1.9 → v1.10 (rename + ~20 edit surgical, sinkron laporan r4)**: TASK-4.4 ditulis ulang (R1 — hapus cabang `ENABLE_MULTI_WEIGHT` packaging, perilaku Custom Build = zip-all existing, override hinting REQ-I04 via pola nama file `NEW_WEIGHTS`; R2 — env var `VERSION` wajib + guard `_die` untuk `FantasqueSansMono-{VERSION}-{Format}.zip`); TASK-4.1 (R1 — `DEFAULTS` + properti `config.schema.json`; manifest mencatat `resolved_options.EnableMultiWeight` sebagai info audit, tidak dikonsumsi packaging; Files 1 → 2, tetap sizing S); TASK-4.2 (R5 — guard `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}` di AWAL RUN chain, pesan `::error::` + exit 1); TASK-4.5 (R5 — prasyarat harmonized sources di README section multi-weight); TASK-5.4 (R2 + MO-1 — runbook 9 → 10 langkah: generate `manifest.json` via `configure.py` sebelum packaging + `custom_build_driver.py build/sources /build` + `VERSION` wajib); TASK-0.7/3.1 (R3 — factor SemiBold dikunci `0.67` eksak, kontrak spesifikasi); TASK-0.10/TEST-003 (R3 — toleransi ±0.005 = kelonggaran presisi float, bukan kebebasan memilih nilai); TASK-0.14 BARU + FILE-025 (R4 — `.github/workflows/test-multi-weight.yml` push-gate `feature/multi-weight-*`, pytest host runner + `importorskip`, memenuhi Spec §6.6); TASK-0.X + TASK-4.X (catatan push-gate host vs Stage 1; verifikasi zip-all + `VERSION` guard); FILE-006/009 diperluas; Introduction paragraf r4 + koordinasi cross-document (Spec v1.6 DIJADWALKAN via `/sdlc-define-specs`); §8 link r4; changelog v1.10; `clarification_reference` → r4
  - **MO-2/MO-3 diverifikasi tanpa perubahan**: overlay PNG cukup di review manual Phase 3 (TASK-3.X); release archive menyertakan `FantasqueSans` (konsisten K16/zip-all — tanpa regresi)
  - **Verifikasi multi-kriteria**: markdownlint exit 0; struktur tabel markdown valid via parser Node charCode (8 kolom; 1 pipe literal di-escape `Medium\|SemiBold\|Light\|ExtraBold` di TASK-4.4); audit otomatis 15/15 cek resolusi r4 (Next Steps §4 laporan r4) lolos; `{version}` lama tidak tersisa (semua → `{VERSION}`)
  - **Pola repo dikonfirmasi**: rename file per versi plan (git history v1.3 → v1.9; sesi ini v1.9 → v1.10 via `git mv`) — konsisten KB "Plan File Rename+Version Bump Protocol"
- **Decisions Made:**
  - Seluruh resolusi R1–R5 + MO-1 diimplementasikan persis sesuai Next Steps laporan r4 §4 — tanpa scope creep, tanpa fitur baru di luar laporan
  - Amendemen Spec → v1.6 (dan PRD opsional FR-4.1) DI LUAR scope plan-tasks — dijadwalkan sesi terpisah; status dicatat di plan Introduction (koordinasi cross-document)
  - TASK-4.4 Files tetap 1 (packaging.sh); TASK-4.1 Files 2 — keduanya dalam batas task sizing (S)
- **Updated Files:**
  - `plan/plan-feature-multi-weight-variants-v1.9.md` → `plan/plan-feature-multi-weight-variants-v1.10.md` — rename + v1.10 (frontmatter, Introduction, TASK-0.7/0.10/0.14 baru/0.X/3.1/4.1/4.2/4.4/4.5/4.X/5.4, §5 FILE-006/009/025, §6 TEST-003, §8, §10 changelog)
- **Dead-Ends (Do NOT Repeat):**
  - **Attempted:** Edit multi-hunk dengan `oldText` berisi `\n` di antara dua frasa yang ternyata berada dalam SATU baris fisik (paragraf koordinasi r2/r3 = baris panjang tunggal) → seluruh panggilan edit ditolak ("Could not find edits[3]")
  - **Reason:** Dokumen plan memakai baris fisik sangat panjang (paragraf = 1 baris tanpa newline internal); asumsi newline antar-paragraf salah; selain itu sisipan paragraf memakai anchor "awal paragraf" sempat menghasilkan urutan kronologis terbalik (r4 sebelum r3)
  - **Note:** Anchor "akhir paragraf unik" lebih aman; jika berulang, promosikan ke KB saat kompaksi berikutnya
- **Next Action / Pending:**
  - **PRIORITAS #1 (user):** Commit: `git add plan/plan-feature-multi-weight-variants-v1.10.md docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r4.md .agents/instructions/memory.instructions.md && git commit -m "docs(plan+audit+memory): plan multi-weight v1.10 sync klarifikasi r4 (R1–R5 + MO-1) + checkpoint"` — catatan: perubahan lain belum di-commit dari sesi lain (AGENTS.md staged `M`, PRD `M`, Spec `M`); commit terakhir `6086e30`
  - **PRIORITAS #2 (next session):** `/sdlc-define-specs` — amendemen Spec v1.5 → v1.6 (R1/R2 §4.10 hapus cabang `ENABLE_MULTI_WEIGHT` + definisi `VERSION`; R5 §4.9 guard harmonized sources; R3 REQ-I01/§6.3 nilai `0.67` eksak; R4 §4.6/§6.6 catatan push-gate `test-multi-weight.yml`)
  - **PRIORITAS #3:** `/sdlc-clarify-reqs` (r5) atas plan v1.10 — atau langsung re-audit konsistensi (audit_reference lama masih 2026-08-01, perlu verifikasi ulang setelah Spec v1.6) → PASS → `/sdlc-write-code` (TASK-0.0 branch `feature/multi-weight-poc`); lampirkan plan v1.10 + spec + PRD + laporan r4 + audit
- **Verification Snapshot:**
  - markdownlint: plan v1.10 = 0 error (npx markdownlint 0.49.1, directive `<!-- markdownlint-disable -->`)
  - Struktur tabel: valid (semua tabel 8 kolom; pipe escaped via parser charCode)
  - Traceability: 10/10 Next Steps r4 → plan v1.10 (audit otomatis 15/15 cek)
  - Git: rename `plan/plan-feature-multi-weight-variants-v1.3.md -> v1.10.md` staged; belum di-commit

<!-- checkpoint-tail: Plan multi-weight v1.10 disinkronkan dengan klarifikasi r4 (R1 hapus ENABLE_MULTI_WEIGHT → zip-all + NEW_WEIGHTS, R2 env VERSION + runbook 10 langkah + generate manifest, R3 factor SemiBold 0.67 eksak, R4 TASK-0.14 push-gate Spec §6.6, R5 guard Sources/Harmonized di RUN chain; MO-1 kontrak SOURCES_DIR OUTPUT_DIR); 15/15 cek lolos, markdownlint 0, tabel valid; rename v1.9 → v1.10, BELUM di-commit. Next: commit → /sdlc-define-specs (Spec v1.6) → clarify/re-audit → /sdlc-write-code. -->

---

## 📝 Session Checkpoint: 2026-08-01 (Klarifikasi r5 Spec v1.6 + Plan v1.10 — 17 Temuan + 1 Non-temuan)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Previous Phase:** Recurring Checkpoint — Plan Multi-Weight v1.10 tersimpan (BELUM di-commit); Spec v1.6 + Plan v1.10 = target interogasi r5
- **Current SDLC Phase:** Recurring Checkpoint — Clarification (`/sdlc-clarify-reqs`, r5) — **SELESAI** (B1–B3, E1–E8, H1–H6, MO-1..3; menunggu amendemen spec/plan di sesi terpisah)
- **Active Artifacts:**
  - `spec/spec-multi-weight-variants.md` — Status: ✅ v1.6 target interogasi r5; ⏳ BUTUH amendemen → v1.7 via `/sdlc-define-specs` (§4.9 B1/B2/H5, §4.4 E4, §4.6 E6, §4.8 B3, §4.12 E1, REQ-I03 E3/E5, REQ-I06 E7, AC-B02 E8, §7 Ask First B1/MO-1, §9.2 SVC-001/SVC-005, §6.7 MO-1)
  - `plan/plan-feature-multi-weight-variants-v1.10.md` — Status: ✅ target interogasi r5; ⏳ BUTUH amendemen → v1.11 via `/sdlc-plan-tasks` (TASK-0.7 Files 1→2 + `.gitignore`, TASK-0.X baru B1/MO-1, TASK-3.2 B3, TASK-3.X baru H1, TASK-4.2 B1/B2/H3, TASK-4.3 H3, TASK-4.4 H3, TASK-5.4 E2/H6, TASK-2.1/2.2/2.3 E1)
  - `docs/prd-20260731-1000-multi-weight-variants.md` — Status: ✅ v1.4 — tidak ada amendemen wajib
  - `docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r5.md` — Status: ✅ BARU (laporan r5, 19.8 KB, markdownlint 0 error)
- **Achieved Milestones:**
  - **Blocker B1 (keputusan eksplisit user, Opsi A):** Dockerfile Stage 1 apt = `ca-certificates, fontforge, python3-pip, make` (TANPA `python3-fontforge`; komentar bindings embedded) → pytest di system python3 TIDAK bisa `import fontforge` → 4 file test §6.3 (`importorskip` level modul) SELALU SKIP → klaim K6 salah. Resolusi: TASK-0.X (Phase 0, mendahului TASK-4.2) instal `python3-fontforge` + pre-check `python3 -c "import fontforge"`; kontrak exit code `detect_incompatibility.py` (E4) jadi prasyarat
  - **Blocker B2:** `T_final` dipropagasi ke RUN chain tanpa pemilik task; snippet §4.9 hardcode `--threshold 15.0` vs GUD-002. Resolusi: §4.9 `--threshold "${T_FINAL}"` + komentar sumber; TASK-4.2 hardcode nilai kalibrasi Phase 1; 15.0 = default CLI
  - **Blocker B3:** sumber TTF specimen Phase 3 tak terdefinisi (driver hanya output `.sfdir`). Resolusi: TASK-3.2 langkah lokal `fontforge -lang=py -script Scripts/custom_build_driver.py build/sources <tmp_output>` → `<tmp>/TTF` jadi input `generate_specimen.py`
  - **Edge E1–E8 & Hidden H1–H6:** tracking.json union+sort; validasi stretch per-weight + jalur eksklusi GUD-004; hmtx unconditional; `--light-factor` wajib bersama `--enable-*`; REQ-I06 "sementara"; FILE-024 → TASK-0.7; laporan JSON dishare (COPY `builder-fontforge` → `/app/build-reports` + `packaging.sh` → `output/reports/` + upload workflow); push-gate = smoke gate; runbook TASK-5.4 di-annotasi stage; `pytest-cov` (MO-1, perpanjangan K2)
  - **Verifikasi codebase r5:** Dockerfile apt Stage 1; `packaging.sh` zip-all tanpa env mode; `custom_build_driver.py` (`_die` unknown flags, `find_sfdirs` top-level sorted, `"Generating {name}"`); `configure.py` (DEFAULTS 4 opsi, FORM_KEY_TO_OPTION, OPTION_TO_DRIVER_FLAG); `config.schema.json` (4 boolean); `custom-build.yml` (tanpa `enable_multi_weight`, `timeout-minutes: 30`, tanpa `-e`, pytest host); `.gitignore` (tanpa `build/`/`Interpolated/`); `tests/` (`test_configure.py` + conftest fixtures)
  - **Non-temuan:** `additionalProperties: true` di `config.schema.json` BUKAN celah — `EnableMultiWeight` dideklarasikan di `properties` → tipe boolean tetap tervalidasi
- **Decisions Made:**
  - B1 = Opsi A (keputusan eksplisit user); B2/B3 + E1–E8 + H1–H6 + MO-1..3 = rekomendasi agent (user delegasikan: "Tolong jawab semua pertanyaan berdasarkan jawaban rekomendasi kamu")
  - Tidak ada istilah kanonis baru → CONTEXT.md TIDAK diubah; tidak ada keputusan triple-gate (semua resolusi spec-level, mudah dibalik) → TIDAK ada ADR baru
- **Updated Files:**
  - `docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r5.md` — BARU (template wajib; daftar amendemen per-bagian spec & per-task plan; bukti verifikasi codebase; AC-B03: paket tambahan tidak mengubah output font — single-weight tetap byte-identical)
  - `.agents/instructions/memory.instructions.md` — checkpoint r5 + KB DE #11 + kompaksi checkpoint r4 (file ini)
- **Dead-Ends (Do NOT Repeat):** +1 DE #11 (pytest system python3 ≠ FontForge bindings → importorskip silent skip). Checkpoint r4 dikompaksi — R1–R5 sudah terserap Plan v1.10/Spec v1.6 + laporan r4 permanen
- **Next Action / Pending:**
  - **PRIORITAS #1 (next session):** `/sdlc-define-specs` — amendemen Spec v1.6 → v1.7 (daftar lengkap per-bagian di laporan r5 §4); changelog + `clarification_reference` → r5
  - **PRIORITAS #2 (next session):** `/sdlc-plan-tasks` — amendemen Plan v1.10 → v1.11 (TASK-0.7, TASK-0.X baru, TASK-3.2, TASK-3.X baru, TASK-4.2, TASK-4.3, TASK-4.4, TASK-5.4, TASK-2.1/2.2/2.3); changelog + `clarification_reference` → r5
  - **PRIORITAS #3:** `/sdlc-audit-consistency` — re-audit setelah amendemen (audit 2026-08-01 status FAIL; `audit_reference` lama perlu verifikasi ulang)
  - **PRIORITAS #4:** `/sdlc-write-code` — HANYA setelah re-audit PASS (TASK-0.0 branch `feature/multi-weight-poc`)
  - **Git:** laporan r5 + memory `??` (untracked); commit disarankan: `git add docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r5.md .agents/instructions/memory.instructions.md && git commit -m "docs(audit+memory): clarification report r5 (B1–B3 + E1–E8 + H1–H6) + checkpoint + KB DE #11"`
- **Verification Snapshot:**
  - markdownlint: laporan r5 = 0 error (npx markdownlint-cli2 v0.23.2)
  - Traceability: 17 temuan (B1–B3, E1–E8, H1–H6) + MO-1..3 → daftar amendemen Spec v1.7 & Plan v1.11 (mapping di laporan r5 §4); 1 non-temuan (`additionalProperties`)
  - Git: commit terakhir `6086e30`; laporan r5 & memory belum di-commit

<!-- checkpoint-tail: Klarifikasi r5 spec v1.6 + plan v1.10 selesai (B1 instal python3-fontforge Stage 1 — importorskip silent skip, B2 --threshold T_final, B3 sumber TTF specimen via driver lokal; E1–E8, H1–H6, MO-1..3; laporan docs/audit/...-2026-08-01-r5.md, markdownlint 0). Kompaksi: checkpoint r4 dihapus (terserap Plan v1.10/Spec v1.6), Plan v1.10 dipertahankan, DE #11 dipromosikan. Next: /sdlc-define-specs (Spec v1.7) → /sdlc-plan-tasks (Plan v1.11) → re-audit → /sdlc-write-code. -->

---

## 📝 Session Checkpoint: 2026-08-01 (Plan Multi-Weight v1.11)

**Active Memory Path:** `.agents/instructions/memory.instructions.md`
**Current SDLC Phase:** Implementation Planning — `/sdlc-plan-tasks` — **Plan v1.11 FINAL**
**Active Artifacts:**
**plan/plan-feature-multi-weight-variants-v1.11.md** — Status: ✅ Completed (v1.11; v1.10 deleted)
**docs/audit/clarification-report-implementation-plan-multi-weight-variants-2026-08-01-r5.md** — Status: ✅ Finalized
**spec/spec-multi-weight-variants.md** — Status: ⏳ v1.6, amend to v1.7 (scheduled)
**Achieved Milestones:**
**Plan v1.10→v1.11** — 20+ surgical edits: front matter (v1.11, r5 ref), Intro paragraphs (r5 summary + cross-doc), 9 NOTE-rows in task tables (NOTE-0.7 H2, NOTE-0.X B1/MO-1, NOTE-2.3 E1, NOTE-3.2 B3, NOTE-3.X H1, NOTE-4.2 B1/B2/H3, NOTE-4.3 H3, NOTE-4.4 H3, NOTE-5.4 E2/H6), FILE-024 update, TEST-007, §8 r5 link, changelog v1.11; v1.10 deleted; bottom-to-top edit ordering.
**Semua resolusi r5 tercatat:** B1 (apt python3-fontforge + pre-check), B2 (T_FINAL shell var), B3 (lokal TTF pra-hinting), E1 (tracking.json union+sort), E2 (validasi per-weight + --exclude), E4 dilewati, H1-H6, MO-1 (pytest-cov container-only).
**Verifikasi:** grep 9 NOTE-rows ✓, TEST-007 ✓, §8 r5 link ✓, changelog v1.11 ✓, front matter v1.11 ✓, glob hanya v1.11 ✓.
**KB Pattern baru:** NOTE-row Insertion for Long Truncated Table Cells — gunakan `PUT >N:` untuk insert NOTE row di bawah task, bukan reproduce baris panjang (>768 chars). [Source: 2026-08-01]
**Decisions Made:** B1 = Opsi A (user override); E4 = dilewati (spec only); sisanya = agent rekomendasi.
**Updated Files:** plan v1.10.md — DELETED; plan v1.11.md — CREATED; memory.instructions.md — checkpoint + KB pattern.
**Next Action:** PRIORITAS #1 commit v1.11; #2 `/sdlc-define-specs` (Spec v1.7); #3 `/sdlc-clarify-reqs` r5 → re-audit → `/sdlc-write-code`.

<!-- checkpoint-tail: Plan multi-weight v1.11 FINAL — sync r5 (B1 python3-fontforge apt, B2 T_FINAL, B3 lokal TTF, E1 tracking.json, E2 per-weigh, E4 dilewati, H3 build-reports, H4 push-gate=smoke, H6 runbook anotasi); 9 NOTE-rows + TEST-007; v1.10 deleted. Next: commit → /sdlc-define-specs → re-audit → /sdlc-write-code. -->
---

## 📝 Session Checkpoint: 2026-08-05 (Phase Code — TASK-1.1 PoC Subset Harmonization)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Phase Code (`/sdlc-write-code`) — Implementation Phase 1 (PoC/MVP) in progress; TASK-1.1 SELESAI, TASK-1.2/1.3/1.X menunggu eksekusi di GitHub Actions
- **Active Artifacts:**
  - `plan/plan-feature-multi-weight-variants-v1.13.md` — TASK-1.1 ditandai ✅ 2026-08-05
  - `docs/audit/poc-glyph-list-2026-08-05.md` — BARU (deliverable TASK-1.1, 40 glyph, 36 harmonized, 4 skip)
  - `Sources/Harmonized/Regular/` + `Sources/Harmonized/Bold/` — BARU (subset font 36 glyph + font.props)
  - `Scripts/validate_interpolation.py` — FIX bug kritis `selfIntersects` (properti → method)
  - `tests/test_validate_interpolation.py` — FIX `test_pass_status` (threshold 100.0; kotak 90° = warning di 15°)
- **Achieved Milestones:**
  - **TASK-1.1 (PoC subset harmonization)**: analisis kuantitatif worst offenders via parser .sfdir teks (tanpa FontForge): 633/1037 (61%) kompatibel, 394 incompatible; engine harmonisasi struktural shape-preserving (ekspansi Refer, matching kontur by centroid, reverse winding, equalisasi node via de Casteljau/lerp/konversi degenerat) → 36/40 glyph terharmonisasi, 0 isu kompatibilitas, shape terverifikasi eksak
  - **4 glyph skip (butuh harmonisasi desainer)**: `d` (4v2 kontur, outline ganda), `m` (1v2 kontur), `at` (Bold 15-node vs Regular 77-node), `percent` (5v3 kontur)
  - **Deviasi FR-2.1 terdokumentasi**: font TIDAK memiliki glyph ligatur `fi`/`fl` (ligature = keluarga `*.liga`, shared pool Phase 2) → `germandbls` sebagai wakil counter kompleks
  - **Bug kritis ditemukan & diperbaiki**: `validate_interpolation.py` memanggil `glyph.selfIntersects` sebagai properti (API FontForge = method) → bound method selalu truthy → SEMUA glyph diklasifikasikan `fail` → gate PoC mustahil lolos; fix surgical + test existing `test_pass_status` jadi regression guard
- **Dead-Ends (Do NOT Repeat):** lihat KB DE #11 (importorskip silent skip — sama akarnya: script Phase 0 tidak pernah dieksekusi nyata karena TASK-0.X belum pernah dijalankan di container; TASK-0.11/0.12/0.X masih pending)
- **Updated Files:**
  - `docs/audit/poc-glyph-list-2026-08-05.md` — BARU (metodologi, tabel subset, runbook GA)
  - `Sources/Harmonized/{Regular,Bold}/` — BARU (36 glyph subset + font.props)
  - `Scripts/validate_interpolation.py` — fix `selfIntersects()` call
  - `tests/test_validate_interpolation.py` — fix threshold test_pass_status
  - `plan/plan-feature-multi-weight-variants-v1.13.md` — TASK-1.1 ✅
- **Decisions Made:**
  - User: instalasi FontForge/Docker lokal DITUNDA — eksekusi & testing via GitHub Actions (2026-08-05)
  - Harmonisasi PoC = kompatibilisasi struktural shape-preserving (ASUMSI terdokumentasi: BUKAN harmonisasi desain final Phase 2; gate manusia FR-2.4 tetap berlaku)
  - Subset master = font subset-only (bukan salinan penuh) — konsisten FR-2.1 "PoC mencakup subset"
  - Glyph tidak terharmonisasi TIDAK disertakan dalam subset master (gate statistik = subset terharmonisasi saja)
- **Next Action / Pending:**
  - **PRIORITAS #1 (user, di GA):** TASK-1.2 interpolasi subset → Medium via `poc_interpolation.py`; TASK-1.3 specimen + kalibrasi dua-pass (15.0° → T_final); TASK-1.X dual gate (pass_rate ≥ 90%, fail_count = 0) — runbook lengkap di poc-glyph-list-2026-08-05.md §4
  - **PRIORITAS #2:** TASK-0.11/0.12/0.X (eksperimen E0.1–E0.3 + VERIFY container) masih pending dari Phase 0 — verifikasi di GA sekaligus (termasuk regression `test_pass_status`)
  - **PRIORITAS #3:** TASK-1.Y approval → Phase 2 (harmonisasi desain penuh; d/m/at/percent butuh desainer)
  - **Git:** seluruh perubahan BELUM di-commit (sesuai preferensi user commit manual); branch `feature/multi-weight-poc`
- **Verification Snapshot:**
  - Kompatibilitas harmonized: 36/36 glyph, 0 isu (kontur/node/winding) — verifikasi re-parse
  - Shape preservation: deviasi on-curve & kurva ≤ 0.7 em-unit (artefak sampling verifikasi, konvergen kuadratik; nilai sejati ≈ 0)
  - `python -m py_compile` kedua file yang diedit: OK

<!-- checkpoint-tail: Phase Code TASK-1.1 selesai 2026-08-05 — analisis worst offenders + harmonisasi struktural 36/40 glyph subset (4 skip: d, m, at, percent), Sources/Harmonized/{Regular,Bold} dibuat, poc-glyph-list-2026-08-05.md; bug kritis validate_interpolation.py selfIntersects() diperbaiki; FontForge lokal ditunda user — TASK-1.2/1.3/1.X dijalankan di GitHub Actions (runbook §4 doc). -->

---

## 📝 Session Checkpoint: 2026-08-05 (Phase Code — Phase 2 Full Harmonization, Structural Pass)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Phase Code (`/sdlc-write-code`) — Phase 2 (Full Master Harmonization) structural pass SELESAI (TASK-2.1/2.2/2.3 ✅); TASK-2.4/2.X/2.Y menunggu desainer + GA; Phase 1 gate (TASK-1.2/1.3/1.X) tetap blocked di GA
- **Active Artifacts:**
  - `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}/` — 4 master PENUH (1042/1040/1046/1041 glyph) — menggantikan subset PoC 36 glyph
  - `Sources/Harmonized/tracking.json` — 481 entri `needs_harmonization` (union+sort, schema §4.12 valid)
  - `build/poc/harmonize_engine.py` + `build/poc/verify_masters.py` — tooling reproducible (build/ git-ignored, BUKAN artifact plan)
  - `plan/plan-feature-multi-weight-variants-v1.13.md` — TASK-2.1/2.2/2.3 ✅ 2026-08-05
  - `docs/audit/poc-glyph-list-2026-08-05.md` — catatan supersede (master penuh)
- **Achieved Milestones:**
  - **Harmonisasi struktural penuh (shape-preserving)**: RB 304 glyph terharmonisasi + 31 ref-copied + 282 copied, 340 skip; IB 400 + 72 ref-copied + 235 copied, 264 skip (union skip 481: 123 di kedua pasangan)
  - **Matcher kontur diupgrade**: centroid → **area-rank + sanity centroid** (centroid ambigu memproduksi CROSSED PAIRING — terdeteksi via rasio luas: numbersign/Aring/Theta/dollar di run pertama; eliminasi di run kedua)
  - **Verifikasi PASS** (script reusable `build/poc/verify_masters.py`): compat_issues=0, shape_violations=0 (threshold 5.0 — artefak sampling 128-step terbukti konvergen 4.83→0.44 @1024 step, kurva tajam radius kecil), area_flags=0 (dollar = false positive, centroid stroke cocok)
  - **Bug engine file**: `resolve_glyph` drop kind/flags (3-tuple) → IndexError; diperbaiki pertahankan arity tuple
- **Dead-Ends (Do NOT Repeat):**
  - **Attempted:** kontur matching by CENTROID SAJA untuk glyph multi-kontur berimpit (numbersign, Aring, Theta, dollar)
  - **Reason:** centroid ambigu (kontur fitur berbeda dengan centroid mirip) → pasangan SILANG → equalize shape-preserving tetap jalan tapi interpolasi akan blend fitur yang salah (garbage) — tidak terdeteksi oleh cek kompatibilitas struktural
  - **Note:** pairing HARUS divalidasi dengan ukuran/area + sanity centroid; area-ratio > 4 bukan otomatis salah (stroke dollar proporsional beda antar weight — false positive bila centroid cocok)
- **Updated Files:**
  - `Sources/Harmonized/{Regular,Bold,Italic,BoldItalic}/` — 4 master penuh (ditulis ulang via engine)
  - `Sources/Harmonized/tracking.json` — 481 entri needs_harmonization (assign Designer A/B per pair, notes + reason, date_flagged)
  - `build/poc/harmonize_engine.py` — BARU (git-ignored tooling; parser, resolve, reverse, equalize, matcher area-rank, write-back)
  - `build/poc/verify_masters.py` — BARU (git-ignored; compat + shape + pairing verification)
  - `plan/plan-feature-multi-weight-variants-v1.13.md` — TASK-2.1/2.2/2.3 ✅
  - `docs/audit/poc-glyph-list-2026-08-05.md` — catatan supersede
- **Decisions Made:**
  - Phase 1 TIDAK ditandai selesai (TASK-1.2/1.3/1.X belum dieksekusi — GA); user override: lanjut Phase 2 (2026-08-05)
  - Harmonisasi Phase 2 = pass struktural shape-preserving oleh AI; 481 glyph skip = worklist desainer (tracking.json); gate TASK-2.X (fail_count=0) TIDAK bisa lulus sampai desainer menangani
  - Master penuh menggantikan subset PoC (runbook GA tetap valid)
- **Next Action / Pending:**
  - **PRIORITAS #1 (GA):** TASK-1.2/1.3/1.X (PoC gate) + TASK-2.X (harmonization gate) — runbook di poc-glyph-list-2026-08-05.md §4; `validate_harmonization.py` untuk 4 master
  - **PRIORITAS #2 (desainer):** 481 glyph needs_harmonization (tracking.json) — terutama d/m/at/percent (PoC) + skip struktural
  - **PRIORITAS #3:** TASK-2.Y approval → Phase 3
  - **Git:** seluruh perubahan BELUM di-commit; branch `feature/multi-weight-poc`
- **Verification Snapshot:**
  - `python build/poc/verify_masters.py` → RESULT: PASS (RB: 304 harmonized, 0/0/0; IB: 400 harmonized, 0/0/0)
  - tracking.json: 481 entri, sorted, schema §4.12 conformant
  - Jumlah glyph master = jumlah sumber (1042/1040/1046/1041)

<!-- checkpoint-tail: Phase 2 structural pass selesai 2026-08-05 — 4 master penuh (RB 304 + IB 400 harmonized, area-rank matcher anti-crossing), tracking.json 481 needs_harmonization, verify PASS; Phase 1 gate tetap di GA; desainer harus tangani 481 skip sebelum TASK-2.X lulus. -->
