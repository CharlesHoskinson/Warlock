#!/usr/bin/env python3
"""Reviewed, bounded Omarchy presentation trial; invoke only through loop.py native."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import socket
import stat
import subprocess
import sys
import time
import uuid

REPO=Path('/home/charl/Warlock')
sys.path.insert(0,str(REPO/'window-integration-qa'))
from qa_launch import require_qa_scope
SSH='/home/charl/.local/state/warlock-team/20261102-restored/tools/guest-ssh'
QMP='/home/charl/.cache/warlock-omarchy/qmp.sock'
SYSTEMD='env XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus '
BUILD_REPORT=REPO/'.warlock-contributor/haskell-cpu-1793660842333746847/report.json'
FRONTEND_REPORT=REPO/'.warlock-contributor/elm-cpu-1793659009641647454/report.json'
FRONTEND_REPORT_SHA='f6443ca2cbae8e816b3517ca09f3efe0bb56568fe27eae5ef9ecfbc47a17a294'
ASSETS=('helper','guest','owner','backend','controller','bar','popup')
HEX=re.compile(r'[0-9a-f]{64}\Z')
UNIT=re.compile(r'warlock-trial-[0-9a-f]{32}\Z')


def sha(raw): return hashlib.sha256(raw).hexdigest()


def read_regular(path):
    path=Path(path)
    if not path.is_absolute() or '..' in path.parts or str(path)!=str(path.resolve(strict=True)):
        raise ValueError('noncanonical or symlinked input path')
    parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        for part in path.parts[1:-1]:
            nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
            os.close(parent);parent=nxt
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
    finally:
        os.close(parent)
    with os.fdopen(fd,'rb') as f:
        a=os.fstat(f.fileno())
        if not stat.S_ISREG(a.st_mode): raise ValueError('expected regular file')
        body=f.read();b=os.fstat(f.fileno())
    if (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns): raise ValueError('file changed while reading')
    return body


def reviewed_file(item):
    if set(item)!={'path','sha256'} or not Path(item['path']).is_absolute() or not HEX.fullmatch(item['sha256']): raise ValueError('invalid reviewed file reference')
    body=read_regular(item['path'])
    if sha(body)!=item['sha256']: raise ValueError('reviewed file changed')
    return body


def validate_reviewed_inputs(packet,build,frontend,abi,scenario):
    if (set(packet)!={'schema','durationSeconds','applicationAttachment','assets','buildReport','frontendReceipt','abiReceipt','scenarioRecord','participantIndex','requirements','requirement','scenario'} or type(packet['schema']) is not int or packet['schema']!=1 or packet['durationSeconds']!=28 or packet['applicationAttachment'] is not True): raise ValueError('invalid fixed trial packet')
    if packet['requirement']!='ELM-TEA-004' or packet['scenario']!='tea-subscriptions':raise ValueError('unexpected original scenario')
    sl=scenario.get('slice',{})
    if not isinstance(sl,dict) or packet['requirement'] not in sl.get('requirements',[]) or packet['scenario'] not in sl.get('scenarios',[]):raise ValueError('original-scenario record not bound')
    if set(packet['assets'])!=set(ASSETS): raise ValueError('incomplete assets')
    for v in packet['assets'].values():
        if set(v)!={'path','sha256'} or not Path(v['path']).is_absolute() or not HEX.fullmatch(v['sha256']): raise ValueError('invalid asset')
    if packet['buildReport']['path']!=str(BUILD_REPORT) or build.get('passed') is not True or build.get('build',{}).get('profile')!='ui-origin' or build['build'].get('passed') is not True: raise ValueError('source build report not qualified')
    if (type(frontend.get('schema')) is not int or frontend.get('schema')!=1 or frontend.get('passed') is not True or frontend.get('scope')!='protected-subscriptions-html' or not isinstance(frontend.get('sources'),dict) or not frontend['sources'] or not isinstance(frontend.get('documents'),dict)):
        raise ValueError('frontend receipt incomplete')
    if set(frontend['documents'])!={'controller','bar','popup'} or any(frontend['documents'][n]!=packet['assets'][n]['sha256'] for n in ('controller','bar','popup')): raise ValueError('frontend bytes differ')
    required={'schema','disposition','independent','reviewer','buildReportSHA256','ownerSHA256','backendSHA256','guestSystem','guestDSOs','loaderPath','loaderVerified','symbolVersionsVerified','qmpUuid','guestIdentityFile','guestIdentitySHA256','artifactProvenanceReviewed','provenanceEvidence'}
    if (set(abi)!=required or type(abi['schema']) is not int or abi['schema']!=1 or abi['disposition']!='accepted' or abi['independent'] is not True or not isinstance(abi['reviewer'],str) or not abi['reviewer'].strip() or abi['buildReportSHA256']!=packet['buildReport']['sha256'] or abi['ownerSHA256']!=packet['assets']['owner']['sha256'] or abi['backendSHA256']!=packet['assets']['backend']['sha256'] or abi['loaderVerified'] is not True or abi['symbolVersionsVerified'] is not True or not isinstance(abi['guestSystem'],str) or not abi['guestSystem'] or not isinstance(abi['guestDSOs'],dict) or not abi['guestDSOs'] or abi['loaderPath'] not in abi['guestDSOs'] or abi['artifactProvenanceReviewed'] is not True or not re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',abi['qmpUuid']) or not Path(abi['guestIdentityFile']).is_absolute() or not HEX.fullmatch(abi['guestIdentitySHA256'])): raise ValueError('guest ABI qualification missing')
    for path,digest in abi['guestDSOs'].items():
        if not Path(path).is_absolute() or not HEX.fullmatch(digest): raise ValueError('invalid guest dependency pin')


def fixture_inputs(reason):
    d='a'*64; ref={'path':str(BUILD_REPORT),'sha256':d}
    packet={'schema':1,'durationSeconds':28,'applicationAttachment':True,'assets':{n:{'path':'/fixture/'+n,'sha256':d} for n in ASSETS},'buildReport':ref,'frontendReceipt':ref,'abiReceipt':ref,'scenarioRecord':ref,'participantIndex':ref,'requirements':ref,'requirement':'ELM-TEA-004','scenario':'tea-subscriptions'}
    build={'passed':True,'build':{'passed':True,'profile':'ui-origin'}}
    front={'schema':1,'passed':True,'scope':'protected-subscriptions-html','sources':{'x':d},'documents':{n:d for n in ('controller','bar','popup')}}
    abi={'schema':1,'disposition':'accepted','independent':True,'reviewer':'reviewer','buildReportSHA256':d,'ownerSHA256':d,'backendSHA256':d,'guestSystem':'fixture','guestDSOs':{'/fixture/loader':d},'loaderPath':'/fixture/loader','loaderVerified':True,'symbolVersionsVerified':True,'qmpUuid':'12345678-1234-1234-1234-123456789abc','guestIdentityFile':'/fixture/id','guestIdentitySHA256':d,'artifactProvenanceReviewed':True,'provenanceEvidence':ref}
    if reason=='unknown-abi':abi['disposition']='unknown'
    if reason=='source-mismatch':abi['buildReportSHA256']='0'*64
    if reason=='html-mismatch':front['documents']['bar']='0'*64
    if reason=='wrong-deadline':packet['durationSeconds']=29
    if reason=='wrong-attachment':packet['applicationAttachment']=False
    scenario={'slice':{'requirements':['ELM-TEA-004'],'scenarios':['tea-subscriptions']}}
    return packet,build,front,abi,scenario


def proc_birth(raw):
    end=raw.rfind(')')
    if end<0: raise ValueError('invalid proc stat')
    fields=raw[end+2:].split()
    if len(fields)<20: raise ValueError('short proc stat')
    return fields[19]


def census_status(rows):
    if rows is None or any(row.get('startTicks') is None for row in rows): return 'unknown'
    return 'observed'



def validate_pre_capture(ready,identity,live,guest):
    if ready.get('invocation')!=identity['InvocationID'] or ready.get('cgroup')!=identity['ControlGroup'] or not ready.get('mappedOwnerPids') or ready.get('observedMonotonicNs',0)>=ready.get('deadlineMonotonicNs',0):raise RuntimeError('mapped owner observation is invalid')
    rows=live.get('rows');by_pid={row['pid']:row for row in (rows or [])};ready_births={row['pid']:row['startTicks'] for row in ready['actors']}
    if census_status(rows)!='observed' or sum(row.get('exe')==guest+'/owner' for row in rows)<2 or not any(row.get('exe')==guest+'/backend' for row in rows) or any(pid not in by_pid or by_pid[pid]['startTicks']!=ready_births.get(pid) for pid in ready['mappedOwnerPids']):raise RuntimeError('live mapped owner/backend census unavailable')
    return ready_births


def validate_post_capture(ready,ready_births,after,guest_now):
    rows=after.get('rows');by_pid={row['pid']:row for row in (rows or [])}
    if guest_now>=ready['deadlineMonotonicNs'] or census_status(rows)!='observed' or any(pid not in by_pid or by_pid[pid]['startTicks']!=ready_births.get(pid) for pid in ready['mappedOwnerPids']):
        raise RuntimeError('screenshot completion after deadline or owner birth changed')


def recover_service_identity(unit,identity,launch_attempted,show):
    if identity is not None:return identity
    if not launch_attempted:return None
    candidate=show(unit);require_same_service(candidate,candidate,unit)
    return candidate

def retirement_state(pids,populated):
    if pids is None or populated is None: return 'unknown'
    return 'observed-empty' if not pids and not populated else 'not-retired'


def require_same_service(expected,current,unit):
    if not UNIT.fullmatch(unit): raise ValueError('invalid owned service name')
    if set(expected)!={'InvocationID','ControlGroup'} or current.get('InvocationID')!=expected['InvocationID'] or current.get('ControlGroup')!=expected['ControlGroup'] or not re.fullmatch('[0-9a-f]{32}',expected['InvocationID']) or not expected['ControlGroup'].startswith('/user.slice/') or not expected['ControlGroup'].endswith('/'+unit+'.service'): raise ValueError('owned service identity changed or missing')


def stop_owned(unit,expected,show,stop):
    require_same_service(expected,show(unit),unit);stop(unit)


def ssh(command,data=None,timeout=15,check=True):
    return subprocess.run([SSH,command],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,check=check)


def show_service(unit):
    text=ssh(SYSTEMD+'systemctl --user show '+shlex.quote(unit+'.service')+' --property=InvocationID --property=ControlGroup').stdout.decode()
    return dict(line.split('=',1) for line in text.splitlines() if '=' in line)


def stop_service(unit): ssh(SYSTEMD+'systemctl --user stop '+shlex.quote(unit+'.service'),timeout=10)


def show_service_status(unit):
    command=(SYSTEMD+'systemctl --user show --all '+shlex.quote(unit+'.service')+
             ' --property=InvocationID --property=ControlGroup --property=ActiveState --property=SubState'
             ' --property=MainPID --property=Result --property=ExecMainCode --property=ExecMainStatus')
    output=ssh(command,timeout=4).stdout.decode()
    return dict(line.split('=',1) for line in output.splitlines() if '=' in line)


def matching_terminal(unit,identity,status):
    # Validates the saved identity, not the current cgroup. A returned status
    # is evidence only; it never grants permission to stop the unit.
    require_same_service(identity,identity,unit)
    if status.get('InvocationID')!=identity['InvocationID']:
        return None
    group=status.get('ControlGroup','')
    if group and group!=identity['ControlGroup']:
        return None
    state,status_detail=status.get('ActiveState'),status.get('SubState')
    if not ((state=='active' and status_detail=='exited') or (state=='inactive' and status_detail=='dead') or (state=='failed' and status_detail=='failed')):
        return None
    if (status.get('MainPID')!='0' or not status.get('Result')
            or not re.fullmatch(r'[0-9]+',status.get('ExecMainCode',''))
            or not re.fullmatch(r'[0-9]+',status.get('ExecMainStatus',''))):
        return None
    return status


def cleanup_owned_service(result,unit,identity,show_status,show_identity,stop,observe):
    current=show_status(unit)
    terminal=matching_terminal(unit,identity,current)
    if terminal is not None:
        result['terminalService']=terminal
        result['terminalObservedHostMonotonicNs']=time.monotonic_ns()
    # The exact original live identity and group gate is not weakened. If the
    # group vanished, this raises and retirement remains UNKNOWN.
    require_same_service(identity,current,unit)
    result['beforeStopCensus']=observe(identity['ControlGroup'])
    stop_owned(unit,identity,show_identity,stop)
    result['stopRequested']=True
    after=observe(identity['ControlGroup']);result['afterStopCensus']=after
    result['scopeRetirement']=retirement_state(after['rows'],None if after['populated'] is None else after['populated']!='0')


def invocation_journal(unit,identity):
    require_same_service(identity,identity,unit)
    command=(SYSTEMD+'journalctl --user --no-pager --output=json --lines=200 --user-unit='
             +shlex.quote(unit+'.service')+' --invocation='+shlex.quote(identity['InvocationID']))
    return ssh(command,timeout=4).stdout


def qmp_screenshot(destination,expected_uuid):
    if destination.exists() or destination.is_symlink(): raise ValueError('capture exists')
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as sock:
        sock.settimeout(3);sock.connect(QMP);stream=sock.makefile('rwb',buffering=0);json.loads(stream.readline())
        def command(packet):
            stream.write(json.dumps(packet).encode()+b'\n')
            while True:
                result=json.loads(stream.readline())
                if 'error' in result:raise RuntimeError('QMP command refused')
                if 'return' in result:return result['return']
        command({'execute':'qmp_capabilities'})
        actual=command({'execute':'query-uuid'})
        if str(actual.get('UUID','')).lower()!=expected_uuid.lower():raise RuntimeError('QMP VM identity differs from reviewed guest')
        status=command({'execute':'query-status'})
        if status.get('running') is not True:raise RuntimeError('QMP guest is not running')
        command({'execute':'screendump','arguments':{'filename':str(destination),'format':'png'}})
    raw=read_regular(destination)
    if len(raw)<24 or not raw.startswith(b'\x89PNG\r\n\x1a\n'):raise RuntimeError('QMP output is not a PNG')
    return {'sha256':sha(raw),'bytes':len(raw),'qmpUuid':expected_uuid,'hostMonotonicNs':time.monotonic_ns()}


UPLOAD='''import os,sys,hashlib,json\nm=json.loads(sys.stdin.buffer.readline()); data=sys.stdin.buffer.read()\nif hashlib.sha256(data).hexdigest()!=m["sha256"]: raise SystemExit("hash")\nif not m["name"].isidentifier(): raise SystemExit("name")\nd=os.open(m["dir"],os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW); f=os.open(m["name"],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o700 if m["name"] in ("owner","backend") else 0o600,dir_fd=d)\nwith os.fdopen(f,"wb") as out:out.write(data);out.flush();os.fsync(out.fileno())\nos.close(d)\n'''


def upload(directory,name,body):
    header=json.dumps({'dir':directory,'name':name,'sha256':sha(body)}).encode()+b'\n'
    ssh('python3 -B -c '+shlex.quote(UPLOAD),header+body,timeout=60)


CGROUP_OBSERVE = r'''import json,os,pathlib,sys
p=pathlib.Path('/sys/fs/cgroup')/sys.argv[1].lstrip('/')
try:
 rows=[]
 for f in p.rglob('cgroup.procs'):
  for x in f.read_text().split():
   pid=int(x)
   try:
    text=pathlib.Path('/proc',str(pid),'stat').read_text();start=text[text.rfind(')')+2:].split()[19]
   except (OSError,IndexError):start=None
   try:executable=os.readlink('/proc/'+str(pid)+'/exe')
   except OSError:executable=None
   rows.append({'pid':pid,'startTicks':start,'cgroup':str(f.parent),'exe':executable})
 ev=dict(line.split() for line in (p/'cgroup.events').read_text().splitlines())
 print(json.dumps({'rows':rows,'populated':ev.get('populated')}))
except (OSError,ValueError):print(json.dumps({'rows':None,'populated':None}))
'''


def observe_guest_cgroup(group):
    if not group.startswith('/user.slice/') or '..' in Path(group).parts:raise ValueError('invalid owned cgroup')
    return json.loads(ssh('python3 -B -c '+shlex.quote(CGROUP_OBSERVE)+' '+shlex.quote(group),timeout=5).stdout)

PRESERVATION_PROBE = 'import json, os, subprocess, time\nfrom pathlib import Path\n\ndef run(args,env):\n    p=subprocess.run(args,env=env,capture_output=True,text=True,timeout=4,check=False)\n    return {"exit":p.returncode,"stdout":p.stdout,"stderr":p.stderr}\ndef birth(pid):\n    raw=Path("/proc",str(pid),"stat").read_text()\n    return raw[raw.rfind(")")+2:].split()[19]\ndef session(env):\n    r=run(["hyprctl","instances","-j"],env)\n    if r["exit"]: raise ValueError("instances failed")\n    xs=[x for x in json.loads(r["stdout"]) if x.get("wl_socket")=="wayland-1"]\n    if len(xs)!=1 or not isinstance(xs[0].get("instance"),str) or not xs[0]["instance"] or type(xs[0].get("pid")) is not int or xs[0]["pid"]<=0: raise ValueError("ambiguous session")\n    return {"instance":xs[0]["instance"],"pid":xs[0]["pid"],"birth":birth(xs[0]["pid"])}\nenv={k:v for k,v in os.environ.items() if not k.startswith("LD_") and k!="GLIBC_TUNABLES"}\nenv.update(XDG_RUNTIME_DIR="/run/user/1000", WAYLAND_DISPLAY="wayland-1", OMARCHY_PATH="/usr/share/omarchy", LANG="C.UTF-8", LC_ALL="C.UTF-8")\nout={"startMonotonicNs":time.monotonic_ns(),"valid":False}\ntry:\n    boot=Path("/proc/sys/kernel/random/boot_id").read_text().strip()\n    if not boot: raise ValueError("missing boot")\n    first=session(env);env["HYPRLAND_INSTANCE_SIGNATURE"]=first["instance"]\n    clients=run(["hyprctl","clients","-j"],env);idle=run(["omarchy-shell","idle","status"],env);lock=run(["omarchy-shell","lock","isLocked"],env)\n    out.update(rawClients=clients,rawIdle=idle,rawLock=lock)\n    if clients["exit"] or idle["exit"] or lock["exit"]: raise ValueError("desktop query failed")\n    windows=json.loads(clients["stdout"]);state=json.loads(idle["stdout"]);locked=json.loads(lock["stdout"])\n    if not isinstance(windows,list) or not isinstance(state,dict) or any(type(state.get(k)) is not bool for k in ("enabled","stayAwake")) or type(locked) is not bool: raise ValueError("malformed desktop status")\n    foot=[]\n    for row in windows:\n        if not isinstance(row,dict):raise ValueError("malformed client")\n        if str(row.get("class","")).casefold()!="foot":continue\n        pid=row.get("pid");address=row.get("address")\n        if type(pid) is not int or pid<=0 or not isinstance(address,str) or not address:raise ValueError("invalid foot identity")\n        foot.append({"address":address,"pid":pid,"birth":birth(pid)})\n    foot.sort(key=lambda x:(x["address"],x["pid"],x["birth"]))\n    if len({x["address"] for x in foot})!=len(foot):raise ValueError("duplicate foot address")\n    if session(env)!=first or Path("/proc/sys/kernel/random/boot_id").read_text().strip()!=boot or any(birth(x["pid"])!=x["birth"] for x in foot):raise ValueError("identity changed during snapshot")\n    out.update(valid=True,boot=boot,session=first,foot=foot,idle={"enabled":state["enabled"],"stayAwake":state["stayAwake"],"locked":locked})\nexcept Exception as exc:out["error"]=type(exc).__name__+": "+str(exc)\nout["endMonotonicNs"]=time.monotonic_ns()\nprint(json.dumps(out))\n'


def preservation_snapshot(out, label):
    try:
        raw=ssh('python3 -B -c '+shlex.quote(PRESERVATION_PROBE),timeout=25).stdout
        if len(raw)>4*1024*1024:raise ValueError('desktop snapshot too large')
        snapshot=json.loads(raw)
        if not isinstance(snapshot,dict):raise ValueError('invalid desktop snapshot')
        (out/('preservation-'+label+'.json')).write_bytes(raw)
        return snapshot
    except Exception as exc:
        return {'valid':False,'error':type(exc).__name__+': '+str(exc)}


def compare_preservation(before,after):
    unknown={'foot':'unknown','idle':'unknown'}
    if not isinstance(before,dict) or not isinstance(after,dict) or before.get('valid') is not True or after.get('valid') is not True:return unknown
    session=before.get('session')
    if not isinstance(before.get('boot'),str) or not before['boot'] or before.get('boot')!=after.get('boot') or not isinstance(session,dict) or not isinstance(session.get('instance'),str) or not session['instance'] or type(session.get('pid')) is not int or session['pid']<=0 or not isinstance(session.get('birth'),str) or not session['birth'].isdigit() or session!=after.get('session'):return unknown
    if any(type(x.get(k)) is not int for x in (before,after) for k in ('startMonotonicNs','endMonotonicNs')):return unknown
    if any(x['startMonotonicNs']>x['endMonotonicNs'] for x in (before,after)) or before['endMonotonicNs']>=after['startMonotonicNs']:return unknown
    a,b=before.get('foot'),after.get('foot');i,j=before.get('idle'),after.get('idle')
    if not isinstance(a,list) or not isinstance(b,list) or not isinstance(i,dict) or not isinstance(j,dict):return unknown
    if any(type(x.get(k)) is not bool for x in (i,j) for k in ('enabled','stayAwake','locked')):return unknown
    if any(not isinstance(x,dict) or not isinstance(x.get('address'),str) or not x['address'] or type(x.get('pid')) is not int or x['pid']<=0 or not isinstance(x.get('birth'),str) or not x['birth'].isdigit() for x in a+b):return unknown
    if any(len({row['address'] for row in rows})!=len(rows) for rows in (a,b)):return unknown
    return {'foot':('not-present-at-baseline' if not a else ('preserved' if a==b else 'changed')), 'idle':('preserved' if all(i[k]==j[k] for k in ('enabled','stayAwake','locked')) else 'changed')}


def main(argv=None):
    require_qa_scope()
    ap=argparse.ArgumentParser();ap.add_argument('--packet',required=True);ap.add_argument('--sha256',required=True);ap.add_argument('--output',required=True);args=ap.parse_args(argv)
    raw=read_regular(args.packet)
    if not HEX.fullmatch(args.sha256) or sha(raw)!=args.sha256: raise ValueError('reviewed trial packet changed')
    packet=json.loads(raw);build=json.loads(reviewed_file(packet['buildReport']));frontend=json.loads(reviewed_file(packet['frontendReceipt']));abi=json.loads(reviewed_file(packet['abiReceipt']))
    scenario=json.loads(reviewed_file(packet['scenarioRecord']))
    validate_reviewed_inputs(packet,build,frontend,abi,scenario)
    index_ref=packet['participantIndex']
    if index_ref['path']!=str(REPO/'.warlock-contributor/participant-index.json'):raise ValueError('unexpected participant index')
    index=json.loads(reviewed_file(index_ref))
    index_payload={'schema':1,'records':dict(sorted(index['records'].items()))}
    if 'bootstrapClassifications' in index:index_payload['bootstrapClassifications']=index['bootstrapClassifications']
    if sha(json.dumps(index_payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())!=index.get('indexSha256'):raise ValueError('participant index corrupt')
    scenario_path=Path(packet['scenarioRecord']['path'])
    if not scenario_path.is_relative_to(REPO):raise ValueError('scenario record outside repository')
    entry=index['records'].get(str(scenario_path.relative_to(REPO)))
    if not isinstance(entry,dict) or entry.get('recordSha256')!=packet['scenarioRecord']['sha256']:raise ValueError('scenario record not indexed by exact bytes')
    identity={'owner':scenario.get('owner'),'baseline':scenario.get('baseline'),'startedUTC':scenario.get('startedUTC'),'requirements':scenario['slice']['requirements'],'scenarios':scenario['slice']['scenarios']}
    if sha(json.dumps(identity,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())!=entry.get('identitySha256'):raise ValueError('scenario record identity differs')
    if packet['requirements']['path']!=str(REPO/'docs/elm-roadmap/requirements.json'):raise ValueError('unexpected requirement register')
    requirements=json.loads(reviewed_file(packet['requirements']))['requirements']
    matches=[x for x in requirements if x.get('id')==packet['requirement']]
    if len(matches)!=1 or sum(x.get('name')==packet['scenario'] for x in matches[0].get('scenarios',[]))!=1:raise ValueError('original requirement/scenario pair missing')
    for entry in packet['assets'].values(): reviewed_file(entry)
    if frontend['report']!={'path':str(FRONTEND_REPORT),'sha256':FRONTEND_REPORT_SHA}:raise ValueError('unexpected protected subscriptions report')
    frontend_report=json.loads(reviewed_file(frontend['report']))
    subs=frontend_report.get('subscriptions',{})
    if (frontend_report.get('passed') is not True or subs.get('passed') is not True or subs.get('requirement')!='ELM-TEA-004' or subs.get('scenario')!='tea-subscriptions' or subs.get('marker')!='TEA_SUBSCRIPTIONS_OBSERVE_V1'):
        raise ValueError('protected subscriptions report did not pass the exact mode')
    observer=frontend_report.get('httpRootObserver',{})
    if observer.get('result',{}).get('ok') is not True or len(frontend_report.get('compiledSubscriptionRoots',[]))!=8:raise ValueError('HTTP root observer incomplete')
    if sha(read_regular(FRONTEND_REPORT.parent/observer['resultPath']))!=observer.get('resultSHA256'):raise ValueError('HTTP root observer bytes changed')
    provenance=json.loads(reviewed_file(abi['provenanceEvidence']))
    if (provenance.get('schema')!=1 or provenance.get('independent') is not True or provenance.get('disposition')!='accepted' or provenance.get('buildReportSHA256')!=packet['buildReport']['sha256'] or provenance.get('ownerSHA256')!=packet['assets']['owner']['sha256'] or provenance.get('backendSHA256')!=packet['assets']['backend']['sha256'] or provenance.get('ownerPath')!=packet['assets']['owner']['path'] or provenance.get('backendPath')!=packet['assets']['backend']['path'] or provenance.get('sourceHashesVerified') is not True or not isinstance(provenance.get('reviewer'),str) or not provenance['reviewer'].strip()):raise ValueError('production binary provenance not independently reviewed')
    docs=frontend_report.get('httpDocuments',{})
    if any(docs.get(n,{}).get('sha256')!=frontend['documents'][n] for n in ('controller','bar','popup')):raise ValueError('HTML differs from protected subscriptions report')
    report_sources={k:v for k,v in frontend_report.get('sources',{}).items() if k.startswith('implementation/warlock/src/') and k.endswith('.elm')}
    if report_sources!=frontend['sources']:raise ValueError('Elm closure differs from subscriptions report')
    if sha(read_regular(REPO/'implementation/warlock/elm.json'))!=frontend_report.get('sources',{}).get('implementation/warlock/elm.json'):raise ValueError('Elm configuration changed')
    production=(BUILD_REPORT.parent/'haskell-build/dist-production').resolve(strict=True)
    for name,basename in (('owner','warlock-ui-owner'),('backend','warlock-ui-backend')):
        binary=Path(packet['assets'][name]['path'])
        if binary.name!=basename or not binary.resolve(strict=True).is_relative_to(production):raise ValueError('binary outside protected production build')
    # Compare actual complete Haskell tree against the protected build inventory.
    src=REPO/'implementation/warlock/haskell';expected=build['build']['sourceHashes'];observed={}
    for f in sorted(src.rglob('*')):
        if any(x in ('dist','dist-newstyle','.stack-work') for x in f.relative_to(src).parts):continue
        if f.is_symlink():raise ValueError('symlink in Haskell source')
        if f.is_file():observed[str(f.relative_to(src))]=sha(read_regular(f))
    if observed!=expected:raise ValueError('current Haskell source differs from protected build')
    elm=REPO/'implementation/warlock/src';current={str(p.relative_to(REPO)):sha(read_regular(p)) for p in sorted(elm.rglob('*.elm')) if p.is_file()}
    if current!=frontend['sources']:raise ValueError('current Elm source differs from reviewed frontend')
    if Path(packet['assets']['helper']['path'])!=REPO/'tools/omarchy_ui_mvp.py':raise ValueError('unexpected helper source')
    out=Path(args.output)
    if not out.is_absolute():raise ValueError('absolute private output required')
    out.mkdir(mode=0o700,parents=False,exist_ok=False)
    (out/'reviewed-packet.json').write_bytes(raw)
    runid=uuid.uuid4().hex;unit='warlock-trial-'+runid;guest='/tmp/'+unit;identity=None;launch_attempted=False;result={'unit':unit,'guestDir':guest,'scopeRetirement':'unknown','retiredBirths':'unknown','applicationAttachment':'presentation-only','nativeAccepted':False,'originalAccepted':False,'releaseAccepted':False}
    before=preservation_snapshot(out,'before')
    try:
        state=ssh(SYSTEMD+'systemctl --user show '+shlex.quote(unit+'.service')+' --property=LoadState',check=False).stdout.decode().strip()
        if state!='LoadState=not-found':raise RuntimeError('unique guest unit already exists or state unknown')
        ssh('mkdir -m 700 -- '+shlex.quote(guest))
        for n in ASSETS:upload(guest,n,reviewed_file(packet['assets'][n]))
        guest_packet={'unit':unit,'dir':guest,'assets':{n:packet['assets'][n]['sha256'] for n in ASSETS},'abiReview':abi}
        upload(guest,'packet',json.dumps(guest_packet).encode())
        cmd=SYSTEMD+'systemd-run --user --remain-after-exit --unit='+unit+' --property=Type=exec --property=KillMode=control-group --property=RuntimeMaxSec=60s -- python3 -B '+shlex.quote(guest+'/guest')+' '+shlex.quote(guest+'/packet')
        launch_attempted=True
        ssh(cmd)
        identity=show_service(unit);require_same_service(identity,identity,unit);result['serviceIdentity']=identity
        upload(guest,'gate',json.dumps(identity).encode())
        # A guest marker is written only after preflight and a live actor census.
        terminal_seen=False
        for _ in range(100):
            status=show_service_status(unit)
            terminal=matching_terminal(unit,identity,status)
            if terminal is not None:
                result['terminalService']=terminal
                result['terminalObservedHostMonotonicNs']=time.monotonic_ns()
                result['error']='bound service completed before readiness'
                terminal_seen=True
                break
            require_same_service(identity,status,unit)
            probe=ssh('test -f '+shlex.quote(guest+'/ready'),check=False,timeout=3)
            if probe.returncode==0:
                ready=json.loads(ssh('cat -- '+shlex.quote(guest+'/ready'),timeout=3).stdout)
                require_same_service(identity,show_service(unit),unit)
                clients_raw=ssh('cat -- '+shlex.quote(guest+'/clients-live.json'),timeout=3).stdout
                if sha(clients_raw)!=ready.get('clientsSHA256'):raise RuntimeError('mapped client inventory changed')
                clients=json.loads(clients_raw)
                for surface in ready.get('mappedOwnerSurfaces',[]):
                    if not any(c.get('mapped') is True and all(c.get(k)==surface.get(k) for k in ('pid','address','at','size')) for c in clients):raise RuntimeError('mapped surface differs from client inventory')
                if not ready.get('mappedOwnerSurfaces') or set(x['pid'] for x in ready['mappedOwnerSurfaces'])!=set(ready.get('mappedOwnerPids',[])):raise RuntimeError('mapped surface identity missing')
                live=observe_guest_cgroup(identity['ControlGroup']);result['beforeScreenshotCensus']=live;result['guestReady']=ready
                ready_births=validate_pre_capture(ready,identity,live,guest)
                result['screenshotQualification']='unqualified desktop frame'
                result['screenshot']=qmp_screenshot(out/'live.png',abi['qmpUuid'])
                require_same_service(identity,show_service(unit),unit)
                guest_now=int(ssh('python3 -B -c '+shlex.quote('import time; print(time.monotonic_ns())'),timeout=3).stdout)
                after=observe_guest_cgroup(identity['ControlGroup']);result['afterScreenshotCensus']=after;result['guestAfterScreenshotMonotonicNs']=guest_now
                validate_post_capture(ready,ready_births,after,guest_now)
                result['screenshotQualification']='unqualified desktop frame; mapped owner observed before capture'
                break
            time.sleep(.1)
        else:result['error']='live census marker unavailable'
        # A retained successful service is active/exited, not inactive.
        # Report it promptly; this does not alter the guest's 28-second deadline.
        if not terminal_seen:
            for _ in range(320):
                status=show_service_status(unit)
                terminal=matching_terminal(unit,identity,status)
                if terminal is not None:
                    result['terminalService']=terminal
                    result['terminalObservedHostMonotonicNs']=time.monotonic_ns()
                    break
                require_same_service(identity,status,unit)
                time.sleep(.1)
    except Exception as exc:
        result['error']=str(exc)
    finally:
        if identity is None and launch_attempted:
            try:
                identity=recover_service_identity(unit,identity,launch_attempted,show_service);result['serviceIdentity']=identity
            except Exception as exc:result['cleanupError']='identity unavailable: '+str(exc)
        if identity is not None:
            try:
                cleanup_owned_service(result,unit,identity,show_service_status,show_service,stop_service,observe_guest_cgroup)
            except Exception as exc:result['cleanupError']=str(exc)
            try:
                journal=invocation_journal(unit,identity)
                (out/'guest-invocation-journal.jsonl').write_bytes(journal[:1048576])
            except Exception as exc:result['invocationJournalError']=str(exc)
        try:
            journal=ssh(SYSTEMD+'journalctl --user --unit='+shlex.quote(unit+'.service')+' --no-pager --lines=200',timeout=4).stdout
            (out/'guest-service-journal.txt').write_bytes(journal[:1048576])
        except Exception:pass
        for name in ('receipt.json','process-samples.json','clients-before.json','clients-live.json','clients-after.json','observation.json','backend.stdout','backend.stderr','ready'):
            try:
                data=ssh('cat -- '+shlex.quote(guest+'/'+name),timeout=4).stdout
                if len(data)<=8*1024*1024:(out/('guest-'+name)).write_bytes(data)
            except Exception:pass
        try:
            receipt_bytes=read_regular(out/'guest-receipt.json')
            receipt=json.loads(receipt_bytes)
            if not isinstance(receipt,dict) or type(receipt.get('backendExitCode')) is not int:
                raise ValueError('missing or invalid backend exit')
            result['backendReceiptSHA256']=sha(receipt_bytes)
            result['backendExitCode']=receipt['backendExitCode']
            result['backendDiagnostic']=receipt.get('backendDiagnostic')
        except (OSError,ValueError,TypeError) as exc:result['backendReceiptError']=str(exc)
        try:
            if sha(read_regular(args.packet))!=args.sha256:raise ValueError('post-run trial packet changed')
            for item in list(packet['assets'].values())+[packet['buildReport'],packet['frontendReceipt'],packet['abiReceipt'],packet['scenarioRecord'],packet['participantIndex'],packet['requirements'],abi['provenanceEvidence'],frontend['report']]:reviewed_file(item)
            post_haskell={}
            for f in sorted(src.rglob('*')):
                if any(x in ('dist','dist-newstyle','.stack-work') for x in f.relative_to(src).parts):continue
                if f.is_symlink():raise ValueError('post-run Haskell symlink')
                if f.is_file():post_haskell[str(f.relative_to(src))]=sha(read_regular(f))
            post_elm={str(f.relative_to(REPO)):sha(read_regular(f)) for f in sorted(elm.rglob('*.elm')) if f.is_file()}
            if post_haskell!=expected or post_elm!=frontend['sources']:raise ValueError('post-run source inventory changed')
            result['postInputCheck']='matched'
        except Exception as exc:result['postInputCheck']='failed: '+str(exc)
        after=preservation_snapshot(out,'after')
        result['desktopPreservation']=compare_preservation(before,after)
        result['desktopPreservationSnapshots']={'before':before,'after':after}
        (out/'observation.json').write_text(json.dumps(result,indent=2)+'\n')
    # Retired births/cgroup can vanish; this trial never claims confirmed cleanup.
    return 1

if __name__=='__main__':raise SystemExit(main())
