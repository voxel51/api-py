#!/usr/bin/env bash
# Generates Python client library documentation.
#
# Usage:
#   bash docs/generate_docs.bash
#
# Copyright 2017-2019, Voxel51, Inc.
# voxel51.com
#

echo "**** Generating documentation"

sphinx-apidoc -f -o docs/source voxel51/

cd docs
make html
cd ..

echo "**** Documentation complete"
