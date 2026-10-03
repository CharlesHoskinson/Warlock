#!/usr/bin/env python3
"""Exclusive copied app proof. Native mode requires root's GUI grant. Never mutate original Files."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,signal,subprocess,time
import observations as obs
B=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--attempt',type=Path,required=True);parser.add_argument('--native',action='store_true');args=parser.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify():
 manifest=json.loads((B/'frozen-inputs.json').read_text())
 for item in manifest['files']:assert Path(item['path']).is_file() and sha(Path(item['path']))==item['sha256'],item['path']
 return manifest
frozen=(B/'frozen-inputs.json').read_bytes();verify();O=args.attempt.resolve();assert O.parent==B and O.name.startswith('attempt-');os.umask(0o077);O.mkdir(mode=0o700)
plan=json.loads((B/'source-plan.json').read_text());destination=Path(plan['nativeDestination'])
for item in plan['nativeFiles']:assert sha(destination/item['path'])==item['sha256'],'Root must install fresh reviewed durable native assets first'
app=O/'app';shutil.copytree(B/'baseline-app',app)
witness=app/'ReloadWitness.qml';assert not witness.exists();shutil.copyfile(B/'witness-initial.qml',witness)
# Bootstrap the copied responsive host hidden, with the production process's
# FILES_OPEN=home still present. Candidate host is deployed byte-for-byte;
# PersistentProperties must suppress its genuine FILES_OPEN initialization.
host=app/'shell.qml';text=host.read_text();needle='var o = Quickshell.env("FILES_OPEN")';assert text.count(needle)==1;host.write_text(text.replace(needle,'var o = "" // QA baseline bootstrap only; candidate remains exact'))
home=O/'home';home.mkdir();fixture=home/'fixture';fixture.mkdir();(fixture/'alpha.txt').write_text('private fixture bytes\n');(fixture/'image.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>');(fixture/'subfolder').mkdir()
report={'scope':'Exact durable native URL, copied same-PID responsive-to-keyboard reload; no main input or operations','platform':'main Wayland' if args.native else 'private offscreen','checks':[],'preservation':{},'result':'pending','bootstrapOnlyChange':needle+' -> empty in copied baseline only','sourceManifestSHA256':sha(B/'frozen-inputs.json'),'sourcePlanSHA256':sha(B/'source-plan.json'),'durableUrl':str(destination),'copiedOnlyReloadWitness':{'path':str(witness),'initialSHA256':sha(B/'witness-initial.qml'),'finalSHA256':sha(B/'witness-final.qml'),'uninstantiated':True,'productSourceMutation':False}}
process=None;before=None;executed=None;log=(O/'copied.log').open('w');attempt_start=time.monotonic()
def check(name,value,**detail):
 report['checks'].append({'name':name,'passed':bool(value),**detail});assert value,name

def wait(fn,label,seconds=10):
 until=time.monotonic()+seconds
 while time.monotonic()<until:
  try:
   value=fn()
   if value:return value
  except (subprocess.CalledProcessError,ValueError):pass
  time.sleep(.08)
 raise AssertionError(label)
def ipc(method,*a):return obs.run('qs','ipc','--pid',process.pid,'call','files',method,*a)
def state(method):return json.loads(ipc(method))
def hidden_client_check():return not any(r['pid']==process.pid for r in obs.data('clients'))
def canonical_ui(value,allow_empty=False):
 value=dict(value)
 if allow_empty:assert value.pop('focusIdentity','')=='','Hidden reload must not restore a focus target'
 return value

def reload_sources():
 previous=(O/'copied.log').read_text().count('Configuration Loaded')
 handle=os.pidfd_open(process.pid);stopped=False
 try:
  signal.pidfd_send_signal(handle,signal.SIGSTOP);stopped=True
  for item in plan['changedQml']:
   p=app/item['path'];new=p.with_name(p.name+'.qa-new');new.write_bytes((B/'candidate-app'/item['path']).read_bytes());os.replace(new,p)
 finally:
  if stopped:signal.pidfd_send_signal(handle,signal.SIGCONT)
  os.close(handle)
 wait(lambda:(O/'copied.log').read_text().count('Configuration Loaded')>previous,'actual completed source-watcher reload')
try:
 if args.native:before=obs.capture(O/'before-main')
 env=dict(os.environ,HOME=str(home),FILES_STATE=str(O/'state'),FILES_DRYRUN='1',FILES_WIDGET='0',FILES_OPEN='home',XDG_CACHE_HOME=str(O/'cache'))
 if not args.native:env.update(QT_QPA_PLATFORM='offscreen',QT_QPA_PLATFORMTHEME='basic',QT_STYLE_OVERRIDE='Fusion',QT_QUICK_BACKEND='software',DISPLAY='',WAYLAND_DISPLAY='')
 process=subprocess.Popen(['qs','-p',str(app)],env=env,stdout=log,stderr=log,start_new_session=True)
 loaded=wait(lambda: state('migrationStatus') if state('migrationStatus').get('ready') else None,'baseline ready');identity={'pid':process.pid,'start':obs.start(process.pid),'instance':loaded['instance']};report['fixtureIdentity']=identity
 check('baseline initialized hidden before map',not state('uiState')['visible'] and not loaded['initialization']['visible'] and not loaded['initialization']['backingVisible'])
 ipc('act','go','home');ipc('act','go',str(fixture));wait(lambda:state('state')['entries']==3,'fixture loaded');ipc('act','go','home');time.sleep(.3)
 public=state('state');ui=state('uiState');obs.private_json(O/'copied-home-before.json',{'public':public,'ui':ui})
 check('hidden Home has actual three-entry history',not ui['visible'] and len(public['hist'])==3 and public['hIdx']==2 and public['view']=='home')
 if args.native:check('copied baseline has never mapped',hidden_client_check())
 reload_sources()
 loaded=wait(lambda:state('migrationStatus') if state('migrationStatus').get('ready') and state('migrationStatus')['initialization']['resumed'] else None,'candidate resumed PersistentProperties');wait(lambda:canonical_ui(state('uiState'),True)==ui,'full Home state restored');after=state('uiState');obs.private_json(O/'copied-home-after.json',{'public':state('state'),'ui':after,'loaded':loaded})
 check('same copied PID/start/instance after exact durable reload',process.poll() is None and obs.start(process.pid)==identity['start'] and loaded['pid']==identity['pid'] and loaded['instance']==identity['instance'])
 check('candidate imports snapshot before backing map',loaded['initialization']['resumed'] and not loaded['initialization']['visible'] and not loaded['initialization']['backingVisible'])
 check('full Home state exact with empty optional focus identity',canonical_ui(after,True)==ui)
 check('public Home state exact',state('state')==public)
 check('FILES_OPEN home did not reopen copied explorer',not after['visible'])
 maps=Path(f'/proc/{process.pid}/maps').read_text();check('actual process loaded exact durable native SO',str(destination/'libwindowaccessibility.so') in maps)
 check('all 15 executed candidate QML files exact production bytes',all(sha(app/i['path'])==i['deploymentSha256'] for i in plan['changedQml']))
 executed=[{'path':str(p),'sha256':sha(p)} for p in sorted(app.rglob('*')) if p.is_file() and p!=witness]
 obs.private_json(O/'executed-inputs.json',{'files':executed,'nativeFiles':plan['nativeFiles'],'nativeDestination':str(destination)})
 if args.native:check('candidate reload never maps a copied client',hidden_client_check())
 # A second same-PID reload exercises generic persistence with actual paths,
 # selection, clipboard, preferences and a pending prompt while still hidden.
 ipc('act','go',str(fixture));wait(lambda:state('state')['entries']==3,'folder state');ipc('act','select','alpha.txt');ipc('act','copy','');ipc('act','hidden','');ipc('act','sort','size');ipc('act','view','list');ipc('act','zoom','280');ipc('act','detail','on');ipc('act','prompt','');time.sleep(.3)
 full=state('uiState');public2=state('state');obs.private_json(O/'copied-rich-before.json',{'ui':full,'public':public2});check('real hidden snapshot carries prompt/absolute selection/clipboard',not full['visible'] and full['prompt']['visible'] and full['prompt']['mode']=='mkdir' and full['clip']['paths']==[str(fixture/'alpha.txt')] and list(full['sel'])==[str(fixture/'alpha.txt')])
 # Quickshell ignores identical-content writes. Only this copied uninstantiated
 # sentinel changes; every actual executed product QML byte remains exact.
 previous=(O/'copied.log').read_text().count('Configuration Loaded')
 check('copied uninstantiated witness has frozen initial bytes',sha(witness)==sha(B/'witness-initial.qml'))
 temporary=witness.with_name(witness.name+'.qa-new');temporary.write_bytes((B/'witness-final.qml').read_bytes());os.replace(temporary,witness)
 wait(lambda:(O/'copied.log').read_text().count('Configuration Loaded')>previous,'actual completed rich-state source-watcher reload')
 wait(lambda:state('migrationStatus')['initialization']['resumed'],'second resumed');time.sleep(.6);wait(lambda:state('uiState')==full,'rich state post-model restoration')
 check('only copied witness changed to frozen final bytes',sha(witness)==sha(B/'witness-final.qml') and all(sha(app/i['path'])==i['deploymentSha256'] for i in plan['changedQml']))
 rich_after=state('uiState');obs.private_json(O/'copied-rich-after.json',{'ui':rich_after,'public':state('state')})
 check('generic persistent reload exact full state',rich_after==full)
 check('generic persistent reload exact public state',state('state')==public2)
 check('generic persistent reload same PID/start/instance',process.poll() is None and obs.start(process.pid)==identity['start'] and state('migrationStatus')['instance']==identity['instance'])
 check('hidden reload has no focus target to steal',not rich_after['visible'] and not rich_after.get('focusIdentity'))
 if args.native:check('rich hidden reload has no mapped copied client',hidden_client_check())
 check('no migration snapshot file required',not (app/'ui-migration.json').exists())
except Exception as error:report['error']=repr(error)
finally:
 if process:
  try:obs.private_json(O/'copied-final.json',{'ui':state('uiState'),'public':state('state'),'loaded':state('migrationStatus')})
  except Exception as error:report['finalObservationError']=repr(error)
  forced=False
  members=[]
  for proc in Path('/proc').iterdir():
   if not proc.name.isdigit():continue
   try:
    if os.getpgid(int(proc.name))==process.pid:members.append({'pid':int(proc.name),'start':obs.start(int(proc.name))})
   except (FileNotFoundError,ProcessLookupError,PermissionError):pass
  if process.poll() is None:
   os.killpg(process.pid,signal.SIGTERM)
   try:process.wait(timeout=8)
   except subprocess.TimeoutExpired:
    forced=True;os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=4)
  until=time.monotonic()+2
  while any(Path(f'/proc/{p["pid"]}').exists() for p in members) and time.monotonic()<until:time.sleep(.08)
  remaining=[p for p in members if Path(f'/proc/{p["pid"]}').exists() and obs.start(p['pid'])==p['start']]
  report['cleanup']={'pid':process.pid,'exitCode':process.poll(),'forcedKill':forced,'gone':not Path(f'/proc/{process.pid}').exists(),'exactOwnedMembers':members,'remainingOwnedMembers':remaining}
  report['preservation']['ownedFixtureNormalExit']=not forced and process.poll() in (0,-signal.SIGTERM)
  report['preservation']['ownedFixtureGone']=report['cleanup']['gone'] and not remaining
 log.close()
 if before:
  try:
   checks,detail=obs.compare(before,O/'after-main');report['preservation'].update(checks);report['preservationDetails']=detail
  except Exception as error:report['preservationError']=repr(error)
 report['copiedOnlyReloadWitness']['actualFinalSHA256']=sha(witness)
 if executed is not None:report['preservation']['actualExecutedAppInputsExact']=all(Path(i['path']).is_file() and sha(Path(i['path']))==i['sha256'] for i in executed)
 report['preservation']['durableNativeAssetsExact']=all(sha(destination/i['path'])==i['sha256'] for i in plan['nativeFiles'])
 report['preservation']['frozenManifestBytes']=(B/'frozen-inputs.json').read_bytes()==frozen
 try:verify();report['preservation']['allFrozenInputsExact']=True
 except Exception as error:report['preservation']['allFrozenInputsExact']=False;report['hashError']=repr(error)
 report['elapsedSeconds']=time.monotonic()-attempt_start
 report['result']='pass' if not report.get('error') and not report.get('preservationError') and all(c['passed'] for c in report['checks']) and all(report['preservation'].values()) else 'fail'
 obs.private_json(O/'report.json',report)
 print(json.dumps({'result':report['result'],'featureGates':len(report['checks']),'preservation':report['preservation'],'error':report.get('error'),'reportSHA256':sha(O/'report.json'),'cleanup':report.get('cleanup')}))
raise SystemExit(report['result']!='pass')
