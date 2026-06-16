#!/usr/bin/env bash
# Pushes ONLY the contents of memoria_tfg/ to Overleaf as root.
# Uses git plumbing to avoid submodule/working-tree issues.
set -e

REPO=$(git rev-parse --show-toplevel)
cd "$REPO"

git fetch overleaf

TREE=$(git rev-parse HEAD:memoria_tfg)
PARENT=$(git rev-parse overleaf/master)
COMMIT=$(git commit-tree "$TREE" -p "$PARENT" -m "sync: update Overleaf from memoria_tfg/")

git push overleaf "$COMMIT":master

echo "Overleaf sync done — only memoria_tfg/ content pushed."
