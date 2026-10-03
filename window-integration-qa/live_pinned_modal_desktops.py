#!/usr/bin/env python3
"""Pinned native modal families across desktop changes; disposable apps only."""
import json, os, subprocess, tempfile, time
from pathlib import Path
H=Path.home(); report={'checks':[],'failures':[]}; processes=[]; pointer=None; created=[]
def ctl(*args):return subprocess.check_output(['hyprctl',*args],text=True).strip()
def data(name):return json.loads(ctl(name,'-j'))
def backend(*args):return json.loads(subprocess.check_output([str(H/'.local/bin/hypr-desktops'),*map(str,args)],text=True))
def wait(fn,label):
    end=time.monotonic()+6
    while time.monotonic()<end:
        value=fn()
        if value:return value
        time.sleep(.1)
    raise AssertionError(label)
def focus(w):ctl('dispatch',f'hl.dsp.focus({{window="address:{w["address"]}"}})')
def arrange(w,x,y,width,height):
    if not w['floating']:ctl('dispatch',f'hl.dsp.window.float({{action="set",window="address:{w["address"]}"}})')
    ctl('dispatch',f'hl.dsp.window.resize({{x={width},y={height},window="address:{w["address"]}"}})')
    ctl('dispatch',f'hl.dsp.window.move({{x={x},y={y},window="address:{w["address"]}"}})')
def check(name,value,**details):
    report['checks'].append(dict(name=name,passed=bool(value),**details))
    if not value:report['failures'].append(name)
