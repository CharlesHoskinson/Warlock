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

def strict_json(line):
    def pairs(rows):
        result={}
        for key,value in rows:
            if key in result:raise Refused('Duplicate receipt JSON key')
            result[key]=value
        return result
    def constant(value):raise Refused('Nonfinite receipt JSON')
    return json.loads(line,object_pairs_hook=pairs,parse_constant=constant)

def receipts(raw,count):
    commands=count if type(count) is list else None
    count=len(commands) if commands is not None else count
    byte_bound=4096*(1+sum(c.startswith("observe ") for c in commands)) if commands else 4096
    if type(raw) is not bytes or len(raw)>byte_bound or any(len(line)>4096 for line in raw.splitlines()) or not raw.endswith(b'\n'):raise Refused('Parent receipt byte/framing bound')
    rows=[strict_json(line) for line in raw.decode('utf-8',errors='strict').splitlines()]
    if len(rows)!=count+1:raise Refused('Parent receipt count')
    ready=rows[0]
    if type(ready) is not dict or set(ready)!={'ready','scope'} or type(ready['ready']) is not bool or ready['ready'] is not True or ready['scope']!='parent-notify-only':raise Refused('Canonical parent readiness')
    for index,row in enumerate(rows[1:],1):
        observing=commands is not None and commands[index-1].startswith('observe ')
        fields={'sequence','accepted','scope','observation'} if observing else {'sequence','accepted','scope'}
        if type(row) is not dict or set(row)!=fields:raise Refused('Exact parent receipt fields')
        if type(row['sequence']) is not int or not 1<=row['sequence']<=2**32-1 or row['sequence']!=index:raise Refused('Canonical parent sequence')
        if type(row['accepted']) is not bool or row['accepted'] is not True or row['scope']!=('parent-surface-observation' if observing else 'parent-notify-only'):raise Refused('Canonical parent admission')
        if observing and type(row['observation']) is not dict:raise Refused('Parent observation packet shape')
    return rows

def _owned_process(session,host,client,commands,deadline,directory,record):
    # Evidence files exist before launch. Child output cannot block on our pipe.
    directory.mkdir(mode=0o700,parents=True,exist_ok=False)
    stdout=directory/'stdout.raw';stderr=directory/'stderr.raw';evidence=directory/'record.json'
    byte_bound=4096*(1+sum(c.startswith('observe ') for c in commands))
    record.update(commands=commands,byteBound=byte_bound,argv=[str(client)],stdout=str(stdout),stderr=str(stderr),physicalHardwareAccepted=False,probeAccepted=False)
    def persist():
        for name,path in (('stdout',stdout),('stderr',stderr)):
            if path.exists():
                extent=path.stat().st_size
                cap=byte_bound if name=='stdout' else 4096
                with path.open('rb') as source:captured=source.read(cap)
                record[name+'Bytes']=extent;record[name+'CapturedBytes']=len(captured)
                record[name+'PrefixSHA256']=hashlib.sha256(captured).hexdigest()
                record[name+'Truncated']=extent>len(captured)
        evidence.write_text(json.dumps(record,indent=2)+'\n')
    persist();process=None
    try:
        remaining=deadline_guard(deadline)
        limit=min(3,remaining);operation_end=time.monotonic()+limit
        with stdout.open('xb',buffering=0) as out,stderr.open('xb',buffering=0) as err:
            process=subprocess.Popen([str(client)],stdin=subprocess.PIPE,stdout=out,stderr=err,
                env=dict(session.host.env,ELM_PARENT_INPUT_QA='1'),cwd=session.host.runtime,start_new_session=True)
            row=host.original.process(process.pid);row.update(name='owned-parent-input',command=[str(client)],log=str(stdout))
            session.host.processes.append((process,row))
            record.update(process=row,actualStart=Path('/proc',str(process.pid),'stat').read_text().rsplit(')',1)[1].split()[19],registered=True,mayHavePressed=any(command.startswith('press ') for command in commands));persist()
            payload='\n'.join([*commands,'quit','']).encode('ascii')
            if len(payload)>1024:raise Refused('Parent command byte bound')
            process.stdin.write(payload);process.stdin.flush();process.stdin.close()
            while process.poll() is None:
                session.guard()
                if stdout.stat().st_size>byte_bound or stderr.stat().st_size>4096:raise Refused('Parent output bound')
                if time.monotonic()>=operation_end:raise subprocess.TimeoutExpired([str(client)],limit)
                time.sleep(min(.01,max(0,operation_end-time.monotonic())))
            record['exitCode']=process.returncode;persist()
        deadline_guard(deadline)
        if stdout.stat().st_size>byte_bound or stderr.stat().st_size>4096:raise Refused('Parent terminal output bound')
        if process.returncode!=0:raise Refused('Parent helper nonzero exit')
        record['receipts']=receipts(stdout.read_bytes(),commands);persist()
        return record
    except BaseException as error:
        record['error']=repr(error);record['timeout']=isinstance(error,subprocess.TimeoutExpired)
        if process is not None:
            if process.poll() is None:
                process.terminate();record['terminated']=True
                try:process.wait(timeout=.25)
                except subprocess.TimeoutExpired:process.kill();record['killed']=True;process.wait(timeout=.25)
            record['exitCode']=process.returncode
            if process.stdin and not process.stdin.closed:process.stdin.close()
            record['destructorReleaseFallback']='resource disconnect may release held buttons; NOT confirmed target delivery'
        persist();raise
    finally:
        persist()

