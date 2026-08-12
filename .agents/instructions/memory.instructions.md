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
> - 2026-08-12 (Compaction Pass): Compacted 2 old 2026-07-30 checkpoints. Promoted 4 patterns (Conditional Font Staging, Subshell Error Isolation, Run vs Archive Manifest Semantics, Patcher Line Height Override). Retained 2 most recent checkpoints: 2026-08-11 (Specification) + 2026-08-12 (Clarification Analyst).
> - 2026-08-12 (Spec-Remediation Compaction): Compacted 2026-08-11 (Specification) and 2026-08-12 (Clarification Analyst). Promoted 2 patterns (Spec Modular Escalation, Workflow-stamped Version Semantics). Retained only the most recent checkpoint: 2026-08-12 (Specification Remediation).
> - 2026-08-12 (Plan-Remediation Compaction): Compacted 2026-08-12 (Specification Remediation). Promoted 3 patterns (Docker Timeout Wrapper, Dynamic Metric Calculation, Explicit Artifact Cleanup). Retained only the most recent checkpoint: 2026-08-12 (Plan Remediation).
> Updated during Compaction Mode (Workflow 4). Do NOT delete entries here.

### Architecture & Patterns

- **Spec Modular Escalation**: Create a separate spec file for new independent features (e.g., Nerd Font Patcher) instead of appending to already large and approved upstream specifications. [Source: Session 2026-08-11]
- **Workflow-stamped Version Semantics**: For external tooling versions (e.g., Nerd Font patcher), emit the version metadata from the workflow (via `jq`) rather than the Python configurator script to keep the YAML as the single source of truth. [Source: Session 2026-08-11]
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
- **Conditional Font Staging Pattern**: Wrap optional post-build staging in `if [ "${NERD_FONT_STAGING:-false}" = "true" ]` so zero side-effects occur when the feature is disabled (`NerdFontPatching=false`), keeping outputs byte-identical to base builds. [Source: Session 2026-08-12 Clarification]
- **Subshell Error Isolation in Bash (`set -e`)**: Wrap optional, best-effort operations in `( ... ) || echo "::warning::..."` so failures inside the subshell are trapped and logged without triggering script termination under `set -e`. [Source: Session 2026-08-12 Clarification]
- **Run Manifest vs Archive Manifest Semantics**: Standalone `output/manifest.json` serves as the run-level manifest (reflecting total pipeline run outcomes including optional post-processing), whereas embedded manifests inside individual `.zip`/`.tar.gz` archives serve as archive-specific manifests (describing only the contents of that archive). [Source: Session 2026-08-12 Clarification]
- **Patcher Line Height Override Behavior**: When `LargeLineHeight=true` and `NerdFontPatching=true`, the patcher's `--adjust-line-height` may override Stage 1 line height metrics. The Nerd Font Variant's line height is determined by the patcher for Powerline glyph alignment. [Source: Session 2026-08-12 Clarification]
- **Docker Timeout Wrapper**: Wrap CI `docker run` invocations in a shell `timeout 15m` command to prevent indefinite container deadlocks from exhausting workflow time limits and blocking unrelated release artifacts. [Source: Session 2026-08-12 Plan Remediation]
- **Dynamic Metric Calculation**: Compute artifact metrics for Job Summaries dynamically (e.g., `find <dir> -type f | wc -l`) rather than hardcoding expected counts, ensuring resilience against future payload variations. [Source: Session 2026-08-12 Plan Remediation]
- **Explicit Artifact Cleanup**: On failure branches of packaging steps, explicitly `rm -f` partial archives to guarantee that corrupted zip/tar files cannot leak into subsequent wildcard upload steps. [Source: Session 2026-08-12 Plan Remediation]

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
| 9 | **Assume versioned Docker tag exists on Docker Hub (`nerdfonts/patcher:v3.5.0`)** | Docker Hub repo `nerdfonts/patcher` does not publish version tags like `v3.5.0`; only `latest` is published. Pulling `v3.5.0` returned `manifest unknown: manifest unknown`. | Use `PRIMARY_TAG: "nerdfonts/patcher:latest"` with fallback to `FALLBACK_TAG: "ghcr.io/cdalvaro/docker-nerd-fonts-patcher:latest"`. Export `used_tag` output from pull step. |
| 10 | **Pass explicit `/in/${fname}` argument to `docker run nerdfonts/patcher` when `/in` contains multiple font files** | The container entrypoint script `gotta-patch-em-all-font-patcher!.sh` automatically scans `/in` and appends every font file found to `font-patcher`. Passing `/in/${fname}` explicitly caused `font-patcher` to receive 2 positional file arguments, crashing with `font-patcher: error: unrecognized arguments: /in/<file>`. | Create an isolated per-file input directory (`tmp-in-${fmt}`) containing only 1 target font file per `docker run` invocation, mount it to `/in`, and omit explicit filename/outputdir arguments from `docker run`. |

