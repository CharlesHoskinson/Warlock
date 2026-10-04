import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=ROOT/'qa/test-1791156163998650959/report.json'
d=json.loads(report.read_text())
assert d['passed'] and not d['nativeAcceptance'] and len(d['checks'])==51
assert len(d['mutants'])==6 and all(m['killed'] for m in d['mutants'])
for p,h in d['inputs'].items():assert sha(p)==h
for p,h in d['artifacts'].items():assert sha(report.parent/p)==h
upstream=ROOT.parent/'elm-own-popup-native-grab-join-v315/component-manifest.json'
assert sha(upstream)=='e89897fcd85478caa182957abf09a8be1f2cd9d661a985111c54aa5c6565c705'
u=json.loads(upstream.read_text());external={}
for name,row in u['files'].items():
    p=upstream.parent/name;assert sha(p)==row['sha256'];external[str(p)]={'sha256':sha(p)}
for name,digest in u['external'].items():
    p=Path(name);assert sha(p)==digest;external[str(p)]={'sha256':sha(p)}
external[str(upstream)]={'sha256':sha(upstream)}
own={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json' and '__pycache__' not in p.parts}
manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'authenticated':False,'ownBlockerGrantQualified':False,'scope':'Strict joined DTO and diagnostic matcher, synthetic records only; no trusted peer or operation permission','files':own,'externalFiles':external,'testReport':str(report),'upstreamManifestSHA256':sha(upstream)}
(ROOT/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'ownFiles':len(own),'externalFiles':len(external),'manifestSHA256':sha(ROOT/'component-manifest.json')}))
