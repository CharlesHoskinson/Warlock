"""Protected QA: verify current code/proofs and retain private fixture evidence."""
import datetime,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((ROOT/'build/build-report.json').read_text());assert build['passed']
for f,sha in build['files'].items():assert digest(ROOT/f)==sha,f
elm=json.loads((ROOT/'qa/elm-test-results.json').read_text());assert elm['passed'] and len(elm['results'])==14
final=sorted((ROOT/'qa').glob('final-pass-*/report.json'))[-1];assert json.loads(final.read_text())['passed']
reports=[(p,json.loads(p.read_text())) for p in sorted((ROOT/'qa').glob('native-smoke-*.json'))]
accepted={}
for p,d in reports:
 if d['passed']:accepted[d['surfaceRole']]=(p,d)
assert set(accepted)=={'xdg','layer'}
# The latest layer acceptance must bind the current native binary/assets/build.
_,layer=accepted['layer'];assert layer['filesSHA256'][str(ROOT/'build/elm-host')]==digest(ROOT/'build/elm-host')
for role,(p,d) in accepted.items():
 assert d['hostExitCode']==0 and d['cleanupPassed'] and d['renderReport']['body']['actionsDisabled']
for p,d in reports:
 source=Path(d['output']);assert source.parent==Path('/home/hoskinson/window-integration-qa') and source.name.startswith('elm-fixture-host-')
 target=ROOT/'qa/native-evidence'/source.name
 if not target.exists():shutil.copytree(source,target)
 # Original archived source paths are kept; portable paths supplement them.
 image=d.get('image',{}).get('path')
 if image:assert digest(target/Path(image).name)==d['image']['sha256']
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='slice-manifest.json')
result=dict(observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='First fixture-only Elm/native host slice; no production host selection or window-effects/GPU/AT acceptance',passed=True,elmChecks=14,nativeHostTestGroups=2,acceptedSurfaces=list(accepted),currentLayerReport=str(accepted['layer'][0].relative_to(ROOT)),finalPass=str(final.relative_to(ROOT)),requirementsSHA256=digest(REPO/'docs/elm-roadmap/requirements.json'),files=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p),bytes=p.stat().st_size) for p in files])
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
