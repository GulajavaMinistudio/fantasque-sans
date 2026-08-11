# Fantasque Sans Mono — Custom Build Context

Domain glossary for the Custom Build feature in the Fantasque Sans Mono project. Defines terminology to prevent ambiguity across the codebase and documentation.

## Language

**Custom Build**:
A feature that allows GitHub users to generate personalized variants of the Fantasque Sans Mono font directly from the cloud without a local build toolchain.

**Variant**:
A combination of one or more build options that produces a font output with specific visual characteristics.
_Avoid_: configuration, preset, build option

**Normal**:
A Fantasque Sans Mono variant with no build options enabled — the result of the un-modified build pipeline.
_Avoid_: default variant, baseline, standard

**Fork Owner**:
A GitHub user who has forked the upstream repository and has permission to trigger a Custom Build on their own fork.
_Avoid_: fork maintainer, repo owner

**Upstream**:
The original `belluzj/fantasque-sans` repository which serves as the primary source of truth for all community forks.
_Avoid_: main repo, original repository, source of truth

**Manifest**:
The `manifest.json` file included in every build archive, containing build metadata (timestamp, resolved options, checksum, toolchain versions) for auditing and verification purposes.

**Workflow**:
The `.github/workflows/custom-build.yml` GitHub Actions file in the upstream repository that defines the automated pipeline for building custom font variants.

**Nerd Font Patcher**:
A tool that injects developer-specific icons and symbols into a monospace font.
_Avoid_: Icon patcher, font enhancer

**Nerd Font Variant**:
The font output that has gone through the Nerd Font Patcher process and contains 10,000+ additional icons.
_Avoid_: Patched font, icon font

**Nerd Font Archive**:
The standalone deliverable containing all Nerd Font Variant font files plus the patcher-stamped manifest, packaged separately from the base build archives.
_Avoid_: patched archive, icon archive, NF bundle
