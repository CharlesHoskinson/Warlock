import hashlib,json,resource,stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bp=r/'build-1791138396123416417/report.json';b=json.loads(bp.read_text());assert b['passed'];external={}
for name,digest in b['inputs'].items():assert sha(r/name)==digest==sha(bp.parent/'inputs'/name)
for section in ['owningFiles','dependencies','tools','linkedLibraries']:
 for name,digest in b[section].items():
  p=Path(name);assert sha(p)==digest;external[name]={'sha256':digest,'size':p.stat().st_size}
origin=json.loads((r/'origin.json').read_text())
for name in ['legacyBuildReport','observerManifest']:
 p=Path(origin[name]);assert sha(p)==origin[name+'SHA256'];external[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
for name,digest in origin['legacyInputs'].items():assert sha(r/'original151'/name)==digest
for name,digest in origin['observerInputs'].items():assert sha(r/'native'/name if name=='surface-observer.h' else r/'original225'/name)==digest
for directory in ['client-1791138640888683343','observer-1791138527977203339']:
 p=r/'qa'/directory/'report.json';d=json.loads(p.read_text());assert d['passed']
 for path,digest in d['inputs'].items():assert sha(path)==digest,path
old=json.loads((r/'qa/client-1791138610140084852/report.json').read_text());assert not old['passed'];assert sha(r/'qa/client-1791138610140084852/failed-test.py')==old['inputs'][str(r/'qa/test.py')]
descriptor={'schema':1,'nativeAcceptance':False,'installed':False,'inputProtocol':7,'observerProtocol':1,'module':{'path':b['module'],'sha256':b['moduleSHA256']},'client':{'path':b['client'],'sha256':b['clientSHA256']},'buildReport':str(bp),'buildReportSHA256':sha(bp),'scope':'Compiled input7+read-only observer1 union only; actual keyboard recipient/native union acceptance open'}
for key in ['module','client']:assert sha(descriptor[key]['path'])==descriptor[key]['sha256']
(r/'parent-probe-build-report.json').write_text(json.dumps(descriptor,indent=2)+'\n')
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in r.rglob('*') if p.is_file() and p.name!='component-manifest.json'}
m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Input7 observer1 actual ABI compile/preservation/mocked callback CPU only','files':files,'externalFiles':external,'parentProof':origin,'buildReport':str(bp),'buildReportSHA256':sha(bp)}
p=r/'component-manifest.json';assert not p.exists();p.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'externalFiles':len(external),'manifestSHA256':sha(p),'descriptorSHA256':sha(r/'parent-probe-build-report.json')}))
