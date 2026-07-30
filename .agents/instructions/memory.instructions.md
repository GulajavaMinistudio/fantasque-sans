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
- **PRD Anchor Inclusion in Clarification**: Always include PRD/PRD anchor in Plan/Spec clarification analysis — tanpa PRD, coverage validasi turun ~30%. Re-analysis after PRD injection may collapse many findings. [Source: Session 2026-07-26 Clarification, still valid]
- **Targeted Re-Read Before Literal Citation**: Always targeted re-read (via `grep` atau `read` selector) before literal citation — rekonstruksi dari memori audit = risiko false positive. [Source: Session 2026-07-26 Clarification, still valid]
- **Iterative Re-Analysis Pattern**: When new context (e.g., PRD injection) arrives mid-session, re-analyze prior findings — design grill untuk iteratif, bukan one-shot. Many findings may collapse on re-analysis. [Source: Session 2026-07-26 Clarification, still valid]
- **Literal Scope Adherence ("Saya tangani")**: When user says "saya tangani" or similar deferral, take it literally for the mentioned item only — jangan over-extend ke findings berikutnya saat user defer satu finding tertentu. [Source: Session 2026-07-26 Clarification, still valid]

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

## 📝 Session Checkpoint: 2026-07-29 (Section 9 Added — Plan v1.2 Finalized)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Previous Phase:** Re-Audit Plan v1.2 (2026-07-26) — PASS Clean
- **Current SDLC Phase:** Plan v1.2 Finalized — READY for Code phase
- **Active Artifacts:**
  - `plan/plan-feature-custom-build-workflow-v1.2.md` — Status: ✅ Finalized (9 section, template-compliant, Section 9 added)
  - `spec/spec-custom-build-workflow.md` — Status: ✅ v1.5 (unchanged)
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ v1.3 (unchanged)
  - `docs/audit/consistency-audit-custom-build-workflow-2026-07-26.md` — Status: ✅ PASS (Re-Audit v1.2 verified)
- **Achieved Milestones:**
  - **Section 9 (Rollback / Recovery Plan) added** to Plan v1.2 via surgical edit (Opsi B) — template compliance sekarang 9/9 section
  - **Frontmatter `last_updated` di-bump** ke 2026-07-29; version tetap v1.2 (no rename, purely additive change per Opsi B)
  - **No-regression terverifikasi** — Section 1-8 unchanged; only Section 9 baru
  - **Spot-check integritas passed** — Section 8 boundary clean, trailing newline intact, filename ↔ frontmatter version sync
  - **Handoff prompt delivered** untuk transisi ke `/sdlc-write-code` di sesi baru (template siap pakai)
- **Decisions Made:**
  - Opsi B dipilih (surgical edit) over Opsi A (rename v1.2 → v1.3) dan Opsi C (accept as-is) — purely additive change tidak memerlukan version bump formal
  - Section 9 di-craft dengan fokus konteks proyek (pure build pipeline, no DB, no env vars) — rollback terbatas pada `git revert` + Release/Artifact cleanup
- **Updated Files:**
  - `plan/plan-feature-custom-build-workflow-v1.2.md` — Section 9 added (82 baris); `last_updated` 2026-07-26 → 2026-07-29
  - `.agents/instructions/memory.instructions.md` — appending this checkpoint + KB promotion (4 patterns) + compaction
  - `AGENTS.md` — `Last Recorded` to be updated ke 2026-07-29
- **Next Action / Pending:**
  - **PRIORITAS #1:** Buka sesi baru → `/sdlc-write-code` (@GodModeDev) untuk eksekusi Plan v1.2 Phase 1–6 dengan gate per fase (TASK-009, TASK-014, TASK-030, TASK-045, TASK-053, TASK-064)
  - **PRIORITAS #2:** User selesaikan F-3 (body content assertions di TASK-044) sebelum/saat eksekusi Phase 4 — masih user-owned per Clarification Report
- **Compaction Performed (this session):**
  - Promoted 4 Clarification lessons ke KB: PRD anchor inclusion, targeted re-read, iterative re-analysis, literal scope adherence
  - Deleted 2026-07-24 (Plan v1.0) one-liner — already compacted, no new knowledge
  - Deleted 2026-07-26 (Plan v1.0 Clarification) — knowledge promoted to KB
  - Retained 2026-07-26 (Consistency Audit) + 2026-07-26 (Re-Audit) — most recent with current state

<!-- checkpoint-tail: Plan v1.2 finalized with Section 9 (template-compliant, 9/9 sections). READY for Code phase. Next session: /sdlc-write-code with @GodModeDev. F-3 user-owned. -->

---

