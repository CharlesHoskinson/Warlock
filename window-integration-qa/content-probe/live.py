#!/usr/bin/env python3
"""Physical display repaint/movement under bounded CPU and browser workload."""
import argparse,hashlib,http.server,json,os,subprocess,tempfile,threading,time
from pathlib import Path
from analyze import analyze
# Avoid importing two modules under the same name.
import importlib.util
_spec=importlib.util.spec_from_file_location('geometry_analysis',Path(__file__).resolve().parents[1]/'motion-probe/analyze.py')
_geometry=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_geometry)
H=Path.home();HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(H/'.cache/window-content-native'))
parser.add_argument('--library',default=str(HERE/'content-probe-v3.so'))
parser.add_argument('--no-input',action='store_true',help='Use compositor geometry requests; no caption or native focus claim')
args=parser.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
report={'cases':[],'failures':[],'scope':'One physical output; animated content and bounded load; disposable apps'}
report['movementInput']='compositor requests' if args.no_input else 'virtual caption input'
process=None;workers=[];loaded=False;state={'work':0,'browser':{}}
def ctl(*a):return subprocess.check_output(['hyprctl',*a],text=True).strip()
def data(name):return json.loads(ctl(name,'-j'))
def dispatch(code):return ctl('dispatch',code)
def wait(fn,label):
    until=time.monotonic()+10
    while time.monotonic()<until:
        value=fn()
        if value:return value
        time.sleep(.05)
    raise AssertionError(label)
def window():return next((w for w in data('clients') if w['pid']==process.pid or w['title'].startswith('Content repaint QA') and w['pid'] in pids()),None)
def pids():
    # Browser may publish its main PID through a launcher that execs it.
    return {process.pid}
def lua(name,*values):return ctl('eval',name+'('+','.join(json.dumps(v) for v in values)+')')
def arrange():
    w=window();a=w['address']
    if not w['floating']:dispatch(f'hl.dsp.window.float({{action="set",window="address:{a}"}})')
    lua('hypr_snap_restore',a)
    dispatch(f'hl.dsp.window.resize({{x=600,y=350,window="address:{a}"}})')
    dispatch(f'hl.dsp.window.move({{x=260,y=300,window="address:{a}"}})')
    dispatch(f'hl.dsp.focus({{window="address:{a}"}})')
    dispatch(f'hl.dsp.window.alter_zorder({{mode="top",window="address:{a}"}})')
    time.sleep(1)
