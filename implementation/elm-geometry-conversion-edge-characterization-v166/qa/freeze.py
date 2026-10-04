"""Hold actual conversion slices, failure history and paired math closure."""
import hashlib,json,resource,shutil,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selected=ROOT/'qa/characterize-1791124674571594068/report.json';r=json.loads(selected.read_text())
assert r['passed'] and r['runs']['actual']['exitCode']==0 and r['runs']['actual']['checks']==23
assert r['runs']['unsafe-bare-workarea']['exitCode']==1 and r['runs']['unsafe-client-times-scale']['exitCode']==1
for rel,w in r['artifacts'].items():assert sha(selected.parent/rel)==w,rel
review=Path(r['reviewedInputs']);assert sha(review)==r['reviewedInputsSHA256']
for path,row in json.loads(review.read_text())['files'].items():assert sha(Path(path))==row['sha256'],path
pair=Path(r['pairReport']);assert sha(pair)==r['pairReportSHA256'];pdata=json.loads(pair.read_text())
external={}
for section in ['dependencies','linkedLibraries']:
 for path,w in r[section].items():
  p=Path(path);assert sha(p)==w,path
  external[path]={'sha256':w,'size':p.stat().st_size,'resolved':str(p.resolve())}
  if '/hyprutils/' in path:assert pdata['dependencies'][path]==w,path
library=Path(r['pairedHyprutils']['library']);assert sha(library)==pdata['linkedLibraries'][str(library)]
for name in ['c++','as','ld','pkg-config']:
 p=Path(shutil.which(name));external[str(p)]={'sha256':sha(p),'size':p.stat().st_size,'resolved':str(p.resolve())}
cc1=Path(subprocess.check_output(['c++','-print-prog-name=cc1plus'],text=True).strip())
external[str(cc1)]={'sha256':sha(cc1),'size':cc1.stat().st_size,'resolved':str(cc1.resolve())}
old=REPO/'implementation/elm-geometry-conversion-characterization-v162'
failure=old/'qa/characterize-1791124499432621357/report.json';bad=json.loads(failure.read_text());assert not bad['passed'] and len(bad['runs']['actual']['failedNames'])==2
for rel,w in bad['artifacts'].items():assert sha(failure.parent/rel)==w,rel
ancestor={str(p.relative_to(old)):{'sha256':sha(p),'size':p.stat().st_size} for p in old.rglob('*') if p.is_file()}
diagnostic=ROOT/'qa/characterize-1791124627337410027/report.json';bad=json.loads(diagnostic.read_text());assert not bad['passed']
assert 'OBSERVED real-box -9 22 96 75' in (diagnostic.parent/'actual.stdout').read_text()
target=ROOT/'component-manifest.json';assert not target.exists()
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in ROOT.rglob('*') if p.is_file() and p!=target}
packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Actual owning conversion method slices and paired real Hyprutils CPU characterization; no eligibility/native/model acceptance',
 'nativeAcceptance':False,'policyAcceptance':False,'modelAcceptance':False,'selectedReport':str(selected),'selectedReportSHA256':sha(selected),
 'checks':23,'unsafeControlsRejected':2,'files':files,'externalClosure':external,
 'ancestorRoot':str(old),'ancestorInventory':ancestor,'observedDiagnostic':str(diagnostic),'observedDiagnosticSHA256':sha(diagnostic),
 'reviewedInputs':str(review),'reviewedInputsSHA256':sha(review),'pairReport':str(pair),'pairReportSHA256':sha(pair)}
target.write_text(json.dumps(packet,indent=2)+'\n')
for rel,row in files.items():assert sha(ROOT/rel)==row['sha256']
print(json.dumps({'passed':True,'files':len(files),'external':len(external),'ancestorFiles':len(ancestor),'manifest':str(target),'manifestSHA256':sha(target)}))