def send(session,host,parent,identity,client,commands,deadline,*,evidence_dir,observation_proof=None):
    import re
    record={'startedMonotonic':time.monotonic(),'commands':commands,'probeAccepted':False,'physicalHardwareAccepted':False}
    # One directory per original attempt; any cleanup attempt has a separate record.
    directory=Path(evidence_dir)/('attempt-'+str(time.time_ns()))
    try:
        if type(commands) is not list or not 1<=len(commands)<=6 or any(type(c) is not str or not re.fullmatch(r'(?:motion [0-9]{1,4} [0-9]{1,4}|(?:press|release) (?:272|273|274)|observe [1-9][0-9]{0,9} [1-9][0-9]{0,19})',c) for c in commands):raise Refused('Closed original parent commands')
        peer=verify_peer(session,host,parent,identity,deadline);record['peer']=peer
        _owned_process(session,host,client,commands,deadline,directory,record)
        if any(c.startswith('observe ') for c in commands):
            if observation_proof is None:raise Refused('Missing exact parent observation proof')
            record['observations']=[observation_proof(row,record) for row in record['receipts'][1:] if row['scope']=='parent-surface-observation']
        record['peerAfter']=verify_peer(session,host,parent,identity,deadline)
        record['probeAccepted']=True
        (directory/'record.json').write_text(json.dumps(record,indent=2)+'\n')
        return record
    except BaseException as error:
        directory.mkdir(mode=0o700,parents=True,exist_ok=True)
        record['error']=repr(error);record['probeAccepted']=False
        if record.get('mayHavePressed'):
            cleanup={'scope':'release-only failure cleanup; never probe acceptance','originalDirectory':str(directory),'probeAccepted':False}
            # Original gesture has failed. This bounded .5s is cleanup only; it
            # cannot extend the successful six-second stage or retry a press.
            try:
                cleanup_end=time.monotonic()+.5
                cleanup['peer']=verify_peer(session,host,parent,identity,cleanup_end)
                buttons=sorted({c.split()[1] for c in commands if c.startswith('press ')})
                _owned_process(session,host,client,['release '+b for b in buttons],cleanup_end,directory/'release-cleanup',cleanup)
                cleanup['explicitReleaseAdmission']=True
            except BaseException as release_error:
                cleanup['explicitReleaseAdmission']=False;cleanup['error']=repr(release_error)
            record['releaseAttempt']=cleanup
        else:record['releaseAttempt']={'attempted':False,'reason':'No press submitted or helper never started'}
        (directory/'record.json').write_text(json.dumps(record,indent=2)+'\n')
        raise
