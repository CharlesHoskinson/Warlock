#!/usr/bin/env python3
"""Restart only reviewed attention daemon; no compositor/window/input actions."""
import argparse,datetime,hashlib,json,os,signal,socket,subprocess,time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
HELPER=Path.home()/'.local/bin/hypr-taskbar-attention'
EXPECTED_PID=2470611
EXPECTED_START=4836508
SIGNATURE='efb50993780079460b0cbed1363e2166a2de1d9f_1790777558_556595558'
FIXED_HASH='b544917f44fcc4786fcc0b4eca922bbc4c3df00b9b4b1f92a220d4c6fcb10b5e'
RUNTIME=Path('/run/user/1000')
CATALOG=[Path.home()/'.config/omarchy'/name for name in ('virtual-desktops.json','taskbar-settings.json','taskbar-order.json','taskbar-session-order.json')]

def process_identity(pid):
    proc=Path('/proc')/str(pid)
    args=[arg.decode() for arg in proc.joinpath('cmdline').read_bytes().split(b'\0') if arg]
    env=dict(arg.decode().split('=',1) for arg in proc.joinpath('environ').read_bytes().split(b'\0') if b'=' in arg)
    fields=proc.joinpath('stat').read_text().split()
    return {'pid':pid,'cmdline':args,'parent':int(fields[3]),'startTick':int(fields[21]),'state':fields[2],
        'signature':env.get('HYPRLAND_INSTANCE_SIGNATURE'),'runtime':env.get('XDG_RUNTIME_DIR')}
def exact_process(pid):
    item=process_identity(pid)
    assert item['cmdline']==['python3',str(HELPER)],item
    assert item['signature']==SIGNATURE and item['runtime']==str(RUNTIME),item
    return item
def ctl(*args):return subprocess.check_output(['hyprctl',*args],text=True,timeout=8).strip()
def query(*args):return json.loads(ctl(*args,'-j'))
def bytes_or_none(path):return path.read_bytes() if path.exists() else None
def digest(path):
    content=bytes_or_none(path);return hashlib.sha256(content).hexdigest() if content is not None else None
def a11y():
    path=RUNTIME/'at-spi/bus_0'
    if not path.exists():return {'exists':False}
    info=path.stat();stream=socket.socket(socket.AF_UNIX);stream.settimeout(1)
    try:stream.connect(str(path));connects=True
    except OSError:connects=False
    finally:stream.close()
    return {'exists':True,'dev':info.st_dev,'inode':info.st_ino,'connects':connects}
def snapshot():
    clients=query('clients')
    return {'clients':sorted([{'address':w['address'],'pid':w.get('pid'),'stableId':w.get('stableId'),'at':w.get('at'),'size':w.get('size'),'workspace':w.get('workspace'),'pinned':w.get('pinned'),'fullscreen':w.get('fullscreen')} for w in clients],key=lambda w:w['address']),
        'focus':query('activewindow').get('address'),'cursor':query('cursorpos'),'monitors':query('monitors'),
        'catalogHashes':{str(path):digest(path) for path in CATALOG},'a11y':a11y(),
        'launcherCacheHash':digest(RUNTIME/'hypr-taskbar-launcher.json')}
def find_new():
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name)==EXPECTED_PID:continue
        try:
            item=process_identity(int(proc.name))
            if item['cmdline']==['python3',str(HELPER)] and item['runtime']==str(RUNTIME) and item['signature']==SIGNATURE and item['state']!='Z':return item
        except (OSError,ValueError,UnicodeError):pass
    return None
def wait(fn,label):
    end=time.monotonic()+5
    while time.monotonic()<end:
        result=fn()
        if result:return result
        time.sleep(.05)
    raise AssertionError(label)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:print('Prepared only; no install, termination, launch or input action.');return
    report=json.loads((ROOT/'deployment-report.json').read_text())
    assert os.getenv('HYPRLAND_INSTANCE_SIGNATURE')==SIGNATURE
    assert hashlib.sha256(HELPER.read_bytes()).hexdigest()==FIXED_HASH
    old=exact_process(EXPECTED_PID)
    assert old['startTick']==EXPECTED_START and old['parent']==1468
    before=snapshot();report['beforeRestart']=before;report['oldDaemonIdentity']=old
    state_path=RUNTIME/'hypr-taskbar-attention.json';backup=ROOT/'attention-runtime.before-instance-selection.json'
    assert not backup.exists(),'Do not overwrite runtime backup'
    contents=bytes_or_none(state_path)
    if contents is not None:backup.write_bytes(contents)
    report['runtimeStateBackup']=str(backup) if contents is not None else None
    report['runtimeStateBefore']=json.loads(contents) if contents is not None else None
    (ROOT/'deployment-report.json').write_text(json.dumps(report,indent=2))
    try:
        # Recheck identity immediately before the only termination operation.
        descriptor=os.pidfd_open(EXPECTED_PID)
        try:
            assert exact_process(EXPECTED_PID)['startTick']==EXPECTED_START
            signal.pidfd_send_signal(descriptor,signal.SIGTERM)
        finally:os.close(descriptor)
        def old_exited():
            try:return process_identity(EXPECTED_PID)['state']=='Z'
            except FileNotFoundError:return True
        wait(old_exited,'reviewed old daemon exits')
        report['launchCommand']=['hyprctl','eval',f'hl.exec_cmd({json.dumps(str(HELPER))})']
        report['launchResult']=ctl('eval',f'hl.exec_cmd({json.dumps(str(HELPER))})')
        new=wait(find_new,'new exact main attention daemon appears')
        # The socket connects immediately after lock/state creation.
        time.sleep(.25);new=exact_process(new['pid'])
        report['newDaemonIdentity']=new
        report['newDaemonSocketFDs']=[os.readlink(path) for path in (Path('/proc')/str(new['pid'])/'fd').iterdir() if os.readlink(path).startswith('socket:')]
        report['expectedEventSocket']=str(RUNTIME/'hypr'/SIGNATURE/'.socket2.sock')
        report['querySignature']=new['signature']
        after=snapshot();report['afterRestart']=after
        report['preservation']={name:before[name]==after[name] for name in ('clients','focus','cursor','catalogHashes','a11y','launcherCacheHash')}
        def monitors(values):return [{name:m.get(name) for name in ('id','name','width','height','scale','x','y','transform','reserved','activeWorkspace')} for m in values]
        report['preservation']['monitors']=monitors(before['monitors'])==monitors(after['monitors'])
        selected=json.loads(subprocess.check_output(['hyprctl','-i',new['signature'],'clients','-j'],text=True,timeout=8))
        report['selectedQueryClientsMatch']=sorted([w['address'] for w in selected])==sorted([w['address'] for w in before['clients']])
        report['runtimeStateAfter']=json.loads(state_path.read_text())
        report['restartedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        report['status']='installed and restarted; preservation pass' if all(report['preservation'].values()) and report['selectedQueryClientsMatch'] and report['newDaemonSocketFDs'] else 'restart completed; preservation requires review'
    except Exception as error:
        report.update(status='restart failure',error=repr(error));raise
    finally:(ROOT/'deployment-report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({name:report[name] for name in ('status','newDaemonIdentity','querySignature','preservation','selectedQueryClientsMatch','runtimeStateBackup')},indent=2))
    assert report['status']=='installed and restarted; preservation pass'

if __name__=='__main__':main()
