# Project Memory Log

> Active Location: `.agents/instructions/memory.instructions.md`
> This file is managed by the `memory-manager` skill.
> It persists context across AI chat sessions to prevent knowledge loss.
> Do NOT manually edit this file unless necessary.

---

## 🧠 Knowledge Base

> This section accumulates cross-session knowledge that must survive compaction.
> Checkpoints for Sessions 1–6 compacted on 2026-07-24. Knowledge promoted to this section.
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

### Dead-Ends (Do NOT Repeat)

| # | Attempted | Why It Failed | Correct Solution |
|---|-----------|---------------|------------------|
| 1 | Include spacing presets in V1 | `Scripts/build.py` spacing block fully commented out — not production-ready | Defer spacing to V2 |
| 2 | Run `configure.py` inside Stage 2 Docker container | Stage 1 needs resolved args before container build (chicken-and-egg) | Run `configure.py` on host runner; pass args via `docker build --build-arg` |
| 3 | Batch `edit` with multiple hunks in one call using stale snapshot tag | A stale tag on any hunk causes partial rejection — 5 of 9 hunks silently dropped | Always re-`read` for a fresh `#TAG` before sequential multi-hunk edits; never batch hunks across stale snapshots |

### Key Metrics & Baselines

<!-- Stable metrics that serve as reference points (test counts, coverage, performance baselines). -->

---

## 📝 Session Checkpoint: 2026-07-24 (Spec Surgical Fix v1.4)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Phase Spec (Technical Specification) — Surgical Fix (post Re-Audit r2)
- **Active Artifacts:**
  - `spec/spec-custom-build-workflow.md` — Status: ✅ v1.4 (R-2 rationale + R-3 schema gap fixed)
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ v1.3 (R-1 body version fixed to 1.3)
  - `CONTEXT.md` — Status: ✅ Clean
  - `docs/adr/0002-multi-stage-docker-deferred-engine-port.md` — Status: ✅ Accepted
- **Achieved Milestones:**
  - R-2 (MEDIUM) resolved: Spec §7 line 345 corrected — "post-build packaging tooling only" + configure.py on host runner
  - R-3 (MEDIUM) resolved: Spec §4.6 `config_source` added to `required` array (between `font_files` and `spdx_license`)
  - R-1 (LOW) resolved by @ProductManagerPRD: PRD §1.1 body version `1.2` → `1.3`
  - Spec bumped v1.3 → v1.4; new §12 Revision History section created
- **Updated Files:**
  - `spec/spec-custom-build-workflow.md` — v1.3 → v1.4: 2 surgical fixes + version bump + revision history
- **Next Action / Pending:**
  - `@ArtifactConsistencyChecker` final re-audit untuk verifikasi R-1/R-2/R-3 resolved + handoff clearance
  - `@PlannerArchitect` untuk `/plan/` Implementation Plan

<!-- checkpoint-tail: Spec v1.4 finalized with R-2+R-3 fixes applied. R-1 PRD version also fixed. Ready for final re-audit then @PlannerArchitect handoff. -->

---

## 📝 Session Checkpoint: 2026-07-24 (Final Re-Audit — Spec v1.4 Handoff Clearance)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Recurring Checkpoint: Artifact Consistency Audit (Re-Audit r3, Final) — Completed
- **Active Artifacts:**
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ v1.3 (R-1 fixed — body version 1.3 matches frontmatter)
  - `spec/spec-custom-build-workflow.md` — Status: ✅ v1.4 (R-2 + R-3 fixed — rationale corrected, config_source in required array)
  - `CONTEXT.md` — Status: ✅ Clean (zero _Avoid_ body violations)
  - `docs/adr/0002-multi-stage-docker-deferred-engine-port.md` — Status: ✅ Accepted (8/8 aspects aligned, Triple Gate passed)
- **Achieved Milestones:**
  - Verified all 3 prior findings (R-1, R-2, R-3) resolved on disk via targeted re-reads
  - Full traceability re-audit: **11/11 FR** coverage, **15/15 US** coverage, **8/8 ADR-0002** alignment
  - Cross-document contradiction scan: 7 quantitative parameters — all identical across PRD/Spec
  - Zero domain-level `_Avoid_` violations across all 4 documents
  - Zero scope creep — Spec v1.4 adds zero new requirements
  - ADR-0002 Triple Gate validated: Hard to reverse ✅ | Surprising without context ✅ | Real trade-off ✅
  - **Verdict: PASS — Spec v1.4 READY FOR HANDOFF to @PlannerArchitect**
- **Non-Blocking Observations:**
  - OBS-1 (COSMETIC): PRD §1.1 body date still `2026-07-23` (not bumped when version was fixed) — DEFER
  - OBS-2 (LOW): PRD §5.3 release accumulation warning (>20) not traced to Spec — note for @PlannerArchitect
- **Decisions Made:**
  - Handoff clearance granted without reservation — zero blocker findings
  - Planner guidance: rely on Spec §4.4/§4.5/ADR-0002 for architecture; `config_source` is mandatory per §4.6 `required` array; add task for release-count warning from PRD §5.3
- **Next Action / Pending:**
  - **PRIORITAS:** Buka sesi baru → `@PlannerArchitect` untuk `/plan/` Implementation Plan dari Spec v1.4
  - Setelah Plan disetujui: `@ArtifactConsistencyChecker` (Spec v1.4 ↔ Plan), lalu `@GodModeDev` untuk Phase 6
  - OBS-1 & OBS-2 dapat difiksasi oportunistik oleh agen masing-masing

<!-- checkpoint-tail: Final re-audit PASS — Spec v1.4 cleared for @PlannerArchitect handoff. All 3 prior findings resolved. 11/11 FR, 15/15 US, 8/8 ADR, 0 _Avoid_ violations, 0 contradictions. 2 cosmetic observations noted. -->
