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

### Key Metrics & Baselines

<!-- Stable metrics that serve as reference points (test counts, coverage, performance baselines). -->
- **Test Suite (configure.py)**: 62/62 pytest unit tests passing, 0.20s execution time. [Source: Session 2026-07-29 Phase 1; re-verified 2026-07-30 plan-refactor]
- **Knowledge Base Size**: 8 Dead-Ends + 28 Architecture & Patterns (16 stable + 12 from latest sessions). [Source: Session 2026-07-30, post plan-refactor compaction]
- **Plan-Refactor Execution (2026-07-30)**: 16 tasks across 3 phases, all completed in single session; 13/13 acceptance criteria met; pytest 62/62 PASS; CON-001 preserved. [Source: Session 2026-07-30, plan-refactor-code-review v1.0]
- **End-to-End Build**: 8 iteration cycles to first successful CI run (issues #1–#8). [Source: Session 2026-07-30, first end-to-end run 30520458083]
- **GitHub Actions Actions Versions**: `actions/checkout@v7` + `actions/setup-python@v6` + `actions/upload-artifact@v4` (Node.js 24 LTS). [Source: Session 2026-07-30]
- **Custom-build Release Tag Format**: `custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}` (UTC). [Source: PRD v1.3, Plan v1.2 §TASK-040]
- **CON-001 (Constraint)**: `Scripts/features.py` is FORBIDDEN to modify (legacy). All environment fixes go in `Dockerfile` or workflow YAML. Verified via `git diff --stat` on legacy files = empty. [Source: Plan v1.2 §CON-001, verified 2026-07-30 plan-refactor]

---

## 📝 Session Checkpoint: 2026-07-30 (Code Phase Debugging — Build SUCCESS After 4 More Iterations)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Previous Phase:** Code phase debugging (2026-07-30 morning) — 4 issues fixed locally, awaiting more iterations
- **Current SDLC Phase:** Code phase — **first end-to-end CI run SUCCEEDED** after 4 more iteration cycles (issues #5, #6, #7, #8)
- **Active Artifacts:**
  - `Dockerfile` — Status: ✅ Ubuntu 26.04 + Python 3.x + `pip3 install --break-system-packages --no-cache-dir future` for shim
  - `.github/workflows/custom-build.yml` — Status: ✅ Node 24 actions, no `:ro` on manifest mount, jq backticks corrected
  - `Scripts/packaging.sh` — Status: ✅ Unchanged from original (no workaround needed after workflow fix)
  - `plan/plan-feature-custom-build-workflow-v1.2.md` — Status: ✅ Unchanged (env deviation pending v1.3 bump)
  - `spec/spec-custom-build-workflow.md` — Status: ✅ Unchanged (multi-stage contract preserved)
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ Unchanged
  - **NEW: GitHub Release** — Status: ✅ `https://github.com/GulajavaMinistudio/fantasque-sans/releases` has new `custom-build-*` release with zip + tar.gz + manifest.json attached
- **Achieved Milestones (this continuation session):**
  - **Issue #5** — `ppa:fontforge/fontforge` 404 on `resolute` suite (Ubuntu 26.04). FIX: removed PPA entirely, removed `software-properties-common` and `add-apt-repository`. Use default Ubuntu 26.04 fontforge (Python 3 bindings embedded). [Continuation of DE #5]
  - **Issue #6** — `python3-future` removed from Ubuntu 26.04 main repos (PEP 668 / minimalism trend). FIX: install `future` via pip with `--break-system-packages --no-cache-dir`. [PROMOTED to DE #6]
  - **Issue #7** — `packaging.sh:151: Read-only file system` when script tried to write updated manifest to `/app/manifest.json`. ROOT CAUSE: workflow mounts manifest as `:ro` (defensive) but script's design intent is to writeback updated manifest to source path. FIX: removed `:ro` flag from manifest volume mount in workflow (custom-build.yml:152). Script unchanged. Trade-off: lost defense-in-depth in favor of clean build. [PROMOTED to DE #7]
  - **Issue #8** — `jq: error: Invalid escape at line 1, column 4` at custom-build.yml:294. ROOT CAUSE: `\\\`` (backslash + backtick) in jq string, copied from bash context where backtick IS command substitution. Inside single-quoted bash string passed to jq, backticks are literal in jq — no escape needed. FIX: removed 4 `\\\`` pairs from jq string. Other 5 `\\\`` in workflow (lines 191, 192, 210, 303, 304) are in bash DOUBLE-quoted strings, where escape is correct. [PROMOTED to KB Pattern: Cross-tool Escape Hierarchy]
  - **8/8 fixes committed** by user (manual `git commit` + `git push` per AGENTS.md workflow): `e4056a4`, `0422e16`, `b108eac`, `b890d6d`, `3ae66d7`, `01fc5f5`, `422f19b` (+ memory/AGENTS.md pending)
  - **End-to-end CI build SUCCESS** — first successful run on user's fork; GitHub Release created with attached zip + tar.gz + manifest.json
- **Decisions Made:**
  - **Trade `:ro` for clean build**: defense-in-depth is nice, but build correctness > defense when the conflicting code is trusted (same image). Future: could be revisited via separate writable manifest mount (e.g., mount OUTPUT_DIR copy for script's writeback target).
  - **Update DE #5**: DE #5 said "use `python3-future`" but that package is also removed from Ubuntu 26.04. Correction: use `pip3 install --break-system-packages future` instead. DE #5's "Correct Solution" column updated in this session.
  - **Plan v1.3 bump needed**: Plan v1.2 §Phase 2 still references `python3-future` apt install. v1.3 bump needed (or post-v1.2 erratum) to reflect (a) base image `ubuntu:18.04` → `ubuntu:26.04`, (b) Python 2.7 → 3.x, (c) `python3-future` apt → `pip3 install future` pattern.
  - **User does manual commits**: 8 individual commits per session iteration matches AGENTS.md "manual commit+push" rule. This pattern worked well for traceability — each fix is atomic and traceable to a specific error.
- **Updated Files (this session, all committed except memory):**
  - `Dockerfile` — Stage 1: `ppa:fontforge/fontforge` removed, `software-properties-common` removed, `python3-future` removed, `pip3 install --break-system-packages --no-cache-dir future` added
  - `.github/workflows/custom-build.yml` — manifest mount `:ro` removed, jq string backticks unescaped (4 locations)
  - `.agents/instructions/memory.instructions.md` — DE #5 update + DE #6 + DE #7 + 2 new KB patterns + this checkpoint (pending commit)
  - `AGENTS.md` — `Last Recorded` to be re-confirmed as 2026-07-30 (already current per previous session)
- **Dead-Ends (do NOT repeat):**
  - **Attempted**: Install `python3-future` via `apt-get install` on Ubuntu 26.04. **Reason**: Package removed from Ubuntu 26.04 main repos (PEP 668 / minimalism). `apt-get install python3-future` returns `E: Unable to locate package python3-future`. **Solution**: For legacy Python 2/3 shim packages, use `pip3 install --break-system-packages --no-cache-dir <package>` instead of apt. Add `python3-pip` to apt-install list as bootstrap. [PROMOTED to DE #6]
  - **Attempted**: Mount source manifest as `:ro` in workflow but have packaging script write updated manifest back to same path. **Reason**: `:ro` mount rejects all writes; script fails with `Read-only file system` error. The defensive `:ro` conflicts with script's clear design intent (update manifest in place for archive step). **Solution**: Either (a) remove `:ro` flag (chosen), (b) refactor script to use a different filename in /app/ (more complex, breaks manifest name in archive), or (c) copy script's writeback target to OUTPUT_DIR first and have script write there. [PROMOTED to DE #7]
- **Lessons Learned (KB candidates for next compaction):**
  - **Cross-tool escape hierarchy (bash → jq)**: When passing strings to tools like `jq`, `yq`, etc., be aware of escape context. In bash DOUBLE-quoted strings, backtick `` ` `` triggers command substitution → escape with `` \` ``. In bash SINGLE-quoted strings, backtick is literal (no escape). In jq/yq strings (inside bash single-quotes), backtick is also literal (no escape). The pattern `` \`\(.field)\` `` in a single-quoted bash → jq context is a copy-paste mistake from bash double-quoted context. Valid escapes inside jq double-quoted strings: `\\`, `\"`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`, `\uXXXX`. [PROMOTED to KB Pattern: Cross-tool Escape Hierarchy]
  - **Defense-in-depth vs script intent in Docker mounts**: When a script's design intent is to write back to a mounted path, but the workflow mount is `:ro`, the workflow needs to grant the necessary write access. Either remove `:ro`, use a different mount path, or refactor the script. Defense-in-depth is good but should not block legitimate build behavior. [PROMOTED to KB Pattern: Defense-in-Depth vs Script Intent]
- **Next Action / Pending:**
  - **PRIORITAS #1 (user):** Commit memory updates → `git add .agents/instructions/memory.instructions.md AGENTS.md && git commit -m "docs(memory): checkpoint 2026-07-30 build success + DE #6 #7 + 2 KB patterns"` → `git push origin master`
  - **PRIORITAS #2 (user, next session):** Open new chat session → invoke `/sdlc-code-review` for formal review of Dockerfile + custom-build.yml + packaging.sh
  - **PRIORITAS #3 (user, next session):** Formally bump Plan v1.2 → v1.3 to reflect (a) base image `ubuntu:18.04` → `ubuntu:26.04`, (b) Python 2.7 → 3.x, (c) `python3-future` apt → pip install
  - **PRIORITAS #4 (user, after CI confirms AC-001..AC-005 across multiple matrix values):** Mark TASK-060, TASK-061 (3/5 runtime), TASK-062 (runtime), TASK-063 ✅. Approve TASK-064.
  - **PRIORITAS #5 (next session, after code review approval):** Invoke `/sdlc-generate-docs` for final user-facing documentation per Diátaxis framework
  - **User explicit decision (per "Stop setelah save memory"):** Session ends after memory commit. Next SDLC phase (`/sdlc-code-review` or `/sdlc-generate-docs`) will be opened in a NEW session per Strict Session Isolation.
- **Build Verification:**
  - GitHub Actions run: `30520458083` (and possibly later runs) — all steps PASS
  - GitHub Release: created with tag `custom-build-YYYYMMDD-HHMMSS-...` containing zip + tar.gz + manifest.json
  - URL: `https://github.com/GulajavaMinistudio/fantasque-sans/releases`

<!-- checkpoint-tail: Code phase: end-to-end CI build SUCCESS after 8 iteration cycles. 8 commits, 3 new dead-ends, 2 new KB patterns, Plan v1.3 bump pending. User chose "Stop setelah save memory" — session ends after memory commit. Next: commit memory + /sdlc-code-review + Plan v1.3. -->

## 📝 Session Checkpoint: 2026-07-30 (Plan-Refactor Execution — Documentation Sync & Minor Fixes)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Previous Phase:** Code phase — first end-to-end CI build SUCCESS (8 iterations, 2026-07-30 morning+afternoon); Code Review surfaced 5 findings (CR-F1..CR-F5)
- **Current SDLC Phase:** Code Review remediation — `plan/plan-refactor-code-review-v1.0.md` v1.1 fully executed; plan itself bumped to v1.2 (Complete); ready for `/sdlc-code-review` next session
- **Active Artifacts:**
  - `plan/plan-refactor-code-review-v1.0.md` — Status: ✅ v1.1 → v1.2 (Complete + Execution Results section)
  - `plan/plan-feature-custom-build-workflow-v1.2.md` → renamed to `v1.3.md` + content synced
  - `spec/spec-custom-build-workflow.md` — Status: ✅ v1.5 → v1.6 (7 sections: REQ-004, §1.1, §1.2, §4.4, §4.5, §7, §8.2)
  - `docs/adr/0002-multi-stage-docker-deferred-engine-port.md` — Status: ✅ env sync (Revision Note 2026-07-30)
  - `docs/prd-20260723-1130-custom-build-workflow.md` — Status: ✅ 5 sections synced (§140, §253, §293, §308, §468)
  - `docs/ARCHITECTURE.md` — Status: ✅ Tools table, Dockerfile note, EOL section synced
  - `.github/workflows/custom-build.yml` — Status: ✅ GUD-003 retry fixed (`max_attempts=4` + 1s/5s/25s delays)
  - `Scripts/configure.py` — Status: ✅ `WORKFLOW_VERSION = "1.3"`
  - `Scripts/packaging.sh` — Status: ✅ `:ro` mount removed from manifest path
  - `.dockerignore` — Status: ✅ NEW (9 entries: `.git/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `output/`, `*.zip`, `*.tar.gz`, `.agents/`, `.github/`)
- **Achieved Milestones (this session):**
  - **5/5 code review findings addressed** (CR-F1 doc sync, CR-F2 full spec sync, CR-F3 GUD-003 fix, CR-F4 stale comment/version, CR-F5 .dockerignore)
  - **13/13 acceptance criteria met** (8 Phase 1 + 5 Phase 2)
  - **pytest 62/62 PASS** (regression test, no flakes, 0.20s)
  - **CON-001 preserved** (`git diff Scripts/build.py Scripts/fontbuilder.py Scripts/features.py Makefile` = empty)
  - **markdownlint 0 errors** on both plan files
  - **All internal links resolve** in Plan v1.3 (spec, PRD, ADR, CONTEXT.md)
  - **No new ADR needed** — existing ADR-0002 covers all architectural decisions; ADR-0001 retained as Superseded for historical reference
- **Decisions Made:**
  - **No new ADR for plan-refactor**: All architectural decisions (env migration, `future` shim, deferred engine port) already documented in ADR-0002. Adding ADRs for non-architectural changes (e.g., `.dockerignore` baseline, retry strategy, version constant bump) would violate the triple-gate criteria (hard to reverse / surprising / real trade-off).
  - **ADR-0001 retained as Superseded**: Standard MADR practice — superseded ADRs are never deleted; they preserve historical decision context.
  - **Plan itself updated to reflect completion**: v1.1 → v1.2 bump, status `Draft → Complete`, `## 6. Execution Results` section. The plan is the record of work, not just the work instruction.
- **Updated Files (this session):**
  - `plan/plan-refactor-code-review-v1.0.md` — v1.1 → v1.2, status Complete, Execution Results section
  - `plan/plan-feature-custom-build-workflow-v1.2.md` → renamed to `v1.3.md` + content sync
  - `spec/spec-custom-build-workflow.md` — v1.5 → v1.6
  - `docs/adr/0002-multi-stage-docker-deferred-engine-port.md` — Revision Note 2026-07-30
  - `docs/prd-20260723-1130-custom-build-workflow.md` — 5 sections synced
  - `docs/ARCHITECTURE.md` — synced
  - `.github/workflows/custom-build.yml` — GUD-003 retry fix
  - `Scripts/configure.py` — `WORKFLOW_VERSION = "1.3"`
  - `Scripts/packaging.sh` — `:ro` removed
  - `.dockerignore` — NEW (9 entries)
  - `.agents/instructions/memory.instructions.md` — this compaction + new KB entries
- **Next Action / Pending:**
  - **PRIORITAS #1 (user, next session):** Open new chat session → invoke `/sdlc-code-review` for formal Two-Axis review of Phase 2 changes (`.github/workflows/custom-build.yml`, `Scripts/configure.py`, `Scripts/packaging.sh`, `.dockerignore`).
  - **PRIORITAS #2 (user):** Commit memory + plan updates → `git add .agents/instructions/memory.instructions.md plan/ && git commit -m "docs(memory+plan): checkpoint 2026-07-30 plan-refactor complete + DE #8 + 3 KB patterns"` → `git push`.
  - **PRIORITAS #3 (user, optional):** Trigger CI re-run on fork with `workflow_dispatch` for smoke test (TEST-004 in plan).
  - **PRIORITAS #4 (user, after code review):** Invoke `/sdlc-generate-docs` for user-facing documentation (Diátaxis framework).
- **Verification Snapshot:**
  - pytest: 62/62 PASSED in 0.20s
  - markdownlint: 0 errors on `plan/plan-feature-custom-build-workflow-v1.3.md` and `plan/plan-refactor-code-review-v1.0.md`
  - Internal links: 4/4 resolve in Plan v1.3 (spec, PRD, ADR, CONTEXT.md)
  - `grep "python2.7"` and `grep "ubuntu:18.04"` in 4 target docs: 0 matches each
  - `git diff Scripts/build.py Scripts/fontbuilder.py Scripts/features.py Makefile`: empty (CON-001 compliant)

<!-- checkpoint-tail: Plan-refactor-code-review v1.0 fully executed (16 tasks, 3 phases, all complete). 5 CR findings addressed; 13/13 AC met; pytest 62/62; CON-001 preserved. Plan itself updated to v1.2 Complete. No new ADR needed. Next: /sdlc-code-review. -->

---

## 📝 Session Checkpoint: 2026-08-11 (Specification — Nerd Font Patcher Integration)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Specification (`/sdlc-define-specs`) — Nerd Font Patcher Integration
- **Active Artifacts:**
  - `docs/discovery-draft-20260811-1200-nerd-font-patcher.md` — Status: ✅ Complete (Phase 0)
  - `docs/prd-20260811-1351-nerd-font-patcher.md` — Status: ✅ Finalized (approved; upstream input for this spec)
  - `spec/spec-process-nerd-font-patcher.md` — Status: ✅ NEW v1.0 (created this session)
  - `CONTEXT.md` — Status: ✅ Updated (new term: **Nerd Font Archive**)
- **Achieved Milestones (this session):**
  - **Spec v1.0 lengkap** (586 lines, 15 sections + Introduction) mengikuti Mandatory Specification Template; traceable ke PRD: REQ-001..010, CON-001..006, AC-101..114 ↔ GH-001..014
  - **User mengonfirmasi ASSUMPTION-001 (Opsi A):** font staging via modifikasi `Scripts/packaging.sh` copy TTF/OTF ke `output/TTF` + `output/OTF` (di luar CON-001; satu mount existing)
  - **Baseline pytest 62/62 PASS** (0.59s) — mengonfirmasi hanya 4 test mekanis 4-option yang perlu di-update ke 5-option (ASSUMPTION-009)
  - **Domain Glossary diperbarui** (lazy creation): istilah `Nerd Font Archive` ditambahkan ke `CONTEXT.md`
- **Decisions Made:**
  - **File spec terpisah** (`spec-process-nerd-font-patcher.md`) — Modular Escalation; bukan append ke `spec-custom-build-workflow.md` v1.6 (file 27KB yang sudah approved)
  - **`nerd_font_version` ditulis oleh workflow (jq)**, bukan `configure.py` — mengikuti pola `toolchain_versions.ttfautohint`; source of truth di YAML (ASSUMPTION-002)
  - **`nerd_font_version` hanya saat patching sukses** (ASSUMPTION-003); base archive tidak pernah di-stamp (ASSUMPTION-004/CON-006)
  - **Tidak ada ADR baru** — semua keputusan mengikuti ADR-0002 yang sudah diratifikasi; opsi baru reversible (triple-gate tidak terpenuhi)
  - **`timeout-minutes` 30 → 45**; `WORKFLOW_VERSION` 1.3 → 1.4; `MANIFEST_VERSION` tetap 1.0
- **Updated Files (this session):**
  - `spec/spec-process-nerd-font-patcher.md` — NEW v1.0 (Nerd Font Patcher Integration, Stage 3)
  - `CONTEXT.md` — tambah istilah `Nerd Font Archive` (_Avoid_: patched archive, icon archive, NF bundle)
- **Next Action / Pending:**
  - **PRIORITAS #1 (user, next session):** Buka chat session baru → invoke `/sdlc-clarify-reqs` pada `@spec/spec-process-nerd-font-patcher.md` (lampirkan juga `@docs/prd-20260811-1351-nerd-font-patcher.md`) untuk interogasi ambiguitas & hidden assumptions
  - **PRIORITAS #2 (user, setelah clarify ≥80):** `/sdlc-plan-tasks` di sesi baru (lampirkan spec + PRD)
  - **Assumptions yang wajib di-interogasi clarify:** ASSUMPTION-008 (urutan label release title: `Custom Build: NoLoopK, NerdFont` vs `(default), NerdFont`), ASSUMPTION-003 (`nerd_font_version` saat patching gagal), ASSUMPTION-009 (4 test mekanis di-update: `test_schema_has_four_boolean_properties`, `test_all_defaults`, `test_mixed_precedence_all_four_sources`, `test_emits_one_line_per_option`)
- **Verification Snapshot:**
  - pytest: 62/62 PASSED in 0.59s
  - spec: 586 lines, 15 `## ` sections + `# Introduction`, tanpa placeholder markers
  - Baseline green sebelum implementasi; implementasi (Code phase) belum dimulai

<!-- checkpoint-tail: Specification phase complete untuk Nerd Font Patcher Integration. Spec v1.0 baru di spec/spec-process-nerd-font-patcher.md + CONTEXT.md updated (Nerd Font Archive). User confirmed font staging via packaging.sh copy ke output/. Next: /sdlc-clarify-reqs di sesi baru (attach spec + PRD). -->
