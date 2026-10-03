"""Owned nongraphical wrapper/delegate fixture; no compositor authority claim."""
from pathlib import Path
import os,sys,json
import helper_observer as observer
from qa_launch import require_qa_scope
require_qa_scope()
if sys.argv[1]=='delegate':
    fd=os.open(sys.argv[2],os.O_RDONLY);value=os.read(fd,1);os.close(fd)
    sys.exit(int(sys.argv[3]) if value==b'1' else 125)
log,ready,gate,code=sys.argv[2:]
wrapper=observer.process(os.getpid());child=os.fork()
if child==0:os.execv('/usr/bin/python3',['/usr/bin/python3','-B',__file__,'delegate',gate,code])
delegate=observer.process(child)
row=dict(operation='hydrate',args=['hydrate'],helper='snap',wrapper=wrapper,delegate=delegate,serviceOperation=None,queryRoot=None,**{'class':'compositor'})
with observer.locked_log(log) as stream:observer.append(stream,dict(row,event='started',timeNs=__import__('time').time_ns(),fixtureOnly=True,compositorAuthorityClaimed=False))
fd=os.open(ready,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,json.dumps(row).encode());os.close(fd)
_,status=os.waitpid(child,0);result=os.waitstatus_to_exitcode(status)
with observer.locked_log(log) as stream:observer.append(stream,dict(row,event='terminal',exitCode=result,timeNs=__import__('time').time_ns(),fixtureOnly=True,compositorAuthorityClaimed=False))
sys.exit(result)
