#!/bin/bash
# du.sh DIR -> "bytes<TAB>path" for depth<=2, low priority
exec nice -n 19 ionice -c3 du -x -B1 -d 2 -- "${1:-$HOME}" 2>/dev/null
