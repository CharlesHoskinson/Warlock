"""Freeze shared Elm boundary evidence without asserting native host acceptance."""
import hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reports={'compiled':sorted((ROOT/'qa').glob('outputs-*/report.json'))[-1],'inherited':sorted((ROOT/'qa').glob('checks-*/report.json'))[-1],'model':REPO/'implementation/elm-output-controller-model-v143/qa/model-1791089304148738374/report.json'}
for name,p in reports.items():
 r=json.loads(p.read_text());assert r['passed'],name
 if name!='model':
  for relative,digest in r['inputs'].items():assert sha(ROOT/relative)==digest,relative
  for relative,digest in r['artifacts'].items():assert sha(p.parent/relative)==digest,relative
 else:
  assert sha(REPO/'implementation/elm-output-controller-model-v143/spec/views.qnt')==r['sourceSHA256']
  assert r['namedScenarios']==10 and len(list(p.parent.glob('named-*.itf.json')))==10
assert json.loads(reports['compiled'].read_text())['typedChecks']==37
assert json.loads(reports['inherited'].read_text())['typedChecks']==58
roots=['elm-output-controller-v141','elm-output-controller-v142','elm-output-controller-model-v143','elm-output-controller-v144','elm-output-controller-v145']
files={str(p.relative_to(REPO)):sha(p) for name in roots for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and p!=ROOT/'qa/component-manifest.json'}
manifest={'passed':True,'scope':'Compiled single Elm controller and read-only Bar boundary with capability-scoped callbacks; native shared host remains pending','nativeAcceptance':False,'launchableSharedHost':False,'sharedControllerChecks':37,'inheritedControllerChecks':58,'inheritedPresenterChecks':12,'quintNamedScenarios':10,'quintInvariantSamples':1000,'completedRequirementIds':[],'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for k,p in reports.items()},'retainedProductionNativeEvidence':'implementation/elm-output-production-qa-v140/qa/slice-manifest.json','files':files}
(ROOT/'qa/component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items() if k!='files'}))
