#!/usr/bin/env python3
"""Live QML/task-switcher scope QA on disposable windows; restores settings."""
import json
import subprocess
import time
from pathlib import Path

BIN=Path.home()/'.local/bin'
CONTROLS=Path.home()/'.local/share/hypr-window-controls'
SETTINGS=Path.home()/'.config/omarchy/taskbar-settings.json'
report={'checks':[]}
processes=[]
initial_settings=SETTINGS.read_bytes() if SETTINGS.exists() else None

def ctl(*args):return subprocess.check_output(['hyprctl',*map(str,args)],text=True).strip()
def data(*args):return json.loads(ctl(*args,'-j'))
def ipc(target,method,*args):
    path='/usr/share/omarchy/shell' if target=='hoskinson.windows' else str(CONTROLS)
    return subprocess.check_output(['qs','-p',path,'ipc','call',target,method,*map(str,args)],text=True).strip()
def wait(fn,label):
    deadline=time.monotonic()+7
    while time.monotonic()<deadline:
        result=fn()
        if result:return result
        time.sleep(.15)
    raise AssertionError(label)
def focus(address):ctl('dispatch',f'hl.dsp.focus({{window="address:{address}"}})')
def launch(title,workspace):
    p=subprocess.Popen(['foot','--app-id=window-parity-scope-qa','--title='+title,'sleep','180'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    processes.append(p)
    window=wait(lambda:next((w for w in data('clients') if w['pid']==p.pid),None),'foot create')
    ctl('dispatch',f'hl.dsp.window.move({{workspace="{workspace}",follow=false,window="address:{window["address"]}"}})')
    return window['address']
def config(key,value):subprocess.run([str(BIN/'hypr-taskbar'),'config',key,value],check=True)
def shown():return {address for g in json.loads(ipc('hoskinson.windows','state'))['indicators'] for address in g['windows']}
def switcher(scope):
    config('switcherScope',scope)
    subprocess.run([str(BIN/'hypr-window-menu'),'switcher'],check=True)
    state=wait(lambda:json.loads(ipc('controls','state')) if json.loads(ipc('controls','state')).get('opened') else None,'switcher open')
    addresses={c['address'] for c in state['request']['candidates']}
    ipc('controls','hide')
    return addresses
initial=data('activewindow');cursor=data('cursorpos')
try:
    assert not any(w['workspace']['name'] in ('987','988') for w in data('clients'))
    a=launch('Scope current QA',987)
    b=launch('Scope foreign QA',988)
    c=launch('Scope minimized foreign QA',988)
    subprocess.run([str(BIN/'hypr-windowctl'),'minimize',c],check=True)
    focus(a)
    config('desktopScope','current')
    visible=wait(lambda:shown() if a in shown() and b not in shown() and c not in shown() else None,'taskbar current scope')
    report['checks'].append({'name':'taskbar current excludes foreign visible/minimized','addresses':sorted(visible)})
    config('desktopScope','all')
    visible=wait(lambda:shown() if {a,b,c}.issubset(shown()) else None,'taskbar all scope')
    report['checks'].append({'name':'taskbar all includes foreign visible/minimized','addresses':sorted(visible)})
    current=switcher('current')
    assert a in current and b not in current and c not in current,current
    report['checks'].append({'name':'Alt+Tab current scope','addresses':sorted(current)})
    all_desktops=switcher('all')
    assert {a,b,c}.issubset(all_desktops),all_desktops
    report['checks'].append({'name':'Alt+Tab all includes minimized foreign identity','addresses':sorted(all_desktops)})
    statefile=Path('/run/user/1000/hypr-windowctl')/c
    original=statefile.read_text();parts=original.split();parts[-1]='stale-id';statefile.write_text(' '.join(parts)+'\n')
    try:
        assert c not in switcher('all')
        report['checks'].append({'name':'stale minimized identity excluded live'})
    finally:statefile.write_text(original)
    config('switcherScope','all')
    subprocess.run([str(BIN/'hypr-window-menu'),'switcher'],check=True)
    state=json.loads(ipc('controls','state'))
    index=next(i for i,w in enumerate(state['request']['candidates']) if w['address']==b)
    for _ in range((index-state['selected'])%len(state['request']['candidates'])):ipc('controls','cycle',1)
    subprocess.run([str(BIN/'hypr-window-menu'),'switcher-commit'],check=True)
    wait(lambda:data('activewindow').get('address')==b,'all-desktop commit focuses foreign window')
    assert data('activewindow')['workspace']['name']=='988'
    report['checks'].append({'name':'all-desktop commit restores captured identity on foreign desktop'})
    focus(a)
    target=next(w for w in data('clients') if w['address']==b)
    target['pid']+=1
    rejected=subprocess.run([str(BIN/'hypr-window-menu'),'switcher-restore',json.dumps(target)],capture_output=True)
    assert rejected.returncode!=0 and data('activewindow')['address']==a
    report['checks'].append({'name':'stale captured PID cannot focus a different identity'})
    report['result']='pass'
except Exception as error:
    report['result']='fail';report['error']=repr(error)
finally:
    ipc('controls','hide');ipc('hoskinson.windows','dismiss')
    for p in processes:
        p.terminate()
        try:p.wait(timeout=3)
        except subprocess.TimeoutExpired:p.kill();p.wait()
    if initial_settings is None:SETTINGS.unlink(missing_ok=True)
    else:SETTINGS.write_bytes(initial_settings)
    if initial.get('address'):focus(initial['address'])
    ctl('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
    report['remainingQaWindows']=[w for w in data('clients') if w['class']=='window-parity-scope-qa']
    Path.home().joinpath('.cache/window-scope-live-qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert report['result']=='pass'
