import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-native-owner-counterfactual-reviewed-v561/qa/slice-manifest.json';assert sha(parent)=='69ce75e7b31ca7b537ae49dbaf93ceb5fc005d3ffa07a2618c7cfdbe4b572219'
accepted=REPO/'implementation/elm-keyboardless-current-acceptance-v222/acceptance-manifest.json';assert sha(accepted)=='bbb42789486071600535cf66d4ba869722530c6fe590cc7f1af72a203fc80fe4';held=json.loads(accepted.read_text())
base=REPO/'implementation/elm-stable-surface-publication-v521';candidate=REPO/'implementation/elm-pending-observation-join-v567';changes=[]
for section in ['src','native','adapter','assets']:
 for p in (candidate/section).glob('*'):
  if p.is_file() and sha(p)!=sha(base/p.relative_to(candidate)):changes.append(str(p.relative_to(candidate)))
assert changes==['src/Desktop.elm']
files=[];links=[];reports=[];native=[]
for number in range(562,572):
 directory=next((REPO/'implementation').glob('*v'+str(number)))
 for p in sorted(directory.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json':continue
  j=json.loads(p.read_text());assert j['passed']==(number not in [563,569]);reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':j['passed']})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  if p.parent.name.startswith('native-'):
   expected={563:16,569:75}[number];assert len(j['checks'])==expected and all(c['passed'] for c in j['checks']) and j['cleanupPassed'] and not j['mainDesktopActions'];assert j['pair']==held['nativePair'];native.append({'path':str(p.relative_to(REPO)),'passed':False,'checksReached':expected,'cleanupPassed':True})
   if number==569:assert any(c['name']=='tabEnterPickerSelectionActivatesActualKeyboardRecipient' and c['passed'] for c in j['checks'])
  if number==566:assert len(j['namedScenarios'])==10 and j['invariantSamples']==1000 and j['mutantsRejected']==6
  if number==568:assert len(j['checks'])==8
  if number==570:assert j['reviewedNativeChecks']==473 and j['adoptedBoundedNativeEvidence'] and j['nativePair']==held['nativePair']
assert len(native)==2 and len(reports)==8
for p in [Path(__file__).resolve(),ROOT/'HANDOFF.md']:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'source':'implementation/elm-pending-observation-join-v567','diagnosticSource':'implementation/elm-pending-observation-action-trace-v571','baselineSource':'implementation/elm-stable-surface-publication-v521','reviewedNativeBaseline':str(accepted.relative_to(REPO)),'reviewedNativeBaselineSHA256':sha(accepted),'reviewedNativeChecks':473,'nativePair':held['nativePair'],'parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),'nativeAcceptance':False,'joinRepairActualNativeBehaviorObserved':True,'nativeCampaigns':native,'candidateQualificationComplete':False,'pointerRaceCausallyResolved':False,'fullReleaseAccepted':False,'completedRequirementIds':[],'quintNamedScenarios':10,'quintSamples':1000,'quintMutantsRejected':6,'typedCompiledCases':8,'files':files,'symlinks':links,'reports':reports}
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifestSHA256':sha(p)}))
