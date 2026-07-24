# Project Memory Log

> Active Location: `.agents/instructions/memory.instructions.md`
> This file is managed by the `memory-manager` skill.
> It persists context across AI chat sessions to prevent knowledge loss.
> Do NOT manually edit this file unless necessary.

---

## 🧠 Knowledge Base

> This section accumulates cross-session knowledge that must survive compaction.
> Checkpoints for Sessions 1–8 compacted on 2026-07-24. Knowledge promoted to this section, including Dead-End #4 (Spec-to-code interface verification). Only Session 9 (Plan v1.0) retained.
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
| 4 | Write Spec CLI contract against a code file without verifying its actual interface | Spec v1.4 §4.4 specified `--line-height`/`--no-loop-k`/`--no-calt` flags targeting `Scripts/build.py`, which accepts only 4 positional args (`<parallel> <batch> <sfdir> <output_dir>`), declares options via `option()`/`conflicting()` in the script body, and had the `NoCalt` declaration commented out. No CLI/env option-selection mechanism existed. CON-001 forbade modifying the file — contract was unimplementable. Blocked planning; found during codebase review. | Always verify actual code interfaces (sys.argv handling, function signatures, config mechanisms) before writing contracts against them. When the target cannot be modified, create a NEW wrapper/driver script that imports the legacy module primitives and implements the contract. |

### Key Metrics & Baselines

<!-- Stable metrics that serve as reference points (test counts, coverage, performance baselines). -->

---

## 📝 Session Checkpoint: 2026-07-24 (Plan v1.0 — Planning Phase Completed)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Phase Plan (Implementation Planning) — Completed
- **Active Artifacts:**
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ v1.3 (stable)
  - `spec/spec-custom-build-workflow.md` — Status: ✅ v1.5 (R-4 BLOCKER fixed — Surgical fix by Planner Architect under explicit user authorization; ✅ frontmatter → §1.2 scope → §4.4 driver contract → §4.5 Stage 1 RUN → §12 revision history row)
  - `plan/plan-feature-custom-build-workflow-v1.0.md` — Status: ✅ v1.0 (NEW — 6 phases, 28 actionable tasks, full Ref ID/AC Ref traceability, 5 rejected alternatives, 7 risks + 3 assumptions)
  - `docs/adr/0002-multi-stage-docker-deferred-engine-port.md` — Status: ✅ Accepted
  - `CONTEXT.md` — Status: ✅ Clean
- **Achieved Milestones:**
  - **R-4 Discovery (BLOCKER):** Spec v1.4 §4.4/§4.5 contract specified CLI flags (`--line-height`/`--no-loop-k`/`--no-calt`) targeting the immutable `Scripts/build.py`, which (a) accepts only 4 positional args, (b) declares options statically in-source (NoCalt commented out), and (c) builds all permutations — flags were unimplementable under CON-001. Blocked planning.
  - **Spec v1.5 Surgical Fix (6 edits, user-authorized):** Re-targeted CLI contract to new Stage 1 driver script `Scripts/custom_build_driver.py` (flag names unchanged); added driver contract in §4.4 (single-combination build, NoCalt via `DropCAltAndLiga()`, MUST NOT invoke ttfautohint/compression — Stage 2 responsibilities); updated §4.5 `RUN` to proven `fontforge -lang=py -script` invocation; added driver to §1.2 scope; documented in §12 as R-4.
  - **Plan v1.0 created: 6 executable phases** — Phase 1 (configure.py + schema + pytest gate), Phase 2 (driver + Dockerfile + ttx glyph parity gate), Phase 3 (workflow YAML from dispatch→artifacts), Phase 4 (release publishing with retry/idempotency), Phase 5 (docs), Phase 6 (e2e AC matrix + backward compat audit). OBS-2 (release-count warning >20) → TASK-028.
  - 5 alternatives formally rejected (§3): ALT-001 (flags to build.py — Spec v1.4 contract), ALT-002 (sed patch), ALT-003 (build-all-permutations), ALT-004 (codegen vs static driver), ALT-005 (softprops action vs gh CLI).
- **Dead-Ends (Do NOT Repeat):**
  - **Attempted:** Write Spec CLI contract (`--line-height`/`--no-loop-k`/`--no-calt`) targeting `Scripts/build.py` without verifying its actual interface (Spec v1.4 §4.4).
  - **Reason:** `build.py` accepts 4 positional args only (`<parallel> <batch> <sfdir> <output_dir>`), declares options via `option()`/`conflicting()` calls in-script body, and `NoCalt` declaration is commented out. No CLI/env option-selection mechanism exists in legacy codebase. CON-001 forbids modifying the file.
  - **Flag for KB:** Promote to Knowledge Base during next compaction — generalizable lesson: always verify actual code interfaces before writing contracts against them. Combine with the driver-script pattern as the proven fix.
- **Updated Files:**
  - `spec/spec-custom-build-workflow.md` — v1.4 → v1.5 (6 edits)
  - `plan/plan-feature-custom-build-workflow-v1.0.md` — NEW (21,528 bytes)
- **Decisions Made:**
  - Driver script approach (static, version-controlled) over codegen/transient alternatives — testable, reviewable, no drift.
  - `gh` CLI (preinstalled) over `softprops/action-gh-release` for release publishing — zero third-party action trust surface (SEC-001).
  - `ttx` table-diff parity gate (Phase 2 VERIFY) mandatory before any approval — mitigates driver-vs-legacy divergence risk (RISK-004).
  - Baseline audit bertambah: consistency audit berikutnya wajib memakai `PRD v1.3 ↔ Spec v1.5 ↔ Plan v1.0` — baseline versi lama (v1.4 vs v1.4) sudah usang.
- **Next Action / Pending:**
  - **PRIORITAS #1:** Buka sesi baru → `@ClarificationAnalyst` untuk analisis Plan v1.0 terhadap ambiguities & hidden assumptions. File: `@plan/plan-feature-custom-build-workflow-v1.0.md`, referensi: `@spec/spec-custom-build-workflow.md` + `@docs/prd-20260723-1130-custom-build-workflow.md`.
  - **PRIORITAS #2:** `@ArtifactConsistencyChecker` dengan baseline **baru** (PRD v1.3 ↔ Spec v1.5 ↔ Plan v1.0) — jangan gunakan baseline v1.4 yang sudah obsolete.
  - **PRIORITAS #3:** `@GodModeDev` eksekusi Plan Phase 1–6 — setiap fase wajib berhenti di gate APPROVAL, tidak bisa skip.
  - OBS-1 (tanggal body PRD §1.1) — defer ke `@ProductManagerPRD` saat oportunistik.
  - OBS-2 — sudah tertampung di Plan TASK-028; tidak perlu tindakan lagi.

<!-- checkpoint-tail: Plan v1.0 completed from Spec v1.5 (R-4 blocker fix — driver script replaces CLI-to-build.py contract). 6 phases, 28 tasks traceable to REQ/CON/SEC/GUD/FR/AC/US. OBS-2 folded into TASK-028. Next: @ClarificationAnalyst → @ArtifactConsistencyChecker (new baseline PRDv1.3↔Specv1.5↔Planv1.0) → @GodModeDev execution. -->
