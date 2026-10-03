#!/bin/bash
# list.sh DIR -> records: Y(type after symlink) \t y(type) \t size \t mtime \t name  \x1e
cd -- "$1" 2>/dev/null || exit 1
find . -mindepth 1 -maxdepth 1 -printf '%Y\t%y\t%s\t%T@\t%P\036'
