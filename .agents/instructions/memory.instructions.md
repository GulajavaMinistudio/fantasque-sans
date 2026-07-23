# Project Memory Log

> This file is managed by the `memory-manager` skill.
> It persists context across AI chat sessions to prevent knowledge loss.
> Do NOT manually edit this file unless necessary.

---


## 🧠 Knowledge Base

> This section accumulates cross-session knowledge that must survive compaction.
> Updated during Compaction Mode (Workflow 4). Do NOT delete entries here.

### Architecture & Patterns

- **Agent ↔ Skill Separation of Concerns**: Agent files define persona, scope, and rules; Skill files define workflows and templates. Agents delegate execution to skills. [Source: Session 2026-06-03, still valid]
- **Ecosystem Synchronization**: `.opencode/` is the Master Source of Truth; mirrored/adapted into `.agents/` (Antigravity) and `.github/` (Copilot) for native IDE compatibility. [Source: Session 2026-06-03, still valid]
- **SDLC Phase Gates**: Strict sequential phases (Discovery → PRD → Clarification → Spec → Clarification → Consistency → Plan → Clarification → Code → Review → Docs). Each phase requires a new chat session (Strict Session Isolation). [Source: AGENTS.md institutionalized]
- **Custom Build — configure.py on Host Runner**: `configure.py` (Python 3.14) runs on GitHub Actions host runner, not inside Docker. Passes resolved build args to Stage 1 via `docker build --build-arg BUILD_ARGS`. Stage 2 (Ubuntu 26.04 + Python 3.14) handles packaging tooling only. [Source: Spec v1.2 §1.2/§4.4/§4.5, ADR-0002 revision]
- **Config Precedence**: `workflow_dispatch` form input > `config.json` > build defaults. `config_source` taxonomy: `defaults` | `config.json` | `form` | `form_override`. Naming: snake_case (form), PascalCase (config.json). [Source: PRD FR-3/FR-8, Spec v1.2 §9.1]
- **Multi-Stage Docker with Deferred Engine Port (ADR-0002)**: Stage 1 (ubuntu:18.04 + Python 2.7 + FontForge) runs legacy `build.py`/`fontbuilder`/`features`. Engine port to Python 3.14 deferred to V2 because `build.py` imports both in-process (`from fontbuilder import *`). [Source: ADR-0002, Spec §7]

### Dead-Ends (Do NOT Repeat)

| # | Attempted | Why It Failed | Correct Solution |
|---|-----------|---------------|------------------|
| 1 | Include spacing presets in V1 | `Scripts/build.py` spacing block fully commented out — not production-ready | Defer spacing to V2 |
| 2 | Run `configure.py` inside Stage 2 Docker container | Stage 1 needs resolved args before container build (chicken-and-egg) | Run `configure.py` on host runner; pass args via `docker build --build-arg` |

---

## 📝 Session Checkpoint: 2026-07-23 (Clarification)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Clarification Checkpoint (Recurring, Post-PRD) — Completed
- **Active Artifacts:**
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ Finalized (awaiting 12 post-clarification updates)
  - `CONTEXT.md` — Status: ✅ Created (7 domain terms defined)
  - `docs/adr/0001-multi-stage-docker-legacy-tools.md` — Status: ✅ Created (Accepted)
- **Achieved Milestones:**
  - Activated `@ClarificationAnalyst` persona; codebase-verified PRD against actual `Scripts/build.py`, `fontbuilder.py`, `features.py`, `generate-other-formats`, `Dockerfile`, and `Makefile`
  - Discovered critical fact: `Scripts/build.py` spacing block (Loose/HalfLoose/HalfTight/Tight) is fully commented out — not production-ready
  - Discovered critical fact: DeadSnakes PPA does NOT provide Python 2.7 for Ubuntu 22.04+ (requires libssl<3)
  - Discovered critical fact: `ppa:fontforge/fontforge` is dead — last updated 2019, only supports up to Eoan 19.10 (no Focal/Jammy/Noble)
  - Conducted 12 sequential "Grill Me" protocol questions, all resolved with concrete stakeholder decisions
- **Dead-Ends (Do NOT Repeat):**
  - None encountered in this session (all technical risks identified proactively via codebase verification)
- **Updated Files:**
  - `CONTEXT.md` — New file: Domain Glossary (7 terms: Custom Build, Variant, Normal, Fork Owner, Upstream, Manifest, Workflow)
  - `docs/adr/0001-multi-stage-docker-legacy-tools.md` — New file: ADR for multi-stage Docker strategy
