import hashlib,json,os,resource,stat
from pathlib import Path
REPO=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
names=['elm-host-admission-handoff-v293','elm-shared-recovery-ui-v294','elm-admission-handoff-model-v295','elm-admission-handoff-model-fixed-v296','elm-admission-pipeline-v297','elm-admission-pipeline-fixed-v298','elm-admission-handoff-acceptance-v299']
reports=[];files=[];special=[]
for name in names:
 root=REPO/'implementation'/name
 for p in sorted(root.glob('qa/*/report.json')):
  d=json.loads(p.read_text());reports.append({'path':str(p.relative_to(REPO)),'passed':d['passed'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checks':len(d['checks']) if isinstance(d.get('checks'),list) else d.get('checks'),'scope':d.get('scope')})
 for p in sorted(root.glob('qa/preflight-failure.json')):
  reports.append({'path':str(p.relative_to(REPO)),'passed':False,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checks':0,'scope':'Preflight failure before behavioral execution'})
 for p in sorted(root.rglob('*')):
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode),'uid':st.st_uid,'gid':st.st_gid}
  if stat.S_ISLNK(st.st_mode):row.update(type='symlink',target=os.readlink(p));files.append(row)
  elif stat.S_ISREG(st.st_mode):row.update(size=st.st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());files.append(row)
  elif not stat.S_ISDIR(st.st_mode):special.append(row)
assert len(reports)==8 and sum(x['passed'] for x in reports)==6
p=OUT/'slice-manifest.json';assert not p.exists()
d={'schema':1,'passed':True,'scope':'Compiled shared Elm/C host and live admission/production handler CPU handoff; native GUI and full release remain open','files':files,'specialFiles':special,'reports':reports,'liveCAndPythonChecks':110,'productionHandlerChecks':21,'compiledSharedOutputChecks':37,'compiledSharedRecoveryChecks':49,'quintNamedScenarios':12,'quintInvariantSamples':1000,'quintMaxSteps':40,'sourceHost':'implementation/elm-shared-recovery-ui-v294','sourceBroker':'implementation/elm-host-admission-handoff-v293/adapter','nativeHostAdmissionSourceIntegrated':True,'nativeGUIHandoffQualified':False,'nativeRun':False,'fullReleaseAccepted':False,'completedRequirementIds':[]}
p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'manifest':str(p),'files':len(files),'reports':len(reports)}))
