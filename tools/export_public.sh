#!/usr/bin/env bash
# export_public.sh — copy ONLY the public subset of the project into a clean
# directory, ready to be published as a public repository (GATV GitLab / GitHub).
#
# Safety model: ALLOWLIST. Only the paths listed in PUBLIC below are copied;
# everything else (thesis, paper, internal notes, session logs, personal files)
# is left behind by default. Nothing is pushed anywhere — this only prepares a
# folder; you review it and push it yourself.
#
# Usage:  bash tools/export_public.sh [TARGET_DIR]
#         (default TARGET_DIR: ../voctomix2-public)

set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(cd "$(dirname "$0")/.." && pwd)")"
cd "$ROOT"
SRC="$(pwd)"
DST="${1:-$SRC/../voctomix2-public}"

# --- PUBLIC allowlist (code, infra, docs, scripts) ---
PUBLIC=(
  # core project code
  voctocore voctogui vocto
  # source / utility scripts
  example-scripts tools
  # deployment scenarios
  1pc_escenario1 2pc_escenario2 docker_escenario3 k8s k8s_escenario
  # assets
  images
  # documentation (paper-workbench is removed below)
  docs
  # CI
  .github
  # container / infra files
  Dockerfile docker-compose.yml docker-compose.experiments.yml docker-compose.stability.yml
  docker-ep.sh check_pep8.sh
  launch_docker_studio.sh launch_k8s.sh start_server.sh start_studio_single_pc.sh
  # project meta
  README.md README_DOCKER.md README-TRANSITIONS.md
  CHANGELOG.md CONTRIBUTING.md CODE_OF_CONDUCT.md SECURITY.md LICENSE.txt CITATION.cff .env.example
)

# --- Reproducibility: measurement scripts + raw logs (TFG write-ups excluded below) ---
PUBLIC+=( experiments )

echo "Source : $SRC"
echo "Target : $DST"
if [ -e "$DST" ] && [ -n "$(ls -A "$DST" 2>/dev/null)" ]; then
  echo "ERROR: target exists and is not empty. Choose an empty/new dir." >&2
  exit 1
fi
mkdir -p "$DST"

copy() {
  local item="$1"
  [ -e "$SRC/$item" ] || { echo "  skip (missing): $item"; return; }
  if [ -d "$SRC/$item" ]; then
    rsync -a --exclude '__pycache__' --exclude '*.pyc' --exclude '.DS_Store' \
          "$SRC/$item" "$DST/"
  else
    cp -p "$SRC/$item" "$DST/"
  fi
  echo "  + $item"
}

echo "== Copying public allowlist =="
for item in "${PUBLIC[@]}"; do copy "$item"; done

# Remove internal notes that live inside docs/
rm -rf "$DST/docs/paper-workbench"
rm -f "$DST/docs/DOC_PATTERNS.md"
# Drop TFG-flavoured write-ups if experiments/ was included
rm -f "$DST/experiments/"*_CAP5.md 2>/dev/null || true
# Drop junk asset
rm -f "$DST/images/bg(feoooo).png" 2>/dev/null || true

# Public-facing .gitignore for the new repo
cat > "$DST/.gitignore" <<'EOF'
__pycache__/
*.pyc
registros/
*.log
.env
EOF

echo "== Secret scan (should be empty) =="
if grep -rniE 'password\s*=|secret\s*=|api[_-]?key|token\s*=|BEGIN .*PRIVATE KEY' "$DST" \
     2>/dev/null | grep -viE 'RABBITMQ_DEFAULT_PASS|guest|example|password_file|#|export_public.sh'; then
  echo "  !! review the matches above before publishing"
else
  echo "  clean: no obvious secrets"
fi

cat <<EOF

Done. Clean public copy is at: $DST

Next (you run these, with your own credentials):
  cd "$DST"
  git init && git add -A && git commit -m "Initial public release: Voctomix 2.0"
  # GitHub:
  #   git remote add origin git@github.com:martin1210235/voctomix-2.0.git
  # GATV GitLab:
  #   git remote add origin git@gitlab.com:GATV/nemo/voctomix.git
  git push -u origin main

Review the folder contents before pushing. Nothing was pushed by this script.
EOF