def capture(toolkit,load):
    state['work']=8 if toolkit=='browser' and load else 0
    if load:
        for _ in range(2):workers.append(subprocess.Popen(['python3','-c','import math,time\nend=time.monotonic()+20\nwhile time.monotonic()<end:\n for i in range(5000): math.sin(i)'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL))
    try:
        arrange();w=window();name=toolkit+('-load' if load else '-baseline')
        before=out/(name+'-before.png');after=out/(name+'-after.png')
        subprocess.run(['grim','-T',w['stableId'],str(before)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        assert json.loads(ctl('contentprobe','start',w['address'],str(w['pid'])))['active']
        time.sleep(.6);assert json.loads(ctl('contentprobe','mark','begin'))['marked']
        if toolkit=='browser':report.setdefault('browserStates',{})[name+'-begin']=dict(state['browser'])
        # Continuous content while compositor movement, snap and exact restore
        # exercise the same visible client under bounded application workload.
        commands=['move 460 288','sleep 60','button 272 1','sleep 30']
        for i in range(1,81):commands.extend([f'move {460+3*i} {288+i}','sleep 8'])
        commands.extend(['button 272 0','sleep 100'])
        if args.no_input:
            # A privileged overlay's exclusive grab invalidates caption/focus
            # testing. Explicit geometry requests still measure rendering of
            # this fully visible disposable client below that overlay.
            for i in range(1,25):
                dispatch(f'hl.dsp.window.move({{x={260+10*i},y={300+80*i/24},window="address:{w["address"]}"}})')
                time.sleep(.02)
        else:
            subprocess.run([str(H/'.local/share/hypr-window-controls/qa/virtual-pointer'),'1600','1000'],input='\n'.join(commands)+'\n',text=True,check=True,stdout=subprocess.DEVNULL)
        time.sleep(.4);lua('hypr_snap_zone','left',w['address'],False);time.sleep(.8)
        lua('hypr_snap_restore',w['address']);time.sleep(1)
        assert json.loads(ctl('contentprobe','mark','end'))['marked'];raw=json.loads(ctl('contentprobe','stop'))
        (out/(name+'.json')).write_text(json.dumps(raw,indent=2))
        subprocess.run(['grim','-T',w['stableId'],str(after)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        metrics=analyze(raw);geometry=_geometry.analyze(raw)
        checks={'bounded':not raw['overflow'],'unambiguous':raw['ambiguous']==0,
                'contentObserved':metrics['distinctObservedEpochs']>=30,
                'hardwareClock':metrics['allHardwareClockCompletion'] and metrics['negativeAges']==0,
                'no100msContentStall':metrics['observedContentGapsMs']['count']>0 and metrics['observedContentGapsMs']['over100ms']==0,
                'exactMovedRectangleRestored':window()['at']+window()['size']==[500,380,600,350],
                'differentNativePixels':hashlib.sha256(before.read_bytes()).digest()!=hashlib.sha256(after.read_bytes()).digest(),
                'no100msGeometryStall':geometry['geometryGapsOver33ms']==0 or geometry['maxGeometryGapMs']<=100}
        if toolkit=='browser':
            latest=state['browser'];report['browserStates'][name+'-end']=dict(latest)
            checks['browserRAFActive']=len(latest.get('frames',[]))>=60
            if load:checks['boundedBrowserWork']=latest.get('work')==8 and latest.get('iterations',0)>0
        case={'name':name,'load':{'cpuWorkers':2 if load else 0,'browserWorkMs':state['work']},'checks':checks,'content':metrics,'geometry':geometry}
        report['cases'].append(case)
        if not all(checks.values()):report['failures'].append(name)
        print(json.dumps(case),flush=True)
    finally:
        for worker in workers:
            worker.terminate();worker.wait(timeout=3)
        workers.clear();state['work']=0
class Server(http.server.BaseHTTPRequestHandler):
    def log_message(self,*a):pass
    def do_GET(self):
        payload=(HERE/'browser.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(payload)
    def do_POST(self):
        state['browser']=json.loads(self.rfile.read(min(2000000,int(self.headers.get('Content-Length','0')))))
        payload=json.dumps({'work':state['work']}).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(payload)
initial=data('activewindow');cursor=data('cursorpos');original={w['stableId'] for w in data('clients')}
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Server);threading.Thread(target=server.serve_forever,daemon=True).start()
motion=H/'.config/hypr/reduced-motion';saved=motion.read_bytes() if motion.exists() else None
animations='bool: true' in ctl('getoption','animations:enabled')
try:
    mon=data('monitors');assert len(mon)==1 and mon[0]['width']/mon[0]['scale']==1600 and mon[0]['height']/mon[0]['scale']==1000
    report['monitor']=mon[0];assert ctl('plugin','load',args.library)=='ok';loaded=True
    subprocess.run([str(H/'.local/bin/hypr-reduced-motion'),'off'],check=True,stdout=subprocess.DEVNULL)
    with tempfile.TemporaryDirectory(prefix='window-content-brave-') as profile:
        for toolkit,command in [('gtk',['python3',str(HERE/'gtk.py')]),('qt',['qs','-p',str(HERE/'qt.qml')]),
              ('browser',['/usr/bin/brave','--user-data-dir='+profile,'--no-first-run','--disable-extensions','--disable-sync','--disable-background-networking','--disable-component-update','--disable-default-apps','--no-default-browser-check',f'http://127.0.0.1:{server.server_port}/'])]:
            with (out/(toolkit+'-stderr.log')).open('w') as err:process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=err)
            wait(window,toolkit+' mapped')
            if toolkit=='browser':wait(lambda:state['browser'].get('ready'),'browser ready')
            capture(toolkit,False);capture(toolkit,True)
            pid=process.pid;process.terminate();process.wait(timeout=8);process=None
            wait(lambda:not any(w['pid']==pid for w in data('clients')),'fixture closed')
    report['result']='pass' if not report['failures'] else 'fail'
except Exception as e:report['error']=repr(e);report['result']='fail';raise
finally:
    if process:
        process.terminate()
        try:process.wait(timeout=8)
        except subprocess.TimeoutExpired:process.kill();process.wait()
    for worker in workers:worker.terminate();worker.wait(timeout=3)
    if loaded:ctl('contentprobe','stop');assert ctl('plugin','unload',args.library)=='ok'
    if saved is None:motion.unlink(missing_ok=True)
    else:motion.write_bytes(saved)
    ctl('eval','hl.config({animations={enabled='+str(animations).lower()+'}}); hypr_reduced_motion='+str(saved is not None and saved.strip()==b'1').lower()+'; if hypr_motion_changed then hypr_motion_changed(hypr_reduced_motion) end')
    live=data('clients');report['originalWindowsPreserved']=original.issubset({w['stableId'] for w in live})
    if any(w['stableId']==initial.get('stableId') and w['pid']==initial.get('pid') for w in live):dispatch(f'hl.dsp.focus({{window="address:{initial["address"]}"}})')
    dispatch(f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})');server.shutdown();server.server_close()
    (out/'report.json').write_text(json.dumps(report,indent=2))
assert report['result']=='pass',report['failures']
