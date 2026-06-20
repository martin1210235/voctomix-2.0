#!/bin/sh
set -e

# ignore import-not-at-top (required by gi)
pycodestyle --ignore=E402,E501 --exclude=voctocore,voctogui,vocto,experiments,doc,example-scripts .

# ignore long lines (prefer explanatory test-names)
pycodestyle --ignore=E501 voctocore/tests
