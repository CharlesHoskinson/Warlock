import hashlib,json,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
assert not (ROOT/'component-manifest.json').exists()
external={}
for name in ['Binding.elm','UInt64.elm']:
 p=REPO/'implementation/elm-recovery-context-feedback-v592/src'/name;assert sha(p)==sha(ROOT/'src'/name);external[str(p)]=sha(p)
for relative in ['src/MenuBridge.elm','src/NativeProvider.elm','native/host.c','native/shared-host.c']:
 p=REPO/'implementation/elm-recovery-context-feedback-v592'/relative;external[str(p)]=sha(p)
p=REPO/'implementation/elm-geometry-coordinate-authority-v409/native/geometry.inc';external[str(p)]=sha(p)
parent=REPO/'implementation/elm-gtk-popup-eligibility-failure-review-v302';manifest=parent/'component-manifest.json';r=json.loads(manifest.read_text());assert r['sourceHeld'] is True;assert sha(manifest)=='5f295e5895cef9d3069997ab325c58cd507d981f062000945d5adcec0b31d7dd';external[str(manifest)]=sha(manifest)
for relative,row in r['files'].items():
 p=parent/relative;expected=row['sha256'];assert sha(p)==expected;external[str(p)]=expected
selected=['test-1791152555101891795','mutations-1791152661218174336']
for name in selected:
 r=json.loads((ROOT/'qa'/name/'report.json').read_text());assert r['passed'] is True and r['nativeAcceptance'] is False
 for p,h in r['sourceInputs'].items():assert sha(p)==h,p
 for p,h in r.get('capturedSources',{}).items():assert sha(p)==h,p
 for p,h in r.get('tools',{}).items():assert sha(p)==h;external[p]=h
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in sorted(ROOT.rglob('*')) if p.is_file()}
(ROOT/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'integratedAcceptance':False,'authenticatedTransportImplemented':False,'newQuintLogic':False,'files':files,'externalFiles':external,'selectedReports':selected,'fullOriginalGtk02StillOpen':True},indent=2)+'\n');print(json.dumps({'passed':True,'manifestSHA256':sha(ROOT/'component-manifest.json'),'ownFiles':len(files),'externalFiles':len(external)}))
