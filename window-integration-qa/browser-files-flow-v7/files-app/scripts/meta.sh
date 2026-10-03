#!/usr/bin/env bash
# meta.sh <path> <kind> -> key=value lines
p=$1; k=$2
case $k in
  image) identify -format 'dims=%wx%h\n' "$p[0]" 2>/dev/null | head -1 ;;
  video) ffprobe -v error -select_streams v:0 -show_entries stream=width,height:format=duration -of default=nw=1 "$p" 2>/dev/null ;;
  pdf) pdfinfo "$p" 2>/dev/null | awk -F': *' '/^Pages/{print "pages="$2} /^Page size/{print "dims="$2}' ;;
esac
