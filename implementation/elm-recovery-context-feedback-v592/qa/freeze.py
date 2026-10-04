#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parents[1]/'implementation/elm-unknown-recovery-ui-v589'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REPLAY=ROOT/'qa/replay-1791146043447506188/report.json';BUILD=ROOT/'qa/build-1791146069348127960/report.json'
r=json.loads(REPLAY.read_text());b=json.loads(BUILD.read_text());assert r['passed'] and len(r['checks'])==35 and all(x['passed'] for x in r['checks']) and b['passed']
for path,digest in r['artifacts'].items():assert sha(REPLAY.parent/path)==digest,path
for path,digest in r['sourceFiles'].items():assert sha(ROOT/path)==digest,path
for path,digest in b['inputs'].items():
 if path.startswith(('src/','native/','adapter/','assets/')):assert sha(ROOT/path)==digest,path
for name in ['elm.js','bar.js','popup.js']:assert sha(ROOT/'assets'/name)==sha(BUILD.parent/'inputs/assets'/name),name
changes=[]
for folder in ['src','native','adapter','assets']:
 for p in (BASE/folder).glob('*'):
  if p.is_file():
   current=ROOT/folder/p.name;assert current.exists()
   if sha(p)!=sha(current):changes.append({'path':folder+'/'+p.name,'parentSHA256':sha(p),'currentSHA256':sha(current)})
assert {x['path'] for x in changes} <= {'src/Surface.elm','assets/elm.js','assets/bar.js','assets/popup.js'}
assert sha(ROOT/'native/surface.h')==sha(BASE/'native/surface.h') and sha(ROOT/'src/SurfaceRenderer.elm')==sha(BASE/'src/SurfaceRenderer.elm')
files={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name!='component-manifest.json'}
(ROOT/'component-manifest.json').write_text(json.dumps({'schema':1,'passed':True,'sourceHeld':True,'nativeAcceptance':False,'scope':'Compiled contextual feedback repair preserving58921+14 additional assertions; no native/AT/IME/settlement/release claim','parentManifest':str(BASE/'component-manifest.json'),'parentManifestSHA256':sha(BASE/'component-manifest.json'),'inheritedPresentationAmendment':str(BASE/'presentation-amendment.json'),'inheritedPresentationAmendmentSHA256':sha(BASE/'presentation-amendment.json'),'productionChanges':changes,'replayReport':str(REPLAY),'replayReportSHA256':sha(REPLAY),'buildReport':str(BUILD),'buildReportSHA256':sha(BUILD),'checks':35,'optimizedAssetsMatch':True,'files':files},indent=2)+'\n')
print(json.dumps({'passed':True,'checks':35,'heldFiles':len(files),'productionChanges':[x['path'] for x in changes]}))
