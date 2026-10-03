#!/usr/bin/env python3
"""Actual Alt+Tab, titlebar Shake and Snap Assist with disposable modal families."""
import json, os, subprocess, tempfile, time
from pathlib import Path
H=Path.home(); B=H/'.local/bin'; C=H/'.local/share/hypr-window-controls'
report={'checks':[],'failures':[]}; processes=[]; pointer=None; keyboard=None

def ctl(*args): return subprocess.check_output(['hyprctl',*args],text=True).strip()
def data(*args): return json.loads(ctl(*args,'-j'))
def wait(fn,label):
    end=time.monotonic()+7
    while time.monotonic()<end:
        value=fn()
        if value:return value
        time.sleep(.1)
    raise AssertionError(label)
def check(name,value,**details):
    report['checks'].append(dict(name=name,passed=bool(value),**details))
    if not value: report['failures'].append(name)
def focus(w): ctl('dispatch',f'hl.dsp.focus({{window="address:{w["address"]}"}})')
def menu():
    r=subprocess.run(['qs','-p',str(C),'ipc','call','controls','state'],capture_output=True,text=True)
    try:return json.loads(r.stdout)
    except ValueError:return {}
def arrange(w,x,y,width,height):
    ctl('dispatch',f'hl.dsp.window.resize({{x={width},y={height},window="address:{w["address"]}"}})')
    ctl('dispatch',f'hl.dsp.window.move({{x={x},y={y},window="address:{w["address"]}"}})')
