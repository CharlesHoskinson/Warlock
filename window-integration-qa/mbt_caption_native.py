#!/usr/bin/env python3
"""Replay caption Quint traces against a dedicated nested native compositor.

Projection covers caption identity and rectangles. Snap is installed with the
model's rectangle/normal-size precondition; rehydration after Lua reload keeps
this projection independent of the separately tested persistence backend.
Motion spacing avoids invoking the independently audited titlebar Shake gesture.
"""
import json, os, subprocess, sys, time
from pathlib import Path
H=Path.home();sys.path.insert(0,str(H/'window-behavior-spec'))
from mbt_desktop import decode
report={'traces':[],'checkedStates':0,'events':{},'activeMotions':0};processes={};pointer=None

def ctl(*args):return subprocess.check_output(['hyprctl',*args],text=True).strip()
def data(*args):return json.loads(ctl(*args,'-j'))
def wait(fn,label):
    end=time.monotonic()+5
    while time.monotonic()<end:
        value=fn()
        if value:return value
        time.sleep(.05)
    raise AssertionError(label)
def send(command,pause=.08):pointer.stdin.write(command+'\nsleep 30\n');pointer.stdin.flush();time.sleep(pause)
def live(id):return next(w for w in data('clients') if id in processes and w['pid']==processes[id].pid)
def focus(id):ctl('dispatch',f'hl.dsp.focus({{window="address:{live(id)["address"]}"}})')
def box(id):w=live(id);return w['at']+w['size']
def expected(s,id):b=s['boxes'][id];return [10*b[k] for k in ['x','y','w','h']]
def arrange(id,rect):
    address=live(id)['address'];x,y,w,h=rect
    ctl('dispatch',f'hl.dsp.window.resize({{x={w},y={h},window="address:{address}"}})')
    ctl('dispatch',f'hl.dsp.window.move({{x={x},y={y},window="address:{address}"}})')
def launch(id,s):
    p=subprocess.Popen(['foot','--app-id=caption-model-replay','--title=Caption model '+str(id),'sleep','300'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);processes[id]=p
    wait(lambda:next((w for w in data('clients') if w['pid']==p.pid),None),'foot map')
    arrange(id,expected(s,id))
def close(id):
    p=processes.pop(id,None)
    if p:
        p.terminate()
        try:p.wait(timeout=3)
        except subprocess.TimeoutExpired:p.kill();p.wait()
def hydrate(id):
    if live(id)['size']==[800,960]:ctl('eval',f'hypr_snap_hydrate("{live(id)["address"]}",600,350,260,300,"left")')
instances=data('instances');signature=os.environ['HYPRLAND_INSTANCE_SIGNATURE'];instance=next(i for i in instances if i['instance']==signature)
assert b'window-integration-qa/nested_caption.lua' in Path(f'/proc/{instance["pid"]}/cmdline').read_bytes(),'dedicated compositor required'
paths=sorted((H/'window-behavior-spec/qa-traces').glob('caption-native-*.itf.json'));assert paths
try:
    ctl('dispatch','hl.dsp.focus({monitor="DRAG-QA"})')
    pointer=subprocess.Popen([str(H/'.local/share/hypr-window-controls/qa/virtual-pointer'),'2880','1000'],stdin=subprocess.PIPE,text=True,stdout=subprocess.DEVNULL)
    for path in paths:
        send('button 272 0');send('move 900 150')
        for id in list(processes):close(id)
        states=[decode(s) for s in json.loads(path.read_text())['states']]
        for id in states[0]['alive']:launch(id,states[0])
        focus(1);checked=0;lastMotion=0
        for index,s in enumerate(states):
            if index:
                previous=states[index-1];e=s['last'];tag=e['tag'];value=e.get('value');report['events'][tag]=report['events'].get(tag,0)+1
                if tag=='Press':
                    id=value['id'];focus(id);ctl('dispatch',f'hl.dsp.window.alter_zorder({{mode="top",window="address:{live(id)["address"]}"}})')
                    send(f'move {10*s["press"]["x"]} {10*s["press"]["y"]}');send('button 272 1')
                elif tag=='Motion':
                    if previous['phase']:
                        # This contract concerns pointer anchoring; a slow move
                        # prevents the same trace from becoming a Shake gesture.
                        remaining=1.35-(time.monotonic()-lastMotion)
                        if remaining>0:time.sleep(remaining)
                        report['activeMotions']+=1;lastMotion=time.monotonic()
                    send(f'move {10*value["point"]["x"]} {10*value["point"]["y"]}')
                elif tag=='Release':send('button 272 0')
                elif tag=='Focus':
                    if value in processes:focus(value)
                elif tag=='Cancel':subprocess.run(['wtype','-k','Escape'],check=True);time.sleep(.1)
                elif tag=='Reload':
                    ctl('reload');assert not ctl('configerrors')
                    for id in s['alive']:hydrate(id)
                elif tag=='Close':close(value)
                elif tag=='Open':
                    if value not in processes:launch(value,s)
                elif tag=='Snap':
                    id=value;ctl('eval',f'hypr_snap_restore("{live(id)["address"]}")');arrange(id,expected(s,id));hydrate(id)
                else:raise AssertionError(tag)
            for id in s['alive']:
                actual=box(id);wanted=expected(s,id)
                assert actual==wanted,(path.name,index,s['last'],id,actual,wanted)
            checked+=1;report['checkedStates']+=1
        report['traces'].append(dict(name=path.name,states=checked));print(path.name,checked,'PASS',flush=True)
    report['result']='pass'
except Exception as error:report['result']='fail';report['error']=repr(error)
finally:
    if pointer:pointer.stdin.close();pointer.wait(timeout=3)
    for id in list(processes):close(id)
    (H/'.cache/window-caption-native-mbt-qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));assert report['result']=='pass'
