#!/bin/bash
# recent.sh -> newest files under $HOME (skips dot-dirs and heavy dirs)
cd -- "$HOME" || exit 1
find . -mindepth 1 \( -name '.*' -o -name node_modules -o -name __pycache__ -o -name target -o -name venv -o -name models -o -name Wallpapers \) -prune -o \
  -type f -mtime -30 -printf '%T@\t%s\t%p\n' 2>/dev/null | sort -rn | head -${1:-60}
