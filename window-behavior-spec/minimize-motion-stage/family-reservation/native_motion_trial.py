#!/usr/bin/env python3
"""Native motion observer for explicitly supplied disposable window identities.

No app launch, pointer/key injection or focus-based pass/fail. Requires deployed
candidate helpers/widget. Original fixture window state is restored in finally.
Only --reduced-motion-trial changes the global motion setting, then restores it.
"""
import argparse,hashlib,json,math,os
from pathlib import Path
import shutil,subprocess,time

BIN=Path.home()/'.local/bin'

def run(argv,timeout=4):
 return subprocess.check_output([str(a) for a in argv],text=True,timeout=timeout).strip()

def windows():return {w['address']:w for w in json.loads(run(['hyprctl','clients','-j']))}
def identity(w):return [w['address'],str(w.get('stableId','')),w.get('pid')]
def rectangle(w):return [*w['at'],*w['size']]
def minimized(w):return w['workspace']['name']=='special:win-minimized'
def visual():return json.loads(run(['omarchy-shell','hoskinson.windows','motionVisualState']))
def records():
 session=hashlib.sha256(os.getenv('HYPRLAND_INSTANCE_SIGNATURE','session').encode()).hexdigest()[:20]
 path=Path(os.getenv('XDG_RUNTIME_DIR',str(Path.home()/'.cache')))/'hypr-window-motion'/session/'pending.json'
 try:return json.loads(path.read_text())
 except (OSError,ValueError):return []

def checked_current(original):
 current=windows()
 for w in original:
  if w['address'] not in current or identity(current[w['address']])!=identity(w):raise RuntimeError('fixture closed or identity changed: '+w['address'])
 return current


