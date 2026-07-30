#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Fantasque Sans Mono Custom Build -- Stage 2 packaging script.
#
# Runs INSIDE the Stage 2 Docker image (ubuntu:26.04 + Python 3.14 +
# ttfautohint + woff-tools + woff2 + zip + tar + jq). Invoked by the
# GitHub Actions workflow (Phase 3 TASK-026) via:
#
#     docker run --rm \
#         -v <host>/manifest.json:/app/manifest.json:ro \
#         -v <host>/output:/app/output \
#         fantasque-custom \
#         bash /app/Scripts/packaging.sh
#
# Contract (Spec v1.5 section 4.5 / 4.6 / 4.7 + Plan TASK-026):
#
#   1. Read UseHinted from /app/manifest.json (produced by configure.py
#      on the host runner). When true, run ttfautohint on every TTF in
#      /app/TTF/.
#   2. Run sfnt2woff and woff2_compress on every TTF in /app/TTF/ to
#      produce .woff and .woff2 files alongside the source.
#   3. Compute SHA-256 + size_bytes for every font file under
#      /app/{TTF,OTF,Webfonts} and append a font_files entry to the
#      manifest.
#   4. Stamp toolchain_versions.ttfautohint in the manifest with the
#      installed binary version.
#   5. Assemble .zip and .tar.gz archives in /app/output containing
#      TTF/, OTF/, Webfonts/, manifest.json, LICENSE.txt, README.md
#      (Spec REQ-006). The updated manifest is also placed at the root
#      of /app/output/ for the workflow to consume downstream
#      (Phase 4 release notes).
#
# Failure mode: the script aborts on the first error (set -euo pipefail).
# A non-zero exit is propagated to the workflow step, which fails the
# job and emits a diagnostic via the job summary.

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths (mount contract with the workflow)
# ---------------------------------------------------------------------------
readonly APP_DIR="/app"
readonly INPUT_MANIFEST="${APP_DIR}/manifest.json"
readonly OUTPUT_DIR="${APP_DIR}/output"
readonly TTF_DIR="${APP_DIR}/TTF"
readonly OTF_DIR="${APP_DIR}/OTF"
readonly WEB_DIR="${APP_DIR}/Webfonts"

# Package basename (workflow reads back the matching .zip/.tar.gz).
readonly PACKAGE_BASENAME="fantasque-sans-custom-build"

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
[ -f "${INPUT_MANIFEST}" ] || { echo "packaging: missing ${INPUT_MANIFEST}" >&2; exit 1; }
for required_bin in jq sha256sum ttfautohint sfnt2woff woff2_compress zip tar; do
    command -v "${required_bin}" >/dev/null 2>&1 \
        || { echo "packaging: required binary '${required_bin}' not in PATH" >&2; exit 1; }
done
for required_dir in "${TTF_DIR}" "${OTF_DIR}" "${WEB_DIR}"; do
    [ -d "${required_dir}" ] || { echo "packaging: missing directory ${required_dir}" >&2; exit 1; }
done
[ -f "${APP_DIR}/LICENSE.txt" ] || { echo "packaging: missing ${APP_DIR}/LICENSE.txt" >&2; exit 1; }
[ -f "${APP_DIR}/README.md" ] || { echo "packaging: missing ${APP_DIR}/README.md" >&2; exit 1; }

mkdir -p "${OUTPUT_DIR}"

# ---------------------------------------------------------------------------
# 1. Read UseHinted from the host-generated manifest
# ---------------------------------------------------------------------------
USE_HINTED=$(jq -r '.resolved_options.UseHinted' "${INPUT_MANIFEST}")
echo "packaging: UseHinted=${USE_HINTED}"

