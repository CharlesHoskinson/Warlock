"""Own native dynamic C qualification derivative without changing held105."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v105';target=repo/'implementation/warlock-client-provider-native-v106';manifest=parent/'component-manifest.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();d=json.loads(manifest.read_text());assert d.get('passed') or d.get('evidenceIntegrityPassed')
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
assert not target.exists()
def exclusions(path,names):return [n for n in names if n in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path).name=='qa' and (n.startswith('native-') or n.startswith('prepare-')))]
shutil.copytree(parent,target,ignore=exclusions)
(target/'ANCESTRY.json').write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Retain all105 original controls/pixels/deadlines and exact owning ABI. Add separate actual dynamic C three-window probe with retained original waiting deadline and same bootstrap/journal/physical drain. Review/qualify against held newGUI65; no native launch until all CPU QA terminal and original protected serialized launcher owns tuple.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n');print(target)
