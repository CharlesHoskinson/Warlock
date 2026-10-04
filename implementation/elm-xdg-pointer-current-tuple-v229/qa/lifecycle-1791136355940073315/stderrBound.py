#!/usr/bin/python3
import sys,json,time
commands=[line.strip() for line in sys.stdin if line.strip()!="quit"]
sys.stderr.write("x"*5000);print(json.dumps({"ready":True,"scope":"parent-notify-only"}),flush=True)
for i,c in enumerate(commands,1):print(json.dumps({"sequence":i,"accepted":True,"scope":"parent-notify-only"}),flush=True)
