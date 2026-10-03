#!/usr/bin/env python3
"""Exercise the candidate native plugin in an isolated nested compositor."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from qa_nested_target import attach
info,env=attach()
report={'checks':[],'compositorPid':info['pid']}
process=None
def ctl(*args):
    fresh,_=attach()
    assert fresh['descriptorSHA256']==info['descriptorSHA256'],'session descriptor replaced'
    return subprocess.check_output(['hyprctl','-i',info['signature'],*args],env=env,text=True).strip()
def data(*args):return json.loads(ctl(*args,'-j'))
def wait(fn,label):
    deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        result=fn()
        if result:return result
        time.sleep(.1)
    raise AssertionError(label)
def events():
    rows=ctl('repl','for _,e in ipairs(qa_drag_events) do print(e.kind,e.address) end').splitlines()
    return [line.split() for line in rows if line.strip()]
pointer=Path.home()/'.local/share/hypr-window-controls/qa/virtual-pointer'
def inject(text):subprocess.run([str(pointer),'2880','1000'],env=env,input=text,text=True,check=True)
try:
    assert json.loads(ctl('getoption','xwayland:enabled','-j'))['bool'] is False,'drag QA must disable Xwayland'
    old=Path(info.get('pluginPath',str(Path.home()/'src/hyprbars-dragend/hyprbars-v7.so')))
    candidate=Path(sys.argv[1]) if len(sys.argv)>1 else Path.home()/'src/hyprbars-dragend/hyprbars-v7b.so'
    if data('plugin','list'):ctl('plugin','unload',str(old))
    assert ctl('plugin','load',str(candidate))=='ok','candidate load failed'
    info['pluginPath']=str(candidate)
    ctl('reload')
    assert not ctl('configerrors'),ctl('configerrors')
    assert ctl('repl','print(hl.plugin.hyprbars.drag_bridge())')=='true'
    ctl('dispatch','hl.dsp.focus({monitor="DRAG-QA"})')
    process=subprocess.Popen(['foot','--app-id=window-parity-native-bridge-qa','--title=Isolated native drag QA','sleep','180'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    address=wait(lambda:next((w['address'] for w in data('clients') if w['pid']==process.pid),None),'foot create')
    def reset():
        ctl('eval',f'hypr_snap_restore("{address}")')
        ctl('dispatch',f'hl.dsp.window.resize({{x=600,y=350,window="address:{address}"}})')
        ctl('dispatch',f'hl.dsp.window.move({{x=260,y=300,window="address:{address}"}})')
        ctl('dispatch',f'hl.dsp.focus({{window="address:{address}"}})')
        ctl('eval','qa_drag_events={}')
    def current():return next(w for w in data('clients') if w['address']==address)
    def rectangle():return current()['at']+current()['size']
    for modifier in ['logo','alt']:
        reset()
        keyboard=subprocess.Popen(['wtype','-M',modifier,'-s','900','-m',modifier],env=env)
        time.sleep(.15)
        inject('move 460 430\nsleep 100\nbutton 272 1\nsleep 100\nmove 500 440\nsleep 100\nbutton 272 0\nsleep 100\n')
        keyboard.wait(timeout=3)
        observed=events()
        assert observed==[['begin',address],['release',address]],(modifier,observed)
        report['checks'].append(dict(path=modifier,events=observed))
    reset()
    inject('move 460 288\nsleep 100\nbutton 272 1\nsleep 100\nmove 500 310\nsleep 100\nbutton 272 0\nsleep 100\n')
    assert events()==[['begin',address],['release',address]],events()
    report['checks'].append(dict(path='titlebar',events=events()))
    reset()
    keyboard=subprocess.Popen(['wtype','-M','logo','-s','1500','-m','logo'],env=env)
    time.sleep(.15)
    held_pointer=subprocess.Popen([str(pointer),'2880','1000'],env=env,stdin=subprocess.PIPE,text=True)
    try:
        held_pointer.stdin.write('move 460 430\nbutton 272 1\nsleep 100\nmove 500 440\nsleep 100\n')
        held_pointer.stdin.flush()
        time.sleep(.3)
        assert events()==[['begin',address]],('pointer released before cancellation',events())
        subprocess.run(['wtype','-s','150','-k','Escape','-s','250'],env=env,check=True)
        assert events()==[['begin',address],['cancel',address]],events()
        assert rectangle()==[260,300,600,350],('cancel did not restore source',rectangle())
        held_pointer.stdin.write('button 272 0\nsleep 100\n')
        held_pointer.stdin.flush()
    finally:
        held_pointer.stdin.close()
        held_pointer.wait(timeout=3)
    keyboard.wait(timeout=3)
    assert events()==[['begin',address],['cancel',address]],events()
    report['checks'].append(dict(path='Escape cancellation',events=events()))
    ctl('reload')
    reset()
    inject('move 460 288\nbutton 272 1\nsleep 100\nmove 500 310\nsleep 100\nbutton 272 0\nsleep 100\n')
    assert events()==[['begin',address],['release',address]],events()
    report['checks'].append(dict(path='after Lua reload',events=events()))
    reset()
    keyboard=subprocess.Popen(['wtype','-M','logo','-s','2200','-m','logo'],env=env)
    time.sleep(.15)
    held_pointer=subprocess.Popen([str(pointer),'2880','1000'],env=env,stdin=subprocess.PIPE,text=True)
    try:
        held_pointer.stdin.write('move 460 430\nbutton 272 1\nsleep 100\nmove 5 450\nsleep 100\n')
        held_pointer.stdin.flush()
        time.sleep(.6)
        assert events()==[['begin',address]],events()
        assert current()['size']==[600,350],('snapped while held',rectangle())
        held_pointer.stdin.write('button 272 0\nsleep 100\n')
        held_pointer.stdin.flush()
        time.sleep(.2)
        assert 'win-snapped' in [t.rstrip('*') for t in current()['tags']],current()
        assert current()['size'][0]>700,rectangle()
        dropped=rectangle()
        held_pointer.stdin.write('move 500 500\nsleep 100\n')
        held_pointer.stdin.flush()
        time.sleep(.2)
        assert rectangle()==dropped,('stuck after release',rectangle())
        report['checks'].append(dict(path='modifier edge pause/release',rectangle=dropped))
    finally:
        held_pointer.stdin.close();held_pointer.wait(timeout=3)
        keyboard.wait(timeout=3)
    ctl('eval',f'hypr_snap_restore("{address}")')
    assert rectangle()==[260,300,600,350],('edge restore changed origin',rectangle())
    ctl('eval',f'hypr_snap_zone("left","{address}",false)')
    snapped_rectangle=rectangle()
    sx,sy,sw,sh=snapped_rectangle
    px,py=round(sx+sw*.9),sy+180
    ctl('eval','qa_drag_events={}')
    keyboard=subprocess.Popen(['wtype','-M','logo','-s','2200','-m','logo'],env=env)
    time.sleep(.15)
    held_pointer=subprocess.Popen([str(pointer),'2880','1000'],env=env,stdin=subprocess.PIPE,text=True)
    try:
        held_pointer.stdin.write(f'move {px} {py}\nbutton 272 1\nsleep 100\n')
        held_pointer.stdin.flush();time.sleep(.2)
        anchored=rectangle()
        assert anchored[2:]==[600,350],('unsnap dimensions',anchored)
        assert anchored[0]<=px<=anchored[0]+anchored[2] and anchored[1]<=py<=anchored[1]+anchored[3],('cursor left restored window',anchored,px,py)
        held_pointer.stdin.write('move 1100 600\nsleep 100\n');held_pointer.stdin.flush();time.sleep(.2)
        subprocess.run(['wtype','-s','150','-k','Escape','-s','250'],env=env,check=True)
        assert events()==[['begin',address],['cancel',address]],events()
        assert rectangle()==snapped_rectangle,('cancel lost source snap',rectangle(),snapped_rectangle)
        report['checks'].append(dict(path='snapped unsnap anchor and Escape restore',anchored=anchored,restored=rectangle()))
    finally:
        held_pointer.stdin.close();held_pointer.wait(timeout=3)
        keyboard.wait(timeout=3)
    reset()
    keyboard=subprocess.Popen(['wtype','-M','logo','-s','900','-m','logo'],env=env)
    time.sleep(.15)
    inject('move 500 430\nbutton 273 1\nsleep 100\nmove 550 460\nsleep 100\nbutton 273 0\nsleep 100\n')
    keyboard.wait(timeout=3)
    assert ctl('repl','print(#qa_drag_events)')=='0',events()
    report['checks'].append(dict(path='resize does not trigger move snapping',rectangle=rectangle()))
    reset()
    ctl('dispatch',f'hl.dsp.window.fullscreen({{mode="maximized",action="toggle",window="address:{address}"}})')
    assert current()['fullscreen']==1,current()
    keyboard=subprocess.Popen(['wtype','-M','logo','-s','2200','-m','logo'],env=env)
    time.sleep(.15)
    held_pointer=subprocess.Popen([str(pointer),'2880','1000'],env=env,stdin=subprocess.PIPE,text=True)
    try:
        held_pointer.stdin.write('move 1200 300\nbutton 272 1\nsleep 100\nmove 1200 350\nsleep 100\n')
        held_pointer.stdin.flush();time.sleep(.3)
        assert current()['fullscreen']==0 and current()['size']==[600,350],('maximized drag did not restore normal',rectangle())
        held_pointer.stdin.write('move 1595 450\nbutton 272 0\nsleep 100\n');held_pointer.stdin.flush();time.sleep(.3)
        assert 'win-snapped' in [t.rstrip('*') for t in current()['tags']],current()
        assert events()==[['begin',address],['release',address]],events()
        ctl('eval',f'hypr_snap_restore("{address}")')
        assert rectangle()==[260,300,600,350],('maximized drag changed normal restore',rectangle())
        report['checks'].append(dict(path='maximized modifier drag to snap and exact normal restore',rectangle=rectangle()))
    finally:
        held_pointer.stdin.close();held_pointer.wait(timeout=3)
        keyboard.wait(timeout=3)
    report['result']='pass'
except Exception as error:report['result']='fail';report['error']=repr(error)
finally:
    if process:
        process.terminate()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:process.kill();process.wait()
    Path.home().joinpath('.cache/window-drag-bridge-nested-qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert report['result']=='pass'
