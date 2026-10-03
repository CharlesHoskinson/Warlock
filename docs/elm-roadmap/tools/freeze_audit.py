"""Freeze the planning draft supplied to independent auditors."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];DEST=ROOT/'audits/draft-packet'
files=[ROOT/name for name in ['ROADMAP.md','BASELINE.md','GPU.md','LAYERING.md','requirements.json','REQUIREMENTS.md','TRACEABILITY.md','generation.json','validation.json','gpu-inventory.json','heroic-layering-observation.json']]
files+=sorted((ROOT/'contributions').glob('*.md'))
files+=sorted((REPO/'openspec/changes/elm-desktop-pivot').rglob('*.md'))
manifest=[]
for path in files:
 rel=path.relative_to(REPO);dest=DEST/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
 manifest.append({'path':str(rel),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
(ROOT/'audits/draft-manifest.json').write_text(json.dumps({'scope':'First independent audit input; immutable after review begins','files':manifest},indent=2)+'\n')
# Avoid redundant copies of generated EARS/spec/tasks in embedded prompt; registry includes exact normative text and scenarios.
selected=[p for p in files if p.name in ['ROADMAP.md','BASELINE.md','GPU.md','LAYERING.md','requirements.json','validation.json','proposal.md','design.md'] or p.parent.name=='contributions']
packet=['# Frozen Elm desktop planning review packet','', 'The canonical requirement registry includes exact OpenSpec normative text/scenarios, implementation tasks, phase and evidence mapping. OpenSpec strict verification is included. All implementation/native/GPU acceptance is pending. Report defects with stable IDs, concrete counterexamples and precise corrections. Do not infer that source acquisition or model tests prove native behavior.','']
for path in selected:packet+=['\n---\nFILE: '+str(path.relative_to(REPO))+'\n',path.read_text()]
(ROOT/'audits/review-packet.md').write_text('\n'.join(packet))
print(json.dumps({'frozenFiles':len(files),'embeddedBytes':(ROOT/'audits/review-packet.md').stat().st_size,'sha256':hashlib.sha256((ROOT/'audits/review-packet.md').read_bytes()).hexdigest()}))
