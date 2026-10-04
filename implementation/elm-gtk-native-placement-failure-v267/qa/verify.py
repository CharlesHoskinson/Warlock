"""Close actual native failure evidence without treating empty census as normal exit."""
import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
BASE=REPO/'implementation/elm-gtk-post-bus-retirement-v263'
NATIVE=BASE/'qa/native-1791145436509122699'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def live(row):
 try:return Path('/proc',str(row['pid']),'stat').read_text().rsplit(')',1)[1].split()[19]==str(row['start'])
 except FileNotFoundError:return False
out=ROOT/'qa'/('verify-'+str(time.time_ns()));out.mkdir()
report={'passed':False,'nativeAcceptance':False,'fullCampaignPassed':False,'qualifiedCleanupPassed':False,'checks':[]}
external={}
def check(name,ok):
 report['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
try:
 manifest=BASE/'component-manifest.json';check('owningHeld263',sha(manifest)=='35b2f1d4c3080475dc2a2abe876433002e5d806cabe2a119f04f4b1fcd27f27a')
 packet=json.loads(manifest.read_text())
 for filename,row in packet['files'].items():check('held:'+filename,sha(BASE/filename)==row['sha256'])
 external[str(manifest)]=sha(manifest)
 data=json.loads((NATIVE/'report.json').read_text());check('actualNativeFailure',data['passed'] is False and data['nativeAcceptance'] is False and data['fullCampaignPassed'] is False)
 check('nineMappedChecks',len(data['checks'])==9 and all(row['passed'] for row in data['checks']))
 joined=data['checks'][-1];check('actualTwoGTKSurfaceJoins',joined['name']=='actualIndependentGtkRootsMapped' and joined['A']['identity']['surfaceId']==42 and joined['C']['identity']['surfaceId']==71)
 for filename,digest in data['artifacts'].items():check('actualArtifact:'+filename,sha(NATIVE/filename)==digest);external[str(NATIVE/filename)]=digest
 external[str(NATIVE/'report.json')]=sha(NATIVE/'report.json')
 ipc=NATIVE/'native-evidence/bounded-ipc/1791145441942266662'
 command=json.loads((ipc/'record.json').read_text());check('placementIPCFailureExact',command['exitCode']==7 and command['argv'][-3:-1]==['dispatch','setfloating'] and command['argv'][-1].startswith('address:'))
 check('actualLuaParserRefusal',"')' expected near 'address'" in (ipc/'stdout').read_text())
 evidence=NATIVE/'native-evidence';host=json.loads((evidence/'host-evidence.json').read_text());post=json.loads((evidence/'activation-post-retirement.json').read_text());actor=json.loads((evidence/'gtk-role-client/actor.json').read_text())
 check('activationFinalGateRefused',host['privateActivationCleanupPassed'] is False and post['passed'] is False and 'privateActivationPostRetirementError' in host)
 documents=next(row for row in post['records'] if Path(row['journal']).parent.name=='org.freedesktop.portal.Documents')
 check('actualDocumentsIdentityAccountingFailure','missing unique PID/start before reap' in documents['terminal']['error'])
 check('topCleanupClaimContradicted',data['cleanupPassed'] is True and host['privateActivationCleanupPassed'] is False)
 check('inheritedEmptyButNotNormalProof',host['runtimeGone'] is True and host['remainingDescendants']==[] and host['cleanupErrors']==[])
 check('GTKActorCancelledNotNormal',actor['exitCode']==-15 and actor['failureCleanupTerminate'] is True)
 check('actualOwningProcessesRetired',not live(actor['process']) and not live(data['nativeProcess']) and not live(post['busIdentity']))
 report.update(passed=True,nativeReport=str(NATIVE/'report.json'),nativeReportSHA256=sha(NATIVE/'report.json'),artifactCount=len(data['artifacts']),originalCleanupPassed=data['cleanupPassed'],privateActivationCleanupPassed=host['privateActivationCleanupPassed'],actorExitCode=actor['exitCode'],documentsTerminal=documents['terminal'],firstIPC=command)
finally:
 (out/'verify.py').write_bytes(Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
if report['passed']:
 path=ROOT/'component-manifest.json';assert not path.exists()
 files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file()}
 path.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'qualifiedCleanupPassed':False,'files':files,'externalFiles':external,'report':str(out/'report.json')},indent=2)+'\n')
