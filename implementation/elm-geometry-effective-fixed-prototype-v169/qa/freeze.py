"""Hold experimental CPU proposal without changing upstream/source or models."""
import hashlib,json,resource,shutil,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selected=ROOT/'qa/experiment-1791125795904400760/report.json';report=json.loads(selected.read_text());assert report['passed']
assert report['runs']['original1710']['checks']==1710 and report['runs']['experimental1710']['checks']==1710
assert report['runs']['effective-cases']['checks']==34 and report['runs']['effective-cases']['exitCode']==0
controls=[row for name,row in report['runs'].items() if name.startswith('unsafe-')]
assert len(controls)==4 and all(row['exitCode']==1 and row['failedCases'] for row in controls)
for rel,w in report['artifacts'].items():assert sha(selected.parent/rel)==w,rel
for rel,w in report['inputs'].items():assert sha(ROOT/rel)==w,rel
origin=json.loads((ROOT/'origin.json').read_text());old=Path(origin['source'])
for rel,w in origin['files'].items():assert sha(old/rel)==w,rel
assert sha(ROOT/'qa/projection-test.cpp')==origin['files']['qa/projection-test.cpp']
review=REPO/'implementation/elm-geometry-authority-protocol-review-v168/reviewed-inputs.json'
upstream={str(review):{'sha256':sha(review),'size':review.stat().st_size}}
reviewed=json.loads(review.read_text())
compiled=next(Path(p) for p in reviewed['files'] if p.endswith('/candidate/ProspectiveGeometry.hpp'))
assert sha(compiled)==reviewed['files'][str(compiled)]['sha256']==origin['files']['candidate/ProspectiveGeometry.hpp']
upstream[str(compiled)]={'sha256':sha(compiled),'size':compiled.stat().st_size}
owner=Path(report['owningMath']['report']);assert sha(owner)==report['owningMath']['reportSHA256']
pair=json.loads(owner.read_text());upstream[str(owner)]={'sha256':sha(owner),'size':owner.stat().st_size}
external={}
for section in ['dependencies','linkedLibraries']:
 for path,w in report[section].items():
  p=Path(path);assert sha(p)==w,path
  external[path]={'sha256':w,'size':p.stat().st_size,'resolved':str(p.resolve())}
  if '/hyprutils/' in path:assert pair['dependencies'][path]==w,path
library=Path(report['owningMath']['library']);assert sha(library)==pair['linkedLibraries'][str(library)]
for name in ['c++','as','ld']:
 p=Path(shutil.which(name));external[str(p)]={'sha256':sha(p),'size':p.stat().st_size,'resolved':str(p.resolve())}
target=ROOT/'component-manifest.json';assert not target.exists()
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in ROOT.rglob('*') if p.is_file() and p!=target}
packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'experimental':True,'scope':'Proposed integer-profile effective fixed-axis guard; CPU compatibility/characterization only',
 'nativeAcceptance':False,'policyAcceptance':False,'modelAcceptance':False,'releaseAcceptance':False,
 'originalChecks':1710,'experimentalOriginalChecks':1710,'targetedChecks':34,'unsafeControlsRejected':4,
 'selectedReport':str(selected),'selectedReportSHA256':sha(selected),'files':files,'externalClosure':external,'upstream':upstream,'origin':origin}
target.write_text(json.dumps(packet,indent=2)+'\n')
for rel,row in files.items():assert sha(ROOT/rel)==row['sha256']
print(json.dumps({'passed':True,'files':len(files),'manifest':str(target),'manifestSHA256':sha(target)}))
