#!/usr/bin/env python3
"""Native file drag over taskbar into a minimized disposable GTK receiver."""
import json,subprocess,tempfile,time
from pathlib import Path
report={'checks':[]};processes=[];held=None
home=Path.home();pointer=home/'.local/share/hypr-window-controls/qa/virtual-pointer'
def ctl(*args):return subprocess.check_output(['hyprctl',*args],text=True).strip()
def data(*args):return json.loads(ctl(*args,'-j'))
def ipc(method,*args):return subprocess.check_output(['qs','-p','/usr/share/omarchy/shell','ipc','call','hoskinson.windows',method,*map(str,args)],text=True).strip()
def state():
    try:return json.loads(ipc('state'))
    except ValueError:return {}
def wait(fn,label):
    until=time.monotonic()+6
    while time.monotonic()<until:
        result=fn()
        if result:return result
        time.sleep(.1)
    raise AssertionError(label)
initial=data('activewindow');cursor=data('cursorpos')
def window(address):return next(w for w in data('clients') if w['address']==address)
def send(text):held.stdin.write(text);held.stdin.flush();time.sleep(.15)
def start_drag():
    global held
    ctl('dispatch',f'hl.dsp.focus({{window="address:{source}"}})')
    held=subprocess.Popen([str(pointer),'1600','1000'],stdin=subprocess.PIPE,text=True)
    send('move 1000 700\nbutton 272 1\nsleep 120\nmove 1050 700\nsleep 120\n')
def stop_drag():
    global held
    if held:held.stdin.close();held.wait(timeout=3);held=None
