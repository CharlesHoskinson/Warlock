import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-pending-observation-reviewed-v572/qa/slice-manifest.json';assert sha(parent)=='bba863a897917bd70fadf9c3ef3d1411d3af9c5e7dd73e7e811febf771b705bc'
held=json.loads(parent.read_text());files=[];links=[];reports=[]
for number in range(573,582):
 directory=next((REPO/'implementation').glob('*v'+str(number)))
 for p in sorted(directory.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json':continue
  j=json.loads(p.read_text());assert j['passed']==(number not in [573,576,577,578]),(number,p)
  reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':j['passed']})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest,(number,rel)
  if number==573:assert len(j['checks'])==75 and all(c['passed'] for c in j['checks']) and j['cleanupPassed'] and not j['mainDesktopActions'] and j['pair']==held['nativePair']
  if number==581:assert len(j['namedScenarios'])==11 and j['invariantSamples']==1000 and j['maxSteps']==40 and j['mutantsRejected']==7
  if number==579:assert len(j['owningHeaders'])==694 and not j['missingSymbols'] and j['core']['sha256']=='bda6ce0094961c285673589afa2b61fe2b97321a1d86b248823b482122fec0f5' and not j['nativeAcceptance'] and not j['installed']
  if number==580:
   assert len(j['checks'])==10 and j['mutantsRejected']==3 and j['headerSHA256']==sha(REPO/'implementation/elm-binding-registration-query-v579/native/binding-registration.hpp') and j['authoritySHA256']==sha(REPO/'implementation/elm-binding-registration-query-v579/native/authority.cpp')
assert len(reports)==9,len(reports)
base=REPO/'implementation/elm-keyboardless-focus-owning-pair-v206';candidate=REPO/'implementation/elm-binding-registration-query-v579'
changed=[]
for section in ['native','candidate']:
 for p in (candidate/section).rglob('*'):
  if p.is_file():
   old=base/p.relative_to(candidate)
   if not old.exists() or sha(old)!=sha(p):changed.append(str(p.relative_to(candidate)))
assert set(changed)=={'native/authority.cpp','native/binding-registration.hpp'}
for p in [Path(__file__).resolve(),ROOT/'HANDOFF.md']:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
r={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'source':'implementation/elm-binding-registration-query-v579','baselineSource':held['baselineSource'],'reviewedNativeChecks':473,'nativePair':held['nativePair'],'parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),'nativeAcceptance':False,'nativeDiagnosticChecksReached':75,'nativeDiagnosticCleanupPassed':True,'rootCause':'Unknown target reservation survives new binding and fresh snapshots; actual native action admitted but public Effects reducer refuses new intent','quintNamedScenarios':11,'quintSamples':1000,'quintMutantsRejected':7,'compiledRegistrationChecks':10,'compiledRegistrationMutantsRejected':3,'registrationQueryCompilePassed':True,'registrationQueryNativeAccepted':False,'durableReconciliationImplemented':False,'candidateQualificationComplete':False,'fullReleaseAccepted':False,'completedRequirementIds':[],'files':files,'symlinks':links,'reports':reports}
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifestSHA256':sha(p)}))
