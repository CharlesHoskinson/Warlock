"""Verify scoped native receipts and preserve source/artifact closure."""
import hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1), 'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
native=ROOT/'qa/native-1791066870280313454/report.json'
policy=ROOT/'qa/policy-1791066977725523380/report.json'
n=json.loads(native.read_text());p=json.loads(policy.read_text())
assert n['passed'] and n['cleanupPassed'] and not n['mainDesktopActions']
assert len(n['checks'])==97 and all(c['passed'] for c in n['checks'])
assert p['passed'] and p['namedScenarios']==11 and p['invariantSamples']==1000
for manifest in ('qa/build-pair-manifest.json','qa/source-manifest.json'):
 for relative,digest in json.loads((ROOT/manifest).read_text())['files'].items():
  assert sha(ROOT/relative)==digest,relative
for artifact in n['pair']['core'], n['pair']['authority']:
 assert sha(Path(artifact['path']))==artifact['sha256']
report={'passed':True,'scope':'Main-content pinned input-hole native regression at fixed unit scale only; broad scene/release gates remain open',
        'wholeFeatureAccepted':False,'canonicalSceneCapability':False,'mainDesktopActions':False,'completedRequirementIds':[],
        'nativeChecks':97,'nativeCleanupPassed':True,'abstractNamedScenarios':11,'abstractInvariantSamples':1000,
        'reports':{str(path.relative_to(ROOT)):sha(path) for path in (native,policy)},
        'failedBaseline':'../elm-input-region-v22/qa/native-1791066600635179376/report.json'}
destination=ROOT/'qa/slice-manifest.json'
assert not destination.exists(),'Preserve original closure'
report['files']={str(path.relative_to(ROOT)):sha(path) for path in sorted(ROOT.rglob('*')) if path.is_file() and not path.is_symlink()}
destination.write_text(json.dumps(report,indent=2)+'\n')
print(destination)
