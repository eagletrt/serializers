# syntax=docker/dockerfile:1
#
# Generator image: everything needed to turn a folder of .proto files into the
# C++/Python wrappers, the CMake project and the JSON Schemas.
#
#   docker run --rm -v $PWD/proto:/in:ro -v $PWD/out:/out \
#     ghcr.io/eagletrt/serializers:<version> generate
#
# The toolchain versions are pinned here: the same image always produces the
# same output. Published on ghcr.io on every `vX.Y.Z` tag (see
# .github/workflows/docker.yaml).

# Declared before the first FROM so that every stage can use it (see stage 2).
ARG PROTOC_VERSION=35.1

# ---- Stage 1: protoc-gen-jsonschema, built at a pinned commit ----------------
# The project has no semver tags that Go can resolve, so `@latest` is a moving
# target: pin the commit instead (this one is the HEAD of 2024-02-12).
#
# The stage runs on the build machine and cross-compiles for the target
# platform, so the arm64 variant is not built under QEMU emulation. With
# CGO_ENABLED=0 the binary is static. `go install` puts cross-compiled binaries
# in bin/<os>_<arch>/, hence the `find`.
FROM --platform=$BUILDPLATFORM golang:1.24-bookworm AS jsonschema
ARG TARGETOS
ARG TARGETARCH
ARG JSONSCHEMA_REF=73d5723042b812758310ea5ef661a273f0faa9ed
RUN CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${TARGETARCH} go install \
        github.com/chrusty/protoc-gen-jsonschema/cmd/protoc-gen-jsonschema@${JSONSCHEMA_REF} \
    && mkdir /out \
    && find "$(go env GOPATH)/bin" -type f -name protoc-gen-jsonschema -exec mv {} /out/ \; \
    && test -x /out/protoc-gen-jsonschema

# ---- Stage 2: protoc, from the official release -----------------------------
# protoc 35.x is the release of the protobuf 7.35.x Python runtime pinned in
# requirements.txt: the generated code and the runtime always match. Change
# PROTOC_VERSION, both checksums and requirements.txt together. The checksums
# are the sha256 digests that GitHub shows for the release assets; ADD fails
# the build if a download does not match.
FROM scratch AS protoc-amd64
ARG PROTOC_VERSION
ADD --checksum=sha256:6930ebf62bd4ea607b98fff052596c6ee564b9835b4ce172c75a3f53ae9d91b7 \
    https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOC_VERSION}/protoc-${PROTOC_VERSION}-linux-x86_64.zip /protoc.zip
FROM scratch AS protoc-arm64
ARG PROTOC_VERSION
ADD --checksum=sha256:01bf9d08808c7f96678b63f4bd8efa559bb4f83d5a7a270d5edaf507f9d5d9cf \
    https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOC_VERSION}/protoc-${PROTOC_VERSION}-linux-aarch_64.zip /protoc.zip
FROM protoc-${TARGETARCH} AS protoc

# ---- Stage 3: generator ------------------------------------------------------
FROM python:3.14-slim-trixie

# protoc (bin/protoc and the well-known types in include/) goes to /usr/local.
# The zip does not keep the executable bit, hence the chmod. The build fails if
# the binary does not report the expected version.
ARG PROTOC_VERSION
RUN --mount=from=protoc,source=/protoc.zip,target=/tmp/protoc.zip \
    python3 -m zipfile -e /tmp/protoc.zip /usr/local \
    && chmod 755 /usr/local/bin/protoc \
    && rm -f /usr/local/readme.txt \
    && protoc --version | grep -qx "libprotoc ${PROTOC_VERSION}"

# The Python dependencies, protobuf included, are pinned in requirements.txt.
WORKDIR /opt/serializers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=jsonschema /out/protoc-gen-jsonschema /usr/local/bin/protoc-gen-jsonschema
COPY src ./src
COPY scripts ./scripts
COPY docker/serializers.sh /usr/local/bin/serializers
RUN chmod +x /usr/local/bin/serializers scripts/compile_proto.sh scripts/generate_pb scripts/generate_schemas \
    && ln -s serializers /usr/local/bin/generate \
    && ln -s serializers /usr/local/bin/check \
    && ln -s serializers /usr/local/bin/clean
# /opt/serializers stays read-only: every run works in a temporary copy, so the
# container can run as any user (docker run --user) and with --read-only
# (plus a tmpfs on /tmp).

ARG VERSION=dev
ENV SERIALIZERS_VERSION=${VERSION} \
    HOME=/tmp \
    PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["serializers"]
CMD ["generate"]
