Fantasque Sans Mono
===================
<!-- markdownlint-disable -->
A programming font, designed with functionality in mind, and with some
wibbly-wobbly handwriting-like fuzziness that makes it unassumingly cool.
[Download](https://github.com/belluzj/fantasque-sans/releases/latest) or 
see [installation instructions](#installation).


![](Specimen/urxvt13.png)

Previously known as *Cosmic Sans Neue Mono*. It
appeared that [similar names were already in use for other
fonts](https://github.com/belluzj/cosmic-sans-neue/issues/16), and that
people tended to extend their instinctive hatred of Comic Sans to this very
font of mine (which of course can only be *loved*). Why the previous name?
Here is my original explanation:

> The name comes from my realization that at some point it looked like the
> mutant child of Comic Sans and Helvetica Neue. Hopefully it is not the
> case any more.

Inspirational sources include Inconsolata and Monaco. I have also been using
Consolas a lot in my programming life, so it may have some points in common.

![](Specimen/kdevelop11.png)
![](Specimen/sublime11.png)

Weights, variants and glyph coverage
------------------------------------

The family now includes four weights — Regular, Medium, SemiBold, and Bold —
each with an upright and an italic variant, for eight faces in total. All
faces share the same monospace metrics and the same ranges of characters:
latin letters, some accented glyphs (quite a lot), some greek letters, some
arrows. Medium and SemiBold are derived from the Regular design through an
algorithmic stroke-widening process.

Please note that I have not tested all of the glyphs I have drawn (some letters
have those two layers of crazy accents that I have never witnessed before), so
it might look bad in some cases. Please report these problems: see next section.

It also features a good italic version, which I designed in a fashion similar
to Consolas' italic version, with new glyph designs, not just an added slant.

![](Specimen/vim21.png)

Stylistic set(s)
----------------

### `ss01`: nondescript `k`

No ~~distractive~~ lovely loop.
[Get the pre-activated version here](https://github.com/belluzj/fantasque-sans/releases/download/v1.9.0/FantasqueSansMono-NoLoopK.zip)
or see the [issue #67](https://github.com/belluzj/fantasque-sans/issues/67)
for techniques to activate the stylistic set.

![](Specimen/noloopk.png)

Author and license
------------------

Created by Jany Belluz \<jany.belluz AT hotmail.fr\>

Licensed under the SIL Open Font License (see [LICENSE.txt](LICENSE.txt)).

Please send me an e-mail or [report an issue on
Github](http://github.com/belluzj/cosmic-sans-neue/issues) if you stumble upon
bad design or rendering problems (with screen shot if possible), or if you need
more characters, or if you want to compliment me (I love compliments).

Building with GitHub Actions (Custom Build)
-------------------------------------------

Need a Variant of Fantasque Sans Mono that is not in the official
releases? The Custom Build workflow lets you compile a personalized
variant directly from GitHub Actions — no local toolchain required.
Follow these six steps to go from a fresh fork to a downloadable
build archive plus a tagged GitHub Release.

> **Looking for the full Variant tree (all weights, all formats)?**
> Use the separate **Standard Build (make)** workflow instead — it
> runs the legacy `make` pipeline and uploads the complete `Variants/`
> tree as a workflow artifact.

#### Step 1 — Fork this repository

Click the **Fork** button at the top-right of
[github.com/belluzj/fantasque-sans](https://github.com/belluzj/fantasque-sans)
and pick your personal account as the destination. Custom Build runs
entirely on your fork's GitHub Actions runners, so your own copy is
your isolated build environment.

#### Step 2 — Enable GitHub Actions on your fork

Open the **Actions** tab on your fork. If GitHub shows a banner asking
you to opt in, click **I understand my workflows, go ahead and enable
them**. Forks disable workflows by default for security; enabling once
is sufficient for all future runs.

#### Step 3 — Open the **Custom Build** workflow

In the left sidebar of the Actions tab, select **Custom Build**. Then
click the green **Run workflow** button on the right.

#### Step 4 — Adjust the five boolean inputs (optional)

The Run workflow form shows five checkboxes. Leave them at the defaults
for a `Normal` Variant, or tick the boxes that match the Variant you
want:

| Input                | Default | Effect                                                        |
| -------------------- | ------- | ------------------------------------------------------------- |
| `large_line_height`  | off     | Increases line-height metric for accented capital rendering.  |
| `no_loop_k`          | off     | Uses the straight, non-looped variant of lowercase `k`.       |
| `no_calt`            | off     | Disables programming-ligature contextual alternates.          |
| `use_hinted`         | on      | Runs `ttfautohint` on TTFs for screen rendering.              |
| `nerd_font_patching` | off     | Adds 10,000+ developer icons via [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) v3.5.1 in a separate archive. |

For the full description of each Option, precedence rules,
`config.json` persistence, and CLI triggering, see
[`docs/CUSTOM-BUILD.md`](docs/CUSTOM-BUILD.md).

#### Step 5 — Run the workflow

Click the green **Run workflow** button at the bottom of the form. The
yellow dot turns into an animated spinner while the run is in progress.
Typical wall-clock time is **5–15 minutes** depending on GitHub runner
availability and whether the optional Nerd Font patching step runs.

#### Step 6 — Download the result

Once the run finishes (green checkmark), download the result from
either channel:

- **Artifacts** tab of the run page — single-run archive that expires
  after the retention window (default 90 days for public forks).
- **Releases** page of your fork — persistent, discoverable from your
  fork's sidebar; useful for archiving a specific configuration.

Each successful run produces two archives:

- `fantasque-sans-custom-build-{run_id}-{run_attempt}.zip` / `.tar.gz`
  — the base build (TTF, OTF, WOFF, WOFF2, SVG)
- `fantasque-sans-nerd-font.zip` / `.tar.gz` — **only** when
  `nerd_font_patching` is enabled; contains the same fonts plus
  10,000+ developer icons

For command-line triggering, troubleshooting, and reproducible builds
via `config.json`, see [`docs/CUSTOM-BUILD.md`](docs/CUSTOM-BUILD.md).

Installation
------------

You can [download the latest version](https://github.com/belluzj/fantasque-sans/releases/latest)
and install it by hand. In the `NoLoopK` variant, the looped lowercase `k` is 
replaced with a straight version. The `LargeLineHeight` variant is especially 
useful for users of accented capitals. For more info, see the [CHANGELOG](CHANGELOG.md).

Automatic installation on macOS with [homebrew](https://brew.sh):

    brew install --cask font-fantasque-sans-mono

Instructions for other platforms might follow.

Building installable font files
-------------------------------

The build process requires:
* FontForge with python scripting support,
* `ttfautohint`
* `sfnt2woff` (from the `woff-tools` package on Ubuntu)
* `woff2_compress` from [the Google WOFF2
  tools](https://github.com/google/woff2) or `woff2` package on Ubuntu

Run `make`. You should see green stuff and some "OK" messages.

If you are using Ubuntu, please note that the FontForge version
in the default Ubuntu repositories is much outdated at the time of this writing,
and that [is known to have caused subtle problems](https://github.com/belluzj/fantasque-sans/issues/59).
You are advised to install FontForge from
[this PPA](https://launchpad.net/~fontforge/+archive/ubuntu/fontforge)
(using `sudo add-apt-repository ppa:fontforge/fontforge` prior to the installation).
Alternatively, you can always [download](https://github.com/belluzj/fantasque-sans/releases/latest)
the latest prebuilt release of these fonts.

`make install` will install the TTF fonts into your local `.fonts/` directory
and update the font cache. It comes in handy while modifying the font.

Alternatively, if you'd like to build Fantasque without installing required
dependencies, a Dockerfile is provided. Run the following command, and the
fonts will be built to the `./Variants` directory.

```sh
docker build -t fantasque .
docker run -v "$(pwd)/Variants:/fantasque/Variants" fantasque
```

[![](Specimen/Specimen.png)](Specimen/Specimen.pdf)

Webfonts
--------

Each variant has a `Webfonts/` folder which contains various font formats for
use on the web, along with the matching CSS font declarations. To use them,
you must combine in the same folder:
* a custom `.css` file that you can assemble from the `*-decl.css` fragments
  (you can only pick the styles that you need, e.g. normal and bold)
* the matching `.svg`, `.woff`, `.woff2` files from `Webfonts/`
* the matching `.ttf` files from the `TTF/` folder
* the matching `.otf` files from the `OTF/` folder.

Versions
--------

[Check out the changelog](CHANGELOG.md).
