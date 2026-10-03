#!/usr/bin/env python3
"""Caption offset, captured owner and interruption acceptance with disposable foots."""
import json, os, subprocess, time
from pathlib import Path
H=Path.home();report={'checks':[],'failures':[]};processes=[];pointer=None

def ctl(*args):return subprocess.check_output(['hyprctl',*args],text=True).strip()
def data(*args):return json.loads(ctl(*args,'-j'))
def wait(fn):
    end=time.monotonic()+5
    while time.monotonic()<end:
        value=fn()
        if value:return value
        time.sleep(.1)
    raise AssertionError('disposable window create')
def check(name,value,**details):
    report['checks'].append(dict(name=name,passed=bool(value),**details))
    if not value:report['failures'].append(name)
def focus(address):ctl('dispatch',f'hl.dsp.focus({{window="address:{address}"}})')
def arrange(address,x,y,w,h):
    ctl('dispatch',f'hl.dsp.window.resize({{x={w},y={h},window="address:{address}"}})')
    ctl('dispatch',f'hl.dsp.window.move({{x={x},y={y},window="address:{address}"}})')
initial=data('activewindow');cursor=data('cursorpos')
try:
    for title in ['Caption anchor QA','Caption peer QA']:
        p=subprocess.Popen(['foot','--app-id=window-parity-caption-anchor-qa','--title='+title,'sleep','180'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);processes.append(p)
        w=wait(lambda:next((w for w in data('clients') if w['pid']==p.pid),None))
        if not w['floating']:ctl('dispatch',f'hl.dsp.window.float({{action="set",window="address:{w["address"]}"}})')
    def window(p):return next(w for w in data('clients') if w['pid']==p.pid)
    address=window(processes[0])['address'];peer=window(processes[1])['address']
    arrange(peer,1020,400,380,300)
    def current():return window(processes[0])
    def rect():return current()['at']+current()['size']
    def send(text,pause=.35):pointer.stdin.write(text);pointer.stdin.flush();time.sleep(pause)
    def release():send('button 272 0\nmove 500 800\nsleep 100\n')
    def reset():
        release();ctl('eval',f'hypr_snap_restore("{address}")');arrange(address,260,300,600,350);focus(address);time.sleep(.5)
        ctl('repl',f'local w=hl.get_window("address:{address}"); print(w.address)')
    def down(x=460,y=288):send(f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 150\n')
    pointer=subprocess.Popen([str(H/'.local/share/hypr-window-controls/qa/virtual-pointer'),os.getenv('CAPTION_POINTER_WIDTH','1600'),'1000'],stdin=subprocess.PIPE,text=True,stdout=subprocess.DEVNULL)
    reset();down();send('move 600 350\nsleep 150\n')
    check('first titlebar motion preserves original press offset',current()['at']==[400,362],expected=[400,362],actual=current()['at'])
    send('move 650 380\nsleep 150\n');check('later caption motion retains the same press offset',current()['at']==[450,392],actual=current()['at'])
    release();dropped=rect();send('move 900 600\nsleep 150\n');check('released caption cannot follow a later pointer move',rect()==dropped)
    reset();before_peer=window(processes[1])['at']+window(processes[1])['size'];down();send('move 1150 550\nsleep 150\n')
    check('first motion over another app keeps pressed caption owner',current()['at']==[950,562] and window(processes[1])['at']+window(processes[1])['size']==before_peer,expected=[950,562],actual=current()['at'],peer=window(processes[1])['at'])
    reset();down();focus(peer);send('move 1150 550\nsleep 150\n')
    check('focus change during pending press cannot redirect caption drag',current()['at']==[950,562] and window(processes[1])['at']+window(processes[1])['size']==before_peer,actual=current()['at'])
    reset();down();send('move 950 100\nsleep 150\n');check('first motion into empty space still moves pressed owner',current()['at']==[750,112],actual=current()['at'])
    reset();ctl('eval',f'hypr_snap_zone("left","{address}",false)');time.sleep(.5);snapped=rect();x,y,width,height=snapped
    px=x+round(width*.25);py=y-12;expected=[int(px-(px-x)/width*600+.5)+140,y+62,600,350]
    down(px,py);send(f'move {px+140} {py+62}\nsleep 150\n')
    check('first snapped-caption motion restores about original fractional press offset',rect()==expected,source=snapped,expected=expected,actual=rect())
    subprocess.run(['wtype','-k','Escape'],check=True);time.sleep(.3)
    check('Escape returns snapped caption to exact original rectangle',rect()==snapped,expected=snapped,actual=rect())
    release();time.sleep(.5);snapped=rect();x,y,width,height=snapped;down(x+round(width*.25),y-12);release()
    check('caption press/release without motion keeps snapped geometry',rect()==snapped)
    reset();down();send('move 600 350\nsleep 150\n');subprocess.run(['wtype','-k','Escape'],check=True);time.sleep(.3)
    cancelled=rect();send('move 900 600\nsleep 150\n');check('normal-caption Escape restores source and clears capture',cancelled==[260,300,600,350] and rect()==cancelled,actual=rect())
    reset();down();subprocess.run(['wtype','-k','Escape'],check=True);send('move 600 350\nsleep 150\n')
    check('Escape cancels a caption press before any motion',rect()==[260,300,600,350],actual=rect())
    reset();down();ctl('reload');assert not ctl('configerrors');send('move 600 350\nsleep 150\n')
    check('reload invalidates an unstarted caption press',rect()==[260,300,600,350],actual=rect())
    reset();down();send('move 600 350\nsleep 150\n');ctl('reload');assert not ctl('configerrors');time.sleep(.3)
    cancelled=rect();send('move 900 600\nsleep 150\n')
    check('reload cancels active caption drag and clears later motion',cancelled==[260,300,600,350] and rect()==cancelled,actual=rect())
    release();reset();down();p=processes[0];p.terminate();p.wait(timeout=3);send('move 1150 550\nsleep 150\n')
    check('closing caption owner cannot transfer its pending drag to peer',window(processes[1])['at']+window(processes[1])['size']==before_peer)
    release();report['result']='pass' if not report['failures'] else 'fail'
except Exception as error:report['result']='fail';report['error']=repr(error)
finally:
    if pointer:pointer.stdin.close();pointer.wait(timeout=3)
    for p in processes:
        if p.poll() is None:
            p.terminate()
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:p.kill();p.wait()
    if initial.get('address'):focus(initial['address'])
    ctl('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
    Path(os.getenv('CAPTION_ANCHOR_REPORT',str(H/'.cache/window-titlebar-anchor-qa.json'))).write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));assert report['result']=='pass'
