#!/usr/bin/env python3
"""Pointer focus may scroll hovered windows without taking keyboard focus."""
import json
from pathlib import Path
import subprocess
import tempfile
import time
HERE=Path(__file__).parent
report={'checks':[]}
processes=[]
def ctl(*args):return subprocess.check_output(['hyprctl',*args],text=True).strip()
def data(*args):return json.loads(ctl(*args,'-j'))
def wait(fn,label):
    deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        result=fn()
        if result:return result
        time.sleep(.1)
    raise AssertionError(label)
initial_focus=data('activewindow');cursor=data('cursorpos')
initial_mode=data('getoption','input:follow_mouse')['int']
pointer=Path.home()/'.local/share/hypr-window-controls/qa/virtual-pointer'
def focus(address):ctl('dispatch',f'hl.dsp.focus({{window="address:{address}"}})')
def inject(text):subprocess.run([str(pointer),'1600','1000'],input=text,text=True,check=True)
def events(path):return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
with tempfile.TemporaryDirectory(prefix='inactive-scroll-qa-') as temp:
    try:
        windows=[];logs=[]
        for i,x in enumerate((180,700)):
            log=Path(temp)/str(i);logs.append(log)
            p=subprocess.Popen(['python3',str(HERE/'wheel_probe_gtk.py'),f'Inactive scroll QA {i}',str(log)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            processes.append(p)
            w=wait(lambda:next((w for w in data('clients') if w['pid']==p.pid),None),'GTK probe created')
            windows.append(w['address'])
            ctl('dispatch',f'hl.dsp.window.resize({{x=400,y=300,window="address:{w["address"]}"}})')
            ctl('dispatch',f'hl.dsp.window.move({{x={x},y=300,window="address:{w["address"]}"}})')
        time.sleep(.4)
        a,b=windows
        for mode in (0,2):
            ctl('eval',f'hl.config({{input={{follow_mouse={mode},float_switch_override_focus=0}}}})')
            focus(b)
            inject('move 850 450\nsleep 100\nmove 300 450\nsleep 200\nwheel 120\nsleep 200\n')
            active=data('activewindow')['address']
            observed=[events(log) for log in logs]
            report['checks'].append(dict(mode=mode,active=active,events=observed))
            if mode==2:
                assert active==b,'hover stole keyboard focus'
                assert any(e['event']=='wheel' for e in observed[0]),'inactive surface did not receive wheel'
                assert not any(e['event']=='wheel' for e in observed[1]),'wheel reached keyboard-focused peer'
                subprocess.run(['wtype','x'],check=True)
                wait(lambda:any(e.get('keyval')==120 for e in events(logs[1])),'keyboard input stays in active peer')
                inject('move 300 450\nbutton 272 1\nbutton 272 0\nsleep 200\n')
                assert data('activewindow')['address']==a,'click did not focus hovered window'
                report['checks'].append(dict(clickFocus=a,keyboardPeer=b))
            for log in logs:log.write_text('')
        report['result']='pass'
    except Exception as error:report['result']='fail';report['error']=repr(error)
    finally:
        for p in processes:
            p.terminate()
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        ctl('eval',f'hl.config({{input={{follow_mouse={initial_mode}}}}})')
        if initial_focus.get('address'):focus(initial_focus['address'])
        ctl('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
        Path.home().joinpath('.cache/window-inactive-scroll-live-qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert report['result']=='pass'
