#!/bin/bash
# preview.sh DIR -> "<item count>\t<up to 4 media paths>" (folder mosaic), cheap: top-level only
cd -- "$1" 2>/dev/null || exit 1
shopt -s nullglob
n=0; c=0; out=()
for f in *; do
  n=$((n+1))
  if [ $c -lt 4 ] && [ -f "$f" ]; then
    case "${f,,}" in *.jpg|*.jpeg|*.png|*.webp|*.gif|*.bmp|*.avif|*.mp4|*.mkv|*.webm|*.mov|*.pdf) out+=("$PWD/$f"); c=$((c+1));; esac
  fi
  [ $n -ge 300 ] && break
done
printf '%s' "$n"; for f in "${out[@]}"; do printf '\t%s' "$f"; done; printf '\n'
