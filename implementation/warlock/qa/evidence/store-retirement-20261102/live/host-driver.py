#!/usr/bin/env python3
"""ROOT-only checked physical-QMP current-product component journey.
Run with existing pixelrag Python (Pillow); no work on import, no unchecked input.
Every event gets its own fresh complete guest fence and exclusive adapter receipt.
"""
import argparse,hashlib,importlib.util,json,os,shlex,stat,subprocess,sys,time
from pathlib import Path
from PIL import Image,ImageChops

if sys.flags.optimize != 0: raise RuntimeError('Guard assertions require nonoptimized Python')

VM=Path('/home/charl/vm/omarchy')
REPOSITORY=Path('/home/charl/code/Warlock')
OLD=VM/'evidence/warlock-ui-mvp-20261101/actual-app-20261101T1058Z/engine-idle-20261101T172728Z'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def stable_json(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def write_new(path,value):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as out:json.dump(value,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('stage',type=Path)
 parser.add_argument('--guest-controller')
 parser.add_argument('--guest-qa-run')
 parser.add_argument('--templates',type=Path,default=OLD)
 args=parser.parse_args()
 assert args.stage.is_absolute() and args.templates.is_absolute()
 stage=json.loads(args.stage.read_bytes());root=stage['guestRoot'];evidence=Path(stage['hostEvidence'])
 os.chdir(VM)  # Existing qmp.py helpers resolve the owned socket in this cwd.
 assert evidence.is_absolute() and evidence.is_dir() and not evidence.is_symlink()
 assert REPOSITORY!=evidence.resolve() and REPOSITORY not in evidence.resolve().parents
 assert stage['originalTrialDurationSeconds']==28 and root.startswith('/home/charl/warlock-live-usability-')
 out=evidence/'run-01';out.mkdir(mode=0o700)
 receipts=out/'qmp-receipts';receipts.mkdir(mode=0o700)
 controller=args.guest_controller or root+'/live-usability-controller.py'
 qa=args.guest_qa_run or root+'/qa-mocks/qa_run.py'
 adapter_path=evidence/'qa-mocks/terra-vm-qmp-receipts-1902.py'
 assert sha(adapter_path)==stage['stagedHelperSHA256']['terra-vm-qmp-receipts-1902.py']
 spec=importlib.util.spec_from_file_location('owned_checked_qmp',adapter_path);adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
 report={'schema':1,'scope':'Actual current Elm/Haskell application-only usability on Omarchy VM; not native/release/AT/IME/provider qualification',
  'stageSha256':sha(args.stage),'originalDurationSeconds':28,'nativeAccepted':False,'releaseAccepted':False,'providerCleanupQualified':False,
  'events':[],'screenshots':[],'completedPhysicalSequence':False,'semanticVerdict':'Requires Root visual review of positive-foot and negative-footz screenshots; no automatic text/DOM semantic proof.',
  'noBackendWindowEffectsRequested':True,'physicalInputNature':'QEMU-injected guest pointer/key events, not hardwareinput qualification'}
 expected=None;sequence=0;screen_sequence=0;current_box=None;current_key=None;button_down=False;launcher_pid=None
 def ssh(command,timeout=3):
  process=subprocess.run([str(VM/'ssh.sh'),command],cwd=VM,capture_output=True,text=True,timeout=timeout)
  if process.returncode:raise RuntimeError('Guest command refused '+process.stderr[-400:])
  return process.stdout
 def probe():
  begun=time.monotonic()
  raw=ssh('python3 -B '+shlex.quote(controller)+' probe '+shlex.quote(root),timeout=2.5)
  value=json.loads(raw);value['hostProbeSeconds']=time.monotonic()-begun
  return value
 def attempt_identity(value):return hashlib.sha256(stable_json(value['identity']).encode()).hexdigest()
 def fail_receipt(predicate,action,extra=None):
  assert predicate and all(ch.isalnum() or ch=='-' for ch in predicate)
  entry={'kind':'failed-predicate','predicate':predicate,'sequence':sequence,'action':action,'targetBox':list(current_box) if current_box is not None else None}
  if extra:entry.update(extra)
  report['events'].append(entry);write_new(receipts/f'failed-predicate-{sequence:04d}-{len(report["events"]):04d}-{predicate}.json',entry)
 def check_pred(ok,predicate,action):
  if not ok:fail_receipt(predicate,action);assert False,predicate
 def guard_region(value,box,action='guard'):
  x0,y0,x1,y1=box;x,y=value['client']['at'];w,h=value['client']['size']
  check_pred(x<=x0<x1<=x+w and y<=y0<y1<=y+h,'client-bounds',action)
  for other in value['clients']:
   if other.get('address')==value['client']['address'] or not other.get('mapped') or other.get('hidden') or other.get('visible') is False:continue
   a,b=other['at'];c,d=other['size'];check_pred(x1<=a or a+c<=x0 or y1<=b or b+d<=y0,'foreign-client-disjoint',action)
  levels=value['layers'][value['monitor']['name']]['levels'];check_pred(set(levels)=={'0','1','2','3'},'layer-levels-complete',action)
  for level in ('2','3'):
   for layer in levels[level]:
    a,b,c,d=[layer[k] for k in ('x','y','w','h')];check_pred(x1<=a or a+c<=x0 or y1<=b or b+d<=y0,'overlay-layer-disjoint',action)
 def fence(encoded,action):
  value=probe();check_pred(value['identity']==expected,'identity-match',action)
  check_pred(current_box is not None,'target-box-present',action)
  guard_region(value,current_box,action)
  payload=json.loads(encoded)
  check_pred(set(payload)=={'execute','arguments'},'payload-envelope',action)
  x0,y0,x1,y1=current_box
  if action=='key':
   check_pred(current_key in 'footz','key-allowlist',action)
   check_pred(payload=={'execute':'send-key','arguments':{'keys':[{'type':'qcode','data':current_key}],'hold-time':60}},'key-payload-shape',action)
   cursor=value['cursor'];check_pred(x0<=cursor['x']<x1 and y0<=cursor['y']<y1,'cursor-in-target-box',action)
  else:
   check_pred(payload['execute']=='input-send-event' and set(payload['arguments'])=={'events'},'pointer-payload-shape',action)
   events=payload['arguments']['events']
  if action=='motion':
   check_pred(len(events)==2,'motion-event-count',action)
   for event,axis,low,high,extent in zip(events,('x','y'),(x0,y0),(x1,y1),(1280,800)):
    check_pred(event['type']=='abs' and event['data']['axis']==axis,'motion-axis-type',action)
    coordinate=event['data']['value']
    center=(low+high)//2
    permitted={center*32767//extent}
    if axis=='x':permitted.add((center-3)*32767//extent)
    check_pred(type(coordinate) is int and coordinate in permitted,'motion-coordinate-permitted',action)
  elif action in ('press','release'):
   check_pred(len(events)==1 and events[0]=={'type':'btn','data':{'down':action=='press','button':'left'}},'button-event-shape',action)
   cursor=value['cursor'];check_pred(x0<=cursor['x']<x1 and y0<=cursor['y']<y1,'cursor-in-target-box',action)
  elif action!='key':raise RuntimeError('Unexpected physical input action')
  conservative=value['remainingNs']/1e9-value['hostProbeSeconds']-.1
  report['events'].append({'kind':'fresh-guard','action':action,'data':value,'targetBox':list(current_box),'validatedPayloadSha256':hashlib.sha256(encoded.encode()).hexdigest()})
  return {'remaining_s':conservative,'attempt_identity':attempt_identity(value),'validated_payload_sha256':hashlib.sha256(encoded.encode()).hexdigest()}
 def dispatch(action,events):
  nonlocal sequence,button_down
  sequence+=1
  payload=({'execute':'send-key','arguments':{'keys':[{'type':'qcode','data':current_key}],'hold-time':60}}
   if action=='key' else {'execute':'input-send-event','arguments':{'events':events}})
  adapter.dispatch_checked(helper_argv=['python3','-I',str(VM/'qmp.py'),'cmd'],payload=payload,evidence_dir=receipts,repository_root=REPOSITORY,
   attempt_id=expected['attempt'],expected_attempt_identity=hashlib.sha256(stable_json(expected).encode()).hexdigest(),sequence=sequence,action=action,fence=fence,timeout_s=1.0,reserve_s=8.0)
  if action=='press':button_down=True
  elif action=='release':button_down=False
 def screenshot(label):
  nonlocal screen_sequence
  screen_sequence+=1;path=out/(str(screen_sequence).zfill(3)+'-'+label+'.png');assert not path.exists()
  process=subprocess.run(['python3','-I',str(VM/'qmp.py'),'shot',str(path)],cwd=VM,capture_output=True,text=True,timeout=2)
  if process.returncode:raise RuntimeError('Screenshot helper failed')
  status=path.lstat();assert stat.S_ISREG(status.st_mode) and not path.is_symlink() and status.st_size>0
  report['screenshots'].append({'path':str(path),'sha256':sha(path),'label':label,'rootVisualReviewPending':True})
  return path
 def visible(template,rectangle,label,max_wait=2.0):
  end=time.monotonic()+max_wait;last_box=None;last_diff=None;last_path=None
  with Image.open(args.templates/template) as original:mask=original.convert('L').crop(rectangle).point(lambda value:255 if value>140 else 0)
  while time.monotonic()<end:
   value=probe();check_pred(value['identity']==expected,'visible-identity-match',label)
   check_pred(value['remainingNs']/1e9-value['hostProbeSeconds']>10,'visible-deadline-budget',label)
   path=screenshot(label);x,y=expected['at'];w,h=expected['size'];translated=(rectangle[0]-647+x,rectangle[1]-38+y,rectangle[2]-647+x,rectangle[3]-38+y)
   check_pred(0<=translated[0]<translated[2]<=1280 and 0<=translated[1]<translated[3]<=800 and x<=translated[0]<translated[2]<=x+w and y<=translated[1]<translated[3]<=y+h,'visible-client-bounds',label)
   with Image.open(path) as image:
    check_pred(image.size==(1280,800),'visible-screenshot-size',label)
    live=image.convert('L').crop(translated).point(lambda pixel:255 if pixel>140 else 0)
   diff=ImageChops.difference(mask,live).getbbox()
   if diff is None:
    report['events'].append({'kind':'exact-visible-mask','label':label,'template':str(args.templates/template),'templateSha256':sha(args.templates/template),'referenceBox':rectangle,'currentBox':translated,'comparison':'Exact binary luminance>140; translated current owned client origin','screenshot':str(path)})
    return
   last_box=translated;last_diff=diff;last_path=path
   time.sleep(.08)
  fail_receipt('visible-mask-match',label,{'referenceBox':list(rectangle),'currentBox':list(last_box) if last_box else None,'diffBbox':list(last_diff) if last_diff else None,'screenshotName':last_path.name if last_path else None})
  raise RuntimeError('Required visible control mask absent: '+label)
 def click(local,label):
  nonlocal current_box
  x,y=expected['at'];current_box=(x+local[0],y+local[1],x+local[2],y+local[3]);cx=(current_box[0]+current_box[2])//2;cy=(current_box[1]+current_box[3])//2
  dispatch('motion',[{'type':'abs','data':{'axis':'x','value':cx*32767//1280}},{'type':'abs','data':{'axis':'y','value':cy*32767//800}}]);time.sleep(.07)
  dispatch('motion',[{'type':'abs','data':{'axis':'x','value':(cx-3)*32767//1280}},{'type':'abs','data':{'axis':'y','value':cy*32767//800}}]);time.sleep(.07)
  dispatch('press',[{'type':'btn','data':{'down':True,'button':'left'}}]);time.sleep(.07)
  dispatch('release',[{'type':'btn','data':{'down':False,'button':'left'}}]);time.sleep(.1)
  report['events'].append({'kind':'checked-click-completed','label':label,'box':list(current_box)})
 def type_text(text):
  nonlocal current_key
  for letter in text:
   current_key=letter
   dispatch('key',None);time.sleep(.09)
 try:
  # The unchanged guest launcher owns DRM/device/scope guards. A refusal is
  # terminal, not a reason to bypass it or relaunch this attempt.
  check_pred(ssh('env OMARCHY_PATH=/usr/share/omarchy LANG=C.UTF-8 LC_ALL=C.UTF-8 omarchy-shell lock isLocked').strip()=='false','desktop-unlocked','startup')
  launch='nohup python3 -B '+shlex.quote(qa)+' -- python3 -B '+shlex.quote(controller)+' run '+shlex.quote(json.dumps(stage,separators=(',',':')))
  launch+=' > '+shlex.quote(root+'/controller-launch.stdout')+' 2> '+shlex.quote(root+'/controller-launch.stderr')+' < /dev/null & echo $!'
  launcher_pid=int(ssh(launch));report['guestQaLauncherPID']=launcher_pid
  readiness=time.monotonic()+8
  while True:
   try:value=probe();expected=value['identity'];break
   except (RuntimeError,subprocess.SubprocessError,ValueError,AssertionError):
    if time.monotonic()>=readiness:raise
    time.sleep(.12)
  write_new(out/'physical-expected.json',expected)
  report['pinnedAllThreeProcessIdentities']=expected
  # Prove actual Applications bar-button interior + glyph silhouette painted in bView
  # (strictly above horizontal scrollbar local y=41..53) before any QMP input.
  visible('run-03-before.png',(660,52,768,75),'applications-ready')
  click((13,28,121,37),'Applications')
  visible('run-03-apps-settled.png',(663,205,800,223),'search-label-ready')
  click((18,194,580,235),'Search')
  type_text('foot');time.sleep(.3)
  positive=screenshot('positive-foot')
  type_text('z');time.sleep(.35)
  negative=screenshot('negative-footz')
  with Image.open(positive) as a,Image.open(negative) as b:
   x,y=expected['at'];w,h=expected['size'];region=(x+18,y+240,min(x+580,x+w),min(y+600,y+h))
   changed=ImageChops.difference(a.convert('RGB').crop(region),b.convert('RGB').crop(region)).getbbox()
  report['lastKeyPixelObservation']={'resultsRegion':region,'changedPixelBounds':changed,'semanticLimit':'A pixel difference is not semantic proof of Foot/no-match or query/result synchronization; Root must inspect both complete screenshots.'}
  # A read-only catalog refresh attempt; all original per-input fences and D28 remain.
  check_pred(expected['size'][0]>=600,'refresh-viewport-width','refresh')
  refresh_x=3*expected['size'][0]//4
  click((refresh_x-40,250,refresh_x+40,282),'Refresh')
  time.sleep(.35)
  refreshed=screenshot('after-refresh-footz')
  report['physicalRefreshAttempt']={'image':str(refreshed),'scope':'Acknowledged guarded pointer input to the rendered Refresh button; inspect visible query/result afterward.','acceptanceLimit':'No correlated catalog-generation or backend receipt is inferred from a click or unchanged pixels.'}
  report['completedPhysicalSequence']=True
 except BaseException as error:
  report['failure']=type(error).__name__+': '+str(error)
 finally:
  report['inputCustody']={'lastAcknowledgedButtonDown':button_down,'keyboardMode':'One checked QMP send-key per printable qcode with hold-time60ms and QEMU timed release.','keyReleaseObserved':False,'atomicFocusProof':False,'releaseScope':'Keyboard transitions are not independently sampled; QMP timed release and acknowledgement do not prove guest delivery. Mouse motion/down/up each retain separate fresh fences. No blind release or input retry on refusal/unknown.'}
  report['qmpReceiptCount']=sequence
  report['guestRun']=root+'/run-01'
  # The guest controller alone terminates its unique owned unit at original D
  # and restores exact idle state. Observe its result; never kill global names.
  if launcher_pid is not None:
   end=time.monotonic()+35
   while time.monotonic()<end:
    try:
     text=ssh('cat '+shlex.quote(root+'/run-01/trial-result.json'),timeout=2)
     report['guestTrialResult']=json.loads(text);break
    except (RuntimeError,subprocess.SubprocessError,ValueError):time.sleep(.2)
   else:report['cleanupObservation']='Guest result unavailable; owned cleanup remains unconfirmed. Root must inspect this attempt, no automatic retry.'
  write_new(out/'host-journey-result.json',report)
 print(json.dumps({'report':str(out/'host-journey-result.json'),'completedPhysicalSequence':report['completedPhysicalSequence'],'nativeAccepted':False}))
 trial=report.get('guestTrialResult',{})
 cleanup=trial.get('cleanup',{})
 return 0 if report['completedPhysicalSequence'] is True and report.get('failure') is None and type(trial.get('exit')) is int and trial.get('exit')==0 and trial.get('failure') is None and trial.get('forcedAtOriginalDeadlineOrRefusal') is False and not cleanup.get('error') and cleanup.get('launcherReaped') is True and cleanup.get('scopeInventoryConfirmedEmpty') is True and cleanup.get('footPreserved') is True and cleanup.get('idleRestore',{}).get('exactEnabledRestored') is True and cleanup.get('originalOwnedBirthsRemain')==[] and cleanup.get('originalOwnedBirthsUnknown')==[] else 1

if __name__=='__main__':raise SystemExit(main())
