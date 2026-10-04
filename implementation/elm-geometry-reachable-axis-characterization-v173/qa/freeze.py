import hashlib,json,resource,stat,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=ROOT/'qa/characterize-1791126799074634174/report.json';d=json.loads(p.read_text());assert d['passed'] and d['checks']==151 and len(d['controls'])==2 and all(x['rejected'] and x['failures'] for x in d['controls'])
for name,h in d['inputs'].items():assert sha(Path(name))==h,name
for section in ['compilerDependencies','linkedLibraries']:
 for name,h in d[section].items():assert sha(Path(name))==h,name
for name,h in d['artifacts'].items():assert sha(p.parent/name)==h,name
provenance=json.loads(Path(next(x for x in d['inputs'] if x.endswith('v155/reviewed-inputs.json'))).read_text())
for name,row in provenance['files'].items():assert sha(Path(name))==row['sha256'],name
files={}
for f in sorted(ROOT.rglob('*')):
 if f.name=='held-source-manifest.json':continue
 assert not f.is_symlink(),f
 if f.is_file():files[str(f.relative_to(ROOT))]={'sha256':sha(f),'size':f.stat().st_size,'mode':stat.S_IMODE(f.stat().st_mode)}
manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Actual owning reachable-size arithmetic characterization only','nativeAcceptance':False,'modelAcceptance':False,'productionAdopted':False,'acceptedReport':str(p),'acceptedReportSHA256':sha(p),'checks':151,'unsafeControls':2,'failedReportsPreserved':[str(x.relative_to(ROOT)) for x in sorted(ROOT.glob('qa/characterize-*/report.json')) if not json.loads(x.read_text())['passed']],'files':files}
output=ROOT/'qa/held-source-manifest.json';assert not output.exists();output.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'passed':True,'manifest':str(output),'sha256':sha(output),'files':len(files)}))
