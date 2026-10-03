"""Private helper materialization and archival; never starts a process on import."""
from pathlib import Path
from contextlib import contextmanager
import hashlib
import json
import os
import shutil
import stat
import time
import helper_observer as observer

B = Path(__file__).resolve().parent
PAIR = B.parent / 'toolkit-interruption-v6'
SNAP = PAIR / 'native-candidate/installed-snap.lua'
OMARCHY_BIND = Path('/usr/share/omarchy/default/hypr/helpers.lua')
FRESH_HELPER = B.parent / 'snap-close-identity-v1/hypr-snap-groups'

class HelperBusy(RuntimeError):
    """A genuine prior invocation is still completing; no registration changed."""

def archive_witness(info):
    return (info.st_dev,info.st_ino,info.st_uid,info.st_mode,info.st_size,info.st_mtime_ns,info.st_ctime_ns)

def archive_descriptor(stream,path):
    before=os.fstat(stream.fileno())
    if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or stat.S_IMODE(before.st_mode)!=0o600 or before.st_size>67108864:
        raise RuntimeError('Unsafe bounded helper archival source')
    stream.seek(0);data=stream.read(67108865)
    if len(data)!=before.st_size or archive_witness(os.fstat(stream.fileno()))!=archive_witness(before) or archive_witness(Path(path).lstat())!=archive_witness(before):
        raise RuntimeError('Helper archival source changed during full EOF read')
    return data,dict(device=before.st_dev,inode=before.st_ino,uid=before.st_uid,mode=stat.S_IMODE(before.st_mode),size=before.st_size,mtimeNs=before.st_mtime_ns,ctimeNs=before.st_ctime_ns)

def diagnostic_material(config):
    home=Path(config['log']).parent;settings=config['delegateDiagnostic']
    source=home/'.local/bin/delegate_diagnostics.py';directory=home/'delegate-diagnostics'
    if settings['source']!=str(source) or settings['directory']!=str(directory):raise RuntimeError('Exact private diagnostic material required')
    observer.regular(source,0o700)
    if observer.digest(source)!=settings['sourceSHA256']:raise RuntimeError('Exact diagnostic source changed')
    info=directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o700:raise RuntimeError('Exact private diagnostic directory required')
    return directory

def diagnostic_path(config,event):
    directory=diagnostic_material(config);identity=event['wrapper']
    expected=directory/(str(identity['pid'])+'-'+str(identity['start'])+'.jsonl')
    if event.get('diagnosticLog')!=str(expected):raise RuntimeError('Exact authorized diagnostic log differs')
    return expected

def diagnostic_records(path):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    with os.fdopen(fd,'rb') as stream:data,identity=archive_descriptor(stream,path)
    if len(data)>33554432 or (data and not data.endswith(b'\n')):raise RuntimeError('Bounded complete diagnostic JSONL required')
    rows=[json.loads(line) for line in data.splitlines()]
    if len(rows)>2048 or any(not isinstance(row,dict) or row.get('index')!=index for index,row in enumerate(rows)):raise RuntimeError('Complete ordered diagnostic records required')
    return data,identity,rows

