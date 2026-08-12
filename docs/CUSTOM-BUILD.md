# Custom Build

<!-- markdownlint-disable -->

Cloud-hosted personalized build system for [Fantasque Sans Mono](https://github.com/belluzj/fantasque-sans).
Trigger a workflow from your fork of `belluzj/fantasque-sans` on the GitHub Actions tab and
receive TTF, OTF, WOFF, WOFF2, and SVG outputs as a downloadable archive and a tagged
GitHub Release — no local toolchain required.

This page is for **Fork Owners** of the Fantasque Sans Mono repository.
If you are a font *user*, see the [main README](../README.md) for installation.

---

## Getting Started

This guide walks you from a fresh fork to a downloadable build of your custom
Variant in five steps. Total wall-clock time: about 5–15 minutes depending on
GitHub Actions runner availability.

### 1. Fork this repository

Click the **Fork** button at the top-right of
[github.com/belluzj/fantasque-sans](https://github.com/belluzj/fantasque-sans).
Pick your personal account as the destination.

**Why:** Custom Build runs entirely on GitHub Actions, so you need your own
copy of the repository. Your fork is an isolated build environment — no other
fork's builds or releases affect yours.

### 2. Open the Actions tab

On **your fork**, click the **Actions** tab in the top navigation. If prompted,
enable workflows for the fork by clicking **I understand my workflows, go ahead
and enable them**.

**Why:** GitHub disables workflows on forks by default for security. The
**Custom Build** workflow is published by the **upstream** repository
(`belluzj/fantasque-sans`), so the first time you visit the Actions tab on a
fresh fork you may need to opt in.

### 3. Click "Custom Build" → "Run workflow"

In the left sidebar, select **Custom Build**, then click the green
**Run workflow** button on the right.

**Why:** `workflow_dispatch` is the only trigger exposed for this workflow
(by design — it is a manual, on-demand build). There are no scheduled runs
and no automatic builds on push.

### 4. Adjust the five boolean inputs (optional)

The Run workflow form shows five checkboxes:

| Input                | Default | Effect                                                        |
| -------------------- | ------- | ------------------------------------------------------------- |
| `large_line_height`  | off     | Increases line-height metric for accented capital rendering.  |
| `no_loop_k`          | off     | Uses the straight, non-looped variant of lowercase `k`.       |
| `no_calt`            | off     | Disables programming-ligature contextual alternates.          |
| `use_hinted`         | on      | Runs `ttfautohint` on TTFs for screen rendering.              |
| `nerd_font_patching` | off     | Patches generated fonts with 10,000+ developer icons from Nerd Fonts (Powerline, Font Awesome, Material Design, Octicons, etc.). Output is packaged in a separate archive. |

You can leave the defaults for a `Normal` build, or tick the boxes that match
the Variant you want.

**Why:** These five flags map 1:1 to the five build Options. Defaults produce
the `Normal` Variant with bytecode-hinted TTFs — equivalent to the legacy
local `make` output.

#### Nerd Fonts (Optional)

When `nerd_font_patching` is enabled, the Custom Build workflow runs [Nerd Fonts Patcher](https://github.com/ryanoasis/nerd-fonts) v3.5.0 over the generated TTF and OTF fonts.

* **Icon coverage:** `--complete` mode patches over 10,000 developer icons from Powerline, Font Awesome, Material Design, Octicons, Codicons, Devicons, and Weather Icons.
* **Font types:** Mono fonts (`FantasqueSansMono-*`) are patched with `--mono --adjust-line-height` for terminal grid alignment. Proportional fonts (`FantasqueSans`) are patched with `--adjust-line-height`.
* **Separate Archive:** Patched fonts are packaged into a separate `fantasque-sans-nerd-font.zip` and `.tar.gz` archive to preserve the base build's compact size.
* **File Size:** Expect the Nerd Font archive size to increase to ~30–40 MB due to the high volume of added icon glyphs.

### 5. Download the result

Wait for the run to finish (the yellow dot turns ✅). Then either:

- **Artifacts** tab of the run page — download `fantasque-sans-custom-build-{run_id}-{run_attempt}.zip`
  or the matching `.tar.gz`.
- **Releases** page of your fork — every successful run also publishes a
  GitHub Release with the same archives attached.

**Why:** Two delivery channels are provided so that:
1. **Artifacts** are scoped to a single run and expire after the retention
   window (default 90 days for public repos).
2. **Releases** are persistent and discoverable in your fork's
   "Releases" tab — useful for archiving a specific configuration.

---

## Advanced Configuration

This section is for Fork Owners who want reproducible builds, version
control over their build options, or command-line triggering.

### `config.json` reference

Create a `config.json` at the **root of your fork** with the five
boolean Options. All keys are optional — omitted keys fall back to
defaults (`false`, `false`, `false`, `true`, `false`).

```json
{
  "LargeLineHeight": false,
  "NoLoopK": false,
  "NoCalt": false,
  "UseHinted": true,
  "NerdFontPatching": false
}
```

The full JSON Schema (Draft-07) is published in this repository as
[`config.schema.json`](../config.schema.json). Validate your config locally
before pushing:

```sh
python3 Scripts/configure.py \
  --config-file config.json \
  --schema-file config.schema.json
```

Unknown keys in `config.json` produce a warning but do **not** fail the build
— this is intentional forward-compatibility behavior.

### Precedence rules

The build resolves each Option through this hierarchy (highest priority first):

1. **`workflow_dispatch` form input** (only when explicitly set, i.e. differs from default)
2. **`config.json`** in your fork's root
3. **Built-in defaults** — `false`, `false`, `false`, `true`

The build logs one line per Option naming its source, e.g.:

```
Using config.json value for no_loop_k
Using form value (overrides config.json) for large_line_height
Using default for no_calt
Using default for use_hinted
```

The single `config_source` recorded in the `manifest.json` reflects the
**highest-priority source used across all Options**:

- `"form_override"` — at least one Option was overridden via the form
- `"form"` — at least one Option was set via the form, no `config.json` present
- `"config.json"` — at least one Option came from `config.json`, none from the form
- `"defaults"` — every Option came from built-in defaults

### Worked example: from inputs to release title

Suppose your fork's `config.json` is:

```json
{ "NoCalt": true }
```

… and you leave the form at its defaults except `use_hinted = off`.

| Option            | Resolved | Source            |
| ----------------- | -------- | ----------------- |
| `LargeLineHeight` | `false`  | default           |
| `NoLoopK`         | `false`  | default           |
| `NoCalt`          | `true`   | `config.json`     |
| `UseHinted`       | `false`  | form (override)   |

Resulting release title: **`Custom Build: NoCalt (unhinted)`**

| Active display flag | None?           | UseHinted? | NerdFontPatching? | `config_source` | Title suffix         | Example title                                      |
| ------------------- | --------------- | ---------- | ----------------- | --------------- | -------------------- | -------------------------------------------------- |
| —                   | none active     | `true`     | `false`           | `defaults`      | `(default)`          | `Custom Build: Normal (default)`                   |
| —                   | none active     | `true`     | `false`           | `form`          | *(none)*             | `Custom Build: Normal`                             |
| —                   | none active     | `false`    | `false`           | `config.json`   | `(unhinted)`         | `Custom Build: Normal (unhinted)`                  |
| one or more         | any combination | `true`     | `false`           | any             | *(none)*             | `Custom Build: NoLoopK`                            |
| one or more         | any combination | `false`    | `false`           | any             | `(unhinted)`         | `Custom Build: NoCalt (unhinted)`                  |
| any                 | any combination | any        | `true`            | any             | `, NerdFont`         | `Custom Build: NoLoopK, NerdFont`                  |

### Triggering from the command line

You can trigger the workflow from your terminal using the `gh` CLI without
visiting the GitHub UI:

```sh
gh workflow run custom-build.yml \
  -f large_line_height=false \
  -f no_loop_k=true \
  -f no_calt=true \
  -f use_hinted=true \
  -f nerd_font_patching=true
```

The four `-f` flags are the same booleans as the form inputs. To see the
resulting run, list recent workflow runs:

```sh
gh run list --workflow=custom-build.yml --limit 5
```

And to download the resulting artifact directly:

```sh
gh run download <run-id> \
  --name fantasque-sans-custom-build-<run-id>-<run_attempt>
```

---

## Troubleshooting

### "Invalid config.json: 'X' must be a boolean, got Y"

Your `config.json` has a value of the wrong type for one of the four Options.
The error message names the exact key and the offending type.

Common causes:

- `true` quoted as a string: `{"NoLoopK": "true"}` → change to `{"NoLoopK": true}`
- Missing `{}` braces: `LargeLineHeight: true` is YAML, not JSON — wrap in braces
  and quote the key: `{"LargeLineHeight": true}`

The build fails fast at the validation step (no Docker is built, no
GitHub minutes are spent) so this is a free error to fix and re-run.

### "Release creation failed after 3 retries"

The release publish step retries up to 3 times with backoff (1 s, 5 s, 25 s).
If all three attempts fail, the run fails with a clear error.

Common causes:

- **Network glitch** — the GitHub API may have a transient 5xx. Re-run the
  workflow; the retry usually succeeds on the second try.
- **Rate limit** — `gh release create` returns 403 if you exceed the
  unauthenticated rate limit. With `GITHUB_TOKEN` (the default), the
  primary rate limit is generous (~1000/hour). If you fork-traffic-spam
  the workflow, wait 10 minutes and retry.
- **Disk artifact already exists at same tag** — by design this is
  impossible because the tag is unique per `run_attempt` (it includes
  `run_id` and `run_attempt`). If you see this, check whether two parallel
  runs collided on the same `run_id` (extremely rare).

### "Your fork has N releases" warning

When a fork accumulates more than 20 releases, the job summary on the run
page displays a warning. This is informational only — older releases do not
affect new builds.

To bulk-delete test releases:

```sh
gh release list --limit 100 | awk '{print $1}' | xargs -I {} gh release delete {} --yes
```

Or delete a specific release by tag:

```sh
gh release delete custom-build-20260729-120000-1234567890-1 --yes
```

After deletion, the corresponding artifact (if still in the retention
window) remains available from the run page.

### Build fails during Stage 1 or Stage 2 Docker

A `docker build` or `docker run` failure is usually an environmental issue
on the GitHub runner (out of disk, transient network). The build is
self-contained — re-running with the same inputs almost always succeeds.

If the failure is reproducible:

1. Open the run page and inspect the failed step's logs.
2. Look for the file/line that mentions the failing binary
   (`fontforge`, `ttfautohint`, `sfnt2woff`, `woff2_compress`).
3. File an issue at
   [belluzj/fantasque-sans/issues](https://github.com/belluzj/fantasque-sans/issues)
   with the run URL and the relevant log excerpt.

### I need a build Option that isn't in the form

The four boolean Options in the form are the complete public V1 surface.
Other Variants (e.g. the `spacing` preset) are **out of scope for V1** and
require local `make` from the legacy `Scripts/build.py` until V2 lands.

If you need a feature that isn't listed, open an issue on the upstream
repository describing the use case — it helps prioritize V2 work.

---

## See also

- [`config.schema.json`](../config.schema.json) — JSON Schema (Draft-07) for `config.json`
- [Technical Specification](https://github.com/belluzj/fantasque-sans/blob/main/spec/spec-custom-build-workflow.md) — full design contract
- [Architecture Decision Record 0002](adr/0002-multi-stage-docker-deferred-engine-port.md) — why Custom Build is multi-stage Docker
- [Main README](../README.md) — font installation (for users, not Fork Owners)
