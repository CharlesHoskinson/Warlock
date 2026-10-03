"""Source-only prepared native software campaign; only root may execute it."""
from pathlib import Path
from contextlib import ExitStack
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import traceback
import c1_pairing
import observations
from producer_observer import Observer,generated_source,wait
from verify_c1 import verify

B=Path(__file__).resolve().parent
QA=B.parent
HOST=QA/'private-weston-aq-host-v4'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def exact():
    packet=c1_pairing.verified_packet()
    row=json.loads((B/'frozen-inputs.json').read_text())
    for name,value in row['inputs'].items():
        if sha(name)!=value or Path(name).stat().st_mode&0o7777!=row['inputModes'][name]:raise ValueError('Frozen software closure changed: '+name)
    for name,value in row['symlinks'].items():
        if not Path(name).is_symlink() or os.readlink(name)!=value:raise ValueError('Frozen loader link changed')
    return packet,row
def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--attempt',type=Path);a=p.parse_args()
    packet,closure=exact()
    if not a.execute:
        print(json.dumps(dict(preflight='pass',nativeLaunch=False,inputs=len(closure['inputs']))));return 0
    sys.path.insert(0,str(QA));from qa_launch import require_qa_scope
    sys.path.insert(0,str(c1_pairing.PRODUCER));from verify_production_pipeline import verify_selection
    require_qa_scope();os.umask(0o077)
    if not a.attempt:p.error('Fresh owned --attempt required')
    out=a.attempt.resolve()
    if out.parent!=B or not out.name.startswith('attempt-'):raise ValueError('Owned fresh attempt required')
    out.mkdir(mode=0o700)
    report=dict(result='pending',checks=[],nativeEffectAccepted=False,physicalCadenceAccepted=False,mainWrites=False)
    before=None;session=None;observers=[]
    def check(name,value,**details):
        report['checks'].append(dict(name=name,passed=bool(value),**details))
        if not value:raise RuntimeError(name)
    def close_all():
        failures=[]
        for observer in reversed(observers):
            try:
                code=observer.close()
                row=dict(pid=observer.process.pid,exitCode=code,completeEOF=observer.stdout_eof,
                         gone=not Path('/proc',str(observer.process.pid)).exists())
                report.setdefault('producerCleanup',[]).append(row)
                if code!=0 or not row['gone']:failures.append(row)
            except BaseException as error:failures.append(dict(error=repr(error)))
        if failures:report['cleanupFailure']=failures;raise RuntimeError('Normal clients-first producer close failed')
    try:
        before=observations.capture(out/'main-before')
        spec=importlib.util.spec_from_file_location('_c1_host',HOST/'weston_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
        with host.PrivateHyprSession(output=out/'host',main_env=dict(os.environ),width=320,height=240,
                nested_lua=(B/'private-nested.lua').read_bytes(),dri_prime='pci-0000_00_02_0',mesa_vendor=True) as session,ExitStack() as resources:
            resources.callback(close_all)
            session.guard();session.ctl('output','create','headless','ORACLE-SECOND')
            monitors=session.data('monitors')
            check('Actual private mixed scale outputs and Xwayland disabled',
                {(r['name'],r['scale']) for r in monitors}=={('WAYLAND-1',1),('ORACLE-SECOND',1.5)}
                and session.data('getoption','xwayland:enabled')['bool'] is False,outputs=monitors)
            captured=[]
            for i in range(3):
                path=out/('member-'+str(i)+'.png');generated_source(path,96,80,i)
                rect=dict(x=270+i*16,y=32+i*16,width=96,height=80)
                captured.append(dict(stableId='abc'+str(i+1),pid=os.getpid(),path=str(path),digest=sha(path),pixels=[96,80],captureScale=1,nativeRect=rect,atlasRect=rect,iconRect=dict(x=380+i*8,y=196,width=24,height=20),insets=dict(left=0,top=0,right=0,bottom=0)))
            ids=[{k:s[k] for k in ('stableId','pid')} for s in captured]
            def launch(name):
                directory=out/name;directory.mkdir(mode=0o700)
                observer=Observer([packet['binary']],session.env,directory);observers.append(observer)
                proc=Path('/proc')/str(observer.process.pid)
                status=proc.joinpath('status').read_text();start=proc.joinpath('stat').read_text().rsplit(')',1)[1].split()[19]
                uid=next(line.split()[1:] for line in status.splitlines() if line.startswith('Uid:'))
                parent=next(line.split()[1] for line in status.splitlines() if line.startswith('PPid:'))
                check(name+' exact owned renderer lifetime/UID/argv/executable',
                    all(int(x)==os.getuid() for x in uid) and int(parent)==os.getpid()
                    and proc.joinpath('cgroup').read_text()==Path('/proc/self/cgroup').read_text()
                    and proc.joinpath('exe').resolve()==Path(packet['binary']).resolve()
                    and sha(proc/'exe')==packet['binarySHA256']
                    and proc.joinpath('cmdline').read_bytes().split(b'\0')==[packet['binary'].encode(),b''],
                    pid=observer.process.pid,start=start)
                observer.send(command='prepareOutputs')
                outputs=observer.find(lambda r:r.get('event')=='outputs','Actual ordinary output identities')['outputs']
                selection=verify_selection(observer.rows,'production-default')
                check(name+' exact ordinary mode without diagnostic flags',selection['actualModeSelectionGate'],command=[packet['binary']],selection=selection)
                check(name+' actual reviewed backend and mapped frozen material',any(r.get('event')=='backendObserved' and r.get('reviewed') is True and r.get('mappedMaterialMatches') is True for r in observer.rows))
                return observer,outputs
            def interior(observer,token,outputs):
                def current():
                    session.guard()
                    if observer.read_failure or observer.process.poll() is not None:raise RuntimeError('Actual renderer drain/lifetime failed')
                    with observer.lock:
                        if any(r.get('event') in ('fatal','rejected') for r in observer.rows):raise RuntimeError('Actual ordinary renderer refused')
                        latest={r['output']:r for r in observer.rows if r.get('event')=='presented' and r.get('accepted') is True and r.get('token')==token}
                    return latest if set(latest)=={o['name'] for o in outputs} and all(0<r['progress']<1 for r in latest.values()) else None
                return wait(current,'Actual interior presentation on every output')
            observer,outputs=launch('mixed')
            tokens=['abcdef123456-'+str(i) for i in range(1,4)]
            observer.send(command='seed',token=tokens[0],operation='minimize',durationMs=220,members=captured,outputs=[{k:o[k] for k in ('name','generation')} for o in outputs])
            observer.find(lambda r:r.get('event')=='seeded','Actual immutable seed')
            observer.send(command='validate',token=tokens[0],identities=ids)
            observer.find(lambda r:r.get('event')=='ready','Actual complete presented readiness')
            observer.send(command='start',token=tokens[0],identities=ids)
            interior(observer,tokens[0],outputs)
            observer.send(command='start',token=tokens[0],identities=ids)
            for token,operation in zip(tokens[1:],('restore','minimize')):
                observer.send(command='retarget',token=token,operation=operation,durationMs=220,identities=ids)
                observer.send(command='validate',token=token,identities=ids)
                observer.find(lambda r:r.get('event')=='retargeted' and r.get('token')==token,'Actual common output retarget')
                if token!=tokens[-1]:interior(observer,token,outputs)
            observer.find(lambda r:r.get('event')=='endpoint' and r.get('token')==tokens[-1],'Complete current ordinary endpoint')
            observer.close();observers.remove(observer)
            with observer.lock:events=list(observer.rows)
            audit=verify(events,ids,captured,original=False)
            report['mixedAudit']=audit
            check('Actual mixed output C1 pairs/common duration/one-shot clock',audit['analyticT0Pairs']==4 and len(audit['cadence'])==2 and sum(r.get('event')=='uploaded' for r in events)==3,audit=audit)
            check('Mixed ordinary producer closes normal exact EOF',observer.process.returncode==0 and observer.stdout_eof and not Path('/proc',str(observer.process.pid)).exists())
            reduced,outputs=launch('cancel-delegate')
            reduced.send(command='seed',token=tokens[0],operation='minimize',durationMs=220,members=captured,outputs=[{k:o[k] for k in ('name','generation')} for o in outputs])
            reduced.find(lambda r:r.get('event')=='seeded','Reduced delegate actual seed')
            reduced.send(command='validate',token=tokens[0],identities=ids);reduced.find(lambda r:r.get('event')=='ready','Reduced delegate actual ready')
            reduced.send(command='start',token=tokens[0],identities=ids);interior(reduced,tokens[0],outputs)
            reduced.send(command='cancel',token=tokens[0],identities=ids)
            reduced.find(lambda r:r.get('event')=='cancelled','Actual exact latest token cancellation')
            def cleared():
                reduced.send(command='state',observationId='after-cancel')
                state=reduced.find(lambda r:r.get('event')=='state' and r.get('observationId')=='after-cancel','Actual cancelled state')
                return state if state['transparentCommitCount']>=2 else None
            state=wait(cleared,'Actual transparent layer commits')
            check('Reduced-motion renderer cancel delegate retires active native readiness',not state['active'] and not state['nativeReady'] and not state['nativeEndpoint'] and state['pending']==0,actualState=state,endUserReducedMotionSettingAccepted=False)
        check('All owned producers normal before compositor retirement',not report.get('cleanupFailure'))
        report['result']='pass'
    except BaseException:report['result']='fail';report['error']=traceback.format_exc()
    finally:
        if session:
            report['hostEvidence']=session.evidence
            if session.evidence.get('unexpectedInnerDescendants') or session.evidence.get('remainingDescendants') or session.evidence.get('cleanupErrors') or not session.evidence.get('runtimeGone'):report['result']='fail'
            protocol=(out/'host/hyprland.log').read_text() if (out/'host/hyprland.log').exists() else ''
            archived=list((out/'host/runtime-archive/hypr').glob('*/hyprland.log'))
            archive=archived[0].read_text() if len(archived)==1 else ''
            weston=(out/'host/weston-renderer.log').read_text() if (out/'host/weston-renderer.log').exists() else ''
            forbidden=r'\[libseat\]|DRM Backend failed|Starting the DRM backend|enabling fallbacks|error [0-9]+:|Broken pipe|parent transport failed|xdg_surface[^\n]*never[^\n]*configured'
            report['actualParentBackend']=dict(clean=not re.search(forbidden,protocol+'\n'+archive+'\n'+weston,re.I),mandatorySelected='Private AQ_BACKENDS=wayland: mandatory parent, no DRM or libseat backend' in archive,configureAckObserved='Output WAYLAND-1: configure surface with ' in archive)
            if not all(report['actualParentBackend'].values()):report['result']='fail'
        if before:
            try:
                checks,details=observations.compare(before,out/'main-after')
                report['mainPreservation']=checks;report['mainPreservationDetails']=details
                if not checks or not all(checks.values()):report['result']='fail'
            except BaseException:report['result']='fail';report['mainObserverError']=traceback.format_exc()
        try:exact();report['frozenInputsExact']=True
        except BaseException:report['result']='fail';report['closureError']=traceback.format_exc()
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(result=report['result'],checks=len(report['checks']),reportSHA256=sha(out/'report.json'))))
    return 0 if report['result']=='pass' else 1
if __name__=='__main__':raise SystemExit(main())
