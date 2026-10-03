#!/usr/bin/env python3
"""Prepared native compositor restart QA; execute only after root grants a slot.

python3 isolated_restart.py prints its plan without launching a compositor.
python3 isolated_restart.py --execute creates disposable nested windows.
This provides nested restart evidence, never physical hotplug/main restart QA.
"""
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from qa_launch import require_qa_scope,owned_runtime,nested_env,verify_parent,verify_runtime
CONFIG=ROOT/'isolated_restart.lua'
REPORT=ROOT/'isolated-restart-report.json'


def a11y_state():
    path=Path('/run/user')/str(os.getuid())/'at-spi/bus_0'
    try: identity=[path.stat().st_dev,path.stat().st_ino]
    except FileNotFoundError:identity=None
    connects=False
    if identity:
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as stream:
            stream.settimeout(.2)
            try:stream.connect(str(path));connects=True
            except OSError:pass
    return {'identity':identity,'connects':connects}


def wait(predicate,label):
    end=time.monotonic()+10
    while time.monotonic()<end:
        try:
            value=predicate()
            if value:return value
        except (OSError,ValueError,subprocess.SubprocessError):pass
        time.sleep(.05)
    raise AssertionError(label)


if '--execute' not in sys.argv:
    print(json.dumps({'execution':'not started; requires root agent native slot grant',
        'plan':['private runtime/config/D-Bus established before service activation',
                'dedicated AQ_BACKENDS=wayland compositor with disposable Foot pair',
                'record actual snap group, reload/hydrate and exact normal restore',
                'terminate only dedicated compositor and disposable apps',
                'restart same isolated runtime; foreign groups must clear',
                'compare original main clients and a11y socket after cleanup'],
        'limits':['nested lifecycle only','no main restart','no physical hotplug']}))
    sys.exit(0)

if os.environ.get('RESTART_QA_PRIVATE_BUS')!='1':
    require_qa_scope()
    original=json.loads(subprocess.check_output(['hyprctl','clients','-j'],text=True))
    identities={(w['address'],w.get('pid'),w.get('stableId')) for w in original}
    original_focus=json.loads(subprocess.check_output(['hyprctl','activewindow','-j'],text=True))
    original_cursor=json.loads(subprocess.check_output(['hyprctl','cursorpos','-j'],text=True))
    before=a11y_state()
    # Hyprland embeds its long signature in AF_UNIX paths (108-byte limit).
    with owned_runtime() as directory:
        env,parent_identity=nested_env(dict(os.environ),directory)
        env.update(XDG_CONFIG_HOME=directory+'/config',RESTART_QA_PRIVATE_BUS='1',NO_AT_BRIDGE='1',GTK_A11Y='none',HYPR_WINDOWCTL_MOTION='0')
        for name in ['AT_SPI_BUS_ADDRESS','DBUS_SESSION_BUS_ADDRESS','HYPRLAND_INSTANCE_SIGNATURE','DISPLAY','SESSION_MANAGER']:
            env.pop(name,None)
        result=subprocess.run(['dbus-run-session','--',sys.executable,str(Path(__file__).resolve()),'--execute'],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (ROOT/'isolated-restart.log').write_text(result.stdout)
    remaining=json.loads(subprocess.check_output(['hyprctl','clients','-j'],text=True))
    after={(w['address'],w.get('pid'),w.get('stableId')) for w in remaining}
    focus_key=(original_focus.get('address'),original_focus.get('pid'),original_focus.get('stableId'))
    restored_focus=json.loads(subprocess.check_output(['hyprctl','activewindow','-j'],text=True))
    restored_cursor=json.loads(subprocess.check_output(['hyprctl','cursorpos','-j'],text=True))
    report=json.loads(REPORT.read_text()) if REPORT.exists() else {'checks':{},'result':'failed'}
    report['isolation']={'a11yBefore':before,'a11yAfter':a11y_state(),'originalClientIdentities':len(identities),
        'originalFocus':list(focus_key),'restoredFocus':[restored_focus.get('address'),restored_focus.get('pid'),restored_focus.get('stableId')],
        'originalCursor':original_cursor,'restoredCursor':restored_cursor}
    report['checks']['mainClientsPreserved']=identities<=after
    report['checks']['mainA11yUnchanged']=before==report['isolation']['a11yAfter']
    report['checks']['mainFocusPreserved']=list(focus_key)==report['isolation']['restoredFocus']
    report['checks']['mainCursorPreserved']=original_cursor==restored_cursor
    report['result']='pass' if result.returncode==0 and all(report['checks'].values()) else 'failed'
    REPORT.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));sys.exit(result.returncode)

