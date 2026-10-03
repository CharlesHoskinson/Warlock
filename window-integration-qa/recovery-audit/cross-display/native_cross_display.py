#!/usr/bin/env python3
"""Actual GTK file drag through per-display taskbars; execute only in a granted GUI slot."""
import argparse,hashlib,json,math,os,socket,subprocess,tempfile,time,traceback
from pathlib import Path

HERE=Path(__file__).resolve().parent
HOME=Path.home()
NAME='WINDOW-PARITY-FILE-DRAG-QA'
FILES=[HOME/'.config/omarchy'/name for name in ('virtual-desktops.json','taskbar-settings.json','taskbar-order.json','taskbar-session-order.json')]
POINTER=HOME/'.local/share/hypr-window-controls/qa/virtual-pointer'
IPC_RETRIES=[]

def command(*args):
    return subprocess.check_output(list(map(str,args)),text=True,timeout=12).strip()
def ctl(*args):return command('hyprctl',*args)
def data(*args):return json.loads(ctl(*args,'-j'))
def ipc(method,*args):
    # IPC ownership follows the monitor poll. A focus transition may briefly
    # leave no enabled owner. Retry diagnostic reads and retain the evidence.
    deadline=time.monotonic()+2
    while True:
        response=command('qs','-p','/usr/share/omarchy/shell','ipc','call','hoskinson.windows',method,*args)
        try:return json.loads(response)
        except json.JSONDecodeError:
            IPC_RETRIES.append({'method':method,'response':response,'time':time.monotonic()})
            if time.monotonic()>=deadline:raise
            time.sleep(.1)
def wait(fn,label,timeout=8):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        result=fn()
        if result:return result
        time.sleep(.1)
    raise AssertionError(label)
def a11y():
    path=Path(os.environ['XDG_RUNTIME_DIR'])/'at-spi/bus_0'
    if not path.exists():return {'exists':False}
    stat=path.stat();connection=socket.socket(socket.AF_UNIX);connection.settimeout(1)
    try:connection.connect(str(path));connected=True
    except OSError:connected=False
    finally:connection.close()
    return {'exists':True,'dev':stat.st_dev,'inode':stat.st_ino,'connects':connected}
def key(w):return [w.get('address'),w.get('pid'),w.get('stableId')]
def monitor_key(m):return {name:m.get(name) for name in ('name','width','height','refreshRate','x','y','scale','transform','reserved')}
def file_bytes(path):return path.read_bytes() if path.exists() else None
def lua_string(value):return json.dumps(value)

