ARG base_image=debian
ARG codename=bookworm
ARG crystal_version=1.16.0
ARG llvm_version=19

# Copy the statically compiled compiler from this image
FROM 84codes/crystal:latest-alpine AS alpine

FROM $base_image:$codename AS builder
# add dependencies required for building crystal from source
ARG llvm_version
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y git gcc g++ pkg-config make \
    libpcre2-dev libevent-dev libssl-dev libgmp-dev libyaml-dev libxml2-dev zlib1g-dev llvm-$llvm_version-dev \
    autoconf automake libtool libffi-dev devscripts debhelper dh-make
RUN git config --global advice.detachedHead false

COPY --from=alpine /usr/bin/shards /usr/bin/
COPY --from=alpine /usr/bin/crystal /usr/bin/
COPY --from=alpine /usr/share/crystal /usr/share/crystal

# build libgc
WORKDIR /tmp/libgc
ARG gc_version=8.2.8
RUN git clone --depth=1 --single-branch --branch=v${gc_version} https://github.com/ivmai/bdwgc.git . && \
  ./autogen.sh && \
  ./configure --disable-debug --disable-shared --enable-large-config --prefix=/usr && \
  make -j$(nproc) $(shell dpkg-buildflags --export=cmdline) && \
  make install

# Build crystal
WORKDIR /tmp/crystal
ARG crystal_version
RUN git clone --depth=1 --single-branch --branch=$crystal_version https://github.com/crystal-lang/crystal.git . && \
  gzip -9 man/crystal.1 && \
  make crystal release=1 interpreter=1 PREFIX=/usr CRYSTAL_CONFIG_LIBRARY_PATH=/usr/lib/crystal LDFLAGS="$(dpkg-buildflags --get LDFLAGS)" && \
  rm -f src/llvm/ext/llvm_ext.o

# Build shards
WORKDIR /tmp/shards
ARG shards_version=0.19.1
RUN git clone --depth=1 --single-branch --branch=v${shards_version} https://github.com/crystal-lang/shards.git . && \
  gzip -9 man/shards.1 man/shard.yml.5 && \
  make bin/shards release=1 FLAGS="--link-flags=\"$(dpkg-buildflags --get LDFLAGS)\""

# Setup package source directory
WORKDIR /tmp/pkg/crystal-${crystal_version}

COPY debian/ debian/
# Create debian directory structure
RUN mkdir -p usr/share/man/man1 \
    usr/share/man/man5 \
    usr/share/crystal \
    usr/bin \
    usr/lib/crystal

# Copy files
RUN cp /tmp/crystal/man/crystal.1.gz usr/share/man/man1/ && \
    cp /tmp/shards/man/shards.1.gz usr/share/man/man1/ && \
    cp /tmp/shards/man/shard.yml.5.gz usr/share/man/man5/ && \
    cp -r /tmp/crystal/src usr/share/crystal/ && \
    cp /tmp/crystal/.build/crystal usr/bin/ && \
    cp /tmp/shards/bin/shards usr/bin/ && \
    cp /usr/lib/libgc.a usr/lib/crystal/

# Copy debian package files
ARG pkg_revision=1

# Update version and llvm version in control file
RUN sed -i "s/\${crystal_version}/${crystal_version}/g; s/\${pkg_revision}/${pkg_revision}/g; s/\$(date -R)/$(date -R)/g" debian/changelog && \
    sed -i "s/\$(date +%Y)/$(date +%Y)/g" debian/copyright

# Build the package
RUN debuild -us -uc -b

# put .deb file in a scratch image for exporting
FROM scratch AS pkgs
COPY --from=builder /tmp/pkg/../*.deb .

# start from a clean image
FROM $base_image:$codename
# add dependencies commonly required for building crystal applications
COPY --from=builder /tmp/pkg/*.deb .
RUN apt-get update && \
    apt-get install -y curl gnupg make ./*.deb && \
    rm -rf /var/lib/apt/lists/* ./*.deb
# set the default cmd, example usage: docker run --rm 84codes/crystal eval 'puts "hello world"'
ENTRYPOINT ["/usr/bin/crystal"]
