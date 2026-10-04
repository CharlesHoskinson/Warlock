"""Parent native fake-seat injection and full-journal interval checks."""
import hashlib,json,math,os,socket,struct,subprocess,time
from pathlib import Path

class Refused(ValueError):pass

def deadline_guard(deadline):
    remaining=deadline-time.monotonic()
    if remaining<=0:raise Refused('Original six-second pointer deadline')
    return remaining

def complete_pair(events,baseline,*,pid,button,expected,oracle):
    # No selection by PID/button/desired state: ALL button records are handed to decoder.
    interval=[row for row in events if row.get('sequence',0)>baseline and row.get('event')=='pointer-button']
    return oracle.validate_pair(interval,pid=pid,after_sequence=baseline,button=button,expected_local=expected)

def cursor_point(value,expected,oracle):
    if type(value) is not dict or set(value)!= {'x','y'}:raise Refused('Actual compositor cursor shape')
    actual=[oracle.fixed(value[k]) for k in ('x','y')]
    if actual!=[oracle.fixed(v) for v in expected]:raise Refused('Independent child-global cursor mismatch')
    return actual

def verify_peer(session,host,parent,identity,deadline):
    session.guard();remaining=deadline_guard(deadline)
    path=session.host.runtime/'weston-host'
    if host.original.socket_identity(path,session.host.runtime)!=identity or not host.original.same_process(parent):raise Refused('Parent identity replaced')
    with socket.socket(socket.AF_UNIX) as probe:
        probe.settimeout(min(2,remaining));probe.connect(str(path))
        pid,uid,gid=struct.unpack('3i',probe.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
    if pid!=parent['pid'] or uid!=os.getuid():raise Refused('Foreign parent peer')
    if host.original.socket_identity(path,session.host.runtime)!=identity or not host.original.same_process(parent):raise Refused('Parent peer replaced after probe')
    deadline_guard(deadline)
    return {'pid':pid,'uid':uid,'gid':gid,'socket':str(path),'identity':identity,'process':parent}

def send(session,host,parent,identity,client,commands,deadline):
    peer=verify_peer(session,host,parent,identity,deadline)
    result=subprocess.run([str(client)],input='\n'.join([*commands,'quit','']),text=True,capture_output=True,
        env=dict(session.host.env,ELM_PARENT_INPUT_QA='1'),cwd=session.host.runtime,timeout=min(3,deadline_guard(deadline)))
    deadline_guard(deadline)
    if len(result.stdout)>4096 or len(result.stderr)>4096:raise Refused('Parent receipt bound')
    receipts=[json.loads(line) for line in result.stdout.splitlines()]
    if result.returncode!=0 or len(receipts)!=1+len(commands) or receipts[0]!={'ready':True,'scope':'parent-notify-only'}:raise Refused('Parent normal exit/receipt count')
    for sequence,row in enumerate(receipts[1:],1):
        if row!={'sequence':sequence,'accepted':True,'scope':'parent-notify-only'}:raise Refused('Parent exact ordered admission')
    verify_peer(session,host,parent,identity,deadline)
    return {'commands':commands,'exitCode':result.returncode,'receipts':receipts,'peer':peer,'physicalHardwareAccepted':False}