def operation(command,w):
 env=dict(os.environ,HYPR_WINDOWCTL_ASYNC='1',HYPR_WINDOWCTL_MOTION='1')
 issued=time.monotonic()
 process=subprocess.Popen([str(BIN/'hypr-windowctl'),command,*[str(v) for v in identity(w)]],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
 process.motionIssuedMono=issued
 return process


def active_sample(original,primary,previous_token=None,duration=3):
 # The compositor image may need hundreds of milliseconds to arrive. Intent
 # reversal is permitted only after matching native readiness and actual tween.
 deadline=time.monotonic()+duration
 while time.monotonic()<deadline:
  checked_current(original)
  observed=time.monotonic()
  frames=visual();pending=records()
  for frame in frames:
   if frame['identity']!=identity(primary) or frame['token']==previous_token:continue
   record=next((r for r in pending if r['token']==frame['token'] and r['identity']==identity(primary)),None)
   if record and record['phase']=='running' and frame['visible'] and frame['imageReady'] and 0<frame['routeProgress']<1:
    image=Path(record['image'])
    digest=hashlib.sha256(image.read_bytes()).hexdigest()
    return {'observed':observed,'finished':time.monotonic(),'visual':frame,'phase':'running','imageDigest':digest,'serviceProfile':record.get('profile',{})}
  time.sleep(.004)
 raise AssertionError('never observed a matching running, in-flight animation before interruption')


class ReversalError(AssertionError):
 def __init__(self,message,diagnostics):super().__init__(message);self.diagnostics=diagnostics

def assert_reversal(before,after,operation):
 old=before['visual'];new=after['visual']
 diagnostics={'before':before,'after':after,'requestedOperation':operation}
 def fail(message):raise ReversalError(message,diagnostics)
 if new['token']==old['token'] or new['identity']!=old['identity'] or new['operation']!=operation:
  fail('reversal did not acquire a fresh token for the same captured identity')
 if before['imageDigest']!=after['imageDigest']:
  fail('reversal replaced the captured window pixels')
 # next.from is sampled by QML when it stops the prior tween. It must lie
 # forward of our last actual observation on that prior route, within the
 # maximum cubic easing velocity (3 / duration), allowing IPC observation time.
 elapsed=after['finished']-before['observed']
 duration=.190 if old['operation']=='minimize' else .230
 lower=old['routeProgress']-.025
 upper=min(1,old['routeProgress']+3*elapsed/duration+.025)
 inferred=[]
 for field in ('x','y','width','height'):
  delta=old['to'][field]-old['from'][field]
  value=new['from'][field]
  if abs(delta)<.01:
   if abs(value-old['from'][field])>.5:fail('stationary rectangle field jumped on reversal')
  else:inferred.append((value-old['from'][field])/delta)
 if not inferred or max(inferred)-min(inferred)>.015:
  fail('reversal start left the previous visual rectangle route')
 progress=sum(inferred)/len(inferred)
 distance_from_start=max(abs(new['from'][field]-old['from'][field]) for field in ('x','y','width','height'))
 distance_from_end=max(abs(new['from'][field]-old['to'][field]) for field in ('x','y','width','height'))
 interior_tolerance=.001
 diagnostics.update(previousProgress=old['routeProgress'],reversalProgress=progress,minimumProgress=lower,maximumProgress=upper,observationGap=elapsed,distanceFromStartPx=distance_from_start,distanceFromEndPx=distance_from_end,interiorTolerance=interior_tolerance)
 if progress<lower or progress>upper or not interior_tolerance<progress<1-interior_tolerance or min(distance_from_start,distance_from_end)<=.5:
  fail('reversal reset/jumped or arrived after the previous animation endpoint')
 return {'sameIdentity':True,'samePixels':True,'strictlyInterior':True,'interiorTolerance':interior_tolerance,'distanceFromStartPx':distance_from_start,'distanceFromEndPx':distance_from_end,'previousProgress':old['routeProgress'],'reversalProgress':progress,'maximumProgress':upper,'observationGap':elapsed}


def assert_freeze_profile(before,after):
 profile=after.get('serviceProfile',{});frozen=profile.get('frozen',{})
 diagnostics={'serviceProfile':profile,'requestIssued':after.get('requestIssued')}
 def fail(message):raise ReversalError(message,diagnostics)
 if not frozen.get('accepted') or not frozen.get('rect'):
  fail('reversal lacks actual accepted QML freeze acknowledgement')
 for field in ('x','y','width','height'):
  if abs(frozen['rect'][field]-after['visual']['from'][field])>.01:
   fail('new route did not start at the actual frozen rectangle')
 for first,last in [('received','freezeSent'),('freezeSent','freezeAck'),('freezeAck','clientsStart'),('clientsStart','clientsDone'),('clientsDone','familyStart'),('familyStart','familyDone'),('familyDone','beginSent')]:
  if first not in profile or last not in profile or profile[first]>profile[last]:
   fail('freeze did not precede metadata preparation: '+first+' -> '+last)
 if frozen['previousToken']!=before['visual']['token'] or frozen['token']!=after['visual']['token']:
  fail('freeze acknowledgement belongs to another visual token')
 return {'capturedRectanglePreserved':True,'freezeBeforeMetadata':True,'priorProgress':frozen.get('routeProgress'),
   'processToReceiptMs':1000*(profile['received']-after['requestIssued']),
   'receiptToFreezeMs':1000*(profile['freezeAck']-profile['received']),
   'freezeToBeginMs':1000*(profile['beginSent']-profile['freezeAck'])}


def record_reversal(report,before,after,operation,require_freeze=False):
 attempt={'operation':operation,'before':before,'after':after}
 report['attempts'].append(attempt)
 try:
  evidence=assert_reversal(before,after,operation)
  if require_freeze:evidence['freezeProfile']=assert_freeze_profile(before,after)
  attempt['passed']=True;attempt['diagnostics']=evidence
  report['continuity'].append(evidence);return evidence
 except ReversalError as error:
  attempt['passed']=False;attempt['error']=str(error);attempt['diagnostics']=error.diagnostics;raise


def observe(original,process,command,report,output,capture=False,duration=3):
 samples=[];deadline=time.monotonic()+duration;begin=time.monotonic();captured=0
 while time.monotonic()<deadline:
  current=checked_current(original)
  frames=visual();pending=records()
  sample={'elapsed':time.monotonic()-begin,'windows':[{**dict(zip(('address','stableId','pid'),identity(current[w['address']]))),'rect':rectangle(current[w['address']]),'minimized':minimized(current[w['address']]),'workspace':current[w['address']]['workspace']['name'],'pinned':current[w['address']]['pinned'],'fullscreen':current[w['address']].get('fullscreen'),'fullscreenClient':current[w['address']].get('fullscreenClient')} for w in original],
          'visuals':[f for f in frames if f['identity'] in [identity(w) for w in original]],
          'phases':[{k:r.get(k) for k in ('token','identity','phase','operation')} for r in pending if r['identity'] in [identity(w) for w in original]]}
  samples.append(sample)
  if capture and sample['visuals'] and captured<8:
   frame=sample['visuals'][0]
   if frame['imageReady'] and 0<frame['routeProgress']<1:
    screenshot=output/(command+'-'+str(captured)+'.png')
    subprocess.run(['grim','-o',frame['screenName'],str(screenshot)],check=True,stdout=subprocess.DEVNULL,timeout=3)
    sample['screenshot']=str(screenshot);captured+=1
  settled=not any(r['identity'] in [identity(w) for w in original] for r in pending)
  if process.poll() is not None and settled and len(samples)>2:break
  time.sleep(.004)
 code=process.wait(timeout=8);error=process.stderr.read()
 if code:raise RuntimeError(command+' helper failed: '+error)
 report.append({'command':command,'samples':samples})
 return samples


def collect_screenshots(original,command,report,output):
 # Screenshots run in a separate replay, after uninstrumented assertions pass.
 # Their renderer/readback cost is reported and never used as a cadence oracle.
 primary=original[0];process=operation(command,primary);shots=[];start=time.monotonic()
 pending_shots=[];deadline=start+3;seen=set();source_frames=[];copied=set()
 while time.monotonic()<deadline:
  frames=[f for f in visual() if f['identity']==identity(primary) and f['imageReady'] and 0<f['routeProgress']<1]
  if frames and len(pending_shots)<3:
   frame=frames[0];bucket=int(frame['routeProgress']*3)
   if frame['token'] not in copied:
    record=next((r for r in records() if r['token']==frame['token']),None)
    if record and record.get('image'):
     destination=output/(command+'-captured-whole-frame.png')
     try:
      destination.write_bytes(Path(record['image']).read_bytes());copied.add(frame['token'])
      source_frames.append({'path':str(destination),'token':frame['token'],'wholeWindow':record.get('wholeWindow',False),'nativeRect':record.get('nativeRect'),'fullRect':record.get('rect'),'identity':record['identity'],'sampledVisual':frame})
     except OSError:pass
   if bucket not in seen:
    seen.add(bucket);path=output/(command+'-capture-'+str(bucket)+'.png')
    begun=time.monotonic()
    shot=subprocess.Popen(['grim','-o',frame['screenName'],str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    pending_shots.append((shot,path,begun,frame))
  if process.poll() is not None and not records():break
  time.sleep(.012)
 code=process.wait(timeout=8)
 if code:raise RuntimeError(process.stderr.read())
 for shot,path,begun,frame in pending_shots:
  code=shot.wait(timeout=8)
  shots.append({'path':str(path),'captureLatency':time.monotonic()-begun,'exitCode':code,'sampledVisual':frame})
 report.append({'command':command,'instrumentedScreenshotReplay':True,'screenshots':shots,'sourceFrames':source_frames,'elapsed':time.monotonic()-start})


def assert_geometry(original):
 current=checked_current(original)
 for w in original:
  actual=current[w['address']]
  if rectangle(actual)!=rectangle(w):raise AssertionError('native geometry changed: '+w['address'])
  if actual['pinned']!=w['pinned'] or actual['workspace']['name']!=w['workspace']['name']:raise AssertionError('native ownership changed: '+w['address'])
  if any(actual.get(field)!=w.get(field) for field in ('fullscreen','fullscreenClient','fullscreenHandler')):raise AssertionError('native maximize/fullscreen state changed: '+w['address'])


def assert_route(samples,command,primary):
 frames=[f for s in samples for f in s['visuals'] if f['identity']==identity(primary) and f['imageReady']]
 in_flight=[f for f in frames if 0<f['routeProgress']<1]
 if len(in_flight)<2:raise AssertionError(command+': fewer than two native in-flight samples; timing/renderer or safe fallback requires investigation')
 last=-1
 for f in frames:
  progress=f['routeProgress']
  if progress+1e-6<last:raise AssertionError(command+': route reversed unexpectedly')
  last=progress
  for field in ('x','y','width','height'):
   expected=f['from'][field]+(f['to'][field]-f['from'][field])*progress
   if not math.isclose(f['rect'][field],expected,abs_tol=.01):raise AssertionError(command+': visual rectangle left endpoint route')
 if not any(s['phases'] for s in samples):raise AssertionError(command+': no native readiness/running acknowledgement sampled')


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--window',action='append',required=True,help='Exact address of each disposable family member; first is primary')
 parser.add_argument('--output',type=Path,required=True)
 parser.add_argument('--capture-frames',action='store_true')
 parser.add_argument('--require-freeze',action='store_true',help='Require actual frozen QML rect + freeze-before-query profile on reversals')
 parser.add_argument('--reduced-motion-trial',action='store_true')
 args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 current=windows();original=[current[address] for address in args.window]
 if any(not w.get('stableId') or not w.get('pid') or minimized(w) or not w['workspace']['name'].isdigit() for w in original):raise RuntimeError('fixtures must be visible numbered-desktop windows with stable ID/PID')
 family=json.loads(subprocess.check_output([str(BIN/'hypr-window-family'),original[0]['address']],input=json.dumps(list(current.values())),text=True,timeout=3))
 if any(w['address'] not in args.window for w in family['windows']):raise RuntimeError('supply every disposable transient-family member; unrelated windows will not be operated on')
 target=json.loads(run(['omarchy-shell','hoskinson.windows','motionTarget',json.dumps(dict(zip(('address','stableId','pid'),identity(original[0]))))]))
 if not target or not target.get('visible'):raise RuntimeError('primary fixture needs an actually visible taskbar icon; missing target would use native fallback')
 motion=json.loads(run([BIN/'hypr-reduced-motion','status']))['reducedMotion']
 if motion and not args.reduced_motion_trial:raise RuntimeError('motion is reduced; opt into --reduced-motion-trial to change and restore the setting')
 report={'original':original,'target':target,'trials':[],'focusIsNotAnOracle':True,'started':time.time()}
 try:
  report['layersBefore']=json.loads(run(['hyprctl','layers','-j']))
  if args.reduced_motion_trial:run([BIN/'hypr-reduced-motion','off'])
  primary=original[0]
  samples=observe(original,operation('minimize',primary),'minimize',report['trials'],args.output,False)
  assert_route(samples,'minimize',primary)
  if any(not minimized(checked_current(original)[w['address']]) for w in original):raise AssertionError('minimize did not hide the captured family')
  cache=Path(os.getenv('XDG_RUNTIME_DIR',str(Path.home()/'.cache')))/'hypr-window-previews'
  for w in original:
   metadata=json.loads((cache/(w['address']+'.json')).read_text())
   if metadata!={'pid':w['pid'],'stableId':w['stableId']}:raise AssertionError('preview metadata identity differs')
   if not (cache/(w['address']+'-0.png')).is_file():raise AssertionError('minimized thumbnail missing')
  samples=observe(original,operation('restore',primary),'restore',report['trials'],args.output,False)
  assert_route(samples,'restore',primary);assert_geometry(original)
  # Explicit identity commands overlap; no pointer or focus dependency.
  rapid={'samples':[],'continuity':[],'attempts':[]};report['activeReversals']=rapid
  first=operation('minimize',primary)
  first_active=active_sample(original,primary)
  first_active['requestIssued']=first.motionIssuedMono;rapid['samples'].append(first_active)
  second=operation('restore',primary)
  second_active=active_sample(original,primary,first_active['visual']['token'])
  second_active['requestIssued']=second.motionIssuedMono;rapid['samples'].append(second_active)
  record_reversal(rapid,first_active,second_active,'restore',args.require_freeze)
  third=operation('minimize',primary)
  third_active=active_sample(original,primary,second_active['visual']['token'])
  third_active['requestIssued']=third.motionIssuedMono;rapid['samples'].append(third_active)
  record_reversal(rapid,second_active,third_active,'minimize',args.require_freeze)
  observe(original,third,'rapid-min-restore-min',report['trials'],args.output,False)
  for process in (first,second):
   if process.wait(timeout=8):raise RuntimeError(process.stderr.read())
  if any(not minimized(checked_current(original)[w['address']]) for w in original):raise AssertionError('latest rapid minimize intent lost')
  observe(original,operation('restore',primary),'rapid-cleanup',report['trials'],args.output,False);assert_geometry(original)
  if args.reduced_motion_trial:
   process=operation('minimize',primary)
   report['reduceInterrupted']=active_sample(original,primary)
   run([BIN/'hypr-reduced-motion','on'])
   observe(original,process,'reduce-during-minimize',report['trials'],args.output,False)
   if any(f['identity'] in [identity(w) for w in original] for f in visual()):raise AssertionError('reduced motion left a live visual')
   observe(original,operation('restore',primary),'restore-reduced',report['trials'],args.output,False);assert_geometry(original)
  if args.capture_frames:
   if args.reduced_motion_trial:run([BIN/'hypr-reduced-motion','off'])
   report['captureTrials']=[]
   collect_screenshots(original,'minimize',report['captureTrials'],args.output)
   collect_screenshots(original,'restore',report['captureTrials'],args.output)
   assert_geometry(original)
  report['passed']=True
 except Exception as error:
  report['passed']=False;report['error']=str(error)
  try:report['pendingAtFailure']=records();report['visualAtFailure']=visual()
  except Exception as inspection:report['inspectionError']=str(inspection)
  raise
 finally:
  try:
   diagnostic=subprocess.run([str(BIN/'hypr-window-motion'),'diagnostics'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=2)
   report['serviceDiagnostics']=json.loads(diagnostic.stdout) if diagnostic.returncode==0 else {'error':diagnostic.stderr.strip()}
  except Exception as inspection:report['diagnosticsError']=str(inspection)
  for w in original:
   now=windows().get(w['address'])
   if now and identity(now)==identity(w) and minimized(now):
    subprocess.run([str(BIN/'hypr-windowctl'),'restore',*[str(v) for v in identity(w)]],env=dict(os.environ,HYPR_WINDOWCTL_ASYNC='0',HYPR_WINDOWCTL_MOTION='1'),stdout=subprocess.DEVNULL,check=False,timeout=10)
  if args.reduced_motion_trial:run([BIN/'hypr-reduced-motion','on' if motion else 'off'])
  report['finished']=time.time();(args.output/'motion-trial.json').write_text(json.dumps(report,indent=2))
 print('Native motion route/acknowledgement/geometry trials passed; report: '+str(args.output/'motion-trial.json'))


if __name__=='__main__':main()
