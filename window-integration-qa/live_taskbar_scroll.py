#!/usr/bin/env python3
import json,subprocess,time
from pathlib import Path
report={}
initial_focus=json.loads(subprocess.check_output(['hyprctl','activewindow','-j'],text=True))
def ipc(method,*args):return subprocess.check_output(['qs','-p','/usr/share/omarchy/shell','ipc','call','hoskinson.windows',method,*map(str,args)],text=True).strip()
def state():
    try:return json.loads(ipc('state'))
    except ValueError:return {}
def wait(fn,label):
    deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        value=fn()
        if value:return value
        time.sleep(.1)
    raise AssertionError(label)
initial_cursor=json.loads(subprocess.check_output(['hyprctl','cursorpos','-j'],text=True))
try:
    wait(lambda:state() if state().get('currentMonitor',-1)>=0 else None,'taskbar initialized')
    ipc('menu',1)
    before=wait(lambda:state() if state()['popupOpen'] and state()['keyboardFocus'] else None,'keyboard menu open')
    assert before['popupContentHeight']>before['popupViewportHeight'],before
    subprocess.run(['wtype']+['-k','Down']*(len(before['menuLabels'])-1),check=True)
    after=wait(lambda:state() if state()['selectedWindowIndex']==len(before['menuLabels'])-1 and state()['popupScrollY']>0 else None,'keyboard selected final row remains visible')
    report['keyboard']={'before':before,'after':after}
    subprocess.run(['grim','-g','0,0 650x550','/tmp/taskbar-scope-settings-v38.png'],check=True)
    ipc('dismiss');ipc('menu',1)
    wait(lambda:state()['popupOpen'] and state()['popupScrollY']==0 and state()['popupContentHeight']>state()['popupViewportHeight'],'reset menu scroll')
    pointer=Path.home()/'.local/share/hypr-window-controls/qa/virtual-pointer'
    subprocess.run([str(pointer),'1600','1000'],input='move 100 150\nsleep 300\nwheel 120\nsleep 300\n',text=True,check=True)
    wheel=wait(lambda:state() if state()['popupScrollY']>0 else None,'native wheel scrolls popup')
    report['wheel']=wheel
    # Native Escape must release the layer's keyboard focus.
    subprocess.run(['wtype','-k','Escape'],check=True)
    wait(lambda:not state()['popupOpen'],'Escape closes keyboard menu')
    for iteration in range(5):
        ipc('menu',1)
        wait(lambda:state()['popupOpen'] and state()['keyboardFocus'],'rapid menu focus')
        ipc('dismiss');ipc('menu',1)
        time.sleep(.15)
        assert state()['popupOpen'] and state()['keyboardFocus'],state()
        ipc('dismiss')
    report['rapidReopen']=5
    time.sleep(.2)
    subprocess.run([str(pointer),'1600','1000'],input='move 185 13\nsleep 100\nbutton 273 1\nbutton 273 0\nsleep 200\nmove 100 150\nwheel 120\nsleep 200\n',text=True,check=True)
    mouse=wait(lambda:state() if state()['popupOpen'] and not state()['keyboardMode'] and state()['popupScrollY']>0 else None,'right-click menu wheel')
    report['mouseWheel']=mouse
    subprocess.run([str(pointer),'1600','1000'],input='move 700 600\nbutton 272 1\nbutton 272 0\nsleep 200\n',text=True,check=True)
    wait(lambda:not state()['popupOpen'],'outside click dismisses mouse menu')
    ipc('menu',1)
    wait(lambda:state()['popupOpen'] and state()['keyboardFocus'],'keyboard menu reopened')
    time.sleep(.1)
    subprocess.run([str(pointer),'1600','1000'],input='move 700 600\nbutton 272 1\nbutton 272 0\nsleep 200\n',text=True,check=True)
    wait(lambda:not state()['popupOpen'],'outside click dismisses keyboard menu')
    report['dismissal']='Escape and outside click in both modes pass'
    report['result']='pass'
except Exception as error:report['result']='fail';report['error']=repr(error)
finally:
    ipc('dismiss')
    if initial_focus.get('address'):
        subprocess.run(['hyprctl','dispatch',f'hl.dsp.focus({{window="address:{initial_focus["address"]}"}})'],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['hyprctl','dispatch',f'hl.dsp.cursor.move({{x={initial_cursor["x"]},y={initial_cursor["y"]}}})'],check=True,stdout=subprocess.DEVNULL)
    Path.home().joinpath('.cache/taskbar-scroll-live-qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'result':report['result'],'error':report.get('error')},indent=2))
assert report['result']=='pass'
