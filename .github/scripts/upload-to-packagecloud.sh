#!/bin/bash
set -euxo pipefail

# Arguments:
# $1 - Package type (deb or rpm)
# $2 - Distribution information (distro/version)

PACKAGECLOUD_TOKEN="$PACKAGECLOUD_TOKEN"
PKG_TYPE="$1"
DIST_INFO="$2"

# Parse distribution name and version
IFS='/' read -r DIST_NAME DIST_VERSION <<< "$DIST_INFO"

# If distributions.json doesn't exist, download it
if [ ! -f distributions.json ]; then
  curl -fsSO -u "$PACKAGECLOUD_TOKEN:" https://packagecloud.io/api/v1/distributions.json
fi

# Get distribution ID
DIST_ID=$(jq ".${PKG_TYPE}[] | select(.index_name == \"$DIST_NAME\").versions[] | select(.index_name == \"$DIST_VERSION\").id" distributions.json)

# Find and upload packages
find pkgs -name "*.$PKG_TYPE" | xargs -I{} curl -fsSu "$PACKAGECLOUD_TOKEN:" \
  -F "package[distro_version_id]=$DIST_ID" \
  -F "package[package_file]=@{}" \
  -XPOST https://packagecloud.io/api/v1/repos/84codes/crystal/packages.json
