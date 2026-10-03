#!/bin/bash
# ops.sh copy|move|mkdir|newfile|rename|trash ARGS...
#
#   copy    DEST SRC...   copy each SRC into DEST
#   move    DEST SRC...   move each SRC into DEST (SRC already in DEST: skipped)
#   mkdir   DIR NAME      create folder DIR/NAME   (prints the created path)
#   newfile DIR NAME      create empty file DIR/NAME (prints the created path)
#   rename  SRC NEWPATH   rename within the same folder
#   trash   PATH...       move to the freedesktop trash (gio trash)
#
# Never uses rm and never overwrites: copy/move/mkdir/newfile pick a free name
# ("x (copy).ext", "x (copy 2).ext", ...). Multi-item ops run in order and stop
# at the first failure (earlier items stay done).
#
# Exit codes (the explorer and the Quint model depend on these):
#   0 ok · 1 failed / missing source · 2 target exists (rename) ·
#   3 folder into itself · 4 invalid name · 13 permission denied
#   64 usage
#
# Formal model: ~/.local/share/omarchy-files/spec/fileops.qnt
set -u

die() { exit "$1"; }

valid_name() { # NAME -> ok if usable as a single path component
  case "$1" in ''|.|..|*/*) return 1 ;; esac
  return 0
}

uniq_name() { # DIR BASE -> free path
  local d="$1" b="$2" stem ext n=1 c
  c="$d/$b"
  [ -e "$c" ] || [ -L "$c" ] || { printf '%s' "$c"; return; }
  if [[ "$b" == *.* && "$b" != .* ]]; then stem="${b%.*}"; ext=".${b##*.}"; else stem="$b"; ext=""; fi
  c="$d/$stem (copy)$ext"
  while [ -e "$c" ] || [ -L "$c" ]; do n=$((n+1)); c="$d/$stem (copy $n)$ext"; done
  printf '%s' "$c"
}

need_dir() { [ -d "$1" ] || die 1; }                 # target folder must exist
need_w()   { [ -w "$1" ] && [ -x "$1" ] || die 13; } # ...and be writable
exists()   { [ -e "$1" ] || [ -L "$1" ]; }
inside()   { # A B -> true if folder A is B or lies inside B
  local a b; a=$(realpath -m -- "$1"); b=$(realpath -m -- "$2")
  [ "$a" = "$b" ] || [[ "$a" == "$b"/* ]]
}

[ $# -ge 1 ] || die 64
op="$1"; shift
case "$op" in
  copy|move)
    [ $# -ge 2 ] || die 64
    dest="${1%/}"; [ -n "$dest" ] || dest=/; shift
    need_dir "$dest"
    for s in "$@"; do
      s="${s%/}"
      exists "$s" || die 1
      if [ -d "$s" ] && [ ! -L "$s" ] && inside "$dest" "$s"; then die 3; fi
      if [ "$op" = move ]; then
        [ "$(dirname -- "$s")" = "$dest" ] && continue
        need_w "$(dirname -- "$s")"
        # moving a folder to a new parent rewrites its "..", so it must be writable too
        if [ -d "$s" ] && [ ! -L "$s" ]; then need_w "$s"; fi
      fi
      need_w "$dest"
      t=$(uniq_name "$dest" "$(basename -- "$s")")
      if [ "$op" = copy ]; then cp -a --reflink=auto -- "$s" "$t" || die 1
      else mv -n -- "$s" "$t" || die 1; exists "$s" && die 1; fi
    done ;;
  mkdir|newfile)
    [ $# -eq 2 ] || die 64
    dir="${1%/}"; [ -n "$dir" ] || dir=/
    valid_name "$2" || die 4
    need_dir "$dir"; need_w "$dir"
    t=$(uniq_name "$dir" "$2")
    if [ "$op" = mkdir ]; then mkdir -- "$t" || die 1
    else ( set -C; : > "$t" ) 2>/dev/null || die 1; fi
    printf '%s\n' "$t" ;;
  rename)
    [ $# -eq 2 ] || die 64
    src="${1%/}"; new="${2%/}"
    valid_name "$(basename -- "$new")" || die 4
    [ "$(dirname -- "$src")" = "$(dirname -- "$new")" ] || die 4
    exists "$src" || die 1
    [ "$src" = "$new" ] && exit 0
    need_w "$(dirname -- "$src")"
    exists "$new" && die 2
    mv -n -- "$src" "$new" || die 1
    exists "$src" && die 1 ;;
  trash)
    [ $# -ge 1 ] || die 64
    for p in "$@"; do
      p="${p%/}"
      exists "$p" || die 1
      need_w "$(dirname -- "$p")"
      if [ -d "$p" ] && [ ! -L "$p" ]; then need_w "$p"; fi
      gio trash -- "$p" 2>/dev/null || die 1
    done ;;
  *) die 64 ;;
esac
exit 0
