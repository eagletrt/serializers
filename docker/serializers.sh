#!/usr/bin/env bash
# Entrypoint of the generator image.
#
#   serializers generate [--in DIR] [--out DIR]   generate the code and the JSON Schemas
#   serializers check    [--in DIR]               generate, compile the protos and run the tests
#
# `generate` and `check` are also installed as commands, so a Dockerfile can
# simply `RUN generate --out /out`.
#
# Defaults: --in /in (read-only is fine), --out /out.
set -euo pipefail

HOME_DIR="${SERIALIZERS_HOME:-/opt/serializers}"
IN_DIR="${SERIALIZERS_IN:-/in}"
OUT_DIR="${SERIALIZERS_OUT:-/out}"
# The generator and compile_proto.sh expect the output folder to be relative to
# the sources, so the code is built here and copied to --out at the end.
BUILD_DIR="serializers"
MARKER=".serializers-version"

usage() {
    sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
}

cmd="$(basename "$0")"
if [ "$cmd" = "serializers" ] || [ "$cmd" = "serializers.sh" ]; then
    cmd="${1:-generate}"
    [ $# -gt 0 ] && shift
fi

while [ $# -gt 0 ]; do
    case "$1" in
        --in)  IN_DIR="${2:?--in needs a directory}"; shift 2 ;;
        --out) OUT_DIR="${2:?--out needs a directory}"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "error: unknown option '$1'" >&2; usage >&2; exit 2 ;;
    esac
done

build() {
    if [ ! -d "$IN_DIR" ] || ! find "$IN_DIR" -name '*.proto' -print -quit | grep -q .; then
        echo "error: no .proto files in '$IN_DIR' (mount them with -v <proto dir>:/in:ro)" >&2
        exit 2
    fi
    IN_DIR="$(cd "$IN_DIR" && pwd)"
    cd "$HOME_DIR"
    rm -rf "$BUILD_DIR" tests .generated scripts/.proto_sources.txt
    python3 src/generator/main.py "$IN_DIR" "$BUILD_DIR"
    scripts/generate_schemas "$BUILD_DIR/proto" "$BUILD_DIR"
}

case "$cmd" in
    generate)
        mkdir -p "$OUT_DIR"
        OUT_DIR="$(cd "$OUT_DIR" && pwd)"
        build
        # Only a folder that a previous run created is cleaned, so a wrong
        # --out can never delete unrelated files.
        if [ -e "$OUT_DIR/$MARKER" ]; then
            find "$OUT_DIR" -mindepth 1 -delete
        fi
        cp -a "$BUILD_DIR"/. "$OUT_DIR"/
        echo "${SERIALIZERS_VERSION:-unknown}" > "$OUT_DIR/$MARKER"
        echo "[serializers] generated code in $OUT_DIR (generator ${SERIALIZERS_VERSION:-unknown})"
        ;;
    check)
        build
        scripts/compile_proto.sh
        pytest --verbose
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        echo "error: unknown command '$cmd'" >&2
        usage >&2
        exit 2
        ;;
esac
