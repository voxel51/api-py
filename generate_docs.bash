#!/usr/bin/env bash
# Generate API documentation
#
# Usage:
#  bash generate_docs.bash
#
# Copyright 2018, Voxel51, LLC
# voxel51.com
#

echo "**** Generating API documentation"

sphinx-apidoc -f -o docs/source voxel51/

cd docs
make html
cd ..

echo "**** API documentation complete"
