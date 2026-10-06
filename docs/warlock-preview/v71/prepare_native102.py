"""Own a fresh serialized native campaign derived from held native101."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v101';target=repo/'implementation/warlock-client-provider-native-v102';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=parent/'component-manifest.json';data=json.loads(manifest.read_text())
for rel,row in data['files'].items():assert sha(parent/rel)==row['sha256'],rel
p=next(parent.glob('qa/native-*/report.json'));d=json.loads(p.read_text());assert d['passed'] and d['cleanupPassed'] and len(d['checks'])==2392 and len(d['ownedExitCodes'])==260 and all(row['exitCode']==0 for row in d['ownedExitCodes'])
assert not target.exists();shutil.copytree(parent,target,ignore=shutil.ignore_patterns('native-*','prepare-*','component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'))
(target/'ANCESTRY.json').write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Retain all original native101 cases/deadlines on same exact owning ABI, requalify held changedGUI59 and new actual own trusted ImportedClients receiver/journal membership growth with held GIO reader and bounded shared captures. Native capture eligibility and full release remain unqualified.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
print(json.dumps({'source':str(target),'parentReport':str(p)}))
