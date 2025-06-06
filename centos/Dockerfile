ARG base_image=quay.io/centos/centos
ARG base_image_tag=stream9
ARG crystal_version=1.16.1

# Copy the statically compiled compiler from this image
FROM --platform=$BUILDPLATFORM 84codes/crystal:latest-alpine AS alpine

FROM --platform=$BUILDPLATFORM $base_image:$base_image_tag AS builder
ARG llvm_version
# add dependencies required for building crystal from source
RUN dnf install -y --nodocs --enablerepo=crb \
        git gcc gcc-c++ make libevent-devel \
        llvm${llvm_version}-devel \
        pcre2-devel libxml2-devel libyaml-devel \
        zlib-devel gc-devel && \
    dnf clean all
COPY --from=alpine /usr/bin/shards /usr/bin/
COPY --from=alpine /usr/bin/crystal /usr/bin/
COPY --from=alpine /usr/share/crystal /usr/share/crystal
COPY --from=alpine /usr/share/man/man1/crystal.1.gz /usr/share/man/man1/
COPY --from=alpine /usr/share/man/man1/shards.1.gz /usr/share/man/man1/
COPY --from=alpine /usr/share/man/man5/shard.yml.5.gz /usr/share/man/man5/
# Cross compile for target architecture
ARG TARGETARCH
# Build crystal
WORKDIR /tmp/crystal
ARG crystal_version
RUN git clone --depth=1 --single-branch --branch=$crystal_version https://github.com/crystal-lang/crystal.git . && \
  gzip -9 man/crystal.1 && \
  mkdir .build && \
  make crystal interpreter=1 release=1 target=$TARGETARCH-unknown-linux-gnu \
    PREFIX=/usr FLAGS="--no-debug" CRYSTAL_CONFIG_LIBRARY_PATH=/usr/lib64/crystal | tail -1 > .build/crystal.sh
# Build shards
WORKDIR /tmp/shards
ARG shards_version=0.19.1
RUN git clone --depth=1 --single-branch --branch=v${shards_version} https://github.com/crystal-lang/shards.git . && \
  gzip -9 man/shards.1 man/shard.yml.5 && \
  make bin/shards FLAGS="--release --no-debug --cross-compile --target=$TARGETARCH-unknown-linux-gnu" | tail -1 > bin/shards.sh

# link on target platform
FROM $base_image:$base_image_tag AS target-builder
ARG llvm_version
RUN dnf install -y --nodocs --enablerepo=crb \
        git gcc gcc-c++ make libevent-devel \
        llvm${llvm_version}-devel \
        pcre2-devel libxml2-devel libyaml-devel libffi-devel \
        openssl-devel zlib-devel gmp-devel autoconf automake libtool && \
    dnf clean all
# build libgc
WORKDIR /tmp/libgc
ARG gc_version=8.2.8
RUN git clone --depth=1 --single-branch --branch=v${gc_version} https://github.com/ivmai/bdwgc.git . && \
  ./autogen.sh && \
  ./configure --disable-debug --disable-shared --enable-large-config --prefix=/usr && \
  make -j$(nproc) CFLAGS="-DNO_GETCONTEXT -pipe -fPIE -O3" && \
  make install
# Link crystal
WORKDIR /tmp/crystal
COPY --from=builder /tmp/crystal/Makefile .
COPY --from=builder /tmp/crystal/src/llvm/ext src/llvm/ext
COPY --from=builder /tmp/crystal/.build .build
RUN make llvm_ext
RUN sh -ex .build/crystal.sh && strip .build/crystal
# Link shards
WORKDIR /tmp/shards
COPY --from=builder /tmp/shards/bin bin
RUN sh -ex bin/shards.sh && strip bin/shards

# build rpm package
FROM --platform=$BUILDPLATFORM $base_image:$base_image_tag AS pkg-builder
RUN dnf install -y --nodocs \
    ruby ruby-devel make gcc rpm-build && gem install --no-document fpm
# build distribution packages
WORKDIR /tmp/pkg
# copy the binaries + stdlib + libgc from the build stage
COPY --from=builder /tmp/crystal/man/crystal.1.gz pkg/usr/share/man/man1/
COPY --from=builder /tmp/shards/man/shards.1.gz pkg/usr/share/man/man1/
COPY --from=builder /tmp/shards/man/shard.yml.5.gz pkg/usr/share/man/man5/
COPY --from=builder /tmp/crystal/src pkg/usr/share/crystal/src
COPY --from=target-builder /tmp/crystal/.build/crystal pkg/usr/bin/
COPY --from=target-builder /tmp/shards/bin/shards pkg/usr/bin/
COPY --from=target-builder /usr/lib64/libgc.a pkg/usr/lib64/crystal/
ARG llvm_version
ARG pkg_revision=1
ARG TARGETARCH
RUN fpm -s dir -t rpm -n crystal -v $(sed 's/-/~/' pkg/usr/share/crystal/src/VERSION) --iteration ${pkg_revision} -a ${TARGETARCH} \
  --url https://crystal-lang.org --maintainer "84codes <contact@84codes.com>" \
  --description "a general-purpose, object-oriented programming language" \
  --depends gcc --depends pkgconfig --depends libevent-devel \
  --depends pcre2-devel \
  --depends gmp-devel --depends openssl-devel --depends libxml2-devel \
  --depends libyaml-devel --depends zlib-devel \
  --depends llvm${llvm_version}-libs --depends libffi \
  --license "ASL 2.0" --chdir pkg .

# put .rpm file in a scratch image for exporting
FROM scratch AS pkgs
COPY --from=pkg-builder /tmp/pkg/*.rpm .

# start from a clean image
FROM $base_image:$base_image_tag
COPY --from=pkg-builder /tmp/pkg/*.rpm .
RUN dnf install -y --nodocs --enablerepo=crb git make ./*.rpm && dnf clean all && rm ./*.rpm
# set the default cmd, example usage: docker run --rm 84codes/crystal eval 'puts "hello world"'
ENTRYPOINT ["/usr/bin/crystal"]
