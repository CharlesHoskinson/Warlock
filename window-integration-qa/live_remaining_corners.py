#!/usr/bin/env python3
"""Native titlebar release trials for the previously missing two corners."""
import json
from pathlib import Path
import subprocess
import time
report={'checks':[]}
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
pointer=Path.home()/'.local/share/hypr-window-controls/qa/virtual-pointer'
process=None
def inject(text):subprocess.run([str(pointer),'1600','1000'],input=text,text=True,check=True)
def rectangle(w):return w['at']+w['size']
try:
    monitor=next(m for m in data('monitors') if m['focused'])
    assert monitor['x']==0 and monitor['y']==0 and monitor['width']/monitor['scale']==1600 and monitor['height']/monitor['scale']==1000,'fixture requires current 1600x1000 logical display'
    process=subprocess.Popen(['foot','--app-id=window-parity-corner-qa','--title=Native missing corner QA','sleep','120'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    address=wait(lambda:next((w['address'] for w in data('clients') if w['pid']==process.pid),None),'foot create')
    ctl('eval',f'qa_corner_events={{}}; hl.on("hyprbars.drag_start",function(w) if w.address=="{address}" then table.insert(qa_corner_events,{{kind="begin",fullscreen=w.fullscreen,x=w.at.x,y=w.at.y}}) end end); hl.on("hyprbars.drag_finish",function(w,released) if w.address=="{address}" then table.insert(qa_corner_events,{{kind=released and "release" or "cancel",fullscreen=w.fullscreen,x=w.at.x,y=w.at.y}}) end end)')
    def current():return next(w for w in data('clients') if w['address']==address)
    for zone,x,y,expected in [('top_right',1595,75,[804,60,786,447]),('bottom_left',5,995,[10,541,784,448]),('maximize',800,2,None)]:
        ctl('eval',f'hypr_snap_restore("{address}")')
        ctl('dispatch',f'hl.dsp.focus({{window="address:{address}"}})')
        ctl('dispatch',f'hl.dsp.window.resize({{x=600,y=350,window="address:{address}"}})')
        ctl('dispatch',f'hl.dsp.window.move({{x=260,y=300,window="address:{address}"}})')
        time.sleep(.4)
        inject(f'move 460 288\nsleep 100\nbutton 272 1\nsleep 80\nmove 600 320\nsleep 60\nmove {x} {y}\nsleep 120\nbutton 272 0\nsleep 500\n')
        result=wait(lambda:current() if (current()['fullscreen']==1 if zone=='maximize' else any(t.rstrip('*')=='win-snapped' for t in current()['tags'])) else None,'native edge/corner release snap')
        observed=rectangle(result)
        if expected:assert all(abs(a-b)<=2 for a,b in zip(observed,expected)),(zone,observed,expected)
        subprocess.run([str(Path.home()/'.local/bin/hypr-window-menu'),'hide'],check=True)
        inject('move 500 500\nsleep 300\n')
        assert rectangle(current())==observed,'release left a stuck drag'
        report['checks'].append(dict(zone=zone,rectangle=observed,noStuckDrag=True))
        ctl('eval',f'hypr_snap_restore("{address}")');time.sleep(.3)
        assert rectangle(current())==[260,300,600,350],('restore changed',rectangle(current()))
    report['result']='pass'
except Exception as error:
    report['result']='fail';report['error']=repr(error)
    try:
        report['window']=current()
        report['events']=ctl('repl','for _,e in ipairs(qa_corner_events) do print(e.kind,e.fullscreen,e.x,e.y) end')
        report['cursor']=data('cursorpos')
    except Exception:pass
finally:
    subprocess.run([str(Path.home()/'.local/bin/hypr-window-menu'),'hide'],stdout=subprocess.DEVNULL)
    if process:
        process.terminate()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:process.kill();process.wait()
    if initial_focus.get('address'):ctl('dispatch',f'hl.dsp.focus({{window="address:{initial_focus["address"]}"}})')
    ctl('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
    Path.home().joinpath('.cache/window-controls-remaining-corners-qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert report['result']=='pass'
