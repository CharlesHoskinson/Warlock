#!/usr/bin/env python3
"""Native modal focus/family acceptance audit, with disposable windows only."""
import json, os, subprocess, tempfile, time
from pathlib import Path

home = Path.home()
report = {'checks': [], 'failures': []}
processes = []
pointer = None
overlay = None
def ctl(*args): return subprocess.check_output(['hyprctl', *args], text=True).strip()
def data(*args): return json.loads(ctl(*args, '-j'))
def wait(fn, label):
    end = time.monotonic() + 5
    while time.monotonic() < end:
        value = fn()
        if value: return value
        time.sleep(.1)
    raise AssertionError(label)
def find(name): return next((w for w in data('clients') if w['title'] == 'Modal QA ' + name and w['pid'] in {p.pid for p in processes}), None)
def dispatch(expr): ctl('dispatch', expr)
def focus(w): dispatch('hl.dsp.focus({window="address:' + w['address'] + '"})')
def move(w, x, y): dispatch(f'hl.dsp.window.move({{x={x},y={y},window="address:{w["address"]}"}})')
def resize(w,x,y): dispatch(f'hl.dsp.window.resize({{x={x},y={y},window="address:{w["address"]}"}})')
def check(name, passed, **details):
    report['checks'].append(dict(name=name, passed=bool(passed), **details))
    if not passed: report['failures'].append(name)
