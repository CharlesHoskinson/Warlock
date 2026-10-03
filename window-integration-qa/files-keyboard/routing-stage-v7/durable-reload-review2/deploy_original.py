#!/usr/bin/env python3
"""Root-agent reviewed, same-PID atomic reload. No automatic retries or post-reload rollback."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,signal,time
import observations as obs
from atomic_reload import replace_while_stopped,WriteFailure
B=Path(__file__).resolve().parent;LIVE=Path.home()/'.local/share/omarchy-files'
parser=argparse.ArgumentParser();parser.add_argument('--attempt',type=Path,required=True);parser.add_argument('--accepted-reload-report',type=Path,required=True);parser.add_argument('--execute',action='store_true',required=True);args=parser.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
manifest_path=B/'frozen-inputs.json';frozen=manifest_path.read_bytes();manifest=json.loads(frozen)
def verify():
 for item in manifest['files']:assert sha(Path(item['path']))==item['sha256'],item['path']
verify();plan=json.loads((B/'source-plan.json').read_text());O=args.attempt.resolve();assert O.parent==B and O.name.startswith('deployment-attempt-');os.umask(0o077);O.mkdir(mode=0o700)
proof=json.loads(args.accepted_reload_report.read_text());assert proof['result']=='pass' and proof['platform']=='main Wayland' and proof['durableUrl']==plan['nativeDestination'] and proof['sourceManifestSHA256']==sha(manifest_path) and all(proof['preservation'].values()) and all(c['passed'] for c in proof['checks']),'Require accepted exact native durable-reload packet'
for i in plan['nativeFiles']:assert sha(Path(plan['nativeDestination'])/i['path'])==i['sha256']
for i in plan['changedQml']:assert sha(LIVE/i['path'])==i['baselineSha256'] and sha(B/'candidate-app'/i['path'])==i['deploymentSha256']
for i in plan['unchangedOperationsAndSpec']:assert sha(LIVE/i['path'])==i['sha256']
assert not (LIVE/'ui-migration.json').exists(),'Existing responsive host needs no legacy migration file'
report={'result':'pending','checks':{},'preservation':{},'sourceManifestSHA256':sha(manifest_path),'acceptedReloadReportSHA256':sha(args.accepted_reload_report),'rollbackPackageRetained':True,'sourcePlanSHA256':sha(B/'source-plan.json')}
before=obs.capture(O/'before-main');identity=before['files'];expected=plan['original'];assert identity['pid']==expected['pid'] and identity['instance']==expected['instance'] and identity['start']==expected['processStart']
ui=identity['ui'];public=identity['public'];assert not ui['visible'] and ui['view']=='home' and not ui['sel'] and not ui['clip']['paths'] and not ui['prompt']['visible'] and not ui['menu']['visible'] and not ui['lbOpen'] and not ui.get('focusIdentity')
assert not any(r['pid']==identity['pid'] for r in obs.data('clients'))
for name,source in [('backup',LIVE),('staged',B/'candidate-app'),('rollback',LIVE)]:
 folder=O/name;folder.mkdir(mode=0o700)
 for item in plan['changedQml']:
  p=folder/item['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((source/item['path']).read_bytes());p.chmod((source/item['path']).stat().st_mode&0o777)
handle=os.pidfd_open(identity['pid']);replaced=[];resumed=False
try:
 # Exact source and process guards repeated immediately before the one mutation.
 verify();assert obs.start(identity['pid'])==identity['start'];assert obs.files()==identity
 for i in plan['changedQml']:assert sha(LIVE/i['path'])==i['baselineSha256']
 changes=[{'path':i['path'],'staged':O/'staged'/i['path'],'live':LIVE/i['path'],'rollback':O/'rollback'/i['path']} for i in plan['changedQml']]
 try:replaced=replace_while_stopped(handle,changes);resumed=True
 except WriteFailure as error:
  replaced=error.replaced;report['preResumeRollbackApplied']=not error.rollback_errors;report['preResumeRollbackErrors']=error.rollback_errors;resumed=True
  raise
 end=time.monotonic()+12
 while True:
  try:
   loaded=json.loads(obs.run('qs','ipc','--pid',identity['pid'],'call','files','migrationStatus'));current=json.loads(obs.run('qs','ipc','--pid',identity['pid'],'call','files','uiState'))
   if loaded.get('error'):raise AssertionError(loaded['error'])
   if loaded.get('ready') and loaded['initialization']['resumed'] and 'focusIdentity' in current and str(Path(plan['nativeDestination'])/'libwindowaccessibility.so') in Path(f'/proc/{identity["pid"]}/maps').read_text():
    copy=dict(current);assert copy.pop('focusIdentity')==''
    if copy==ui:break
  except (ValueError, __import__('subprocess').CalledProcessError):pass
  if time.monotonic()>end:raise AssertionError('Same-PID durable reload did not settle exact complete UI state')
  time.sleep(.08)
 time.sleep(.3)
 report['loadedInitialization']=loaded['initialization'];report['checks']['samePidInstanceStart']=loaded['pid']==identity['pid'] and loaded['instance']==identity['instance'] and obs.start(identity['pid'])==identity['start']
 report['checks']['hiddenBeforeBackingMap']=loaded['initialization']['resumed'] and not loaded['initialization']['visible'] and not loaded['initialization']['backingVisible'] and not current['visible']
 report['checks']['exact15InstalledQml']=all(sha(LIVE/i['path'])==i['deploymentSha256'] for i in plan['changedQml'])
 report['checks']['operationsAndSpecExact']=all(sha(LIVE/i['path'])==i['sha256'] for i in plan['unchangedOperationsAndSpec'])
 report['checks']['durableNativeAssetsExact']=all(sha(Path(plan['nativeDestination'])/i['path'])==i['sha256'] for i in plan['nativeFiles'])
except Exception as error:report['error']=repr(error)
finally:
 os.close(handle);report['resumedOnce']=resumed;report['replacedPaths']=replaced
 try:
  checks,details=obs.compare(before,O/'after-main',allow_empty_focus_addition=True);report['preservation']=checks;report['preservationDetails']=details
 except Exception as error:report['preservationError']=repr(error)
 report['checks']['unchangedFrozenManifestBytes']=manifest_path.read_bytes()==frozen
 try:verify();report['checks']['allFrozenInputsExact']=True
 except Exception as error:report['checks']['allFrozenInputsExact']=False;report['hashError']=repr(error)
 report['result']='pass' if not report.get('error') and not report.get('preservationError') and all(report['checks'].values()) and all(report['preservation'].values()) else 'fail'
 report['recovery']='Retain this private backup and raw before/after evidence. After a post-resume failure, root reviews exact current state before any source rollback; no implicit source rollback/retry.'
 obs.private_json(O/'report.json',report);print(json.dumps({'result':report['result'],'checks':report['checks'],'preservation':report['preservation'],'reportSHA256':sha(O/'report.json'),'error':report.get('error')}))
raise SystemExit(report['result']!='pass')
