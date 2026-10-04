#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT.parents[1]/'implementation/elm-pending-observation-join-v567'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REPLAY=ROOT/'qa/replay-1791145651865921603/report.json';BUILD=ROOT/'qa/build-1791145677156791200/report.json'
replay=json.loads(REPLAY.read_text());build=json.loads(BUILD.read_text());assert replay['passed'] and len(replay['checks'])==21 and build['passed']
for path,digest in replay['artifacts'].items():assert sha(REPLAY.parent/path)==digest,path
for path,digest in replay['sourceFiles'].items():assert sha(ROOT/path)==digest,path
for path,digest in build['inputs'].items():
 if path.startswith(('src/','native/','adapter/','assets/')):assert sha(ROOT/path)==digest,path
for name in ['elm.js','bar.js','popup.js']:assert sha(ROOT/'assets'/name)==sha(BUILD.parent/'inputs/assets'/name),name
unchanged=['Effects.elm','Shell.elm','Desktop.elm','TaskbarShell.elm','Taskbar.elm','OutputController.elm','SurfaceController.elm']
for name in unchanged:assert sha(ROOT/'src'/name)==sha(BASE/'src'/name),name
changes=[]
for base in ['src','native','adapter','assets']:
 for p in (BASE/base).glob('*'):
  if p.is_file() and (ROOT/base/p.name).exists() and sha(p)!=sha(ROOT/base/p.name):changes.append({'path':base+'/'+p.name,'baselineSHA256':sha(p),'currentSHA256':sha(ROOT/base/p.name)})
(ROOT/'presentation-amendment.json').write_text(json.dumps({'schema':1,'version':'UI589','status':'compiled component only; native original bounds requalification pending','surfaceProtocol':2,'barControlBound':{'original':257,'current':259,'reason':'256 groups + Applications + timeout refresh + observation-only recovery refresh'},'popupControlBoundUnchanged':2051,'changes':changes,'unchangedAuthorityModules':unchanged,'nativeKeyboardATIMEAccepted':False},indent=2)+'\n')
files={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name!='component-manifest.json'}
(ROOT/'component-manifest.json').write_text(json.dumps({'schema':1,'passed':True,'sourceHeld':True,'nativeAcceptance':False,'scope':'Pure UI recovery presentation and compiled/native-helper component evidence; no native GUI or authoritative release claim','checks':21,'replayReport':str(REPLAY),'replayReportSHA256':sha(REPLAY),'buildReport':str(BUILD),'buildReportSHA256':sha(BUILD),'optimizedAssetsMatch':True,'files':files,'limitations':replay['limitations']},indent=2)+'\n')
print(json.dumps({'passed':True,'checks':21,'heldFiles':len(files),'buildReport':str(BUILD)}))
