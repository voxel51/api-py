#!/usr/bin/env bash
# Generates documentation for the voxel51-api-py package.
#
# Usage:
#   bash docs/generate_docs.bash
#
# Copyright 2017-2019, Voxel51, Inc.
# voxel51.com
#

SOURCE_DIR=docs/source
BUILD_DIR=docs/build

# Show usage information
usage() {
    echo "Usage:  bash $0 [-h] [-c]

Getting help:
-h      Display this help message.

Build options:
-c      Perform a clean build by first deleting any existing build directory.
"
}

# Parse flags
SHOW_HELP=false
CLEAN_BUILD=false
while getopts "hc" FLAG; do
    case "${FLAG}" in
        h) SHOW_HELP=true ;;
        c) CLEAN_BUILD=true ;;
        *) usage ;;
    esac
done
[ ${SHOW_HELP} = true ] && usage && exit 0

if [ ${CLEAN_BUILD} = true ]; then
    echo "**** Deleting existing build directory, if necessary"
    rm -rf ${BUILD_DIR}
fi

#
# We exclude `voxel51/cli` from the generated docs, because the CLI is
# self-documenting from the command-line
#
echo "**** Generating documentation"
sphinx-apidoc -f -o ${SOURCE_DIR} voxel51 voxel51/cli

cd docs
make html
cd ..

echo "**** Documentation complete"
printf "To view the docs, run:\n\nopen ${BUILD_DIR}/html/index.html\n\n"
