#!/usr/bin/python3
import sys,json,time
commands=[line.strip() for line in sys.stdin if line.strip()!="quit"]
sys.stdout.write('{"ready":true');sys.stdout.flush()
