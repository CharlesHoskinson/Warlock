import hashlib,json,resource,stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=ROOT/'qa/capture-1791127317724421882/report.json';d=json.loads(p.read_text());assert d['passed'] and d['checks']==36
for section in ['inputs','dependencies','linkedLibraries']:
 for name,h in d[section].items():assert sha(Path(name))==h,name
for name,h in d['artifacts'].items():assert sha(p.parent/name)==h,name
files={}
for f in sorted(ROOT.rglob('*')):
 if f.name=='held-source-manifest.json':continue
 assert not f.is_symlink()
 if f.is_file():files[str(f.relative_to(ROOT))]={'sha256':sha(f),'size':f.stat().st_size,'mode':stat.S_IMODE(f.stat().st_mode)}
m={'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Actual rounded-fixed counterexample diagnostic only','nativeAcceptance':False,'modelAcceptance':False,'policyAdopted':False,'acceptedReport':str(p),'acceptedReportSHA256':sha(p),'checks':36,'files':files}
p=ROOT/'qa/held-source-manifest.json';assert not p.exists();p.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'passed':True,'manifest':str(p),'sha256':sha(p),'files':len(files)}))
