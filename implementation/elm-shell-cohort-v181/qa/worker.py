"""Controlled escaping-session worker; no GUI or system mutation."""
import json,os,resource,signal,sys,time
from pathlib import Path
mode,output=sys.argv[1:];output=Path(output)
def identity():
 raw=Path('/proc/self/stat').read_text();fields=raw[raw.rindex(')')+2:].split()
 return {'pid':os.getpid(),'start':fields[19],'pgid':os.getpgrp(),'cgroup':Path('/proc/self/cgroup').read_text(),'core':list(resource.getrlimit(resource.RLIMIT_CORE))}
if mode=='peer':
 output.write_text(json.dumps(identity()))
 signal.signal(signal.SIGTERM,lambda *_:sys.exit(0))
 while True:time.sleep(.05)
assert mode=='cohort'
helper=os.fork()
if helper==0:
 os.setsid();signal.signal(signal.SIGTERM,signal.SIG_IGN)
 output.with_suffix('.helper.json').write_text(json.dumps(identity()))
 while True:time.sleep(.05)
signal.signal(signal.SIGTERM,signal.SIG_IGN)
output.write_text(json.dumps({**identity(),'helper':helper}))
while True:time.sleep(.05)