def run(*args): subprocess.run([str(a) for a in args],check=True,stdout=subprocess.DEVNULL)
def shake(w):
    x=w['at'][0]+65;y=w['at'][1]-12
    pointer.stdin.write(f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 150\n')
    pointer.stdin.flush();time.sleep(.3)
    trace=[]
    # The first motion enters native drag mode. Four subsequent movements
    # supply the three direction reversals required by the Shake recognizer.
    for offset in [140,-100,140,-100,140]:
        pointer.stdin.write(f'move {x+offset} {y}\nsleep 150\n');pointer.stdin.flush();time.sleep(.23)
        trace.append(dict(cursor=data('cursorpos'),windows=[{k:w.get(k) for k in ['title','at','size','workspace']} for w in data('clients') if w['pid'] in {p.pid for p in processes}],menu=menu()))
    report.setdefault('shakeTraces',[]).append(trace)
    # Leave caption controls after release so their normal hover picker does
    # not cover the next gesture being audited.
    pointer.stdin.write(f'button 272 0\nmove {x+140} {y+100}\nsleep 150\n');pointer.stdin.flush();time.sleep(.9)
initial=data('activewindow');cursor=data('cursorpos');monitor=next(m for m in data('monitors') if m['focused']);initial_ws=monitor['activeWorkspace']['name']
setting=data('getoption','input:resolve_binds_by_sym')['bool'];settings=H/'.config/omarchy/taskbar-settings.json';saved_settings=settings.read_bytes() if settings.exists() else None
catalog=H/'.config/omarchy/virtual-desktops.json';saved_catalog=catalog.read_bytes() if catalog.exists() else None
workspace=next(str(i) for i in range(974,985) if str(i) not in {w['workspace']['name'] for w in data('clients')})
with tempfile.TemporaryDirectory(prefix='modal-navigation-qa-') as directory:
    tmp=Path(directory);control=tmp/'control'
    def find(name):return next((w for w in data('clients') if w['title']=='Modal QA '+name and w['pid'] in {p.pid for p in processes}),None)
    try:
        assert monitor['width']/monitor['scale']==1600 and monitor['height']/monitor['scale']==1000
        ctl('dispatch',f'hl.dsp.focus({{workspace="{workspace}"}})')
        ctl('eval','hl.config({input={resolve_binds_by_sym=true}})')
        run(B/'hypr-taskbar','config','switcherScope','current')
        for mode in ['family','peer']:
            processes.append(subprocess.Popen(['python3',str(H/'window-integration-qa/modal_probe_gtk.py'),mode,str(control),str(tmp/(mode+'.jsonl'))],stdout=subprocess.DEVNULL,stderr=(tmp/'errors').open('a')))
        owner=wait(lambda:find('owner'),'owner');peer=wait(lambda:find('peer'),'peer')
        arrange(owner,120,250,580,380);arrange(peer,1020,400,380,300)
        control.write_text('open');child=wait(lambda:find('child'),'child');arrange(child,330,360,320,180)
        control.write_text('nested');nested=wait(lambda:find('nested'),'nested');arrange(nested,440,420,240,140);time.sleep(.4)
        report['platform']='XWayland' if nested.get('xwayland') else 'Wayland'
        focus(peer)
        keyboard=subprocess.Popen(['wtype','-M','alt','-P','Alt_L','-k','Tab','-s','2500','-p','Alt_L','-m','alt'])
        state=wait(lambda:menu() if menu().get('opened') else None,'Alt+Tab opens')
        candidates=state['request']['candidates'];addresses={w['address'] for w in candidates}
        check('Alt+Tab lists deepest modal and independent peer, excludes disabled ancestors',addresses=={nested['address'],peer['address']},menu=state)
        keyboard.wait(timeout=5);keyboard=None
        wait(lambda:data('activewindow').get('address')==nested['address'],'Alt release focuses deepest modal')
        check('Alt release commits exact modal identity',data('activewindow').get('stableId')==nested['stableId'])
        keyboard=subprocess.Popen(['wtype','-M','alt','-P','Alt_L','-M','shift','-P','Shift_L','-k','Tab','-p','Shift_L','-m','shift','-s','1500','-k','Escape','-s','500','-p','Alt_L','-m','alt'])
        state=wait(lambda:menu() if menu().get('opened') else None,'reverse switcher opens')
        selected=state['request']['candidates'][state['selected']]
        check('reverse Alt+Tab selects unrelated peer',selected['address']==peer['address'])
        keyboard.wait(timeout=5);keyboard=None;time.sleep(.3)
        check('Escape cancels modal switch and later Alt release does not commit',not menu().get('opened') and data('activewindow').get('address')==nested['address'],menu=menu(),active=data('activewindow').get('title'))
        pointer=subprocess.Popen([str(C/'qa/virtual-pointer'),'1600','1000'],stdin=subprocess.PIPE,text=True,stdout=subprocess.DEVNULL)
        shake(find('nested'));wait(lambda:find('peer')['workspace']['name']=='special:win-minimized','Shake minimizes unrelated peer')
        check('native dialog Shake preserves complete owner family',all(find(n)['workspace']['name']==workspace for n in ['owner','child','nested']))
        shake(find('nested'));wait(lambda:find('peer')['workspace']['name']==workspace,'second Shake restores peer')
        check('second native Shake restores peer and retains modal focus',data('activewindow').get('address')==nested['address'])
        ctl('eval',f'hypr_snap_zone("left","{peer["address"]}",false)');time.sleep(.4)
        assist=json.loads(subprocess.check_output([str(B/'hypr-snap-groups'),'assist-data',peer['address'],'left'],text=True))
        check('Snap Assist excludes modal dialogs and disabled owner',not assist['candidates'],assist=assist)
        blocked=json.loads(subprocess.check_output([str(B/'hypr-snap-groups'),'assist-data',owner['address'],'left'],text=True))
        check('disabled owner cannot offer a Snap Assist operation',not blocked['candidates'] and not blocked['zones'])
        control.write_text('close_nested');wait(lambda:not find('nested'),'nested closes')
        control.write_text('close');wait(lambda:not find('child'),'child closes');time.sleep(.3)
        focus(peer);run(B/'hypr-window-menu','assist',peer['address'],'left')
        state=wait(lambda:menu() if menu().get('opened') and menu()['request'].get('mode')=='assist' else None,'eligible owner Snap Assist opens')
        check('Snap Assist restores owner eligibility after dialog close',{w['address'] for w in state['request']['candidates']}=={owner['address']})
        run('wtype','-k','Return');wait(lambda:any(t.rstrip('*')=='win-snapped' for t in find('owner')['tags']),'picker snaps selected owner')
        groups=json.loads(subprocess.check_output([str(B/'hypr-snap-groups'),'list'],text=True))
        report['snapGroups']=groups
        check('native Snap Assist selection forms complementary Snap Group',any({m['address'] for m in g['members']}=={owner['address'],peer['address']} for g in groups))
        report['result']='pass' if not report['failures'] else 'fail'
    except Exception as error:
        report['result']='fail';report['error']=repr(error)
        report['failedActive']=data('activewindow');report['failedMenu']=menu();report['failedClients']=data('clients')
    finally:
        if keyboard:
            try:keyboard.wait(timeout=5)
            except subprocess.TimeoutExpired:keyboard.terminate();keyboard.wait()
        run(B/'hypr-window-menu','hide')
        if pointer:pointer.stdin.close();pointer.wait(timeout=3)
        for p in processes:
            p.terminate()
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        for path,content in [(settings,saved_settings),(catalog,saved_catalog)]:
            if content is not None:path.write_bytes(content)
            else:path.unlink(missing_ok=True)
        ctl('eval',f'hl.config({{input={{resolve_binds_by_sym={str(setting).lower()}}}}})')
        ctl('dispatch',f'hl.dsp.focus({{workspace="{initial_ws}"}})')
        if initial.get('address'):focus(initial)
        ctl('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
        run(B/'hypr-snap-groups','sync')
        runtime=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr-windowctl'
        runtime.joinpath('minimize-others-'+workspace).unlink(missing_ok=True)
        for sidecar in runtime.glob('*.monitor.json'):
            try:
                if json.loads(sidecar.read_text()).get('pid') in {p.pid for p in processes}:
                    runtime.joinpath(sidecar.name.removesuffix('.monitor.json')).unlink(missing_ok=True);sidecar.unlink()
            except (OSError,ValueError):pass
        report['gtkErrors']=(tmp/'errors').read_text() if (tmp/'errors').exists() else ''
        Path(os.getenv('MODAL_NAV_REPORT',str(H/'.cache/window-modal-navigation-qa.json'))).write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));assert report['result']=='pass'