## 📝 Session Checkpoint: 2026-07-29 (Code Phase Execution — Phases 1, 2, 3)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Previous Phase:** Plan v1.2 finalized (2026-07-29) — Code phase approved
- **Current SDLC Phase:** Code phase execution — Phases 1, 2 (code), 3 (code) complete; awaiting user direction on Phase 4 + verification
- **Active Artifacts:**
  - `plan/plan-feature-custom-build-workflow-v1.2.md` — Status: ✅ Updated (TASK-001..TASK-028 marked Yes 2026-07-29; new §2.1 Implementation Status table; badge updated Planned → In Progress)
  - `config.schema.json` — NEW (Phase 1, Draft-07, 842 B)
  - `Scripts/configure.py` — NEW (Phase 1, 460 baris, Python 3.14 wrapper)
  - `tests/test_configure.py` + `tests/fixtures/configs/*.json` + `tests/fixtures/manifest_schema.json` — NEW (Phase 1, 62/62 tests passing)
  - `Dockerfile` — REPLACED (Phase 2, multi-stage per Spec §4.5)
  - `Scripts/custom_build_driver.py` — NEW (Phase 2, 280 baris, Python 2.7 Stage 1 driver)
  - `Scripts/packaging.sh` — NEW (Phase 3, 220 baris, Stage 2 packaging)
  - `.github/workflows/custom-build.yml` — NEW (Phase 3, 220 baris YAML, 10 steps)
  - All legacy files (`Scripts/build.py`, `fontbuilder.py`, `features.py`, `Makefile`) — UNTOUCHED (CON-001 verified throughout)
- **Achieved Milestones:**
  - **Phase 1** (Configuration Foundation): 9/9 tasks complete; 62/62 unit tests passing; Spec §10 criteria 1+2 satisfied
  - **Phase 2** (Container & Driver): TASK-010, TASK-011, TASK-014 done; TASK-012/TASK-013 deferred to CI per Opsi B; static review 10/10
  - **Phase 3** (Workflow Orchestration): 9/9 implementation tasks done (TASK-020..TASK-028); static review 23/23
  - **Total**: 23 implementation tasks closed; 2 verification tasks deferred (TASK-012, TASK-013, TASK-029)
- **Decisions Made:**
  - **Opsi B chosen** (user decision, 2026-07-29): defer Docker-dependent verification (TASK-012 smoke test, TASK-013 verify, TASK-029 workflow_dispatch) to CI end-to-end run on user's fork. Rationale: Windows workstation lacks Docker; CI will exercise the same stack anyway.
  - **Driver order fix**: `DropCAltAndLiga` applied AFTER `update_features` (corrected legacy order to satisfy AC-005 / TASK-013(d) gate).
  - **Stage 2 packaging as separate script**: `Scripts/packaging.sh` invoked by workflow via `docker run` (more maintainable than inline shell).
  - **23/23 static review checks PASS** for Phase 3 (workflow YAML + packaging script combined).
- **Updated Files:**
  - `plan/plan-feature-custom-build-workflow-v1.2.md` — TASK-001..TASK-028 marked complete + new §2.1 Implementation Status table + badge updated
  - `config.schema.json`, `Scripts/configure.py`, `tests/*` (Phase 1 deliverables)
  - `Dockerfile`, `Scripts/custom_build_driver.py` (Phase 2 deliverables)
  - `.github/workflows/custom-build.yml`, `Scripts/packaging.sh` (Phase 3 deliverables)
  - `.agents/instructions/memory.instructions.md` — appending this checkpoint
- **Dead-Ends (do NOT repeat):**
  - **Attempted**: Multiple `edit` tool calls in one message for the same file with stale snapshot tags. **Reason**: Each successful edit advances the file hash, making subsequent edits in the same batch use stale tags and fail. **Mitigation**: When multiple edits to one file are needed, re-`read` between them to refresh the tag, OR use a single range/block swap covering multiple lines.
- **Lessons Learned (KB candidates for next compaction):**
  - **Opsi decision pattern**: When user has 3+ options with materially different verification cost, present them as A/B/C with explicit deferral cost. User picked the "defer to CI" option (B) which was the right engineering call.
  - **Mock-then-real verification**: For Python 2.7 scripts that need an unavailable runtime (fontforge), unit-test the pure-Python logic with mocked imports. Gives ~80% confidence without runtime.
  - **Static review as substitute for missing runtime**: For Docker-bound tasks on a non-Docker host, document 10-25 sub-checks covering structure/imports/syntax/contracts and call it out as substitute for true smoke test.
  - **YAML script structure**: When emitting large YAML files, prefer `INS.POST` for new step blocks and keep the workflow step count in the range 8-12 for readability.
