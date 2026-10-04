import hashlib,json,os,resource,shlex,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
build=ROOT/'qa/build-1791110691541578995/report.json';test=ROOT/'qa/disposition-1791111414897040459/report.json'
reports={};external={}
for p in [build,test]:
 d=json.loads(p.read_text());assert d['passed'] and all(c['exitCode']==0 for c in d['commands'])
 for relative,wanted in d['artifacts'].items():assert sha(p.parent/relative)==wanted,relative
 reports[str(p.relative_to(ROOT))]={'sha256':sha(p),'passed':True}
# Bind exact current production modules to actual completed host/Main build.
d=json.loads(build.read_text())
for relative,wanted in d['inputs'].items():
 if relative.startswith(('src/','native/','assets/')) and relative!='src/BatchReplay.elm':assert sha(ROOT/relative)==wanted,relative
for relative,wanted in json.loads(test.read_text())['inputs'].items():assert sha(ROOT/relative)==wanted,relative
for path,wanted in json.loads(test.read_text())['compilerDependencies'].items():assert sha(path)==wanted;external[path]={'sha256':wanted}
workspace=build.parent/'inputs'
for token in shlex.split((build.parent/'host.d').read_text().replace('\\\n',' ').split(':',1)[1]):
 p=(workspace/token).resolve();external[str(p)]={'sha256':sha(p)}
origins=json.loads((ROOT/'qa/source-origins.json').read_text());upstream=Path(origins['manifest']);assert sha(upstream)==origins['manifestSHA256']
packet=json.loads(upstream.read_text())
for row in packet['files']:
 p=REPO/row['path']
 if 'sha256' in row:assert sha(p)==row['sha256'];external[str(p)]={'sha256':row['sha256']}
 if row.get('type')=='symlink':assert os.readlink(p)==row['target']
external[str(upstream)]={'sha256':sha(upstream)}
for lane in ['elm-menu-retirement-native-forensics-v94']:
 p=REPO/'implementation'/lane/'qa/held-source-manifest.json';md=json.loads(p.read_text());assert md['sourceHeld'] and md['evidenceIntegrityPassed']
 for relative,row in md['files'].items():assert sha(p.parents[1]/relative)==row['sha256']
 external[str(p)]={'sha256':sha(p)}
# Record the actual complete-host compilation's runtime link/tool closure.
links=subprocess.run(['ldd',str(build.parent/'elm-host')],capture_output=True,text=True,check=True).stdout
for word in links.split():
 if word.startswith('/') and Path(word).is_file():external[word]={'sha256':sha(word)}
for executable in ['cc','pkg-config','node','npm']:
 p=Path(subprocess.run(['which',executable],capture_output=True,text=True,check=True).stdout.strip()).resolve();external[str(p)]={'sha256':sha(p)}
manifest=ROOT/'qa/held-source-manifest.json';assert not manifest.exists()
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=manifest}
checks=json.loads(test.read_text())['checks']
result={'sourceHeld':True,'evidenceIntegrityPassed':True,'boundedPrototype':True,'nativeAcceptance':False,'fullRecoveryAccepted':False,'releaseAcceptance':False,'reports':reports,'compiledDispositionChecks':len(checks),'files':files,'externalFiles':external,'openDefects':['Stale exact observation certificate may dismiss UI before checking current observation slots','Topology retirement can strand possibly-sent observational expectations','Pre-owner refusal exhausts transport conservatively','Unsent operation terminal disposition and post-admission uncertainty/storage recovery remain unqualified','Oversized/cross-binding catalog/launch/reconnect recovery not qualified']}
manifest.write_text(json.dumps(result,indent=2)+'\n')
for relative,row in files.items():assert sha(ROOT/relative)==row['sha256']
for path,row in external.items():assert sha(path)==row['sha256']
print(json.dumps({'passed':True,'manifest':str(manifest),'sha256':sha(manifest),'files':len(files),'externalFiles':len(external),'compiledDispositionChecks':len(checks),'fullRecoveryAccepted':False}))
