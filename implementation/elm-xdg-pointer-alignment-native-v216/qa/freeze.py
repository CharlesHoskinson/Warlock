from pathlib import Path
import hashlib,json,sys,resource,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=Path(__file__).resolve().parents[1];repo=root.parents[1]
paths=[
'implementation/elm-shared-keyboard-runtime-v435/candidate_host.py',
'implementation/elm-shared-keyboard-runtime-v435/aq-tuple.json',
'implementation/elm-shared-keyboard-runtime-v435/parent-probe-build.json',
'implementation/elm-seat-burst-fixture-fixed-v82/qa/interactive-client.py',
'implementation/elm-seat-burst-fixture-fixed-v82/native/parent-input-module.c',
'implementation/elm-seat-burst-fixture-fixed-v82/native/parent-input-client.c',
'implementation/elm-seat-burst-fixture-fixed-v82/build-1791106310522558513/report.json',
'implementation/elm-shared-keyboard-menu-native-v436/qa/native.py',
'implementation/elm-geometry-staged-menu-native-v77/qa/native.py',
'implementation/elm-keyboard-focus-cancellation-v155/candidate/src/backend/Wayland.cpp',
'implementation/elm-keyboard-focus-cancellation-v155/candidate/src/backend/NestedPresentation.hpp',
'implementation/elm-geometry-xdg-hint-choice-fixture-v197/component-manifest.json',
'implementation/elm-xdg-presented-landmark-oracle-v210/component-manifest.json',
'implementation/elm-xdg-pointer-journal-oracle-v213/component-manifest.json',
'implementation/elm-xdg-pointer-journal-independent-review-v215/component-manifest.json',
'implementation/elm-xdg-presented-landmark-native-v212/qa/native-1791133183538677576/report.json',
]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
missing=[p for p in paths if not (repo/p).is_file()]
if missing:raise RuntimeError('Missing source pins: '+repr(missing))
external={p:{'sha256':digest(repo/p),'size':(repo/p).stat().st_size} for p in paths}
local={str(p.relative_to(root)):{'sha256':digest(p),'size':p.stat().st_size} for p in sorted(root.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
packet={'sourceHeld':True,'passed':True,'scope':'source-only pointer-alignment requirements; no executable native runner or native acceptance','files':local,'externalFiles':external,'nativeAccepted':False,'physicalHardwareAccepted':False,'nonzeroCapabilityAccepted':False,'mutableScreenshotSourceCaptured':False}
out=root/'component-manifest.json';out.write_text(json.dumps(packet,indent=2)+'\n')
for name,row in local.items():assert digest(root/name)==row['sha256']
for name,row in external.items():assert digest(repo/name)==row['sha256']
print(json.dumps({'passed':True,'localFiles':len(local),'externalPins':len(external),'manifestSHA256':digest(out),'nativeAccepted':False}))
