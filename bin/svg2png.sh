#!/usr/bin/env bash
#
# convert an svg to a png with rsvg
#

set -o errexit
set -o pipefail
set -o nounset

IN_FILE=${1:-BAD}
OUT_FILE=${2:-BAD}
if [ "${IN_FILE}" = "BAD"  ] || [ ${OUT_FILE:-BAD} == "BAD" ]; then
	echo "usage: svg2ico.sh IN_FILE OUT_FILE"
	echo "       IN_FILE is SVG file to convert"
	echo "       OUT_FILE is png file to create"
	exit 1
fi

SIZE=${SIZE:-512}

rsvg-convert \
    --format=png \
    --keep-aspect-ratio \
    --height=${SIZE} \
    --output="${OUT_FILE}" \
    --width=${SIZE} \
    "${IN_FILE}"
