#!/usr/bin/env python3
"""Main compositor drag regression using disposable peers and persistent input."""
import json,subprocess,time
from pathlib import Path
report={'checks':[]};process=None;peer=None;held=None;keyboard=None
pointer=Path.home()/'.local/share/hypr-window-controls/qa/virtual-pointer'
def ctl(*args):return subprocess.check_output(['hyprctl',*args],text=True).strip()
def data(*args):return json.loads(ctl(*args,'-j'))
def wait(fn,label):
    end=time.monotonic()+5
    while time.monotonic()<end:
        result=fn()
        if result:return result
        time.sleep(.1)
    raise AssertionError(label)
initial=data('activewindow');cursor=data('cursorpos');input_setting=data('getoption','input:resolve_binds_by_sym')['bool']
def menu_present():return any(s.get('namespace')=='omarchy-menu' for m in data('layers').values() for surfaces in m.get('levels',{}).values() for s in surfaces)
initial_menu=menu_present()
def inject(text):subprocess.run([str(pointer),'1600','1000'],input=text,text=True,check=True)
def begin(modifier,x=460,y=430):
    global held,keyboard
    if modifier:
        keyboard=subprocess.Popen(['wtype','-M',modifier,'-s','4000','-m',modifier])
        time.sleep(.15)
    held=subprocess.Popen([str(pointer),'1600','1000'],stdin=subprocess.PIPE,text=True)
    send(f'move {x} {y}\nbutton 272 1\nsleep 100\n')
def send(text):held.stdin.write(text);held.stdin.flush();time.sleep(.2)
def finish():
    global held,keyboard
    if held:
        held.stdin.close();held.wait(timeout=3);held=None
    if keyboard:keyboard.wait(timeout=5);keyboard=None
try:
    assert ctl('repl','print(hl.plugin.hyprbars.drag_bridge())')=='true'
    m=next(m for m in data('monitors') if m['focused'])
    assert m['x']==0 and m['y']==0 and m['width']/m['scale']==1600 and m['height']/m['scale']==1000
    ctl('eval','hl.config({input={resolve_binds_by_sym=true}})')
    process=subprocess.Popen(['foot','--app-id=window-parity-modifier-qa','--title=Modifier drag QA','sleep','180'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    address=wait(lambda:next((w['address'] for w in data('clients') if w['pid']==process.pid),None),'foot create')
    def current():return next(w for w in data('clients') if w['address']==address)
    def rect():return current()['at']+current()['size']
    def reset():
        ctl('eval',f'hypr_snap_restore("{address}")')
        ctl('dispatch',f'hl.dsp.window.resize({{x=600,y=350,window="address:{address}"}})')
        ctl('dispatch',f'hl.dsp.window.move({{x=260,y=300,window="address:{address}"}})')
        ctl('dispatch',f'hl.dsp.focus({{window="address:{address}"}})')
        time.sleep(.3)
    for modifier in ['logo','alt']:
        reset();begin(modifier);send('move 5 450\nsleep 100\n');time.sleep(.4)
        assert current()['size']==[600,350] and not any(t.rstrip('*')=='win-snapped' for t in current()['tags']),('snapped before release',modifier,rect())
        send('button 272 0\nsleep 100\n')
        wait(lambda:any(t.rstrip('*')=='win-snapped' for t in current()['tags']),'released edge snap')
        dropped=rect();send('move 500 500\nsleep 100\n');assert rect()==dropped,('stuck release',modifier)
        finish();ctl('eval',f'hypr_snap_restore("{address}")');time.sleep(.3)
        assert rect()==[260,300,600,350],('normal restore',modifier,rect())
        report['checks'].append(dict(path=modifier+' held edge/release/restore',rectangle=dropped))
    for modifier in ['logo',None]:
        reset();begin(modifier,460,430 if modifier else 288);send('move 800 500\nsleep 100\n')
        subprocess.run(['wtype','-s','150','-k','Escape','-s','250'],check=True);time.sleep(.2)
        assert rect()==[260,300,600,350],('Escape restore',modifier,rect())
        send('move 900 600\nsleep 100\n');assert rect()==[260,300,600,350],('movement after cancel',modifier,rect())
        finish();report['checks'].append(dict(path=('logo' if modifier else 'titlebar')+' Escape cancel/unstuck'))
    reset();ctl('eval',f'hypr_snap_zone("left","{address}",false)');time.sleep(.3)
    snapped=rect();x,y,w,h=snapped;px,py=round(x+w*.9),y+180
    begin('logo',px,py);anchored=rect()
    assert anchored[2:]==[600,350] and anchored[0]<=px<=anchored[0]+600 and anchored[1]<=py<=anchored[1]+350,('unsnap cursor anchor',anchored,px,py)
    send('move 1000 600\nsleep 100\n');subprocess.run(['wtype','-s','150','-k','Escape','-s','250'],check=True);time.sleep(.3)
    assert rect()==snapped,('cancel source snap',rect(),snapped)
    finish();report['checks'].append(dict(path='snapped anchor/cancel',anchored=anchored,restored=snapped))
    ctl('reload');assert not ctl('configerrors');ctl('eval','hl.config({input={resolve_binds_by_sym=true}})')
    reset();begin('alt');send('move 1595 450\nbutton 272 0\nsleep 100\n')
    wait(lambda:any(t.rstrip('*')=='win-snapped' for t in current()['tags']),'snap after reload')
    finish();report['checks'].append(dict(path='Alt snap after config reload',rectangle=rect()))
    report['result']='pass'
except Exception as error:report['result']='fail';report['error']=repr(error)
finally:
    try:finish()
    except Exception:pass
    subprocess.run([str(Path.home()/'.local/bin/hypr-window-menu'),'hide'],stdout=subprocess.DEVNULL)
    if not initial_menu and menu_present():
        subprocess.run(['omarchy-shell','shell','hide','omarchy.menu'],check=True,stdout=subprocess.DEVNULL)
    if process:
        process.terminate()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:process.kill();process.wait()
    ctl('eval',f'hl.config({{input={{resolve_binds_by_sym={"true" if input_setting else "false"}}}}})')
    if initial.get('address'):ctl('dispatch',f'hl.dsp.focus({{window="address:{initial["address"]}"}})')
    ctl('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
    Path.home().joinpath('.cache/window-modifier-drag-qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));assert report['result']=='pass'
