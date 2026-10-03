import json, subprocess, time
from pathlib import Path
BIN=Path.home()/'.local/bin'
report={'checks':[]}
name='WINDOW-PARITY-QA'
processes=[]

def ctl(*args):return subprocess.check_output(['hyprctl',*args],text=True).strip()
def data(*args):return json.loads(ctl(*args,'-j'))
def eval_(text):ctl('eval',text)
def wait(fn,label):
    deadline=time.monotonic()+6
    while time.monotonic()<deadline:
        result=fn()
        if result:return result
        time.sleep(.1)
    raise AssertionError(label)
def current(address):return next(w for w in data('clients') if w['address']==address)
def focus(address):ctl('dispatch',f'hl.dsp.focus({{window="address:{address}"}})')
def binding(description):
    eval_('hl.config({input={resolve_binds_by_sym=true}})')
    subprocess.run(['wtype','-M','logo','-M','shift','-k','Right','-m','shift','-m','logo'],check=True)
def launch(title):
    p=subprocess.Popen(['foot','--app-id=window-parity-monitor-qa','--title='+title,'sleep','180'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);processes.append(p)
    window=wait(lambda:next((w for w in data('clients') if w['pid']==p.pid),None),'foot create')
    return window['address']
initial_monitors=data('monitors');initial_focus=data('activewindow');cursor=data('cursorpos')
settings=Path.home()/'.config/omarchy/taskbar-settings.json'
initial_settings=settings.read_bytes() if settings.exists() else None
catalog=Path.home()/'.config/omarchy/virtual-desktops.json'
initial_catalog=catalog.read_bytes() if catalog.exists() else None
def taskbar():
    try:
        state=json.loads(subprocess.check_output(['qs','-p','/usr/share/omarchy/shell','ipc','call','hoskinson.windows','state'],text=True))
        return {a for g in state['indicators'] for a in g['windows']}
    except (ValueError,subprocess.SubprocessError):return set()
try:
    assert not any(m['name']==name for m in initial_monitors)
    for physical in initial_monitors:
        eval_(f'hl.monitor({{output="{physical["name"]}",mode="{physical["width"]}x{physical["height"]}@{physical["refreshRate"]}",position="{physical["x"]}x{physical["y"]}",scale={physical["scale"]}}})')
    ctl('output','create','headless',name)
    wait(lambda:any(m['name']==name for m in data('monitors')),'monitor create')
    eval_(f'hl.monitor({{output="{name}",mode="1920x1080@60",position="1600x0",scale=1.5}})')
    m=wait(lambda:next((m for m in data('monitors') if m['name']==name and m['scale']==1.5),None),'monitor scale')
    a=launch('Minimized monitor owner QA')
    ctl('dispatch',f'hl.dsp.window.move({{monitor="{name}",window="address:{a}"}})')
    b=launch('Visible monitor owner QA')
    ctl('dispatch',f'hl.dsp.window.move({{monitor="{initial_monitors[0]["name"]}",window="address:{b}"}})')
    focus(b)
    subprocess.run([str(BIN/'hypr-taskbar'),'config','displayMode','all'],check=True)
    wait(lambda:{a,b}.issubset(taskbar()),'both owners populated')
    report['before']={'a':current(a),'b':current(b)}
    subprocess.run([str(BIN/'hypr-windowctl'),'minimize',a],check=True)
    wait(lambda:current(a)['workspace']['name']=='special:win-minimized','minimized foreign owner')
    report['minimized']=current(a)
    subprocess.run([str(BIN/'hypr-taskbar'),'config','displayMode','monitor'],check=True)
    wait(lambda:b in taskbar() and a not in taskbar(),'minimized foreign window remains excluded from physical taskbar')
    report['checks'].append('minimized foreign window stays on its home monitor taskbar')
    # The empty home workspace can disappear while the minimized owner lives.
    home=report['before']['a']['workspace']['name']
    ctl('dispatch',f'hl.dsp.focus({{monitor="{name}"}})')
    ctl('dispatch','hl.dsp.focus({workspace="989"})')
    focus(b)
    wait(lambda:not any(w['name']==home for w in data('workspaces')),'empty home workspace disappeared')
    time.sleep(.5)
    assert a not in taskbar(),'saved home monitor lost after workspace deletion'
    report['checks'].append('inactive deleted workspace retains named home monitor')
    subprocess.run([str(BIN/'hypr-windowctl'),'restore',a],check=True)
    wait(lambda:current(a)['monitor']==m['id'] and current(a)['workspace']['name']!='special:win-minimized','restored owner returned to monitor')
    report['checks'].append('restore recreates deleted workspace on home monitor')
    subprocess.run([str(BIN/'hypr-windowctl'),'minimize',a],check=True)
    focus(b)
    target=current(b)['workspace']['name']
    subprocess.run([str(BIN/'hypr-desktops'),'move',a,target],check=True)
    wait(lambda:{a,b}.issubset(taskbar()),'minimized desktop move adopts physical monitor')
    subprocess.run([str(BIN/'hypr-windowctl'),'restore',a],check=True)
    wait(lambda:current(a)['monitor']==initial_monitors[0]['id'],'desktop-moved owner restores physically')
    report['checks'].append('moving minimized window to another desktop updates taskbar and restore monitor')
    c=launch('Minimized unplug QA')
    ctl('dispatch',f'hl.dsp.window.move({{monitor="{name}",window="address:{c}"}})')
    subprocess.run([str(BIN/'hypr-windowctl'),'minimize',c],check=True)
    focus(b)
    ctl('output','remove',name)
    wait(lambda:{a,b,c}.issubset(taskbar()),'removed output minimized owner adopts surviving monitor')
    subprocess.run([str(BIN/'hypr-windowctl'),'restore',c],check=True)
    wait(lambda:current(c)['monitor']==initial_monitors[0]['id'],'unplugged minimized owner restores physically')
    report['checks'].append('output removal preserves minimized entry and restores on surviving monitor')
    report['result']='pass'
except Exception as error:
    report['result']='fail';report['error']=repr(error)
finally:
    if any(m['name']==name for m in data('monitors')):ctl('output','remove',name)
    for p in processes:
        p.terminate()
        try:p.wait(timeout=3)
        except subprocess.TimeoutExpired:p.kill();p.wait()
    if initial_catalog is None:catalog.unlink(missing_ok=True)
    else:catalog.write_bytes(initial_catalog)
    if initial_settings is None:settings.unlink(missing_ok=True)
    else:settings.write_bytes(initial_settings)
    ctl('reload')
    if initial_focus.get('address'):focus(initial_focus['address'])
    ctl('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
    report['afterMonitors']=data('monitors')
    report['configerrors']=ctl('configerrors')
    Path.home().joinpath('.cache/window-minimized-monitor-live-qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('minimized','monitors','before','moved','scaled','restored','recovered','maximizedRecovered','afterMonitors')},indent=2))