def verify_diagnostic(config,start,terminal):
    path=diagnostic_path(config,start);data,identity,rows=diagnostic_records(path)
    summary=terminal.get('diagnostic')
    if not isinstance(summary,dict) or summary.get('path')!=str(path) or summary.get('complete') is not True or summary.get('normalOriginalWait') is not True or summary.get('errors')!=[] or summary.get('exitCode')!=terminal['exitCode'] or summary.get('productFdRoutingChanged') is not False:raise RuntimeError('Exact complete delegate diagnostic required')
    if not rows or rows[0]['event']!='observer-bound' or rows[-1]['event']!='delegate-wait-terminal':raise RuntimeError('Exact diagnostic boundary records required')
    bound=rows[0];end=rows[-1]
    if bound['delegate']!=start['delegate'] or bound['parent']!=start['ancestry'][0] or bound['qs']!=start['ancestry'][1] or bound['metadata']['operation']!=start['operation'] or bound['metadata']['actualSHA256']!=start['actualSHA256'] or bound['metadata']['observerSHA256']!=config['delegateDiagnostic']['sourceSHA256']:raise RuntimeError('Exact diagnostic source/lifetime binding differs')
    if end['identity']!=start['delegate'] or end['complete'] is not True or end['errors']!=[] or end['normalOriginalWait'] is not True or end['exitCode']!=terminal['exitCode'] or os.waitstatus_to_exitcode(end['rawWaitStatus'])!=terminal['exitCode']:raise RuntimeError('Exact original delegate wait differs')
    allowed={'observer-bound','bootstrap-stop','bootstrap-syscall-return','backend-exec','stdio-write-entry','stdio-write-return','genuine-signal-forward','delegate-wait-terminal'}
    if any(row['event'] not in allowed for row in rows):raise RuntimeError('Unknown/error diagnostic event')
    execs=[row for row in rows if row['event']=='backend-exec']
    if [row['execOrdinal'] for row in execs]!=[0,1] or end['execChain']!=2:raise RuntimeError('Exact backend exec chain incomplete')
    actual=start['actual'];expected=[(str(Path('/usr/bin/env').resolve()),['/usr/bin/env','python3',actual,'list','--json']),(str(Path('/usr/bin/python3').resolve()),['python3',actual,'list','--json'])]
    if any(row['identity']!=start['delegate'] or row['stdio']!=bound['stdio'] or (row['executable'],row['argv'])!=target for row,target in zip(execs,expected)):raise RuntimeError('Exact diagnostic exec/stdio identity differs')
    if any(type(row.get('monotonicNs')) is not int or type(row.get('utcNs')) is not int for row in rows) or any(left['monotonicNs']>right['monotonicNs'] for left,right in zip(rows,rows[1:])):raise RuntimeError('Exact chronological diagnostic observations required')
    entries={row['index']:row for row in rows if row['event']=='stdio-write-entry'};returned=set()
    for row in rows:
        if row['event']!='stdio-write-return':continue
        key=row['entry']
        if key not in entries or key in returned or key>=row['index']:raise RuntimeError('Exact stdio entry/return pairing required')
        entry=entries[key];raw=bytes.fromhex(entry['offeredBytesHex']);value=row['kernelReturn'];error=value<0
        if entry.get('fdWitness')!=bound['stdio'].get(str(entry['fd'])) or entry['fd'] not in (1,2) or entry['nr'] not in (1,20) or entry['fd']!=row['fd'] or entry['nr']!=row['nr'] or len(raw)>1048576 or sum(entry['vectorLengths'])!=len(raw) or hashlib.sha256(raw).hexdigest()!=entry['offeredSHA256'] or type(value) is not int or value>len(raw) or row['kernelIsError']!=error or row['errno']!=(-value if error else None) or row['offeredCount']!=len(raw) or row['deliveredCount']!=(0 if error else value):raise RuntimeError('Exact original stdio bytes/return required')
        returned.add(key)
    if returned!=set(entries) or end['stdioSyscalls']!=len(entries) or summary['stdioSyscalls']!=len(entries):raise RuntimeError('Incomplete original stdio observations')
    return dict(path=str(path),sha256=hashlib.sha256(data).hexdigest(),identity=identity,records=len(rows),stdioSyscalls=len(entries),completeEOF=True,exitCode=terminal['exitCode'],schedulingPerturbed=True,nativeTimingAccepted=False)

