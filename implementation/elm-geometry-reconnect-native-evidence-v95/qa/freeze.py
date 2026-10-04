"""Preserve native reconnect pass and atomic-publication retirement failure."""
import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=REPO/'implementation/elm-geometry-staged-menu-reconnect-native-v83';held=base/'qa/held-source-manifest.json';assert sha(held)=='29424e529ceca6980ec17a35cc44079e82deb9f058a4d62cd80e7b8267af4da9'
packet=json.loads(held.read_text());assert packet['sourceHeld'] and packet['evidenceIntegrityPassed']
for rel,row in packet['files'].items():assert sha(base/rel)==row['sha256'],rel
report_path=base/'qa/native-1791108937556480076/report.json';r=json.loads(report_path.read_text())
assert r['passed'] is False and r['cleanupPassed'] is True and len(r['checks'])==133 and all(c['passed'] for c in r['checks'])
assert r['scenarios']==['GEOMETRY-MENU-'+str(i).zfill(2) for i in range(1,9)] and not r['allContractScenariosPassed'] and not r['fullRoadmapAccepted']
assert 'line 232' in r['traceback'] and r['error']=="RuntimeError('Whole-transition absolute six-second deadline')"
f=r['reconnectFixture'];assert f['actualDetachedBeforePhysicalClick'] and f['deadlineSeconds']==6 and f['normalEOF']['childExit']==0 and f['normalEOF']['stdinClosed'] is True
assert f['retiredActor']['relay']!=f['newActor']['relay'] and f['retiredActor']['child']!=f['newActor']['child']
for rel,digest in r['artifacts'].items():assert sha(report_path.parent/rel)==digest,rel
for path,digest in r['inputs'].items():assert sha(path)==digest,path
log=report_path.parent/'native-evidence/elm-webview.log';text=log.read_text(errors='replace');assert 'surface-refused: commit-preflight' in text
files={str(p.relative_to(REPO)):{'sha256':sha(p),'size':p.stat().st_size} for p in [*base.rglob('*'),*ROOT.rglob('*')] if p.is_file() and not p.is_symlink()}
manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'inventoryBase':str(REPO),'files':files,'nativeCampaignPassed':False,'boundedReconnectObserved':True,'fullMenuAccepted':False,'releaseAccepted':False,'report':str(report_path),'reportSHA256':sha(report_path),'scope':'Actual private original01–08 assertions and realEOF/reconnect passed;10 failed before replacement,09 unexecuted; native popup auto-close/atomic commit rejection requires fresh forensic reproduction and fix.'}
p=ROOT/'component-manifest.json'
with p.open('x') as f:f.write(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(p),'sha256':sha(p),'files':len(files)}))
