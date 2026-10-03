#!/usr/bin/env python3
"""Physical-output motion audit using disposable Foot, GTK and Qt windows.

Records raw submission geometry and DRM presentation timestamps. Associations
are accepted only for one successful synchronous commit per presentation.
This measures compositor rectangles/cadence, not application pixel repainting.
"""
import argparse, json, subprocess, time
from pathlib import Path
from analyze import analyze

HOME = Path.home()
HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--library', default=str(HERE/'motion-probe-v3.so'))
parser.add_argument('--output', default=str(HOME/'.cache/window-motion-native'))
args = parser.parse_args()
output = Path(args.output); output.mkdir(parents=True, exist_ok=True)
report = {'cases': [], 'failures': [], 'scope': 'Physical output; compositor geometry and presentation cadence; disposable apps only'}
process = None
loaded = False

def ctl(*args):
    return subprocess.check_output(['hyprctl', *args], text=True).strip()
def data(name): return json.loads(ctl(name, '-j'))
def wait(fn, label):
    deadline = time.monotonic() + 7
    while time.monotonic() < deadline:
        value = fn()
        if value: return value
        time.sleep(.05)
    raise AssertionError(label)
def dispatch(expr): return ctl('dispatch', expr)
def window(): return next((w for w in data('clients') if w['pid'] == process.pid), None)
def capture(name, action, delay=.9, reduced=False, expected=None):
    w = window()
    assert json.loads(ctl('motionprobe','start',w['address'],str(process.pid)))['active']
    action()
    time.sleep(delay)
    raw = json.loads(ctl('motionprobe','stop'))
    (output/(name+'.json')).write_text(json.dumps(raw, indent=2))
    case = {'name':name, 'reducedMotion':reduced, **analyze(raw)}
    case['finalRectangle'] = window()['at'] + window()['size']
    case['checks'] = {
        'bounded':not raw['overflow'],
        'nativePairs':case['paired'] > 0 and not raw['ambiguous'],
        'hardwareCompletion':all((p[3]&7)==7 for p in raw['presentations'] if p[7]>=0 and p[6]),
        'settled':case['finalGoalError'] is not None and case['finalGoalError'] <= 1,
    }
    if expected is not None: case['checks']['expectedRectangle'] = case['finalRectangle']==expected
    if reduced: case['checks']['noIntermediateGeometry'] = case['intermediateFrames']==0
    marks=dict(raw.get('marks',[]))
    if 'reduced' in marks:
        later=[f for f in raw['frames'] if f[0]>marks['reduced']]
        case['checks']['midMotionReductionSettles']=bool(later) and all(
            max(abs(a-b) for a,b in zip(f[1:5],f[5:9]))<=1 and not f[12] for f in later)
    # A 33 ms stall is a visible failure even on a 60 Hz output. Refresh-level
    # misses are reported separately; they are not hidden by this coarse gate.
    if case['movingIntervals']: case['checks']['no33msStall'] = case['gapsOver33ms']==0
    if case['geometryUpdates']: case['checks']['no33msGeometryStall'] = case['geometryGapsOver33ms']==0
    if 'maxOvershootPixels' in case: case['checks']['noVisibleOvershoot'] = case['maxOvershootPixels']<=1
    if not all(case['checks'].values()): report['failures'].append(name)
    report['cases'].append(case)
    print(json.dumps(case),flush=True)
    (output/'report.json').write_text(json.dumps(report,indent=2))
def lua(function,*params): ctl('eval',function+'('+','.join(json.dumps(p) for p in params)+')')
def reduced(enabled):
    subprocess.run([str(HOME/'.local/bin/hypr-reduced-motion'),'on' if enabled else 'off'],
                   check=True, stdout=subprocess.DEVNULL)
def arrange():
    address=window()['address']
    lua('hypr_snap_restore',address)
    dispatch(f'hl.dsp.window.resize({{x=600,y=350,window="address:{address}"}})')
    dispatch(f'hl.dsp.window.move({{x=260,y=300,window="address:{address}"}})')
    dispatch(f'hl.dsp.focus({{window="address:{address}"}})')
    dispatch(f'hl.dsp.window.alter_zorder({{mode="top",window="address:{address}"}})')
    time.sleep(.8)