- **Decisions Made:**
  - **#1 — Spacing:** Dikeluarkan dari V1 → V2 (kode spacing di `build.py` dikomentari, belum siap)
  - **#2 — Python 2.7:** Multi-stage Docker — salin binary dari `ubuntu:18.04` (DeadSnakes tidak mendukung)
  - **#3 — FontForge:** Multi-stage Docker — salin dari `ubuntu:18.04` + PPA (PPA mati, tidak mendukung Noble)
  - **#4 — Akumulasi Release:** Dokumentasi + peringatan di workflow summary (tanpa cleanup otomatis)
  - **#5 — UG-5 (Cross-fork discoverability):** Dikeluarkan dari V1 → V2 (belum ada mekanisme discovery)
  - **#6 — Docker Registry:** Build on-the-fly, tanpa registry eksternal
  - **#7 — SM-T2 (Build time):** Disesuaikan dari ≤8 menit → ≤15 menit (konsekuensi build on-the-fly)
  - **#8 — Release Tag Collision:** Tambah `{run_id}-{run_attempt}` ke format tag
  - **#9 — `use_hinted=false` vs `generate-other-formats`:** Salinan temp script, hapus baris `ttfautohint` + `mv`
  - **#10 — `config.json` kosong (`{}`):** `config_source: "defaults"`
  - **#11 — `UseHinted` di `config.json`:** Ditambahkan sebagai key ke-4
  - **#12 — Format Judul Release:** PascalCase + ` + ` + flag `(unhinted)` hanya jika `UseHinted=false`
- **Next Action / Pending:**
  - **PRIORITAS:** Perbarui PRD (`docs/prd-20260723-1130-custom-build-workflow.md`) dengan 12 perubahan dari laporan klarifikasi §4.1
  - Setelah PRD diperbarui: buka sesi baru, invoke `@SpecificationArchitect` untuk `/spec/` documents
  - Setelah Spec: invoke `@ArtifactConsistencyChecker` (PRD ↔ Spec), lalu `@PlannerArchitect`
  - ⚠️ V1 scope final: 3 varian (LargeLineHeight, NoLoopK, NoCalt) + 1 flag build (UseHinted) — total 4 key di config.json, 4 input di form
  - ⚠️ Spacing dan UG-5 ditunda ke V2

<!-- checkpoint-tail: Completed Clarification Checkpoint on PRD. Codebase-verified; 3 critical blockers found (commented-out spacing, dead PPA, no Python 2.7 on Noble). 12 ambiguities resolved via Grill Me protocol. Created CONTEXT.md (7 terms) and ADR-0001 (multi-stage Docker). PRD needs 12 updates before Spec phase. Spacing + UG-5 deferred to V2. -->

---

## 📝 Session Checkpoint: 2026-07-23 (Technical Specification)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Phase Spec (Technical Specification) — Completed
- **Active Artifacts:**
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ Finalized
  - `docs/adr/0002-multi-stage-docker-deferred-engine-port.md` — Status: ✅ Accepted
  - `spec/spec-custom-build-workflow.md` — Status: ✅ Finalized
  - `CONTEXT.md` — Status: ✅ Active (Domain Glossary)
- **Achieved Milestones:**
  - Activated `@SpecificationArchitect` persona and drafted comprehensive Technical Specification in `spec/spec-custom-build-workflow.md` based on PRD v1.2 and ADR-0002
  - Defined data contracts for `config.json` and `config.schema.json` (Draft-07 schema for 4 boolean options: `LargeLineHeight`, `NoLoopK`, `NoCalt`, `UseHinted`)
  - Specified wrapper CLI & precedence resolution interface for `Scripts/configure.py` (Python 3.14)
  - Specified multi-stage Docker compilation architecture per ADR-0002 (Stage 1: legacy Python 2.7 + FontForge for `build.py` / `fontbuilder.py` / `features.py`; Stage 2: Ubuntu 26.04 LTS + Python 3.14 for `configure.py`, `ttfautohint`, `woff-tools`, `woff2`, and packaging)
  - Specified `.github/workflows/custom-build.yml` with `workflow_dispatch` form inputs and auto-publishing to GitHub Release and Workflow Artifacts
  - Specified `manifest.json` schema (`config_source` taxonomy, SHA-256 checksums, `OFL-1.1`)
  - Defined Given-When-Then Acceptance Criteria (AC-001..AC-005) and two-layer test strategy (micro pytest for `configure.py` + macro container smoke tests)
  - Verified visual and functional alignment with user-provided Maple Mono workflow reference image
  - Conducted self-audit and consistency verification against PRD, ADR-0002, and `CONTEXT.md`
- **Dead-Ends (Do NOT Repeat):**
  - None encountered in this session
- **Updated Files:**
  - `spec/spec-custom-build-workflow.md` — New file: Technical Specification (11 sections covering contracts, schemas, Docker multi-stage build, workflow, acceptance criteria, test strategy, and ADR references)
- **Decisions Made:**
  - Multi-stage Docker contract: Stage 1 = Python 2.7 + FontForge; Stage 2 = Ubuntu 26.04 + Python 3.14 (ADR-0002)
  - Engine port to Python 3.14 deferred to V2 because `build.py` imports `fontbuilder`/`features` in-process
  - Release title naming matrix & `(unhinted)` suffix rules locked
