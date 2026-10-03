#!/bin/bash
# thumb.sh FILE -> prints path to a PNG thumbnail (freedesktop cache first, then generated).
f="$1"; cache="${FILES_CACHE:-${XDG_CACHE_HOME:-$HOME/.cache}/omarchy-files}/thumbs"
mkdir -p "$cache"
uri=$(python3 -c 'import sys,urllib.parse as u;print("file://"+u.quote(sys.argv[1]))' "$f")
h=$(printf '%s' "$uri" | md5sum | cut -d' ' -f1)
for s in large normal; do t="$HOME/.cache/thumbnails/$s/$h.png"; [ -f "$t" ] && { echo "$t"; exit 0; }; done
key=$(printf '%s%s' "$f" "$(stat -c %Y -- "$f")" | md5sum | cut -d' ' -f1)
out="$cache/$key.png"
[ -s "$out" ] && { echo "$out"; exit 0; }
case "${f,,}" in
  *.pdf) pdftoppm -png -singlefile -scale-to 512 -f 1 -l 1 -- "$f" "${out%.png}" ;;
  *) ffmpegthumbnailer -i "$f" -o "$out" -s 512 -q 6 2>/dev/null ;;
esac
[ -s "$out" ] && echo "$out"
