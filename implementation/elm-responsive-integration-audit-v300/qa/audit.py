import hashlib,json,resource,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=REPO/'implementation/elm-reconciliation-frontend-v611';files=['src/SurfaceRenderer.elm','src/Surface.elm','assets/shell.css'];captured={};(ROOT/'qa/inputs').mkdir()
for name in files:
 p=source/name;data=p.read_bytes();target=ROOT/'qa/inputs'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);captured[name]=hashlib.sha256(data).hexdigest()
assert all(sha(source/name)==digest for name,digest in captured.items()),'Observed source changed during read; not a frozen integration parent'
renderer=(ROOT/'qa/inputs/src/SurfaceRenderer.elm').read_text();presentation=(ROOT/'qa/inputs/src/Surface.elm').read_text();css=(ROOT/'qa/inputs/assets/shell.css').read_text()
assert 'class "surface-bar"' in renderer and 'class "surface-popup"' in renderer
assert '.bar #app>div' in css and '.popup #app>div' in css
assert 'span [class "control-detail"] [text item.detail]' in renderer and 'Awaiting native confirmation' in presentation
current=REPO/'implementation/elm-responsive-surfaces-gui-v278/assets/shell.css';accepted=current.read_text();assert '.bar .surface-bar' in accepted and '.popup .surface-popup' in accepted
r={'passed':True,'scope':'Protected read-only observation of unaccepted live611 integration source; no implementation/native/Quint/release claim','unacceptedSourceObservation':True,'frozenIntegrationParent':False,'source':str(source.relative_to(REPO)),'sourceReadStable':True,'inputs':captured,'acceptedCssSHA256':sha(current),'findings':['611 renders same surface-bar/surface-popup roots and still contains stale #app layout selectors; actual278 root corrections are applicable only after frozen source integration','611 adds per-target Awaiting native confirmation details plus read-only Refresh controls; current278 wholebutton ellipsis may hide detail after long labels, an inference requiring actual DOM/pixel/keyboard proof','New pending/recovery popup may contain extra Refresh row; retain viewport scrolling and test actual focused/control visibility on400logical outputs rather than inheriting only three-action compact-menu result'],'next':'Integrate responsive root styles into a fresh derivative of the primary reviewed coherent frontend; preserve readable uncertainty detail separately from truncated title and actual keyboard/pointer reachability. Compile and run current models/replays plus original135/473 and narrow-output native cases on owning205/594/AQ155.'}
with (ROOT/'qa/report.json').open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':True,'scope':'Unaccepted source observation only','inputs':len(captured),'reportSHA256':sha(ROOT/'qa/report.json')}))
