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
    report['monitors']=data('monitors')
    a=launch('Monitor transfer QA')
    ctl('dispatch',f'hl.dsp.window.move({{monitor="{initial_monitors[0]["name"]}",window="address:{a}"}})')
    focus(a)
    eval_(f'hypr_snap_zone("left","{a}",false)')
    time.sleep(.5)
    before=current(a);report['before']=before
    binding('Move window to next display')
    moved=wait(lambda:current(a) if current(a)['monitor']==m['id'] else None,'bound monitor transfer')
    time.sleep(.5);moved=current(a);report['moved']=moved
    assert any(t.rstrip('*')=='win-snapped' for t in moved['tags']), 'monitor transfer lost snap state'
    assert moved['size'][0] in range(620,641), ('not destination half',moved['size'])
    report['checks'].append('bound snapped transfer preserves destination half')
    b=launch('Monitor filter QA')
    ctl('dispatch',f'hl.dsp.window.move({{monitor="{initial_monitors[0]["name"]}",window="address:{b}"}})')
    focus(a)
    subprocess.run([str(BIN/'hypr-taskbar'),'config','displayMode','all'],check=True)
    wait(lambda:{a,b}.issubset(taskbar()),'both windows populated before monitor filter')
    subprocess.run([str(BIN/'hypr-taskbar'),'config','displayMode','monitor'],check=True)
    wait(lambda:a in taskbar() and b not in taskbar(),'taskbar monitor filter')
    report['checks'].append('real QML monitor filter shows destination owner and excludes other display')
    subprocess.run([str(BIN/'hypr-taskbar'),'config','displayMode','all'],check=True)
    wait(lambda:{a,b}.issubset(taskbar()),'taskbar all displays')
    report['checks'].append('real QML all-display mode shows both owners')
    eval_(f'hl.monitor({{output="{name}",mode="1920x1080@60",position="1600x0",scale=2}})')
    time.sleep(.7)
    scaled=current(a);report['scaled']=scaled
    assert scaled['at'][0]>=1600 and scaled['at'][0]+scaled['size'][0]<=2560 and scaled['at'][1]+scaled['size'][1]<=540, ('scale change left snap offscreen',scaled['at'],scaled['size'])
    report['checks'].append('scale change keeps snap bounded')
    subprocess.run(['grim','-o',name,'/tmp/window-monitor-scale-qa.png'],check=True)
    eval_(f'hypr_snap_restore("{a}")');time.sleep(.3)
    restored=current(a);report['restored']=restored
    assert restored['at'][0]>=m['x'] and restored['at'][0]+restored['size'][0]<=m['x']+m['width']/m['scale']
    report['checks'].append('normal restore remains on destination monitor')
    eval_(f'hypr_snap_zone("left","{a}",false)')
    time.sleep(.3)
    focus(b)
    eval_(f'hypr_snap_zone("maximize","{b}",false)')
    binding('Move window to next display')
    wait(lambda:current(b)['monitor']==m['id'] and current(b)['fullscreen']==1,'maximized transfer')
    report['checks'].append('bound transfer preserves maximized mode')
    ctl('output','remove',name)
    recovered=wait(lambda:current(a) if current(a)['monitor']==initial_monitors[0]['id'] else None,'monitor remove recovery')
    time.sleep(.5);recovered=current(a)
    assert recovered['size'][0] in range(780,791) and any(t.rstrip('*')=='win-snapped' for t in recovered['tags']), ('unplug lost snap',recovered)
    assert current(b)['monitor']==initial_monitors[0]['id'] and current(b)['fullscreen']==1,'unplug lost maximized mode'
    report['maximizedRecovered']=current(b)
    report['recovered']=recovered
    report['checks'].append('headless unplug retains window on physical monitor')
    report['result']='pass'
except Exception as error:
    report['result']='fail';report['error']=repr(error)
finally:
    if any(m['name']==name for m in data('monitors')):ctl('output','remove',name)
    for p in processes:
        p.terminate()
        try:p.wait(timeout=3)
        except subprocess.TimeoutExpired:p.kill();p.wait()
    if initial_settings is None:settings.unlink(missing_ok=True)
    else:settings.write_bytes(initial_settings)
    ctl('reload')
    if initial_focus.get('address'):focus(initial_focus['address'])
    ctl('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
    report['afterMonitors']=data('monitors')
    report['configerrors']=ctl('configerrors')
    Path.home().joinpath('.cache/window-monitor-live-qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('monitors','before','moved','scaled','restored','recovered','maximizedRecovered','afterMonitors')},indent=2))
