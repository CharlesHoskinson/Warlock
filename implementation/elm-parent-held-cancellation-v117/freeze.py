import hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=sorted(ROOT.glob('build-*/report.json'))[-1];r=json.loads(out.read_text());assert r['passed'] and r['publicHeadersUnchanged'] and r['currentMembershipAndWeakPublication'] and not r['missingParentSymbols']
assert sha(ROOT/'build.py')==r['runnerSHA256'] and sha(r['library'])==r['librarySHA256']
prior=Path(json.loads((ROOT/'upstream.json').read_text())['parent'])
changes=[]
for rel,value in r['sources'].items():
 assert sha(ROOT/'candidate'/rel)==value
 if sha(prior/'candidate'/rel)!=value:changes.append(rel)
assert changes==['src/backend/Wayland.cpp'],changes
for path,value in r['dependencies'].items():assert sha(path)==value,path
for p in r['proofReports']:
 assert sha(p['path'])==p['sha256'];packet=json.loads(Path(p['path']).read_text());assert packet['passed']
for rel,value in r['capturedInputs'].items():assert sha(out.parent/'inputs'/rel)==value
cpu=json.loads(Path(r['proofReports'][0]['path']).read_text());assert cpu['candidateChecks']==63 and cpu['mutantsRejected']==7
model=json.loads(Path(r['proofReports'][1]['path']).read_text());assert len(model['namedScenarios'])==10 and model['mutantsRejected']==8
for packet in [cpu,model]:
 for path,wanted in packet.get('inputs',{}).items():assert sha(path)==wanted,path
assert b'checks: 47' in (out.parent/'presentation-tests.stdout').read_bytes()
entries=[]
for p in sorted(ROOT.rglob('*')):
 if p.name=='component-manifest.json':continue
 if p.is_symlink():entries.append({'path':str(p.relative_to(ROOT)),'symlink':os.readlink(p)})
 elif p.is_file():entries.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size':p.stat().st_size})
manifest={'schema':1,'passed':True,'component':'AQ one-shot parent transport retirement and deferred poll-source withdrawal source/build','nativeAcceptance':False,'releaseAcceptance':False,'buildReport':str(out),'buildReportSHA256':sha(out),'scope':'One implementation source changes; complete library compile, all V79 public headers/export symbols retained; 63 actual-body typed checks/7 compiled mutants and Quint10/1000 sampled traces/8 mutants; native fault and normal regression separate','files':entries}
p=ROOT/'component-manifest.json';assert not p.exists();p.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'manifest':str(p),'sha256':sha(p),'files':len(entries)}))