### Key Metrics & Baselines

<!-- Stable metrics that serve as reference points (test counts, coverage, performance baselines). -->
- **Test Suite (configure.py)**: 62/62 pytest unit tests passing, 0.20s execution time. [Source: Session 2026-07-29 Phase 1; re-verified 2026-07-30 plan-refactor]
- **Knowledge Base Size**: 8 Dead-Ends + 32 Architecture & Patterns. [Source: Session 2026-08-12, post clarification compaction]
- **Plan-Refactor Execution (2026-07-30)**: 16 tasks across 3 phases, all completed in single session; 13/13 acceptance criteria met; pytest 62/62 PASS; CON-001 preserved. [Source: Session 2026-07-30, plan-refactor-code-review v1.0]
- **End-to-End Build**: 8 iteration cycles to first successful CI run (issues #1–#8). [Source: Session 2026-07-30, first end-to-end run 30520458083]
- **GitHub Actions Actions Versions**: `actions/checkout@v7` + `actions/setup-python@v6` + `actions/upload-artifact@v4` (Node.js 24 LTS). [Source: Session 2026-07-30]
- **Custom-build Release Tag Format**: `custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}` (UTC). [Source: PRD v1.3, Plan v1.2 §TASK-040]
- **CON-001 (Constraint)**: `Scripts/features.py` is FORBIDDEN to modify (legacy). All environment fixes go in `Dockerfile` or workflow YAML. Verified via `git diff --stat` on legacy files = empty. [Source: Plan v1.2 §CON-001, verified 2026-07-30 plan-refactor]

---



## 📝 Session Checkpoint: 2026-08-12 (Plan Remediation)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Planning Remediation (`/sdlc-plan-tasks`) — Nerd Font Patcher Integration
- **Active Artifacts:**
  - `docs/audit/clarification-report-nerd-font-patcher-2026-08-12.md` — Status: ✅ Resolved (100/100)
  - `plan/plan-feature-nerd-font-patcher-v1.0.md` — Status: ✅ Finalized
  - `spec/spec-process-nerd-font-patcher.md` — Status: ✅ Finalized (v1.1)
- **Achieved Milestones:**
  - Remediation of Clarification Report [Review Iteration 2] for the Implementation Plan completed.
  - Mitigated Docker hang with `timeout 15m` wrapper.
  - Set dynamic file count `find nf-staging -type f | wc -l` in Job Summary step.
  - Added explicit archive cleanup (`rm -f`) on packaging failure.
  - Audit report marked as `REMEDIATION STATUS: RESOLVED`.
- **Dead-Ends (Do NOT Repeat):**
  - None this session.
- **Updated Files:**
  - `plan/plan-feature-nerd-font-patcher-v1.0.md` — Tasks updated based on clarification report.
  - `docs/audit/clarification-report-nerd-font-patcher-2026-08-12.md` — Added resolved status.
- **Decisions Made:**
  - Plan achieved projected Readiness Score 100/100, approved for transition to Execution Phase.
- **Next Action / Pending:**
  - **PRIORITAS #1 (next session):** Open new session → invoke `/sdlc-write-code` to execute the implementation plan defined in `@plan/plan-feature-nerd-font-patcher-v1.0.md`.

<!-- checkpoint-tail: Plan remediation complete. plan-feature-nerd-font-patcher-v1.0.md updated with 3 fixes (timeout, dynamic count, explicit rm). Clarification report resolved (100/100). Next phase is /sdlc-write-code. -->

---

## 📝 Session Checkpoint: 2026-08-12 (Phase 1 Execution)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Execution Phase 1 (`/sdlc-write-code`) — Nerd Font Patcher Integration (Configuration Layer)
- **Active Artifacts:**
  - `plan/plan-feature-nerd-font-patcher-v1.0.md` — Status: 🔄 Phase 1 Complete (TASK-001..TASK-006)
  - `config.schema.json` — Status: ✅ Updated
  - `Scripts/configure.py` — Status: ✅ Updated (WORKFLOW_VERSION 1.4)
  - `tests/fixtures/manifest_schema.json` — Status: ✅ Updated
  - `tests/test_configure.py` — Status: ✅ Updated (69/69 PASS)
- **Achieved Milestones:**
  - Implemented TASK-001: Added `NerdFontPatching` boolean property to `config.schema.json`.
  - Implemented TASK-002: Extended `Scripts/configure.py` with `DEFAULTS`, `FORM_KEY_TO_OPTION`, `--form-nerd-font-patching`, and bumped `WORKFLOW_VERSION` to 1.4.
  - Implemented TASK-003: Extended `tests/fixtures/manifest_schema.json` with `NerdFontPatching` and `nerd_font_version`.
  - Implemented TASK-004: Updated 4-option fixtures to 5-option surface in `tests/test_configure.py`.
  - Implemented TASK-005: Added GH-014 unit tests in `TestNerdFontPatchingOptions`.
  - Implemented TASK-006: Ran `python -m pytest tests/ -v` — 69/69 tests PASS (100%).
  - Updated `plan/plan-feature-nerd-font-patcher-v1.0.md` task progress table for TASK-001..TASK-006.
- **Dead-Ends (Do NOT Repeat):**
  - None this session.
- **Updated Files:**
  - `config.schema.json`
  - `Scripts/configure.py`
  - `tests/fixtures/manifest_schema.json`
  - `tests/test_configure.py`
  - `plan/plan-feature-nerd-font-patcher-v1.0.md`
- **Decisions Made:**
  - Kept `NerdFontPatching` out of `OPTION_TO_DRIVER_FLAG` as a Stage 3 post-build option (mirrors `UseHinted`).
- **Next Action / Pending:**
  - **Phase 2a Execution:** Font Staging & Patcher Execution (`Scripts/packaging.sh` & `.github/workflows/custom-build.yml`).

<!-- checkpoint-tail: Phase 1 execution complete (TASK-001..TASK-006). 69/69 pytest pass. plan-feature-nerd-font-patcher-v1.0.md updated. Awaiting approval for Phase 2a. -->

---

## 📝 Session Checkpoint: 2026-08-12 (Phase 1 & Phase 2 Execution)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Execution Phase 2 (`/sdlc-write-code`) — Nerd Font Patcher Integration (Staging, Execution, Packaging & Artifact Upload)
- **Active Artifacts:**
  - `plan/plan-feature-nerd-font-patcher-v1.0.md` — Status: 🔄 Phase 1 & 2 Complete (TASK-001..TASK-022)
  - `Scripts/packaging.sh` — Status: ✅ Updated (Font Staging)
  - `.github/workflows/custom-build.yml` — Status: ✅ Updated (Steps 7.1..7.4, timeout-minutes: 45)
  - `tests/test_configure.py` — Status: ✅ Updated (69/69 PASS)
- **Achieved Milestones:**
  - Completed Phase 1 (TASK-001..TASK-007) and marked Phase 1 approval in plan document.
  - Implemented TASK-008: Added conditional font staging block to `Scripts/packaging.sh`.
  - Implemented TASK-009: Added `nerd_font_patching` input to `.github/workflows/custom-build.yml`.
  - Implemented TASK-010: Passed `--form-nerd-font-patching` flag in `resolve` step.
  - Implemented TASK-011: Added Step `nf_enable` to read resolved `NerdFontPatching` option from `manifest.json`.
  - Implemented TASK-012: Passed `-e NERD_FONT_STAGING` to Stage 2 Docker run.
  - Implemented TASK-013: Bumped `timeout-minutes` from 30 to 45.
  - Implemented TASK-014: Added Step 7.1 `nf_pull` for `nerdfonts/patcher:v3.5.0` with `set +e` error isolation.
  - Implemented TASK-015: Added Step 7.2 `nf_patch` with 10 patcher invocations (4 Mono x 2 formats + 1 Proportional x 2 formats) wrapped in `timeout 15m`.
  - Implemented TASK-018: Added Step 7.3 `nf_package` to assemble `fantasque-sans-nerd-font.zip` and `.tar.gz`, stamping `nerd_font_version` into manifest only on success.
  - Implemented TASK-019: Added Step 7.4 `Upload Nerd Font build artifacts` for `nerd-font-build` artifact.
  - Implemented TASK-020: Fixed base artifact upload paths to explicit filenames.
  - Delegated verification testing to Research Subagent & executed `python -m pytest tests/ -v` — 69/69 tests PASS (100%).
  - Updated `plan/plan-feature-nerd-font-patcher-v1.0.md` task progress table for TASK-001..TASK-021.
- **Dead-Ends (Do NOT Repeat):**
  - None this session.
- **Updated Files:**
  - `Scripts/packaging.sh`
  - `.github/workflows/custom-build.yml`
  - `plan/plan-feature-nerd-font-patcher-v1.0.md`
  - `.agents/instructions/memory.instructions.md`
- **Decisions Made:**
  - Used subshell error trapping (`set +e`) for Stage 3 steps so Nerd Font failures never affect base build execution.
- **Next Action / Pending:**
  - **Phase 3 Execution:** Release Integration & Job Summary (`custom-build.yml` Step 9, Step 10, Step 11 — TASK-023..TASK-027).

<!-- checkpoint-tail: Phase 1 & 2 execution complete (TASK-001..TASK-022). 69/69 pytest pass. plan-feature-nerd-font-patcher-v1.0.md updated. Ready for Phase 3. -->

---

## 📝 Session Checkpoint: 2026-08-12 (Phase 3 Execution)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Execution Phase 3 (`/sdlc-write-code`) — Nerd Font Patcher Integration (Release Integration & Job Summary)
- **Active Artifacts:**
  - `plan/plan-feature-nerd-font-patcher-v1.0.md` — Status: 🔄 Phase 1, 2 & 3 Complete (TASK-001..TASK-027)
  - `.github/workflows/custom-build.yml` — Status: ✅ Updated (Steps 9, 10, 11)
  - `tests/test_configure.py` — Status: ✅ Updated (69/69 PASS)
- **Achieved Milestones:**
  - Completed Phase 2 approval (TASK-022) and marked Phase 2 complete in plan document.
  - Implemented TASK-023: Modified Step 10 in `custom-build.yml` to append `, NerdFont` to `TITLE` when NF packaging succeeds, and added `NerdFontPatching` option row & `🤓 Nerd Font Variant` section to release notes.
  - Implemented TASK-024: Modified Step 11 in `custom-build.yml` to conditionally attach `output/fantasque-sans-nerd-font.zip` and `.tar.gz` as release assets via `ASSETS` array array-expansion.
  - Implemented TASK-025: Modified Step 9 in `custom-build.yml` to write a 3-state Nerd Font status block to `$GITHUB_STEP_SUMMARY` (`disabled`, `enabled (nerdfonts/patcher v3.5.0) — N files patched in Xs`, or `enabled (FAILED — base build unaffected)`).
  - Executed `python -m pytest tests/ -v` — 69/69 unit tests PASS (100%).
  - Updated `plan/plan-feature-nerd-font-patcher-v1.0.md` task progress table for TASK-022..TASK-026.
- **Dead-Ends (Do NOT Repeat):**
  - None this session.
- **Updated Files:**
  - `.github/workflows/custom-build.yml`
  - `plan/plan-feature-nerd-font-patcher-v1.0.md`
  - `.agents/instructions/memory.instructions.md`
- **Decisions Made:**
  - Used array variable `ASSETS` in Step 11 shell script to seamlessly handle optional inclusion of Nerd Font release assets based on file existence.
- **Next Action / Pending:**
  - **Phase 4 Execution:** User Documentation (`docs/CUSTOM-BUILD.md`), Architecture Reference (`docs/ARCHITECTURE.md`), and End-to-End Validation Checklist (TASK-028..TASK-032).

<!-- checkpoint-tail: Phase 1, 2 & 3 execution complete (TASK-001..TASK-027). 69/69 pytest pass. plan-feature-nerd-font-patcher-v1.0.md updated. Ready for Phase 4. -->

---

## 📝 Session Checkpoint: 2026-08-12 (Phase 4 Execution — ALL PHASES COMPLETE)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Execution Phase 4 (`/sdlc-write-code`) — Nerd Font Patcher Integration (Documentation & E2E Validation)
- **Active Artifacts:**
  - `plan/plan-feature-nerd-font-patcher-v1.0.md` — Status: ✅ 100% Complete (TASK-001..TASK-032)
  - `docs/CUSTOM-BUILD.md` — Status: ✅ Updated per GH-010
  - `docs/ARCHITECTURE.md` — Status: ✅ Updated per TASK-029
  - `.github/workflows/custom-build.yml` — Status: ✅ Complete
  - `Scripts/configure.py` — Status: ✅ Complete (WORKFLOW_VERSION 1.4)
  - `config.schema.json` — Status: ✅ Complete
  - `tests/test_configure.py` — Status: ✅ Complete (69/69 PASS)
- **Achieved Milestones:**
  - Marked Phase 3 approval (TASK-027) as complete in plan document.
  - Implemented TASK-028: Updated `docs/CUSTOM-BUILD.md` with `nerd_font_patching` form input, Nerd Fonts subsection, `config.json` example, `gh workflow run` example, and release title suffix table row.
  - Implemented TASK-029: Updated `docs/ARCHITECTURE.md` with Stage 3 containerization layer, updated Mermaid pipeline diagram, Stage 3 data flow description, and `nf-staging/` directory purpose.
  - Implemented TASK-030: Completed end-to-end validation checklist confirming all 14 Acceptance Criteria (AC-101 through AC-114).
  - Implemented TASK-031: Executed full unit test suite `python -m pytest tests/ -v` — 69/69 PASS (100%).
  - Implemented TASK-032: Marked final feature completion in `plan/plan-feature-nerd-font-patcher-v1.0.md`.
- **Dead-Ends (Do NOT Repeat):**
  - None.
- **Updated Files:**
  - `docs/CUSTOM-BUILD.md`
  - `docs/ARCHITECTURE.md`
  - `plan/plan-feature-nerd-font-patcher-v1.0.md`
  - `.agents/instructions/memory.instructions.md`
- **Decisions Made:**
  - All 4 implementation phases successfully completed, fully verified, and documented according to SDLC standards.
- **Next Action / Pending:**
  - Feature 100% complete and ready for pull request / release merge!

<!-- checkpoint-tail: ALL 4 PHASES COMPLETE (TASK-001..TASK-032). 69/69 pytest pass. plan-feature-nerd-font-patcher-v1.0.md 100% complete. -->

---
