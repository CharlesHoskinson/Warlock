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
model=json.loads(Path(r['proofReports'][1]['path']).read_text());assert len(model['namedScenarios'])==10 and model['mutantsRejected']==7 and model['invariantSamples']==1000 and model['maxSteps']==40 and model['sourceSHA256']==sha(ROOT/'spec/held.qnt')
cancel=json.loads(Path(r['proofReports'][2]['path']).read_text());assert cancel['candidateChecks']==152 and cancel['candidateValidated'] and cancel['mutantsRejected']==5
keys=json.loads(Path(r['proofReports'][3]['path']).read_text());assert keys['passed'] and keys['candidateValidated'] and keys['mutantsRejected']==7 and keys['candidateChecks']>=2000
for packet in [cpu,model,cancel,keys]:
 for path,wanted in packet.get('inputs',{}).items():assert sha(path)==wanted,path
assert b'checks: 47' in (out.parent/'presentation-tests.stdout').read_bytes()
entries=[]
for p in sorted(ROOT.rglob('*')):
 if p.name=='component-manifest.json':continue
 if p.is_symlink():entries.append({'path':str(p.relative_to(ROOT)),'symlink':os.readlink(p)})
 elif p.is_file():entries.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size':p.stat().st_size})
manifest={'schema':1,'passed':True,'component':'AQ admitted held-key cancellation before parent transport device retirement source/build','nativeAcceptance':False,'releaseAcceptance':False,'buildReport':str(out),'buildReportSHA256':sha(out),'scope':'Only Wayland.cpp changes relative to AQ120; complete library compile and all parent public headers/export symbols retained. Actual C++ cancellation helper152 checks/5 mutants and transport bodies63 checks/7 mutants; Quint10 two-key named scenarios/1000x40 traces/7 mutants; actual key admission/cancellation >=2000 checks and7 compiled mutants. Callback and multi-object ownership are actual C++ checks, not Quint refinement. Native held-key loss, modifier/shortcut ledgers and normal regressions remain separate.','files':entries}
p=ROOT/'component-manifest.json';assert not p.exists();p.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'manifest':str(p),'sha256':sha(p),'files':len(entries)}))
