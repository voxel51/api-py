#!/usr/bin/env bash
# Generate Python client library documentation
#
# Usage:
#   bash docs/generate_docs.bash
#
# Copyright 2018, Voxel51, Inc.
# voxel51.com
#

echo "**** Generating API documentation"

sphinx-apidoc -f -o docs/source voxel51/

cd docs
make html
cd ..

echo "**** API documentation complete"