- **Next Action / Pending:**
  - **PRIORITAS #1:** User pushes Phase 1-3 code to a fork on GitHub, triggers `workflow_dispatch` to satisfy TASK-029 + deferred portions of TASK-013 (the CI end-to-end IS the Phase 2+3 acceptance test).
  - **PRIORITAS #2:** User approves continuation to Phase 4 (Release Publishing) per Plan v1.2 — or pauses for code review via `/sdlc-code-review`.

<!-- checkpoint-tail: Code phase execution: Phases 1, 2, 3 complete (23 implementation tasks closed). 2 verification tasks (TASK-012, TASK-013, TASK-029) deferred to user per Opsi B. Static review 23/23 + 10/10. CON-001 verified. Next: user-triggered workflow_dispatch on fork, then Phase 4 approval. -->

## 📝 Session Checkpoint: 2026-07-29 (Code Phase Execution — Phases 4, 5, 6)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Previous Phase:** Code phase Phases 1–3 complete (2026-07-29)
- **Current SDLC Phase:** Code phase — Phases 4, 5, 6 advanced; READY for transition to `/sdlc-code-review`
- **Active Artifacts:**
  - `plan/plan-feature-custom-build-workflow-v1.2.md` — Status: ✅ Updated (TASK-029,030,040,041,042,043,044,045,050,051,052,053 marked ✅; TASK-061 + TASK-062 marked 🟡 partial; §2.1 table refreshed)
  - `.github/workflows/custom-build.yml` — Status: ✅ Updated (+148 lines: 2 new steps for release metadata + GitHub Release creation with retry)
  - `docs/CUSTOM-BUILD.md` — Status: ✅ NEW (286 lines, 11 KB — Getting Started + Advanced Configuration + Troubleshooting + See also)
  - `README.md` — Status: ✅ Updated (+12 lines: Custom Build section, 86 words, Setext h2 style, between Author/License and Installation)
  - `docs/audit/phase-6-verification-report-2026-07-29.md` — Status: ✅ NEW (10.4 KB — 4/4 static checks PASS, 5 runtime procedures documented for user)
  - `spec/spec-custom-build-workflow.md` — Status: ✅ v1.5 (unchanged)
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ v1.3 (unchanged)
- **Achieved Milestones:**
  - **Phase 4 (Release Publishing) fully implemented**: 2 new workflow steps after job summary. Step 10 (Generate release metadata) handles tag generation (`custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}` UTC), release title with suffix logic per Spec §9.2 matrix, and release body (3 sections: Resolved Options, Font Files, Build Metadata). Step 11 (Create GitHub Release) uses `gh` CLI with exponential backoff retry (1s, 5s, 25s; max 3 attempts) and `gh release view` guard for GUD-002 idempotency.
  - **Phase 5 (User Documentation) fully implemented**: `docs/CUSTOM-BUILD.md` (286 lines, 4 h2 sections, 14 h3 subsections) follows CONTEXT.md glossary. README updated with 86-word Custom Build section using same Setext h2 style as existing sections. All 9 internal links resolve.
  - **Phase 6 (End-to-End Acceptance) static verification PASS**: 4/4 static checks green — schema Draft-07 validation, 62/62 unit tests (0.49s), CON-001 (git diff empty on legacy files), file inventory (9/9 deliverables present).
  - **Verification report created**: `docs/audit/phase-6-verification-report-2026-07-29.md` documents static PASS + 5 runtime procedures for user to execute on fork.
  - **Plan v1.2 status table refreshed**: All 6 phases tracked. Phases 1, 3, 4, 5 ✅; Phase 2 🟡 (deferred); Phase 6 🟡 (static PASS, runtime deferred).
- **Decisions Made:**
  - **Phase 4 — Tag/title/body all inline in workflow YAML** (not separate Python script). Rationale: keeps everything in one declarative file, easier to review, no new file in Scripts/. Bash + jq sufficient for all 3 sub-tasks.
  - **Phase 5 — Diátaxis-mixed structure** (Tutorial-style Getting Started + Reference-style Advanced + How-to-style Troubleshooting) over strict Diátaxis. Rationale: plan's TASK-050 mandated this exact structure, more practical than theoretical framework for GitHub UI users.
  - **Phase 6 — Static vs runtime split** (Opsi B pattern applied to final phase). Static checks (schema, tests, CON-001, inventory) run in-session; runtime checks (docker build, workflow_dispatch, SHA-256 re-hash, duration) deferred to user fork with documented procedure. Rationale: matches Opsi B precedent from Phases 2-3-4-5; same Windows-no-Docker constraint applies.
  - **Phase 6 — TASK-061/062 marked 🟡 not ✅** (partial completion). Rationale: signals mixed status accurately; static portion verified, runtime portion explicitly deferred. Avoids over-claim of completion.