with tempfile.TemporaryDirectory(prefix='taskbar-file-drag-') as tmp:
    tmp=Path(tmp);payload=tmp/'sample.txt';payload.write_text('Disposable taskbar drag QA\n')
    def events(name):
        p=tmp/(name+'.jsonl')
        return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []
    def launch(mode,title,app_id,log):
        p=subprocess.Popen(['python3',str(home/'window-integration-qa/file_drag_probe_gtk.py'),app_id,title,mode,str(payload),str(tmp/(log+'.jsonl'))],stdout=subprocess.DEVNULL,stderr=(tmp/'gtk-errors.log').open('a'))
        processes.append(p)
        return wait(lambda:next((w['address'] for w in data('clients') if w['pid']==p.pid),None),'GTK create')
    try:
        target=launch('target','Taskbar drop destination','org.omarchy.DragTargetQA','target')
        ctl('dispatch',f'hl.dsp.window.move({{x=300,y=400,window="address:{target}"}})')
        source=launch('source','Taskbar drag source','org.omarchy.DragSourceQA','source')
        ctl('dispatch',f'hl.dsp.window.move({{x=800,y=600,window="address:{source}"}})')
        time.sleep(.6)
        start_drag();send('move 480 550\nsleep 200\nbutton 272 0\nsleep 300\n');stop_drag()
        assert any(e['event']=='drop' for e in events('target')),('direct GTK drop failed',events('source'),events('target'))
        report['checks'].append(dict(path='direct GTK file transfer baseline'))
        (tmp/'target.jsonl').unlink()
        probe=subprocess.run(['qs','-p','/tmp/taskbar-drag-probe.qml','ipc','call','probe','state'],capture_output=True,text=True)
        if probe.returncode==0 and probe.stdout.startswith('{'):
            before=json.loads(probe.stdout)['entries']
            start_drag();send('move 800 980\nsleep 500\n')
            after=json.loads(subprocess.check_output(['qs','-p','/tmp/taskbar-drag-probe.qml','ipc','call','probe','state'],text=True))['entries']
            send('button 272 0\nsleep 100\n');stop_drag()
            assert after>before,('standalone Qt panel did not receive drag',before,after)
            report['checks'].append(dict(path='standalone Qt panel drag enter',entries=after))
        subprocess.run([str(home/'.local/bin/hypr-windowctl'),'minimize',target],check=True)
        item=wait(lambda:next((g for g in state().get('taskbarItems',[]) if target in g['windows']),None),'target taskbar entry')
        tx=round(item['x']+item['width']/2);ty=13
        start_drag();assert any(e['event']=='begin' for e in events('source')),events('source')
        send(f'move {tx} {ty}\nsleep 150\nmove 1050 700\nsleep 1000\n')
        assert window(target)['workspace']['name']=='special:win-minimized','short drag hover restored destination'
        send('button 272 0\nsleep 150\n');stop_drag()
        report['checks'].append(dict(path='leave before dwell cancels activation',dragEntries=state()['dragEntries']))
        start_drag();send(f'move {tx} {ty}\nsleep 1100\n')
        wait(lambda:window(target)['workspace']['name']!='special:win-minimized','drag hover restores minimized target')
        assert data('activewindow')['address']==target,'destination not focused'
        send('move 480 550\nsleep 200\nbutton 272 0\nsleep 300\n');stop_drag()
        wait(lambda:any(e['event']=='drop' for e in events('target')),'file reaches destination after taskbar hover')
        assert events('target')[-1]['value']==payload.as_uri(),events('target')
        assert payload.read_text()=='Disposable taskbar drag QA\n','source payload changed'
        assert all(not e.get('delete',False) for e in events('source')),events('source')
        report['checks'].append(dict(path='minimized hover restore and destination drop',source=events('source'),target=events('target'),state=state()))
        peer=launch('target','Second taskbar drop destination','org.omarchy.DragTargetQA','peer')
        ctl('dispatch',f'hl.dsp.window.move({{x=300,y=400,window="address:{peer}"}})')
        for address in [target,peer]:subprocess.run([str(home/'.local/bin/hypr-windowctl'),'minimize',address],check=True)
        item=wait(lambda:next((g for g in state().get('taskbarItems',[]) if target in g['windows'] and peer in g['windows']),None),'grouped destinations')
        tx=round(item['x']+item['width']/2)
        start_drag();send(f'move {tx} 13\nsleep 1100\n')
        report['groupHoverInput']={'expected':[tx,13],'actual':data('cursorpos'),'state':state()}
        chooser=wait(lambda:state() if state().get('popupOpen') and len(state().get('previewItems',[]))==2 else None,'grouped drag chooser')
        assert all(window(a)['workspace']['name']=='special:win-minimized' for a in [target,peer]),'group hover selected destination prematurely'
        preview=next(w for w in chooser['previewItems'] if w['address']==peer)
        px,py=round(preview['x']+preview['width']/2),round(preview['y']+preview['height']/2)
        assert px>0 and py>26,('preview geometry unavailable',preview)
        send(f'move {px} {py}\nsleep 950\n')
        wait(lambda:window(peer)['workspace']['name']!='special:win-minimized','preview drag dwell restores selected destination')
        assert window(target)['workspace']['name']=='special:win-minimized','group preview restored wrong peer'
        send('move 480 550\nsleep 200\nbutton 272 0\nsleep 300\n');stop_drag()
        wait(lambda:any(e['event']=='drop' for e in events('peer')),'file reaches chosen group preview destination')
        assert events('peer')[-1]['value']==payload.as_uri(),events('peer')
        wait(lambda:not state().get('fileDragActive') and not state().get('popupOpen'),'drop clears drag state')
        report['checks'].append(dict(path='group preview chooses exact minimized destination and preserves file drop',preview=preview,peer=events('peer'),otherStillMinimized=True))
        item=next(g for g in state()['taskbarItems'] if target in g['windows'] and peer in g['windows'])
        tx=round(item['x']+item['width']/2)
        start_drag();send(f'move {tx} 13\nsleep 600\n')
        wait(lambda:state().get('popupOpen'),'group chooser for Escape test')
        subprocess.run(['wtype','-s','200','-k','Escape','-s','300'],check=True)
        wait(lambda:not state().get('fileDragActive') and not state().get('popupOpen'),'Escape clears file drag and chooser')
        assert window(target)['workspace']['name']=='special:win-minimized','Escape restored unselected destination'
        send('move 1050 700\nsleep 700\n');assert not state().get('popupOpen'),'cancelled file drag reopened chooser'
        stop_drag();report['checks'].append(dict(path='Escape cancels chooser and subsequent hover without restoring unselected peer'))
        report['result']='pass'
    except Exception as error:
        report['result']='fail';report['error']=repr(error);report['state']=state();report['cursor']=data('cursorpos');report['sourceEvents']=events('source');report['targetEvents']=events('target');report['gtkErrors']=(tmp/'gtk-errors.log').read_text()
    finally:
        stop_drag();ipc('dismiss')
        for p in processes:
            p.terminate()
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        # Remove only stale minimize metadata for our disposable process IDs.
        live={w['address'] for w in data('clients')}
        runtime=Path(__import__('os').environ['XDG_RUNTIME_DIR'])/'hypr-windowctl'
        pids={p.pid for p in processes}
        for sidecar in runtime.glob('*.monitor.json'):
            try:
                if json.loads(sidecar.read_text()).get('pid') in pids and sidecar.name.removesuffix('.monitor.json') not in live:
                    runtime.joinpath(sidecar.name.removesuffix('.monitor.json')).unlink(missing_ok=True);sidecar.unlink()
            except (OSError,ValueError):pass
        if initial.get('address'):ctl('dispatch',f'hl.dsp.focus({{window="address:{initial["address"]}"}})')
        ctl('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
        home.joinpath('.cache/taskbar-file-drag-live-qa.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));assert report['result']=='pass'
