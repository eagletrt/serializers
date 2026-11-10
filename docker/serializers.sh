#!/usr/bin/env bash
# Entrypoint of the generator image.
#
#   serializers generate [--in DIR] [--out DIR] [--force]   generate the code and the JSON Schemas
#   serializers check    [--in DIR]                         generate, compile the protos and run the tests
#   serializers clean    [--out DIR]                        remove the files that `generate` wrote
#
# `generate`, `check` and `clean` are also installed as commands, so a
# Dockerfile can simply `RUN generate --out /out`.
#
# Defaults: --in /in (read-only is fine), --out /out.
#
# `generate` writes into an empty folder, or into a folder that a previous run
# created. It refuses any other non-empty folder unless --force is given.
# Only the files listed in the folder's manifest (the ones a previous run
# wrote) are ever deleted, so a wrong --out cannot remove unrelated files.
set -euo pipefail

HOME_DIR="${SERIALIZERS_HOME:-/opt/serializers}"
IN_DIR="${SERIALIZERS_IN:-/in}"
OUT_DIR="${SERIALIZERS_OUT:-/out}"
FORCE=0
# The generator and compile_proto.sh expect the output folder to be relative to
# the sources, so the code is built in a temporary copy of the generator and
# copied to --out at the end. /opt/serializers itself is never written.
BUILD_DIR="serializers"
MARKER=".serializers-version"
MANIFEST=".serializers-manifest"

usage() {
    sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
}

cmd="$(basename "$0")"
if [ "$cmd" = "serializers" ] || [ "$cmd" = "serializers.sh" ]; then
    cmd="${1:-generate}"
    [ $# -gt 0 ] && shift
fi

while [ $# -gt 0 ]; do
    case "$1" in
        --in)    IN_DIR="${2:?--in needs a directory}"; shift 2 ;;
        --out)   OUT_DIR="${2:?--out needs a directory}"; shift 2 ;;
        --force) FORCE=1; shift ;;
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
    WORK_DIR="$(mktemp -d)"
    trap 'rm -rf "$WORK_DIR"' EXIT
    cp -R "$HOME_DIR/src" "$HOME_DIR/scripts" "$WORK_DIR"/
    chmod -R u+w "$WORK_DIR"
    cd "$WORK_DIR"
    python3 src/generator/main.py "$IN_DIR" "$BUILD_DIR"
    scripts/generate_schemas "$BUILD_DIR/proto" "$BUILD_DIR"
}

# Delete the files listed in the manifest of $OUT_DIR, then the folders that
# became empty because of it. Anything else in $OUT_DIR is left alone.
remove_generated() {
    [ -f "$OUT_DIR/$MANIFEST" ] || return 0
    (
        cd "$OUT_DIR"
        while IFS= read -r file; do
            case "$file" in
                ./*/../*|./../*|*/..) continue ;; # never leave the folder
                ./*) rm -f -- "$file" ;;
            esac
        done < "$MANIFEST"
        sed -n 's|^\./\(.*\)/[^/]*$|\1|p' "$MANIFEST" | sort -ru | while IFS= read -r dir; do
            rmdir -p --ignore-fail-on-non-empty -- "$dir" 2>/dev/null || true
        done
        rm -f -- "$MANIFEST" "$MARKER"
    )
}

case "$cmd" in
    generate)
        mkdir -p "$OUT_DIR"
        OUT_DIR="$(cd "$OUT_DIR" && pwd)"
        if [ ! -e "$OUT_DIR/$MARKER" ] && [ -n "$(ls -A "$OUT_DIR")" ] && [ "$FORCE" != 1 ]; then
            echo "error: '$OUT_DIR' is not empty and was not created by serializers." >&2
            echo "       Use an empty folder, or --force to write into it anyway" >&2
            echo "       (files with the same name are overwritten, nothing else is deleted)." >&2
            exit 2
        fi
        build
        remove_generated
        cp -R "$BUILD_DIR"/. "$OUT_DIR"/
        (cd "$BUILD_DIR" && find . -type f | LC_ALL=C sort) > "$OUT_DIR/$MANIFEST"
        echo "${SERIALIZERS_VERSION:-unknown}" > "$OUT_DIR/$MARKER"
        echo "[serializers] generated code in $OUT_DIR (generator ${SERIALIZERS_VERSION:-unknown})"
        ;;
    check)
        build
        scripts/compile_proto.sh
        pytest --verbose -p no:cacheprovider
        ;;
    clean)
        if [ ! -d "$OUT_DIR" ] || [ ! -e "$OUT_DIR/$MARKER" ]; then
            echo "[serializers] nothing to clean in $OUT_DIR"
            exit 0
        fi
        OUT_DIR="$(cd "$OUT_DIR" && pwd)"
        remove_generated
        echo "[serializers] removed the generated files from $OUT_DIR"
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
