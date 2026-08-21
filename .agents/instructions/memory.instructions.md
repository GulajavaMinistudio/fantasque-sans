# Project Memory Log

> Active Location: `.agents/instructions/memory.instructions.md`
> This file is managed by the `memory-manager` skill.
> It persists context across AI chat sessions to prevent knowledge loss.
> Do NOT manually edit this file unless necessary.

---

## 🧠 Knowledge Base

> This section accumulates cross-session knowledge that must survive compaction.
> Compaction history (condensed 2026-08-16): all sessions from 2026-07-24 through 2026-08-13 were compacted in multiple passes; all knowledge was promoted to this Knowledge Base at the time. The detailed per-pass log was removed in the 2026-08-16 cleanup (user request).
> Compaction 2026-08-18: the two older Medium-refactor checkpoints (Code-Review Remediation, Refactor v1.1) were compacted; 4 lessons promoted; the Finalization checkpoint retained for Medium-round continuity.
> Compaction 2026-08-20 (user request): the 2026-08-16 Finalization and 2026-08-18 PRD-v1.0 checkpoints were compacted; 4 lessons promoted to this Knowledge Base; replaced by the 2026-08-20 PRD-v1.1 checkpoint.
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
- **Spec Self-Audit Against PRD + Codebase Before Handoff**: Before handing a spec to the Plan phase, verify every integration claim (Makefile wildcard, script interfaces, metadata readers) against the actual code files, not just the PRD — applies Dead-End #4 lesson at the spec level. [Source: Session 2026-08-13 Spec Remediation]
- **Validate-font Output Inspection**: `Scripts/validate-font` hardcodes `exit 0` before `exit $error`, so its exit code is always 0. Treat `Error in ...` lines in its output as the real failure signal in all validation gates. [Source: Session 2026-08-13 Spec Remediation]
- **FontForge changeWeight Counter Type Semantics**: `font.changeWeight(stroke_width, type, serif_height, serif_fuzz, counter_type)` — counter_type `"retain"` (lowercase per FontForge's case-sensitive `co_types` flaglist) preserves inner counters (chosen per PRD GH-006), `"squish"` compresses them, `"Auto"` balances. Signature verified against official FontForge docs. [Source: Session 2026-08-13 Spec Clarification]
- **SFNT Weight-String Persistence (finding B-04)**: Generated sources inherit `Weight: Regular` / `Weight: Book` from their inputs unless `font.weight` is set explicitly — FontForge derives SFNT name IDs 3/16/17 from the weight string when explicit records are absent. Always assert `font.weight` in unit tests AND dump the name table from the BUILT binary (not just the `.sfdir` source) to prove SubFamily/Fullname/PostScriptName + `os2_weight` on the shipped artifact. Watch for preferred-family records (ID 16/17) appearing as a side effect of the assignment. [Source: Session 2026-08-16, refactor Phase 1]
- **GitHub Actions Supply-Chain Hygiene**: Pin `uses:` to full commit SHAs (resolve via GitHub API `<repo>/commits/<tag>`, keep tag+date in a comment). Pin pip installs (`pkg==x.y.z`, matched to the local macro-gate environment); for apt prefer documented baseline acceptance (rolling `ubuntu-latest` + Dockerfile-mirrored lists make apt pins fragile) and always add `rm -rf /var/lib/apt/lists/*` per Dockerfile convention. [Source: Session 2026-08-16, refactor Phase 3]
- **Sub-Agent Doc-Sync Delegation**: For multi-document syncs, brief each sub-agent with exact old/new text per hunk, forbid unrelated reformatting, and require per-file verification gates (markdownlint exit 0, scoped `git diff`, grep readback). Independently re-verify the diffs after completion — trust but verify. [Source: Session 2026-08-16]
- **Post-Build SFNT Evidence Record**: Record name-table dumps of built binaries verbatim (License/Copyright boilerplate summarized) in the plan's Execution Results so GH-004-type acceptance criteria are evidenced in-repo. During later doc syncs, leave dated historical rows untouched (plan-as-record). [Source: Session 2026-08-16, refactor Phases 1–2]
- **Plan Task-ID Scoping Across Files**: When multiple plan files reuse identical task IDs (e.g., TASK-207 in both v1.0 and v1.1), always qualify task IDs with file scope when recording status across plans. [Source: Session 2026-08-16]
- **Plan-as-Record Honesty**: Plans must never overstate completion; externally blocked tasks are recorded honestly (e.g., "22/23 + 1 externally blocked", TASK-207 `[ ]` pending with annotation) rather than "23/23 ✅". [Source: Session 2026-08-16]
- **Memory Status Claims Verification**: Before recording git-state claims (e.g., "uncommitted") in memory checkpoints, re-check `git log`/`git status` — stale claims mislead later sessions. [Source: Session 2026-08-16]
- **Accepted-Deviation Markers at PRD v1.0**: Record known accepted-deviation markers (residual algorithmic artifacts, validation baseline profiles) directly in PRD v1.0 acceptance criteria instead of deferring them to a later remediation round. [Source: Session 2026-08-18]
- **Weight-Generation Commit Discipline**: Commit generated `.sfdir` sources to a temporary feature branch; merge to `master` only after maintainer visual QA sign-off (GH-006) — do not repeat Medium's pre-QA master commit. [Source: Session 2026-08-18, PRD SemiBold FR-03/GH-006]
- **Stroke Calibration Contract (Algorithmic Weight)**: Select the highest stroke in the target band (e.g., 55–70 em-units) that passes the "discernible counters" visual gate; if none pass, descend step-wise (50, then the hard floor 45). If the gate fails at/above the floor, the single-pass approach is declared failed and escalated to a maintainer decision (re-scope / abandon / manual fix) — never silently ship a lighter clone. Manual per-glyph fixes are NOT an automatic fallback (maintainer-request only). [Source: Session 2026-08-20, PRD v1.1 FR-01/§8.3/GH-006]
- **Exact-Marker Compliance in Audit Reports**: When marking remediation status on an audit report, keep the mandated marker verbatim (`REMEDIATION STATUS: RESOLVED` per AGENTS.md/skill template); add supplementary status (e.g., `IMPLEMENTATION STATUS: IMPLEMENTED`) as a SEPARATE block — never by editing the required marker. [Source: Session 2026-08-20, advisory]
- **Claim-File Consistency Verification (Post-Fix)**: Before declaring a doc finding resolved, re-grep/verify the exact changed phrases so claims (e.g., "phrase removed", "score 100") match the file state — claim↔file mismatches are flagged as blockers by advisories. [Source: Session 2026-08-20, advisory]

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
| 11 | **Use per-glyph `glyph.intersect()` to clean up self-intersections after `changeWeight`** | `glyph.intersect()` is a Boolean intersect — "Leaves the areas where the contours of a glyph overlap" (fontforge/python.cpp). For glyphs whose contours do NOT overlap (outer ring + inner counter), it empties the foreground entirely. Destroyed the outlines of 661 glyphs on the Medium sources; the resulting "clean" validation was false-green because empty glyphs produce zero validation flags. | Never use `intersect()` for cleanup. `removeOverlap()` and `simplify()` are the only plan-safe cleanup operations; residual self-intersections are a documented limitation of algorithmic `ChangeWeight` deferred to visual QA. Verify any font-generating pipeline with a **foreground-preservation audit**: count glyphs where `len(glyph.foreground)==0 AND len(glyph.references)==0` and compare against the source baseline (flag profiles alone cannot detect emptied glyphs). |

### Key Metrics & Baselines

<!-- Stable metrics that serve as reference points (test counts, coverage, performance baselines). -->
- **Test Suite**: 83/83 pytest — 69 existing + 14 in `tests/test_generate_medium_source.py` (12 original + 2 `font.weight` tests added in refactor Phase 1). [Source: Session 2026-08-16, verified after every refactor phase]
- **Knowledge Base Size**: 11 Dead-Ends + 44 Architecture & Patterns (1 retired; +4 promoted 2026-08-20). [Source: Session 2026-08-16 cleanup, updated 2026-08-20]
- **Plan-Refactor Execution (2026-07-30)**: 16 tasks across 3 phases, all completed in single session; 13/13 acceptance criteria met; pytest 62/62 PASS; CON-001 preserved. [Source: Session 2026-07-30, plan-refactor-code-review v1.0]
- **Nerd Font Patcher Integration (2026-08-12)**: 32 tasks across 4 phases, all complete; 14/14 acceptance criteria (AC-101..AC-114); `configure.py` WORKFLOW_VERSION 1.4. Feature ready for PR/release merge. [Source: Session 2026-08-12 Phase 4]
- **End-to-End Build**: 8 iteration cycles to first successful CI run (issues #1–#8). [Source: Session 2026-07-30, first end-to-end run 30520458083]
- **GitHub Actions Pins (build-make.yml)**: `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (tag v7, 2026-07-17) + `actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02` (tag v4, 2025-03-19); pip `pytest==9.1.1`, `jsonschema==4.26.0`, `future==1.0.0`. `custom-build.yml` remains tag-based (baseline). [Source: Session 2026-08-16, refactor Phase 3]
- **Custom-build Release Tag Format**: `custom-build-YYYYMMDD-HHMMSS-{run_id}-{run_attempt}` (UTC). [Source: PRD v1.3, Plan v1.2 §TASK-040]
- **CON-001 (Constraint)**: `Scripts/features.py` is FORBIDDEN to modify (legacy). All environment fixes go in `Dockerfile` or workflow YAML. Verified via `git diff --stat` on legacy files = empty. [Source: Plan v1.2 §CON-001, verified 2026-07-30 plan-refactor]
- **Variant Permutation Count (build.py)**: 4 actual permutations — Normal, LargeLineHeight, NoLoopK, LargeLineHeight-NoLoopK — the full matrix of the 2 active `Scripts/build.py` options. [Source: Session 2026-08-13 Spec Clarification]
- **Advance Width Baseline (Monospace Grid)**: 1060 em-units for every glyph (1042 glyphs in `Sources/FantasqueSansMono-Regular.sfdir`). FontForge `ChangeWeight` may drift widths — always re-enforce 1060 after emboldening. [Source: Session 2026-08-13 PRD Remediation]
- **Medium Weight Remediation (2026-08-16)**: `plan-refactor-medium-weight-v1.0.md` Complete — 22/23 tasks, 1 externally blocked (TASK-207 AC-007 PR reference pending on PR open; "23/23" claim corrected in the v1.1 round — plan-as-record honesty fix, B-12). Doc versions after sync: Spec v1.6, PRD v1.3, plan-design v1.1 (Complete). All changes uncommitted on `feat/medium-font-weight` at session end.

### Retired Knowledge (2026-08-16)

- **Node.js 20 Deprecation in GitHub Actions** *(retired — action completed)*: the repo already runs `actions/checkout@v7` / `setup-python@v6`, and `build-make.yml` actions are now pinned to commit SHAs; the historical deprecation warning is no longer actionable. [Retired from active patterns on 2026-08-16]

---

## 📝 Session Checkpoint: 2026-08-20 (PRD SemiBold — Clarification Remediation → PRD v1.1)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** PRD Phase (`/sdlc-draft-prd`) — remediation complete; PRD v1.1 ready; next = `/sdlc-define-specs` or `/sdlc-clarify-reqs` in a NEW session
- **Active Artifacts:**
  - `docs/prd-20260818-1636-semibold-font-weight.md` — Status: ✅ DRAFT v1.1 (2026-08-20; all clarification findings applied; projected readiness 100/100)
  - `docs/audit/clarification-report-semibold-font-weight-2026-08-20.md` — Status: ✅ RESOLVED & IMPLEMENTED (exact-marker `REMEDIATION STATUS: RESOLVED` block + separate `IMPLEMENTATION STATUS: IMPLEMENTED` note)
  - `docs/discovery-draft-20260818-1625-semibold-font-weight.md` — unchanged (approved)
  - `CONTEXT.md` — unchanged (SemiBold term already present; no new domain terms)
- **Achieved Milestones:**
  - PRD v1.0 → v1.1: applied all 4 Resolved Items + 7 Auto-Resolved items from the Clarification Report (Review Iteration 2, score 95/100).
  - Stroke calibration contract encoded (band 55–70, grid 50/60/70, floor 45, escalation on failure) in FR-01, §5.3, §8.3, §9.2, GH-006 AC3/AC4.
  - SVG added to output-format enumerations (FR-04, GH-003 AC1, GH-005 AC3, GH-007 AC2) — repo-verified (fontbuilder.py:114, custom_build_driver.py:253, generate-css-decl:51, packaging.sh:113).
  - `Scripts/generate-css-decl` added to CON-07 zero-touch enumeration (§2.3, §7.3, GH-003 AC3); `zip-all-variants` auto-discovery verified (`find "$variants"/*`).
  - §7.1: Adoption Rate metric removed; "valid" glyph-issue triage + editor-compat measurement method defined; §7.2 marks Release Bundle Completeness as sole quantitative adoption metric.
  - Advisory-driven cleanup: literal `"ask first" boundary` remnant removed from §8.3; grep-verified zero residual old phrases.
- **Dead-Ends (Do NOT Repeat):**
  - **Attempted:** Kept literal `(replaces any "ask first" boundary)` in §8.3 as documentation of the replacement.
  - **Reason:** Advisory blocker — the resolution says the phrase is *replaced*, so any literal remnant contradicts the "removed" claim.
  - **Note:** After resolving a doc finding, re-grep the exact phrase to prove zero residual occurrences before claiming completion (see KB Claim-File Consistency Verification).
  - **Attempted:** Changed the audit-report marker to `REMEDIATION STATUS: RESOLVED & IMPLEMENTED`.
  - **Reason:** Advisory blocker — AGENTS.md/skill mandate the exact marker `REMEDIATION STATUS: RESOLVED`; altering it breaks compliance.
  - **Note:** Keep required markers verbatim; add supplementary status as a separate block (see KB Exact-Marker Compliance in Audit Reports).
- **Updated Files:**
  - `docs/prd-20260818-1636-semibold-font-weight.md` — v1.0 → v1.1 (18 surgical edits; version/date bump 2026-08-20)
  - `docs/audit/clarification-report-semibold-font-weight-2026-08-20.md` — added exact `REMEDIATION STATUS: RESOLVED` block + separate `IMPLEMENTATION STATUS: IMPLEMENTED` block; Target Document line notes v1.0 → v1.1
- **Decisions Made:**
  - Stroke calibration contract locked (promoted to KB): highest stroke in 55–70 band passing the "discernible counters" gate; descend 50 → 45 floor; fail at/above floor → maintainer decision; manual fixes only on maintainer request.
  - Weight-generation commit discipline (promoted to KB): temporary feature branch; merge to `master` only after maintainer visual QA sign-off (GH-006).
  - Spec strategy (from compacted 2026-08-18 checkpoint, still valid): separate spec file `spec-design-semibold-weight.md` (KB Spec Modular Escalation).
- **Next Action / Pending:**
  - Handoff: `/sdlc-define-specs` (Option A) or `/sdlc-clarify-reqs` (Option B) in a NEW session with `@docs/prd-20260818-1636-semibold-font-weight.md` (v1.1).
  - Medium round (optional, still open): open `feat/medium-font-weight` PR + attach AC-007 review reference.

<!-- checkpoint-tail: PRD SemiBold remediated v1.0 → v1.1 (2026-08-20): 4 resolutions + 7 auto-resolutions applied, calibration rule/floor/escalation encoded, SVG enumerated, audit report RESOLVED & IMPLEMENTED (exact marker preserved); next = /sdlc-define-specs or /sdlc-clarify-reqs in new session. -->

---

## 📝 Session Checkpoint: 2026-08-20 (Status Review & Handoff Decision)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** PRD Phase (`/sdlc-draft-prd`) — closed at v1.1; awaiting `/sdlc-define-specs` in NEW session
- **Active Artifacts:**
  - `docs/prd-20260818-1636-semibold-font-weight.md` — Status: ✅ DRAFT v1.1 (2026-08-20; projected 100/100)
  - `docs/audit/clarification-report-semibold-font-weight-2026-08-20.md` — Status: ✅ RESOLVED & IMPLEMENTED
  - `docs/discovery-draft-20260818-1625-semibold-font-weight.md` — unchanged (approved)
  - `CONTEXT.md` — unchanged
- **Achieved Milestones:**
  - Status review session — read memory.instructions.md, presented current state to user.
  - Confirmed PRD v1.1 (SemiBold remediation) is ready for handoff.
  - User decision: handoff to `/sdlc-define-specs` in a NEW chat session.
  - Strict Session Isolation enforced (refused intra-session phase switch per AGENTS.md §8).
- **Dead-Ends (Do NOT Repeat):**
  - None new this session (read-only review).
- **Updated Files:**
  - None — read-only memory check + handoff decision only.
- **Decisions Made:**
  - Handoff target: `/sdlc-define-specs` with `@docs/prd-20260818-1636-semibold-font-weight.md` (v1.1) as mandatory input.
  - Spec strategy: separate file `spec-design-semibold-weight.md` (per KB "Spec Modular Escalation" pattern).
  - No KB promotion this round (no new durable lesson surfaced).
- **Next Action / Pending:**
  - User opens a NEW chat session and invokes `/sdlc-define-specs` with PRD v1.1 attached.
  - Medium round remains optional pending `feat/medium-font-weight` PR open + AC-007 review reference.

<!-- checkpoint-tail: Status review 2026-08-20 closed; PRD v1.1 ready for /sdlc-define-specs in new session; no working-tree changes; handoff decided, no KB promotion this round. -->

---
## 📝 Session Checkpoint: 2026-08-20 (Spec SemiBold — Clarification, Review Iteration 1)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Spec Clarification (`/sdlc-clarify-reqs`) on `spec/spec-design-semibold-weight.md` — session complete; spec remediation + re-audit pending
- **Active Artifacts:**
  - `spec/spec-design-semibold-weight.md` — Status: 🔄 In Progress (Readiness Score: **77/100 — Below Threshold**; remediation NOT yet applied)
  - `docs/audit/clarification-report-spec-semibold-weight-2026-08-20.md` — Status: 🔄 NEW file saved (Review Iteration 1; Below Threshold; NO `REMEDIATION STATUS: RESOLVED` marker — allowed only after the spec author remediates and file claims are verified)
  - `docs/prd-20260818-1636-semibold-font-weight.md` — unchanged (v1.1)
  - `CONTEXT.md` — unchanged (no new domain term)
- **Achieved Milestones:**
  - Interrogated the SemiBold spec; verified all codebase claims accurate (`validate-font` exit 0, `generate-css-decl` dynamic reads, `zip-all-variants` discovery, Makefile wildcard, `Scripts/custom_build_driver.py::find_sfdirs()`, 83-test baseline, Italic source `Weight: Book`).
  - Four user-resolved ambiguities (all Option A) recorded as Critical Findings → Resolved Items: Q1 `font.weight` acceptance gate, Q2 italic AND calibration gate, Q3 two-sided neighbor-distinctness gate, Q4 idempotency verification path.
  - Three minor items classified: Q5 grid wording `[Assumed / Backlog]`, Q6 "unit-test runner" terminology `[Assumed / Auto-Resolved]`, Q7 input-validation `[Assumed / Backlog]`.
- **Dead-Ends (Do NOT Repeat):**
  - **Attempted:** Cited FontForge `knownweights`/`realweights` tables as the `font.weight` setter contract ("Demi" as required value).
  - **Reason:** Those tables belong to PS name parsing (`_GetModifiers`), not the setter; the claim was unfounded and pushed a fallback that violates the `_Avoid_` list (DemiBold).
  - **Note:** Frame binding-behavior unknowns as empirical verification gates, never as pre-committed naming fallbacks.
  - **Attempted:** Presented the projected post-remediation score (94/100) as the spec file's current state ("resolutions encoded").
  - **Reason:** The resolutions were session agreements not yet written into the file; claim-file mismatch flagged as blocker.
  - **Note:** Report current file score vs projected score separately; re-audit after remediation (see KB Claim-File Consistency Verification).
- **Updated Files:**
  - `docs/audit/clarification-report-spec-semibold-weight-2026-08-20.md` — created (mandatory template; 77/100 Below Threshold; 4 blockers, 4 resolved items, 3 assumed/backlog; no User Decision Prompt block at score < 80)
- **Decisions Made:**
  - Q1: Phase 1 empirical gate — dump from built TTF/OTF: `font.weight`, `Weight:` in `font.props`, SFNT IDs 2/4/6, ID 16/17 side-effect check, `os2_weight` = 600; evidence verbatim in `plan/` Execution Results (PR description only a copy).
  - Q2: "Discernible counters" = AND gate upright + italic at every candidate; italic failure → descend per locked 70→60→50→45; escalate only if none passes both.
  - Q3: Neighbor comparison = two-sided gate (clearly > Medium, clearly < Bold) in the selection loop; failure → descend; escalate when none passes all gates.
  - Q4: Idempotency verified per TEST-005 precedent (two clean runs, `.glyph`/metrics identical; `font.props` diffed per-field, only `ModificationTime`-type metadata may differ).
- **Next Action / Pending:**
  - Spec author (`/sdlc-define-specs`) applies Resolutions Q1–Q4 + wording Q5/Q6 to `spec/spec-design-semibold-weight.md` — resolutions still pending, NOT applied.
  - Author then runs the Remediation Sequence (projected 94/100; append `REMEDIATION STATUS: RESOLVED` only after actual update + verification) and triggers a re-audit.
  - Spec must NOT be declared ready for the next phase at 77/100.

<!-- checkpoint-tail: Spec SemiBold clarification (2026-08-20): 77/100 Below Threshold; Q1-Q4 resolutions agreed but pending spec author; report saved without RESOLVED marker; re-audit required after remediation. -->

---

## 📝 Session Checkpoint: 2026-08-20 (Plan SemiBold — Clarification + Remediation)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Planning (`/sdlc-clarify-reqs` on Plan → `/sdlc-plan-tasks` remediation) — complete; plan ready; next = `/sdlc-write-code` in a NEW session
- **Active Artifacts:**
  - `plan/plan-design-semibold-weight-v1.0.md` — Status: ✅ Remediated (Readiness projected **100/100**; all 8 §4 fixes from the clarification report applied)
  - `docs/audit/clarification-report-plan-semibold-weight-2026-08-20.md` — Status: ✅ RESOLVED (exact `REMEDIATION STATUS: RESOLVED` marker block added at top; original score 96/100)
  - `spec/spec-design-semibold-weight.md` — unchanged this session (v1.1)
  - `docs/prd-20260818-1636-semibold-font-weight.md` — unchanged (v1.1)
  - `CONTEXT.md` — unchanged (no new domain term)
- **Achieved Milestones:**
  - Plan clarification (`/sdlc-clarify-reqs`): 7 grill questions (Q1–Q7), all resolved Option A; saved clarification report (Review Iteration 1, **96/100**, Good Enough).
  - Verified codebase facts: Italic source `Weight: Book` & Regular `Weight: Regular` (§4.2.1 gate premise factually correct); single root `Makefile` wildcard + `Scripts/generate-font-variants` fan out the 4 permutations (Normal/LargeLineHeight/NoLoopK/LargeLineHeight-NoLoopK); `Scripts/generate-css-decl` writes `Webfonts/<basename>-decl.css` reading `os2_weight`/`italicangle` at runtime.
  - Plan remediation (`/sdlc-plan-tasks`, `[bypass-sdlc]`): rewrote plan applying all 8 §4 fixes — **reorder** (TASK-006/TASK-007 moved to Phase 2, post-push), `INF-001`/`P-ASSUMPTION-002` → GitHub Actions CI like Medium, TASK-004 per-candidate CI loop + `Normal` scope + mandatory Q3 auditable evidence, TASK-005/006 uniform `make`, TASK-006 artifacts #1&#2 from `font.weight` TTF/OTF (`.sfdir` `font.props` dropped) + ID 1 added, TASK-011 "5→3 weights", TASK-022 PR-approval sign-off + `Normal` scope, FILE-005/rollback updated.
  - Appended exact `REMEDIATION STATUS: RESOLVED` block to the clarification report; projected readiness **100/100**.
- **Dead-Ends (Do NOT Repeat):**
  - None new this session (clarification + remediation only; prior spec-round dead-ends already in KB).
- **Updated Files:**
  - `plan/plan-design-semibold-weight-v1.0.md` — full rewrite (~87KB) applying 8 clarification fixes; phase reorder; `Execution Results` tables corrected (ID 1 added, `font.props` removed).
  - `docs/audit/clarification-report-plan-semibold-weight-2026-08-20.md` — added exact `REMEDIATION STATUS: RESOLVED` block at top.
- **Decisions Made:**
  - Empirical gates (calibration TASK-004, `font.weight` gate TASK-006, idempotency TASK-007) execute in **GitHub Actions CI** (`build-make.yml`), same path as the Medium build — NOT locally, NOT pre-commit. Feature branch MUST be pushed before the gates run.
  - Calibration = per-candidate full CI cycle (edit `STROKE_WIDTH` → commit → push → `build-make.yml` → download TTF → inspect `Normal` permutation locally); candidates 70/60/50/45.
  - Q3 "clearly heavier/lighter" stays maintainer judgment but requires **auditable evidence**: side-by-side specimen captures (Medium vs candidate vs Bold at 12/14/16px) + stem-width ratio estimate recorded in `Execution Results`.
  - Visual QA (TASK-022) sign-off = **PR review approval** (recorded evidence); self-review only with single-maintainer note + attached specimens; scoped to `Normal` permutation (glyph geometry identical across permutations).
  - Existing monospace weights = **3** (Regular/Medium/Bold), not 5.
- **Next Action / Pending:**
  - Handoff: `/sdlc-write-code` in a NEW session with `@plan/plan-design-semibold-weight-v1.0.md` + `@spec/spec-design-semibold-weight.md` + relevant source files (`Scripts/generate-medium-source.py`, `Sources/FantasqueSansMono-Italic.sfdir/font.props`).
  - Medium round (optional, still open): open `feat/medium-font-weight` PR + attach AC-007 review reference.

<!-- checkpoint-tail: Plan SemiBold clarified (7 grills, 96/100) + remediated (8 fixes applied, reorder to post-push CI gates, REMEDIATION STATUS: RESOLVED, projected 100/100); next = /sdlc-write-code in new session. -->

---

## 📝 Session Checkpoint: 2026-08-21 (SemiBold — Phase 1 Code Execution Complete)

- **Active Memory Path:** `.agents/instructions/memory.instructions.md`
- **Current SDLC Phase:** Code Execution (`/sdlc-write-code`) — Phase 1 **COMPLETE** (TASK-001..009); Phase 2 in progress (TASK-010/014 ✅, TASK-006/007 evidence recorded, TASK-011/012/013 pending on `build-make.yml` dispatch)
- **Active Artifacts:**
  - `plan/plan-design-semibold-weight-v1.1.md` — Status: 🔄 In Progress (Phase 1 tasks marked ✅; `Execution Results` updated: calibration LOCKED 70, TASK-006 Run A/B tables, idempotency, Phase 1+2 records; **plan edits UNCOMMITTED** — pending user instruction, Git protocol)
  - `spec/spec-design-semibold-weight.md` — Status: ✅ (v1.1, unchanged)
  - `docs/prd-20260818-1636-semibold-font-weight.md` — Status: ✅ (v1.1, unchanged)
  - `Scripts/generate-semibold-source.py` — Status: ✅ committed (`30936705`, `STROKE_WIDTH = 70`)
  - `Sources/FantasqueSansMono-SemiBold.sfdir` + `SemiBoldItalic.sfdir` — Status: ✅ committed (`30936705`, stroke 70; 1042/1046 glyphs, all widths 1060)
  - `tests/test_generate_semibold_source.py` — Status: ✅ committed (`30e9e159`, 14 tests)
- **Achieved Milestones:**
  - **Calibration LOCKED: `STROKE_WIDTH = 70` em-units** (§4.3 composite AND gate). Candidate 70 passes: upright + italic counters discernible at 12/14/16px (specimens `D:/tmp-semibold-calibration/specimens/`), Q3 two-sided neighbor gate (≈2.06× Medium numerical / 1.6–1.8× visual; ≈0.7× Bold). Evidence from CI-built artifacts — Custom Build run `32461218479` @ `30936705` (fork Iosevka-Mayukai, branch `feature/semibold-weight`).
  - TASK-006 `font.weight` gate: Run A + Run B, 5 artifacts each from CI-built TTFs — **ALL PASS** (SFNT IDs 1/2/4/6 correct, no ID 16/17, `usWeightClass` 600, `macStyle` italic + `italicAngle` -11 on Run B).
  - TASK-007 idempotency: `.glyph` files byte-identical; `font.props` differs **only** in `ModificationTime` (1787297903 vs 1787297943).
  - TASK-014 zero-touch audit: **clean** vs merge-base `311ebe70` AND vs `bcbbce10`; Medium script/sources untouched; zero-touch set untouched.
  - Full suite: **97/97 pass, 0 failures** (83 baseline + 14 new; re-run 2026-08-21).
- **Dead-Ends (Do NOT Repeat):**
  - **Attempted:** None new. **Caution verified:** `master` = `311ebe70` has the misleading title "feat: add SemiBold and SemiBold Italic variants" but is a **docs-only commit** (plan v1.0/spec/PRD/reports — `git show --name-only` verified; `Scripts/generate-semibold-source.py` NOT on master) → **no REQ-10 violation**. Always verify commit contents before assuming a master-merge violation.
- **Updated Files:**
  - `plan/plan-design-semibold-weight-v1.1.md` — Execution Update block; Phase-1 table (TASK-004/005/008 ✅); Phase-2 table (TASK-010/006/007/014 ✅); calibration table (70 LOCKED); TASK-006 Run A/B tables (filled); idempotency results; Phase 2 execution record. **UNCOMMITTED.**
- **Decisions Made:**
  - Rule-6 stroke record: **PR description only** (user chose — no amend/force-push; preserves SHA `30936705` evidence traceability). Prepared text recorded in plan.
  - `build-make.yml` evidence: **user dispatches manually** from Actions UI on `feature/semibold-weight` (TASK-011/013/017).
  - TASK-006/007 evidence path: CI-built artifacts (Custom Build) + local real-FontForge dry-runs — deviation from the CI-execution plan recorded in `Execution Results`; build-make re-confirmation pending.
- **Next Action / Pending:**
  - Commit the plan v1.1 updates (user instruction required — Git protocol; optionally amend `30936705` message later).
  - User dispatches `build-make.yml` on `feature/semibold-weight` → verify TASK-011 (4 permutations × TTF/OTF/WOFF/WOFF2/SVG), TASK-013 (CSS decl 600), TASK-017 (green + full `Variants/` upload), TASK-019 (zip contents).
  - TASK-012 `validate-font` on both sources (needs FontForge — CI runner or container; expected only the maintainer baseline exception: `slash_asterisk_asterisk_slash.liga` + `ChangeWeight` artifacts).
  - Retrieve CI-runner FontForge version (auth-gated logs) to complete the TASK-006 tables.
  - Then TASK-015 VERIFY → TASK-016 approval → Phase 3 (TASK-017..021) → Phase 4 visual QA TASK-022 (both specimens) + merge.

<!-- checkpoint-tail: SemiBold Phase 1 complete (2026-08-21): stroke 70 LOCKED via CI-built specimens, sources committed/pushed @ 30936705, TASK-006/007/014 evidence recorded in plan v1.1 (uncommitted); next = user dispatches build-make.yml for TASK-011/013/017. -->

---
