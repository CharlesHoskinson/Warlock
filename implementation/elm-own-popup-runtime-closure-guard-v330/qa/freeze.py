import hashlib,json,os,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=ROOT/'qa/test-1791157683917112187/report.json';d=json.loads(report.read_text())
assert d['passed'] and not d['nativeAcceptance'] and len(d['checks'])==42 and len(d['mutants'])==5
for p,h in d['inputs'].items():assert sha(p)==h
for p,h in d['artifacts'].items():assert sha(report.parent/p)==h
upstream=ROOT.parent/'elm-own-popup-runtime-closure-guard-v329/component-manifest.json'
assert sha(upstream)=='047f1a922a4b2c5d9d89f795ed5c6579a58d266356087f38bec9ee4577ad36e9'
u=json.loads(upstream.read_text());external={}
for p,row in u['files'].items():
    path=upstream.parent/p;assert sha(path)==row['sha256'];external[str(path)]={'sha256':sha(path)}
for p,row in u['externalFiles'].items():
    path=Path(p)
    if 'symlink' in row:
        assert path.is_symlink() and os.readlink(path)==row['symlink'];external[str(path)]=row
    else:
        assert sha(path)==row['sha256'];external[str(path)]={'sha256':sha(path)}
external[str(upstream)]={'sha256':sha(upstream)}
own={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json' and '__pycache__' not in p.parts}
m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'authenticatedHost':False,'scope':'Read-only deadline-bound runtime/source and bracketed maps guard; actual self ELF/libc plus synthetic controls only','files':own,'externalFiles':external,'testReport':str(report),'upstreamManifestSHA256':sha(upstream)}
(ROOT/'component-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'passed':True,'manifestSHA256':sha(ROOT/'component-manifest.json'),'ownFiles':len(own),'externalFiles':len(external)}))