def caption_drag():
    commands=['move 460 288','sleep 60','button 272 1','sleep 30']
    for i in range(1,81): commands.extend([f'move {460+3*i} {288+i}', 'sleep 8'])
    commands.extend(['button 272 0','sleep 60'])
    mon=report['monitor']
    subprocess.run([str(HOME/'.local/share/hypr-window-controls/qa/virtual-pointer'),
                    str(round(mon['width']/mon['scale'])),str(round(mon['height']/mon['scale']))],
                   input='\n'.join(commands)+'\n',text=True,check=True,stdout=subprocess.DEVNULL)

initial = data('activewindow'); cursor=data('cursorpos')
initial_windows = {w['stableId'] for w in data('clients')}
motion=HOME/'.config/hypr/reduced-motion'
motion_bytes=motion.read_bytes() if motion.exists() else None
animations_enabled='bool: true' in ctl('getoption','animations:enabled')
try:
    monitors=data('monitors')
    assert len(monitors)==1 and monitors[0]['x']==0 and monitors[0]['y']==0, 'single physical output fixture'
    report['monitor']=monitors[0]
    result=ctl('plugin','load',args.library)
    assert result=='ok',result
    loaded=True
    for toolkit, command in [
        ('foot',['foot','--app-id=motion-qa-foot','--title=Motion QA Foot','sleep','180']),
        ('gtk',['python3',str(HERE/'gtk.py')]),
        ('qt',['qs','-p',str(HERE/'qt.qml')])]:
        reduced(False)
        with (output/(toolkit+'-stderr.log')).open('w') as err:
            process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=err)
        w=wait(window,toolkit+' map')
        if not w['floating']: dispatch(f'hl.dsp.window.float({{action="set",window="address:{w["address"]}"}})')
        arrange(); address=window()['address']
        capture(toolkit+'-caption-drag',caption_drag,expected=[500,380,600,350])
        arrange()
        capture(toolkit+'-snap-left',lambda:lua('hypr_snap_zone','left',address,False))
        capture(toolkit+'-snap-restore',lambda:lua('hypr_snap_restore',address),expected=[260,300,600,350])
        capture(toolkit+'-maximize',lambda:lua('hypr_snap_zone','maximize',address,False))
        capture(toolkit+'-maximize-restore',lambda:lua('hypr_snap_restore',address),expected=[260,300,600,350])
        def reverse():
            lua('hypr_snap_zone','left',address,False); time.sleep(.12)
            lua('hypr_snap_zone','right',address,False); time.sleep(.12)
            lua('hypr_snap_restore',address)
        capture(toolkit+'-snap-reversal',reverse,expected=[260,300,600,350])
        def reduce_in_flight():
            lua('hypr_snap_zone','left',address,False); time.sleep(.12)
            reduced(True)
            assert json.loads(ctl('motionprobe','mark','reduced'))['marked']
        capture(toolkit+'-reduce-during-snap',reduce_in_flight)
        lua('hypr_snap_restore',address); time.sleep(.2)
        reduced(True)
        capture(toolkit+'-reduced-snap',lambda:lua('hypr_snap_zone','right',address,False),reduced=True)
        capture(toolkit+'-reduced-restore',lambda:lua('hypr_snap_restore',address),reduced=True,expected=[260,300,600,350])
        closed_pid=process.pid
        process.terminate(); process.wait(timeout=5); process=None
        wait(lambda:not any(w['pid']==closed_pid for w in data('clients')),'cleanup')
    report['result']='pass' if not report['failures'] else 'fail'
except Exception as error:
    report['result']='fail'; report['error']=repr(error)
    raise
finally:
    if process:
        process.terminate()
        try: process.wait(timeout=5)
        except subprocess.TimeoutExpired: process.kill(); process.wait()
    if loaded:
        ctl('motionprobe','stop')
        assert ctl('plugin','unload',args.library)=='ok'
    if motion_bytes is None:
        motion.unlink(missing_ok=True)
    else: motion.write_bytes(motion_bytes)
    ctl('eval','hl.config({animations={enabled='+str(animations_enabled).lower()+'}}); hypr_reduced_motion='+
        str(motion_bytes is not None and motion_bytes.strip()==b'1').lower()+
        '; if hypr_motion_changed then hypr_motion_changed(hypr_reduced_motion) end')
    live_windows=data('clients')
    report['originalWindowsPreserved']=initial_windows.issubset({w['stableId'] for w in live_windows})
    if any(w['stableId']==initial.get('stableId') and w['pid']==initial.get('pid') for w in live_windows):
        dispatch(f'hl.dsp.focus({{window="address:{initial["address"]}"}})')
    dispatch(f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
    (output/'report.json').write_text(json.dumps(report,indent=2))
assert report['result']=='pass',report['failures']
