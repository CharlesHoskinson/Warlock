#!/usr/bin/env bash
# collect.sh <kind> [query]  -> TSV: type size mtime path   (smart collections, computed live)
kind=$1; q=$2
IMG="jpg jpeg png webp gif bmp avif svg tif tiff heic jxl"
VID="mp4 mkv webm mov avi m4v wmv flv"
AUD="mp3 flac ogg opus wav m4a aac"
DOC="pdf doc docx odt txt md epub xls xlsx ods csv ppt pptx odp rtf"
names() { local first=1; printf '( '; for e in $1; do [ $first = 1 ] || printf ' -o '; printf -- "-iname *.%s" "$e"; first=0; done; printf ' )'; }
expr() { local parts=(); for l in "$@"; do parts+=($(names "$l")); done; echo "${parts[@]}"; }
PRUNE=( \( -name '.*' -o -name node_modules -o -name __pycache__ -o -name site-packages -o -name venv -o -name target -o -name build \) -prune -o )
run() { # run <sortkey> <limit> find-args...
  local sk=$1 lim=$2; shift 2
  find "$@" -printf 'f\t%s\t%T@\t%p\n' 2>/dev/null | sort -t$'\t' -k"$sk","$sk"nr | head -n "$lim"
}
# expand a names-expression into find args
fargs() { read -ra A <<< "$(names "$1")"; printf '%s\n' "${A[@]}"; }
mapfile -t I < <(fargs "$IMG"); mapfile -t V < <(fargs "$VID"); mapfile -t D < <(fargs "$DOC"); mapfile -t U < <(fargs "$AUD")
case $kind in
  recent)
    PRUNE=( \( -name '.*' -o -name node_modules -o -name __pycache__ -o -name site-packages -o -name venv -o -name target -o -name build -o -name models -o -name Wallpapers \) -prune -o )
    run 3 150 "$HOME" -xdev "${PRUNE[@]}" -type f -newermt '35 days ago' \( "${I[@]}" -o "${V[@]}" -o "${D[@]}" -o "${U[@]}" \) ;;
  images) run 3 800 "$HOME" -xdev "${PRUNE[@]}" -type f "${I[@]}" ;;
  videos) run 3 800 "$HOME" -xdev "${PRUNE[@]}" -type f "${V[@]}" ;;
  documents) run 3 800 "$HOME" -xdev "${PRUNE[@]}" -type f "${D[@]}" ;;
  downloads) run 3 800 "$HOME/Downloads" -maxdepth 3 -type f ;;
  large) run 2 200 "$HOME" -xdev "${PRUNE[@]}" -type f -size +100M ;;
  screenshots) run 3 800 "$HOME" -xdev "${PRUNE[@]}" -type f -iname 'screenshot*' "${I[@]}" ;;
  search)
    find "$HOME" -xdev "${PRUNE[@]}" -iname "*$q*" -printf '%Y\t%s\t%T@\t%p\n' 2>/dev/null | sort -t$'\t' -k3,3nr | head -n 400 ;;
esac
