import hashlib,json,os,resource,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
held=REPO/'implementation/elm-responsive-regression-held-v294/acceptance-manifest.json';assert sha(held)=='bba084a81316cdfeba6840d74af43547b2d73cb81f4cca8004d54fab6a24da69';packet=json.loads(held.read_text());assert packet['passed'] and packet['acceptedCurrentGuiGeneralNativeCheckCount']==473
for entry in packet['files']:
 p=REPO/entry['path']
 if 'symlink' in entry:assert p.is_symlink() and os.readlink(p)==entry['symlink']
 else:assert sha(p)==entry['sha256']
build=REPO/'implementation/elm-responsive-surfaces-gui-v278/qa/build-1791147765154709569';report=json.loads((build/'report.json').read_text());assert report['passed'] and sha(build/'elm-host')==report['binarySHA256']
files=[build/'elm-host',*sorted((build/'inputs/assets').iterdir()),*sorted((build/'inputs/adapter').iterdir())]
assert all(p.is_file() and not p.is_symlink() for p in files)
for p in files[1:]:
 rel=str(p.relative_to(build/'inputs'));assert sha(p)==report.get('artifacts',{}).get(str(p.relative_to(build)),report['inputs'].get(rel)),str(p)
manifest={'schema':1,'scope':'Bounded actual278 candidate runtime for original183 recovery; source-held294 scoped473 GUI+280bounds893, no deployment/release selection','host':str(build/'elm-host'),'assets':str(build/'inputs/assets'),'backend':str(build/'inputs/adapter/daemon.py'),'coreSHA256':packet['nativePair']['core']['sha256'],'files':{str(p):sha(p) for p in files}}
with (ROOT/'runtime-manifest.json').open('x') as f:f.write(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'manifestSHA256':sha(ROOT/'runtime-manifest.json')}))
