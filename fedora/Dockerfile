ARG base_image=fedora
ARG base_image_tag=42

# Copy the statically compiled compiler from this image
FROM 84codes/crystal:latest-alpine AS alpine

FROM $base_image:$base_image_tag AS builder
# add dependencies required for building crystal from source
RUN dnf install -y --nodocs --repo=fedora,updates \
        git gcc gcc-c++ make gc-devel \
        llvm-devel \
        pcre2-devel libxml2-devel libyaml-devel libffi-devel \
        openssl-devel zlib-devel gmp-devel autoconf automake libtool \
        rpm-build rpmdevtools && \
    dnf clean all
RUN git config --global advice.detachedHead false

# Use static compiler to compile crystal
COPY --from=alpine /usr/bin/shards /usr/bin/
COPY --from=alpine /usr/bin/crystal /usr/bin/
COPY --from=alpine /usr/share/crystal /usr/share/crystal

# Setup RPM build environment
RUN rpmdev-setuptree

# use rpmbuild to build RPM package
WORKDIR /root/rpmbuild
COPY crystal.spec /root/rpmbuild/SPECS/

ARG crystal_version=1.16.1
ARG gc_version=8.2.8
ARG shards_version=0.19.1
ARG pkg_revision=1

# Build the RPM package
RUN rpmbuild -bb SPECS/crystal.spec \
    --define "crystal_version $crystal_version" \
    --define "gc_version $gc_version" \
    --define "shards_version $shards_version"

# put .rpm file in a scratch image for exporting
FROM scratch AS pkgs
COPY --from=builder /root/rpmbuild/RPMS/*/*.rpm .

# start from a clean image
FROM $base_image:$base_image_tag
COPY --from=builder /root/rpmbuild/RPMS/*/*.rpm .
RUN dnf install -y --nodocs --repo=fedora,updates git curl make ./*.rpm && dnf clean all && rm ./*.rpm
# set the default cmd, example usage: docker run --rm 84codes/crystal eval 'puts "hello world"'
ENTRYPOINT ["/usr/bin/crystal"]
