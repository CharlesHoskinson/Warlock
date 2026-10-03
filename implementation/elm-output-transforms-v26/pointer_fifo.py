"""Owned private pointer helper with controllable lifetime and stdin."""
import os
import sys
fifo, binary = sys.argv[1:]
fd = os.open(fifo, os.O_RDONLY)
os.dup2(fd, 0)
os.close(fd)
os.execv(binary, [binary, '800', '600'])