- **Next Action / Pending:**
  - Invoke `@ClarificationAnalyst` or `@ArtifactConsistencyChecker` for recurring checkpoint audit (PRD ↔ Spec) before moving to Implementation Plan
  - After consistency check: invoke `@PlannerArchitect` to generate `/plan/` implementation plan documents
  - After plan approved: invoke `@ArtifactConsistencyChecker` (Spec ↔ Plan), then `@GodModeDev` for Phase 6 execution

<!-- checkpoint-tail: Completed Technical Specification phase. Drafted spec/spec-custom-build-workflow.md covering schemas, configure.py wrapper API, ADR-0002 multi-stage Docker build, workflow dispatch UI contracts, manifest format, acceptance criteria, and test strategy. Confirmed UI compatibility with Maple Mono reference. Ready for Clarification/Consistency Audit checkpoint. -->

---

---

## 📝 Session Checkpoint: 2026-07-23 (Clarification — Spec & Cross-Doc Consistency)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Clarification Checkpoint (Recurring, Post-Spec) + Cross-Doc Consistency — Completed
- **Active Artifacts:**
  - `spec/spec-custom-build-workflow.md` — Status: ✅ Finalized (v1.2, clarified)
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ Finalized (FR-4 & §8.3 wording aligned)
  - `docs/adr/0002-multi-stage-docker-deferred-engine-port.md` — Status: ✅ Accepted (Decision/Consequences corrected + Revision Note)
  - `CONTEXT.md` — Status: ✅ Active (Domain Glossary, unchanged)
- **Achieved Milestones:**
  - Clarification Analyst re-audit of Spec v1.0 → identified 6 gaps/ambiguities; applied fixes → Spec v1.1
  - Re-audit of Spec v1.1 → 3 residual grill issues resolved via Grill Me protocol → Spec v1.2
  - Cross-document consistency sweep: corrected PRD FR-4 (×2), §8.3 Challenge 1, §8.3 Challenge 2, and ADR-0002 Decision/Consequences to align with the "configure.py runs on host runner" decision
- **Dead-Ends (Do NOT Repeat):**
  - None encountered in this session (all issues resolved via A/B grill options)
- **Updated Files:**
  - `spec/spec-custom-build-workflow.md` — v1.0 → v1.2: §1.2 (configure.py on host), §3.3 GUD-003 (retry), §4.4 (UseHinted + host execution), §4.5 (`ARG BUILD_ARGS`), §4.6 (`toolchain_versions` + `source_commit`), §4.7 (release body), §9.1 (`compute_config_source`)
  - `docs/prd-20260723-1130-custom-build-workflow.md` — FR-4 (×2) & §8.3 Challenge 1/2: "Stage 2 hosts configure.py" → "configure.py runs on host runner; Stage 2 packaging only"
  - `docs/adr/0002-multi-stage-docker-deferred-engine-port.md` — Decision + Consequences corrected; added Revision Note (2026-07-23)
- **Decisions Made:**
  - **Grill #1:** `configure.py` executes on GitHub Actions **host runner** (not inside container); Stage 2 provides Python 3.14 for packaging tooling only; args passed to Stage 1 via `docker build --build-arg BUILD_ARGS`
  - **Grill #2:** `compute_config_source()` derives `"form"` from `sources` dict (`any(s == "form")`), not a `has_form_inputs` boolean — prevents false `"form"` when all form inputs are at defaults
  - **Grill #3:** Manifest field renamed `commit_sha` → `source_commit` to match PRD FR-8/US-008
  - **Cross-doc:** PRD + ADR-0002 aligned to the same "host runner" decision for full consistency
- **Next Action / Pending:**
  - Invoke `@ArtifactConsistencyChecker` for full PRD ↔ Spec ↔ Plan traceability audit (Spec v1.2, PRD v1.2, ADR-0002)
  - After consistency check: invoke `@PlannerArchitect` to generate `/plan/` implementation plan
  - After plan approved: invoke `@ArtifactConsistencyChecker` (Spec ↔ Plan), then `@GodModeDev` for Phase 6 execution
  - ⚠️ Minor Plan-phase note: `manifest.json` transport from host-generated file → Stage 2 archive assembly (build-context COPY vs host-side packaging) still under-specified; resolve in `/plan/`

<!-- checkpoint-tail: Completed Clarification Checkpoint on Spec v1.0→v1.2 (6 gaps + 3 grill fixes). Achieved full cross-doc consistency: fixed PRD FR-4/§8.3 and ADR-0002 to state configure.py runs on host runner, Stage 2 packaging only. Ready for @ArtifactConsistencyChecker then @PlannerArchitect. -->