require_qa_scope()
runtime=verify_runtime(os.environ['XDG_RUNTIME_DIR'])
Path(os.environ['XDG_CONFIG_HOME']).mkdir()
base_env=dict(os.environ)
report={'scope':'dedicated nested compositor shutdown/restart, not main restart or physical hotplug','checks':{},'sessions':[]}
compositor=None;apps=[]
def ctl(env,*args):return subprocess.check_output(['hyprctl',*args],env=env,text=True,timeout=5).strip()
def current(env):return json.loads(ctl(env,'clients','-j'))
def start():
    global compositor
    verify_parent(base_env)
    assert base_env['AQ_BACKENDS']=='wayland' and 'AQ_DRM_DEVICES' not in base_env
    with (ROOT/'isolated-compositor.log').open('a') as log:
        compositor=subprocess.Popen(['Hyprland','--config',str(CONFIG)],env=base_env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    def instance():
        rows=json.loads(ctl(base_env,'instances','-j'))
        return next((r for r in rows if r['pid']==compositor.pid),None)
    info=wait(instance,'dedicated compositor startup')
    env=dict(base_env,HYPRLAND_INSTANCE_SIGNATURE=info['instance'],WAYLAND_DISPLAY=info['wl_socket'])
    assert str(CONFIG).encode() in Path(f'/proc/{compositor.pid}/cmdline').read_bytes()
    wait(lambda:ctl(env,'monitors','-j')!='[]','nested output ready')
    assert ctl(env,'reload')=='ok';assert not ctl(env,'configerrors')
    report['sessions'].append({'pid':compositor.pid,'signature':info['instance']})
    return env
def launch(env,name):
    process=subprocess.Popen(['foot','--app-id='+name,'--title='+name,'sleep','120'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True);apps.append(process)
    return wait(lambda:next((w for w in current(env) if w['pid']==process.pid),None),'disposable Foot client')
def group(env,*args):return subprocess.check_output([str(Path.home()/'.local/bin/hypr-snap-groups'),*args],env=env,text=True,timeout=5).strip()
def stop():
    global compositor
    # The connection stays alive while the clients shut down.
    for process in apps:
        if process.poll() is None:
            try:os.killpg(process.pid,signal.SIGTERM)
            except ProcessLookupError:pass
        process.wait(timeout=5)
    apps.clear()
    if compositor and compositor.poll() is None:
        assert str(CONFIG).encode() in Path(f'/proc/{compositor.pid}/cmdline').read_bytes()
        compositor.terminate();compositor.wait(timeout=10)
    compositor=None

try:
    env=start();pair=[launch(env,'recovery-first'),launch(env,'recovery-second')]
    for w,zone,x in zip(pair,['left','right'],[80,650]):
        a=w['address']
        ctl(env,'eval',f'hl.dispatch(hl.dsp.window.resize({{x=420,y=300,window="address:{a}"}}));hl.dispatch(hl.dsp.window.move({{x={x},y=120,window="address:{a}"}}))')
        ctl(env,'eval',f'hypr_snap_zone("{zone}","{a}",false)')
        group(env,'record',a,zone,'420','300',str(x),'120')
    assert len(json.loads(group(env,'list')))==1
    report['checks']['nativeGroupRecorded']=True
    assert ctl(env,'reload')=='ok';assert not ctl(env,'configerrors');group(env,'hydrate')
    assert len(json.loads(group(env,'list')))==1
    a=pair[0]['address'];ctl(env,'eval',f'hypr_snap_restore("{a}")')
    restored=next(w for w in current(env) if w['address']==a)
    assert restored['at']+restored['size']==[80,120,420,300],restored
    report['checks']['sameInstanceReloadHydratesExactNormalRect']=True
    old_tag=json.loads((runtime/'hypr-snap-groups/state.json').read_text())['instance']
    stop();env=start();new_client=launch(env,'recovery-new-session')
    assert old_tag!=env['HYPRLAND_INSTANCE_SIGNATURE']
    assert json.loads(group(env,'list'))==[]
    saved=json.loads((runtime/'hypr-snap-groups/state.json').read_text())
    assert saved['snapped']=={} and saved['instance']==env['HYPRLAND_INSTANCE_SIGNATURE']
    report['checks']['newInstanceClearsForeignGroups']=True
    assert 'win-snapped' not in [t.rstrip('*') for t in new_client.get('tags',[])]
    report['checks']['newClientReceivesNoStaleSnap']=True
    report['result']='pass'
except Exception as error:
    report['error']=repr(error)
    report['result']='failed'
finally:
    stop();REPORT.write_text(json.dumps(report,indent=2))
if report['result']!='pass':sys.exit(1)