def diagnostic_completeness(config,events):
    starts=[row for row in events if row['event']=='started'];ends=[row for row in events if row['event']=='terminal'];proof=[]
    for start in starts:
        selected=start.get('queryRoot')=='qs' and start['helper']=='snap'
        if not selected:
            if start.get('diagnosticLog') is not None:raise RuntimeError('Unexpected delegated diagnostic role')
            continue
        matches=[row for row in ends if row['operation']==start['operation'] and row['wrapper']==start['wrapper'] and row['delegate']==start['delegate']]
        if len(matches)!=1:raise RuntimeError('Exact diagnostic terminal missing/duplicated')
        if observer.still_live(start['wrapper']) or observer.still_live(start['delegate']):raise RuntimeError('Exact diagnostic processes still active')
        proof.append(verify_diagnostic(config,start,matches[0]))
    expected={Path(row['path']) for row in proof}
    if set(diagnostic_material(config).iterdir())!=expected:raise RuntimeError('Extra or missing diagnostic invocation')
    return dict(complete=True,invocations=proof,observedQSQueries=len(proof),schedulingPerturbed=True,nativeTimingAccepted=False)

def archive_diagnostics(config,events,destination):
    directory=diagnostic_material(config);result=[];expected=set()
    for event in events:
        if event['event']=='started' and event.get('queryRoot')=='qs' and event['helper']=='snap':expected.add(diagnostic_path(config,event))
    destination.mkdir(mode=0o700)
    for path in sorted(set(directory.iterdir())|expected):
        row=dict(source=str(path),expected=path in expected,completeEOF=False)
        try:
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
            with os.fdopen(fd,'rb') as stream:
                before=os.fstat(stream.fileno())
                if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or stat.S_IMODE(before.st_mode)!=0o600 or before.st_size>33554432:raise RuntimeError('Unsafe bounded diagnostic archive')
                data=stream.read(33554433);after=os.fstat(stream.fileno());named=path.lstat()
            complete=len(data)==before.st_size and archive_witness(before)==archive_witness(after)==archive_witness(named)
            fd=os.open(destination/path.name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,'wb') as stream:stream.write(data)
            row.update(archive=str(destination/path.name),sha256=hashlib.sha256(data).hexdigest(),sourceBefore=list(archive_witness(before)),sourceAfter=list(archive_witness(after)),sourceNamed=list(archive_witness(named)),completeEOF=complete)
            if not complete:raise RuntimeError('Diagnostic archival source changed/truncated; raw bytes retained without acceptance')
            if data and not data.endswith(b'\n'):raise RuntimeError('Truncated diagnostic JSONL; raw bytes retained')
            records=[json.loads(line) for line in data.splitlines()]
            if len(records)>2048 or any(not isinstance(record,dict) or record.get('index')!=index for index,record in enumerate(records)):raise RuntimeError('Diagnostic index incomplete; raw bytes retained')
            row['records']=len(records)
        except Exception as error:row['error']=repr(error)
        result.append(row)
    write_json(destination/'archive.json',dict(logs=result,normalLifecycleAccepted=False,sourceSHA256=config['delegateDiagnostic']['sourceSHA256']))
    return result