# ---------------------------------------------------------------------------
# 2. Optional ttfautohint pass (Spec section 1.2: Stage 2 is the only
#    stage allowed to invoke ttfautohint). Mutates TTFs in place.
# ---------------------------------------------------------------------------
if [ "${USE_HINTED}" = "true" ]; then
    echo "packaging: running ttfautohint on every TTF"
    shopt -s nullglob
    for ttf in "${TTF_DIR}"/*.ttf; do
        tmp="${ttf}.tmp"
        ttfautohint "${ttf}" "${tmp}"
        mv "${tmp}" "${ttf}"
    done
    shopt -u nullglob
else
    echo "packaging: skipping ttfautohint (unhinted build)"
fi

# ---------------------------------------------------------------------------
# 3. WOFF and WOFF2 compression (Spec REQ-005)
# ---------------------------------------------------------------------------
echo "packaging: generating WOFF and WOFF2"
shopt -s nullglob
for ttf in "${TTF_DIR}"/*.ttf; do
    # sfnt2woff writes the .woff next to the .ttf.
    sfnt2woff "${ttf}"
    # woff2_compress writes the .woff2 next to the .ttf.
    woff2_compress "${ttf}"
done
shopt -u nullglob

# ---------------------------------------------------------------------------
# 4. Enumerate font files and compute SHA-256 + size_bytes
# ---------------------------------------------------------------------------
echo "packaging: computing SHA-256 and sizes"
FONT_FILES_JSON="[]"
shopt -s nullglob
for src in "${TTF_DIR}"/*.ttf "${TTF_DIR}"/*.otf "${TTF_DIR}"/*.woff "${TTF_DIR}"/*.woff2 \
           "${OTF_DIR}"/*.ttf "${OTF_DIR}"/*.otf \
           "${WEB_DIR}"/*.svg; do
    [ -f "${src}" ] || continue
    sha=$(sha256sum "${src}" | awk '{print $1}')
    size=$(stat -c '%s' "${src}")
    relpath="${src#${APP_DIR}/}"
    case "${src}" in
        *.ttf)  fmt="ttf" ;;
        *.otf)  fmt="otf" ;;
        *.woff) fmt="woff" ;;
        *.woff2) fmt="woff2" ;;
        *.svg)  fmt="svg" ;;
        *)      echo "packaging: skipping unrecognized file ${src}" >&2; continue ;;
    esac
    FONT_FILES_JSON=$(jq \
        --arg fn "${relpath}" \
        --arg fmt "${fmt}" \
        --argjson sz "${size}" \
        --arg sha "${sha}" \
        --argjson arr "${FONT_FILES_JSON}" \
        '. + [{"filename": $fn, "format": $fmt, "size_bytes": $sz, "sha256": $sha}]' \
        <<<"null")
done
shopt -u nullglob

# ---------------------------------------------------------------------------
# 5. Update manifest: font_files + ttfautohint version
# ---------------------------------------------------------------------------
TTFAUTOHINT_VERSION=$(ttfautohint --version 2>&1 | head -n1 | awk '{print $NF}')

UPDATED_MANIFEST=$(jq \
    --argjson ff "${FONT_FILES_JSON}" \
    --arg tav "${TTFAUTOHINT_VERSION}" \
    '.font_files = $ff | .toolchain_versions.ttfautohint = $tav' \
    "${INPUT_MANIFEST}")

# Place the updated manifest at /app/output/manifest.json AND keep a
# copy that the archive step will include at the root of TTF/.
echo "${UPDATED_MANIFEST}" > "${OUTPUT_DIR}/manifest.json"
echo "${UPDATED_MANIFEST}" > "${APP_DIR}/manifest.json"

# ---------------------------------------------------------------------------
# 6. Assemble archives (Spec REQ-006)
# ---------------------------------------------------------------------------
echo "packaging: assembling archives"
cp "${APP_DIR}/LICENSE.txt" "${OUTPUT_DIR}/LICENSE.txt"
cp "${APP_DIR}/README.md" "${OUTPUT_DIR}/README.md"

cd "${APP_DIR}"

# zip: include TTF/ OTF/ Webfonts/ LICENSE.txt README.md manifest.json
zip -r "${OUTPUT_DIR}/${PACKAGE_BASENAME}.zip" \
    TTF OTF Webfonts LICENSE.txt README.md manifest.json \
    >/dev/null

# tar.gz: same set
tar czf "${OUTPUT_DIR}/${PACKAGE_BASENAME}.tar.gz" \
    TTF OTF Webfonts LICENSE.txt README.md manifest.json

echo "packaging: done"
ls -la "${OUTPUT_DIR}"
