#!/usr/bin/env bash
# check_paper.sh — automated consistency guardian for the paper.
# Runs the automatable items of PAPER_REVIEW_CHECKLIST.md so that no
# inconsistency slips through on a paper update. Wire it as a git pre-commit
# hook (see install at the bottom) or run it manually: bash check_paper.sh
#
# Exit code 0 = all good, 1 = at least one check failed.

set -uo pipefail
# Resolve to the paper repo root, whether run manually or as a git hook (symlink).
cd "$(git rev-parse --show-toplevel 2>/dev/null || dirname "$0")"

TEX=main.tex
BIB=references.bib
fail=0
note() { printf '  %s\n' "$1"; }
ok()   { printf '\033[32m[ OK ]\033[0m %s\n' "$1"; }
bad()  { printf '\033[31m[FAIL]\033[0m %s\n' "$1"; fail=1; }

# 1. Every \cite{} key exists in references.bib
echo "== 1. Citations defined =="
missing=0
keys=$(grep -oE '\\cite[tp]?\{[^}]*\}' "$TEX" | sed -E 's/\\cite[tp]?\{//; s/\}//' | tr ',' '\n' | sed 's/ //g' | sort -u)
for k in $keys; do
  [ -z "$k" ] && continue
  if ! grep -q "{$k," "$BIB"; then bad "citation not in $BIB: $k"; missing=1; fi
done
[ "$missing" -eq 0 ] && ok "all \\cite{} keys present in $BIB"

# 2. No stray editing notes / merge markers in the body (hard fail);
#    TODO/pending markers are reported as warnings (tracked, not blocking).
echo "== 2. No stray notes =="
if grep -nE 'CAMBIAR|FIXME|XXX|^<<<<<<< |^=======$|^>>>>>>> ' "$TEX" >/tmp/_paper_notes 2>/dev/null && [ -s /tmp/_paper_notes ]; then
  bad "stray notes / merge markers found:"; sed 's/^/      /' /tmp/_paper_notes
else
  ok "no stray notes / merge markers"
fi
if grep -nE 'TODO|PENDIENTE' "$TEX" >/tmp/_paper_todo 2>/dev/null && [ -s /tmp/_paper_todo ]; then
  printf '\033[33m[WARN]\033[0m %s\n' "open TODO(s) (not blocking):"; sed 's/^/      /' /tmp/_paper_todo
fi

# 3. Regression guard: old/discarded numbers must not reappear
#    (canonical values live in DATA_CONSISTENCY.md)
echo "== 3. Regression guard (discarded values) =="
guard=0
for pat in '829' '3\.32' '22~ms' 'i7-8750' 'UYVY' 'WiFi' '802\.11'; do
  if grep -nE "$pat" "$TEX" >/dev/null 2>&1; then
    bad "discarded value/term present: '$pat' (see DATA_CONSISTENCY.md)"; guard=1
  fi
done
[ "$guard" -eq 0 ] && ok "no discarded values present"

# 4. Compile and check for undefined references/citations
echo "== 4. Compile + undefined refs =="
if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -shell-escape -interaction=nonstopmode "$TEX" >/tmp/_paper_build.log 2>&1 || true
  latexmk -pdf -shell-escape -interaction=nonstopmode "$TEX" >/tmp/_paper_build.log 2>&1 || true
  undef=$(grep -ciE 'Citation .* undefined|Reference .* undefined' main.log 2>/dev/null)
  undef=${undef:-0}
  if [ "$undef" -gt 0 ]; then
    bad "$undef undefined reference(s)/citation(s):"
    grep -iE 'Citation .* undefined|Reference .* undefined' main.log | sort -u | sed 's/^/      /' | head
  else
    ok "compiles with 0 undefined references"
  fi
else
  note "latexmk not found; skipping compile check"
fi

echo
if [ "$fail" -eq 0 ]; then
  printf '\033[32mPAPER CHECKS PASSED\033[0m\n'
else
  printf '\033[31mPAPER CHECKS FAILED — fix before committing\033[0m\n'
fi
exit "$fail"

# ---------------------------------------------------------------------------
# This script lives in the main repo; the paper repo's pre-commit hook points
# to it by absolute path. Install once from the project root:
#   ln -sf "$(pwd)/docs/paper-workbench/check_paper.sh" paper/.git/hooks/pre-commit
# Then every `git commit` inside paper/ runs these checks automatically.
# ---------------------------------------------------------------------------
