from pathlib import Path
import os,json,hashlib,difflib,ast
D=Path(__file__).resolve().parent
base=Path('/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v10/helper_setup.py')
original=base.read_text()
addition='''def completion_snapshot(config, deadline):
    """Owned journal snapshot; no blocking flock beyond the original deadline."""
    path=Path(config['log']);identity=observer.regular(path,0o600)
    fd=os.open(path,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        info=os.fstat(fd)
        if ((info.st_dev,info.st_ino)!=identity or not stat.S_ISREG(info.st_mode)
                or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o600):
            raise RuntimeError('Helper completion log identity changed')
        while True:
            remaining=deadline-time.monotonic()
            if remaining<=0:raise TimeoutError('Original helper completion deadline expired')
            try:
                observer.fcntl.flock(fd,observer.fcntl.LOCK_EX|observer.fcntl.LOCK_NB)
                break
            except BlockingIOError:
                time.sleep(min(.03,remaining))
        with os.fdopen(fd,'r+') as stream:
            fd=-1
            if observer.regular(path,0o600)!=identity:
                raise RuntimeError('Helper completion log replaced')
            if time.monotonic()>=deadline:
                raise TimeoutError('Original helper completion deadline expired')
            events=observer.rows(stream)
            if observer.regular(path,0o600)!=identity:
                raise RuntimeError('Helper completion log replaced during snapshot')
            if time.monotonic()>=deadline:
                raise TimeoutError('Original helper completion deadline expired')
            return events
    finally:
        if fd>=0:os.close(fd)


def registered_helper_closure(events, config):
    """Cleanup evidence only; never grants complete workload acceptance."""
    expected={}
    if 'serviceMembers' in config:
        expected={'service-motionTarget:'+observer.service_member(row):config['serviceTargetLimitPerMember'] for row in config['serviceMembers']}
        expected['service-motionRefresh']=config['serviceRefreshLimit']
    starts=[row for row in events if row['event']=='started']
    roots=config.get('queryRoots',{})
    service=[row for row in starts if row.get('class')=='query' and row.get('queryRoot')=='service']
    if any(row.get('serviceOperation') not in expected for row in service):
        raise RuntimeError('Unregistered service operation during helper drain')
    if any(sum(row.get('serviceOperation')==key for row in service)>limit for key,limit in expected.items()):
        raise RuntimeError('Extra service helper query during helper drain')
    if any(row.get('queryRoot') not in roots for row in starts if row.get('class')=='query'):
        raise RuntimeError('Unregistered query root during helper drain')
    # The unchanged oracle retains duplicate/unknown classes and roles,
    # operation membership, matching terminal identity, normal0 and actual
    # selected wrapper/delegate PID/start/PGID disappearance requirements.
    return observer.summarize(events,config['allowed'],require_all=False,
                              expect_harness=False,expected_service=None)


'''
replacement='''def wait_and_archive(config, destination, require_all=True, seconds=10,expect_harness=False,expect_service=False):
    deadline = time.monotonic() + seconds
    events=[];acceptance_error=None;drain_error=None;cleanup=None
    def archive_failure():
        if destination is not None:
            write_json(Path(destination), {'config':config,'events':events,'result':'fail',
                'reason':str(acceptance_error),
                'originalAcceptanceError':{'type':type(acceptance_error).__name__,'message':str(acceptance_error)},
                'cleanupProof':cleanup,'cleanupError':None if drain_error is None else repr(drain_error),
                'campaignAccepted':False})
    while time.monotonic() < deadline:
        try:events=completion_snapshot(config,deadline)
        except Exception as error:
            if acceptance_error is None:raise
            drain_error=error;break
        if any(row['event'] not in ('started','terminal') for row in events):
            if acceptance_error is None:
                if destination is not None:
                    write_json(Path(destination), {'config':config,'events':events,'result':'fail','reason':'unknown/refused operation'})
                raise RuntimeError('Unregistered/refused helper attempt observed')
            drain_error=RuntimeError('Unregistered/refused helper attempt observed');break
        if acceptance_error is None:
            if require_all and set(r['operation'] for r in events if r['event'] == 'started' and r.get('class','compositor')=='compositor') != set(config['allowed']):
                time.sleep(min(.03,max(0,deadline-time.monotonic())));continue
            try:
                expected=None
                if expect_service:
                    expected={'service-motionTarget:'+observer.service_member(row):config['serviceTargetLimitPerMember'] for row in config['serviceMembers']}
                    expected['service-motionRefresh']=config['serviceRefreshLimit']
                result = observer.summarize(events, config['allowed'], require_all,expect_harness,expected)
            except RuntimeError as error:
                # This exact first acceptance failure is permanent. No later
                # complete-oracle poll may normalize counts or erase it.
                acceptance_error=error
            else:
                if result is not None and time.monotonic()<deadline:
                    if destination is not None:
                        write_json(Path(destination), {'config': config, **result})
                    return result
        if acceptance_error is not None:
            try:result=registered_helper_closure(events,config)
            except Exception as error:drain_error=error;break
            if result is not None and time.monotonic()<deadline:
                cleanup={'registeredJobsNormal':True,'allExactProcessesGone':True,
                         'completionMonotonic':time.monotonic(),'originalDeadlineMonotonic':deadline,
                         'normal':result,'completeWorkloadAccepted':False}
                break
        time.sleep(min(.03,max(0,deadline-time.monotonic())))
    if acceptance_error is not None:
        if cleanup is None and drain_error is None:
            drain_error=TimeoutError('Exact registered helper drain exceeded original completion deadline')
        try:archive_failure()
        except Exception as error:
            acceptance_error.add_note('Helper failure archive error: '+repr(error))
            raise acceptance_error from error
        if drain_error is not None:
            acceptance_error.add_note('Helper cleanup error retained: '+repr(drain_error))
        raise acceptance_error
    if destination is not None:
        write_json(Path(destination), {'config':config,'events':events,'result':'fail','reason':'completion timeout'})
    raise RuntimeError('Exact registered helpers did not all finish normally')
'''
old=original[original.index('def wait_and_archive('):]
proposed=original[:original.index('def wait_and_archive(')]+addition+replacement
proposed=proposed.replace('import hashlib\n','import errno\nimport hashlib\n',1).replace('except BlockingIOError:\n                time.sleep', 'except BlockingIOError as error:\n                if error.errno not in (errno.EAGAIN,errno.EWOULDBLOCK):raise\n                time.sleep')
ast.parse(proposed)
# Unchanged original pure/registration/archive bodies; original observer stays exact.
o={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(original).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
p={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(proposed).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
unchanged={n:o[n]==p[n] for n in o if n!='wait_and_archive'}
assert all(unchanged.values())
def write(name,data):
 fd=os.open(D/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:f.write(data)
write('intended-v2-helper_setup.py',proposed)
write('intended-v2.patch',''.join(difflib.unified_diff(original.splitlines(True),proposed.splitlines(True),fromfile=str(base),tofile='fresh-B11/helper_setup.py')))
row=dict(originalPath=str(base),originalSHA256=hashlib.sha256(original.encode()).hexdigest(),proposedSHA256=hashlib.sha256(proposed.encode()).hexdigest(),originalMode=base.stat().st_mode&0o777,unchangedOriginalFunctions=unchanged,originalObserverPath=str(base.with_name('helper_observer.py')),originalObserverSHA256=hashlib.sha256(base.with_name('helper_observer.py').read_bytes()).hexdigest(),original38Unchanged=True,original34Unchanged=True,originalTimeoutSeconds=10,runtimeApplied=False)
write('intended-v2-source-map.json',json.dumps(row,indent=2)+'\n')
print(json.dumps(row))