def archive_helpers(config,destination):
    """Read-only failure evidence; requires no compositor IPC or live parent."""
    log=Path(config['log']);home=log.parent
    observer.verify_runtime(home.parent)
    if home.name!='taskbar-home' or log!=home/'helper-events.jsonl':raise RuntimeError('Exact owned helper archive path required')
    fd=os.open(home/'helper-config.json',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    with os.fdopen(fd,'rb') as stream:config_bytes,config_identity=archive_descriptor(stream,home/'helper-config.json')
    with observer.locked_log(log) as stream:
        # Binary view of the exact flocked descriptor keeps the raw JSONL bytes.
        with os.fdopen(os.dup(stream.fileno()),'rb') as binary:
            log_bytes,log_identity=archive_descriptor(binary,log)
    destination=Path(destination);destination.mkdir(mode=0o700)
    for name,data in [('helper-events.jsonl',log_bytes),('helper-config.json',config_bytes)]:
        fd=os.open(destination/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as stream:stream.write(data)
    events=[];parse_errors=[]
    for index,line in enumerate(log_bytes.splitlines(),1):
        if not line.strip():continue
        try:
            event=json.loads(line)
            if not isinstance(event,dict):raise ValueError('Event must be object')
            events.append(event)
        except (ValueError,TypeError) as error:parse_errors.append(dict(line=index,error=str(error)))
    try:json.loads(config_bytes)
    except (ValueError,TypeError) as error:parse_errors.append(dict(configError=str(error)))
    processes=[];seen=set()
    for event in events:
        for name in ('wrapper','delegate'):
            row=event.get(name)
            if row is None:continue
            try:identity=(row['pid'],row['start'],row['pgid'])
            except (TypeError,KeyError) as error:
                parse_errors.append(dict(identityError=str(error)));continue
            if identity in seen:continue
            seen.add(identity);processes.append(dict(role=name,identity=row,liveAtArchive=observer.still_live(row)))
    result=dict(configSHA256=hashlib.sha256(config_bytes).hexdigest(),logSHA256=hashlib.sha256(log_bytes).hexdigest(),configIdentity=config_identity,logIdentity=log_identity,events=events,parseErrors=parse_errors,processes=processes,archive=str(destination),completeEOF=True,compositorIPCRequired=False,normalLifecycleAccepted=False)
    result['delegateDiagnostics']=archive_diagnostics(config,events,destination/'delegate-diagnostics')
    write_json(destination/'archive.json',result)
    if parse_errors:raise RuntimeError('Malformed helper evidence retained as raw bytes')
    return result

@contextmanager
def retain_before_runtime_delete(get_config,destination,report):
    try:yield
    finally:
        config=get_config()
        if config is not None:
            try:report['helperArchive']=archive_helpers(config,destination)
            except Exception as error:
                report['helperArchiveError']=repr(error)
                raise


def write_json(path, value):
    temporary = path.with_name(path.name + '.new')
    with temporary.open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')
    temporary.chmod(0o600)
    temporary.replace(path)


def prepare(env, session):
    session.guard()
    home = Path(env['HOME'])
    if home != Path(session.env['XDG_RUNTIME_DIR']) / 'taskbar-home':
        raise RuntimeError('Selected private helper home required')
    helpers={}
    for kind,name,source in (('snap','hypr-snap-groups',FRESH_HELPER),('shell','omarchy-shell',B/'payload/omarchy/bin/omarchy-shell')):
        wrapper=home/'.local/bin'/name
        if kind=='shell':
            if wrapper.exists():raise RuntimeError('Unexpected existing inactive relay entry')
            shutil.copyfile(source,wrapper);wrapper.chmod(0o700)
        if observer.digest(wrapper)!=observer.digest(source):raise RuntimeError('Unreviewed private helper payload')
        actual=wrapper.with_name(name+'.actual');wrapper.rename(actual);actual.chmod(0o700)
        shutil.copyfile(B/'helper_observer.py',wrapper);wrapper.chmod(0o700)
        helpers[kind]={'wrapper':str(wrapper),'wrapperSHA256':observer.digest(wrapper),
                       'actual':str(actual),'actualSHA256':observer.digest(actual),
                       'invocation':str(wrapper) if kind=='snap' else 'omarchy-shell'}
    log=home/'helper-events.jsonl'
    with log.open('x'):pass
    log.chmod(0o600)
    version=session.evidence['ipcReadiness'][-1]
    socket_path=Path(version['path']);info=socket_path.lstat()
    diagnostic_source=home/'.local/bin/delegate_diagnostics.py'
    shutil.copyfile(B/'delegate_diagnostics.py',diagnostic_source);diagnostic_source.chmod(0o700)
    diagnostic_directory=home/'delegate-diagnostics';diagnostic_directory.mkdir(mode=0o700)
    config={'delegateDiagnostic':{'source':str(diagnostic_source),'sourceSHA256':observer.digest(diagnostic_source),'directory':str(diagnostic_directory)},
            'instance':env['HYPRLAND_INSTANCE_SIGNATURE'],
            'compositor':{'pid':session.evidence['compositorPID'],'start':str(session.evidence['compositorStart'])},
            'socket':str(socket_path),'socketIdentity':[info.st_dev,info.st_ino,info.st_uid],
            'versionSHA256':version['replySHA256'],'helpers':helpers,
            'log':str(log),'allowed':['generation:1:hydrate','generation:1:inactive-fileDrag'],
            'loadGeneration':1}
    path = home / 'helper-config.json'; write_json(path, config)
    env['WINDOW_QA_HELPER_CONFIG'] = str(path)
    return config


def register_query_roots(env,config,qs_identity,qs_command,harness_identity,harness_command):
    config['queryTaskbar']={'path':str(Path(env['HOME'])/'.local/bin/hypr-taskbar'),
                            'sha256':observer.digest(Path(env['HOME'])/'.local/bin/hypr-taskbar'),
                            'python':'/usr/bin/python3','pythonSHA256':observer.digest('/usr/bin/python3')}
    config['queryEnvironment']={key:env[key] for key in ('HOME','PATH','XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','OMARCHY_PATH','WINDOW_QA_HELPER_CONFIG')}
    qs_exe=Path(qs_command[0]).resolve();harness_exe=(Path('/proc')/str(harness_identity['pid'])/'exe').resolve()
    config['queryRoots']={
        'qs':{'identity':qs_identity,'argv':list(map(str,qs_command)),'config':str(B/'payload/omarchy/shell'),
              'executable':str(qs_exe),'executableSHA256':observer.digest(qs_exe),
              'configSHA256':observer.digest(B/'payload/omarchy/shell/shell.qml')},
        'harness':{'identity':harness_identity,'argv':harness_command,'source':str(B/'run_native.py'),
                   'sourceSHA256':observer.digest(B/'run_native.py'),'executable':str(harness_exe),'executableSHA256':observer.digest(harness_exe)}}
    write_json(Path(env['WINDOW_QA_HELPER_CONFIG']),config)
    return config

def register_service_root(env,config,identity,command,windows,service_source):
    if 'service' in config['queryRoots']:raise RuntimeError('Service root already registered')
    executable=Path(command[0]).resolve();source=Path(command[1])
    members=[{key:str(w[key]) if key=='stableId' else w[key] for key in ('address','stableId','pid')} for w in windows]
    if len(members)!=3 or len({observer.service_member(row) for row in members})!=3:raise RuntimeError('Exact three distinct service members required')
    config['queryRoots']['service']={'identity':identity,'argv':list(map(str,command)),
        'executable':str(executable),'executableSHA256':observer.digest(executable),
        'source':str(source),'sourceSHA256':observer.digest(source),
        'sources':{str(Path(service_source)/name):observer.digest(Path(service_source)/name) for name in
            ('native_desktop.py','production_motion_6d9.py','scene_controller.py','native_runtime.py','context_provider.py','service_runtime.py')}}
    config['serviceMembers']=members
    config['serviceTargetLimitPerMember']=2;config['serviceRefreshLimit']=3
    write_json(Path(env['WINDOW_QA_HELPER_CONFIG']),config)
    return config


def paired_lua_script(before_snap=''):
    return before_snap + '\n' + 'dofile(' + json.dumps(str(OMARCHY_BIND)) + ')\ndofile(' + json.dumps(str(SNAP)) + ')\nprint("WQA paired Snap Lua loaded")'


def install_lua(env, config, session, repl_script, before_snap=""):
    # Actual compositor HOME must match actual helper/taskbar HOME. The initial
    # owned compositor HOME was separate; changing the client's env is insufficient.
    names = ('HOME', 'PATH', 'OMARCHY_PATH', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_STATE_HOME',
             'XDG_CACHE_HOME', 'PYTHONDONTWRITEBYTECODE', 'GIO_USE_VFS',
             'QT_NO_XDG_DESKTOP_PORTAL', 'WINDOW_QA_HELPER_CONFIG')
    script = '\n'.join('hl.env(' + json.dumps(key) + ',' + json.dumps(env[key]) + ')' for key in names)
    session.ctl('repl', repl_script(script))
    observed = session.ctl('repl', repl_script('print(table.concat({' +
        ','.join('os.getenv(' + json.dumps(key) + ')' for key in names) + '},"\\n"))')).strip()
    if observed.splitlines() != [env[key] for key in names]:
        raise RuntimeError('Actual selected compositor helper environment differs')
    # Actual full sources, not shortened synthetic callback replacements.
    script = paired_lua_script(before_snap)
    result = session.ctl('repl', repl_script(script))
    if result.strip() != 'WQA paired Snap Lua loaded':
        raise RuntimeError('Actual paired Snap Lua load failed: ' + result)
    return {'actualCompositorEnv': dict(zip(names, observed.splitlines())),
            'snapSHA256': observer.digest(SNAP), 'bindingHelperSHA256': observer.digest(OMARCHY_BIND),
            'fullSourcesLoaded': True, 'loadReply': result}


def allow_closes(env, config, windows):
    path = Path(env['WINDOW_QA_HELPER_CONFIG'])
    actual = observer.read_config(path)
    if actual != config:
        raise RuntimeError('Private helper configuration changed before closes')
    operations = [observer.operation(['forget-closed', row['address'], str(row['stableId']), str(row['pid'])]) for row in windows]
    if len(operations) != len(set(operations)):
        raise RuntimeError('Duplicate native close lifetime')
    if any(key in config['allowed'] for key in operations):raise RuntimeError('Close lifetime already registered')
    config['allowed'] = [*config['allowed'], *operations]
    write_json(path, config)
    return config


def register_load_generation(env,config):
    """Serialize a genuine full Snap load after all prior helpers completed."""
    path=Path(env['WINDOW_QA_HELPER_CONFIG'])
    with observer.locked_log(config['log']) as stream:
        if observer.read_config(path)!=config:raise RuntimeError('Load generation configuration changed')
        events=observer.rows(stream)
        started=[row for row in events if row['event']=='started']
        terminal=[row for row in events if row['event']=='terminal']
        required=['generation:'+str(config['loadGeneration'])+':'+name for name in ('hydrate','inactive-fileDrag')]
        if any(row['event']=='refused' for row in events):raise RuntimeError('Refused helper cannot authorize another load')
        if any(sum(row.get('operation')==key for row in started)>1 for key in required):raise RuntimeError('Duplicate prior full Snap load operation')
        if any(sum(row.get('operation')==key for row in started)!=1 for key in required):raise HelperBusy('Prior actual full Snap load operations incomplete')
        for row in started:
            matching=[end for end in terminal if end.get('operation')==row['operation'] and end.get('wrapper')==row['wrapper'] and end.get('delegate')==row['delegate']]
            if len(matching)>1 or any(end.get('exitCode')!=0 for end in matching):raise RuntimeError('Prior exact helper terminal abnormal/duplicated')
            if not matching or observer.still_live(row['wrapper']) or observer.still_live(row['delegate']):raise HelperBusy('Prior exact helpers must normally retire before reload generation')
        generation=config['loadGeneration']+1
        config['loadGeneration']=generation
        config['allowed'] += ['generation:'+str(generation)+':'+name for name in ('hydrate','inactive-fileDrag')]
        write_json(path,config)
    return generation


def append_service_members(env,config,windows):
    """Extend exact already gated root for a new observed three-member family."""
    members=[{key:str(w[key]) if key=='stableId' else w[key] for key in ('address','stableId','pid')} for w in windows]
    if len(members)!=3 or len({observer.service_member(row) for row in members})!=3:raise RuntimeError('Exact three distinct new service members required')
    path=Path(env['WINDOW_QA_HELPER_CONFIG'])
    with observer.locked_log(config['log']) as stream:
        if observer.read_config(path)!=config:raise RuntimeError('Service generation configuration changed')
        observer.service_ancestor({'parent':config['queryRoots']['service']['identity']['pid']},config)
        if any(row in config['serviceMembers'] for row in members):raise RuntimeError('Service member lifetime already registered')
        events=observer.rows(stream)
        service=[row for row in events if row['event']=='started' and row.get('queryRoot')=='service']
        terminal=[row for row in events if row['event']=='terminal']
        expected={ 'service-motionTarget:'+observer.service_member(row):2 for row in config['serviceMembers'] }
        expected['service-motionRefresh']=config['serviceRefreshLimit']
        if any(sum(row.get('serviceOperation')==key for row in service)!=count for key,count in expected.items()):raise RuntimeError('Prior exact service family calls incomplete')
        if any(not any(end.get('operation')==row['operation'] and end.get('wrapper')==row['wrapper'] and end.get('delegate')==row['delegate'] and end.get('exitCode')==0 for end in terminal) or observer.still_live(row['wrapper']) or observer.still_live(row['delegate']) for row in service):raise RuntimeError('Prior service helpers remain active/abnormal')
        if any(row['event']=='refused' for row in events):raise RuntimeError('Refused helper cannot extend service family')
        config['serviceMembers'] += members
        config['serviceRefreshLimit'] += 3
        write_json(path,config)
    return config


def workload_expectations(config,service_launched,harness_attempted,harness_used,full_workload):
    registered=bool(config.get('serviceMembers')) and 'service' in config.get('queryRoots',{})
    if any(key in config for key in ('serviceMembers','serviceTargetLimitPerMember','serviceRefreshLimit')) or 'service' in config.get('queryRoots',{}):
        if not registered or any(type(config.get(key)) is not int or config[key]<=0 for key in ('serviceTargetLimitPerMember','serviceRefreshLimit')):raise RuntimeError('Incomplete exact service registration')
        if len({observer.service_member(row) for row in config['serviceMembers']})!=len(config['serviceMembers']):raise RuntimeError('Duplicate exact service members')
    if service_launched and not registered:raise RuntimeError('Actual launched service lacks exact member/root registration')
    if harness_used and not harness_attempted:raise RuntimeError('Genuine harness snapshot result lacks actual attempt')
    if full_workload and not(registered and service_launched and harness_used):raise RuntimeError('Full held workload lacks genuine service/snapshot routes')
    return dict(serviceRegistered=registered,harnessSnapshotAttempted=bool(harness_attempted),fullWorkloadRequired=bool(full_workload))


def wait_and_archive(config, destination, require_all=True, seconds=10,expect_harness=False,expect_service=False):
    deadline = time.monotonic() + seconds
    events=[]
    while time.monotonic() < deadline:
        with observer.locked_log(config['log']) as stream:
            events = observer.rows(stream)
        if any(row['event'] not in ('started','terminal') for row in events):
            if destination is not None:
                write_json(Path(destination), {'config':config,'events':events,'result':'fail','reason':'unknown/refused operation'})
            raise RuntimeError('Unregistered/refused helper attempt observed')
        if require_all and set(r['operation'] for r in events if r['event'] == 'started' and r.get('class','compositor')=='compositor') != set(config['allowed']):
            time.sleep(.03); continue
        try:
            expected=None
            if expect_service:
                expected={'service-motionTarget:'+observer.service_member(row):config['serviceTargetLimitPerMember'] for row in config['serviceMembers']}
                expected['service-motionRefresh']=config['serviceRefreshLimit']
            result = observer.summarize(events, config['allowed'], require_all,expect_harness,expected)
        except RuntimeError as error:
            if destination is not None:
                write_json(Path(destination), {'config':config,'events':events,'result':'fail','reason':str(error)})
            raise
        if result is not None:
            result['delegateDiagnosticCompleteness']=diagnostic_completeness(config,events)
            if destination is not None:
                write_json(Path(destination), {'config': config, **result})
            return result
        time.sleep(.03)
    if destination is not None:
        write_json(Path(destination), {'config':config,'events':events,'result':'fail','reason':'completion timeout'})
    raise RuntimeError('Exact registered helpers did not all finish normally')
