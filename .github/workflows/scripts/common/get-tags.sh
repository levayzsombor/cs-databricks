#!/bin/bash
echo "TAG=$(git describe --tags --abbrev=0)" >> "$GITHUB_ENV"
echo "TAG_SHA=$(git rev-list -n 1 "$TAG")" >> "$GITHUB_ENV"