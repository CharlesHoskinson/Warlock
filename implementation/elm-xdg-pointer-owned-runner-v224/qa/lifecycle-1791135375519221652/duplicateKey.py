#!/usr/bin/python3
import sys,json,time
commands=[line.strip() for line in sys.stdin if line.strip()!="quit"]
print('{"ready":false,"ready":true,"scope":"parent-notify-only"}',flush=True)
