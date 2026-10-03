#!/bin/bash
# search.sh DIR QUERY -> list.sh-style records (full path as name), skipping dot-dirs
cd -- "$1" 2>/dev/null || exit 1
find . -mindepth 1 \( -name '.*' -o -name node_modules \) -prune -o -iname "*$2*" -printf '%Y\t%y\t%s\t%T@\t%p\036' 2>/dev/null | head -c 400000