class Trial:
    def __init__(self):
        self.report={'checks':[],'kind':'native physical plus temporary headless output; no physical hotplug claim'}
        self.processes=[];self.held=None;self.created=False
    def check(self,name,value,**evidence):
        self.report['checks'].append(dict(name=name,pass_=bool(value),**evidence))
        if not value:raise AssertionError(name)
    def states(self):return ipc('stateAll')
    def remote(self):return ipc('stateForMonitor',str(self.monitor['id']))
    def current(self,address):return next(w for w in data('clients') if w['address']==address)
    def focus(self,address):ctl('dispatch',f'hl.dsp.focus({{window="address:{address}"}})')
    def minimized(self,address):return self.current(address)['workspace']['name']=='special:win-minimized'
    def minimize(self,address):
        command(HOME/'.local/bin/hypr-windowctl','minimize',address)
        wait(lambda:self.minimized(address),'fixture minimized')
    def send(self,text):
        self.held.stdin.write(text);self.held.stdin.flush()
        # Pointer commands are queued on a pipe. Wait for every requested dwell
        # before asserting; flushing alone does not mean the compositor saw it.
        dwell=sum(float(line.split()[1])/1000 for line in text.splitlines() if line.startswith('sleep '))
        time.sleep(dwell+.18)
    def stop(self):
        if self.held:
            self.held.stdin.close()
            try:self.held.wait(timeout=3)
            except subprocess.TimeoutExpired:self.held.terminate();self.held.wait(timeout=3)
            self.held=None
    def start(self):
        self.focus(self.source)
        self.held=subprocess.Popen([str(POINTER),str(self.extent[0]),str(self.extent[1])],stdin=subprocess.PIPE,text=True)
        x,y=self.body(self.source)
        self.send(f'move {x+30} {y+30}\nsleep 120\nmove {x} {y}\nsleep 120\nbutton 272 1\nsleep 120\nmove {x+40} {y}\nsleep 160\n')
        wait(lambda:any(s.get('fileDragActive') for s in self.states()),'native drag relay active')
    def body(self,address):
        w=self.current(address);return round(w['at'][0]+w['size'][0]/2),round(w['at'][1]+w['size'][1]/2)
    def icon(self,addresses):
        def find():
            state=self.remote()
            item=next((item for item in state.get('taskbarItems',[]) if set(addresses).issubset(item['windows'])),None)
            return (state,item) if item and item['height']>0 else None
        state,item=wait(find,'destination taskbar entry')
        m=state['monitorGeometry'];offset=state['barOffset']
        return round(m['x']+offset['x']+item['x']+item['width']/2),round(m['y']+offset['y']+item['y']+item['height']/2)
    def events(self,name):
        path=self.tmp/(name+'.jsonl')
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    def launch(self,mode,name,app_id,monitor,x,y):
        environment=os.environ.copy();environment.update(NO_AT_BRIDGE='1',GTK_A11Y='none')
        p=subprocess.Popen(['python3',str(HERE/'filelist_probe_gtk.py'),app_id,'File drag QA '+name,mode,str(self.payload),str(self.tmp/(name+'.jsonl')),str(self.tmp/(name+'-copies'))],env=environment,stdout=subprocess.DEVNULL,stderr=self.errors)
        self.processes.append(p)
        address=wait(lambda:next((w['address'] for w in data('clients') if w['pid']==p.pid),None),'GTK fixture creates native window')
        ctl('dispatch',f'hl.dsp.window.move({{monitor={lua_string(monitor)},window="address:{address}"}})')
        ctl('dispatch',f'hl.dsp.window.move({{x={x},y={y},window="address:{address}"}})')
        time.sleep(.35);return address
    def drop(self,address,name):
        before=len([e for e in self.events(name) if e['event']=='drop'])
        wait(lambda:not any(v['identity'][0]==address for v in ipc('motionVisualState')),'destination motion settles before native drop')
        x,y=self.body(address)
        evidence={'before':self.current(address),'move':[x,y],'cursorBefore':data('cursorpos'),'statesBefore':self.states(),'motionBefore':ipc('motionVisualState')}
        # Focus can warp to the destination center. Send a real nonzero motion
        # into the content before the center; a no-op absolute event is not an
        # independent native DnD target-entry check.
        self.send(f'move {x+30} {y+30}\nsleep 120\nmove {x} {y}\nsleep 500\n')
        evidence.update(cursor=data('cursorpos'),statesUnderPointer=self.states(),windowUnderPointer=self.current(address),nativeDrag=ctl('eval','return hl.plugin.hyprbars.file_drag_active()'))
        self.report.setdefault('dropDiagnostics',[]).append(evidence)
        self.send('button 272 0\nsleep 300\n');self.stop()
        drops=wait(lambda:[e for e in self.events(name) if e['event']=='drop'] if len([e for e in self.events(name) if e['event']=='drop'])>before else None,'actual native FileList destination copy')
        event=drops[-1];copy=Path(event['copy']).read_bytes()
        self.check('actual FileList copy '+name,event['nativeType']=='Gdk.FileList' and event['sha256']==self.digest and copy==self.payload.read_bytes(),event=event)
        wait(lambda:all(not s['fileDragActive'] and not s['popupOpen'] for s in self.states()),'drop clears every taskbar')
    def perform(self):
        # Queries and diagnostics readiness occur before the first mutation.
        self.original_monitors=data('monitors');self.original_clients=data('clients')
        self.original_focus=data('activewindow');self.original_cursor=data('cursorpos');self.original_a11y=a11y()
        self.backups={path:file_bytes(path) for path in FILES}
        assert self.original_monitors and not any(m['name']==NAME for m in self.original_monitors)
        assert all(m['x']>=0 and m['y']>=0 for m in self.original_monitors),'virtual pointer requires nonnegative layout'
        assert isinstance(self.states(),list),'read-only multioutput diagnostic API not deployed'
        self.physical=next((m for m in self.original_monitors if m.get('focused')),self.original_monitors[0])
        assert self.physical['width']/self.physical['scale']>=900 and self.physical['height']/self.physical['scale']>=700
        self.headless_x=math.ceil(max(m['x']+m['width']/m['scale'] for m in self.original_monitors))
        self.extent=[self.headless_x+1280,math.ceil(max(720,*[m['y']+m['height']/m['scale'] for m in self.original_monitors]))]
        self.report['before']={'monitors':self.original_monitors,'clients':[key(w) for w in self.original_clients],'focus':key(self.original_focus),'cursor':self.original_cursor,'a11y':self.original_a11y,'catalogHashes':{str(p):hashlib.sha256(b).hexdigest() if b is not None else None for p,b in self.backups.items()}}
        with tempfile.TemporaryDirectory(prefix='native-cross-display-') as tmp:
            self.tmp=Path(tmp);self.payload=self.tmp/'copy payload with spaces.bin'
            self.payload.write_bytes(bytes(range(256))*1024+b'Native taskbar drag\x00\xff\n')
            self.digest=hashlib.sha256(self.payload.read_bytes()).hexdigest()
            with (self.tmp/'gtk-errors.log').open('a') as self.errors:
                try:
                    # Freeze existing monitor positions while the temporary output is created.
                    for m in self.original_monitors:
                        ctl('eval',f'hl.monitor({{output={lua_string(m["name"])},mode="{m["width"]}x{m["height"]}@{m["refreshRate"]}",position="{m["x"]}x{m["y"]}",scale={m["scale"]}}})')
                    ctl('output','create','headless',NAME);self.created=True
                    ctl('eval',f'hl.monitor({{output="{NAME}",mode="1920x1080@60",position="{self.headless_x}x0",scale=1.5}})')
                    self.monitor=wait(lambda:next((m for m in data('monitors') if m['name']==NAME and m['scale']==1.5 and m['x']==self.headless_x),None),'fractional second output configured')
                    wait(lambda:any(s['currentMonitor']==self.monitor['id'] for s in self.states()),'real shell destination taskbar exists')
                    for setting,value in [('displayMode','monitor'),('desktopScope','all'),('combineMode','always')]:
                        command(HOME/'.local/bin/hypr-taskbar','config',setting,value)
                    self.target=self.launch('target','target','org.omarchy.CrossDragTargetQA',NAME,self.headless_x+200,200)
                    self.source=self.launch('source','source','org.omarchy.CrossDragSourceQA',self.physical['name'],self.physical['x']+500,self.physical['y']+450)
                    self.start();self.drop(self.target,'target')
                    self.check('direct cross-display baseline owns destination output',self.current(self.target)['monitor']==self.monitor['id'])
                    self.minimize(self.target);tx,ty=self.icon([self.target])
                    self.start();sx,sy=self.body(self.source)
                    self.send(f'move {tx} {ty}\nsleep 150\nmove {sx} {sy}\nsleep 1000\n')
                    self.check('leave remote taskbar before dwell preserves minimized target',self.minimized(self.target))
                    self.send('button 272 0\nsleep 200\n');self.stop()
                    self.start();self.send(f'move {tx} {ty}\nsleep 1400\n')
                    wait(lambda:not self.minimized(self.target),'remote singleton restored')
                    self.check('remote singleton restore retains destination identity and display',self.current(self.target)['monitor']==self.monitor['id'] and data('activewindow')['address']==self.target)
                    self.drop(self.target,'target')
                    self.peer=self.launch('target','peer','org.omarchy.CrossDragTargetQA',NAME,self.headless_x+200,200)
                    for address in [self.target,self.peer]:self.minimize(address)
                    tx,ty=self.icon([self.target,self.peer]);self.start();self.send(f'move {tx} {ty}\nsleep 1100\n')
                    chooser=wait(lambda:self.remote() if self.remote()['popupOpen'] and len(self.remote()['previewItems'])==2 else None,'destination group preview')
                    self.check('remote group chooser preserves both minimized destinations',all(self.minimized(a) for a in [self.target,self.peer]),chooser=chooser)
                    preview=next(p for p in chooser['previewItems'] if p['address']==self.peer)
                    px=round(self.monitor['x']+preview['x']+preview['width']/2);py=round(self.monitor['y']+preview['y']+preview['height']/2)
                    self.send(f'move {px} {py}\nsleep 1100\n')
                    wait(lambda:not self.minimized(self.peer),'remote exact peer preview restore')
                    self.check('remote preview restores exact peer only',self.minimized(self.target) and self.current(self.peer)['monitor']==self.monitor['id'])
                    self.drop(self.peer,'peer')
                    self.minimize(self.peer);tx,ty=self.icon([self.target,self.peer])
                    self.start();self.send(f'move {tx} {ty}\nsleep 650\n')
                    wait(lambda:self.remote()['popupOpen'],'remote chooser before cancel')
                    command('wtype','-k','Escape');time.sleep(.3)
                    wait(lambda:all(not s['fileDragActive'] and not s['popupOpen'] for s in self.states()),'native Escape clears all outputs')
                    self.send(f'move {sx} {sy}\nsleep 700\n')
                    self.check('cancel preserves minimized destinations and clears remote hover',all(self.minimized(a) for a in [self.target,self.peer]) and all(not s['popupOpen'] for s in self.states()))
                    self.send('button 272 0\nsleep 200\n')
                    self.stop()
                    # Output disappearance is an independent scenario. Use a
                    # fresh GTK gesture rather than inheriting backend gesture
                    # cancellation state from the preceding Escape scenario.
                    self.source=self.launch('source','source2','org.omarchy.CrossDragSourceQA',self.physical['name'],self.physical['x']+500,self.physical['y']+450)
                    sx,sy=self.body(self.source)
                    self.start();self.send(f'move {tx} {ty}\nsleep 650\n')
                    wait(lambda:self.remote()['popupOpen'],'remote chooser before output removal')
                    ctl('output','remove',NAME);self.created=False
                    self.send(f'move {sx} {sy}\nsleep 100\n')
                    command('wtype','-k','Escape');self.stop()
                    wait(lambda:all(not s['fileDragActive'] and not s['popupOpen'] for s in self.states()),'output removal clears active chooser')
                    self.check('output removal drops orphan widget and preserves unselected minimized clients',all(s['currentMonitor']!=self.monitor['id'] for s in self.states()) and all(self.minimized(a) for a in [self.target,self.peer]))
                    self.check('copy action preserves source bytes and never requests deletion',hashlib.sha256(self.payload.read_bytes()).hexdigest()==self.digest and all(not e.get('delete',False) for name in ('source','source2') for e in self.events(name)))
                    self.report['events']={name:self.events(name) for name in ('source','source2','target','peer')}
                    self.report['result']='pass'
                except Exception as error:
                    self.report.update(result='fail',error=repr(error),traceback=traceback.format_exc())
                    self.report['events']={name:self.events(name) for name in ('source','source2','target','peer')}
                finally:
                    self.cleanup()
                    self.report['gtkErrors']=(self.tmp/'gtk-errors.log').read_text()
                    self.report['diagnosticEmptyRetries']=IPC_RETRIES
        return self.report
    def cleanup(self):
        cleanup_errors=[]
        def attempt(fn):
            try:fn()
            except Exception as error:cleanup_errors.append(repr(error))
        # Cancel native DnD before releasing the held button, so failure cleanup
        # cannot accidentally drop our file into another application.
        if self.held:attempt(lambda:command('wtype','-k','Escape'))
        attempt(self.stop)
        for p in self.processes:
            p.terminate()
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        attempt(lambda:wait(lambda:not any(w['pid'] in {p.pid for p in self.processes} for w in data('clients')),'fixture clients close'))
        if any(m['name']==NAME for m in data('monitors')):attempt(lambda:ctl('output','remove',NAME))
        time.sleep(.8)
        runtime=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr-windowctl'
        live={w['address'] for w in data('clients')};pids={p.pid for p in self.processes}
        for sidecar in runtime.glob('*.monitor.json'):
            try:
                address=sidecar.name.removesuffix('.monitor.json')
                if json.loads(sidecar.read_text()).get('pid') in pids and address not in live:
                    runtime.joinpath(address).unlink(missing_ok=True);sidecar.unlink()
            except (OSError,ValueError):pass
        for path,contents in self.backups.items():
            if contents is None:path.unlink(missing_ok=True)
            else:path.write_bytes(contents)
        attempt(lambda:ctl('reload'));time.sleep(.6)
        attempt(lambda:self.focus(self.original_focus['address']) if self.original_focus.get('address') else None)
        attempt(lambda:ctl('dispatch',f'hl.dsp.cursor.move({{x={self.original_cursor["x"]},y={self.original_cursor["y"]}}})'))
        after=data('clients');states=self.states()
        preserved={tuple(key(w)) for w in after}=={tuple(key(w)) for w in self.original_clients}
        self.report['restoration']={'clientIdentities':preserved,'clientWorkspaceAndPinned':all(next((a for a in after if key(a)==key(w)),{}).get('workspace')==w.get('workspace') and next((a for a in after if key(a)==key(w)),{}).get('pinned')==w.get('pinned') for w in self.original_clients),'outputs':sorted([monitor_key(m) for m in data('monitors')],key=lambda m:m['name'])==sorted([monitor_key(m) for m in self.original_monitors],key=lambda m:m['name']),'catalogBytes':all(file_bytes(p)==b for p,b in self.backups.items()),'focus':key(data('activewindow'))==key(self.original_focus),'cursor':data('cursorpos')==self.original_cursor,'a11y':a11y()==self.original_a11y,'dragCleared':all(not s['fileDragActive'] and not s['popupOpen'] for s in states),'configErrors':ctl('configerrors')=='','fixtureProcessesExited':all(p.poll() is not None for p in self.processes)}
        self.report['restoration']['clientGeometry']=all(next((a for a in after if key(a)==key(w)),{}).get('at')==w.get('at') and next((a for a in after if key(a)==key(w)),{}).get('size')==w.get('size') and next((a for a in after if key(a)==key(w)),{}).get('fullscreen')==w.get('fullscreen') for w in self.original_clients)
        if cleanup_errors or not all(self.report['restoration'].values()):
            self.report['result']='fail';self.report['cleanupErrors']=cleanup_errors

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    if not args.execute:
        print('Staged only. Requires root-granted GUI slot and deployed stateAll/stateForMonitor diagnostics. No GUI or compositor mutations executed.');return
    trial=Trial()
    try:report=trial.perform()
    except Exception as error:report={'result':'fail','preflightError':repr(error)}
    (HERE/'native-cross-display-report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    if report.get('result')!='pass':raise SystemExit(1)
if __name__=='__main__':main()
