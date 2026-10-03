#!/usr/bin/python3
from pathlib import Path
import os,sys,json,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v10')
import helper_observer as observer
from qa_launch import require_qa_scope
require_qa_scope()
log,ready,gate,source=sys.argv[1:]
wrapper=observer.process(os.getpid())
child=os.fork()
if child==0:
    os.execv('/usr/bin/python3',['/usr/bin/python3','-B',source,'delegate',gate])
delegate=observer.process(child)
row=dict(operation='hydrate',args=['hydrate'],helper='snap',wrapper=wrapper,delegate=delegate,serviceOperation=None,queryRoot=None,**{'class':'compositor'})
with observer.locked_log(log) as stream:observer.append(stream,dict(row,event='started',timeNs=time.time_ns(),fixtureOnly=True,compositorAuthorityClaimed=False))
fd=os.open(ready,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
os.write(fd,json.dumps(row).encode());os.close(fd)
_,status=os.waitpid(child,0)
code=os.waitstatus_to_exitcode(status)
with observer.locked_log(log) as stream:observer.append(stream,dict(row,event='terminal',exitCode=code,timeNs=time.time_ns(),fixtureOnly=True,compositorAuthorityClaimed=False))
sys.exit(code)