initial=data('activewindow'); cursor=data('cursorpos'); initial_workspace=data('activeworkspace')['name']
initial_ids={w['stableId'] for w in data('clients')}
catalog=Path(os.getenv('XDG_CONFIG_HOME',str(H/'.config')))/'omarchy/virtual-desktops.json'
catalog.parent.mkdir(parents=True,exist_ok=True)
saved=catalog.read_bytes() if catalog.exists() else None
with tempfile.TemporaryDirectory(prefix='pinned-modal-desktops-') as directory:
    tmp=Path(directory); control=tmp/'control'; log=tmp/'family.jsonl'
    def find(name):return next((w for w in data('clients') if w['title']=='Modal QA '+name and w['pid'] in {p.pid for p in processes}),None)
    def clicks(name):return sum(e.get('event')=='click' and e.get('window')==name for e in
        [json.loads(line) for line in log.read_text().splitlines()] if log.exists())
    def click(x,y):
        pointer.stdin.write(f'move {x} {y}\nsleep 150\nbutton 272 1\nsleep 100\nbutton 272 0\nsleep 150\n')
        pointer.stdin.flush();time.sleep(.6)
    try:
        processes.append(subprocess.Popen(['python3',str(H/'window-integration-qa/modal_probe_gtk.py'),'family',str(control),str(log)],
            stdout=subprocess.DEVNULL,stderr=(tmp/'stderr').open('w')))
        owner=wait(lambda:find('owner'),'owner');arrange(owner,120,250,580,380)
        control.write_text('open');child=wait(lambda:find('child'),'child');arrange(child,330,360,320,180)
        control.write_text('nested');nested=wait(lambda:find('nested'),'nested');arrange(nested,400,390,240,140)
        report['platform']='XWayland' if owner.get('xwayland') else 'Wayland'
        subprocess.run([str(H/'.local/bin/hypr-pin-toggle'),owner['address']],check=True,stdout=subprocess.DEVNULL)
        time.sleep(.5)
        pointer=subprocess.Popen([str(H/'.local/share/hypr-window-controls/qa/virtual-pointer'),'1600','1000'],stdin=subprocess.PIPE,text=True,stdout=subprocess.DEVNULL)
        focus(owner);time.sleep(.4)
        before=clicks('nested');click(470,450)
        check('baseline pinned modal input before desktop switch',clicks('nested')==before+1 and data('activewindow').get('stableId')==nested['stableId'],
              geometry={n:find(n) for n in ['owner','child','nested']},active=data('activewindow'),cursor=data('cursorpos'),layers=data('layers'))
        assert report['checks'][-1]['passed'],'baseline native modal input'
        for round in range(2):
            before_ids={d['id'] for d in backend('list')['desktops']}
            backend('new')
            after=backend('list'); new_ids={d['id'] for d in after['desktops']}-before_ids
            assert len(new_ids)==1,after
            desktop=new_ids.pop();created.append(desktop);time.sleep(.5)
            family={name:find(name) for name in ['owner','child','nested']}
            workspaces={name:w['workspace']['name'] for name,w in family.items()}
            check(f'family shares active desktop after switch {round}',len(set(workspaces.values()))==1 and
                  next(iter(workspaces.values()))==str(desktop),workspaces=workspaces,desktop=desktop)
            before=clicks('nested');click(470,450)
            check(f'deepest pinned modal receives click after switch {round}',clicks('nested')==before+1 and
                  data('activewindow').get('stableId')==nested['stableId'],active=data('activewindow').get('title'))
            before_owner=clicks('owner');click(180,540)
            check(f'owner remains disabled and routes to modal after switch {round}',clicks('owner')==before_owner and
                  data('activewindow').get('stableId')==nested['stableId'])
        if os.getenv('PINNED_QA_LIBRARY'):
            # Reload repair is isolated: never unload the main user's plugin
            # from this fixture. Reproduce a family already split by v12.
            library=os.environ['PINNED_QA_LIBRARY']
            instance=next(i for i in data('instances') if i['instance']==os.environ['HYPRLAND_INSTANCE_SIGNATURE'])
            assert b'window-integration-qa/nested_pinned.lua' in Path(f'/proc/{instance["pid"]}/cmdline').read_bytes()
            ctl('dispatch',f'hl.dsp.window.move({{workspace="{initial_workspace}",follow=false,window="address:{child["address"]}"}})')
            assert find('child')['workspace']['name']!=find('owner')['workspace']['name'],'split precondition'
            assert ctl('plugin','unload',library)=='ok'
            assert ctl('plugin','load',library)=='ok'
            assert ctl('reload')=='ok' and not ctl('configerrors')
            wait(lambda:all(find(n)['workspace']['name']==str(created[-1]) for n in ['owner','child','nested']),'existing family rehydrated')
            before=clicks('nested');click(470,450)
            check('plugin reload repairs an already split pinned family',clicks('nested')==before+1 and data('activewindow').get('stableId')==nested['stableId'])
        control.write_text('close_nested');wait(lambda:not find('nested'),'old nested closes after switch')
        control.write_text('nested');nested=wait(lambda:find('nested'),'new nested after switch')
        arrange(nested,400,390,240,140);time.sleep(.4)
        before=clicks('nested');click(470,450)
        check('new nested modal after pinned desktop switch receives input',find('nested')['workspace']['name']==str(created[-1]) and
              clicks('nested')==before+1 and data('activewindow').get('stableId')==nested['stableId'])
        backend('switch',initial_workspace);time.sleep(.5)
        before=clicks('nested');click(470,450)
        check('switching back retains modal input',clicks('nested')==before+1 and data('activewindow').get('stableId')==nested['stableId'])
        control.write_text('close_nested');wait(lambda:not find('nested'),'nested closes')
        before=clicks('child');click(470,450)
        check('surviving modal receives input after cross-desktop child close',clicks('child')==before+1 and data('activewindow').get('stableId')==child['stableId'])
        subprocess.run([str(H/'.local/bin/hypr-pin-toggle'),owner['address']],check=True,stdout=subprocess.DEVNULL)
        backend('switch',created[-1]);time.sleep(.4)
        check('unpinning stops family following desktops',not find('owner')['pinned'] and
              all(find(n)['workspace']['name']==initial_workspace for n in ['owner','child']))
        backend('switch',initial_workspace);time.sleep(.4)
        subprocess.run([str(H/'.local/bin/hypr-pin-toggle'),child['address']],check=True,stdout=subprocess.DEVNULL)
        backend('switch',created[-1]);time.sleep(.4)
        before=clicks('child');click(470,450)
        check('pinning a modal carries its parent and retains input',find('child')['pinned'] and not find('owner')['pinned'] and
              all(find(n)['workspace']['name']==str(created[-1]) for n in ['owner','child']) and
              clicks('child')==before+1 and data('activewindow').get('stableId')==child['stableId'])
        report['result']='pass' if not report['failures'] else 'fail'
    except Exception as error:report['result']='fail';report['error']=repr(error)
    finally:
        if pointer:pointer.stdin.close();pointer.wait(timeout=3)
        for p in processes:
            p.terminate()
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        report['gtkEvents']=[json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
        report['stderr']=(tmp/'stderr').read_text() if (tmp/'stderr').exists() else ''
        for desktop in reversed(created):backend('close',desktop)
        if saved is None:catalog.unlink(missing_ok=True)
        else:catalog.write_bytes(saved)
        ctl('dispatch',f'hl.dsp.focus({{workspace="{initial_workspace}"}})')
        live=data('clients');report['originalWindowsPreserved']=initial_ids.issubset({w['stableId'] for w in live})
        if any(w['stableId']==initial.get('stableId') for w in live):focus(initial)
        ctl('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
        Path(os.getenv('PINNED_MODAL_DESKTOP_REPORT',str(H/'.cache/window-pinned-modal-desktops-qa.json'))).write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));assert report['result']=='pass',report['failures']
