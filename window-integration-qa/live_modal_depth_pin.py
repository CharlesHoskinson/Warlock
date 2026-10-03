#!/usr/bin/env python3
"""Disposable native nested/pinned modal family acceptance audit."""
import json, os, subprocess, tempfile, time
from pathlib import Path
home=Path.home();report={'checks':[],'failures':[]};processes=[];pointer=None
def ctl(*args):return subprocess.check_output(['hyprctl',*args],text=True).strip()
def data(*args):return json.loads(ctl(*args,'-j'))
def wait(fn,label):
    end=time.monotonic()+5
    while time.monotonic()<end:
        value=fn()
        if value:return value
        time.sleep(.1)
    raise AssertionError(label)
def check(name,value,**details):
    report['checks'].append(dict(name=name,passed=bool(value),**details))
    if not value:report['failures'].append(name)
def focus(window):ctl('dispatch',f'hl.dsp.focus({{window="address:{window["address"]}"}})')
def arrange(window,x,y,width,height):
    ctl('dispatch',f'hl.dsp.window.resize({{x={width},y={height},window="address:{window["address"]}"}})')
    ctl('dispatch',f'hl.dsp.window.move({{x={x},y={y},window="address:{window["address"]}"}})')
def raise_window(window):ctl('dispatch',f'hl.dsp.window.alter_zorder({{mode="top",window="address:{window["address"]}"}})')
def op(command,window):subprocess.run([str(home/'.local/bin/hypr-windowctl'),command,window['address']],check=True)
def pin(window):subprocess.run([str(home/'.local/bin/hypr-pin-toggle'),window['address']],check=True);time.sleep(.4)
initial=data('activewindow');cursor=data('cursorpos');catalog=Path(os.getenv('XDG_CONFIG_HOME',str(home/'.config')))/'omarchy/virtual-desktops.json';saved=catalog.read_bytes() if catalog.exists() else None
with tempfile.TemporaryDirectory(prefix='modal-depth-pin-qa-') as directory:
    tmp=Path(directory);control=tmp/'control';logs={m:tmp/(m+'.jsonl') for m in ['family','peer']}
    def find(name):return next((w for w in data('clients') if w['title']=='Modal QA '+name and w['pid'] in {p.pid for p in processes}),None)
    def events(mode):return [json.loads(l) for l in logs[mode].read_text().splitlines()] if logs[mode].exists() else []
    def count(name):return sum(e.get('event')=='click' and e.get('window')==name for e in events('family'))
    def click(x,y):
        pointer.stdin.write(f'move {x} {y}\nsleep 120\nbutton 272 1\nsleep 100\nbutton 272 0\nsleep 180\n');pointer.stdin.flush();time.sleep(.5)
    try:
        pointer=subprocess.Popen([str(home/'.local/share/hypr-window-controls/qa/virtual-pointer'),os.getenv('MODAL_POINTER_WIDTH','1600'),'1000'],stdin=subprocess.PIPE,text=True,stdout=subprocess.DEVNULL)
        for mode in logs:
            processes.append(subprocess.Popen(['python3',str(home/'window-integration-qa/modal_probe_gtk.py'),mode,str(control),str(logs[mode])],stdout=subprocess.DEVNULL,stderr=(tmp/'errors').open('a')))
        owner=wait(lambda:find('owner'),'owner');peer=wait(lambda:find('peer'),'peer')
        arrange(owner,120,250,580,380);arrange(peer,1020,400,380,300);raise_window(owner)
        control.write_text('open');child=wait(lambda:find('child'),'child');arrange(child,330,360,320,180);time.sleep(.5)
        report['platform']='XWayland' if child.get('xwayland') else 'Wayland'
        pin(owner);focus(peer);time.sleep(.3)
        order_before=[w['address'] for w in data('clients')]
        check('pinned owner stays below its dialog after unrelated focus',order_before.index(owner['address'])<order_before.index(child['address']))
        before=count('child');click(470,450)
        check('dialog above pinned owner remains clickable',count('child')==before+1 and data('activewindow').get('address')==child['address'],order=[w['title'] for w in data('clients')],pins={n:find(n)['pinned'] for n in ['owner','child']})
        op('minimize',owner);op('restore',owner);time.sleep(.4)
        before=count('child');click(470,450)
        check('pinned family restore keeps dialog clickable',find('owner')['pinned'] and count('child')==before+1 and data('activewindow').get('address')==child['address'])
        control.write_text('close');wait(lambda:not find('child'),'child closed under pinned owner')
        control.write_text('open');child=wait(lambda:find('child'),'new modal under pinned owner');arrange(child,330,360,320,180);time.sleep(.4)
        before=count('child');click(470,450)
        families=json.loads(ctl('repl','print(hl.plugin.hyprbars.window_families())'))
        check('dialog opened after pinning remains clickable',find('owner')['pinned'] and count('child')==before+1 and data('activewindow').get('address')==child['address'],owner=find('owner'),child=find('child'),active=data('activewindow').get('title'),before=before,after=count('child'),nativeFamilies=families)
        pin(owner);control.write_text('nested');nested=wait(lambda:find('nested'),'nested');arrange(nested,400,390,240,140);time.sleep(.5)
        child_before_nested=count('child')
        pin(owner)
        focus(peer);raise_window(owner);raise_window(child);raise_window(nested);click(180,540)
        check('owner click focuses deepest modal',data('activewindow').get('address')==nested['address'])
        click(350,380)
        check('intermediate dialog click focuses deepest modal',data('activewindow').get('address')==nested['address'] and count('child')==child_before_nested)
        before_nested=count('nested');click(470,450)
        check('deepest dialog receives its own click',count('nested')==before_nested+1)
        op('minimize',child)
        check('minimizing intermediate dialog hides whole family',all(find(n)['workspace']['name']=='special:win-minimized' for n in ['owner','child','nested']))
        op('restore',owner);time.sleep(.4)
        check('nested family restore focuses deepest modal',data('activewindow').get('address')==nested['address'] and len({find(n)['workspace']['name'] for n in ['owner','child','nested']})==1)
        before_nested=count('nested');click(470,450)
        check('nested family restore keeps deepest dialog clickable',count('nested')==before_nested+1)
        control.write_text('close_nested');wait(lambda:not find('nested'),'nested closed');focus(owner)
        before=count('child');click(470,450)
        check('closing deepest dialog returns input to surviving modal',data('activewindow').get('address')==child['address'] and count('child')==before+1)
        report['result']='pass' if not report['failures'] else 'fail'
    except Exception as error:report['result']='fail';report['error']=repr(error)
    finally:
        report['events']={m:events(m) for m in logs};report['gtkErrors']=(tmp/'errors').read_text()
        if pointer:pointer.stdin.close();pointer.wait(timeout=3)
        for p in processes:
            p.terminate()
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        if saved is not None:catalog.write_bytes(saved)
        live={w['address'] for w in data('clients')};runtime=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr-windowctl'
        for sidecar in runtime.glob('*.monitor.json'):
            try:
                if json.loads(sidecar.read_text()).get('pid') in {p.pid for p in processes} and sidecar.name.removesuffix('.monitor.json') not in live:
                    runtime.joinpath(sidecar.name.removesuffix('.monitor.json')).unlink(missing_ok=True);sidecar.unlink()
            except (OSError,ValueError):pass
        if initial.get('address'):focus(initial)
        ctl('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
        Path(os.getenv('MODAL_DEPTH_REPORT',str(home/'.cache/window-modal-depth-pin-qa.json'))).write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));assert report['result']=='pass'
