#!/usr/bin/env bash
# sync_full.sh — Sincroniza el working dir de este PC con el repositorio
# privado de trabajo (voctomix-2.0-full), para que este PC y el portatil no
# se descoordinen. No toca el repo principal (origin publico ni Overleaf):
# usa un clon "espejo" aparte que es quien habla con GitHub.
#
#   push   -> sube el estado ACTUAL de este PC al repo privado
#   pull   -> trae los cambios del repo privado a este PC (pide confirmacion)
#   status -> muestra que cambiaria, sin tocar nada
#
# Regla de oro para no perder trabajo:
#   Al empezar en una maquina:  bash sync_full.sh pull
#   Al terminar en una maquina: bash sync_full.sh push
#   No edites las dos maquinas a la vez sin sincronizar en medio.

set -euo pipefail

WORKDIR="/home/sonda/Documentos/voctomix"
MIRROR="/home/sonda/Documentos/voctomix-2.0-full"
REMOTE="git@github.com:martin1210235/voctomix-2.0-full.git"

EXCLUDES=(
  --exclude='.git/'
  --exclude='__pycache__/'
  --exclude='*.pyc'
  --exclude='.~lock.*'
  --exclude='.DS_Store'
  --exclude='registros/'
  --exclude='*.log'
  --exclude='sessions/'
  --exclude='presentacion_tfg/backups/'
  --exclude='.env'
  --exclude='TFG_Mar_Vivanco.pdf'
  --exclude='presentacion_tfg/TFG-Mar Vivanco-presentación (1) (1).pptx'
)

ensure_mirror() {
  if [ ! -d "$MIRROR/.git" ]; then
    echo "Clonando el repo privado en $MIRROR ..."
    git clone "$REMOTE" "$MIRROR"
  fi
}

case "${1:-}" in
  push)
    ensure_mirror
    echo "1/4 Actualizando espejo desde GitHub..."
    git -C "$MIRROR" pull --ff-only
    echo "2/4 Copiando el estado del PC al espejo..."
    rsync -a --delete "${EXCLUDES[@]}" "$WORKDIR/" "$MIRROR/"
    echo "3/4 Registrando cambios..."
    git -C "$MIRROR" add -A
    if git -C "$MIRROR" diff --cached --quiet; then
      echo "4/4 Nada que subir: ya estaba sincronizado."
    else
      git -C "$MIRROR" -c user.name='martin1210235' \
        -c user.email='martin.herranz.sanchez11@gmail.com' \
        commit -q -m "sync: workspace desde PC ($(date +'%Y-%m-%d %H:%M'))"
      echo "4/4 Subiendo a voctomix-2.0-full..."
      git -C "$MIRROR" push
      echo "Hecho: repo privado actualizado con el estado del PC."
    fi
    ;;

  pull)
    ensure_mirror
    echo "1/2 Trayendo cambios desde GitHub al espejo..."
    git -C "$MIRROR" pull --ff-only
    echo "2/2 Cambios que se aplicarian a este PC (simulacion):"
    CHANGES=$(rsync -a -c --itemize-changes --dry-run "${EXCLUDES[@]}" "$MIRROR/" "$WORKDIR/" \
              | grep -E '^[>c<]f' || true)
    if [ -z "$CHANGES" ]; then
      echo "  (sin diferencias: este PC ya esta al dia)"
      exit 0
    fi
    echo "$CHANGES"
    echo
    read -rp "Aplicar estos cambios al working dir del PC? [y/N] " ans
    if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
      rsync -a "${EXCLUDES[@]}" "$MIRROR/" "$WORKDIR/"
      echo "Hecho: working dir del PC actualizado."
    else
      echo "Cancelado. No se ha tocado nada."
    fi
    ;;

  status)
    ensure_mirror
    git -C "$MIRROR" fetch -q || true
    echo "Ficheros donde el PC difiere del espejo (pendientes de 'push'):"
    OUT=$(rsync -a -c --itemize-changes --dry-run --delete "${EXCLUDES[@]}" "$WORKDIR/" "$MIRROR/" \
          | grep -E '^[>c<*]' || true)
    [ -z "$OUT" ] && echo "  (sin diferencias)" || echo "$OUT"
    ;;

  *)
    echo "Uso: bash sync_full.sh {push|pull|status}"
    echo "  push   -> sube el estado de este PC al repo privado"
    echo "  pull   -> trae los cambios del repo privado a este PC (con confirmacion)"
    echo "  status -> muestra que cambiaria sin tocar nada"
    exit 1
    ;;
esac
