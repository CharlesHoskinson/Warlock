import hashlib
import json
from pathlib import Path
import stat
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 build=sorted(ROOT.glob('build-*/report.json'))[-1];cpu=sorted((ROOT/'qa').glob('observer-*/report.json'))[-1];semantics=sorted((ROOT/'qa').glob('semantics-*/report.json'))[-1]
 data=json.loads(build.read_text());assert data['passed']
 for section in ('owningFiles','dependencies','tools','linkedLibraries'):
  for name,value in data[section].items():assert sha(Path(name))==value,(section,name)
 for name,value in data['inputs'].items():assert sha(ROOT/name)==value and sha(build.parent/'inputs'/name)==value,name
 for selected in (cpu,semantics):
  record=json.loads(selected.read_text());assert record['passed']
  for name,value in record['inputs'].items():assert sha(Path(name))==value,name
  for name,value in record.get('artifacts',{}).items():assert sha(selected.parent/name)==value,name
 module=Path(data['module']);client=Path(data['client']);assert sha(module)==data['moduleSHA256'] and sha(client)==data['clientSHA256']
 descriptor={'schema':1,'nativeAcceptance':False,'installed':False,'inputProtocol':3,'observerProtocol':1,'module':{'path':str(module),'sha256':sha(module)},'client':{'path':str(client),'sha256':sha(client)},'buildReport':str(build),'buildReportSHA256':sha(build),'scope':'read-only observer/input fixture candidate; actual ABI compile+CPU only; native recipient/view proofs await root'}
 (ROOT/'parent-probe-build-report.json').write_text(json.dumps(descriptor,indent=2)+'\n')
 packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'actualWeston ABI/source/CPU candidate; parent geometry/delivery unqualified','actualProductionHelperChecks':json.loads(cpu.read_text())['actualChecks'],'rejectedSourceControls':2,'acceptedBuildReport':str(build),'acceptedCPUReport':str(cpu),'acceptedSemanticsReport':str(semantics),'files':{}}
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file() or p.name=='component-manifest.json' or '__pycache__' in p.parts:continue
  assert not p.is_symlink(),str(p)
  packet['files'][str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
 dest=ROOT/'component-manifest.json';assert not dest.exists();dest.write_text(json.dumps(packet,indent=2)+'\n')
 for name,row in packet['files'].items():assert sha(ROOT/name)==row['sha256'],name
 print(json.dumps({'passed':True,'manifest':str(dest),'sha256':sha(dest),'files':len(packet['files']),'buildReport':str(build),'descriptorSHA256':sha(ROOT/'parent-probe-build-report.json')}))
if __name__=='__main__':main()