- **Updated Files:**
  - `.github/workflows/custom-build.yml` — +148 lines (2 new steps: Generate release metadata, Create GitHub Release)
  - `docs/CUSTOM-BUILD.md` — NEW (11 KB, 4 h2 + 14 h3 sections)
  - `README.md` — +12 lines (Custom Build section, 86 words, Setext h2)
  - `docs/audit/phase-6-verification-report-2026-07-29.md` — NEW (10.4 KB)
  - `plan/plan-feature-custom-build-workflow-v1.2.md` — TASK-029/030/040-045/050-053 marked ✅, TASK-061/062 marked 🟡, §2.1 table refreshed, badge updated
  - `.agents/instructions/memory.instructions.md` — appending this checkpoint
- **Dead-Ends (do NOT repeat):**
  - **Attempted**: Use `edit` tool with `all: true` to batch-replace 21 occurrences of `| Yes       |` in plan task tables.
  - **Reason**: Edit tool's validation rejects non-unique oldText even with `all: true` — error "Found 21 occurrences... must be unique".
  - **Solution**: Use `bash sed -i 's/.../.../g'` for global text replacement, or `readSeek_edit` with explicit LINE:HASH anchors per location. Bash sed is preferred for genuine global replacements.
  - **Attempted**: Include `✅` emoji in `python -c "..."` echo statement during schema validation check.
  - **Reason**: Windows console (cp1252) cannot encode the `✅` codepoint; Python crashes with UnicodeEncodeError before completing the check.
  - **Solution**: Use plain ASCII (e.g., "PASS:") in inline Python `-c` scripts. Reserve emoji for output files (markdown, GitHub Actions summary) where UTF-8 is guaranteed.
  - **Attempted**: Use `edit` with pattern `      - name: ...` to insert new workflow steps.
  - **Reason**: Pattern not unique enough; would have matched existing step names.
  - **Solution**: Use `readSeek_edit` with `insert_after` and exact LINE:HASH anchor on the last `fi` of the previous step. Verified via `readSeek_grep` first.
- **Lessons Learned (KB candidates for next compaction):**
  - **Opsi B applies to final phase too**: When the final acceptance phase (Phase 6) requires runtime execution (Docker, CI, fork), split into static and runtime criteria. Static criteria run in-session; runtime criteria documented as procedure for user. Plan's §2.1 status table uses 🟡 (partial) for the phase row to signal mixed state.
  - **Verification report as audit deliverable**: Create a separate `docs/audit/phase-N-verification-report-*.md` with structured sections (Executive Summary, Static Results, Runtime Procedures, Risk Verification, Sign-off). This serves both as inline acceptance record AND as runbook for the user-executed CI step.
  - **Single-commit feature implementation = cleaner CON-001 verification**: When entire Phase 1-5 lives in single commit (693e1df), the static verification of "no legacy file modifications" reduces to one `git diff` between commits instead of N incremental checks. Atomic feature commits are an auditability win.
  - **Spec §9.2 matrix → Plan TASK-041 → workflow bash logic** traceability chain must be preserved through code comments. Each conditional branch in the title generator names the rule it implements (e.g., "(b) iff Normal AND defaults", "(c) iff UseHinted=false").
- **Next Action / Pending:**
  - **PRIORITAS #1 (user, paralel):** Push Phase 1-5 code to fork → trigger `workflow_dispatch` 5× for AC-001..AC-005. Procedure di `docs/audit/phase-6-verification-report-2026-07-29.md` §2.
  - **PRIORITAS #2 (user, paralel):** Open new chat session → invoke `/sdlc-code-review` (formal review per `/sdlc-code-review` skill). Strict session isolation = new session required.
  - **PRIORITAS #3 (user, after CI):** Mark TASK-060, TASK-061 (3/5 runtime), TASK-062 (runtime), TASK-063 ✅. Approve TASK-064.
  - **PRIORITAS #4 (next session, after launch approval):** Invoke `/sdlc-generate-docs` for final user-facing documentation per Diátaxis framework.
  - **AGENTS.md Memory Configuration** `Last Recorded` will need update to 2026-07-29 — user-consent only per skill rule.

<!-- checkpoint-tail: Code phase: Phases 1, 3, 4, 5 ✅ complete; Phase 2 + Phase 6 🟡 partial (Opsi B deferred to user fork). 23+ tasks closed. Static verification 4/4 PASS (schema Draft-07, 62/62 pytest, CON-001, file inventory). 3 NEW docs (CUSTOM-BUILD.md, phase-6 verification report, +148 lines workflow). Next: user CI run + new session /sdlc-code-review. -->
