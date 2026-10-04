import hashlib,json,os,resource,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
policy=REPO/'implementation/elm-geometry-size-policy-v395/qa/policy-1791123338491586381/report.json';p=json.loads(policy.read_text());assert p['passed'] and p['checks']==796
for rel,digest in p['inputs'].items():assert sha(policy.parents[2]/rel)==digest,rel
model=REPO/'implementation/elm-geometry-size-model-v396/qa/model-1791123407592233107/report.json';m=json.loads(model.read_text());assert m['passed'] and m['namedScenarios']==11 and m['unsafeLowerBound']['detected']
assert 'QNT508' in (model.parent/'unsafe.stdout').read_text() and 'minimumAboveWorkareaTest failed' in (model.parent/'unsafe.stdout').read_text()
native=REPO/'implementation/elm-shared-floating-constraints-native-v397/qa/native-1791123525249978187/report.json';n=json.loads(native.read_text());assert not n['passed'] and n['cleanupPassed'] and len(n['checks'])==45
assert n['error']=="AssertionError('floatingMenuHasMultipleActualEnabledActions')"
bounds=n['constraintDiagnostic'];assert len(bounds['targetProtocolObjects'])==1 and {'kind':'min','width':108,'height':42} in bounds['actualClientSizeRequests'] and {'kind':'max','width':0,'height':0} in bounds['actualClientSizeRequests']
files=[];special=[]
for name in ['elm-geometry-size-policy-v395','elm-geometry-size-model-v396','elm-shared-floating-constraints-native-v397',ROOT.name]:
 for path in sorted((REPO/'implementation'/name).rglob('*')):
  st=path.lstat();row={'path':str(path.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if stat.S_ISLNK(st.st_mode):row.update(type='symlink',target=os.readlink(path));files.append(row)
  elif stat.S_ISREG(st.st_mode):row.update(size=st.st_size,sha256=sha(path));files.append(row)
  elif not stat.S_ISDIR(st.st_mode):special.append(row)
prior=REPO/'implementation/elm-shared-receipt-eof-accepted-v394/qa/slice-manifest.json'
path=ROOT/'qa/slice-manifest.json';assert not path.exists();path.write_text(json.dumps({'schema':1,'passed':True,'scope':'Pure size policy/model and truthful retained native representative GTK capability failure; no integration or native maximize acceptance','files':files,'specialFiles':special,'finalPurePolicy':'implementation/elm-geometry-size-policy-v395','productionSourceUnchanged':'implementation/elm-shared-registration-shutdown-merge-v380','priorPacket':str(prior.relative_to(REPO)),'priorPacketSHA256':sha(prior),'policyChecks':796,'quintNamed':11,'traceSamples':1000,'maxSteps':40,'unsafeLowerBoundDetected':True,'nativeReport':str(native.relative_to(REPO)),'nativeReportSHA256':sha(native),'nativePassed':False,'cleanupPassed':True,'observedRawMinimum':[108,42],'observedRawMaximum':[0,0],'wireIntegrated':False,'completedRequirementIds':[],'fullReleaseAccepted':False},indent=2)+'\n');print(json.dumps({'manifest':str(path),'files':len(files)}))
