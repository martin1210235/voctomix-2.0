#!/usr/bin/env bash
set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

STAGED_PY=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -n "$STAGED_PY" ]; then
    echo "Running PEP8 lint..."
    ./check_pep8.sh
    echo "Running voctocore tests..."
    ./voctocore/test.sh
fi

STAGED_TEX=$(git diff --cached --name-only --diff-filter=ACM | grep '\.tex$' || true)

if [ -n "$STAGED_TEX" ]; then
    echo "Compiling LaTeX..."
    cd memoria_tfg && latexmk -pdf -silent main.tex && cd ..
fi

echo "Pre-commit checks passed."
