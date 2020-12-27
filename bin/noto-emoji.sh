#!/usr/bin/env bash
#
# download and rename google noto emoji
#

set -o errexit
set -o pipefail
set -o nounset

echo "INFO: starting at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

REPO_URL=https://github.com/googlefonts/noto-emoji
REPO_DIR=$(basename ${REPO_URL})
REPO_SUBDIR=svg


SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"
TMP_DIR=$(realpath "${SCRIPT_HOME}/../tmp")

TARGET_DIR=${TARGET_DIR:-docs}
DEST_DIR=$(realpath "${SCRIPT_HOME}/../${TARGET_DIR}")

if [ -d "${TMP_DIR}" ]; then
    echo "WARNING: re-using existing tmp directory ${TMP_DIR}"
else
    echo "INFO: creating tmp directory ${TMP_DIR}"
    mkdir -p "${TMP_DIR}"
fi

if [ ! -d "${DEST_DIR}/svg" ]; then
    echo "INFO: creating output directory ${DEST_DIR}/svg"
    mkdir -p "${DEST_DIR}/svg"
fi

if [ ! -d "${DEST_DIR}/png" ]; then
    echo "INFO: creating output directory ${DEST_DIR}/png"
    mkdir -p "${DEST_DIR}/png"
fi

LOCAL_DIR="${TMP_DIR}/${REPO_DIR}"
if [ ! -d "${LOCAL_DIR}" ]; then
    echo "INFO: cloning a fresh copy"
    git clone --depth 1 ${REPO_URL}.git ${LOCAL_DIR}
else
    echo "INFO: using existing clone"
fi

SVG_FILES=($(find ${LOCAL_DIR}/${REPO_SUBDIR} -name "*.svg"))
echo "INFO: found ${#SVG_FILES[@]} SVGs"

if [ "${MAX_ICONS:-BAD}" != "BAD" ]; then
    SVG_FILES=("${SVG_FILES[@]:0:${MAX_ICONS}}")
    echo "INFO: truncating to ${MAX_ICONS}"
fi

echo -n "INFO processing..."
for SVG_FILE in "${SVG_FILES[@]}"
do
    #echo "DEBUG: processing ${SVG_FILE}..."
    BAD_NAME=$(basename "${SVG_FILE}" .svg)
    NICE_NAME="${BAD_NAME##emoji_u}"
    NICE_SVG="${DEST_DIR}/svg/${NICE_NAME}.svg"
    NICE_PNG="${DEST_DIR}/png/${NICE_NAME}.png"

    if [ ! -f "${NICE_SVG}" ]; then
        echo -n "."
        cp "${SVG_FILE}" "${NICE_SVG}"
    fi

    if [ ! -f "${NICE_PNG}" ]; then
        echo -n "+"
        ${SCRIPT_HOME}/svg2png.sh "${SVG_FILE}" "${NICE_PNG}"
    fi

done
echo ""

echo "INFO: complete at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
