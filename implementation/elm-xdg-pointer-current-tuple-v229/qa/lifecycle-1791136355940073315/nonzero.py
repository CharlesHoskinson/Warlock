#!/usr/bin/python3
import sys,json,time
commands=[line.strip() for line in sys.stdin if line.strip()!="quit"]
print("partial-before-exit",flush=True);sys.stderr.write("owned failure\n");sys.exit(6)
