"""Close actual native27 behavior plus failed activation accounting evidence."""
import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
BASE=REPO/'implementation/elm-gtk-native-acquisition-fix-v268';RUN=BASE/'qa/native-1791146650894471270'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=ROOT/'qa'/('verify-'+str(time.time_ns()));out.mkdir()
report={'passed':False,'nativeAcceptance':False,'fullGTKAccepted':False,'qualifiedCleanupPassed':False,'checks':[]};external={}
def check(name,ok):
 report['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
try:
 manifest=BASE/'component-manifest.json';check('held268',sha(manifest)=='8bfcda5de4bd6e0123a56d3a7b571d8d0ec9016a37aeedf467a23c3238bb9a17');external[str(manifest)]=sha(manifest)
 for filename,row in json.loads(manifest.read_text())['files'].items():check('held:'+filename,sha(BASE/filename)==row['sha256'])
 data=json.loads((RUN/'report.json').read_text());external[str(RUN/'report.json')]=sha(RUN/'report.json')
 check('fullNativeStillFailed',not data['passed'] and not data['nativeAcceptance'] and not data['fullCampaignPassed'] and data['cleanupPassed'] is False)
 check('all27RecordedChecksPass',len(data['checks'])==27 and all(row['passed'] for row in data['checks']))
 names={row['name'] for row in data['checks']}
 for name in ['A:actualGtkMarkerRGB','C:actualGtkMarkerRGB','A:unchangedNativeAndProtocolAcrossCapture','C:unchangedNativeAndProtocolAcrossCapture','normalGtkExitAndActualEmptyNativeCensus','ownedToolkitObserverUnload','authorityPluginUnload']:check('actual:'+name,name in names)
 for filename,digest in data['artifacts'].items():check('artifact:'+filename,sha(RUN/filename)==digest);external[str(RUN/filename)]=digest
 evidence=RUN/'native-evidence';host=json.loads((evidence/'host-evidence.json').read_text());post=json.loads((evidence/'activation-post-retirement.json').read_text());actor=json.loads((evidence/'gtk-role-client/actor.json').read_text())
 check('nativeCleanupTruthfullyFalse',host['privateActivationCleanupPassed'] is False and post['passed'] is False and data['cleanupPassed'] is False)
 check('resourceRetirementSeparate',host['runtimeGone'] and host['remainingDescendants']==[] and host['unexpectedInnerDescendants']==[])
 check('actualGTKNormalExit',actor['exitCode']==0)
 journals=[]
 for path in sorted((evidence/'activation-journals').glob('*/*.jsonl')):
  rows=[json.loads(line) for line in path.read_text().splitlines()];terminal=rows[-1];check('completeJournal:'+path.parent.name,terminal['kind']=='terminal')
  journals.append({'service':path.parent.name,'journal':str(path),'sha256':sha(path),'terminal':terminal,'signals':[r for r in rows if r['kind']=='signal']})
 check('actualDocumentsForeignUIDRefusal',any(row['service']=='org.freedesktop.portal.Documents' and 'foreign UID' in str(row['terminal']['error']) for row in journals))
 check('actualSystemdUnavailableExitOne',any(row['service']=='org.freedesktop.systemd1' and row['terminal']['childExitCode']==1 for row in journals))
 check('normalExit15SeparateFromSignal15',any(item['exitCode']==15 for row in journals for item in row['terminal']['allWaitStatuses']))
 report.update(passed=True,sourceNativeReport=str(RUN/'report.json'),recordedNativeChecks=27,actualGTKExitCode=actor['exitCode'],journals=journals,artifactCount=len(data['artifacts']))
finally:
 (out/'verify.py').write_bytes(Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
if report['passed']:
 manifest=ROOT/'component-manifest.json';assert not manifest.exists()
 files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file()}
 manifest.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'qualifiedCleanupPassed':False,'files':files,'externalFiles':external,'report':str(out/'report.json')},indent=2)+'\n')
