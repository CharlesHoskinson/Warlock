import hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path(__file__).resolve().parents[3];ROOTS=[REPO/'implementation'/n for n in ['elm-surface-recovery-v79','elm-surface-recovery-v80','elm-surface-recovery-qa-v81','elm-surface-recovery-checks-v82']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
root=ROOTS[1];build=root/'qa/build-1791082616931167658/report.json';check=ROOTS[3]/'qa/checks-1791082713184937329/report.json';native=ROOTS[2]/'qa/native-1791082675352643893/report.json'
b=json.loads(build.read_text());assert b['passed'];assert sha(build.parent/'elm-host')==b['binarySHA256']
for rel,h in b['inputs'].items():assert sha(root/rel)==h,rel
c=json.loads(check.read_text());assert c['passed'] and c['typedChecks']==41 and c['presentationChecks']==12
for rel,h in c['inputs'].items():assert sha(ROOTS[3]/rel)==h,rel
for p in (root/'src').glob('*.elm'):assert sha(p)==sha(ROOTS[3]/'src'/p.name),p.name
assert sha(root/'elm.json')==sha(ROOTS[3]/'elm.json')
n=json.loads(native.read_text());assert n['passed'] and n['cleanupPassed'] and len(n['checks'])==42 and all(r['passed'] for r in n['checks']) and n['buildReportSHA256']==sha(build)
for p,h in n['inputs'].items():assert sha(Path(p))==h,p
log=(native.parent/'native-evidence/elm-webview.log').read_text();assert 'backend-exit: waited=1 normal=0 code=-1' in log and 'backend-exit: waited=1 normal=1 code=0' in log and 'host-exit: failure=0 rendered=1' in log
for p in [ROOTS[0]/'qa/checks-1791082528523831075/report.json',ROOTS[1]/'qa/checks-1791082643215950921/report.json']:assert not json.loads(p.read_text())['passed']
assert sha(root/'spec/surfaces.qnt')==sha(REPO/'implementation/elm-surface-ack-v77/spec/surfaces.qnt')
for r in ROOTS:
 files={str(p.relative_to(r)):sha(p) for p in sorted(r.rglob('*')) if p.is_file() and 'elm-stuff' not in p.parts and p.name!='slice-manifest.json'}
 (r/'qa/slice-manifest.json').write_text(json.dumps({'sourceClosurePassed':True,'nativeCandidateAccepted':r in ROOTS[1:3],'acceptedSource':'implementation/elm-surface-recovery-v80','acceptedCompiledProof':'implementation/elm-surface-recovery-checks-v82','compiledControllerChecks':41,'compiledPresentationChecks':12,'nativeChecks':42,'surfaceProtocol':2,'wholeFeatureAccepted':False,'completedRequirementIds':[],'scope':'Accessible DOM names and explicit idle-backend recovery only; pending Unknown and full91 native regression not accepted','newQuintRun':False,'files':files},indent=2)+'\n');print(r/'qa/slice-manifest.json')
