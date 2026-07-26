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
> Updated during Compaction Mode (Workflow 4). Do NOT delete entries here.

### Architecture & Patterns

- **Agent ↔ Skill Separation of Concerns**: Agent files define persona, scope, and rules; Skill files define workflows and templates. Agents delegate execution to skills. [Source: Session 2026-06-03, still valid]
- **Ecosystem Synchronization**: `.opencode/` is the Master Source of Truth; mirrored/adapted into `.agents/` (Antigravity) and `.github/` (Copilot) for native IDE compatibility. [Source: Session 2026-06-03, still valid]
- **SDLC Phase Gates**: Strict sequential phases (Discovery → PRD → Clarification → Spec → Clarification → Consistency → Plan → Clarification → Code → Review → Docs). Each phase requires a new chat session (Strict Session Isolation). [Source: AGENTS.md institutionalized]
- **Custom Build — configure.py on Host Runner**: `configure.py` (Python 3.14) runs on GitHub Actions host runner, not inside Docker. Passes resolved build args to Stage 1 via `docker build --build-arg BUILD_ARGS`. Stage 2 (Ubuntu 26.04 + Python 3.14) handles post-build packaging tooling only. [Source: Spec v1.4 §1.2/§4.4/§4.5/§7, ADR-0002 revision]
- **Config Precedence**: `workflow_dispatch` form input > `config.json` > build defaults. `config_source` taxonomy: `defaults` | `config.json` | `form` | `form_override`. Naming: snake_case (form), PascalCase (config.json). [Source: PRD v1.3 FR-3/FR-8, Spec v1.4 §9.1]
- **Multi-Stage Docker with Deferred Engine Port (ADR-0002)**: Stage 1 (ubuntu:18.04 + Python 2.7 + FontForge) runs legacy `build.py`/`fontbuilder`/`features` in-process. Engine port to Python 3.14 deferred to V2 because `build.py` imports both in-process (`from fontbuilder import *`). [Source: ADR-0002, Spec v1.4 §7]
- **Bilingual Glossary Convention**: English `_Avoid_` lists in `CONTEXT.md` govern English-language documents (PRD, Spec, ADR body). Indonesian canonical terms are authoritative for Indonesian-language content. Cross-check both language surfaces during audits. [Source: Re-Audit r2, 2026-07-24]
- **Terminology Fix Propagation**: `_Avoid_` violations are contagious across SDLC artifacts. Fixing one document requires checking PRD, Spec, and CONTEXT.md together, plus updating audit reports with resolution logs. The same forbidden synonyms apply globally. [Source: Sessions 2026-07-24 Terminology Revisions]
- **Re-audit Pattern (After-Finding-Closure)**: When a finding is closed via document update (e.g., Plan v1.1 → v1.2), always perform a re-audit before approving the next SDLC phase. Re-audit focuses on: (1) deltas verification, (2) no-regression check, (3) section alignment (e.g., RISK-006 mitigation ↔ TASK-010 owner). Result: PASS bersih (tanpa "WITH WARNINGS") gives cleaner gate to next phase. [Source: Session 2026-07-26, still valid]
- **Single Audit Report Pattern**: For re-audits, update the original audit file in-place (add new section, renumber subsequent sections) rather than creating a new file. Preserves audit trail continuity; subsequent readers see both initial audit and re-audit in chronological order. [Source: Session 2026-07-26, still valid]
- **Delta Verification Pattern (Version-Increment Audit)**: For audit on Plan v1.X → v1.Y, focus on three things: (1) **Deltas** — verify every promised change is actually applied (frontmatter version, filename rename, task description expansion, Ref ID update); (2) **No-Regression** — verify sections NOT updated (e.g., §3 Alternatives, §4 Dependencies, §7 Risks) remain identical; (3) **Cross-Section Alignment** — e.g., RISK-006 mitigation text must match with the TASK that now owns the action. [Source: Session 2026-07-26, still valid]
- **Plan File Rename+Version Bump Protocol**: When user chooses "formal Plan update" option (e.g., FINDING-001 closure via v1.1 → v1.2), not enough to just edit file contents — must also: (1) rename file from `*-v1.1.md` to `*-v1.2.md`, (2) bump `version:` in frontmatter, (3) verify filename ↔ frontmatter version consistency. Failure to rename = file version mismatch that confuses next auditor. [Source: Session 2026-07-26, still valid]
- **User Override Priority (AGENTS.md Rule #1)**: Explicit user command overrides role boundaries. Example: `@ArtifactConsistencyChecker` normally cannot edit Plan documents, but user choice "Update Plan v1.1 secara formal (Opsi A1)" overrides that rule. Always confirm via ask_user_question before performing override. [Source: Session 2026-07-26, still valid]

### Dead-Ends (Do NOT Repeat)

| # | Attempted | Why It Failed | Correct Solution |
|---|-----------|---------------|------------------|
| 1 | Include spacing presets in V1 | `Scripts/build.py` spacing block fully commented out — not production-ready | Defer spacing to V2 |
| 2 | Run `configure.py` inside Stage 2 Docker container | Stage 1 needs resolved args before container build (chicken-and-egg) | Run `configure.py` on host runner; pass args via `docker build --build-arg` |
| 3 | Batch `edit` with multiple hunks in one call using stale snapshot tag | A stale tag on any hunk causes partial rejection — 5 of 9 hunks silently dropped | Always re-`read` for a fresh `#TAG` before sequential multi-hunk edits; never batch hunks across stale snapshots |
| 4 | Write Spec CLI contract against a code file without verifying its actual interface | Spec v1.4 §4.4 specified `--line-height`/`--no-loop-k`/`--no-calt` flags targeting `Scripts/build.py`, which accepts only 4 positional args (`<parallel> <batch> <sfdir> <output_dir>`), declares options via `option()`/`conflicting()` in the script body, and had the `NoCalt` declaration commented out. No CLI/env option-selection mechanism existed. CON-001 forbade modifying the file — contract was unimplementable. Blocked planning; found during codebase review. | Always verify actual code interfaces (sys.argv handling, function signatures, config mechanisms) before writing contracts against them. When the target cannot be modified, create a NEW wrapper/driver script that imports the legacy module primitives and implements the contract. |

### Key Metrics & Baselines

<!-- Stable metrics that serve as reference points (test counts, coverage, performance baselines). -->

---

## 📝 Session Checkpoint: 2026-07-24 (Plan v1.0) — COMPACTED 2026-07-26

> Original checkpoint compacted on 2026-07-26 after re-audit cycle completion. Key knowledge already promoted to Knowledge Base (see §3 entry "Re-audit Pattern" + Dead-End #4 + Architecture & Patterns: "Custom Build — configure.py on Host Runner", "Config Precedence", "Multi-Stage Docker with Deferred Engine Port (ADR-0002)"). The "Plan v1.0 completed" status is preserved for historical context only — superseded by Plan v1.2 (post-re-audit).

<!-- checkpoint-tail: [COMPACTED 2026-07-26] Plan v1.0 historical reference only. Superseded by Plan v1.2. KB entries preserved. -->

## 📝 Session Checkpoint: 2026-07-26 (Plan v1.0 Clarification — Phase Completed)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Previous Phase:** Plan v1.0 (2026-07-24) → Clarification (2026-07-26) — completed
- **Current SDLC Phase:** Post-Clarification — awaiting Plan v1.1 increment + Consistency Check
- **Active Artifacts:**
  - `docs/audit/clarification-report-plan-custom-build-workflow-2026-07-26.md` — Status: ✅ NEW (16,303 bytes; 10 findings, 9 resolved/closed/positive, 1 user-handled)
  - `plan/plan-feature-custom-build-workflow-v1.0.md` — Status: ⏳ Awaiting v1.1 increment (4 Plan updates from clarification)
  - `spec/spec-custom-build-workflow.md` — Status: ✅ v1.5 (no changes)
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ v1.3 (used for F-5..F-10 validation)
- **Achieved Milestones:**
  - **F-1 false positive caught + corrected** (typo `UseHinUseHinted` tidak ada di Plan line 84; agen rekonstruksi teks dari memori) — lesson learned dipromosikan ke KB.
  - **F-2 resolved (Opsi A)** — suffix logic preskriptif: ` (default)` hanya saat `Normal` AND `config_source=="defaults"`; ` (unhinted)` saat `UseHinted==false`.
  - **F-4 resolved by F-2** — kasus `Normal` + `form` (tanpa suffix) otomatis ter-cover oleh aturan Opsi A.
  - **F-5, F-6, F-8, F-10 validated as non-findings** via PRD v1.3 cross-reference (semua anchor valid; Plan conform).
  - **F-3 user-handled** — release body content verification di-defer ke user @ 2026-07-26.
  - **F-7, F-9 positive confirmations** — gate `calt/liga` lookup dan `ttx` parity sudah ada di Plan; tidak ada gap.
  - **Re-analysis metodologis** — PRD injeksi pertengahan sesi meruntuhkan mayoritas findings; lesson: selalu include PRD/anchor PRD dalam klarifikasi Plan.
- **Decisions Made:**
  - 5 grill questions (F-2, F-5, F-6, F-8, F-10) seluruhnya Opsi A (lightest-touch, delegate ke konsistensi check atau documentation note).
  - F-3 user-handled di luar sesi Clarification.
  - Tidak ada update `CONTEXT.md` (tidak ada canonical term baru).
  - Tidak ada ADR baru (tidak ada keputusan arsitektur yang memenuhi Triple Gate).
- **Updated Files:**
  - `docs/audit/clarification-report-plan-custom-build-workflow-2026-07-26.md` — NEW (16,303 bytes)
  - `.agents/instructions/memory.instructions.md` — appending this checkpoint
- **Next Action / Pending:**
  - **PRIORITAS #1:** Buka sesi baru → `@PlannerArchitect` untuk Plan v1.1 increment (4 items):
    - TASK-041 diperbarui dengan suffix logic preskriptif (F-2 Opsi A + F-4 deklarasi eksplisit)
    - TASK-027 ditambah catatan retention default GitHub (F-6 Opsi A)
    - TASK-029 ditambah `act` invocation fallback (F-8 Opsi A)
    - `§7 Risks & Assumptions` dokumentasi `ttx` parity gate (F-9)
  - **PRIORITAS #2:** User mengeksekusi F-3 (body content assertions di TASK-044) di luar sesi Clarification — out-of-scope.
  - **PRIORITAS #3:** Buka sesi baru → `@ArtifactConsistencyChecker` dengan baseline **baru** (PRD v1.3 ↔ Spec v1.5 ↔ Plan v1.1) — JANGAN gunakan baseline v1.4↔v1.4.
  - **PRIORITAS #4:** `@GodModeDev` eksekusi Plan v1.1 Phase 1-6 dengan gate per fase.
- **Lessons Learned (KB candidates for next compaction):**
  1. **Always include PRD/PRD anchor in Plan/Spec clarification analysis** — tanpa PRD, coverage validasi turun ~30%.
  2. **Always targeted re-read (via `grep` atau `read` selector) before literal citation** — rekonstruksi dari memori audit = risiko false positive (F-1 case).
  3. **Re-analysis after PRD injection may collapse many findings** — design grill untuk iteratif, bukan one-shot.
  4. **"Saya tangani" = literal scope only** — jangan over-extend ke findings berikutnya saat user defer satu finding tertentu.

<!-- checkpoint-tail: Plan v1.0 Clarification completed 2026-07-26. 9 of 10 findings resolved/closed/positive; 1 (F-3) deferred to user. Plan v1.1 increment (4 items) + F-3 user-handled before @ArtifactConsistencyChecker. Baseline baru: PRDv1.3↔Specv1.5↔Planv1.1. -->

## 📝 Session Checkpoint: 2026-07-26 (Consistency Audit — Phase Completed, Plan v1.1 → v1.2)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Previous Phase:** Plan v1.0 Clarification (2026-07-26) — completed
- **Current SDLC Phase:** Consistency Check — completed (with re-audit scheduled for v1.2)
- **Active Artifacts:**
  - `docs/audit/consistency-audit-custom-build-workflow-2026-07-26.md` — Status: ✅ NEW (8 sections, 2 enhanced sections at user request)
  - `plan/plan-feature-custom-build-workflow-v1.2.md` — Status: ✅ NEW (renamed from v1.1; TASK-010 expanded with `SOURCE_DATE_EPOCH` per PRD US-015; version bumped)
  - `plan/plan-feature-custom-build-workflow-v1.1.md` — Status: ⚠️ Superseded (renamed to v1.2; original content preserved in v1.2)
  - `spec/spec-custom-build-workflow.md` — Status: ✅ v1.5 (no changes)
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ v1.3 (no changes)
  - `docs/audit/clarification-report-plan-custom-build-workflow-2026-07-26.md` — Status: ✅ Verified (all 5 Plan-update recommendations absorbed in v1.1)
- **Achieved Milestones:**
  - **Tri-directional audit completed** (PRD v1.3 ↔ Spec v1.5 ↔ Plan v1.1) with 5 audit dimensions: (1) traceability, (2) orphaned items, (3) contradictions, (4) standards compliance, (5) ADR Triple Gate + `_Avoid_` synonym.
  - **Result: PASS WITH WARNINGS** — 0 FAIL/CRITICAL, 2 minor findings.
  - **Verification matrix populated:** 11 FR + 15 US + 7 REQ + 3 CON + 3 GUD/SEC + 5 AC all traced from PRD → Spec → Plan tasks. 12-parameter contradiction check (defaults, tag format, retry, enum, Docker, license) all consistent.
  - **5 Clarification Report recommendations verified absorbed:** F-2 (suffix logic), F-4 (Normal+form case), F-6 (retention note), F-8 (act fallback), F-9 (ttx parity gate documentation).
  - **FINDING-001 closed via formal Plan update (Opsi A1):** Added `SOURCE_DATE_EPOCH` to TASK-010 description; updated `Ref ID` to include US-015; Plan v1.1 → v1.2.
  - **Audit report enhanced per user request:** Added §7 Positive Findings (31 items across 5 categories: structure/traceability, resilience, domain language, documentation standards, execution/testing) and §8 Specific Line Citations (7 mapping tables: findings, requirements, AC, clarification report, manifest fields, ADR Triple Gate, glossary usage).
- **Decisions Made:**
  - Chose Opsi A1 (formal Plan update for FINDING-001) over Opsi A2 (Docker step) or A3 (defer to micro-fix in Phase 2) — keeps Plan v1.1 → v1.2 increment traceable and auditable.
  - **Re-audit scheduled in NEW session** (per Strict Session Isolation) before invoking `@GodModeDev`.
  - **F-3 (body content assertions) remains user-owned** per Clarification Report — user must complete before/during Phase 4.
- **Updated Files:**
  - `plan/plan-feature-custom-build-workflow-v1.1.md` → renamed to `plan/plan-feature-custom-build-workflow-v1.2.md`; TASK-010 expanded; frontmatter version bumped
  - `docs/audit/consistency-audit-custom-build-workflow-2026-07-26.md` — NEW (~32,000 bytes after §7 + §8 enhancements)
  - `.agents/instructions/memory.instructions.md` — appending this checkpoint
- **Dead-Ends (Do NOT Repeat):**
  - **Attempted:** Use Windows `find` command without restricting search path to verify audit file write.
  - **Reason:** Without explicit path scoping, `find` scanned the entire C:\ drive including Windows SxS folders (2.5M+ files), producing useless output. Recovered by using `read` with offset/limit to verify file structure instead.
  - **Note:** Bash shell `find` on Windows without `--path` scoping is dangerous. Use targeted `ls` or `read` for file verification.
- **Lessons Learned (KB candidates for next compaction):**
  1. **Audit reports benefit from Positive Findings section** — balances the "warning-heavy" tone of pure audit documents; preserves institutional knowledge of "what we're doing right" alongside gaps.
  2. **Specific Line Citations transform audit reports into re-verification indexes** — auditor berikutnya dapat langsung menavigasi ke baris spesifik tanpa membaca ulang seluruh dokumen; massively improves re-audit velocity.
  3. **Plan file rename + version bump is part of formal update protocol** — when user chooses "formal update" option, also rename file (v1.1 → v1.2) to keep filename and frontmatter version consistent.
  4. **Per AGENTS.md Rule #1, user explicit choice overrides role boundaries** — @ArtifactConsistencyChecker normally tidak boleh edit Plan documents, tapi user command eksplisit ("Update Plan v1.1 secara formal") override aturan tersebut.
- **Next Action / Pending:**
  - **PRIORITAS #1:** Buka sesi baru → `@ArtifactConsistencyChecker` untuk **re-audit Plan v1.2** (verify SOURCE_DATE_EPOCH addition + nothing regressed). Baseline: `PRD v1.3 ↔ Spec v1.5 ↔ Plan v1.2`. Target status: PASS bersih (tanpa "WITH WARNINGS") karena FINDING-001 sudah tertutup.
  - **PRIORITAS #2:** User menyelesaikan F-3 (body content assertions di TASK-044) di luar sesi audit — masih user-owned.
  - **PRIORITAS #3:** Setelah re-audit PASS + F-3 selesai → buka sesi baru → `@GodModeDev` eksekusi Plan v1.2 Phase 1-6 dengan gate per fase (TASK-009, TASK-014, TASK-030, TASK-045, TASK-053, TASK-064).
  - AGENTS.md Memory Configuration "Last Recorded" masih 2026-07-24 — user akan update manual jika diperlukan (skill rule: tidak boleh auto-update tanpa consent).

<!-- checkpoint-tail: Consistency Audit completed 2026-07-26 → Plan v1.1 updated to v1.2 (FINDING-001 closed via formal TASK-010 expansion); FINDING-002 (F-3) remains user-owned. Audit report saved with 8 sections (incl. positive findings + line citations). Next: re-audit v1.2 in new session → @GodModeDev execution. -->

## 📝 Session Checkpoint: 2026-07-26 (Re-Audit Plan v1.2 — PASS Clean, Audit File Updated)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Previous Phase:** Consistency Audit (2026-07-26, v1.1) — completed
- **Current SDLC Phase:** Re-Audit (post-FINDING-001 closure) — completed; READY for Code phase
- **Active Artifacts:**
  - `docs/audit/consistency-audit-custom-build-workflow-2026-07-26.md` — Status: ✅ UPDATED (8 sections + new §6 Re-Audit Delta Verification; 12 coordinated edits applied)
  - `plan/plan-feature-custom-build-workflow-v1.2.md` — Status: ✅ v1.2 (FINDING-001 closed)
  - `spec/spec-custom-build-workflow.md` — Status: ✅ v1.5 (unchanged)
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ v1.3 (unchanged)
  - `docs/audit/clarification-report-plan-custom-build-workflow-2026-07-26.md` — Status: ✅ Verified (F-3 still user-owned)
- **Achieved Milestones:**
  - **Re-audit completed** on Plan v1.2 (delta verification + no-regression check + RISK-006↔TASK-010 alignment).
  - **FINDING-001 formally closed** — 4 dari 4 closure aspects verified (task eksplisit, US-015 traceability, byte-identity disclaimer consistency, RISK-006 mitigation ownership).
  - **Zero regression terverifikasi** — 12 sections of Plan v1.2 confirmed identical to v1.1 except TASK-010 expansion.
  - **Overall status changed**: PASS WITH WARNINGS → **PASS bersih** (zero in-scope findings; F-3 tetap user-owned di luar scope Plan).
  - **Audit file updated** with new §6 Re-Audit Delta Verification (5 sub-sections: Deltas, Closure, Alignment, No-Regression, Re-Audit Verdict); subsequent §6-§8 renumbered to §7-§9.
- **Decisions Made:**
  - **Single Audit Report Pattern applied** — updated existing audit file in-place rather than creating a new re-audit file (preserves audit trail continuity).
  - **Memory compaction** — promoted 5 new patterns to Knowledge Base (Re-audit, Single Audit Report, Delta Verification, Plan File Rename+Version Bump, User Override Priority). Compacted 2026-07-24 (Plan v1.0) checkpoint to one-liner after key knowledge already in KB.
- **Updated Files:**
  - `docs/audit/consistency-audit-custom-build-workflow-2026-07-26.md` — 12 coordinated edits (~32KB final)
  - `plan/plan-feature-custom-build-workflow-v1.1.md` → renamed to `plan-feature-custom-build-workflow-v1.2.md`
  - `plan/plan-feature-custom-build-workflow-v1.2.md` — TASK-010 expanded; frontmatter version bumped
  - `.agents/instructions/memory.instructions.md` — this checkpoint + KB updates + old checkpoint compaction
  - `AGENTS.md` — Memory Configuration `Last Recorded` updated to 2026-07-26
- **Next Action / Pending:**
  - **PRIORITAS #1:** Buka sesi baru → `@GodModeDev` untuk eksekusi Plan v1.2 Phase 1–6 (TASK-001 s.d. TASK-064) dengan gate per fase (TASK-009, TASK-014, TASK-030, TASK-045, TASK-053, TASK-064).
  - **PRIORITAS #2:** User menyelesaikan F-3 (body content assertions di TASK-044) sebelum/saat eksekusi Phase 4 — masih user-owned per Clarification Report 2026-07-26.
  - **Sesi ini ditutup** — semua aksi audit telah selesai; berikutnya adalah transisi ke Code phase di sesi baru.

<!-- checkpoint-tail: Re-Audit Plan v1.2 PASS clean (zero in-scope findings; F-3 user-owned). All artifacts ready for Code phase. Next: @GodModeDev in new session, F-3 user-completion before/during Phase 4. -->
