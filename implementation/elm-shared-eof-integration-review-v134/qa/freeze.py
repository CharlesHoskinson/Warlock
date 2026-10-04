"""Append-only review inventory; no upstream writes and no native acceptance."""
import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
REPO=next(p for p in ROOT.parents if (p/'AGENTS.md').is_file())
SOURCE=REPO/'implementation/elm-shared-context-disposition-wire-v132'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selected=ROOT/'qa/review-1791119522381354281/report.json'
report=json.loads(selected.read_text());assert report['passed'] and len(report['checks'])==26
for rel,want in report['artifacts'].items():assert sha(selected.parent/rel)==want,rel
assert sha(SOURCE/'component-manifest.json')==report['sourceManifestSHA256']
for row in json.loads((SOURCE/'component-manifest.json').read_text())['ownProduction']:
 assert sha(SOURCE/row['path'])==row['sha256'],row['path']
upstream={}
paths=[SOURCE/'component-manifest.json',SOURCE/'HANDOFF.md',
 REPO/'implementation/elm-geometry-broker-eof-deadline-v92/qa/relay.py',
 REPO/'implementation/elm-geometry-receipt-eof-relay-v90/qa/relay.py',
 REPO/'implementation/elm-geometry-receipt-selector-v82/qa/wrapper.py',
 REPO/'implementation/elm-geometry-family-menu-receipt-cleanup-native-v100/qa/native.py',
 REPO/'implementation/elm-geometry-family-menu-receipt-cleanup-native-v100/qa/native-1791110259133139744/report.json',
 REPO/'implementation/elm-shared-terminal-order-acceptance-v348/HANDOFF.md']
for p in paths:upstream[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
target=ROOT/'component-manifest.json';assert not target.exists()
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size}
 for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p!=target}
packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Read-only EOF/schema5 integration review and26 actual bounded CPU checks; no GUI/native effects or complete compiler dependency closure claim',
 'nativeAcceptance':False,'fullRecoveryAcceptance':False,'releaseAcceptance':False,
 'selectedReport':str(selected),'selectedReportSHA256':sha(selected),'files':files,'upstream':upstream}
target.write_text(json.dumps(packet,indent=2)+'\n')
for rel,row in files.items():assert sha(ROOT/rel)==row['sha256']
print(json.dumps({'passed':True,'files':len(files),'manifest':str(target),'manifestSHA256':sha(target)}))