initial = data('activewindow'); cursor = data('cursorpos')
desktop_state = Path(os.getenv('XDG_CONFIG_HOME',str(home/'.config')))/'omarchy/virtual-desktops.json'
desktop_state.parent.mkdir(parents=True,exist_ok=True)
saved_desktops = desktop_state.read_bytes() if desktop_state.exists() else None
with tempfile.TemporaryDirectory(prefix='modal-family-qa-') as directory:
    tmp = Path(directory); control=tmp/'control'; logs={m:tmp/(m+'.jsonl') for m in ['family', 'peer']}
    def events(mode): return [json.loads(line) for line in logs[mode].read_text().splitlines()] if logs[mode].exists() else []
    try:
        pointer=subprocess.Popen([str(home/'.local/share/hypr-window-controls/qa/virtual-pointer'),os.getenv('MODAL_POINTER_WIDTH','1600'),'1000'],stdin=subprocess.PIPE,text=True,stdout=subprocess.DEVNULL)
        for mode in ['family', 'peer']:
            processes.append(subprocess.Popen(['python3',str(home/'window-integration-qa/modal_probe_gtk.py'),mode,str(control),str(logs[mode])],stdout=subprocess.DEVNULL,stderr=(tmp/'errors').open('a')))
        owner=wait(lambda:find('owner'),'owner created'); peer=wait(lambda:find('peer'),'peer created')
        resize(owner,580,380);resize(peer,380,300)
        move(owner,120,250);move(peer,1020,400);focus(owner)
        dispatch('hl.dsp.window.alter_zorder({mode="top",window="address:'+owner['address']+'"})');time.sleep(.5)
        control.write_text('open');child=wait(lambda:find('child'),'modal child created');move(child,330,360);time.sleep(.5)
        report['platform']='XWayland' if child.get('xwayland') else 'Wayland'
        report['nativeFamilies']=[w for w in json.loads(ctl('repl','print(hl.plugin.hyprbars.window_families())')) if w.get('pid')==child['pid']]
        def click(x,y):
            pointer.stdin.write(f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 100\nbutton 272 0\nsleep 200\n');pointer.stdin.flush();time.sleep(.5)
        click(1150,550)
        check('unrelated app remains clickable with modal open',data('activewindow').get('address')==peer['address'] and any(e.get('event')=='click' for e in events('peer')),active=data('activewindow').get('title'))
        focus(child)
        dispatch('hl.dsp.window.alter_zorder({mode="top",window="address:'+owner['address']+'"})')
        dispatch('hl.dsp.window.alter_zorder({mode="top",window="address:'+child['address']+'"})');time.sleep(.3)
        report['beforeOwnerClick']={n:find(n) for n in ['owner','child','peer']}
        click(180,540)
        report['afterOwnerClick']={'cursor':data('cursorpos'),'active':data('activewindow'),'clientOrder':[w['address'] for w in data('clients')]}
        check('owner interaction redirects to modal',data('activewindow').get('address')==child['address'] and not any(e.get('event')=='click' and e.get('window')=='owner' for e in events('family')),active=data('activewindow').get('title'))
        focus(peer);click(180,238)
        check('disabled owner titlebar focuses modal without starting drag',data('activewindow').get('address')==child['address'])
        click(470,450)
        check('modal child receives its own click',any(e.get('event')=='click' and e.get('window')=='child' for e in events('family')) and data('activewindow').get('address')==child['address'])
        focus(peer);focus(owner)
        check('programmatic owner focus redirects to child',data('activewindow').get('address')==child['address'])
        order=[w['address'] for w in data('clients')]
        check('activating owner raises family above unrelated peer',order.index(peer['address'])<order.index(owner['address'])<order.index(child['address']),order=order)
        overlay_path=home/'window-integration-qa/ModalOverlayQA.qml'
        overlay=subprocess.Popen(['qs','-p',str(overlay_path)],stdout=subprocess.DEVNULL,stderr=(tmp/'errors').open('a'))
        def overlay_ipc(method):
            return subprocess.run(['qs','-p',str(overlay_path),'ipc','call','modalOverlayQA',method],capture_output=True,text=True)
        wait(lambda:overlay_ipc('count').stdout.strip().isdigit(),'overlay IPC ready')
        assert overlay_ipc('openPanel').returncode==0
        time.sleep(.5);report['overlayLayers']=data('layers');click(180,540)
        overlay_count=overlay_ipc('count').stdout.strip()
        check('overlay above disabled owner receives its own click',overlay_count=='1' and data('activewindow').get('address')==child['address'],count=overlay_count,active=data('activewindow').get('title'))
        assert overlay_ipc('closePanel').returncode==0;time.sleep(.3)
        focus(peer)
        pointer.stdin.write('move 180 540\nsleep 300\n');pointer.stdin.flush();time.sleep(.4)
        check('hovering disabled owner preserves unrelated keyboard focus',data('activewindow').get('address')==peer['address'])
        pointer.stdin.write('button 272 1\nsleep 200\n');pointer.stdin.flush();time.sleep(.3)
        control.write_text('close');wait(lambda:not find('child'),'modal closed while owner button held')
        pointer.stdin.write('button 272 0\nsleep 200\n');pointer.stdin.flush();time.sleep(.3)
        check('consumed owner release stays consumed after dialog closes',not any(e.get('event')=='click' and e.get('window')=='owner' for e in events('family')))
        click(180,540)
        check('owner becomes interactive after dialog closes',any(e.get('event')=='click' and e.get('window')=='owner' for e in events('family')) and data('activewindow').get('address')==owner['address'])
        control.write_text('open');child=wait(lambda:find('child'),'modal reopened');move(child,330,360);time.sleep(.4)
        subprocess.run([str(home/'.local/bin/hypr-windowctl'),'minimize',owner['address']],check=True);time.sleep(.4)
        check('minimizing owner hides modal family',all(find(n)['workspace']['name']=='special:win-minimized' for n in ['owner','child']),workspaces={n:find(n)['workspace']['name'] for n in ['owner','child']})
        subprocess.run([str(home/'.local/bin/hypr-windowctl'),'restore',owner['address']],check=True);time.sleep(.4)
        check('restoring owner focuses modal',data('activewindow').get('address')==child['address'] and find('owner')['workspace']['name']==find('child')['workspace']['name'],active=data('activewindow').get('title'))
        # Desktop action is reversible; preserve the user's catalog byte for byte.
        output=json.loads(subprocess.check_output([str(home/'.local/bin/hypr-desktops'),'new-move',owner['address']],text=True))
        time.sleep(.4)
        check('desktop move keeps modal with owner',find('owner')['workspace']['name']==find('child')['workspace']['name'],workspaces={n:find(n)['workspace']['name'] for n in ['owner','child']})
        report['desktopAction']=output
        report['gtkEvents']={m:events(m) for m in logs}
        report['result']='pass' if not report['failures'] else 'fail'
    except Exception as error:
        report['result']='fail';report['error']=repr(error)
    finally:
        report['gtkErrors']=(tmp/'errors').read_text()
        if pointer:
            pointer.stdin.close();pointer.wait(timeout=3)
        if overlay:
            overlay.terminate()
            try:overlay.wait(timeout=3)
            except subprocess.TimeoutExpired:overlay.kill();overlay.wait()
        for p in processes:
            p.terminate()
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        if saved_desktops is not None:desktop_state.write_bytes(saved_desktops)
        else:desktop_state.unlink(missing_ok=True)
        live={w['address'] for w in data('clients')};runtime=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr-windowctl'
        for sidecar in runtime.glob('*.monitor.json'):
            try:
                if json.loads(sidecar.read_text()).get('pid') in {p.pid for p in processes} and sidecar.name.removesuffix('.monitor.json') not in live:
                    runtime.joinpath(sidecar.name.removesuffix('.monitor.json')).unlink(missing_ok=True);sidecar.unlink()
            except (OSError,ValueError):pass
        if initial.get('workspace',{}).get('name','').isdigit():dispatch('hl.dsp.focus({workspace="'+initial['workspace']['name']+'"})')
        if initial.get('address'):focus(initial)
        dispatch(f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
        Path(os.getenv('MODAL_QA_REPORT',str(home/'.cache/window-modal-family-qa.json'))).write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert report['result']=='pass'
