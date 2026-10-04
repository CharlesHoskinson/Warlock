import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
parent=REPO/'implementation/elm-picker-ready-acceptance-v261/acceptance-manifest.json';assert sha(parent)=='686b1a2e231e8110de1703a004d49209cf7c900128c1c81671feab4d75e698ad';pair=json.loads(parent.read_text())['nativePair']
reports=[]
for name,passed in [('elm-picker-ready-cohort-native-v263',False),('elm-picker-ready-cohort-native-v265',True)]:
 p=next((REPO/'implementation'/name/'qa').glob('native-*/report.json'));m=json.loads(p.read_text());assert m['passed']==passed and m['cleanupPassed'] and not m['inputChanges'] and m['pair']==pair
 for path,digest in m['inputs'].items():assert sha(path)==digest
 for rel,digest in m['artifacts'].items():assert sha(p.parent/rel)==digest
 reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':passed,'checks':len(m['checks']),'cleanupPassed':True})
 if passed:
  assert all(c['passed'] for c in m['checks']) and m['cohortCleanup'][-1]['remaining']==[] and len(m['supervisorEvents']['starts'])==2 and len(m['supervisorEvents']['exits'])==2
  accepted=len(m['checks'])
files=[]
for name in ['elm-current-recovery-contract-v262','elm-picker-ready-cohort-native-v263','elm-picker-ready-cohort-v264','elm-picker-ready-cohort-native-v265','elm-picker-ready-cohort-v266',ROOT.name]:
 for path in sorted((REPO/'implementation'/name).rglob('*')):
  if path==ROOT/'acceptance-manifest.json':continue
  st=path.lstat();row={'path':str(path.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if path.is_symlink():row['symlink']=os.readlink(path)
  elif path.is_file():row.update(sha256=sha(path),size=st.st_size)
  elif path.is_dir():continue
  else:raise RuntimeError('Unexpected special file '+str(path))
  files.append(row)
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':True,'acceptedGuiNativeCheckCount':473,'acceptedCurrentRecoveryNativeCheckCount':accepted,'currentNativeRecoveryUIAccepted':True,'historical168ExitCampaignAccepted':False,'pendingUnknownReconciliationAccepted':False,'serverOldGrantRetirementAccepted':False,'fullRoadmapAccepted':False,'fullReleaseAccepted':False,'parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),'nativePair':pair,'reports':reports,'files':files,'scope':'Bounded original183 native recovery UI/cohort/replacement/cancellation acceptance on actual231 current205 tuple; old-packet refusal proves local endpoint binding only, broader recovery/roadmap/release separate'}
with (ROOT/'acceptance-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'acceptedCurrentRecoveryNativeCheckCount':accepted,'manifestSHA256':sha(ROOT/'acceptance-manifest.json')}))
