#!/usr/bin/env python3
"""Private Wayland compositor/bus smoke, preserving the main a11y socket."""
import json,os,signal,socket,subprocess,tempfile,time,sys
from pathlib import Path
H=Path.home();HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from qa_launch import require_qa_scope,owned_runtime,nested_env,verify_parent
require_qa_scope()
def a11y():
    p=Path('/run/user')/str(os.getuid())/'at-spi/bus_0'
    identity=[p.stat().st_dev,p.stat().st_ino] if p.exists() else None
    connected=False
    if identity:
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
            s.settimeout(.2)
            try:s.connect(str(p));connected=True
            except OSError:pass
    return {'identity':identity,'connects':connected}
def outer(*a):return subprocess.check_output(['hyprctl',*a],text=True).strip()
initial=json.loads(outer('activewindow','-j'));pointer=json.loads(outer('cursorpos','-j'));before=a11y()
report={'checks':{},'mainA11yBefore':before};compositor=None;app=None;loaded=False
with owned_runtime() as temp:
    runtime=Path(temp);runtime.chmod(0o700)
    config=runtime/'nested.lua';config.write_text((HERE.parent/'motion-probe/nested.lua').read_text())
    env,parent_identity=nested_env(dict(os.environ),runtime)
    report['parent']=parent_identity
    env['XDG_CONFIG_HOME']=str(runtime/'config')
    for name in ('DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','HYPRLAND_INSTANCE_SIGNATURE','DISPLAY','SESSION_MANAGER'):env.pop(name,None)
    try:
        with (H/'.cache/window-content-probe-nested.log').open('w') as log:
            assert verify_parent(env)==parent_identity,'parent changed before launch'
            compositor=subprocess.Popen(['dbus-run-session','--','Hyprland','--config',str(config)],env=env,start_new_session=True,stdout=log,stderr=subprocess.STDOUT)
        until=time.monotonic()+12;instance=None
        while time.monotonic()<until:
            try:
                instances=json.loads(subprocess.check_output(['hyprctl','instances','-j'],env=env,text=True,stderr=subprocess.DEVNULL))
                instance=next((i for i in instances if str(config).encode() in Path(f'/proc/{i["pid"]}/cmdline').read_bytes()),None)
            except (OSError,ValueError,subprocess.SubprocessError):pass
            if instance:break
            assert compositor.poll() is None,'isolated compositor exited'
            time.sleep(.1)
        assert instance,'isolated compositor timeout'
        nested=dict(env,HYPRLAND_INSTANCE_SIGNATURE=instance['instance'],WAYLAND_DISPLAY=instance['wl_socket'])
        def ctl(*a):return subprocess.check_output(['hyprctl',*a],env=nested,text=True).strip()
        lib=str(HERE/'content-probe-v3.so');assert ctl('plugin','load',lib)=='ok';loaded=True
        # GTK's a11y bridge connects to the isolated compositor's private bus,
        # discovered from its inherited child environment; no outer bus import.
        private_env={}
        for item in Path(f'/proc/{instance["pid"]}/environ').read_bytes().split(b'\0'):
            if b'=' in item:
                key,value=item.split(b'=',1)
                if key==b'DBUS_SESSION_BUS_ADDRESS':private_env[key.decode()]=value.decode()
        assert private_env.get('DBUS_SESSION_BUS_ADDRESS'),'private bus env missing'
        nested.update(private_env)
        app=subprocess.Popen(['python3',str(HERE/'gtk.py')],env=nested,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        w=None
        for _ in range(80):
            w=next((w for w in json.loads(ctl('clients','-j')) if w['pid']==app.pid),None)
            if w:break
            time.sleep(.1)
        assert w,'GTK map timeout'
        assert json.loads(ctl('contentprobe','start',w['address'],str(app.pid)))['active']
        time.sleep(2);raw=json.loads(ctl('contentprobe','stop'))
        report['checks'].update({'bounded':not raw['overflow'],'contentCommits':len(raw['contentCommits'])>=20,
                                'frames':len(raw['frames'])>=20,'presentationFeedback':bool(raw['presentations']),
                                'stalePID':bool(json.loads(ctl('contentprobe','start',w['address'],str(app.pid+1))).get('error'))})
        assert ctl('plugin','unload',lib)=='ok';loaded=False;report['checks']['unload']=True
        report['raw']=raw
    except Exception as error:report['error']=repr(error)
    finally:
        if app:
            app.terminate()
            try:app.wait(timeout=5)
            except subprocess.TimeoutExpired:app.kill();app.wait()
        if loaded:
            try:ctl('plugin','unload',lib)
            except subprocess.SubprocessError:pass
        if compositor:
            try:os.killpg(compositor.pid,signal.SIGTERM)
            except ProcessLookupError:pass
            try:compositor.wait(timeout=6)
            except subprocess.TimeoutExpired:os.killpg(compositor.pid,signal.SIGKILL);compositor.wait()
        # Observe the main desktop; do not restore a stale user focus/cursor.
        report['mainFocusAfter']=json.loads(outer('activewindow','-j'))
        report['mainCursorAfter']=json.loads(outer('cursorpos','-j'))
report['mainA11yAfter']=a11y();report['checks']['mainA11yUnchanged']=report['mainA11yAfter']==before
report['result']='pass' if not report.get('error') and all(report['checks'].values()) else 'fail'
(H/'.cache/window-content-probe-smoke.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='raw'},indent=2));assert report['result']=='pass'
