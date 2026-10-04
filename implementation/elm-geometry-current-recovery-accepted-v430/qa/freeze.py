import ast,hashlib,json,os,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-geometry-shared-accepted-v425/qa/slice-manifest.json'
assert sha(parent)=='12f99d5cf3557bafb8e0bfa6a8f86c58df80db9d0b647b963a7492b15a60fb46'
held=json.loads(parent.read_text());assert held['passed']
for e in held['files']:assert sha(REPO/e['path'])==e['sha256']
for e in held['symlinks']:assert os.readlink(REPO/e['path'])==e['target']
files=[];reports=[]
for name in ['elm-geometry-current-receipt-fixture-v427','elm-geometry-current-relay-native-v428','elm-geometry-current-reconnect-native-v429']:
 source=REPO/'implementation'/name
 for p in sorted(source.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  assert not p.is_symlink()
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name=='report.json':
   data=json.loads(p.read_text());assert data['passed']
   for c in data.get('checks',[]):assert c['passed']
   if 'native-' in p.parent.name:
    assert data['cleanupPassed'];assert len(data['checks'])==(50 if 'v428' in str(p) else 57)
   reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'checks':len(data.get('checks',[]))})
 assert (source/'README.md').is_file()
for old,new in [('elm-shared-relay-baseline-native-v392','elm-geometry-current-relay-native-v428'),('elm-shared-relay-reconnect-native-v393','elm-geometry-current-reconnect-native-v429')]:
 a=(REPO/'implementation'/old/'qa/native.py').read_text();b=(REPO/'implementation'/new/'qa/native.py').read_text()
 for before,after in [('elm-shared-terminal-runtime-v336','elm-geometry-bounds-runtime-v420'),('elm-shared-registration-shutdown-merge-v380','elm-shared-geometry-carrier-v422'),('elm-shared-receipt-eof-fixture-v391','elm-geometry-current-receipt-fixture-v427'),('build-1791121552616106038','build-1791127807406303648')]:a=a.replace(before,after)
 assert a==b,'Native oracle changed'
for p in [ROOT/'HANDOFF.md',Path(__file__).resolve()]:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
output=ROOT/'qa/slice-manifest.json';assert not output.exists()
output.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Bounded current422 native recovery50/57 and receipt/EOF CPU closure; original geometry08/09/10 and full release open','parentManifest':str(parent),'parentManifestSHA256':sha(parent),'files':files,'reports':reports,'nativeAcceptance':True,'fullGeometryCampaignAccepted':False,'fullReleaseAccepted':False,'completedRequirementIds':[]},indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifest':str(output),'sha256':sha(output)}))
