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
PAIR = B.parent / 'toolkit-interruption-v5'
SNAP = PAIR / 'native-candidate/installed-snap.lua'
OMARCHY_BIND = Path('/usr/share/omarchy/default/hypr/helpers.lua')
FRESH_HELPER = B.parent / 'snap-close-identity-v1/hypr-snap-groups'

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
    config={'instance':env['HYPRLAND_INSTANCE_SIGNATURE'],
            'compositor':{'pid':session.evidence['compositorPID'],'start':str(session.evidence['compositorStart'])},
            'socket':str(socket_path),'socketIdentity':[info.st_dev,info.st_ino,info.st_uid],
            'versionSHA256':version['replySHA256'],'helpers':helpers,
            'log':str(log),'allowed':['hydrate','inactive-fileDrag']}
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
        'harness':{'identity':harness_identity,'argv':harness_command,'source':str(B/'native_integration.py'),
                   'sourceSHA256':observer.digest(B/'native_integration.py'),'executable':str(harness_exe),'executableSHA256':observer.digest(harness_exe)}}
    write_json(Path(env['WINDOW_QA_HELPER_CONFIG']),config)
    return config


def install_lua(env, config, session, repl_script):
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
    script = 'dofile(' + json.dumps(str(OMARCHY_BIND)) + ')\ndofile(' + json.dumps(str(SNAP)) + ')\nprint("WQA paired Snap Lua loaded")'
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
    config['allowed'] = ['hydrate','inactive-fileDrag', *operations]
    write_json(path, config)
    return config


def wait_and_archive(config, destination, require_all=True, seconds=10,expect_harness=False):
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
            result = observer.summarize(events, config['allowed'], require_all,expect_harness)
        except RuntimeError as error:
            if destination is not None:
                write_json(Path(destination), {'config':config,'events':events,'result':'fail','reason':str(error)})
            raise
        if result is not None:
            if destination is not None:
                write_json(Path(destination), {'config': config, **result})
            return result
        time.sleep(.03)
    if destination is not None:
        write_json(Path(destination), {'config':config,'events':events,'result':'fail','reason':'completion timeout'})
    raise RuntimeError('Exact registered helpers did not all finish normally')
