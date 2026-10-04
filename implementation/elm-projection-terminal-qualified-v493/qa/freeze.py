import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-xdg-origin-combined-qualification-v484/qa/slice-manifest.json';assert sha(parent)=='1860680083a19d1db101ed30f066a2b25b8442e63071663953124f368a5fbbc4';held=json.loads(parent.read_text())
for e in held['files']:assert sha(REPO/e['path'])==e['sha256']
files=[];links=[];reports=[];native=[]
for number in range(485,493):
 source=next((REPO/'implementation').glob('*v'+str(number)))
 for p in sorted(source.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json' or any(x in p.relative_to(source).parts for x in ['inputs','native-evidence']):continue
  j=json.loads(p.read_text());reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':j['passed']})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  for rel,digest in j.get('inputs',{}).items():assert sha(Path(rel) if Path(rel).is_absolute() else source/rel)==digest
  if number in [487,488]:assert not j['passed'] and 'parsing failed' in j['error']
  else:assert j['passed']
  if number==486:assert j['compiledShellWitness']['commands']==0 and j['compiledShellWitness']['expected']=='58' and j['actualBackendFrames']==[{'protocolVersion':3,'kind':'host-refresh'}]
  if number==489:assert len(j['namedScenarios'])==8 and j['invariantSamples']==1000 and j['maxSteps']==40 and j['mutantsRejected']==5
  if number==491:assert len(j['checks'])==9 and all(c['passed'] for c in j['checks'])
  if p.parent.name.startswith('native-'):
   assert len(j['checks'])==89 and all(c['passed'] for c in j['checks']) and j['cleanupPassed'] and j['pair']==held['nativePair'] and not j['mainDesktopActions'];native.append((p,j))
assert len(native)==1
p,j=native[0];log=p.parent/'native-evidence/elm-webview.log';lines=log.read_text().splitlines();terminals=[(i,json.loads(l.split(': ',1)[1])) for i,l in enumerate(lines) if l.startswith('backend-frame: ') and json.loads(l.split(': ',1)[1]).get('kind')=='projection-unavailable'];assert len(terminals)>=1
observed=[]
for index,t in terminals:
 assert t['reason']=='scene-changed'
 later=[json.loads(l.split(': ',1)[1]) for l in lines[index+1:] if l.startswith('frontend-request: ')];fresh=next(q for q in later if q['kind']=='projection-request');assert fresh['binding']==t['binding'] and int(fresh['requestId'])>int(t['requestId'])
 frames=[json.loads(l.split(': ',1)[1]) for l in lines[index+1:] if l.startswith('backend-frame: ')];assert any(f.get('kind')=='action-projection' and f['binding']==fresh['binding'] and f['requestId']==fresh['requestId'] for f in frames)
 observed.append({'terminal':t,'freshProjectionRequest':fresh})
assert j['retirementExtension']['remainingSeconds']>0
for rel in ['native/host.c','native/shared-host.c','adapter/taskbar_projection.py']:assert sha(REPO/'implementation/elm-projection-correlated-terminal-v490'/rel)==sha(REPO/'implementation/elm-shared-geometry-carrier-v422'/rel)
audit=REPO/'implementation/elm-xdg-pointer-alignment-review-v222/REVIEW.md';auditsha=sha(audit)
for p in [ROOT/'HANDOFF.md',Path(__file__).resolve()]:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
output=ROOT/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Actual backend/typedElm correlated read terminal repair with original89 native menu/keyboard/same-title retirement checks','parentManifest':str(parent),'parentManifestSHA256':sha(parent),'files':files,'symlinks':links,'reports':reports,'nativePair':held['nativePair'],'source':'implementation/elm-projection-correlated-terminal-v490','nativeAcceptance':True,'nativeCheckCount':89,'nativeTerminalRecovery':observed,'quintNamedScenarios':8,'quintSamples':1000,'quintMutantsRejected':5,'typedCompiledCases':9,'pointerHelperAudit':str(audit),'pointerHelperAuditSHA256':auditsha,'fullPointerContractAccepted':False,'fullReleaseAccepted':False,'completedRequirementIds':[]},indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'nativeChecks':89,'actualTerminalRecoveries':len(observed),'manifestSHA256':sha(output)}))
