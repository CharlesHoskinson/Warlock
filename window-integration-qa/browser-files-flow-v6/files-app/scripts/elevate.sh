#!/bin/bash
# elevate.sh OP ARGS...  — run one ops.sh operation as root, authorised through
# the sudo-askpass popup. Runs a root-owned copy of ops.sh, so a user-writable
# script is never executed as root.
#   exit 77  = authorisation cancelled / wrong password
#   exit 126 = root helper not installed
#   else     = ops.sh exit code
ROOT_OPS=/usr/local/lib/omarchy-files/ops.sh
[ -x "$ROOT_OPS" ] || exit 126
case "$1" in
  copy) what="Copy into $2" ;;
  move) what="Move into $2" ;;
  mkdir) what="Create folder $2/$3" ;;
  newfile) what="Create file $2/$3" ;;
  rename) what="Rename $2 → $(basename -- "$3")" ;;
  trash) what="Move to root's Trash: ${*:2}" ;;
  *) exit 64 ;;
esac
# Retry after a partial unprivileged run: move/trash sources that are already
# gone were done by that run, so only the remaining ones are sent.
if [ "$1" = move ] || [ "$1" = trash ]; then
  op="$1"; shift; keep=()
  [ "$op" = move ] && { keep+=("$1"); shift; }
  for s in "$@"; do { [ -e "$s" ] || [ -L "$s" ]; } && keep+=("$s"); done
  set -- "$op" "${keep[@]}"
  [ "$op" = trash ] && [ $# -eq 1 ] && exit 0
  [ "$op" = move ] && [ $# -eq 2 ] && exit 0
fi
export SUDO_ASKPASS="${ELEVATE_ASKPASS:-$HOME/.local/bin/sudo-askpass}"
export ASKPASS_REQUESTER="Files" ASKPASS_COMMAND="$what"
sudo -A -v 2>/dev/null || exit 77
# not exec: without a tty sudo keys its credential cache on the parent process,
# so this must be a sibling of the `sudo -v` above
sudo -n -- "$ROOT_OPS" "$@"
exit $?
